from functools import lru_cache

from fastapi import Request
from app.services.rabbitmq import RabbitMQService

@lru_cache()
def get_rabbitmq_service() -> RabbitMQService:
    return RabbitMQService()


async def limit_by_email(request: Request):
    try:
        body = await request.json()
        email = body.get("email")
        if email:
            return f"email:{email.lower().strip()}"
    except Exception:
        pass
    return f"ip:{request.client.host}"