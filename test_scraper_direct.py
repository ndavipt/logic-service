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
