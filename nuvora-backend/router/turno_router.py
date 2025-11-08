from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.db import SessionLocal
from config.auth import get_current_user, require_admin, require_cajero
from model.users import User
from schema.turno_schema import TurnoCreate, TurnoResponse
from model.turnos import Turno
from typing import List
from datetime import datetime

turno_router = APIRouter(prefix="/turnos", tags=["Turnos"])


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


@turno_router.post("/iniciar", response_model=TurnoResponse)
def iniciar_turno(
	monto_inicial: float,
	observaciones: str = None,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Inicia un turno para el usuario autenticado.
	Ya no necesitas pasar user_id manualmente - se obtiene del token JWT.
	"""
	# Verificar si el usuario ya tiene un turno abierto
	turno_abierto = db.query(Turno).filter(
		Turno.usuario_id == current_user.id,
		Turno.estado == 'abierto'
	).first()
	
	if turno_abierto:
		raise HTTPException(
			status_code=400,
			detail=f"El usuario ya tiene un turno abierto (ID: {turno_abierto.id})"
		)
	
	# Crear el turno con el usuario autenticado
	nuevo_turno = Turno(
		usuario_id=current_user.id,
		fecha_inicio=datetime.now(),
		monto_inicial=monto_inicial,
		observaciones=observaciones,
		estado='abierto'
	)
	db.add(nuevo_turno)
	db.commit()
	db.refresh(nuevo_turno)
	return nuevo_turno


@turno_router.post("/", response_model=TurnoResponse)
def crear_turno(
	data: TurnoCreate,
	db: Session = Depends(get_db),
	admin: User = Depends(require_admin)
):
	"""
	Crear turno manualmente (solo para administradores).
	Los usuarios normales deben usar /iniciar.
	"""
	nueva = Turno(
		usuario_id=data.usuario_id,
		fecha_inicio=data.fecha_inicio if data.fecha_inicio else datetime.now(),
		monto_inicial=data.monto_inicial,
		observaciones=data.observaciones
	)
	db.add(nueva)
	db.commit()
	db.refresh(nueva)
	return nueva


@turno_router.get("/", response_model=List[TurnoResponse])
def listar_mis_turnos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
	"""
	Lista los turnos del usuario autenticado (solo sus propios turnos).
	"""
	return db.query(Turno).filter(Turno.usuario_id == current_user.id).all()


@turno_router.get("/todos", response_model=List[TurnoResponse])
def listar_todos_turnos(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
	"""
	Lista TODOS los turnos de todos los usuarios (solo administradores).
	"""
	return db.query(Turno).all()


@turno_router.get("/actual", response_model=TurnoResponse)
def obtener_turno_actual(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
	"""
	Obtiene el turno actualmente abierto del usuario autenticado.
	Útil para saber si tiene un turno activo y cuál es.
	"""
	turno_actual = db.query(Turno).filter(
		Turno.usuario_id == current_user.id,
		Turno.estado == 'abierto'
	).first()
	
	if not turno_actual:
		raise HTTPException(status_code=404, detail="No tienes un turno abierto actualmente")
	
	return turno_actual


@turno_router.post("/{turno_id}/cerrar", response_model=TurnoResponse)
def cerrar_turno(
	turno_id: int,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Cierra el turno especificado.
	Solo el dueño del turno o un admin puede cerrarlo.
	"""
	turno = db.query(Turno).filter(Turno.id == turno_id).first()
	if not turno:
		raise HTTPException(status_code=404, detail="Turno no encontrado")
	
	# Verificar permisos: solo el dueño o admin puede cerrar
	if turno.usuario_id != current_user.id and current_user.rol != 'admin':
		raise HTTPException(
			status_code=403,
			detail="No tienes permiso para cerrar este turno"
		)
	
	if turno.estado == 'cerrado':
		raise HTTPException(status_code=400, detail="El turno ya está cerrado")

	turno.fecha_fin = datetime.now()
	turno.estado = 'cerrado'
	db.commit()
	db.refresh(turno)
	return turno


# Endpoint para cerrar el turno abierto del usuario autenticado
@turno_router.post("/cerrar", response_model=TurnoResponse)
def cerrar_mi_turno(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Cierra el turno abierto del usuario autenticado (no requiere id manual).
    """
    turno = db.query(Turno).filter(
        Turno.usuario_id == current_user.id,
        Turno.estado == 'abierto'
    ).first()
    if not turno:
        raise HTTPException(status_code=404, detail="No tienes un turno abierto para cerrar")
    turno.fecha_fin = datetime.now()
    turno.estado = 'cerrado'
    db.commit()
    db.refresh(turno)
    return turno

