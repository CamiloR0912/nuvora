from ultralytics import YOLO
import cv2
import easyocr
from rabbitmq_producer import RabbitMQProducer
from datetime import datetime
import logging, time, re, os, sys
from collections import defaultdict, Counter
from difflib import SequenceMatcher
from jose import jwt, JWTError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar modelo YOLO
model = YOLO("yolov8n.pt")

# Inicializar OCR
ocr = easyocr.Reader(['en'])

# Inicializar RabbitMQ Producer
rabbitmq_producer = RabbitMQProducer()
rabbitmq_producer.connect()

# Verificar token JWT
JWT_TOKEN = os.getenv('VISION_SERVICE_JWT_TOKEN', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4IiwidHVybm9faWQiOjMsImV4cCI6MTc2MjcxMTU1NX0.JsxFpDRbZ_EoP1h1tUPqtMEmWIo1aKDIy0W2Iowkq8w')
SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-prod')

if not JWT_TOKEN:
    logger.error("❌ ERROR: No se encontró VISION_SERVICE_JWT_TOKEN")
    logger.error("❌ Configura: $env:VISION_SERVICE_JWT_TOKEN='tu-token'")
    sys.exit(1)

# Decodificar token para obtener user_id y turno_id
try:
    payload = jwt.decode(JWT_TOKEN, SECRET_KEY, algorithms=['HS256'])
    USER_ID = payload.get('sub')
    TURNO_ID = payload.get('turno_id')  # El turno debe venir en el token
    
    if not USER_ID:
        logger.error("❌ Token no contiene user_id (sub)")
        sys.exit(1)
    
    if not TURNO_ID:
        logger.error("❌ Token no contiene turno_id")
        logger.error("⚠️  El token debe incluir el turno_id cuando se inicia sesión con un turno activo")
        sys.exit(1)
        
    logger.info(f"✅ Token válido - User ID: {USER_ID}, Turno ID: {TURNO_ID}")
    
except JWTError as e:
    logger.error(f"❌ Token inválido: {e}")
    sys.exit(1)

# Mapeo de clases YOLO para vehículos
VEHICLE_CLASSES = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}

# Expresión regular de placas colombianas (simplificada)
PLATE_REGEX = re.compile(r'^[A-Z]{3}\d{3}$')

# Historial temporal de detecciones
plate_history = defaultdict(list)
last_sent = {}
sent_plates = {}  # Guarda la última placa enviada por vehículo
last_detected = {}  # Última placa detectada para cada tipo
COOLDOWN = 60  # segundos
MIN_VOTES = 3
MIN_FRAMES = 5
MAX_HISTORY = 10  # Límite de frames en historial
RESET_THRESHOLD = 3  # Si detecta 3 frames de placa diferente, resetea

def normalize_plate(text: str) -> str:
    """
    Normaliza una placa colombiana (formato: AAA123)
    Solo corrige errores obvios de OCR en posiciones específicas.
    """
    if not text:
        return ""
    
    # Convertir a mayúsculas y eliminar espacios
    text = text.upper().replace(" ", "")
    
    # Eliminar caracteres especiales
    text = re.sub(r'[^A-Z0-9]', '', text)
    
    # Solo aplicar correcciones si el texto tiene longitud adecuada (5-6 caracteres)
    if len(text) >= 6:
        # Formato colombiano: 3 letras + 3 números (ABC123)
        # Corregir solo números en la parte de letras (primeros 3 chars)
        corrected = ""
        for i, char in enumerate(text[:6]):
            if i < 3:  # Parte de letras
                if char == '0':
                    corrected += 'O'
                elif char == '1':
                    corrected += 'I'
                elif char == '5':
                    corrected += 'S'
                else:
                    corrected += char
            else:  # Parte de números (últimos 3)
                if char == 'O':
                    corrected += '0'
                elif char == 'I' or char == 'L':
                    corrected += '1'
                elif char == 'S':
                    corrected += '5'
                elif char == 'B':
                    corrected += '8'
                else:
                    corrected += char
        
        # Mantener caracteres extras si los hay
        return corrected + text[6:]
    
    return text

def get_consensus(plates):
    """
    Obtiene la placa más confiable del historial.
    Usa votación y similitud de cadenas.
    """
    if not plates:
        return None
    
    normed = [normalize_plate(p) for p in plates if len(p) >= 5]
    if not normed:
        return None
    
    # Filtrar solo placas que parezcan tener el formato correcto (6 caracteres)
    valid_plates = [p for p in normed if len(p) == 6]
    
    if not valid_plates:
        valid_plates = normed  # Fallback si no hay placas de 6 chars
    
    cnt = Counter(valid_plates)
    best, count = cnt.most_common(1)[0]
    
    # Si hay suficientes votos y cumple el regex, aceptar
    if count >= MIN_VOTES and PLATE_REGEX.match(best):
        logger.info(f"🎯 Consenso por votación: {best} ({count} votos)")
        return best
    
    # Si no hay consenso claro, buscar por similitud
    for candidate, ccount in cnt.most_common(3):  # Revisar top 3
        if len(candidate) != 6:
            continue
            
        ratios = [SequenceMatcher(None, candidate, other).ratio() for other in valid_plates]
        avg_similarity = sum(ratios) / len(ratios)
        
        # Criterio más estricto: similitud alta Y que cumpla regex
        if avg_similarity > 0.8 and PLATE_REGEX.match(candidate):
            logger.info(f"🎯 Consenso por similitud: {candidate} (sim={avg_similarity:.2f})")
            return candidate
    
    logger.warning(f"⚠️ No hay consenso claro. Mejor candidato: {best} ({count} votos)")
    return None

