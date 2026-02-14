from app.core.config import settings
from app.services.email_base import EmailProvider
from app.services.email_providers import ResendProvider, SMTPProvider, ConsoleProvider

class EmailService:
    def __init__(self):
        self.provider: EmailProvider = self._get_provider()
        
    def _get_provider(self) -> EmailProvider:
        provider_type = settings.EMAIL_PROVIDER.lower()
        if provider_type == "resend":
            return ResendProvider()
        elif provider_type == "smtp":
            return SMTPProvider()
        elif provider_type == "console":
            return ConsoleProvider()
        else:
            raise ValueError(f"Unknown EMAIL_PROVIDER: {provider_type}")
        
    async def send_otp(self, email: str, otp: str):
        html = f"""
                <html>
                    <body style="font-family: sans-serif;>
                        <h2>Verify Your LOgin</h2>
                        <p>Your verification code is:</p>
                        <h1 style="color: #333; letter-spacing: 5px;">{otp}</h1>
                        <p>This code expires in 5 minutes.</p>   
                </html>
                """
        subject = "Your OTP Code"
        return await self.provider.send_email(email, subject, html)

# Singleton Instance
email_service = EmailService()