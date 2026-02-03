import json
import time
import sys
import os
import pika
from app.core.config import settings

def send_email_simulation(email: str, code: str):
    """Simulate sending an email via SMTP
    """
    print(f"[x] Connecting to SMTP server for {email}...")
    time.sleep(1)  # Simulate network delay
    print(f"[x] Sent: OTP {code} delivered to {email}")
    return True

def callback(ch, method, properties, body):
    """This function is triggered every time a message is received.
    """
    try:
        data = json.loads(body)
        email = data.get("email")
        otp_code = data.get("otp_code")
        
        print(f" [>] Received task for: {email}")
        
        send_email_simulation(email, otp_code)
        
        #Manual Acknowledgment
        #Tell RabbitMQ that the message has been processed
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    except Exception as e:
        print(f"[!] Error processing message: {e}")
        
def main():
    """Main function to set up RabbitMQ connection and start consuming messages.
    """
    print(" [*] Starting worker Service...")
    
    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USER,
        settings.RABBITMQ_PASSWORD
    )
    
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        credentials=credentials
    )
    
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Idempotency: Ensure queue exists (just in case Worker starts before API)
    channel.queue_declare(queue='otp_notifications', durable=True)
    
    # Fair Dispatch: Don't give me more than 1 message at a time
    channel.basic_qos(prefetch_count=1)
    
    # Start consuming messages
    channel.basic_consume(queue='otp_notifications', on_message_callback=callback)
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(" [*] Exiting...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)