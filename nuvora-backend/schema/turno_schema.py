from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TurnoCreate(BaseModel):
	usuario_id: Optional[int] = None
	fecha_inicio: Optional[datetime] = None
	monto_inicial: Optional[float] = 0.0
	observaciones: Optional[str] = None


class TurnoResponse(BaseModel):
	id: int
	usuario_id: Optional[int]
	fecha_inicio: datetime
	fecha_fin: Optional[datetime]
	monto_inicial: Optional[float]
	monto_total: Optional[float]
	estado: str
	observaciones: Optional[str]

	class Config:
		from_attributes = True
