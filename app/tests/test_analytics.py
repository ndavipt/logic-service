def test_growth_metrics(client, analytics_data):
    """
    Test the growth metrics endpoint
    """
    response = client.get("/api/v1/analytics/growth/test_account")
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == "test_account"
    assert "net_growth" in data
    assert "percentage_growth" in data
    assert "average_daily_growth" in data
    assert "change_12h" in data
    assert "change_24h" in data
    assert "rolling_avg_7day" in data
    
    # Check that we have data for changes between scrapes
    assert "changes_between_scrapes" in data
    assert len(data["changes_between_scrapes"]) > 0
    
    # Check 12-hour change
    assert "change" in data["change_12h"]
    assert "percentage" in data["change_12h"]
    assert "hours_actual" in data["change_12h"]
    
    # Check rolling average data
    assert "average_change" in data["rolling_avg_7day"]
    assert "days_covered" in data["rolling_avg_7day"]

def test_follower_changes(client, analytics_data):
    """
    Test the follower changes endpoint
    """
    response = client.get("/api/v1/analytics/changes/test_account")
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == "test_account"
    assert "change_12h" in data
    assert "change_24h" in data
    assert "changes_between_scrapes" in data
    
    # Verify that data is structured correctly
    assert len(data["changes_between_scrapes"]) > 0
    first_change = data["changes_between_scrapes"][0]
    assert "previous_count" in first_change
    assert "current_count" in first_change
    assert "change" in first_change
    assert "hours_between" in first_change

def test_rolling_average(client, analytics_data):
    """
    Test the rolling average endpoint
    """
    response = client.get("/api/v1/analytics/rolling-average/test_account")
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == "test_account"
    assert "rolling_avg_7day" in data
    
    avg_data = data["rolling_avg_7day"]
    assert "average_change" in avg_data
    assert "days_covered" in avg_data
    assert "total_change" in avg_data

def test_compare_accounts(client, analytics_data):
    """
    Test the account comparison endpoint
    """
    response = client.get("/api/v1/analytics/compare?usernames=test_account&usernames=comparison_account")
    assert response.status_code == 200
    
    data = response.json()
    assert "accounts" in data
    assert "test_account" in data["accounts"]
    assert "comparison_account" in data["accounts"]
    
    # Verify that comparison includes rankings
    test_account = data["accounts"]["test_account"]
    assert "rankings" in test_account
    assert "net_growth" in test_account["rankings"]
    assert "percentage_growth" in test_account["rankings"]
    assert "daily_growth" in test_account["rankings"]