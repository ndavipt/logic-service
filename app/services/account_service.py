from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.models.account import InstagramAccount

def get_accounts(db: Session, skip: int = 0, limit: int = 100) -> List[dict]:
    """
    Retrieve all tracked Instagram accounts.
    """
    db_accounts = db.query(InstagramAccount).offset(skip).limit(limit).all()
    
    return [
        {
            "id": account.id,
            "username": account.username,
            "status": account.status,
            "created_at": account.created_at
        }
        for account in db_accounts
    ]

def delete_account(db: Session, username: str) -> Optional[Dict]:
    """
    Delete an Instagram account and all associated profile data from the database.
    
    Args:
        db: Database session
        username: Instagram username to delete
        
    Returns:
        Dict with account details or None if account not found
    """
    db_account = db.query(InstagramAccount).filter(InstagramAccount.username == username).first()
    if not db_account:
        return None
    
    # Store account data before deletion for return value
    account_data = {
        "id": db_account.id,
        "username": db_account.username,
        "status": db_account.status,
        "created_at": db_account.created_at
    }
    
    # Delete the account (this will cascade delete profiles due to relationship)
    db.delete(db_account)
    db.commit()
    
    return account_data