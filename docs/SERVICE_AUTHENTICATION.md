# 🔐 Autenticación entre Microservicios - Nuvora

## 📋 Problema

Tu **Voice Service** necesita consultar endpoints del **Backend** que están protegidos con JWT, pero:
- El Voice Service no es un usuario, es otro microservicio
- No tiene credenciales de login
- Necesita acceso programático constante

## ✅ Solución: API Key para Service-to-Service

Implementamos un sistema de autenticación dual:
- **Usuarios** → JWT (Bearer Token)
- **Servicios internos** → API Key (X-API-Key header)

---

## 🏗️ Arquitectura

```
┌──────────────────┐                           ┌──────────────────┐
│  Voice Service   │                           │   Backend API    │
│                  │  HTTP Request             │                  │
│  • Whisper STT   │─────────────────────────>│  • FastAPI       │
│  • LangChain     │  Header:                  │  • SQLAlchemy    │
│  • HTTP Client   │  X-API-Key: secret123     │  • MySQL         │
└──────────────────┘                           └──────────────────┘
         │                                              │
         │                                              │
         ▼                                              ▼
    Consultas de voz                         Valida API Key
    "¿Cuántos carros?"                       Retorna datos
```

### Flujo de Autenticación

1. **Voice Service** hace request con header `X-API-Key`
2. **Backend** recibe y valida:
   - Si `X-API-Key` presente y válida → ✅ Autorizado (modo servicio)
   - Si `Authorization: Bearer <jwt>` válido → ✅ Autorizado (modo usuario)
   - Si ninguno → ❌ 401 Unauthorized
3. **Backend** procesa y retorna datos

---

## 🔧 Implementación

### 1. Backend: Autenticación Dual

**Archivo**: `nuvora-backend/config/auth.py`

Ya tienes implementado:

```python
# Variable de entorno para API Key
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "dev-service-key-change-in-prod")

# Función para validar solo API Key
def verify_service_api_key(x_api_key: str = Header(...)) -> bool:
    if x_api_key != SERVICE_API_KEY:
        raise HTTPException(status_code=401, detail="API Key inválida")
    return True

# Función para aceptar JWT o API Key
def get_current_user_or_service(
    token: Optional[str] = Depends(oauth2_scheme),
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Union[User, str]:
    # Valida API Key o JWT
    # Retorna User object o "service"
```

### 2. Voice Service: Cliente HTTP

**Archivo**: `voice_service/http_client.py`

```python
class BackendClient:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.api_key = SERVICE_API_KEY
        self.headers = {
            "X-API-Key": self.api_key,  # 🔑 API Key automática
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method, endpoint, data=None, params=None):
        # Incluye automáticamente X-API-Key en todas las peticiones
        response = requests.request(
            method=method,
            url=f"{self.base_url}{endpoint}",
            headers=self.headers,  # 🔑 Header con API Key
            json=data,
            params=params
        )
        return response.json()
```

**Métodos disponibles**:
- `get_vehiculos_activos()` - Vehículos en parqueadero
- `get_vehiculos_historial()` - Vehículos que salieron
- `search_vehiculo_by_plate(plate)` - Buscar por placa
- `get_vehicle_events_count()` - Conteo de detecciones
- `get_vehicle_events_recent(limit)` - Últimas detecciones

### 3. Command Processor Actualizado

**Archivo**: `voice_service/command_processor.py`

```python
from http_client import backend_client

def get_active_vehicles_count() -> str:
    # ❌ Antes: requests.get() directo sin autenticación
    # ✅ Ahora: usa cliente con API Key
    activos = backend_client.get_vehiculos_activos()
    return f"Hay {len(activos)} vehículos actualmente."
```

---

## 🚀 Configuración

### Docker (Producción)

**`docker-compose.yml`**:

```yaml
services:
  backend:
    environment:
      SECRET_KEY: "your-super-secret-jwt-key-change-in-prod"
      SERVICE_API_KEY: "nuvora-service-key-2024-change-in-prod"
  
  voice_service:
    environment:
      BACKEND_URL: "http://smartpark-backend:8000"
      SERVICE_API_KEY: "nuvora-service-key-2024-change-in-prod"
```

### Local (Desarrollo)

**`voice_service/.env`**:

```bash
BACKEND_URL=http://localhost:8000
SERVICE_API_KEY=nuvora-service-key-2024-change-in-prod
PORT=8003
```

> ⚠️ **IMPORTANTE**: En producción, cambia `SERVICE_API_KEY` por una clave única y segura.

---

## 🧪 Testing

### Test de Autenticación

```bash
cd voice_service
python test_service_auth.py
```

**Verifica**:
1. ✅ Acceso con API Key válida
2. ❌ Rechazo sin autenticación
3. ❌ Rechazo con API Key inválida
4. ✅ Múltiples endpoints

