from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from datetime import datetime

from config.db import SessionLocal
from config.auth import get_current_user
from model.users import User
from model.tickets import Ticket
from model.vehiculos import Vehiculo
from model.turnos import Turno
from schema.vehiculo_schema import (
    VehiculoActivoResponse,
    VehiculoHistorialResponse,
    VehiculoEntradaRequest,
    VehiculoSalidaRequest,
    VehiculoBusquedaResponse
)

vehiculo_router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@vehiculo_router.get("/activos", response_model=List[VehiculoActivoResponse])
def obtener_vehiculos_activos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene TODOS los vehículos activos (tickets abiertos) en el parqueadero.
    Cualquier usuario autenticado puede ver todos los vehículos activos.
    """
    # Query de todos los tickets abiertos sin restricción de turno
    resultados = (
        db.query(
            Ticket.id,
            Vehiculo.placa,
            Ticket.hora_entrada,
            Ticket.turno_id
        )
        .join(Vehiculo, Ticket.vehiculo_id == Vehiculo.id)
        .filter(Ticket.estado == 'abierto')
        .order_by(Ticket.hora_entrada.desc())
        .all()
    )
    
    # Transformar a formato esperado por el frontend
    vehiculos_activos = []
    for ticket_id, placa, hora_entrada, turno_id in resultados:
        vehiculos_activos.append(
            VehiculoActivoResponse(
                id=ticket_id,
                placa=placa,
                fecha_entrada=hora_entrada,
                espacio=None,
                turno_id=turno_id
            )
        )
    
    return vehiculos_activos


@vehiculo_router.get("/historial", response_model=List[VehiculoHistorialResponse])
def obtener_vehiculos_historial(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene TODO el historial de vehículos (tickets cerrados).
    Cualquier usuario autenticado puede ver todo el historial.
    """
    # Query de todos los tickets cerrados sin restricción de turno
    resultados = (
        db.query(
            Ticket.id,
            Vehiculo.placa,
            Ticket.hora_entrada,
            Ticket.hora_salida,
            Ticket.monto_total,
            Ticket.turno_id
        )
        .join(Vehiculo, Ticket.vehiculo_id == Vehiculo.id)
        .filter(Ticket.estado == 'cerrado')
        .order_by(Ticket.hora_salida.desc())
        .all()
    )
    
    # Transformar a formato esperado por el frontend
    vehiculos_historial = []
    for ticket_id, placa, hora_entrada, hora_salida, monto_total, turno_id in resultados:
        vehiculos_historial.append(
            VehiculoHistorialResponse(
                id=ticket_id,
                placa=placa,
                fecha_entrada=hora_entrada,
                fecha_salida=hora_salida,
                total_facturado=float(monto_total) if monto_total else 0.0,
                turno_id=turno_id
            )
        )
    
    return vehiculos_historial


