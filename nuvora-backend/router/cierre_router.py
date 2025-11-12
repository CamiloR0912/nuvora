from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from config.db import SessionLocal
from config.auth import get_current_user, require_admin, create_access_token
from model.cierres import CierreCaja
from model.turnos import Turno
from model.tickets import Ticket
from model.users import User
from schema.cierre_schema import CierreCreate, CierreResponse, CierreConTokenResponse
from typing import List, Optional
from datetime import datetime

cierre_router = APIRouter(prefix="/cierres", tags=["Cierres"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@cierre_router.post("/", response_model=CierreConTokenResponse, status_code=201)
def crear_cierre(payload: CierreCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Crea un cierre de caja:
    1. Cierra el turno abierto actual (si existe)
    2. Consolida TODOS los turnos cerrados que aún NO han sido incluidos en un cierre
    3. Devuelve un nuevo token JWT SIN turno_id para permitir abrir un nuevo turno
    """
    # 1. Buscar y cerrar el turno abierto actual (si existe)
    turno_abierto = db.query(Turno).filter(
        Turno.usuario_id == current_user.id,
        Turno.estado == 'abierto'
    ).first()
    
    if turno_abierto:
        # Calcular totales del turno abierto antes de cerrarlo
        total_recaudado = db.query(func.coalesce(func.sum(Ticket.monto_total), 0)).filter(
            Ticket.turno_cierre_id == turno_abierto.id,
            Ticket.estado == 'cerrado'
        ).scalar() or 0
        
        total_vehiculos = db.query(func.count(Ticket.id)).filter(
            Ticket.turno_cierre_id == turno_abierto.id,
            Ticket.estado == 'cerrado'
        ).scalar() or 0
        
        # Cerrar el turno con los datos calculados
        turno_abierto.fecha_fin = datetime.now()
        turno_abierto.estado = 'cerrado'
        turno_abierto.monto_total = float(total_recaudado)
        turno_abierto.total_vehiculos = int(total_vehiculos)
        turno_abierto.incluido_en_cierre = False  # Aún no incluido
        
        try:
            db.commit()
            db.refresh(turno_abierto)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al cerrar turno: {str(e)}")

    # 2. Buscar todos los turnos cerrados que NO han sido incluidos en un cierre
    turnos_pendientes = db.query(Turno).filter(
        Turno.estado == 'cerrado',
        Turno.incluido_en_cierre == False
    ).all()
    
    if not turnos_pendientes:
        raise HTTPException(
            status_code=400, 
            detail="No tienes turnos pendientes de incluir en un cierre."
        )

    # 3. Calcular totales sumando los datos de cada turno cerrado pendiente
    total_vehiculos = sum(turno.total_vehiculos for turno in turnos_pendientes)
    total_recaudado = sum(float(turno.monto_total or 0) for turno in turnos_pendientes)
    
    # Usar el turno más reciente como referencia (debería ser el que acabamos de cerrar)
    turno_actual = turnos_pendientes[-1] if turnos_pendientes else None
    
    if not turno_actual:
        raise HTTPException(status_code=400, detail="No se encontró turno para el cierre")

    # Crear registro de cierre consolidado
    cierre = CierreCaja(
        turno_id=turno_actual.id,  # Referencia al turno actual del usuario
        total_vehiculos=int(total_vehiculos),
        total_recaudado=float(total_recaudado),
        fecha_cierre=datetime.now(),
        observaciones=payload.observaciones
    )
    db.add(cierre)
    
    # Marcar todos los turnos como incluidos en cierre
    for turno in turnos_pendientes:
        turno.incluido_en_cierre = True
    
    try:
        db.commit()
        db.refresh(cierre)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear cierre: {str(e)}")

    # Crear nuevo token SIN turno_id (solo con user_id)
    nuevo_token = create_access_token({
        "sub": str(current_user.id)
    })

    # Retornar cierre con el nuevo token
    return CierreConTokenResponse(
        id=cierre.id,
        turno_id=cierre.turno_id,
        total_vehiculos=cierre.total_vehiculos,
        total_recaudado=cierre.total_recaudado,
        fecha_cierre=cierre.fecha_cierre,
        observaciones=cierre.observaciones,
        created_at=cierre.created_at,
        access_token=nuevo_token,
        token_type="bearer"
    )

@cierre_router.get("/", response_model=List[CierreResponse])
def listar_cierres(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """
    Lista todos los cierres. Solo accesible para administradores.
    """
    cierres = db.query(CierreCaja).order_by(CierreCaja.created_at.desc()).all()
    return cierres

@cierre_router.get("/{cierre_id}", response_model=CierreResponse)
def obtener_cierre(cierre_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    cierre = db.query(CierreCaja).filter(CierreCaja.id == cierre_id).first()
    if not cierre:
        raise HTTPException(status_code=404, detail="Cierre no encontrado")
    return cierre
