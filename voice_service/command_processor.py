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
        
        # Comandos generales (requieren autenticación)
        elif query_type == "list_users":
            return get_users_list(user_jwt)
        
        elif query_type == "search_plate":
            plate = intent.get("plate")
            if not plate:
                return "Por favor, especifica una placa para buscar. Ejemplo: 'Buscar placa ABC123'"
            return search_vehicle_by_plate(plate, user_jwt)
        
        elif query_type == "available_spaces":
            return get_available_spaces()
        
        elif query_type == "last_detection":
            return get_last_detection(user_jwt)
        
        else:
            return "Lo siento, no entendí tu comando. Intenta preguntarme: ¿Cuántos carros hay? o Buscar placa ABC123"
    
    except Exception as e:
        logger.error(f"❌ Error procesando comando: {e}")
        return f"Lo siento, hubo un error al procesar tu solicitud: {str(e)}"

# ========== FUNCIONES PARA COMANDOS GENERALES (usan API Key) ==========

def search_vehicle_by_plate(plate: str, user_jwt: str) -> str:
    """Busca un vehículo por placa y muestra su estado actual con datos del propietario"""
    try:
        ticket = backend_client.search_ticket_by_plate(plate, user_jwt)
        
        if ticket is None:
            return f"No encontré ningún ticket abierto para la placa {plate} en tus turnos."
        
        # Construir respuesta con toda la información
        placa = ticket.get("placa", plate)
        estado = ticket.get("estado", "desconocido")
        hora_entrada = ticket.get("hora_entrada", "desconocida")
        
        response = f"La placa {placa} está {estado} en el parqueadero. Ingresó el {hora_entrada}."
        
        # Agregar información del cliente si existe
        cliente_nombre = ticket.get("cliente_nombre")
        cliente_telefono = ticket.get("cliente_telefono")
        
        if cliente_nombre:
            response += f" Propietario: {cliente_nombre}."
            if cliente_telefono:
                response += f" Teléfono: {cliente_telefono}."
        else:
            response += " No hay datos de propietario registrados."
        
        return response
    
    except Exception as e:
        logger.error(f"Error buscando placa {plate}: {e}")
        return f"No pude buscar la placa {plate}. Error: {str(e)}"

def get_available_spaces() -> str:
    """Obtiene cupos disponibles (simulado)"""
    # TODO: Implementar cuando se tenga endpoint de cupos reales
    return "Los cupos disponibles se mostrarán en la próxima actualización."


def get_last_detection(user_jwt: str) -> str:
    """Obtiene el último ticket creado en el turno del usuario"""
    try:
        tickets = backend_client.get_my_tickets(user_jwt)
        
        if not tickets:
            return "No hay tickets registrados en tu turno."
        
        # Ordenar por ID descendente para obtener el más reciente
        tickets_sorted = sorted(tickets, key=lambda x: x.get("id", 0), reverse=True)
        ultimo = tickets_sorted[0]
        
        placa = ultimo.get("placa", "desconocida")
        estado = ultimo.get("estado", "desconocido")
        hora_entrada = ultimo.get("hora_entrada", "desconocida")
        
        response = f"El último ticket es de la placa {placa}, ingresó el {hora_entrada}, estado: {estado}."
        
        # Agregar info del cliente si existe
        cliente_nombre = ultimo.get("cliente_nombre")
        if cliente_nombre:
            response += f" Propietario: {cliente_nombre}."
        
        return response
    
    except Exception as e:
        logger.error(f"Error obteniendo último ticket: {e}")
        return "No pude obtener el último ticket."

def get_users_list(user_jwt: str) -> str:
    """Obtiene la lista de usuarios del sistema (requiere autenticación)"""
    try:
        usuarios = backend_client.get_users(user_jwt)
        
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
        
        response = f"Tienes {count} ticket{'s' if count != 1 else ''} en total. "
        
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
