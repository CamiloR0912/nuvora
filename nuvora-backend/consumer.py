from config.rabbitmq import RabbitMQConsumer
from config.db import get_db
from model.tickets import Ticket
from model.vehiculos import Vehiculo
from model.turnos import Turno
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VehicleEventConsumer:
    def __init__(self):
        self.consumer = RabbitMQConsumer(queue_name='ticket_entries')
    
    def process_vehicle_event(self, message: dict):
        """
        Procesa tickets de entrada desde vision_service
        
        Formato esperado:
        {
            'placa': 'ABC123',
            'user_id': 1,
            'turno_id': 5,
            'vehicle_type': 'car',
            'confidence': 0.95,
            'timestamp': '2024-01-01T12:00:00'
        }
        """
        # Crear una nueva sesión para cada mensaje
        db = next(get_db())
        
        try:
            placa = message.get('placa')
            turno_id = message.get('turno_id')
            user_id = message.get('user_id')
            
            if not all([placa, turno_id, user_id]):
                logger.error(f"❌ Mensaje incompleto: {message}")
                return
            
            # Buscar o crear vehículo
            vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == placa).first()
            if not vehiculo:
                vehiculo = Vehiculo(placa=placa)
                db.add(vehiculo)
                db.commit()
                db.refresh(vehiculo)
                logger.info(f"🚗 Nuevo vehículo: {placa}")
            
            # Verificar si ya existe ticket abierto (solo ABIERTO, no cerrado)
            ticket_existente = db.query(Ticket).filter(
                Ticket.vehiculo_id == vehiculo.id,
                Ticket.turno_id == turno_id,
                Ticket.estado == 'abierto'
            ).first()
            
            if ticket_existente:
                logger.info(f"ℹ️ Vehículo {placa} ya tiene un ticket abierto (ID: {ticket_existente.id}) en turno {turno_id}. No se crea duplicado.")
                return
            
            # Crear ticket
            nuevo_ticket = Ticket(
                vehiculo_id=vehiculo.id,
                turno_id=turno_id,
                hora_entrada=datetime.fromisoformat(message.get('timestamp', datetime.now().isoformat())),
                estado='abierto'
            )
            
            db.add(nuevo_ticket)
            db.commit()
            db.refresh(nuevo_ticket)
            
            logger.info(f"✅ Ticket creado: ID {nuevo_ticket.id}, Placa: {placa}, Turno: {turno_id}")
            
            # Notificar a los clientes SSE
            try:
                from router.events_router import update_last_detection
                update_last_detection(
                    placa=placa,
                    timestamp=nuevo_ticket.hora_entrada.isoformat(),
                    vehicle_type=message.get('vehicle_type', 'car')
                )
            except Exception as e:
                logger.error(f"⚠️ Error notificando SSE: {e}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error procesando ticket: {e}", exc_info=True)
        finally:
            db.close()
    
    def start(self):
        self.consumer.connect()
        self.consumer.consume(self.process_vehicle_event)

if __name__ == "__main__":
    consumer = VehicleEventConsumer()
    consumer.start()