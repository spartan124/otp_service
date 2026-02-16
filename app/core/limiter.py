from pyrate_limiter.clocks import MonotonicClock
from redis import Redis
from pyrate_limiter import AbstractBucket, BucketFactory, Limiter, Rate, Duration, RedisBucket, RateItem
from app.core.config import settings

class RedisBucketFactory(BucketFactory):
    """
    Creates a unique RedisBucket for each user/IP.
    This ensures each user/IP has their own rate limit.
    """
    def __init__(self, redis_connection, rates):
        self.redis = redis_connection
        self.rates = rates
        self.clock = MonotonicClock()
        
    def wrap_item(self, name: str, weight: int = 1):
        """Standard wrapper required by pyrate-limiter v4"""
        now = self.clock.now()
        return RateItem(name, now, weight=weight)
    
    def get(self, item) -> AbstractBucket:
        """
        The Magic: Returns a specific bucket for the incoming  'item' (user/IP).
        """
        bucket_key = f"rate-limit:{item.name}"
        
        return RedisBucket.init(
            self.rates,
            self.redis,
            bucket_key
        )
    
    def schedule_leak(self, *args):
        pass
        

def create_redis_limiter(rate_limit: int, duration: int = 60):
    """
    Creates a distributed rate limiter using Upstash Redis.
    Matches PyrateLimiter v4.0.2+ API.
    """
    redis_connection = Redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2
    )
    
    rates = [Rate(rate_limit, duration)]
    
    factory = RedisBucketFactory(redis_connection, rates)
    
    return Limiter(factory)
    
otp_limiter = create_redis_limiter(rate_limit=3, duration=Duration.MINUTE)