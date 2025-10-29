from fastapi import FastAPI
from router.user_router import user
from router.vehicle_router import vehiculo
from config.db import Base, engine
from threading import Thread
from consumer import VehicleEventConsumer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SmartPark API", redirect_slashes=False)

Base.metadata.create_all(bind=engine)

app.include_router(user)
app.include_router(vehiculo)

def start_rabbitmq_consumer():
    """Inicia el consumidor de RabbitMQ en un thread separado"""
    try:
        logger.info("🐰 Iniciando consumidor de RabbitMQ...")
        consumer = VehicleEventConsumer()
        consumer.start()
    except Exception as e:
        logger.error(f"❌ Error al iniciar consumidor de RabbitMQ: {e}")

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    logger.info("🚀 Iniciando SmartPark API...")
    
    # Iniciar el consumidor de RabbitMQ en un thread separado
    consumer_thread = Thread(target=start_rabbitmq_consumer, daemon=True)
    consumer_thread.start()
    logger.info("✅ Consumidor de RabbitMQ iniciado en background")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento que se ejecuta al cerrar la aplicación"""
    logger.info("👋 Cerrando SmartPark API...")

@app.get("/api/points")
def get_points():
    return {...}

@app.get("/")
def root():
    return {
        "message": "SmartPark API",
        "status": "running",
        "services": {
            "rabbitmq_consumer": "active"
        }
    }