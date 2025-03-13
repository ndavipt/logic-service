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
