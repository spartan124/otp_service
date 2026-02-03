from pydantic import BaseModel, EmailStr

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

class OTPMessage(BaseModel):
    """
    The shape of the payload we send to RabbitMQ.
    """
    email: EmailStr
    otp_code: str  # The plain text code (so the worker can email it)
    ttl: int