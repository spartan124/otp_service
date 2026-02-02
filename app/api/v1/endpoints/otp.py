from fastapi import APIRouter, HTTPException, Depends
from redis import Redis
from app.schemas.otp import OTPRequest, OTPVerify
from app.utils import generate_otp, hash_otp
from app.db.redis import get_redis

router = APIRouter()

@router.post("/generate-otp", status_code=201)
async def generate_otp_endpoint(payload: OTPRequest, r: Redis= Depends(get_redis)):
    identifier = payload.email
    otp_code = generate_otp()
    hashed_otp = hash_otp(otp_code)
    redis_key = f"otp:{identifier}"
    try:
        r.setex(redis_key, 300, hashed_otp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")
    return {
        "message": "OTP generated successfully",
        "dev_only_code": otp_code,
        "ttl": 300
    }
