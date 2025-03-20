import httpx
from typing import List, Optional, Dict
import logging
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)

# Import mock implementation if configured
if settings.USE_MOCK_SCRAPER:
    from app.services.mock_scraper_service import (
        fetch_latest_profiles, fetch_accounts, trigger_scrape, add_account, delete_account
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
        
        Uses the scraper service API format:
        - POST /accounts with {"accounts": [{"username": "name"}]}
        - Response includes "added" and "skipped" arrays
        """
        try:
            logger.info(f"Adding account {username} at {settings.SCRAPER_SERVICE_URL}/accounts")
            payload = {
                "accounts": [
                    {"username": username}
                ]
            }
            headers = {"Content-Type": "application/json"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.SCRAPER_SERVICE_URL}/accounts",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                
                # Process response to return meaningful result
                if username in result.get("added", []):
                    return {
                        "status": "success", 
                        "message": f"Successfully added account: {username}"
                    }
                else:
                    # Find reason in skipped array if account wasn't added
                    reason = next((item["reason"] for item in result.get("skipped", [])
                                if item["username"] == username), "Unknown reason")
                    return {
                        "status": "error", 
                        "message": f"Account not added: {reason}"
                    }
                    
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while adding account: {e}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error while adding account: {e}")
            return {"status": "error", "message": str(e)}
            
    async def delete_account(username: str) -> Dict:
        """
        Delete an account from tracking in the Scraper Service.
        """
        try:
            logger.info(f"Deleting account {username} at {settings.SCRAPER_SERVICE_URL}/accounts/{username}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.delete(
                    f"{settings.SCRAPER_SERVICE_URL}/accounts/{username}"
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while deleting account: {e}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error while deleting account: {e}")
            return {"status": "error", "message": str(e)}
