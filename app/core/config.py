import os
from typing import List

# Try to import from pydantic_settings (newer versions)
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fall back to pydantic (older versions)
    from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Logic Service"
    API_V1_STR: str = "/api/v1"
    
    # Database - SQLite by default for local development
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./instagram.db")
    
    # Redis for caching
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Mock scraper setting
    USE_MOCK_SCRAPER: bool = os.getenv("USE_MOCK_SCRAPER", "false").lower() in ("true", "1", "t")
    
    # CORS - defined here rather than in .env to avoid parsing issues
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend development server
        "http://localhost:8000",  # Same origin
        "http://localhost:8001",  # Mock scraper service
        "https://yourdomain.com",  # Production frontend
        "https://frontend-service-0gsj.onrender.com",  # Render frontend
    ]
    
    # Use environment variable for CORS if provided, otherwise use the list above
    # This allows setting CORS_ORIGINS=* in production without code changes
    CORS_ORIGINS_STR: str = os.getenv("CORS_ORIGINS", "")
    if CORS_ORIGINS_STR:
        # Split by comma and strip whitespace
        CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_STR.split(",")]
    
    # Scraper service URL - defaults to mock service in local dev
    SCRAPER_SERVICE_URL: str = os.getenv("SCRAPER_SERVICE_URL", "http://localhost:8001")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
