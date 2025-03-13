# PowerShell script to test direct communication with the real Scraper Service

# Activate virtual environment if it exists
if (Test-Path "venv") {
    .\venv\Scripts\Activate.ps1
}

# Install necessary packages
pip install httpx asyncio

# Create a Python script to test direct scraper communication
$scriptContent = @"
import asyncio
import httpx
import json
from datetime import datetime
import sys

async def test_scraper(url):
    print(f"Testing direct connection to Scraper Service at: {url}")
    
    endpoints = [
        "/",                  # Root endpoint
        "/accounts",          # Get accounts
        "/profiles"           # Get profiles
    ]
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        for endpoint in endpoints:
            print(f"\nTesting endpoint: {endpoint}")
            try:
                full_url = f"{url}{endpoint}"
                print(f"Making request to: {full_url}")
                response = await client.get(full_url)
                status = response.status_code
                print(f"Status: {status}")
                
                if status < 400:  # Successful response
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"Response: List with {len(data)} items")
                            if data:
                                print(f"First item sample: {json.dumps(data[0], indent=2)}")
                        elif isinstance(data, dict):
                            print(f"Response: Dictionary with keys: {list(data.keys())}")
                            print(f"Sample: {json.dumps(list(data.items())[:3], indent=2)}")
                        else:
                            print(f"Response type: {type(data)}")
                            print(f"Raw response: {response.text[:500]}...")
                    except Exception as e:
                        print(f"Error parsing JSON: {e}")
                        print(f"Raw response: {response.text[:500]}...")
                else:
                    print(f"Error response: {response.text[:200]}")
            except Exception as e:
                print(f"Error: {e}")
    
    # Test adding an account
    try:
        print("\nTesting POST /accounts (adding an account)")
        test_username = "test_account_" + datetime.now().strftime("%H%M%S")
        
        post_url = f"{url}/accounts"
        print(f"POST {post_url} with data: {{username: {test_username}}}")
        
        response = await client.post(
            post_url,
            json={"username": test_username}
        )
        
        status = response.status_code
        print(f"Status: {status}")
        
        if status < 400:
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            except:
                print(f"Raw response: {response.text[:200]}")
        else:
            print(f"Error response: {response.text[:200]}")
    except Exception as e:
        print(f"Error adding account: {e}")
    
    # Test triggering a scrape
    try:
        print("\nTesting POST /scrape-accounts (triggering a scrape)")
        
        post_url = f"{url}/scrape-accounts"
        print(f"POST {post_url}")
        
        response = await client.post(post_url)
        
        status = response.status_code
        print(f"Status: {status}")
        
        if status < 400:
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            except:
                print(f"Raw response: {response.text[:200]}")
        else:
            print(f"Error response: {response.text[:200]}")
    except Exception as e:
        print(f"Error triggering scrape: {e}")
    
    print("\nTest complete!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        scraper_url = sys.argv[1]
    else:
        scraper_url = input("Enter the Scraper Service URL: ")
    
    asyncio.run(test_scraper(scraper_url))
"@

# Write the script to a file
$scriptContent | Out-File -FilePath "test_scraper_direct.py" -Encoding utf8

# Ask for the scraper URL
$scraperUrl = Read-Host -Prompt "Enter your Scraper Service URL (e.g., https://scraper-service-907s.onrender.com)"

# Run the test script
Write-Host "Testing direct connection to your Scraper Service..." -ForegroundColor Green
python test_scraper_direct.py $scraperUrl

# After testing, prompt to update the config
$proceed = Read-Host -Prompt "Do you want to configure the Logic Service to use this Scraper Service? (y/n)"

if ($proceed -eq "y") {
    # Update .env file
    @"
# Database connection
# Use SQLite for local development to avoid PostgreSQL dependency
DATABASE_URL=sqlite:///./instagram.db

# For PostgreSQL (when ready):
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/instagram

# Redis for caching (can be disabled)
REDIS_URL=redis://localhost:6379/0

# Scraper service URL - using real service
SCRAPER_SERVICE_URL=$scraperUrl

# Set to false to use the real scraper service
USE_MOCK_SCRAPER=false
"@ | Out-File -FilePath ".env" -Encoding utf8
    
    Write-Host "Updated .env file to use the real Scraper Service at $scraperUrl" -ForegroundColor Green
    
    # Create a script to fetch data and run the service
    $runWithRealDataScript = @"
import asyncio
import httpx
import json
import sys
import os
import time
import sqlite3
from datetime import datetime

# Set environment variables
os.environ["SCRAPER_SERVICE_URL"] = "$scraperUrl"
os.environ["USE_MOCK_SCRAPER"] = "false"

async def fetch_data():
    print(f"Fetching data from Scraper Service at {os.environ['SCRAPER_SERVICE_URL']}")
    scraper_url = os.environ["SCRAPER_SERVICE_URL"]
    
    # Connect to SQLite database
    print("Connecting to SQLite database...")
    db_path = "./instagram.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    print("Creating tables if they don't exist...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS instagram_accounts (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS instagram_profiles (
        id INTEGER PRIMARY KEY,
        account_id INTEGER,
        follower_count INTEGER,
        profile_pic_url TEXT,
        full_name TEXT,
        biography TEXT,
        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (account_id) REFERENCES instagram_accounts(id)
    )
    ''')
    
    conn.commit()
    
    try:
        # Fetch accounts
        print(f"Fetching accounts from {scraper_url}/accounts")
        async with httpx.AsyncClient(timeout=30.0) as client:
            accounts_response = await client.get(f"{scraper_url}/accounts")
            accounts_response.raise_for_status()
            
            # Try to parse the JSON response
            try:
                accounts_data = accounts_response.json()
                # Handle different response formats
                if isinstance(accounts_data, dict) and "accounts" in accounts_data:
                    accounts_data = accounts_data["accounts"]
                    
                print(f"Fetched {len(accounts_data) if isinstance(accounts_data, list) else 'unknown'} accounts")
                
                # Process accounts
                if isinstance(accounts_data, list):
                    for account in accounts_data:
                        username = None
                        if isinstance(account, str):
                            username = account
                        elif isinstance(account, dict) and "username" in account:
                            username = account["username"]
                        
                        if username:
                            # Check if account exists
                            cursor.execute("SELECT id FROM instagram_accounts WHERE username = ?", (username,))
                            existing = cursor.fetchone()
                            
                            if not existing:
                                print(f"Adding account: {username}")
                                cursor.execute(
                                    "INSERT INTO instagram_accounts (username, status) VALUES (?, ?)",
                                    (username, "active")
                                )
                            else:
                                print(f"Account already exists: {username}")
                else:
                    print(f"Unexpected accounts data type: {type(accounts_data)}")
            except Exception as e:
                print(f"Error processing accounts: {e}")
                print(f"Raw response: {accounts_response.text[:500]}")
        
        # Commit account changes
        conn.commit()
        
        # Fetch profiles
        print(f"Fetching profiles from {scraper_url}/profiles")
        async with httpx.AsyncClient(timeout=30.0) as client:
            profiles_response = await client.get(f"{scraper_url}/profiles")
            profiles_response.raise_for_status()
            
            # Try to parse the JSON response
            try:
                profiles_data = profiles_response.json()
                # Handle different response formats
                if isinstance(profiles_data, dict) and "profiles" in profiles_data:
                    profiles_data = profiles_data["profiles"]
                    
                print(f"Fetched {len(profiles_data) if isinstance(profiles_data, list) else 'unknown'} profiles")
                
                # Process profiles
                if isinstance(profiles_data, list):
                    for profile in profiles_data:
                        # Extract profile data based on various possible formats
                        username = None
                        follower_count = 0
                        profile_pic_url = ""
                        full_name = ""
                        biography = ""
                        
                        if isinstance(profile, dict):
                            # Get username
                            if "username" in profile:
                                username = profile["username"]
                            
                            # Get follower count
                            if "follower_count" in profile:
                                follower_count = profile["follower_count"]
                            elif "followers" in profile:
                                follower_count = profile["followers"]
                            
                            # Get profile pic
                            if "profile_pic_url" in profile:
                                profile_pic_url = profile["profile_pic_url"]
                            elif "profile_picture" in profile:
                                profile_pic_url = profile["profile_picture"]
                            
                            # Get full name
                            if "full_name" in profile:
                                full_name = profile["full_name"]
                            elif "name" in profile:
                                full_name = profile["name"]
                            
                            # Get biography
                            if "biography" in profile:
                                biography = profile["biography"]
                            elif "bio" in profile:
                                biography = profile["bio"]
                        
                        if username:
                            # Get account ID
                            cursor.execute("SELECT id FROM instagram_accounts WHERE username = ?", (username,))
                            account_row = cursor.fetchone()
                            
                            if account_row:
                                account_id = account_row[0]
                                
                                # Add profile data
                                print(f"Adding profile for: {username}")
                                cursor.execute(
                                    "INSERT INTO instagram_profiles (account_id, follower_count, profile_pic_url, full_name, biography, checked_at) "
                                    "VALUES (?, ?, ?, ?, ?, ?)",
                                    (account_id, follower_count, profile_pic_url, full_name, biography, datetime.now().isoformat())
                                )
                            else:
                                print(f"Account not found for profile: {username}")
                else:
                    print(f"Unexpected profiles data type: {type(profiles_data)}")
            except Exception as e:
                print(f"Error processing profiles: {e}")
                print(f"Raw response: {profiles_response.text[:500]}")
        
        # Commit profile changes
        conn.commit()
        print("Data import complete!")
        
    except Exception as e:
        print(f"Error during data fetch: {e}")
        conn.rollback()
    finally:
        # Close database connection
        conn.close()

# Run the data fetch
asyncio.run(fetch_data())

# Run the FastAPI server
print("Starting the Logic Service...")
print("Press Ctrl+C to exit")
time.sleep(1)

# Use subprocess to run the server
import subprocess
subprocess.run(["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
"@

    # Write the script
    $runWithRealDataScript | Out-File -FilePath "run_with_real_data.py" -Encoding utf8
    
    # Create a PowerShell script to run it
    @"
# PowerShell script to run the Logic Service with real data

# Activate virtual environment if it exists
if (Test-Path "venv") {
    .\venv\Scripts\Activate.ps1
}

# Run the Python script
Write-Host "Fetching data from Scraper Service and starting Logic Service..." -ForegroundColor Green
python run_with_real_data.py
"@ | Out-File -FilePath "run_with_real_data.ps1" -Encoding utf8
    
    Write-Host "Created run_with_real_data.ps1 script" -ForegroundColor Green
    Write-Host "To run the Logic Service with real data, use:" -ForegroundColor Cyan
    Write-Host ".\run_with_real_data.ps1" -ForegroundColor Cyan
}