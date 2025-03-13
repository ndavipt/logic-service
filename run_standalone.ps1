# PowerShell script to run the application in standalone mode
# This version doesn't require the external mock scraper service

# Activate virtual environment if it exists
if (Test-Path "venv") {
    .\venv\Scripts\Activate.ps1
}

# Set environment variables to use mock data
$env:PYTHONPATH = (Get-Location).Path
$env:ENVIRONMENT = "development"
$env:USE_MOCK_SCRAPER = "true"

# Make sure required packages are installed
pip install fastapi uvicorn httpx

# Update the configuration to use mocked scraper service
$code = @'
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
    ]
    
    # Scraper service URL - defaults to mock service in local dev
    SCRAPER_SERVICE_URL: str = os.getenv("SCRAPER_SERVICE_URL", "http://localhost:8001")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
'@

# Write the updated config
$code | Out-File -FilePath "app/core/config.py" -Encoding utf8

# Create mock scraper service implementation
$mockCode = @'
from typing import List, Dict
import logging
from datetime import datetime
import random

logger = logging.getLogger(__name__)

# Mock data
_accounts = [
    {"username": "instagram", "status": "active", "created_at": "2023-01-01T00:00:00"},
    {"username": "google", "status": "active", "created_at": "2023-01-01T00:00:00"}
]

_profiles = [
    {
        "username": "instagram",
        "follower_count": 500000000,
        "profile_pic_url": "https://example.com/instagram.jpg",
        "full_name": "Instagram",
        "biography": "Instagram official account",
        "checked_at": datetime.now().isoformat()
    },
    {
        "username": "google",
        "follower_count": 30000000,
        "profile_pic_url": "https://example.com/google.jpg",
        "full_name": "Google",
        "biography": "Google official account",
        "checked_at": datetime.now().isoformat()
    }
]

async def fetch_latest_profiles() -> List[Dict]:
    """
    Mock implementation that returns static profile data.
    """
    logger.info("Using mock scraper service: fetch_latest_profiles")
    return _profiles

async def fetch_accounts() -> List[Dict]:
    """
    Mock implementation that returns static account data.
    """
    logger.info("Using mock scraper service: fetch_accounts")
    return _accounts

async def trigger_scrape() -> Dict:
    """
    Mock implementation that simulates a scrape.
    """
    logger.info("Using mock scraper service: trigger_scrape")
    # Update timestamps and follower counts
    for profile in _profiles:
        profile["checked_at"] = datetime.now().isoformat()
        profile["follower_count"] += random.randint(-100, 500)
    
    return {"status": "success", "message": "Mock scrape completed successfully"}

async def add_account(username: str) -> Dict:
    """
    Mock implementation that adds an account.
    """
    logger.info(f"Using mock scraper service: add_account({username})")
    
    # Create new account
    new_account = {
        "username": username,
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    _accounts.append(new_account)
    
    # Create associated profile
    new_profile = {
        "username": username,
        "follower_count": 10000,
        "profile_pic_url": f"https://example.com/{username}.jpg",
        "full_name": username.capitalize(),
        "biography": f"This is {username}'s account",
        "checked_at": datetime.now().isoformat()
    }
    _profiles.append(new_profile)
    
    return new_account
'@

# Write the mock implementation
$mockCode | Out-File -FilePath "app/services/mock_scraper_service.py" -Encoding utf8

# Update the scraper service to use mock when configured
$scaperCode = @'
import httpx
from typing import List, Optional, Dict
import logging
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)

# Import mock implementation if configured
if settings.USE_MOCK_SCRAPER:
    from app.services.mock_scraper_service import (
        fetch_latest_profiles, fetch_accounts, trigger_scrape, add_account
    )
else:
    # Real implementation that calls the external service
    async def fetch_latest_profiles() -> List[Dict]:
        """
        Fetch the latest profile data from the Scraper Service.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{settings.SCRAPER_SERVICE_URL}/profiles")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while fetching profiles: {e}")
            raise HTTPException(status_code=503, detail=f"Error fetching data from Scraper Service: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error while fetching profiles: {e}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def fetch_accounts() -> List[Dict]:
        """
        Fetch the list of tracked accounts from the Scraper Service.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{settings.SCRAPER_SERVICE_URL}/accounts")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while fetching accounts: {e}")
            raise HTTPException(status_code=503, detail=f"Error fetching accounts from Scraper Service: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error while fetching accounts: {e}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def trigger_scrape() -> Dict:
        """
        Trigger a manual scrape in the Scraper Service.
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{settings.SCRAPER_SERVICE_URL}/scrape-accounts")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while triggering scrape: {e}")
            raise HTTPException(status_code=503, detail=f"Error triggering scrape: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error while triggering scrape: {e}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def add_account(username: str) -> Dict:
        """
        Add a new account to track in the Scraper Service.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.SCRAPER_SERVICE_URL}/accounts",
                    json={"username": username}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while adding account: {e}")
            raise HTTPException(status_code=503, detail=f"Error adding account: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error while adding account: {e}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
'@

# Write the updated scraper service
$scaperCode | Out-File -FilePath "app/services/scraper_service.py" -Encoding utf8

# Run the service with auto-reload
Write-Host "Starting FastAPI development server in standalone mode..." -ForegroundColor Green
Write-Host "Mock scraper service is enabled - no need to run a separate mock server" -ForegroundColor Cyan
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000