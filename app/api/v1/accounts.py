from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.account import InstagramAccount
from app.services.account_service import get_accounts, delete_account
from app.services.scraper_service import delete_account as delete_account_from_scraper
from app.services.cache import clear_cache_pattern

router = APIRouter()

@router.get("/", response_model=List[dict])
async def read_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all tracked Instagram accounts.
    """
    accounts = get_accounts(db, skip=skip, limit=limit)
    return accounts

@router.delete("/{username}", response_model=Dict)
async def delete_account_endpoint(
    username: str,
    db: Session = Depends(get_db)
):
    """
    Delete an Instagram account from tracking.
    
    This permanently deletes the account and all its historical data
    from both the scraper service and the database.
    """
    # First delete from scraper service
    scraper_result = await delete_account_from_scraper(username)
    
    if "error" in scraper_result.get("status", ""):
        raise HTTPException(
            status_code=404, 
            detail=scraper_result.get("message", f"Failed to delete {username} from scraper service")
        )
    
    # Then delete from database
    db_result = delete_account(db, username)
    if not db_result:
        raise HTTPException(
            status_code=404, 
            detail=f"Account {username} not found in database"
        )
    
    # Clear all cache entries related to this account
    clear_cache_pattern(f"*{username}*")
    
    return {
        "status": "success",
        "message": f"Account '{username}' and all associated profile data deleted successfully",
        "account": db_result
    }