def test_read_latest_profiles(client, sample_data):
    response = client.get("/api/v1/profiles/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    # Check that the profiles contain the expected data
    usernames = [profile["username"] for profile in data]
    assert "testuser1" in usernames
    assert "testuser2" in usernames
    
    # Check that follower counts are correct
    for profile in data:
        if profile["username"] == "testuser1":
            assert profile["follower_count"] == 1000
        elif profile["username"] == "testuser2":
            assert profile["follower_count"] == 2000