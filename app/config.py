# app/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Indian Finance Dashboard"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/finance_dashboard"
    )
    
    # File storage settings
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # local, s3, etc.
    LOCAL_STORAGE_PATH: str = os.getenv("LOCAL_STORAGE_PATH", "./uploads")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "")
    S3_REGION: str = os.getenv("S3_REGION", "ap-south-1")
    
    # AI service settings
    AI_SERVICE_URL: str = os.getenv("AI_SERVICE_URL", "")
    AI_SERVICE_API_KEY: str = os.getenv("AI_SERVICE_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()


