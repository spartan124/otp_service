import redis
from app.core.config import settings

def get_redis():
    """
    Dependency that provides a Redis connection instance.
    """
    client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )
    try:
        yield client
    finally:
        client.close()
        client.connection_pool.disconnect()