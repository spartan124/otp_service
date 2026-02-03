import pika
import json
from app.core.config import settings
from app.schemas.otp import OTPMessage

class RabbitMQService:
    def __init__(self):
        self.credentials = pika.PlainCredentials(
            settings.RABBITMQ_USER, 
            settings.RABBITMQ_PASSWORD,
        )
        self.parameters = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=self.credentials
        )
        self.queue_name = "otp_notifications"
        
    def publish_otp(self, message: OTPMessage):
        """
        Connects to RabbitMQ and pushes a message to the queue.
        Uses a context manager to ensure the connection always closes.
        """
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        
        #Idempotency: Declare the queue ensures it exists before we publish to it.
        channel.queue_declare(queue=self.queue_name, durable=True)
        
        channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(message.model_dump()),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent (so it survives broker restarts
            )
        )
        
        connection.close()
        