# PowerShell script to fix API issues

# Activate virtual environment if it exists
if (Test-Path "venv") {
    .\venv\Scripts\Activate.ps1
}

# Fix the FastAPI trailing slash and scraper service issues
$fixApiMain = @"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.router import router as api_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create FastAPI app with trailing slash configuration
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Logic Service API for Instagram data analytics",
    version="0.1.0",
    # Don't redirect when trailing slash is missing
    redirect_slashes=False
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Logic Service API",
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": settings.PROJECT_NAME
    }
"@

# Create fixed app/main.py
$fixApiMain | Out-File -FilePath "app/main.py" -Encoding utf8

# Fix the scraper service implementation to handle errors better
$fixScraperService = @"
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
            logger.info(f"Fetching profiles from {settings.SCRAPER_SERVICE_URL}/profiles")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{settings.SCRAPER_SERVICE_URL}/profiles")
                response.raise_for_status()
                
                # Get the JSON data
                data = response.json()
                logger.info(f"Received profiles response: {data}")
                
                # Handle different response formats
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "profiles" in data:
                    return data["profiles"]
                else:
                    logger.warning(f"Unexpected profiles data format: {type(data)}")
                    return []
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while fetching profiles: {e}")
            return []  # Return empty list instead of raising exception
        except Exception as e:
            logger.error(f"Unexpected error while fetching profiles: {e}")
            return []  # Return empty list instead of raising exception

    async def fetch_accounts() -> List[Dict]:
        """
        Fetch the list of tracked accounts from the Scraper Service.
        """
        try:
            logger.info(f"Fetching accounts from {settings.SCRAPER_SERVICE_URL}/accounts")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{settings.SCRAPER_SERVICE_URL}/accounts")
                response.raise_for_status()
                
                # Get the JSON data
                data = response.json()
                logger.info(f"Received accounts response: {data}")
                
                # Handle different response formats
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "accounts" in data:
                    return data["accounts"]
                else:
                    logger.warning(f"Unexpected accounts data format: {type(data)}")
                    return []
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while fetching accounts: {e}")
            return []  # Return empty list instead of raising exception
        except Exception as e:
            logger.error(f"Unexpected error while fetching accounts: {e}")
            return []  # Return empty list instead of raising exception

    async def trigger_scrape() -> Dict:
        """
        Trigger a manual scrape in the Scraper Service.
        """
        try:
            logger.info(f"Triggering scrape at {settings.SCRAPER_SERVICE_URL}/scrape-accounts")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{settings.SCRAPER_SERVICE_URL}/scrape-accounts")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while triggering scrape: {e}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error while triggering scrape: {e}")
            return {"status": "error", "message": str(e)}

    async def add_account(username: str) -> Dict:
        """
        Add a new account to track in the Scraper Service.
        """
        try:
            logger.info(f"Adding account {username} at {settings.SCRAPER_SERVICE_URL}/accounts")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.SCRAPER_SERVICE_URL}/accounts",
                    json={"username": username}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while adding account: {e}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error while adding account: {e}")
            return {"status": "error", "message": str(e)}
"@

# Create fixed scraper service
$fixScraperService | Out-File -FilePath "app/services/scraper_service.py" -Encoding utf8

# Create a mock scraper service implementation
$mockScraperService = @"
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
"@

# Create mock scraper service
$mockScraperService | Out-File -FilePath "app/services/mock_scraper_service.py" -Encoding utf8

# Fix the API routers to handle missing trailing slashes
$fixApiRouter = @"
from fastapi import APIRouter

from app.api.v1 import accounts, profiles, analytics, scraper

router = APIRouter(prefix="/api/v1")

# Include routers with and without trailing slashes
router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
router.include_router(scraper.router, prefix="/scraper", tags=["scraper"])

# Add duplicate routes without trailing slashes
for route in list(accounts.router.routes):
    if str(route.path).endswith('/'):
        new_path = str(route.path)[:-1]  # Remove trailing slash
        accounts.router.add_api_route(new_path, route.endpoint, **route.endpoint_kwargs)

