import asyncio
import httpx
import json
import sys
import os
import time
import sqlite3
from datetime import datetime

# Set environment variables
os.environ["SCRAPER_SERVICE_URL"] = "https://scraper-service-907s.onrender.com"
os.environ["USE_MOCK_SCRAPER"] = "false"

async def fetch_data():
    print(f"Fetching data from Scraper Service at {os.environ['SCRAPER_SERVICE_URL']}")
    scraper_url = os.environ["SCRAPER_SERVICE_URL"]
    
    # Connect to SQLite database
    print("Connecting to SQLite database...")
    db_path = "./instagram.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    print("Creating tables if they don't exist...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS instagram_accounts (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS instagram_profiles (
        id INTEGER PRIMARY KEY,
        account_id INTEGER,
        follower_count INTEGER,
        profile_pic_url TEXT,
        full_name TEXT,
        biography TEXT,
        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (account_id) REFERENCES instagram_accounts(id)
    )
    ''')
    
    conn.commit()
    
    try:
        # Fetch accounts
        print(f"Fetching accounts from {scraper_url}/accounts")
        async with httpx.AsyncClient(timeout=30.0) as client:
            accounts_response = await client.get(f"{scraper_url}/accounts")
            accounts_response.raise_for_status()
            
            # Try to parse the JSON response
            try:
                accounts_data = accounts_response.json()
                # Handle different response formats
                if isinstance(accounts_data, dict) and "accounts" in accounts_data:
                    accounts_data = accounts_data["accounts"]
                    
                print(f"Fetched {len(accounts_data) if isinstance(accounts_data, list) else 'unknown'} accounts")
                
                # Process accounts
                if isinstance(accounts_data, list):
                    for account in accounts_data:
                        username = None
                        if isinstance(account, str):
                            username = account
                        elif isinstance(account, dict) and "username" in account:
                            username = account["username"]
                        
                        if username:
                            # Check if account exists
                            cursor.execute("SELECT id FROM instagram_accounts WHERE username = ?", (username,))
                            existing = cursor.fetchone()
                            
                            if not existing:
                                print(f"Adding account: {username}")
                                cursor.execute(
                                    "INSERT INTO instagram_accounts (username, status) VALUES (?, ?)",
                                    (username, "active")
                                )
                            else:
                                print(f"Account already exists: {username}")
                else:
                    print(f"Unexpected accounts data type: {type(accounts_data)}")
            except Exception as e:
                print(f"Error processing accounts: {e}")
                print(f"Raw response: {accounts_response.text[:500]}")
        
        # Commit account changes
        conn.commit()
        
        # Fetch profiles
        print(f"Fetching profiles from {scraper_url}/profiles")
        async with httpx.AsyncClient(timeout=30.0) as client:
            profiles_response = await client.get(f"{scraper_url}/profiles")
            profiles_response.raise_for_status()
            
            # Try to parse the JSON response
            try:
                profiles_data = profiles_response.json()
                # Handle different response formats
                if isinstance(profiles_data, dict) and "profiles" in profiles_data:
                    profiles_data = profiles_data["profiles"]
                    
                print(f"Fetched {len(profiles_data) if isinstance(profiles_data, list) else 'unknown'} profiles")
                
                # Process profiles
                if isinstance(profiles_data, list):
                    for profile in profiles_data:
                        # Extract profile data based on various possible formats
                        username = None
                        follower_count = 0
                        profile_pic_url = ""
                        full_name = ""
                        biography = ""
                        
                        if isinstance(profile, dict):
                            # Get username
                            if "username" in profile:
                                username = profile["username"]
                            
                            # Get follower count
                            if "follower_count" in profile:
                                follower_count = profile["follower_count"]
                            elif "followers" in profile:
                                follower_count = profile["followers"]
                            
                            # Get profile pic
                            if "profile_pic_url" in profile:
                                profile_pic_url = profile["profile_pic_url"]
                            elif "profile_picture" in profile:
                                profile_pic_url = profile["profile_picture"]
                            
                            # Get full name
                            if "full_name" in profile:
                                full_name = profile["full_name"]
                            elif "name" in profile:
                                full_name = profile["name"]
                            
                            # Get biography
                            if "biography" in profile:
                                biography = profile["biography"]
                            elif "bio" in profile:
                                biography = profile["bio"]
                        
                        if username:
                            # Get account ID
                            cursor.execute("SELECT id FROM instagram_accounts WHERE username = ?", (username,))
                            account_row = cursor.fetchone()
                            
                            if account_row:
                                account_id = account_row[0]
                                
                                # Add profile data
                                print(f"Adding profile for: {username}")
                                cursor.execute(
                                    "INSERT INTO instagram_profiles (account_id, follower_count, profile_pic_url, full_name, biography, checked_at) "
                                    "VALUES (?, ?, ?, ?, ?, ?)",
                                    (account_id, follower_count, profile_pic_url, full_name, biography, datetime.now().isoformat())
                                )
                            else:
                                print(f"Account not found for profile: {username}")
                else:
                    print(f"Unexpected profiles data type: {type(profiles_data)}")
            except Exception as e:
                print(f"Error processing profiles: {e}")
                print(f"Raw response: {profiles_response.text[:500]}")
        
        # Commit profile changes
        conn.commit()
        print("Data import complete!")
        
    except Exception as e:
        print(f"Error during data fetch: {e}")
        conn.rollback()
    finally:
        # Close database connection
        conn.close()

# Run the data fetch
asyncio.run(fetch_data())

# Run the FastAPI server
print("Starting the Logic Service...")
print("Press Ctrl+C to exit")
time.sleep(1)

# Use subprocess to run the server
import subprocess
subprocess.run(["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
