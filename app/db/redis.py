from redis.asyncio import ConnectionPool, Redis
from functools import lru_cache
from app.core.config import settings

if  settings.REDIS_URL:
    pool = ConnectionPool.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        max_connections=10
    )
 
else:
    pool = ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
        max_connections=10
    )
    
async def get_redis():
    """
    Dependency that provides a Redis connection instance.
    """
    return Redis(connection_pool=pool)