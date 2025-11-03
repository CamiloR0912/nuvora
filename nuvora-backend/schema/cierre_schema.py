from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CierreCreate(BaseModel):
    turno_id: Optional[int] = None
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
