import json
import time
import sys
import os
import socket # <--- Make sure this is imported
import pika
import asyncio
import logging
from app.core.config import settings
from app.services.email_service import email_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ... (send_email_simulation and callback functions remain exactly the same) ...
# def send_email_simulation(email: str, code: str):
#     """Simulate sending an email via SMTP"""
#     print(f"[x] Connecting to SMTP server for {email}...")
#     time.sleep(1)  # Simulate network delay
#     print(f"[x] Sent: OTP {code} delivered to {email}")
#     return True

async def process_message(email: str, otp_code: str):
    """
    Actual async logic to send the email.
    """
    try:
        if not email or not otp_code:
            logger.warning("Invalid message format")
            return

        logger.info(f"📨 Sending OTP to {email}...")
        
        # Await the real service
        await email_service.send_otp(email, otp_code)
        
        logger.info(f"✅ Email sent successfully to {email}")

    except Exception as e:
        logger.error(f"❌ Error sending email: {str(e)}")
           
def callback(ch, method, properties, body):
    """This function is triggered every time a message is received."""
    try:
        data = json.loads(body)
        email = data.get("email")
        otp_code = data.get("otp_code")
        
        logger.info(f" [>] Received task for: {email}")
        
        # --- THE FIX IS HERE ---
        # We must create a new event loop to run the async function
        # because 'callback' is synchronous.
        asyncio.run(process_message(email, otp_code))
        
        # Manual Acknowledgment
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    except Exception as e:
        logger.error(f"[!] Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    print(" [*] Starting worker Service...")
    
    retries = 0
    max_retries = 20 # Increased retries just in case
    retry_delay = 5

    while retries < max_retries:
        try:
            
            # --- NEW CONNECTION LOGIC ---
            if settings.RABBITMQ_URL:
                print(f" [i] Using CloudAMQP Connection URL")
                # Production Mode (CloudAMQP)
                # URLParameters handles User, Pass, Host, Port, AND Virtual Host automatically
                parameters = pika.URLParameters(settings.RABBITMQ_URL)
            else:
                print(f" [?] Attempting to connect to Host: '{settings.RABBITMQ_HOST}' Port: {settings.RABBITMQ_PORT}")

                credentials = pika.PlainCredentials(
                    settings.RABBITMQ_USER,
                    settings.RABBITMQ_PASSWORD
                )
                
                parameters = pika.ConnectionParameters(
                    host=settings.RABBITMQ_HOST,
                    port=settings.RABBITMQ_PORT,
                    credentials=credentials,
                    connection_attempts=3,
                    retry_delay=2
                )
                
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            print(" [V] Connected to RabbitMQ!")
            
            channel.queue_declare(queue='otp_notifications', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='otp_notifications', on_message_callback=callback)

            print(" [*] Waiting for messages. To exit press CTRL+C")
            channel.start_consuming()
            break

        # FIX: Catch BOTH Pika errors AND Socket (DNS) errors
        except (pika.exceptions.AMQPConnectionError, socket.gaierror) as e:
            print(f" [!] Connection failed: {e}")
            print(f" [!] Retrying in {retry_delay} seconds... ({retries + 1}/{max_retries})")
            time.sleep(retry_delay)
            retries += 1
        except Exception as e:
            # Catch-all for anything else unexpected
            print(f" [!] Unexpected error: {e}")
            time.sleep(retry_delay)
            retries += 1
            
    if retries >= max_retries:
        print(" [X] Could not connect to RabbitMQ after multiple attempts. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)