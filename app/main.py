from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi import FastAPI
# from fastapi_limiter import FastAPILimiter
from app.core.config import settings
from app.api.v1.endpoints import otp


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     redis_connection = redis.from_url(
#         settings.REDIS_URL, encoding="utf-8", decode_responses=True
#     )
#     await FastAPILimiter.init(redis_connection)
#     yield
    
#     await redis_connection.close()


app = FastAPI(
    title=settings.PROJECT_NAME
)

app.include_router(otp.router, prefix=settings.API_V1_STR, tags=["OTP"])

@app.get("/health")
@app.head("/health")
async def health_check():
    return {"status": "ok"}