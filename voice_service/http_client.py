"""
Cliente HTTP para comunicación entre microservicios
con autenticación mediante API Key
"""
import os
import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Configuración del backend
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "nuvora-service-key-2024-change-in-prod")


class BackendClient:
    """Cliente para hacer peticiones al backend con autenticación de servicio"""
    
    def __init__(self):
        self.base_url = BACKEND_URL
        self.api_key = SERVICE_API_KEY
    
    def _get_headers(self, user_jwt: Optional[str] = None) -> Dict[str, str]:
        """
        Genera headers de autenticación:
        - Si hay JWT de usuario: usa JWT (para endpoints que requieren usuario específico)
        - Si no hay JWT: usa API Key de servicio (para endpoints generales)
        """
        if user_jwt:
            return {
                "Authorization": f"Bearer {user_jwt}",
                "Content-Type": "application/json"
            }
        else:
            return {
                "X-API-Key": self.api_key,
                "Content-Type": "application/json"
            }
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[Any, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        user_jwt: Optional[str] = None
    ) -> Optional[Dict[Any, Any]]:
        """
        Hace una petición HTTP al backend
        
        Args:
            method: GET, POST, PUT, DELETE
            endpoint: Ruta del endpoint (ej: /tickets)
            data: Datos para enviar en el body (POST/PUT)
            params: Query parameters (GET)
            user_jwt: Token JWT del usuario (opcional)
        
        Returns:
            Respuesta JSON o None si hay error
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(user_jwt)
        
        try:
            logger.info(f"🌐 {method} {url}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP Error {e.response.status_code}: {e.response.text}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Error de conexión con {url}")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout en petición a {url}")
            return None
        except Exception as e:
            logger.error(f"❌ Error inesperado: {str(e)}")
            return None
    
    # ========== MÉTODOS PARA VEHÍCULOS ==========
    
    def get_vehiculos_activos(self) -> Optional[list]:
        """Obtiene lista de vehículos activos en el parqueadero"""
        result = self._make_request("GET", "/vehiculos/activos")
        return result if result else []
    
    def get_vehiculos_historial(self) -> Optional[list]:
        """Obtiene historial de vehículos que ya salieron"""
        result = self._make_request("GET", "/vehiculos/historial")
        return result if result else []
    
    def search_vehiculo_by_plate(self, plate: str) -> Optional[Dict[Any, Any]]:
        """Busca un vehículo específico por placa en activos e historial"""
        # Buscar en activos
        activos = self.get_vehiculos_activos()
        if activos:
            for v in activos:
                if v.get("placa", "").upper() == plate.upper():
                    return v
        
        # Buscar en historial
        historial = self.get_vehiculos_historial()
        if historial:
            for v in historial:
                if v.get("placa", "").upper() == plate.upper():
                    return v
        
        return None
    
    # ========== MÉTODOS PARA TICKETS ==========
    
    def get_tickets(
        self, 
        estado: Optional[str] = None,
        limit: int = 100,
        user_jwt: Optional[str] = None
    ) -> Optional[list]:
        """
        Obtiene tickets con filtros opcionales.
        Si se proporciona user_jwt, obtiene los tickets del usuario autenticado.
        Si no, usa API Key de servicio.
        """
        params = {"limit": limit}
        if estado:
            params["estado"] = estado
        
        result = self._make_request("GET", "/tickets/", params=params, user_jwt=user_jwt)
        return result if result else []
    
    def get_my_tickets(self, user_jwt: str) -> Optional[list]:
        """
        Obtiene los tickets del usuario autenticado.
        Requiere JWT del usuario.
        """
        return self.get_tickets(user_jwt=user_jwt)
    
    def get_my_open_tickets(self, user_jwt: str) -> Optional[list]:
        """
        Obtiene solo los tickets abiertos del usuario autenticado.
        Requiere JWT del usuario.
        """
        tickets = self.get_tickets(user_jwt=user_jwt)
        if tickets:
            return [t for t in tickets if t.get("estado") == "abierto"]
        return []
    
    def get_ticket_by_id(self, ticket_id: int) -> Optional[Dict[Any, Any]]:
        """Obtiene un ticket específico"""
        result = self._make_request("GET", f"/tickets/{ticket_id}")
        return result
    
    # ========== MÉTODOS PARA EVENTOS DE VEHÍCULOS ==========
    
    def get_vehicle_events_count(self) -> int:
        """Obtiene el conteo de eventos de vehículos detectados"""
        result = self._make_request("GET", "/vehicle-events/count")
        if result:
            return result.get("count", 0)
        return 0
    
    def get_vehicle_events_recent(self, limit: int = 10) -> Optional[list]:
        """Obtiene eventos recientes de vehículos"""
        result = self._make_request("GET", "/vehicle-events/latest", params={"limit": limit})
        return result if result else []
    
    # ========== MÉTODOS PARA CLIENTES ==========
    
    def get_clientes(self, limit: int = 100) -> Optional[list]:
        """Obtiene lista de clientes"""
        result = self._make_request("GET", "/clientes", params={"limit": limit})
        return result if result else []
    
    def search_cliente_by_name(self, nombre: str) -> Optional[list]:
        """Busca clientes por nombre"""
        result = self._make_request("GET", "/clientes/search", params={"nombre": nombre})
        return result if result else []
    
    # ========== MÉTODOS PARA USUARIOS ==========
    
    def get_users(self) -> Optional[list]:
        """Obtiene todos los usuarios del sistema"""
        result = self._make_request("GET", "/users/")
        return result if result else []


# Singleton para reutilizar en toda la aplicación
backend_client = BackendClient()
