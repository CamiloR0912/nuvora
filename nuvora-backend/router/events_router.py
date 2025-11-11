from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from config.db import SessionLocal
from config.auth import get_current_user_or_service
from model.users import User
from model.tickets import Ticket
from model.vehiculos import Vehiculo
from typing import Union
import asyncio
import json
import logging
from asyncio import Queue

logger = logging.getLogger(__name__)

events_router = APIRouter(prefix="/events", tags=["Events"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Variable global para almacenar la última detección
last_detection = {
    "placa": None,
    "timestamp": None,
    "vehicle_type": None
}

# Cola global para broadcast de eventos
event_queues = []

def update_last_detection(placa: str, timestamp: str, vehicle_type: str = "car"):
    """Actualiza la última detección y notifica a todos los clientes SSE"""
    global last_detection
    last_detection = {
        "placa": placa,
        "timestamp": timestamp,
        "vehicle_type": vehicle_type
    }
    logger.info(f"📡 Última detección actualizada: {placa}")
    
    # Broadcast a todas las colas SSE activas
    event_data = {
        "event_type": "vehicle_detected",
        "placa": placa,
        "timestamp": timestamp,
        "vehicle_type": vehicle_type
    }
    
    for queue in event_queues:
        try:
            queue.put_nowait(event_data)
            logger.info(f"📤 Evento enviado a cola SSE")
        except:
            pass

async def event_stream():
    """
    Genera eventos Server-Sent Events (SSE) para enviar actualizaciones en tiempo real.
    Usa una cola para recibir eventos de nuevas detecciones.
    """
    # Crear una cola para este cliente
    queue = Queue()
    event_queues.append(queue)
    
    try:
        logger.info(f"� SSE cliente conectado. Total clientes: {len(event_queues)}")
        
        while True:
            # Esperar eventos de la cola
            event_data = await queue.get()
            
            logger.info(f"� Enviando evento SSE a cliente: {event_data.get('placa')}")
            
            # Enviar evento SSE
            yield f"data: {json.dumps(event_data)}\n\n"
            
    except asyncio.CancelledError:
        logger.info("🔌 Cliente SSE desconectado")
    finally:
        # Remover la cola cuando el cliente se desconecte
        if queue in event_queues:
            event_queues.remove(queue)
        logger.info(f"📡 Cliente SSE removido. Clientes restantes: {len(event_queues)}")


@events_router.get("/stream")
async def stream_events():
    """
    Endpoint SSE que envía eventos de detección de vehículos en tiempo real.
    Acceso público (sin autenticación) ya que solo envía notificaciones de detección.
    
    NOTA: EventSource no soporta headers personalizados, por lo que no podemos
    requerir autenticación JWT en este endpoint.
    """
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Desactiva buffering en Nginx
            "Access-Control-Allow-Origin": "*",  # Permitir CORS para SSE
        }
    )


@events_router.get("/last-detection")
def get_last_detection():
    """
    Devuelve la última detección de vehículo.
    Útil para sincronización inicial.
    Acceso público.
    """
    return last_detection
