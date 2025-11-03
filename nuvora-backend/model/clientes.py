from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func
from config.db import Base

CLIENT_TYPE = ('visitante', 'abonado')


class Cliente(Base):
	__tablename__ = 'clientes'

	id = Column(Integer, primary_key=True, index=True)
	nombre = Column(String(100), nullable=False)
	telefono = Column(String(15), nullable=True)
	correo = Column(String(100), nullable=True)
	tipo_cliente = Column(Enum(*CLIENT_TYPE, name='tipo_cliente'), nullable=False, default='visitante')
	created_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
