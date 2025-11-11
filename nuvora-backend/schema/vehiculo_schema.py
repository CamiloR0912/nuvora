from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VehiculoActivoResponse(BaseModel):
    """Response para vehículos activos (tickets abiertos)"""
    id: int  # ID del ticket
    placa: str
    fecha_entrada: datetime
    espacio: Optional[str] = None  # Por ahora null, puedes implementarlo después
    turno_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class VehiculoHistorialResponse(BaseModel):
    """Response para vehículos en historial (tickets cerrados)"""
    id: int  # ID del ticket
    placa: str
    fecha_entrada: datetime
    fecha_salida: datetime
    total_facturado: float
    turno_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class VehiculoEntradaRequest(BaseModel):
    """Request para registrar entrada manual"""
    placa: str
    
    class Config:
        from_attributes = True


class VehiculoSalidaRequest(BaseModel):
    """Request para registrar salida manual"""
    placa: str
    fecha_salida: datetime
    
    class Config:
        from_attributes = True


class VehiculoBusquedaResponse(BaseModel):
    """Response para búsqueda de vehículo por placa"""
    vehiculo: Optional[VehiculoActivoResponse | VehiculoHistorialResponse]
    estado: str  # 'activo' o 'historial'
    
    class Config:
        from_attributes = True