def detect_vehicles_and_plates(frame):
    results = model(frame)
    current_time = time.time()
    
    for r in results[0].boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = r
        
        if int(class_id) in VEHICLE_CLASSES:
            vehicle_type = VEHICLE_CLASSES[int(class_id)]
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)
            
            roi = frame[int(y1):int(y2), int(x1):int(x2)]
            if roi.size == 0:
                continue

            ocr_result = ocr.readtext(roi)
            if not ocr_result:
                continue
            
            text = normalize_plate(ocr_result[0][1])
            conf = ocr_result[0][2] if len(ocr_result[0]) > 2 else 1.0

            if len(text) < 5 or conf < 0.5:
                continue
            
            # Verificar si estamos en cooldown y es la misma placa
            if (vehicle_type in sent_plates and 
                vehicle_type in last_sent and
                current_time - last_sent[vehicle_type] < COOLDOWN):
                # Si es la misma placa que ya enviamos, ignorar silenciosamente
                if normalize_plate(text) == sent_plates[vehicle_type]:
                    continue
            
            # Detectar cambio de vehículo: si la placa actual es muy diferente de las recientes
            if vehicle_type in last_detected and plate_history[vehicle_type]:
                recent_plates = plate_history[vehicle_type][-RESET_THRESHOLD:]
                normalized_recent = [normalize_plate(p) for p in recent_plates]
                normalized_current = normalize_plate(text)
                
                # Si ninguna de las últimas placas se parece a la actual, es otro vehículo
                similarities = [SequenceMatcher(None, normalized_current, p).ratio() for p in normalized_recent]
                if similarities and max(similarities) < 0.5:  # Muy diferente
                    logger.info(f"🔄 Nuevo vehículo detectado ({vehicle_type}). Reseteando historial.")
                    plate_history[vehicle_type].clear()
            
            plate_history[vehicle_type].append(text)
            last_detected[vehicle_type] = text
            
            # Limitar tamaño del historial para evitar acumulación infinita
            if len(plate_history[vehicle_type]) > MAX_HISTORY:
                plate_history[vehicle_type] = plate_history[vehicle_type][-MAX_HISTORY:]
            
            logger.info(f"📸 {vehicle_type}: posible placa '{text}' (conf={conf:.2f}) [{len(plate_history[vehicle_type])} frames]")

            # Evaluar si hay consenso
            if len(plate_history[vehicle_type]) >= MIN_FRAMES:
                consensus = get_consensus(plate_history[vehicle_type])
                if consensus:
                    # Verificar si no hemos enviado esta placa recientemente
                    if (vehicle_type not in last_sent or 
                        current_time - last_sent[vehicle_type] > COOLDOWN or
                        sent_plates.get(vehicle_type) != consensus):
                        
                        # Crear ticket de entrada
                        ticket_data = {
                            'placa': consensus,
                            'user_id': USER_ID,
                            'turno_id': TURNO_ID,
                            'vehicle_type': vehicle_type,
                            'confidence': float(score),
                            'timestamp': datetime.now().isoformat()
                        }
                        rabbitmq_producer.publish_ticket_entry(ticket_data)
                        logger.info(f"✅ Ticket de entrada creado para placa: {consensus}")
                        logger.info(f"⏱️ Cooldown activo por {COOLDOWN}s para {vehicle_type}")
                        
                        last_sent[vehicle_type] = current_time
                        sent_plates[vehicle_type] = consensus
                        plate_history[vehicle_type].clear()
                    else:
                        # Ya enviamos esta placa recientemente
                        remaining = COOLDOWN - (current_time - last_sent[vehicle_type])
                        if len(plate_history[vehicle_type]) == MIN_FRAMES:  # Solo log una vez
                            logger.info(f"⏸️ Placa {consensus} ya enviada. Cooldown: {remaining:.0f}s restantes")
                        plate_history[vehicle_type].clear()  # Limpiar para evitar spam
                else:
                    # No hay consenso claro después de suficientes frames
                    # Limpiar historial para empezar de nuevo con el siguiente vehículo
                    logger.warning(f"❌ No se pudo confirmar placa para {vehicle_type} después de {len(plate_history[vehicle_type])} frames. Reseteando.")
                    plate_history[vehicle_type].clear()

    return frame

try:
    cap = cv2.VideoCapture("http://localhost:8001/cameras/entrada/stream")
    logger.info("🎥 Iniciando captura de video...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = detect_vehicles_and_plates(frame)
        cv2.imshow("SmartPark AI - Detección de vehículos", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    logger.info("🛑 Interrumpido por usuario")
except Exception as e:
    logger.error(f"❌ Error: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
    rabbitmq_producer.close()
    logger.info("👋 Vision Service finalizado")
