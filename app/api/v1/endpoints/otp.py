from fastapi import APIRouter, HTTPException, Depends, status
from redis.asyncio import Redis
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Rate, Limiter
from app.api.deps import get_rabbitmq_service, limit_by_email
from app.schemas.otp import OTPMessage, OTPRequest, OTPVerify
from app.utils import generate_otp, hash_otp
from app.db.redis import get_redis
from app.services.rabbitmq import RabbitMQService
from app.core.limiter import otp_limiter

router = APIRouter()

@router.post(
    "/generate-otp",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(RateLimiter(limiter=otp_limiter)),
        Depends(RateLimiter(limiter=otp_limiter, identifier=limit_by_email)),
    ],
)
async def generate_otp_endpoint(payload: OTPRequest, r: Redis= Depends(get_redis), mq_service: RabbitMQService = Depends(get_rabbitmq_service)):
    identifier = payload.email
    otp_code = generate_otp()
    hashed_otp = hash_otp(otp_code)
    redis_key = f"otp:{identifier}"
    try:
        await r.setex(redis_key, 300, hashed_otp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")
    
    # Publish OTP to RabbitMQ for asynchronous processing (e.g., sending email)
    # In a massive scale app, we might inject this service too, 
    # but instantiating it here is fine for now.
    
    message = OTPMessage(
        email=identifier,
        otp_code=otp_code,
        ttl=300
    )
    try:
        mq_service.publish_otp(message)
    except Exception as e:
        await r.delete(f'otp:{identifier}')  # Rollback OTP storage on failure
        raise HTTPException(status_code=500, detail=f"Messaging error: {str(e)}")
    return {
        "message": "OTP generated successfully",
        "status": "queued"
    }

@router.post(
    "/verify-otp",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(RateLimiter(limiter=Limiter(Rate(5, Duration.MINUTE)))),
        Depends(RateLimiter(limiter=Limiter(Rate(3, Duration.MINUTE)), identifier=limit_by_email)),
    ],
)
async def verify_otp(data: OTPVerify, r: Redis = Depends(get_redis)):
    redis_key = f"otp:{data.email}"
    
    stored_hashed_otp = await r.get(redis_key)
    
    if not stored_hashed_otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP Expired or Not Found")
    
    input_hash = hash_otp(data.otp_code)
    if input_hash != stored_hashed_otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
    
    await r.delete(redis_key)
    return {
        "status": "success",
        "message": "OTP verified successfully"
    }