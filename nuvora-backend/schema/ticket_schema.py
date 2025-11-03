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
    hora_entrada: datetime
    hora_salida: Optional[datetime]
    monto_total: Optional[float]
    estado: str

    class Config:
        from_attributes = True
