from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.account import InstagramAccount
from app.models.profile import InstagramProfile
from app.services.cache import clear_cache_pattern

def get_latest_profiles(db: Session) -> List[dict]:
    """
    Retrieve latest profile data for all accounts.
    Uses a subquery to get the latest profile for each account.
    """
    # Subquery to get the latest profile ID for each account
    latest_profiles = db.query(
        InstagramProfile.account_id,
        func.max(InstagramProfile.checked_at).label("latest_checked_at")
    ).group_by(InstagramProfile.account_id).subquery()
    
    # Join with the profiles and accounts tables
    result = db.query(
        InstagramAccount.username,
        InstagramProfile
    ).join(
        latest_profiles,
        InstagramProfile.account_id == latest_profiles.c.account_id
    ).filter(
        InstagramProfile.checked_at == latest_profiles.c.latest_checked_at
    ).join(
        InstagramAccount
    ).all()
    
    return [
        {
            "username": username,
            "follower_count": profile.follower_count,
            "profile_pic_url": profile.profile_pic_url,
            "full_name": profile.full_name,
            "biography": profile.biography,
            "checked_at": profile.checked_at
        }
        for username, profile in result
    ]

def get_latest_profile(db: Session, username: str) -> Optional[Dict]:
    """
    Retrieve the most recent profile data for a specific account.
    """
    result = db.query(
        InstagramProfile
    ).join(
        InstagramAccount
    ).filter(
        InstagramAccount.username == username
    ).order_by(
        desc(InstagramProfile.checked_at)
    ).first()
    
    if not result:
        return None
    
    return {
        "username": username,
        "follower_count": result.follower_count,
        "profile_pic_url": result.profile_pic_url,
        "full_name": result.full_name,
        "biography": result.biography,
        "checked_at": result.checked_at
    }

def get_profile_history(db: Session, username: str, days: int = 30) -> List[dict]:
    """
    Retrieve historical profile data for a specific account over a period of days.
    """
    # Calculate the date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Query the database for the account's profiles within the date range
    result = db.query(
        InstagramProfile
    ).join(
        InstagramAccount
    ).filter(
        InstagramAccount.username == username,
        InstagramProfile.checked_at >= start_date
    ).order_by(
        InstagramProfile.checked_at
    ).all()
    
    return [
        {
            "follower_count": profile.follower_count,
            "checked_at": profile.checked_at,
            "profile_pic_url": profile.profile_pic_url,
            "full_name": profile.full_name,
            "biography": profile.biography
        }
        for profile in result
    ]

def get_followers_at_time(db: Session, username: str, target_time: datetime) -> Optional[Dict]:
    """
    Get the follower count at or before a specific time.
    Finds the closest data point before the target time.
    """
    # Find the closest profile before the target time
    profile = db.query(InstagramProfile).join(
        InstagramAccount
    ).filter(
        InstagramAccount.username == username,
        InstagramProfile.checked_at <= target_time
    ).order_by(
        desc(InstagramProfile.checked_at)
    ).first()
    
    if not profile:
        return None
    
    return {
        "follower_count": profile.follower_count,
        "checked_at": profile.checked_at
    }

def refresh_analytics_cache(username: str) -> None:
    """
    Clear analytics cache for a specific username when new data is available.
    This ensures that analytics endpoints will recalculate with the latest data.
    """
    # Clear all analytics cache patterns for this username
    clear_cache_pattern(f"growth_metrics:{username}:*")
    clear_cache_pattern(f"follower_changes:{username}:*")
    clear_cache_pattern(f"rolling_average:{username}:*")