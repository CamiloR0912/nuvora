from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from config.db import SessionLocal
from config.auth import get_current_user, require_admin
from model.cierres import CierreCaja
from model.turnos import Turno
from model.tickets import Ticket
from model.users import User
from schema.cierre_schema import CierreCreate, CierreResponse
from typing import List, Optional
from datetime import datetime

cierre_router = APIRouter(prefix="/cierres", tags=["Cierres"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@cierre_router.post("/", response_model=CierreResponse, status_code=201)
def crear_cierre(payload: CierreCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Crea un cierre de caja para un turno.
    - Si current_user es admin y envia turno_id, usa ese turno.
    - Si no envía turno_id, usa el turno ABIERTO del usuario autenticado.
    - Si el turno está abierto, lo cierra automáticamente antes de crear el cierre.
    """
    # Determinar turno
    turno: Optional[Turno] = None
    if payload.turno_id is not None:
        turno = db.query(Turno).filter(Turno.id == payload.turno_id).first()
        if not turno:
            raise HTTPException(status_code=404, detail="Turno no encontrado")
        # si no es admin y el turno no pertenece al usuario -> forbidden
        if current_user.rol != 'admin' and turno.usuario_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para cerrar ese turno")
    else:
        turno = db.query(Turno).filter(Turno.usuario_id == current_user.id, Turno.estado == 'abierto').first()
        if not turno:
            raise HTTPException(status_code=400, detail="No tienes un turno abierto para cerrar")

    # Si el turno está abierto, cerrarlo (fecha_fin + estado)
    if turno.estado == 'abierto':
        turno.estado = 'cerrado'
        turno.fecha_fin = datetime.now()
        try:
            db.commit()
            db.refresh(turno)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al cerrar turno: {str(e)}")

    # Calcular totales a partir de tickets asociados al turno
    total_vehiculos = db.query(func.count(Ticket.id)).filter(Ticket.turno_id == turno.id, Ticket.estado == 'cerrado').scalar() or 0
    total_recaudado = db.query(func.coalesce(func.sum(Ticket.monto_total), 0)).filter(Ticket.turno_id == turno.id, Ticket.estado == 'cerrado').scalar() or 0

    # Crear registro de cierre
    cierre = CierreCaja(
        turno_id=turno.id,
        total_vehiculos=int(total_vehiculos),
        total_recaudado=float(total_recaudado),
        fecha_cierre=datetime.now(),
        observaciones=payload.observaciones
    )
    db.add(cierre)
    try:
        db.commit()
        db.refresh(cierre)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear cierre: {str(e)}")

    return cierre

@cierre_router.get("/", response_model=List[CierreResponse])
def listar_cierres(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Lista cierres. Admin ve todos, usuarios normales ven solo los cierres de sus turnos.
    """
    if current_user.rol == 'admin':
        cierres = db.query(CierreCaja).order_by(CierreCaja.created_at.desc()).all()
    else:
        # obtener cierres cuyos turnos pertenecen al usuario
        cierres = (
            db.query(CierreCaja)
            .join(Turno, CierreCaja.turno_id == Turno.id)
            .filter(Turno.usuario_id == current_user.id)
            .order_by(CierreCaja.created_at.desc())
            .all()
        )
    return cierres

@cierre_router.get("/{cierre_id}", response_model=CierreResponse)
def obtener_cierre(cierre_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cierre = db.query(CierreCaja).filter(CierreCaja.id == cierre_id).first()
    if not cierre:
        raise HTTPException(status_code=404, detail="Cierre no encontrado")
    # permiso: admin o propietario del turno
    turno = db.query(Turno).filter(Turno.id == cierre.turno_id).first()
    if current_user.rol != 'admin' and turno and turno.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para ver este cierre")
    return cierre

@cierre_router.delete("/{cierre_id}", status_code=204)
def eliminar_cierre(cierre_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    cierre = db.query(CierreCaja).filter(CierreCaja.id == cierre_id).first()
    if not cierre:
        raise HTTPException(status_code=404, detail="Cierre no encontrado")
    db.delete(cierre)
    db.commit()
    return None