from config.rabbitmq import RabbitMQConsumer
from config.db import get_db
from model.vehicles import Vehicle
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VehicleEventConsumer:
    def __init__(self):
        self.consumer = RabbitMQConsumer()
        self.db = next(get_db())
    
    def process_vehicle_event(self, message: dict):
        try:
            vehicle = Vehicle(
                vehicle_type=message.get('vehicle_type'),
                confidence=message.get('confidence'),
                timestamp=datetime.fromisoformat(message.get('timestamp')),
                location=message.get('coordinates'),  # cambio: coordinates en lugar de location
                plate_number=message.get('plate_number')
            )
            self.db.add(vehicle)
            self.db.commit()
            logger.info(f"✅ Vehicle event saved to database: {message.get('plate_number', 'N/A')}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error saving vehicle event: {e}")
    
    def start(self):
        self.consumer.connect()
        self.consumer.consume(self.process_vehicle_event)

if __name__ == "__main__":
    consumer = VehicleEventConsumer()
    consumer.start()