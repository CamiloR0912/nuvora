from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from config.db import Base
from datetime import datetime

class VehiculoActivo(Base):
    __tablename__ = "vehiculos_activos"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), unique=True, nullable=False)
    fecha_entrada = Column(DateTime, default=datetime.now, nullable=False)


class VehiculoHistorial(Base):
    __tablename__ = "vehiculos_historial"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), nullable=False)
    fecha_entrada = Column(DateTime, nullable=False)
    fecha_salida = Column(DateTime, nullable=False)
    total_facturado = Column(Float, nullable=False)


class Vehicle(Base):
    """Modelo para eventos de vehículos detectados por vision_service"""
    __tablename__ = "vehicle_events"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_type = Column(String(50), nullable=False)  # car, motorcycle, bus, truck
    confidence = Column(Float, nullable=False)  # confianza de la detección
    timestamp = Column(DateTime, nullable=False)  # momento de la detección
    location = Column(JSON, nullable=True)  # coordenadas del vehículo en el frame
    plate_number = Column(String(20), nullable=True)  # placa detectada por OCR
    created_at = Column(DateTime, default=datetime.now, nullable=False) 
