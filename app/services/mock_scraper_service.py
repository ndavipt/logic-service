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
    
    Matches the real scraper service API format:
    - Expects username parameter
    - Returns result in the format of {"status": "success", "message": "..."}
    """
    logger.info(f"Using mock scraper service: add_account({username})")
    
    # Check if account already exists
    if any(account["username"] == username for account in _accounts):
        return {
            "status": "error",
            "message": f"Account not added: Account with username '{username}' already exists"
        }
    
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
    
    # Return result formatted like the real API would
    return {
        "status": "success",
        "message": f"Successfully added account: {username}"
    }

async def delete_account(username: str) -> Dict:
    """
    Mock implementation that deletes an account.
    """
    logger.info(f"Using mock scraper service: delete_account({username})")
    
    # Find and remove account
    for i, account in enumerate(_accounts):
        if account["username"] == username:
            del _accounts[i]
            
            # Remove associated profile
            for j, profile in enumerate(_profiles):
                if profile["username"] == username:
                    del _profiles[j]
                    break
                    
            return {"message": f"Account '{username}' and all associated profile data deleted successfully"}
    
    return {"status": "error", "message": f"Account '{username}' not found"}
