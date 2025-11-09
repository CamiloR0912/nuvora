import pika
import os
import json
from typing import Callable
import logging
import time

logger = logging.getLogger(__name__)

class RabbitMQConfig:
    def __init__(self, queue_name='vehicle_events'):
        self.host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.user = os.getenv('RABBITMQ_USER', 'admin')
        self.password = os.getenv('RABBITMQ_PASS', 'admin')
        self.queue_name = queue_name
        
    def get_connection(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        return pika.BlockingConnection(parameters)
    
    def create_channel(self, connection):
        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name, durable=True)
        return channel

class RabbitMQConsumer:
    def __init__(self, queue_name='vehicle_events'):
        self.config = RabbitMQConfig(queue_name=queue_name)
        self.connection = None
        self.channel = None
        
    def connect(self, max_retries=10, retry_delay=5):
        """Connect to RabbitMQ with retry logic"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to connect to RabbitMQ (attempt {attempt + 1}/{max_retries})...")
                self.connection = self.config.get_connection()
                self.channel = self.config.create_channel(self.connection)
                logger.info("✅ Connected to RabbitMQ successfully")
                return
            except Exception as e:
                logger.warning(f"⚠️ Failed to connect to RabbitMQ (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"❌ Failed to connect to RabbitMQ after {max_retries} attempts")
                    raise
    
    def consume(self, callback: Callable):
        def on_message(ch, method, properties, body):
            try:
                message = json.loads(body)
                callback(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.config.queue_name,
            on_message_callback=on_message
        )
        
        logger.info("Waiting for vehicle events...")
        self.channel.start_consuming()
    
    def close(self):
        if self.connection:
            self.connection.close()
            logger.info("RabbitMQ connection closed")