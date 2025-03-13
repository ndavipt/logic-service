from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.profile_service import get_latest_profiles, get_profile_history, get_latest_profile

router = APIRouter()

@router.get("/", response_model=List[dict])
async def read_latest_profiles(db: Session = Depends(get_db)):
    """
    Retrieve latest profile data for all accounts.
    """
    profiles = get_latest_profiles(db)
    return profiles

@router.get("/current/{username}", response_model=Dict)
async def read_current_profile(
    username: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve current profile data with follower count for a specific account.
    """
    profile = get_latest_profile(db, username=username)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile for {username} not found")
    return profile

@router.get("/history/{username}", response_model=List[dict])
async def read_profile_history(
    username: str,
    days: Optional[int] = Query(30, description="Number of days of history to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Retrieve historical profile data for a specific account.
    """
    profiles = get_profile_history(db, username=username, days=days)
    if not profiles:
        raise HTTPException(status_code=404, detail=f"Profile history for {username} not found")
    return profiles