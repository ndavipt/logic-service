from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.account import InstagramAccount
from app.models.profile import InstagramProfile
from app.services.profile_service import get_profile_history
from app.core.utils.date_utils import get_date_range

def get_growth_metrics(db: Session, username: str, days: int = 30) -> Optional[Dict]:
    """
    Calculate growth metrics for a specific account over a period of days.
    """
    # Get the profile history
    profiles = get_profile_history(db, username=username, days=days)
    
    if not profiles or len(profiles) < 2:
        return None
    
    # Calculate metrics
    first_count = profiles[0]["follower_count"] if profiles else 0
    last_count = profiles[-1]["follower_count"] if profiles else 0
    
    # Net growth
    net_growth = last_count - first_count
    
    # Percentage growth
    percentage_growth = (net_growth / first_count * 100) if first_count > 0 else 0
    
    # Daily averages
    daily_growth = net_growth / days if days > 0 else 0
    
    # Calculate growth between each scrape
    changes_between_scrapes = []
    for i in range(1, len(profiles)):
        change = {
            "previous_count": profiles[i-1]["follower_count"],
            "current_count": profiles[i]["follower_count"],
            "change": profiles[i]["follower_count"] - profiles[i-1]["follower_count"],
            "previous_timestamp": profiles[i-1]["checked_at"],
            "current_timestamp": profiles[i]["checked_at"],
            "hours_between": (profiles[i]["checked_at"] - profiles[i-1]["checked_at"]).total_seconds() / 3600
        }
        changes_between_scrapes.append(change)
    
    # Calculate 12-hour change
    change_12h = calculate_period_change(profiles, hours=12)
    
    # Calculate 24-hour change
    change_24h = calculate_period_change(profiles, hours=24)
    
    # Calculate 7-day rolling average
    rolling_avg_7day = calculate_rolling_average(profiles, days=7)
    
    return {
        "username": username,
        "start_date": profiles[0]["checked_at"] if profiles else None,
        "end_date": profiles[-1]["checked_at"] if profiles else None,
        "start_followers": first_count,
        "end_followers": last_count,
        "net_growth": net_growth,
        "percentage_growth": round(percentage_growth, 2),
        "average_daily_growth": round(daily_growth, 2),
        "change_12h": change_12h,
        "change_24h": change_24h,
        "rolling_avg_7day": rolling_avg_7day,
        "changes_between_scrapes": changes_between_scrapes,
        "data_points": len(profiles)
    }

def calculate_period_change(profiles: List[Dict], hours: int = 24) -> Dict:
    """
    Calculate follower change over a specific period (in hours).
    """
    if not profiles or len(profiles) < 2:
        return {"change": 0, "percentage": 0}
    
    now = profiles[-1]["checked_at"]
    target_time = now - timedelta(hours=hours)
    
    # Find the closest data point before the target time
    closest_profile = None
    for profile in reversed(profiles[:-1]):  # Skip the most recent one
        if profile["checked_at"] <= target_time:
            closest_profile = profile
            break
    
    # If no profile found within the period, use the earliest available
    if not closest_profile and len(profiles) >= 2:
        closest_profile = profiles[0]
    
    if closest_profile:
        change = profiles[-1]["follower_count"] - closest_profile["follower_count"]
        percentage = (change / closest_profile["follower_count"] * 100) if closest_profile["follower_count"] > 0 else 0
        hours_actual = (profiles[-1]["checked_at"] - closest_profile["checked_at"]).total_seconds() / 3600
        
        return {
            "change": change,
            "percentage": round(percentage, 2),
            "previous_count": closest_profile["follower_count"],
            "current_count": profiles[-1]["follower_count"],
            "hours_actual": round(hours_actual, 1),
            "from_timestamp": closest_profile["checked_at"],
            "to_timestamp": profiles[-1]["checked_at"]
        }
    
    return {"change": 0, "percentage": 0}

def calculate_rolling_average(profiles: List[Dict], days: int = 7) -> Dict:
    """
    Calculate rolling average of follower growth over specified days.
    """
    if not profiles or len(profiles) < 2:
        return {"average_change": 0, "data_points": 0}
    
    now = profiles[-1]["checked_at"]
    start_time = now - timedelta(days=days)
    
    # Filter profiles within the rolling window
    window_profiles = [p for p in profiles if p["checked_at"] >= start_time]
    
    if len(window_profiles) < 2:
        return {"average_change": 0, "data_points": len(window_profiles)}
    
    # Group by day and calculate daily changes
    day_changes = []
    daily_data = {}
    
    # Get the latest profile for each day
    for profile in window_profiles:
        day_key = profile["checked_at"].date().isoformat()
        if day_key not in daily_data or profile["checked_at"] > daily_data[day_key]["checked_at"]:
            daily_data[day_key] = profile
    
    # Sort days
    sorted_days = sorted(daily_data.keys())
    
    # Calculate changes between consecutive days
    for i in range(1, len(sorted_days)):
        prev_day = sorted_days[i-1]
        curr_day = sorted_days[i]
        
        change = daily_data[curr_day]["follower_count"] - daily_data[prev_day]["follower_count"]
        
        # Calculate hours between measurements for normalizing to daily change
        hours_between = (daily_data[curr_day]["checked_at"] - daily_data[prev_day]["checked_at"]).total_seconds() / 3600
        
        # Normalize to daily change rate (24 hours) if we have different intervals
        if hours_between > 0 and hours_between != 24:
            normalized_change = (change / hours_between) * 24
        else:
            normalized_change = change
            
        day_changes.append(normalized_change)
    
    # Calculate average (handling empty list case)
    avg_change = sum(day_changes) / len(day_changes) if day_changes else 0
    
    return {
        "average_change": round(avg_change, 2),
        "total_change": sum(day_changes),
        "days_covered": len(sorted_days),
        "data_points": len(window_profiles),
        "from_date": window_profiles[0]["checked_at"].date().isoformat() if window_profiles else None,
        "to_date": window_profiles[-1]["checked_at"].date().isoformat() if window_profiles else None
    }

def get_comparison_data(db: Session, usernames: List[str], days: int = 30) -> Dict:
    """
    Compare growth metrics between multiple accounts.
    """
    results = {}
    
    for username in usernames:
        metrics = get_growth_metrics(db, username=username, days=days)
        if metrics:
            results[username] = metrics
    
    # Calculate rankings
    if results:
        # Sort by different metrics
        net_growth_rank = sorted(results.keys(), key=lambda x: results[x]["net_growth"], reverse=True)
        percentage_growth_rank = sorted(results.keys(), key=lambda x: results[x]["percentage_growth"], reverse=True)
        daily_growth_rank = sorted(results.keys(), key=lambda x: results[x]["average_daily_growth"], reverse=True)
        
        # Add ranking information
        for username in results:
            results[username]["rankings"] = {
                "net_growth": net_growth_rank.index(username) + 1,
                "percentage_growth": percentage_growth_rank.index(username) + 1,
                "daily_growth": daily_growth_rank.index(username) + 1
            }
    
    return {
        "accounts": results,
        "comparison_period_days": days
    }