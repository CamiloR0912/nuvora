# 🚀 Guía Rápida de Inicio

## Para Desarrollo Local

### 1. Configurar Variables de Entorno

```bash
# En voice_service/
cp .env.example .env
```

Edita `.env` si necesitas cambiar el BACKEND_URL.

### 2. Instalar Dependencias

```bash
cd voice_service
pip install -r requirements.txt
```

### 3. Levantar el Backend

```bash
# En una terminal
cd nuvora-backend
uvicorn main:app --reload --port 8000
```

### 4. Levantar el Voice Service

```bash
# En otra terminal
cd voice_service
uvicorn app:app --reload --port 8003
```

### 5. Probar Autenticación

```bash
# En otra terminal
cd voice_service
python test_service_auth.py
```

### 6. Probar Comando de Voz

```bash
cd voice_service
python test_audio.py record
```

---

## Con Docker Compose

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs del voice service
docker-compose logs -f voice_service

# Ver logs del backend
docker-compose logs -f backend

# Probar desde dentro del contenedor
docker exec -it smartpark-voice python test_service_auth.py
```

---

## ⚠️ Troubleshooting

### Error: "API Key inválida"

Verifica que `SERVICE_API_KEY` sea la misma en:
- `docker-compose.yml` → backend environment
- `docker-compose.yml` → voice_service environment

### Error: "Connection refused"

- **Local**: Verifica que backend esté en `http://localhost:8000`
- **Docker**: Usa `http://smartpark-backend:8000` (nombre del servicio)

### Error: "No se han detectado vehículos"

Es normal si la base de datos está vacía. Agrega datos de prueba:
```bash
cd nuvora-backend
python scripts/seed_user.py
```

---

## 🎤 Comandos de Voz Soportados

- "¿Cuántos carros hay?"
- "¿Cuántos vehículos activos?"
- "Buscar placa ABC123"
- "Mostrar historial"
- "Estadísticas del día"
- "Última detección"
