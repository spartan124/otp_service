from functools import lru_cache
from app.services.rabbitmq import RabbitMQService

@lru_cache()
def get_rabbitmq_service() -> RabbitMQService:
    return RabbitMQService()

