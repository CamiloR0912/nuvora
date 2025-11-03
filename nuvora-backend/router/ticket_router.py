from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.db import SessionLocal
from schema.ticket_schema import TicketEntrada, TicketSalidaPorPlaca, TicketResponse
from config.auth import get_current_user, require_admin
from model.tickets import Ticket
from model.vehiculos import Vehiculo
from model.turnos import Turno
from model.users import User
from typing import List
from datetime import datetime

ticket_router = APIRouter(prefix="/tickets", tags=["Tickets"])


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


@ticket_router.post("/entrada", response_model=TicketResponse)
def entrada_ticket(data: TicketEntrada, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Registra la entrada de un vehículo.
    Automáticamente usa el turno abierto del usuario autenticado y registra la hora actual.
    """
    # Buscar el turno abierto del usuario autenticado
    turno_abierto = db.query(Turno).filter(
        Turno.usuario_id == current_user.id,
        Turno.estado == 'abierto'
    ).first()
    
    if not turno_abierto:
        raise HTTPException(
            status_code=400,
            detail="No tienes un turno abierto. Debes iniciar un turno antes de registrar tickets."
        )
    
    # Buscar o crear vehiculo
    veh = db.query(Vehiculo).filter(Vehiculo.placa == data.placa).first()
    if not veh:
        veh = Vehiculo(placa=data.placa)
        db.add(veh)
        db.commit()
        db.refresh(veh)

    # Evitar crear dos tickets abiertos para la misma placa en el mismo turno
    existente = db.query(Ticket).filter(
        Ticket.vehiculo_id == veh.id,
        Ticket.turno_id == turno_abierto.id,
        Ticket.estado != 'cerrado'
    ).first()
    if existente:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un ticket abierto para la placa {data.placa} en tu turno actual (Ticket ID: {existente.id})"
        )

    # Registrar entrada con hora actual
    nuevo = Ticket(
        vehiculo_id=veh.id,
        turno_id=turno_abierto.id,
        hora_entrada=datetime.now()  # Hora automática
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@ticket_router.post("/salida", response_model=TicketResponse)
def salida_ticket(data: TicketSalidaPorPlaca, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Registra la salida de un vehículo buscando por placa en el turno ABIERTO del usuario autenticado.
    La hora de salida se registra automáticamente.
    """
    # 1) Usuario debe tener un turno abierto
    turno_abierto = db.query(Turno).filter(
        Turno.usuario_id == current_user.id,
        Turno.estado == 'abierto'
    ).first()
    if not turno_abierto:
        raise HTTPException(status_code=400, detail="No tienes un turno abierto actualmente")

    # 2) Buscar vehículo por placa
    veh = db.query(Vehiculo).filter(Vehiculo.placa == data.placa).first()
    if not veh:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado por esa placa")

    # 3) Buscar ticket abierto de ese vehículo en el turno abierto del usuario
    ticket = (
        db.query(Ticket)
        .filter(
            Ticket.vehiculo_id == veh.id,
            Ticket.turno_id == turno_abierto.id,
            Ticket.estado == 'abierto'
        )
        .order_by(Ticket.hora_entrada.desc())
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="No hay ticket abierto para esa placa en tu turno actual")

    # 4) Cierre automático con hora actual
    ticket.hora_salida = datetime.now()
    
    # Cálculo del tiempo y monto
    tiempo = ticket.hora_salida - ticket.hora_entrada
    horas = max(1, round(tiempo.total_seconds() / 3600))
    tarifa = 5000
    ticket.monto_total = float(horas * tarifa)
    ticket.estado = 'cerrado'
    
    try:
        db.commit()
        db.refresh(ticket)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al cerrar el ticket: {str(e)}")
    
    return ticket


@ticket_router.get("/", response_model=List[TicketResponse])
def listar_tickets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
	"""
	Lista los tickets.
	- Admin: ve todos los tickets
	- Otros usuarios: solo ven tickets de sus propios turnos
	"""
	if current_user.rol == 'admin':
		return db.query(Ticket).all()
	else:
		# Obtener los IDs de los turnos del usuario
		turnos_usuario = db.query(Turno.id).filter(Turno.usuario_id == current_user.id).all()
		turno_ids = [t[0] for t in turnos_usuario]
		return db.query(Ticket).filter(Ticket.turno_id.in_(turno_ids)).all()


@ticket_router.get("/todos", response_model=List[TicketResponse])
def listar_todos_tickets(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
	"""
	Lista TODOS los tickets de todos los turnos (solo administradores).
	"""
	return db.query(Ticket).all()

