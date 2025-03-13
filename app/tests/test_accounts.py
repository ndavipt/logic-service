def test_read_accounts(client, sample_data):
    response = client.get("/api/v1/accounts/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    usernames = [account["username"] for account in data]
    assert "testuser1" in usernames
    assert "testuser2" in usernames