for route in list(profiles.router.routes):
    if str(route.path).endswith('/'):
        new_path = str(route.path)[:-1]  # Remove trailing slash
        profiles.router.add_api_route(new_path, route.endpoint, **route.endpoint_kwargs)

for route in list(analytics.router.routes):
    if str(route.path).endswith('/'):
        new_path = str(route.path)[:-1]  # Remove trailing slash
        analytics.router.add_api_route(new_path, route.endpoint, **route.endpoint_kwargs)

for route in list(scraper.router.routes):
    if str(route.path).endswith('/'):
        new_path = str(route.path)[:-1]  # Remove trailing slash
        scraper.router.add_api_route(new_path, route.endpoint, **route.endpoint_kwargs)
"@

# Write the improved API router
$fixApiRouter | Out-File -FilePath "app/api/router.py" -Encoding utf8

# Create a new check_api script that better handles redirects
$checkApiScript = @"
import asyncio
import httpx
import json
from datetime import datetime

async def test_api():
    print("Testing Logic Service API...")
    base_url = "http://localhost:8000"
    
    # Test endpoints
    endpoints = [
        "/",
        "/health",
        "/api/v1/accounts/",  # Added trailing slash
        "/api/v1/profiles/",   # Added trailing slash
        "/api/v1/scraper/accounts/",  # Added trailing slash
        "/api/v1/scraper/latest/"     # Added trailing slash
    ]
    
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        for endpoint in endpoints:
            print(f"\nTesting endpoint: {endpoint}")
            try:
                response = await client.get(f"{base_url}{endpoint}")
                status = response.status_code
                print(f"Status: {status}")
                
                if status < 400:  # Successful response
                    try:
                        data = response.json()
                        print(f"Response: {json.dumps(data, indent=2)[:500]}...")  # Print first 500 chars
                    except:
                        print(f"Response is not JSON. Text: {response.text[:200]}...")
                else:
                    print(f"Error response: {response.text[:200]}")
            except Exception as e:
                print(f"Error: {e}")
    
    # Test analytics if accounts exist
    try:
        print("\nChecking for accounts to test analytics...")
        response = await client.get(f"{base_url}/api/v1/accounts/")
        
        if response.status_code < 400:
            accounts = response.json()
            
            if accounts and len(accounts) > 0:
                if isinstance(accounts[0], dict) and "username" in accounts[0]:
                    username = accounts[0]["username"]
                elif isinstance(accounts[0], str):
                    username = accounts[0]
                else:
                    username = ""
                
                if username:
                    print(f"\nTesting analytics for account: {username}")
                    analytics_endpoint = f"/api/v1/analytics/growth/{username}"
                    print(f"Testing endpoint: {analytics_endpoint}")
                    
                    try:
                        response = await client.get(f"{base_url}{analytics_endpoint}")
                        status = response.status_code
                        print(f"Status: {status}")
                        
                        if status < 400:  # Successful response
                            data = response.json()
                            print(f"Response: {json.dumps(data, indent=2)[:500]}...")  # Print first 500 chars
                        else:
                            print(f"Error response: {response.text[:200]}")
                    except Exception as e:
                        print(f"Error: {e}")
            else:
                print("No accounts found to test analytics")
                
    except Exception as e:
        print(f"Error checking accounts: {e}")
    
    print("\nAPI test complete!")

if __name__ == "__main__":
    asyncio.run(test_api())
"@

# Write the improved API test script
$checkApiScript | Out-File -FilePath "test_api.py" -Encoding utf8

Write-Host "API fixes applied. Please restart the Logic Service:" -ForegroundColor Green
Write-Host "1. First stop the current service with Ctrl+C" -ForegroundColor Yellow
Write-Host "2. Then start it again with: .\run_dev.ps1" -ForegroundColor Yellow
Write-Host "3. Once it's running, run: .\check_api.ps1" -ForegroundColor Yellow