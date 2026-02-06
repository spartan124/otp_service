import pika
import json
from app.core.config import settings
from app.schemas.otp import OTPMessage

class RabbitMQService:
    def __init__(self):
        self.queue_name = "otp_notifications"

        # --- CONFIGURATION LOGIC ---
        if settings.RABBITMQ_URL:
            # Production Mode (CloudAMQP)
            print(f" [i] Using CloudAMQP Connection URL")
            self.parameters = pika.URLParameters(settings.RABBITMQ_URL)
        else:
            # Local Development Mode (Docker)
            print(f" [i] Using Local RabbitMQ Credentials")
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER, 
                settings.RABBITMQ_PASSWORD,
            )
            self.parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=2
            )
    
    def connect(self):
        """Helper method to establish connection using stored parameters."""
        return pika.BlockingConnection(self.parameters)
    
    def publish_otp(self, message: OTPMessage):
        """
        Connects to RabbitMQ and pushes a message to the queue.
        """
        # FIX: Use the helper method instead of manual connection!
        connection = self.connect() 
        
        try:
            channel = connection.channel()
            
            # Idempotency: Declare the queue ensures it exists
            channel.queue_declare(queue=self.queue_name, durable=True)
            
            channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(message.model_dump()),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
        finally:
            # Ensuring connection closes even if an error occurs above
            connection.close()