from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from config.db import SessionLocal
from config.auth import get_current_user, require_cajero
from model.users import User
from model.configuracion import Configuracion

configuracion_router = APIRouter(prefix="/configuracion", tags=["Configuración"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ConfiguracionResponse(BaseModel):
    id: int
    total_cupos: int

class ConfiguracionUpdate(BaseModel):
    total_cupos: int = Field(..., ge=0, description="Total de cupos del parqueadero")


@configuracion_router.get("/", response_model=ConfiguracionResponse)
def obtener_configuracion(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Obtiene la configuración actual (total de cupos). Crea registro por defecto si no existe."""
    conf = db.query(Configuracion).order_by(Configuracion.id.asc()).first()
    if not conf:
        conf = Configuracion(total_cupos=0)
        db.add(conf)
        db.commit()
        db.refresh(conf)
    return ConfiguracionResponse(id=conf.id, total_cupos=conf.total_cupos)


@configuracion_router.put("/", response_model=ConfiguracionResponse)
def actualizar_total_cupos(data: ConfiguracionUpdate, db: Session = Depends(get_db), cajero: User = Depends(require_cajero)):
    """Actualiza el total de cupos (requiere rol de cajero o superior)."""
    conf = db.query(Configuracion).order_by(Configuracion.id.asc()).first()
    if not conf:
        conf = Configuracion(total_cupos=data.total_cupos)
        db.add(conf)
    else:
        conf.total_cupos = data.total_cupos
    try:
        db.commit()
        db.refresh(conf)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar configuración: {str(e)}")
    return ConfiguracionResponse(id=conf.id, total_cupos=conf.total_cupos)