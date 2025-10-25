from sqlalchemy import Column, Integer, String, DateTime, Float
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
