# PowerShell script to connect to the real Scraper Service

# Activate virtual environment if it exists
if (Test-Path "venv") {
    .\venv\Scripts\Activate.ps1
}

# Ask for the Scraper Service URL
$scraperUrl = Read-Host -Prompt "Enter the URL of your Scraper Service (e.g., https://scraper-service-907s.onrender.com)"

# Update the .env file with the real Scraper Service URL
@"
# Database connection
# Use SQLite for local development to avoid PostgreSQL dependency
DATABASE_URL=sqlite:///./instagram.db

# For PostgreSQL (when ready):
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/instagram

# Redis for caching (can be disabled)
REDIS_URL=redis://localhost:6379/0

# CORS - Note: don't use a comma-separated list here due to parsing issues
# These are set in app/core/config.py instead

# Scraper service URL - using the real service
SCRAPER_SERVICE_URL=$scraperUrl

# Set to false to use the real scraper service
USE_MOCK_SCRAPER=false
"@ | Out-File -FilePath ".env" -Encoding utf8

# Set environment variables
$env:PYTHONPATH = (Get-Location).Path
$env:ENVIRONMENT = "development"
$env:SCRAPER_SERVICE_URL = $scraperUrl
$env:USE_MOCK_SCRAPER = "false"

# Test the connection to the Scraper Service
Write-Host "Testing connection to Scraper Service at $scraperUrl..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$scraperUrl" -Method Get -ErrorAction Stop
    Write-Host "Successfully connected to Scraper Service!" -ForegroundColor Green
} catch {
    Write-Host "Failed to connect to Scraper Service. Error: $_" -ForegroundColor Red
    Write-Host "Will proceed with the setup, but please verify the URL is correct." -ForegroundColor Yellow
}

# Prompt to fetch initial data from the scraper
$fetchInitial = Read-Host -Prompt "Do you want to fetch initial data from the Scraper Service? (y/n)"

if ($fetchInitial -eq "y") {
    # Write a simple Python script to fetch and store initial data
    $scriptContent = @"
import asyncio
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys
import os

# Add root directory to path so we can import app modules
sys.path.insert(0, os.getcwd())

from app.models.account import InstagramAccount
from app.models.profile import InstagramProfile
from app.db.session import Base

async def fetch_and_store_data():
    print("Fetching data from Scraper Service...")
    scraper_url = os.getenv("SCRAPER_SERVICE_URL")
    
    # Create database engine and tables
    engine = create_engine("sqlite:///./instagram.db")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Fetch accounts
        print(f"Fetching accounts from {scraper_url}/accounts")
        async with httpx.AsyncClient(timeout=30.0) as client:
            accounts_response = await client.get(f"{scraper_url}/accounts")
            accounts_response.raise_for_status()
            accounts_data = accounts_response.json()
            
        print(f"Fetched {len(accounts_data)} accounts")
        
        # Fetch profiles
        print(f"Fetching profiles from {scraper_url}/profiles")
        async with httpx.AsyncClient(timeout=30.0) as client:
            profiles_response = await client.get(f"{scraper_url}/profiles")
            profiles_response.raise_for_status()
            profiles_data = profiles_response.json()
            
        print(f"Fetched {len(profiles_data)} profiles")
        
        # Store accounts
        for account_data in accounts_data:
            username = account_data.get("username")
            # Check if account already exists
            existing = db.query(InstagramAccount).filter_by(username=username).first()
            if not existing:
                account = InstagramAccount(
                    username=username,
                    status=account_data.get("status", "active"),
                    created_at=datetime.fromisoformat(account_data.get("created_at")) if "created_at" in account_data else datetime.now()
                )
                db.add(account)
                print(f"Added account: {username}")
            else:
                print(f"Account already exists: {username}")
        
        # Commit to get account IDs
        db.commit()
        
        # Store profiles
        for profile_data in profiles_data:
            username = profile_data.get("username")
            # Get account ID
            account = db.query(InstagramAccount).filter_by(username=username).first()
            if account:
                # Create profile
                profile = InstagramProfile(
                    account_id=account.id,
                    follower_count=profile_data.get("follower_count", 0),
                    profile_pic_url=profile_data.get("profile_pic_url", ""),
                    full_name=profile_data.get("full_name", ""),
                    biography=profile_data.get("biography", ""),
                    checked_at=datetime.fromisoformat(profile_data.get("checked_at")) if "checked_at" in profile_data else datetime.now()
                )
                db.add(profile)
                print(f"Added profile for: {username}")
            else:
                print(f"Account not found for profile: {username}")
        
        # Final commit
        db.commit()
        print("Data import complete!")
        
    except Exception as e:
        print(f"Error fetching or storing data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(fetch_and_store_data())
"@

    # Write the script to a file
    $scriptContent | Out-File -FilePath "fetch_initial_data.py" -Encoding utf8
    
    # Run the script
    Write-Host "Fetching initial data from the Scraper Service..." -ForegroundColor Green
    python fetch_initial_data.py
}

# Start the FastAPI server
Write-Host "Starting FastAPI server connected to real Scraper Service..." -ForegroundColor Green
Write-Host "Scraper Service URL: $scraperUrl" -ForegroundColor Cyan
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000