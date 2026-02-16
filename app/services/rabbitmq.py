import aio_pika
import json
import logging
from app.core.config import settings
from app.schemas.otp import OTPMessage

logger = logging.getLogger(__name__)

class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "otp_notifications"
        # Determine the URL immediately upon instantiation
        self.url = self._build_connection_url()

    def _build_connection_url(self) -> str:
        """
        Builds the connection URL. 
        Prioritizes CloudAMQP (Prod), falls back to Local Config (Dev).
        """
        if settings.RABBITMQ_URL:
            logger.info(" [i] Using CloudAMQP Connection URL")
            return settings.RABBITMQ_URL
        
        logger.info(" [i] Using Local RabbitMQ Credentials")
        # Construct the AMQP URL manually for local dev
        # Format: amqp://user:password@host:port/
        return (
            f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}"
            f"@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
        )

    async def connect(self):
        """Idempotent connection logic."""
        # If we are already connected, do nothing.
        if self.connection and not self.connection.is_closed:
            return

        try:
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()
            
            # Idempotent queue declaration
            await self.channel.declare_queue(self.queue_name, durable=True)
            logger.info("✅ RabbitMQ Connected")
        except Exception as e:
            logger.error(f"❌ RabbitMQ Connection Failed: {e}")
            raise e

    async def publish_otp(self, message: OTPMessage):
        """Publishes without closing the connection."""
        if not self.channel or self.channel.is_closed:
            await self.connect()

        body = json.dumps(message.model_dump()).encode()
        
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=self.queue_name
        )