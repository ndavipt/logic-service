from sqlalchemy import inspect
from datetime import datetime, timedelta

from app.db.session import engine, SessionLocal
from app.models.account import InstagramAccount
from app.models.profile import InstagramProfile

def initialize_db():
    """
    Initialize database with tables and seed data if needed.
    This is useful for development and testing.
    """
    inspector = inspect(engine)
    
    # Check if tables already exist
    if not inspector.has_table("instagram_accounts"):
        # Create tables
        from app.db.session import Base
        Base.metadata.create_all(bind=engine)
        
        # Seed with some sample data
        seed_sample_data()
        
        print("Database initialized with sample data.")
    else:
        print("Database tables already exist.")

def seed_sample_data():
    """
    Add sample data to the database for testing and development.
    """
    db = SessionLocal()
    try:
        # Create sample accounts
        account1 = InstagramAccount(username="instagram", status="active")
        account2 = InstagramAccount(username="google", status="active")
        
        db.add(account1)
        db.add(account2)
        db.commit()
        
        # Create sample profile data with history
        now = datetime.now()
        
        # Sample data for first account
        follower_count = 500000000
        for days_ago in range(30, -1, -1):
            date_point = now - timedelta(days=days_ago)
            
            # Add some random-like growth
            if days_ago > 0:
                follower_count += 50000 + (days_ago * 1000)
            
            profile = InstagramProfile(
                account_id=account1.id,
                follower_count=follower_count,
                profile_pic_url="https://example.com/instagram.jpg",
                full_name="Instagram",
                biography="Instagram official account",
                checked_at=date_point
            )
            db.add(profile)
        
        # Sample data for second account
        follower_count = 30000000
        for days_ago in range(30, -1, -1):
            date_point = now - timedelta(days=days_ago)
            
            # Different growth pattern
            if days_ago > 0:
                follower_count += 20000 + (days_ago * 500)
            
            profile = InstagramProfile(
                account_id=account2.id,
                follower_count=follower_count,
                profile_pic_url="https://example.com/google.jpg",
                full_name="Google",
                biography="Google official account",
                checked_at=date_point
            )
            db.add(profile)
        
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    initialize_db()