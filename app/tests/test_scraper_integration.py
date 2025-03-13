import pytest
from app.tests.mocks.scraper_service import (
    mock_fetch_profiles, mock_fetch_accounts, 
    mock_trigger_scrape, mock_add_account
)

def test_get_latest_profiles(client, mock_fetch_profiles):
    response = client.get("/api/v1/scraper/latest")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    usernames = [profile["username"] for profile in data]
    assert "test_account" in usernames
    assert "comparison_account" in usernames

def test_get_accounts(client, mock_fetch_accounts):
    response = client.get("/api/v1/scraper/accounts")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    usernames = [account["username"] for account in data]
    assert "test_account" in usernames
    assert "comparison_account" in usernames

def test_trigger_scrape(client, mock_trigger_scrape):
    response = client.post("/api/v1/scraper/trigger")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data

def test_add_account(client, mock_add_account):
    response = client.post("/api/v1/scraper/add-account?username=new_account")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert data["username"] == "new_account"