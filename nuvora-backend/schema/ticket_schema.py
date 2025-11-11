from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TicketEntrada(BaseModel):
    placa: str

    class Config:
        from_attributes = True


class TicketSalidaPorPlaca(BaseModel):
    placa: str

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    id: int
    vehiculo_id: int
    turno_id: Optional[int]
    turno_cierre_id: Optional[int] = None
    hora_entrada: datetime
    hora_salida: Optional[datetime]
    monto_total: Optional[float]
    estado: str

    class Config:
        from_attributes = True


class TicketDetailResponse(BaseModel):
    """Respuesta detallada de ticket con información del vehículo y cliente"""
    id: int
    vehiculo_id: int
    turno_id: Optional[int]
    turno_cierre_id: Optional[int] = None
    hora_entrada: datetime
    hora_salida: Optional[datetime]
    monto_total: Optional[float]
    estado: str
    # Información del vehículo
    placa: Optional[str] = None
    # Información del cliente (si existe)
    cliente_nombre: Optional[str] = None
    cliente_telefono: Optional[str] = None
    cliente_email: Optional[str] = None
    # Información del usuario que registró la entrada
    usuario_entrada_nombre: Optional[str] = None

    class Config:
        from_attributes = True
