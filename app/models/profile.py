from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.session import Base

class InstagramProfile(Base):
    __tablename__ = "instagram_profiles"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("instagram_accounts.id"))
    follower_count = Column(Integer)
    profile_pic_url = Column(Text)
    full_name = Column(String)
    biography = Column(Text)
    checked_at = Column(DateTime, default=func.now())
    
    # Relationship with account
    account = relationship("InstagramAccount", back_populates="profiles")
    
    def __repr__(self):
        return f"<InstagramProfile(account_id={self.account_id}, followers={self.follower_count})>"