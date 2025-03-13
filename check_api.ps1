# PowerShell script to check and test the API endpoints

# Activate virtual environment if it exists
if (Test-Path "venv") {
    .\venv\Scripts\Activate.ps1
}

# Install httpx if not already installed
pip install httpx

# Create a Python script to test the endpoints
$testScript = @"
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
        "/api/v1/accounts",
        "/api/v1/profiles",
        "/api/v1/scraper/accounts",
        "/api/v1/scraper/latest"
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in endpoints:
            print(f"\nTesting endpoint: {endpoint}")
            try:
                response = await client.get(f"{base_url}{endpoint}")
                response.raise_for_status()
                data = response.json()
                print(f"Status: {response.status_code}")
                print(f"Response: {json.dumps(data, indent=2)[:500]}...")  # Print first 500 chars
            except Exception as e:
                print(f"Error: {e}")
    
    # Test analytics if accounts exist
    try:
        print("\nChecking for accounts to test analytics...")
        response = await client.get(f"{base_url}/api/v1/accounts")
        accounts = response.json()
        
        if accounts:
            username = accounts[0].get("username", "")
            if username:
                print(f"\nTesting analytics for account: {username}")
                analytics_endpoint = f"/api/v1/analytics/growth/{username}"
                print(f"Testing endpoint: {analytics_endpoint}")
                
                try:
                    response = await client.get(f"{base_url}{analytics_endpoint}")
                    response.raise_for_status()
                    data = response.json()
                    print(f"Status: {response.status_code}")
                    print(f"Response: {json.dumps(data, indent=2)[:500]}...")  # Print first 500 chars
                except Exception as e:
                    print(f"Error: {e}")
    except Exception as e:
        print(f"Error checking accounts: {e}")
    
    print("\nAPI test complete!")

if __name__ == "__main__":
    asyncio.run(test_api())
"@

# Write the test script
$testScript | Out-File -FilePath "test_api.py" -Encoding utf8

# Run the test script
Write-Host "Testing the Logic Service API..." -ForegroundColor Green
Write-Host "Make sure the Logic Service is running (.\run_dev.ps1)" -ForegroundColor Yellow
Write-Host ""

$proceed = Read-Host -Prompt "Is the Logic Service running? (y/n)"
if ($proceed -eq "y") {
    python test_api.py
} else {
    Write-Host "Please start the Logic Service first with .\run_dev.ps1" -ForegroundColor Red
}