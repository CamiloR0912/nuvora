from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from config.db import Base

class Configuracion(Base):
    __tablename__ = 'configuracion'

    id = Column(Integer, primary_key=True, index=True)
    total_cupos = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False)