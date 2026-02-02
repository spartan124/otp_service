import secrets
import hashlib

def generate_otp(length: int = 6) -> str:
    """
    Generates a cryptographically secure numeric OTP.
    """
    return ''.join(secrets.choice('0123456789') for _ in range(length))

def hash_otp(otp: str) -> str:
    """
    Hashes the OTP using SHA-256 for secure storage.
    """
    return hashlib.sha256(otp.encode()).hexdigest()