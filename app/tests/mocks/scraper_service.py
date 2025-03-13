import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Mock data for testing
MOCK_PROFILES = [
    {
        "username": "test_account",
        "follower_count": 1250,
        "profile_pic_url": "https://example.com/pic1.jpg",
        "full_name": "Test Account",
        "biography": "This is a test account",
        "checked_at": datetime.now().isoformat()
    },
    {
        "username": "comparison_account",
        "follower_count": 2150,
        "profile_pic_url": "https://example.com/pic2.jpg",
        "full_name": "Comparison Account",
        "biography": "This is a comparison account",
        "checked_at": datetime.now().isoformat()
    }
]

MOCK_ACCOUNTS = [
    {
        "username": "test_account",
        "status": "active",
        "created_at": (datetime.now() - timedelta(days=30)).isoformat()
    },
    {
        "username": "comparison_account",
        "status": "active",
        "created_at": (datetime.now() - timedelta(days=30)).isoformat()
    }
]

# Mock for the httpx client
class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP Error: {self.status_code}")

# Fixtures and patches for testing
@pytest.fixture
def mock_fetch_profiles():
    with patch("app.services.scraper_service.httpx.AsyncClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.__aenter__.return_value.get.return_value = MockResponse(MOCK_PROFILES)
        mock_client.return_value = mock_instance
        yield

@pytest.fixture
def mock_fetch_accounts():
    with patch("app.services.scraper_service.httpx.AsyncClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.__aenter__.return_value.get.return_value = MockResponse(MOCK_ACCOUNTS)
        mock_client.return_value = mock_instance
        yield

@pytest.fixture
def mock_trigger_scrape():
    with patch("app.services.scraper_service.httpx.AsyncClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.__aenter__.return_value.post.return_value = MockResponse({"status": "success", "message": "Scrape initiated"})
        mock_client.return_value = mock_instance
        yield

@pytest.fixture
def mock_add_account():
    with patch("app.services.scraper_service.httpx.AsyncClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.__aenter__.return_value.post.return_value = MockResponse({"status": "success", "username": "new_account"})
        mock_client.return_value = mock_instance
        yield