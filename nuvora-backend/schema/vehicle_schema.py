from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class VehiculoEntrada(BaseModel):
    placa: str
    fecha_entrada: Optional[datetime] = None


class VehiculoSalida(BaseModel):
    placa: str
    fecha_salida: datetime


class VehiculoActivoResponse(BaseModel):
    id: int
    placa: str
    fecha_entrada: datetime

    class Config:
        from_attributes = True


class VehiculoHistorialResponse(BaseModel):
    id: int
    placa: str
    fecha_entrada: datetime
    fecha_salida: datetime
    total_facturado: float

    class Config:
        from_attributes = True
