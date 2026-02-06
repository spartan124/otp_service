from fastapi import APIRouter, HTTPException, Depends, status
from redis import Redis
from app.api.deps import get_rabbitmq_service
from app.schemas.otp import OTPMessage, OTPRequest, OTPVerify
from app.utils import generate_otp, hash_otp
from app.db.redis import get_redis
from app.services.rabbitmq import RabbitMQService


router = APIRouter()

@router.post("/generate-otp", status_code=status.HTTP_202_ACCEPTED)
async def generate_otp_endpoint(payload: OTPRequest, r: Redis= Depends(get_redis), mq_service: RabbitMQService = Depends(get_rabbitmq_service)):
    identifier = payload.email
    otp_code = generate_otp()
    hashed_otp = hash_otp(otp_code)
    redis_key = f"otp:{identifier}"
    try:
        r.setex(redis_key, 300, hashed_otp)
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
        r.delete(f'otp:{identifier}')  # Rollback OTP storage on failure
        raise HTTPException(status_code=500, detail=f"Messaging error: {str(e)}")
    return {
        "message": "OTP generated successfully",
        "status": "queued"
    }
