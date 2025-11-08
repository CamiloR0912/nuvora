from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ClienteCreate(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    tipo_cliente: str = 'visitante'  # 'visitante' o 'abonado'

    class Config:
        from_attributes = True

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    tipo_cliente: Optional[str] = None

    class Config:
        from_attributes = True

class ClienteResponse(BaseModel):
    id: int
    nombre: str
    telefono: Optional[str]
    correo: Optional[str]
    tipo_cliente: str
    created_at: datetime

    class Config:
        from_attributes = True