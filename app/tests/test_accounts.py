def test_read_accounts(client, sample_data):
    response = client.get("/api/v1/accounts/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    usernames = [account["username"] for account in data]
    assert "testuser1" in usernames
    assert "testuser2" in usernames
    
def test_delete_account(client, sample_data, monkeypatch):
    # Mock the scraper service delete_account function
    async def mock_delete_account(username):
        return {"message": f"Account '{username}' and all associated profile data deleted successfully"}
    
    # Apply the monkeypatch
    import app.api.v1.accounts
    monkeypatch.setattr(app.api.v1.accounts, "delete_account_from_scraper", mock_delete_account)
    
    # First check that the account exists
    response = client.get("/api/v1/accounts/")
    assert response.status_code == 200
    initial_count = len(response.json())
    assert any(account["username"] == "testuser1" for account in response.json())
    
    # Delete the account
    response = client.delete("/api/v1/accounts/testuser1")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "testuser1" in data["message"]
    assert data["account"]["username"] == "testuser1"
    
    # Verify account was deleted
    response = client.get("/api/v1/accounts/")
    assert response.status_code == 200
    assert len(response.json()) == initial_count - 1
    assert not any(account["username"] == "testuser1" for account in response.json())
    
def test_delete_nonexistent_account(client, sample_data, monkeypatch):
    # Mock the scraper service delete_account function to return error
    async def mock_delete_account(username):
        return {"status": "error", "message": f"Account '{username}' not found"}
    
    # Apply the monkeypatch
    import app.api.v1.accounts
    monkeypatch.setattr(app.api.v1.accounts, "delete_account_from_scraper", mock_delete_account)
    
    # Try to delete non-existent account
    response = client.delete("/api/v1/accounts/nonexistent_user")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]