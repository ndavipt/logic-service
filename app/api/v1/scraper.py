from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.scraper_service import fetch_latest_profiles, fetch_accounts, trigger_scrape, add_account

router = APIRouter()

@router.get("/latest", response_model=List[dict])
async def read_latest_scraper_data():
    """
    Fetch the latest profile data directly from the Scraper Service.
    """
    profiles = await fetch_latest_profiles()
    return profiles

@router.get("/accounts", response_model=List[dict])
async def read_scraper_accounts():
    """
    Fetch the list of tracked accounts from the Scraper Service.
    """
    accounts = await fetch_accounts()
    return accounts

@router.post("/trigger", response_model=dict)
async def trigger_scraper():
    """
    Trigger a manual scrape in the Scraper Service.
    """
    result = await trigger_scrape()
    return result

@router.post("/add-account", response_model=dict)
async def add_new_account(username: str = Query(..., description="Instagram username to track")):
    """
    Add a new account to track in the Scraper Service.
    """
    result = await add_account(username)
    return result