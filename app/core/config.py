from typing import Optional

class Settings:
    """Simple settings class without Pydantic"""
    # Database
    database_url: str = "sqlite:///./vendorr.db"

    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

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
    bank_name: str = "Example Bank"
    bank_account_number: str = "1234567890"
    bank_routing_number: str = "123456789"
    bank_account_name: str = "Vendorr Restaurant LLC"

    # Environment
    debug: bool = True
    environment: str = "development"

settings = Settings()
