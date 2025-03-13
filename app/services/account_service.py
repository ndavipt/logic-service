from typing import List
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