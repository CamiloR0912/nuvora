from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class VehicleEventCreate(BaseModel):
    """Schema para crear un evento de vehículo"""
    vehicle_type: str = Field(..., description="Tipo de vehículo (car, motorcycle, bus, truck)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza de la detección (0-1)")
    timestamp: datetime = Field(..., description="Momento de la detección")
    location: Optional[Dict[str, Any]] = Field(None, description="Coordenadas del vehículo en el frame")
    plate_number: Optional[str] = Field(None, max_length=20, description="Placa detectada por OCR")


class VehicleEventUpdate(BaseModel):
    """Schema para actualizar un evento de vehículo"""
    vehicle_type: Optional[str] = Field(None, description="Tipo de vehículo")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confianza de la detección")
    timestamp: Optional[datetime] = Field(None, description="Momento de la detección")
    location: Optional[Dict[str, Any]] = Field(None, description="Coordenadas del vehículo")
    plate_number: Optional[str] = Field(None, max_length=20, description="Placa detectada")


class VehicleEventResponse(BaseModel):
    """Schema de respuesta para eventos de vehículos"""
    id: int
    vehicle_type: str
    confidence: float
    timestamp: datetime
    location: Optional[Dict[str, Any]]
    plate_number: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class VehicleEventFilter(BaseModel):
    """Schema para filtrar eventos de vehículos"""
    vehicle_type: Optional[str] = None
    plate_number: Optional[str] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
