from functools import lru_cache

from fastapi import Request
from app.services.rabbitmq import RabbitMQService

@lru_cache()
def get_rabbitmq_service_instance() -> RabbitMQService:
    """
    Provides a singleton instance of RabbitMQService.
    """
    return RabbitMQService()

async def get_rabbitmq_service() -> RabbitMQService:
    """
    Dependency that provides a RabbitMQService instance.
    """
    service = get_rabbitmq_service_instance()
    if not service.connection or service.connection.is_closed:
        await service.connect()
        
    return service

async def limit_by_email(request: Request):
    try:
        body = await request.json()
        email = body.get("email")
        if email:
            return f"email:{email.lower().strip()}"
    except Exception:
        pass
    return f"ip:{request.client.host}"