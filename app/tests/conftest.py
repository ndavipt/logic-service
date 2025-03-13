import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.models.account import InstagramAccount
from app.models.profile import InstagramProfile
from app.tests.fixtures.test_data import create_test_data

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for a test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    # Override the get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()

@pytest.fixture
def sample_data(db_session):
    # Create test data
    account1 = InstagramAccount(username="testuser1", status="active")
    account2 = InstagramAccount(username="testuser2", status="active")
    
    db_session.add(account1)
    db_session.add(account2)
    db_session.commit()
    
    profile1 = InstagramProfile(
        account_id=account1.id,
        follower_count=1000,
        profile_pic_url="https://example.com/pic1.jpg",
        full_name="Test User 1",
        biography="This is a test user"
    )
    
    profile2 = InstagramProfile(
        account_id=account2.id,
        follower_count=2000,
        profile_pic_url="https://example.com/pic2.jpg",
        full_name="Test User 2",
        biography="This is another test user"
    )
    
    db_session.add(profile1)
    db_session.add(profile2)
    db_session.commit()
    
    return {"account1": account1, "account2": account2}

@pytest.fixture
def analytics_data(db_session):
    """
    Create a more comprehensive dataset for testing analytics functions
    """
    return create_test_data(db_session)