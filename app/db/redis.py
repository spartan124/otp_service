import redis
from app.core.config import settings

def get_redis():
    """
    Dependency that provides a Redis connection instance.
    """
    if settings.REDIS_URL:
        #Production(upstash)
        print("[*] connecting to Upstash Redis...")
        client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
    else:
        #Development    
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