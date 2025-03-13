from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.account import InstagramAccount
from app.services.account_service import get_accounts

router = APIRouter()

@router.get("/", response_model=List[dict])
async def read_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all tracked Instagram accounts.
    """
    accounts = get_accounts(db, skip=skip, limit=limit)
    return accounts