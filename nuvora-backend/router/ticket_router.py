from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.db import SessionLocal
from schema.ticket_schema import TicketEntrada, TicketSalidaPorPlaca, TicketResponse, TicketDetailResponse
from config.auth import get_current_user, require_admin
from model.tickets import Ticket
from model.vehiculos import Vehiculo
from model.clientes import Cliente
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


def obtener_tickets_abiertos_con_detalles(db: Session, current_user: User) -> List[TicketDetailResponse]:
	"""
	Función auxiliar para obtener tickets abiertos con detalles.
	Reutilizable en múltiples endpoints.
	
	- Admin: todos los tickets abiertos del sistema
	- Usuario normal: TODOS los tickets abiertos (sin importar el turno que los creó)
	
	Esto permite que cualquier usuario pueda cerrar tickets abiertos,
	incluso si fueron creados por un turno anterior.
	"""
	# Obtener TODOS los tickets abiertos del sistema (sin filtrar por turno)
	tickets = db.query(Ticket).filter(Ticket.estado == 'abierto').all()
	
	# Enriquecer con datos del vehículo
	tickets_detallados = []
	for ticket in tickets:
		vehiculo = db.query(Vehiculo).filter(Vehiculo.id == ticket.vehiculo_id).first()
		placa = vehiculo.placa if vehiculo else None
		
		ticket_detallado = TicketDetailResponse(
			id=ticket.id,
			vehiculo_id=ticket.vehiculo_id,
			turno_id=ticket.turno_id,
			turno_cierre_id=ticket.turno_cierre_id,
			hora_entrada=ticket.hora_entrada,
			hora_salida=ticket.hora_salida,
			monto_total=ticket.monto_total,
			estado=ticket.estado,
			placa=placa,
			cliente_nombre=None,
			cliente_telefono=None,
			cliente_email=None
		)
		tickets_detallados.append(ticket_detallado)
	
	return tickets_detallados


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
    Registra la salida de un vehículo buscando por placa.
    Busca cualquier ticket abierto de esa placa (sin importar qué turno lo creó).
    El turno actual registra el cierre en turno_cierre_id.
    """
    # 1) Usuario debe tener un turno abierto
    turno_abierto = db.query(Turno).filter(
        Turno.usuario_id == current_user.id,
        Turno.estado == 'abierto'
    ).first()
    if not turno_abierto:
        raise HTTPException(status_code=400, detail="No tienes un turno abierto actualmente")

    # 2) Buscar vehículo por placa
    veh = db.query(Vehiculo).filter(Vehiculo.placa == data.placa.upper()).first()
    if not veh:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado por esa placa")

    # 3) Buscar el ticket abierto usando la función auxiliar
    tickets_abiertos = obtener_tickets_abiertos_con_detalles(db, current_user)
    
    # Filtrar por placa específica
    ticket_encontrado = next((t for t in tickets_abiertos if t.placa and t.placa.upper() == data.placa.upper()), None)
    
    if not ticket_encontrado:
        raise HTTPException(status_code=404, detail=f"No hay ticket abierto para la placa {data.placa}")
    
    # Obtener el ticket original de la BD para modificarlo
    ticket = db.query(Ticket).filter(Ticket.id == ticket_encontrado.id).first()

    # 4) Cierre automático con hora actual y turno de cierre
    ticket.hora_salida = datetime.now()
    ticket.turno_cierre_id = turno_abierto.id  # Registrar qué turno cerró el ticket
    
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


@ticket_router.get("/", response_model=List[TicketDetailResponse])
def listar_tickets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
	"""
	Lista los tickets con detalles (placa del vehículo).
	- Admin: ve todos los tickets de todos los turnos con detalles
	- Otros usuarios: solo ven tickets de su turno ACTIVO actual
	"""
	if current_user.rol == 'admin':
		# Admin ve todos los tickets
		tickets = db.query(Ticket).all()
	else:
		# Usuario normal: solo tickets de su turno ACTIVO
		turno_activo = db.query(Turno).filter(
			Turno.usuario_id == current_user.id,
			Turno.estado == 'abierto'
		).first()
		
		if not turno_activo:
			return []  # Si no tiene turno activo, retorna lista vacía
		
		tickets = db.query(Ticket).filter(Ticket.turno_id == turno_activo.id).all()
	
	# Enriquecer con datos del vehículo
	tickets_detallados = []
	for ticket in tickets:
		vehiculo = db.query(Vehiculo).filter(Vehiculo.id == ticket.vehiculo_id).first()
		placa = vehiculo.placa if vehiculo else None
		
		ticket_detallado = TicketDetailResponse(
			id=ticket.id,
			vehiculo_id=ticket.vehiculo_id,
			turno_id=ticket.turno_id,
			turno_cierre_id=ticket.turno_cierre_id,
			hora_entrada=ticket.hora_entrada,
			hora_salida=ticket.hora_salida,
			monto_total=ticket.monto_total,
			estado=ticket.estado,
			placa=placa,
			cliente_nombre=None,
			cliente_telefono=None,
			cliente_email=None
		)
		tickets_detallados.append(ticket_detallado)
	
	return tickets_detallados


@ticket_router.get("/abiertos", response_model=List[TicketDetailResponse])
def listar_tickets_abiertos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
	"""
	Lista los tickets ABIERTOS con detalles.

	"""
	return obtener_tickets_abiertos_con_detalles(db, current_user)



@ticket_router.get("/buscar-placa/{placa}", response_model=TicketDetailResponse)
def buscar_ticket_por_placa(placa: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
	"""
	Busca un ticket ABIERTO por placa.
	Utiliza la función auxiliar para obtener tickets abiertos según permisos del usuario.
	"""
	# Obtener todos los tickets abiertos según el usuario
	tickets_abiertos = obtener_tickets_abiertos_con_detalles(db, current_user)
	
	# Buscar por placa específica
	ticket_encontrado = next((t for t in tickets_abiertos if t.placa and t.placa.upper() == placa.upper()), None)
	
	if not ticket_encontrado:
		raise HTTPException(status_code=404, detail=f"No hay ticket abierto para la placa {placa}")
	
	return ticket_encontrado

