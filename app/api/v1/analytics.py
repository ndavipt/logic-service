from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.analytics_service import get_growth_metrics, get_comparison_data
from app.services.cache import get_cache, set_cache

router = APIRouter()

@router.get("/growth/{username}", response_model=dict)
async def read_growth_metrics(
    username: str,
    days: Optional[int] = Query(30, description="Number of days to analyze"),
    refresh: Optional[bool] = Query(False, description="Force refresh data from database"),
    db: Session = Depends(get_db)
):
    """
    Calculate growth metrics for a specific account.
    
    - Change between each scrape
    - Change in last 12 hours
    - Change in last 24 hours
    - 7-day rolling average of daily change
    """
    # Check cache first unless refresh is requested
    cache_key = f"growth_metrics:{username}:{days}"
    if not refresh:
        cached_data = get_cache(cache_key)
        if cached_data:
            return cached_data
    
    metrics = get_growth_metrics(db, username=username, days=days)
    if not metrics:
        raise HTTPException(status_code=404, detail=f"Growth metrics for {username} not found")
    
    # Cache result for 15 minutes (900 seconds)
    set_cache(cache_key, metrics, expire_seconds=900)
    
    return metrics

@router.get("/changes/{username}", response_model=dict)
async def read_follower_changes(
    username: str,
    days: Optional[int] = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get detailed follower changes for a specific account.
    
    - Changes between each scrape
    - 12-hour change
    - 24-hour change
    """
    metrics = get_growth_metrics(db, username=username, days=days)
    if not metrics:
        raise HTTPException(status_code=404, detail=f"Follower changes for {username} not found")
    
    return {
        "username": metrics["username"],
        "current_followers": metrics["end_followers"],
        "changes_between_scrapes": metrics["changes_between_scrapes"],
        "change_12h": metrics["change_12h"],
        "change_24h": metrics["change_24h"],
        "data_points": metrics["data_points"]
    }

@router.get("/rolling-average/{username}", response_model=dict)
async def read_rolling_average(
    username: str,
    days: Optional[int] = Query(7, description="Rolling window in days"),
    db: Session = Depends(get_db)
):
    """
    Get rolling average of follower growth.
    """
    metrics = get_growth_metrics(db, username=username, days=days + 7)  # Add extra days for more data points
    if not metrics:
        raise HTTPException(status_code=404, detail=f"Rolling average for {username} not found")
    
    return {
        "username": metrics["username"],
        "current_followers": metrics["end_followers"],
        "rolling_avg_7day": metrics["rolling_avg_7day"]
    }

@router.get("/compare", response_model=dict)
async def compare_accounts(
    usernames: List[str] = Query(..., description="List of usernames to compare"),
    days: Optional[int] = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Compare growth metrics between multiple accounts.
    """
    comparison = get_comparison_data(db, usernames=usernames, days=days)
    return comparison