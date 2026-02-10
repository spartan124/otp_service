from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # APP_ENV: str
    PROJECT_NAME: str = "OTP Service"
    API_V1_STR: str = "/api/v1"

    # Redis Config
    REDIS_HOST: str | None = None
    REDIS_PORT: int | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_URL: str | None = None 
    
    
    # RabbitMQ Config
    RABBITMQ_USER: str | None = None
    RABBITMQ_PASSWORD: str | None = None
    RABBITMQ_HOST: str | None = None
    RABBITMQ_PORT: int | None = None      
    RABBITMQ_URL: str | None = None
    
    # SMTP / Email Settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str 
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
