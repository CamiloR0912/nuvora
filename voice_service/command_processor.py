import requests
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

# URL del backend (ajustar según entorno)
# Usa localhost cuando se ejecuta fuera de Docker, smartpark-backend dentro de Docker
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def process_command(text: str, intent: Dict[str, Any]) -> str:
    """
    Procesa el comando interpretado y genera una respuesta.
    
    Args:
        text: Texto original del usuario
        intent: Intención interpretada (query_type, params)
    
    Returns:
        Respuesta en texto natural
    """
    query_type = intent.get("query_type")
     
    try:
        if query_type == "total_cars" or query_type == "active_vehicles":
            return get_active_vehicles_count()
        
        elif query_type == "search_plate":
            plate = intent.get("plate")
            if not plate:
                return "Por favor, especifica una placa para buscar. Ejemplo: 'Buscar placa ABC123'"
            return search_vehicle_by_plate(plate)
        
        elif query_type == "history":
            return get_history_summary()
        
        elif query_type == "daily_stats":
            return get_daily_statistics()
        
        elif query_type == "available_spaces":
            return get_available_spaces()
        
        elif query_type == "entries_count":
            return get_entries_count()
        
        elif query_type == "last_detection":
            return get_last_detection()
        
        else:
            return "Lo siento, no entendí tu comando. Intenta preguntarme: ¿Cuántos carros hay? o Buscar placa ABC123"
    
    except Exception as e:
        logger.error(f"❌ Error procesando comando: {e}")
        return f"Lo siento, hubo un error al procesar tu solicitud: {str(e)}"

def get_active_vehicles_count() -> str:
    """Obtiene el número de vehículos detectados"""
    try:
        response = requests.get(f"{BACKEND_URL}/vehicle-events/count", timeout=5)
        response.raise_for_status()
        data = response.json()
        count = data.get("count", 0)
        
        if count == 0:
            return "No se han detectado vehículos aún."
        elif count == 1:
            return "Se ha detectado 1 vehículo."
        else:
            return f"Se han detectado {count} vehículos en total."
    
    except requests.RequestException as e:
        logger.error(f"Error al obtener conteo de vehículos: {e}")
        return "No pude obtener la información de vehículos detectados."

def search_vehicle_by_plate(plate: str) -> str:
    """Busca un vehículo por placa en activos e historial"""
    try:
        # Buscar en activos primero
        response_activos = requests.get(f"{BACKEND_URL}/vehiculos/activos", timeout=5)
        response_activos.raise_for_status()
        activos = response_activos.json()
        
        for vehiculo in activos:
            if vehiculo.get("placa", "").upper() == plate.upper():
                fecha_entrada = vehiculo.get("fecha_entrada", "desconocida")
                return f"La placa {plate} está activa. Ingresó el {fecha_entrada}."
        
        # Si no está en activos, buscar en historial
        response_historial = requests.get(f"{BACKEND_URL}/vehiculos/historial", timeout=5)
        response_historial.raise_for_status()
        historial = response_historial.json()
        
        for vehiculo in historial:
            if vehiculo.get("placa", "").upper() == plate.upper():
                entrada = vehiculo.get("fecha_entrada", "desconocida")
                salida = vehiculo.get("fecha_salida", "desconocida")
                total = vehiculo.get("total_facturado", 0)
                return f"La placa {plate} ya salió. Ingresó el {entrada}, salió el {salida}. Total: ${total:,.0f}"
        
        return f"No encontré ningún vehículo con la placa {plate}."
    
    except requests.RequestException as e:
        logger.error(f"Error buscando placa {plate}: {e}")
        return f"No pude buscar la placa {plate}."

def get_history_summary() -> str:
    """Obtiene un resumen del historial"""
    try:
        response = requests.get(f"{BACKEND_URL}/vehiculos/historial", timeout=5)
        response.raise_for_status()
        historial = response.json()
        count = len(historial)
        
        if count == 0:
            return "No hay vehículos en el historial todavía."
        
        total_facturado = sum(v.get("total_facturado", 0) for v in historial)
        
        return f"Hay {count} vehículos en el historial, con un total facturado de ${total_facturado:,.0f}."
    
    except requests.RequestException as e:
        logger.error(f"Error obteniendo historial: {e}")
        return "No pude obtener el historial."

def get_daily_statistics() -> str:
    """Obtiene estadísticas del día"""
    try:
        activos_resp = requests.get(f"{BACKEND_URL}/vehiculos/activos", timeout=5)
        historial_resp = requests.get(f"{BACKEND_URL}/vehiculos/historial", timeout=5)
        
        activos_resp.raise_for_status()
        historial_resp.raise_for_status()
        
        activos = activos_resp.json()
        historial = historial_resp.json()
        
        total_activos = len(activos)
        total_historial = len(historial)
        total_facturado = sum(v.get("total_facturado", 0) for v in historial)
        
        return (f"Estadísticas del día: {total_activos} vehículos activos, "
                f"{total_historial} han salido, "
                f"recaudado ${total_facturado:,.0f}.")
    
    except requests.RequestException as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return "No pude obtener las estadísticas del día."

def get_available_spaces() -> str:
    """Obtiene cupos disponibles (simulado)"""
    # Esto es simulado porque no tienes endpoint de cupos reales
    return "Los cupos disponibles se mostrarán en la próxima actualización."

def get_entries_count() -> str:
    """Cuenta entradas del día"""
    return get_active_vehicles_count()

def get_last_detection() -> str:
    """Obtiene la última detección de vehículo"""
    try:
        response = requests.get(f"{BACKEND_URL}/vehicle-events/recent?limit=1", timeout=5)
        response.raise_for_status()
        events = response.json()
        
        if not events:
            return "No hay detecciones recientes."
        
        latest = events[0]
        plate = latest.get("license_plate", "desconocida")
        timestamp = latest.get("timestamp", "")
        camera = latest.get("camera_id", "desconocida")
        
        return f"La última placa detectada fue {plate} en la cámara {camera}, a las {timestamp}."
    
    except requests.RequestException as e:
        logger.error(f"Error obteniendo última detección: {e}")
        return "No pude obtener la última detección."
