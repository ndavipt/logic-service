from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn
from datetime import datetime

app = FastAPI(title="Mock Scraper Service")

# Sample data
accounts = [
    {"username": "instagram", "status": "active", "created_at": "2023-01-01T00:00:00"},
    {"username": "google", "status": "active", "created_at": "2023-01-01T00:00:00"}
]

profiles = [
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

class AccountCreate(BaseModel):
    username: str

@app.get("/")
async def root():
    return {"message": "Mock Scraper Service"}

@app.get("/accounts")
async def get_accounts():
    return accounts

@app.get("/profiles")
async def get_profiles():
    return profiles

@app.post("/accounts")
async def add_account(account: AccountCreate):
    new_account = {
        "username": account.username,
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    accounts.append(new_account)
    
    # Also add a profile
    new_profile = {
        "username": account.username,
        "follower_count": 10000,
        "profile_pic_url": f"https://example.com/{account.username}.jpg",
        "full_name": account.username.capitalize(),
        "biography": f"This is {account.username}'s account",
        "checked_at": datetime.now().isoformat()
    }
    profiles.append(new_profile)
    
    return new_account

@app.post("/scrape-accounts")
async def scrape_accounts():
    # Simulate scraping by updating the checked_at time
    for profile in profiles:
        profile["checked_at"] = datetime.now().isoformat()
        # Add a small random change to follower count
        import random
        profile["follower_count"] += random.randint(-100, 500)
    
    return {"status": "success", "message": "Scrape completed successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
