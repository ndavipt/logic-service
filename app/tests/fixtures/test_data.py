from datetime import datetime, timedelta
import pytest
from app.models.account import InstagramAccount
from app.models.profile import InstagramProfile

def create_test_data(db_session):
    """
    Create test data for a single account with follower count history
    """
    # Create account
    account = InstagramAccount(username="test_account", status="active")
    db_session.add(account)
    db_session.commit()
    
    # Create profile history with data points over the last 30 days
    now = datetime.now()
    
    # Start with 1000 followers and have some variability in growth
    follower_count = 1000
    
    for days_ago in range(30, -1, -1):  # From 30 days ago to today
        # Create datetime for this data point
        date_point = now - timedelta(days=days_ago)
        
        # Vary follower growth between -5 and +20 per day with more growth on average
        if days_ago > 0:  # Skip the first point
            follower_change = 10 + (days_ago % 7) - (days_ago % 5)  # Creates some variability
            follower_count += follower_change
        
        profile = InstagramProfile(
            account_id=account.id,
            follower_count=follower_count,
            profile_pic_url=f"https://example.com/pic_{account.username}.jpg",
            full_name=f"Test Account",
            biography="This is a test account for analytics",
            checked_at=date_point
        )
        
        db_session.add(profile)
    
    # Add some additional data points for today to simulate multiple scrapes
    hours_offsets = [20, 16, 12, 8, 4, 2, 1]  # Hours ago
    for hours in hours_offsets:
        # Small variations in follower count for same-day scrapes
        adjustment = (hours % 5) - 1  # Small random-like adjustment
        date_point = now - timedelta(hours=hours)
        
        profile = InstagramProfile(
            account_id=account.id,
            follower_count=follower_count + adjustment,
            profile_pic_url=f"https://example.com/pic_{account.username}.jpg",
            full_name=f"Test Account",
            biography="This is a test account for analytics",
            checked_at=date_point
        )
        
        db_session.add(profile)
    
    # Create a second account for comparison
    account2 = InstagramAccount(username="comparison_account", status="active")
    db_session.add(account2)
    db_session.commit()
    
    # Add data with different growth pattern
    follower_count = 2000
    for days_ago in range(30, -1, -1):
        date_point = now - timedelta(days=days_ago)
        
        if days_ago > 0:
            # Different growth pattern
            follower_change = 5 + (days_ago % 10)
            follower_count += follower_change
        
        profile = InstagramProfile(
            account_id=account2.id,
            follower_count=follower_count,
            profile_pic_url=f"https://example.com/pic_{account2.username}.jpg",
            full_name="Comparison Account",
            biography="This is another test account for comparison",
            checked_at=date_point
        )
        
        db_session.add(profile)
    
    db_session.commit()
    
    return {"account1": account, "account2": account2}