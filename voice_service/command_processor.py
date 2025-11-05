import logging
from typing import Dict, Any
from http_client import backend_client

logger = logging.getLogger(__name__)

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
    """Obtiene el número de vehículos activos"""
    try:
        activos = backend_client.get_vehiculos_activos()
        if activos is None:
            return "No pude conectarme con el sistema de parqueo."
        
        count = len(activos)
        
        if count == 0:
            return "No hay vehículos en el parqueadero actualmente."
        elif count == 1:
            return "Hay 1 vehículo en el parqueadero."
        else:
            return f"Hay {count} vehículos en el parqueadero actualmente."
    
    except Exception as e:
        logger.error(f"Error al obtener conteo de vehículos: {e}")
        return "No pude obtener la información de vehículos activos."

def search_vehicle_by_plate(plate: str) -> str:
    """Busca un vehículo por placa"""
    try:
        vehiculo = backend_client.search_vehiculo_by_plate(plate)
        
        if vehiculo is None:
            return f"No encontré ningún vehículo con la placa {plate}."
        
        # Verificar si está en activos (tiene fecha_entrada pero no fecha_salida)
        if not vehiculo.get("fecha_salida"):
            fecha_entrada = vehiculo.get("fecha_entrada", "desconocida")
            return f"La placa {plate} está activa en el parqueadero. Ingresó el {fecha_entrada}."
        else:
            # Ya salió
            entrada = vehiculo.get("fecha_entrada", "desconocida")
            salida = vehiculo.get("fecha_salida", "desconocida")
            total = vehiculo.get("total_facturado", 0)
            return f"La placa {plate} ya salió. Ingresó el {entrada}, salió el {salida}. Total: ${total:,.0f}"
    
    except Exception as e:
        logger.error(f"Error buscando placa {plate}: {e}")
        return f"No pude buscar la placa {plate}."

def get_history_summary() -> str:
    """Obtiene un resumen del historial"""
    try:
        historial = backend_client.get_vehiculos_historial()
        if historial is None:
            return "No pude obtener el historial."
        
        count = len(historial)
        
        if count == 0:
            return "No hay vehículos en el historial todavía."
        
        total_facturado = sum(v.get("total_facturado", 0) for v in historial)
        
        return f"Hay {count} vehículos en el historial, con un total facturado de ${total_facturado:,.0f}."
    
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        return "No pude obtener el historial."

def get_daily_statistics() -> str:
    """Obtiene estadísticas del día"""
    try:
        activos = backend_client.get_vehiculos_activos()
        historial = backend_client.get_vehiculos_historial()
        
        if activos is None or historial is None:
            return "No pude obtener las estadísticas del día."
        
        total_activos = len(activos)
        total_historial = len(historial)
        total_facturado = sum(v.get("total_facturado", 0) for v in historial)
        
        return (f"Estadísticas del día: {total_activos} vehículos activos, "
                f"{total_historial} han salido, "
                f"recaudado ${total_facturado:,.0f}.")
    
    except Exception as e:
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
        events = backend_client.get_vehicle_events_recent(limit=1)
        
        if not events:
            return "No hay detecciones recientes."
        
        latest = events[0]
        plate = latest.get("license_plate", "desconocida")
        timestamp = latest.get("timestamp", "")
        camera = latest.get("camera_id", "desconocida")
        
        return f"La última placa detectada fue {plate} en la cámara {camera}, a las {timestamp}."
    
    except Exception as e:
        logger.error(f"Error obteniendo última detección: {e}")
        return "No pude obtener la última detección."
