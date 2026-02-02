import os
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import otp

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(otp.router, prefix=settings.API_V1_STR, tags=["OTP"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}