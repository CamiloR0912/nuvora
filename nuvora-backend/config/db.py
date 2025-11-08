from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Usar variable de entorno o valor por defecto
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:12345679@db:3306/test4")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

meta_data = MetaData()

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()