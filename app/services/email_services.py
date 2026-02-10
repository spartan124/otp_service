from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings
from pathlib import Path

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)

async def send_otp_email(email_to: str, otp_code: str):
    """
    Sends an OTP email using FastMail.
    """
    html = f"""
    <html>
        <body style="font-family: sans-serif;>
            <h2>Verify Your LOgin</h2>
            <p>Your verification code is:</p>
            <h1 style="color: #333; letter-spacing: 5px;">{otp_code}</h1>
            <p>This code expires in 5 minutes.</p>   
    </html>
    """
    
    message = MessageSchema(
        subject="Your OTP Code",
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
    
