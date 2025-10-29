from ultralytics import YOLO
import cv2
import easyocr
from rabbitmq_producer import RabbitMQProducer
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar modelo YOLO
model = YOLO("yolov8n.pt")

# Inicializar OCR
ocr = easyocr.Reader(['en'])

# Inicializar RabbitMQ Producer
rabbitmq_producer = RabbitMQProducer()
rabbitmq_producer.connect()

# Mapeo de clases YOLO para vehículos
VEHICLE_CLASSES = {
    2: 'car',
    3: 'motorcycle',
    5: 'bus',
    7: 'truck'
}

def detect_vehicles_and_plates(frame):
    results = model(frame)
    
    for r in results[0].boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = r
        
        # Verificar si es un vehículo
        if int(class_id) in VEHICLE_CLASSES.keys():
            # Dibuja el cuadro verde
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

            # Extrae la región (ROI) para el OCR
            roi = frame[int(y1):int(y2), int(x1):int(x2)]

            # Aplica OCR
            plate_number = None
            text = ocr.readtext(roi)
            if text:
                plate_number = text[0][1]
                # Muestra la placa detectada en consola
                logger.info(f"📸 Placa detectada: {plate_number}")
            
            # Preparar datos del evento
            vehicle_event = {
                'vehicle_type': VEHICLE_CLASSES[int(class_id)],
                'confidence': float(score),
                'timestamp': datetime.now().isoformat(),
                'coordinates': {
                    'x1': int(x1),
                    'y1': int(y1),
                    'x2': int(x2),
                    'y2': int(y2)
                },
                'plate_number': plate_number
            }
            
            # Publicar evento en RabbitMQ
            try:
                rabbitmq_producer.publish_vehicle_event(vehicle_event)
            except Exception as e:
                logger.error(f"❌ Error publicando evento: {e}")
            
    return frame

try:
    cap = cv2.VideoCapture(0)
    logger.info("🎥 Iniciando captura de video...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = detect_vehicles_and_plates(frame)
        cv2.imshow("SmartPark AI - Detección de vehículos y placas", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
except KeyboardInterrupt:
    logger.info("⚠️ Interrupción del usuario")
except Exception as e:
    logger.error(f"❌ Error en la captura: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
    rabbitmq_producer.close()
    logger.info("👋 Vision Service finalizado")