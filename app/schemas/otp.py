from pydantic import BaseModel, EmailStr, Field

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d+$")

class OTPMessage(BaseModel):
    """
    The shape of the payload we send to RabbitMQ.
    """
    email: EmailStr
    otp_code: str   # The plain text code (so the worker can email it)
    ttl: int