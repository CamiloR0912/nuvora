from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CierreCreate(BaseModel):
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True

class CierreResponse(BaseModel):
    id: int
    turno_id: int
    total_vehiculos: int
    total_recaudado: float
    fecha_cierre: datetime
    observaciones: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CierreConTokenResponse(BaseModel):
    """Respuesta al crear un cierre, incluye el cierre y un nuevo token JWT sin turno_id"""
    id: int
    turno_id: int
    total_vehiculos: int
    total_recaudado: float
    fecha_cierre: datetime
    observaciones: Optional[str]
    created_at: datetime
    access_token: str  # Nuevo token SIN turno_id
    token_type: str = "bearer"

    class Config:
        from_attributes = True
