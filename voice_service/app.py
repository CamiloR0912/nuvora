from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import whisper
import tempfile
import os
import logging
from langchain_module import interpret
from command_processor import process_command_with_auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Command Service", version="1.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://nuvora", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar modelo Whisper al iniciar
try:
    logger.info("🔄 Cargando modelo Whisper medium (esto puede tardar unos minutos la primera vez)...")
    model = whisper.load_model("medium")
    logger.info("✅ Modelo Whisper medium cargado correctamente")
except Exception as e:
    logger.error(f"❌ Error al cargar Whisper: {e}")
    model = None

@app.get("/")
def root():
    return {
        "service": "Voice Command Service",
        "status": "running",
        "model_loaded": model is not None
    }

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe un archivo de audio a texto usando Whisper.
    
    Formatos soportados: wav, mp3, m4a, ogg, etc.
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo Whisper no está cargado")
    
    try:
        # Validar tipo de archivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nombre de archivo inválido")
        
        logger.info(f"📝 Recibiendo archivo: {file.filename}")
        
        # Guardar archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        logger.info(f"🎤 Transcribiendo audio...")
        
        # Transcribir el audio
        result = model.transcribe(tmp_path, language="es", fp16=False)
        
        # Limpiar archivo temporal
        os.unlink(tmp_path)
        
        transcription = result["text"].strip()
        logger.info(f"✅ Transcripción: {transcription}")
        
        return {
            "success": True,
            "text": transcription,
            "language": result.get("language", "es")
        }
        
    except FileNotFoundError as e:
        logger.error(f"❌ Error: ffmpeg no encontrado - {e}")
        raise HTTPException(
            status_code=500,
            detail="ffmpeg no está instalado. Instala ffmpeg para procesar audio."
        )
    except Exception as e:
        logger.error(f"❌ Error al transcribir: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al transcribir el audio: {str(e)}"
        )

@app.post("/voice-command")
async def voice_command(
    file: UploadFile = File(...),
    authorization: str = Header(..., alias="Authorization")
):
    """
    Endpoint completo: recibe audio con JWT obligatorio, transcribe, interpreta y ejecuta el comando.
    
    Flujo:
    1. Audio → Whisper → Texto
    2. Texto → LangChain → Intención
    3. Intención → Backend → Respuesta (con JWT del usuario)
    
    Headers:
    - Authorization: Bearer <token> (REQUERIDO)
    
    Raises:
    - 401: Si no se proporciona token JWT
    - 500: Si hay errores en el procesamiento
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo Whisper no está cargado")
    
    # Validar y extraer JWT
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Token de autenticación inválido. Use: 'Bearer <token>'"
        )
    
    user_jwt = authorization.replace("Bearer ", "")
    logger.info("🔐 Token JWT recibido del usuario")
    
    try:
        logger.info(f"🎤 Procesando comando de voz: {file.filename}")
        
        # 1. Transcribir audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        result = model.transcribe(tmp_path, language="es", fp16=False)
        os.unlink(tmp_path)
        
        text = result["text"].strip()
        logger.info(f"📝 Transcripción: {text}")
        
        # 2. Interpretar comando
        intent = interpret(text)
        logger.info(f"🧠 Intención: {intent}")
        
        # 3. Procesar con autenticación de usuario
        response = process_command_with_auth(text, intent, user_jwt)
        logger.info(f"✅ Respuesta: {response}")
        
        return {
            "success": True,
            "query": text,
            "intent": intent,
            "response": response
        }
        
    except Exception as e:
        logger.error(f"❌ Error procesando comando de voz: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando comando: {str(e)}"
        )

@app.get("/health")
def health_check():
    """Verifica el estado del servicio"""
    return {
        "status": "healthy",
        "whisper_model": "medium" if model else "not_loaded"
    }