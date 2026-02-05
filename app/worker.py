import json
import time
import sys
import os
import socket # <--- Make sure this is imported
import pika
from app.core.config import settings

# ... (send_email_simulation and callback functions remain exactly the same) ...
def send_email_simulation(email: str, code: str):
    """Simulate sending an email via SMTP"""
    print(f"[x] Connecting to SMTP server for {email}...")
    time.sleep(1)  # Simulate network delay
    print(f"[x] Sent: OTP {code} delivered to {email}")
    return True

def callback(ch, method, properties, body):
    """This function is triggered every time a message is received."""
    try:
        data = json.loads(body)
        email = data.get("email")
        otp_code = data.get("otp_code")
        
        print(f" [>] Received task for: {email}")
        
        send_email_simulation(email, otp_code)
        
        # Manual Acknowledgment
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    except Exception as e:
        print(f"[!] Error processing message: {e}")

def main():
    print(" [*] Starting worker Service...")
    
    retries = 0
    max_retries = 20 # Increased retries just in case
    retry_delay = 5

    while retries < max_retries:
        try:
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