**Salida esperada**:
```
🔐 TEST DE AUTENTICACIÓN SERVICE-TO-SERVICE
============================================================
✅ Test 1: Autenticación con API Key válida
   ✓ Exitoso: 3 vehículos activos
❌ Test 2: Sin autenticación (debe fallar)
   ✓ Correctamente rechazado (401)
...
📊 RESUMEN: 5/5 tests exitosos
```

### Test de Voz Completo

```bash
cd voice_service
python test_audio.py record
```

Verifica el flujo completo:
1. Grabación de audio
2. Transcripción con Whisper
3. Interpretación con LangChain
4. **Consulta al backend con API Key** 🔑
5. Respuesta al usuario

---

## 📝 Uso en Routers del Backend

### Proteger endpoint para usuarios Y servicios

```python
from config.auth import get_current_user_or_service
from typing import Union

@router.get("/vehiculos/activos")
def get_activos(
    auth: Union[User, str] = Depends(get_current_user_or_service),
    db: Session = Depends(get_db)
):
    # auth puede ser:
    # - User object (si JWT válido)
    # - "service" (si API Key válida)
    
    vehiculos = db.query(Vehiculo).all()
    return vehiculos
```

### Solo para servicios internos

```python
from config.auth import verify_service_api_key

@router.post("/internal/process-batch")
def batch_process(
    api_key: bool = Depends(verify_service_api_key),
    db: Session = Depends(get_db)
):
    # Solo accesible con API Key
    # No permite JWT de usuarios
    ...
```

---

## 🛡️ Seguridad

### ✅ Ventajas
- **Simple**: Solo un header HTTP adicional
- **Sin DB extra**: No requiere tabla de API Keys
- **Flexible**: JWT para usuarios, API Key para servicios
- **Trazable**: Logs identifican llamadas de servicios

### ⚠️ Limitaciones
- **Clave compartida**: Todos los servicios usan la misma key
- **Sin rotación automática**: Cambiar clave requiere redeploy
- **Sin rate limiting**: No distingue entre servicios

### 🔒 Best Practices

1. **HTTPS en producción** - API Key viaja en headers
2. **Rotar claves** - Cambiar cada 3-6 meses
3. **Variables de entorno** - NUNCA hardcodear
4. **Logs de auditoría** - Registrar uso de API Key
5. **Claves por ambiente** - dev/staging/prod diferentes

---

## 🔄 Alternativas (Más Avanzadas)

### Service Token JWT
Cada servicio tiene su propio JWT de larga duración.
- ✅ Estándar, misma librería JWT
- ❌ Más complejo, gestión de tokens

### OAuth2 Client Credentials
Servicios obtienen tokens de un auth server.
- ✅ Estándar OAuth2, tokens expiran
- ❌ Requiere servidor OAuth2

### Service Mesh (Istio, Linkerd)
Autenticación con mTLS a nivel de red.
- ✅ Muy seguro, automático
- ❌ Requiere Kubernetes, muy complejo

### Red Interna sin Auth
Servicios en red privada sin autenticación.
- ✅ Simple
- ❌ Peligroso si hay vulnerabilidad

---

## 📊 Flujo Completo de tu Aplicación

```
👤 Usuario habla: "¿Cuántos carros hay?"
         │
         ▼
🎤 Whisper transcribe → "cuántos carros hay"
         │
         ▼
🧠 LangChain interpreta → {"query_type": "active_vehicles"}
         │
         ▼
📞 Command Processor llama backend_client.get_vehiculos_activos()
         │
         ▼
🔑 HTTP Client agrega header X-API-Key: nuvora-service-key-2024...
         │
         ▼
🌐 Request a http://backend:8000/vehiculos/activos
         │
         ▼
🔐 Backend valida API Key en config/auth.py
         │
         ▼
✅ Backend retorna: [{"placa": "ABC123", ...}, ...]
         │
         ▼
💬 Voice Service responde: "Hay 5 vehículos en el parqueadero"
         │
         ▼
🔊 TTS (Text-to-Speech) al usuario
```

---

## 🎯 Resumen

**¿Cómo accedes a endpoints protegidos desde otro microservicio?**

1. **Backend** acepta autenticación dual (JWT o API Key)
2. **Voice Service** incluye `X-API-Key` en todas sus peticiones
3. **Backend** valida la clave y retorna datos
4. **Voice Service** procesa y responde al usuario

**Clave compartida**: Ambos servicios conocen la misma `SERVICE_API_KEY` vía variables de entorno.

---

## 📚 Referencias

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [API Key Authentication](https://swagger.io/docs/specification/authentication/api-keys/)
- [Service-to-Service Auth Patterns](https://microservices.io/patterns/security/access-token.html)
