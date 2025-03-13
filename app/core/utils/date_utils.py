from datetime import datetime, timedelta
from typing import List, Tuple

def get_date_range(days: int) -> Tuple[datetime, datetime]:
    """
    Calculate start and end dates for a date range.
    
    Args:
        days: Number of days to look back
        
    Returns:
        Tuple of (start_date, end_date)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def date_range_to_str(start_date: datetime, end_date: datetime) -> str:
    """
    Format date range for display.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Formatted date range string
    """
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    return f"{start_str} to {end_str}"

def get_date_intervals(start_date: datetime, end_date: datetime, interval_days: int = 7) -> List[datetime]:
    """
    Get evenly spaced dates between start and end date.
    
    Args:
        start_date: Start date
        end_date: End date
        interval_days: Number of days between intervals
        
    Returns:
        List of datetime objects representing the intervals
    """
    dates = []
    current = start_date
    
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=interval_days)
    
    # Add end date if it's not already included
    if dates[-1] != end_date:
        dates.append(end_date)
        
    return dates