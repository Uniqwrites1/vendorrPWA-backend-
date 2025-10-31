from typing import Optional
import os

class Settings:
    """Simple settings class without Pydantic"""
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./vendorr.db")

    # Fix for Railway/Render PostgreSQL URL (they use postgres:// but SQLAlchemy needs postgresql://)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS - Allow frontend origins
    allowed_origins: list = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")]

    # Redis
    redis_url: str = "redis://localhost:6379"

    # File uploads
    max_file_size: int = 5242880  # 5MB
    upload_folder: str = "uploads"

    # Restaurant info
    restaurant_name: str = "Vendorr"
    restaurant_phone: str = "+1234567890"
    restaurant_email: str = "info@vendorr.com"
    restaurant_address: str = "123 Main St, City, State 12345"

    # Bank details for transfers
    bank_name: str = "Kuda MFB"
    bank_account_number: str = "3002871052"
    bank_routing_number: str = ""
    bank_account_name: str = "Uniqwrtes Edtech Services-vendorr"

    # Environment
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    port: int = int(os.getenv("PORT", "8000"))

settings = Settings()