@vehiculo_router.post("/entrada", response_model=VehiculoActivoResponse)
def registrar_entrada_manual(
    data: VehiculoEntradaRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Registra la entrada manual de un vehículo.
    Cualquier usuario autenticado puede registrar entradas.
    Usa el turno abierto del usuario actual.
    """
    # Validar que el usuario tenga un turno abierto
    turno_abierto = db.query(Turno).filter(
        Turno.usuario_id == current_user.id,
        Turno.estado == 'abierto'
    ).first()
    
    if not turno_abierto:
        raise HTTPException(
            status_code=400,
            detail="No tienes un turno abierto. Debes iniciar un turno antes de registrar entradas."
        )
    
    # Normalizar placa a mayúsculas
    placa = data.placa.strip().upper()
    
    # Buscar o crear vehículo
    vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == placa).first()
    if not vehiculo:
        vehiculo = Vehiculo(placa=placa)
        db.add(vehiculo)
        db.commit()
        db.refresh(vehiculo)
    
    # Verificar que no exista ticket abierto para esta placa en CUALQUIER turno
    # (No solo en el turno del usuario actual)
    ticket_existente = db.query(Ticket).filter(
        Ticket.vehiculo_id == vehiculo.id,
        Ticket.estado == 'abierto'
    ).first()
    
    if ticket_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un ticket abierto para la placa {placa} (ID: {ticket_existente.id}, Turno: {ticket_existente.turno_id})"
        )
    
    # Crear nuevo ticket
    nuevo_ticket = Ticket(
        vehiculo_id=vehiculo.id,
        turno_id=turno_abierto.id,
        hora_entrada=datetime.now(),
        estado='abierto'
    )
    
    db.add(nuevo_ticket)
    
    try:
        db.commit()
        db.refresh(nuevo_ticket)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar entrada: {str(e)}"
        )
    
    # Notificar a clientes SSE
    try:
        from router.events_router import update_last_detection
        update_last_detection(
            placa=placa,
            timestamp=nuevo_ticket.hora_entrada.isoformat(),
            vehicle_type='car'
        )
    except Exception as e:
        # No fallar si SSE falla
        print(f"⚠️ Error notificando SSE: {e}")
    
    return VehiculoActivoResponse(
        id=nuevo_ticket.id,
        placa=placa,
        fecha_entrada=nuevo_ticket.hora_entrada,
        espacio=None,
        turno_id=turno_abierto.id
    )


@vehiculo_router.post("/salida", response_model=VehiculoHistorialResponse)
def registrar_salida_manual(
    data: VehiculoSalidaRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Registra la salida manual de un vehículo.
    Cualquier usuario autenticado puede registrar salidas de CUALQUIER ticket abierto.
    No requiere que el ticket sea del turno del usuario.
    """
    from datetime import timezone  # 👈 Import necesario aquí

    # Normalizar placa
    placa = data.placa.strip().upper()
    
    # Buscar vehículo
    vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == placa).first()
    if not vehiculo:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró vehículo con placa {placa}"
        )
    
    # Buscar CUALQUIER ticket abierto para esta placa (sin restricción de turno)
    ticket = db.query(Ticket).filter(
        Ticket.vehiculo_id == vehiculo.id,
        Ticket.estado == 'abierto'
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail=f"No hay ticket abierto para la placa {placa}"
        )
    
    # Registrar salida con la fecha/hora proporcionada
    ticket.hora_salida = data.fecha_salida

    # ✅ Asegurar que ambas fechas tengan zona horaria UTC
    if ticket.hora_entrada.tzinfo is None:
        ticket.hora_entrada = ticket.hora_entrada.replace(tzinfo=timezone.utc)

    if ticket.hora_salida.tzinfo is None:
        ticket.hora_salida = ticket.hora_salida.replace(tzinfo=timezone.utc)

    # Calcular tiempo y monto
    try:
        tiempo = ticket.hora_salida - ticket.hora_entrada
        horas = max(1, round(tiempo.total_seconds() / 3600))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculando duración: {str(e)}"
        )
    
    tarifa_por_hora = 5000  # Configurar según necesidad
    ticket.monto_total = float(horas * tarifa_por_hora)
    ticket.estado = 'cerrado'
    
    try:
        db.commit()
        db.refresh(ticket)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar salida: {str(e)}"
        )
    
    return VehiculoHistorialResponse(
        id=ticket.id,
        placa=placa,
        fecha_entrada=ticket.hora_entrada,
        fecha_salida=ticket.hora_salida,
        total_facturado=float(ticket.monto_total),
        turno_id=ticket.turno_id
    )



@vehiculo_router.get("/buscar/{placa}", response_model=VehiculoBusquedaResponse)
def buscar_vehiculo_por_placa(
    placa: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca un vehículo por placa en TODOS los tickets del sistema.
    Cualquier usuario autenticado puede buscar en todos los tickets.
    Retorna el estado (activo o historial) y la información correspondiente.
    """
    # Normalizar placa
    placa = placa.strip().upper()
    
    # Buscar vehículo
    vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == placa).first()
    if not vehiculo:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró vehículo con placa {placa}"
        )
    
    # Buscar primero en tickets abiertos (activos) - SIN restricción de turno
    ticket_activo = (
        db.query(Ticket)
        .filter(
            Ticket.vehiculo_id == vehiculo.id,
            Ticket.estado == 'abierto'
        )
        .order_by(Ticket.hora_entrada.desc())
        .first()
    )
    
    if ticket_activo:
        # Vehículo está actualmente en el parqueadero
        return VehiculoBusquedaResponse(
            vehiculo=VehiculoActivoResponse(
                id=ticket_activo.id,
                placa=placa,
                fecha_entrada=ticket_activo.hora_entrada,
                espacio=None,
                turno_id=ticket_activo.turno_id
            ),
            estado='activo'
        )
    
    # Si no está activo, buscar en historial (tickets cerrados) - SIN restricción de turno
    ticket_historial = (
        db.query(Ticket)
        .filter(
            Ticket.vehiculo_id == vehiculo.id,
            Ticket.estado == 'cerrado'
        )
        .order_by(Ticket.hora_salida.desc())
        .first()
    )
    
    if ticket_historial:
        # Vehículo en historial
        return VehiculoBusquedaResponse(
            vehiculo=VehiculoHistorialResponse(
                id=ticket_historial.id,
                placa=placa,
                fecha_entrada=ticket_historial.hora_entrada,
                fecha_salida=ticket_historial.hora_salida,
                total_facturado=float(ticket_historial.monto_total) if ticket_historial.monto_total else 0.0,
                turno_id=ticket_historial.turno_id
            ),
            estado='historial'
        )
    
    # No se encontró ningún ticket
    raise HTTPException(
        status_code=404,
        detail=f"No hay registros para la placa {placa}"
    )
