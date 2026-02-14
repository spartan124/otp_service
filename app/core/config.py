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
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: str | None = None
    MAIL_PORT: int | None = None
    MAIL_SERVER: str | None = None
    MAIL_STARTTLS: bool | None = None
    MAIL_SSL_TLS: bool | None = None
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    
    #RESEND / Email Provider Settings
    RESEND_API_KEY: str | None = None
    RESEND_API_URL: str | None = None
    RESEND_MAIL_FROM: str | None = None
    EMAIL_PROVIDER: str = "resend"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
