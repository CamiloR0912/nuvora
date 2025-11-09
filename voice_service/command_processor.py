import logging
from typing import Dict, Any
from http_client import backend_client

logger = logging.getLogger(__name__)

def process_command_with_auth(text: str, intent: Dict[str, Any], user_jwt: str) -> str:
    """
    Procesa el comando interpretado CON autenticación del usuario (JWT requerido).
    
    Args:
        text: Texto original del usuario
        intent: Intención interpretada (query_type, params)
        user_jwt: Token JWT del usuario autenticado
    
    Returns:
        Respuesta en texto natural
    """
    query_type = intent.get("query_type")
     
    try:
        # Comandos personalizados (requieren JWT del usuario)
        if query_type == "my_tickets":
            return get_my_tickets(user_jwt)
        
        elif query_type == "my_open_tickets":
            return get_my_open_tickets(user_jwt)
        
        elif query_type == "my_stats":
            return get_my_stats(user_jwt)
        
        # Comandos generales (usan API Key de servicio)
        elif query_type == "total_cars" or query_type == "active_vehicles":
            return get_active_vehicles_count()
        
        elif query_type == "list_users":
            return get_users_list()
        
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

# ========== FUNCIONES PARA COMANDOS GENERALES (usan API Key) ==========
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

def get_users_list() -> str:
    """Obtiene la lista de usuarios del sistema"""
    try:
        usuarios = backend_client.get_users()
        
        if usuarios is None:
            return "No pude conectarme con el sistema para obtener los usuarios."
        
        count = len(usuarios)
        
        if count == 0:
            return "No hay usuarios registrados en el sistema."
        
        # Contar por rol
        roles_count = {}
        for user in usuarios:
            rol = user.get("rol", "desconocido")
            roles_count[rol] = roles_count.get(rol, 0) + 1
        
        # Construir respuesta
        response = f"Hay {count} usuario{'s' if count != 1 else ''} registrado{'s' if count != 1 else ''} en el sistema. "
        
        if roles_count:
            roles_text = ", ".join([f"{count} {rol}{'s' if count != 1 else ''}" for rol, count in roles_count.items()])
            response += f"Distribuidos en: {roles_text}."
        
        return response
    
    except Exception as e:
        logger.error(f"Error obteniendo lista de usuarios: {e}")
        return "No pude obtener la lista de usuarios del sistema."

# ========== FUNCIONES CON AUTENTICACIÓN DE USUARIO ==========

def get_my_tickets(user_jwt: str) -> str:
    """Obtiene los tickets del usuario autenticado"""
    try:
        tickets = backend_client.get_my_tickets(user_jwt)
        
        if tickets is None:
            return "No pude conectarme con el sistema para obtener tus tickets."
        
        count = len(tickets)
        
        if count == 0:
            return "No tienes tickets registrados."
        
        # Contar por estado
        abiertos = sum(1 for t in tickets if t.get("estado") == "abierto")
        cerrados = sum(1 for t in tickets if t.get("estado") == "cerrado")
        
        response = f"Tienes {count} ticket{'s' if count != 1 else ''} en total. "
        
        if abiertos > 0:
            response += f"{abiertos} abierto{'s' if abiertos != 1 else ''}, "
        if cerrados > 0:
            response += f"{cerrados} cerrado{'s' if cerrados != 1 else ''}."
        
        # Agregar total facturado
        total_facturado = sum(t.get("monto_total", 0) for t in tickets if t.get("monto_total"))
        if total_facturado > 0:
            response += f" Total facturado: ${total_facturado:,.0f}."
        
        return response
    
    except Exception as e:
        logger.error(f"Error obteniendo mis tickets: {e}")
        return "No pude obtener tus tickets."

def get_my_open_tickets(user_jwt: str) -> str:
    """Obtiene solo los tickets abiertos del usuario"""
    try:
        tickets = backend_client.get_my_open_tickets(user_jwt)
        
        if tickets is None:
            return "No pude conectarme con el sistema."
        
        count = len(tickets)
        
        if count == 0:
            return "No tienes tickets abiertos en este momento."
        
        response = f"Tienes {count} ticket{'s' if count != 1 else ''} abierto{'s' if count != 1 else ''}."
        
        # Mostrar placas de los tickets abiertos
        if count > 0 and count <= 5:
            placas = []
            for ticket in tickets:
                # Buscar el vehículo asociado
                vehiculo_id = ticket.get("vehiculo_id")
                if vehiculo_id:
                    placa = ticket.get("placa", "desconocida")
                    placas.append(placa)
            
            if placas:
                response += f" Placas: {', '.join(placas)}."
        
        return response
    
    except Exception as e:
        logger.error(f"Error obteniendo tickets abiertos: {e}")
        return "No pude obtener tus tickets abiertos."

def get_my_stats(user_jwt: str) -> str:
    """Obtiene estadísticas del usuario autenticado"""
    try:
        tickets = backend_client.get_my_tickets(user_jwt)
        
        if tickets is None:
            return "No pude obtener tus estadísticas."
        
        total = len(tickets)
        abiertos = sum(1 for t in tickets if t.get("estado") == "abierto")
        cerrados = sum(1 for t in tickets if t.get("estado") == "cerrado")
        total_facturado = sum(t.get("monto_total", 0) for t in tickets if t.get("monto_total"))
        
        if total == 0:
            return "No tienes actividad registrada en tu turno."
        
        response = f"Resumen de tu turno: {total} ticket{'s' if total != 1 else ''} procesado{'s' if total != 1 else ''}. "
        response += f"{abiertos} abierto{'s' if abiertos != 1 else ''}, {cerrados} cerrado{'s' if cerrados != 1 else ''}. "
        
        if total_facturado > 0:
            response += f"Total recaudado: ${total_facturado:,.0f}."
        
        return response
    
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return "No pude obtener tus estadísticas."
