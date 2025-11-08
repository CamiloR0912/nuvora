# 🎤 Voice Service - Nuvora

Servicio de comandos de voz para el sistema de parqueo inteligente Nuvora.

## 🌟 Características

- **🎙️ Transcripción de voz** con Whisper (OpenAI)
- **🧠 Interpretación inteligente** con LangChain + Ollama (opcional)
- **🔐 Autenticación segura** con API Key para comunicación con backend
- **📊 Consultas en tiempo real** al sistema de parqueo

## 🏗️ Arquitectura

```
Audio → Whisper → LangChain → Command Processor → Backend API
  ↓                                    ↓              ↓
Archivo    Texto        Intent      HTTP Client   Vehiculos DB
.wav      "cuántos?"   {type: ...}  (API Key)    Tickets DB
```

## 🔑 Autenticación

Este servicio usa **API Key** para autenticarse con el backend:

- Header: `X-API-Key: nuvora-service-key-2024-change-in-prod`
- Configurado en: `http_client.py`
- Variable de entorno: `SERVICE_API_KEY`

Ver [documentación completa](../docs/SERVICE_AUTHENTICATION.md).

## 🚀 Inicio Rápido

### 1. Configurar

```bash
cp .env.example .env
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar

```bash
uvicorn app:app --reload --port 8003
```

### 4. Probar

```bash
# Test de autenticación
python test_service_auth.py

# Test de voz
python test_audio.py record
```

## 📡 Endpoints

### POST `/transcribe`
Transcribe audio a texto usando Whisper.

**Request**: `multipart/form-data` con archivo de audio

**Response**:
```json
{
  "text": "cuántos carros hay",
  "language": "es"
}
```

### POST `/voice-command`
Procesa comando de voz completo (transcribe + interpreta + consulta).

**Request**: `multipart/form-data` con archivo de audio

**Response**:
```json
{
  "query": "cuántos carros hay",
  "intent": {"query_type": "active_vehicles"},
  "response": "Hay 5 vehículos en el parqueadero actualmente."
}
```

## 🎯 Comandos Soportados

| Comando | Acción |
|---------|--------|
| "¿Cuántos carros hay?" | Cuenta vehículos activos |
| "Buscar placa ABC123" | Busca vehículo por placa |
| "Mostrar historial" | Resume vehículos que salieron |
| "Estadísticas del día" | Stats de activos + facturación |
| "Última detección" | Última placa detectada |

## 🔧 Configuración

### Variables de Entorno

```bash
# Backend
BACKEND_URL=http://localhost:8000

# Autenticación
SERVICE_API_KEY=nuvora-service-key-2024-change-in-prod

# Puerto
PORT=8003
```

### Docker

El servicio se incluye automáticamente en `docker-compose.yml`:

```bash
docker-compose up voice_service
```

## 📝 Estructura

```
voice_service/
├── app.py                    # FastAPI app principal
├── command_processor.py      # Lógica de comandos
├── langchain_module.py       # Interpretación con LLM
├── http_client.py           # Cliente HTTP con API Key 🔑
├── test_audio.py            # Test de audio
├── test_service_auth.py     # Test de autenticación 🔐
├── requirements.txt
├── .env.example
└── Dockerfile
```

## 🧪 Testing

### Test de Autenticación
```bash
python test_service_auth.py
```

Verifica:
- ✅ Autenticación con API Key válida
- ❌ Rechazo sin autenticación
- ❌ Rechazo con API Key incorrecta

### Test de Voz
```bash
# Grabar nuevo audio
python test_audio.py record

# Usar archivo existente
python test_audio.py audio.wav
```

## 🔐 Seguridad

- ✅ API Key para autenticación service-to-service
- ✅ Variables de entorno (no hardcoded)
- ✅ Timeout en peticiones HTTP (10s)
- ✅ Manejo de errores de conexión

## 📚 Documentación

- [Autenticación Service-to-Service](../docs/SERVICE_AUTHENTICATION.md)
- [Guía de Inicio Rápido](../docs/QUICK_START.md)

## 🤝 Integración con Backend

El Voice Service consulta estos endpoints del backend:

- `GET /vehiculos/activos` - Lista vehículos en parqueadero
- `GET /vehiculos/historial` - Historial de salidas
- `GET /vehicle-events/count` - Conteo de detecciones
- `GET /vehicle-events/latest` - Últimas detecciones

Todos protegidos con la misma `SERVICE_API_KEY`.

## 🐛 Troubleshooting

### "API Key inválida"
Verifica que `SERVICE_API_KEY` sea igual en backend y voice_service.

### "Connection refused"
- Local: Usa `BACKEND_URL=http://localhost:8000`
- Docker: Usa `BACKEND_URL=http://smartpark-backend:8000`

### "No se detectaron vehículos"
Base de datos vacía. Agrega datos de prueba en el backend.

## 📦 Dependencias Principales

- `fastapi` - Framework web
- `uvicorn` - ASGI server
- `openai-whisper` - Speech-to-text
- `requests` - HTTP client
- `sounddevice` - Audio recording
- `python-dotenv` - Environment variables

## 🚀 Roadmap

- [ ] Autenticación con tokens JWT de servicio
- [ ] Rate limiting por servicio
- [ ] Rotación automática de API Keys
- [ ] Soporte para más idiomas
- [ ] Comandos personalizados por voz
- [ ] TTS (Text-to-Speech) para respuestas
