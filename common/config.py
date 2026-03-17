from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "banking"
    LOG_LEVEL: str = "info"
    POSTGRES_DSN: str = Field(..., alias="POSTGRES_DSN")
    REDIS_DSN: str = Field(..., alias="REDIS_DSN")
    RABBIT_DSN: str = Field(..., alias="RABBIT_DSN")
    JWT_SECRET_KEY: str = Field(..., alias="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "populate_by_name": True,
    }

settings = Settings()
