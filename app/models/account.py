from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db.session import Base

class InstagramAccount(Base):
    __tablename__ = "instagram_accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=func.now())
    
    # Relationship with profiles
    profiles = relationship("InstagramProfile", back_populates="account")
    
    def __repr__(self):
        return f"<InstagramAccount(username='{self.username}')>"