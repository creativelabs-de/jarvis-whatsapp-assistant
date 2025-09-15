from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # WhatsApp API
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = ""
    
    # OpenAI API
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/jarvis_db"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # E-Commerce APIs
    SHOPIFY_API_KEY: Optional[str] = None
    SHOPIFY_API_SECRET: Optional[str] = None
    SHOPIFY_SHOP_NAME: Optional[str] = None
    
    # Development
    DEBUG: bool = True
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()

# Validate required settings
def validate_settings():
    """Validate that required settings are present"""
    required_settings = [
        "WHATSAPP_ACCESS_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID", 
        "WHATSAPP_WEBHOOK_VERIFY_TOKEN",
        "OPENAI_API_KEY"
    ]
    
    missing_settings = []
    for setting in required_settings:
        if not getattr(settings, setting):
            missing_settings.append(setting)
    
    if missing_settings:
        print(f"Warning: Missing required environment variables: {', '.join(missing_settings)}")
        print("Please check your .env file or environment variables.")
    
    return len(missing_settings) == 0

# Validate on import
validate_settings()
