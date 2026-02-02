from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # APP_ENV: str
    PROJECT_NAME: str = "OTP Service"
    API_V1_STR: str = "/api/v1"

    # Redis Config
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    
    
    # RabbitMQ Config
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
