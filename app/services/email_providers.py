import httpx
import logging
from app.core.config import settings
from app.services.email_base import EmailProvider

logger = logging.getLogger(__name__)

# --- 1. Resend Provider ---
class ResendProvider(EmailProvider):
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.api_url = settings.RESEND_API_URL
        
    async def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        headers ={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": settings.RESEND_MAIL_FROM,
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(self.api_url, json=payload, headers=headers, timeout=10.0)
                if resp.status_code == 200:
                    logger.info(f"✅ [Resend] Email sent to {to_email}")
                    return True
                else:
                    logger.error(f"❌ [Resend] Error {resp.status_code}: {resp.text}")
                    return False
            except httpx.RequestError as e:
                logger.error(f"❌ [Resend] Connection Error: {e}")
                return False
            
# --- 2. SMTP Provider (Legacy Backup) ---
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

class SMTPProvider(EmailProvider):
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS
            # USE_CREDENTIALS=settings.USE_CREDENTIALS,
            # VALIDATE_CERTS=settings.VALIDATE_CERTS
        )
        
    async def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        message = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=html_content,
            subtype="html"
        )
        fm = FastMail(self.conf)
        try:
            await fm.send_message(message)
            logger.info(f"✅ [SMTP] Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"❌ [SMTP] Failed: {e}")
            return False
        
# --- 3. Console Provider (local Dev) ---
class ConsoleProvider(EmailProvider):
    async def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        print("\n" + "="*30)
        print(f"📧 [MOCK EMAIL] To: {to_email}")
        print(f"Subject: {subject}")
        print("-" * 10)
        print(html_content)
        print("="*30 + "\n")
        return True