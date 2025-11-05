from fastapi import FastAPI
from router.user_router import user
from router.turno_router import turno_router
from router.ticket_router import ticket_router
from router.client_router import client_router
from router.vehicle_events_router import vehicle_events_router
from config.db import Base, engine
from threading import Thread
from consumer import VehicleEventConsumer
# Importar modelos para registrar tablas en metadata
import model.users
import model.clientes
import model.vehiculos
import model.turnos
import model.tickets
import model.cierres
import model.vehicles
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SmartPark API", redirect_slashes=False)

Base.metadata.create_all(bind=engine)

app.include_router(user)
app.include_router(turno_router)
app.include_router(ticket_router)
app.include_router(client_router)
app.include_router(vehicle_events_router)

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