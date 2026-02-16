from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi import FastAPI
# from fastapi_limiter import FastAPILimiter
from app.core.config import settings
from app.api.v1.endpoints import otp
from app.core.middleware import TimingMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME
)

app.add_middleware(TimingMiddleware)

app.include_router(otp.router, prefix=settings.API_V1_STR, tags=["OTP"])

@app.get("/health")
@app.head("/health")
async def health_check():
    return {"status": "ok"}