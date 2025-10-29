import pika
import os
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RabbitMQProducer:
    def __init__(self):
        self.host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.user = os.getenv('RABBITMQ_USER', 'admin')
        self.password = os.getenv('RABBITMQ_PASS', 'admin')
        self.queue_name = 'vehicle_events'
        self.connection = None
        self.channel = None
        
    def connect(self):
        try:
            credentials = pika.PlainCredentials(self.user, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            logger.info("✅ Connected to RabbitMQ successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            raise
    
    def publish_vehicle_event(self, vehicle_data: dict):
        try:
            message = json.dumps(vehicle_data, ensure_ascii=False)
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
            logger.info(f"📤 Published vehicle event: {vehicle_data.get('plate_number', 'N/A')}")
        except Exception as e:
            logger.error(f"❌ Failed to publish message: {e}")
            raise
    
    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("🔌 RabbitMQ connection closed")