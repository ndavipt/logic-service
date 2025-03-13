import asyncio
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys
import os
import json

# Add root directory to path so we can import app modules
sys.path.insert(0, os.getcwd())

from app.models.account import InstagramAccount
from app.models.profile import InstagramProfile
from app.db.session import Base

async def fetch_and_store_data():
    print("Fetching data from Scraper Service...")
    scraper_url = os.getenv("SCRAPER_SERVICE_URL")
    
    if not scraper_url:
        scraper_url = input("Enter the Scraper Service URL: ")
    
    # Create database engine and tables
    engine = create_engine("sqlite:///./instagram.db")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Fetch accounts
        print(f"Fetching accounts from {scraper_url}/accounts")
        async with httpx.AsyncClient(timeout=30.0) as client:
            accounts_response = await client.get(f"{scraper_url}/accounts")
            accounts_response.raise_for_status()
            accounts_raw = accounts_response.text
            print(f"Raw accounts response: {accounts_raw[:200]}...")  # Print first 200 chars
            
            # Try to parse JSON
            try:
                accounts_data = accounts_response.json()
                # If it's not a list, it might be nested
                if not isinstance(accounts_data, list):
                    if isinstance(accounts_data, dict) and "accounts" in accounts_data:
                        accounts_data = accounts_data["accounts"]
                    else:
                        print(f"Unexpected accounts data format: {type(accounts_data)}")
                        accounts_data = []
            except Exception as e:
                print(f"Error parsing accounts JSON: {e}")
                accounts_data = []
            
        print(f"Fetched {len(accounts_data)} accounts")
        
        # Fetch profiles
        print(f"Fetching profiles from {scraper_url}/profiles")
        async with httpx.AsyncClient(timeout=30.0) as client:
            profiles_response = await client.get(f"{scraper_url}/profiles")
            profiles_response.raise_for_status()
            profiles_raw = profiles_response.text
            print(f"Raw profiles response: {profiles_raw[:200]}...")  # Print first 200 chars
            
            # Try to parse JSON
            try:
                profiles_data = profiles_response.json()
                # If it's not a list, it might be nested
                if not isinstance(profiles_data, list):
                    if isinstance(profiles_data, dict) and "profiles" in profiles_data:
                        profiles_data = profiles_data["profiles"]
                    else:
                        print(f"Unexpected profiles data format: {type(profiles_data)}")
                        profiles_data = []
            except Exception as e:
                print(f"Error parsing profiles JSON: {e}")
                profiles_data = []
            
        print(f"Fetched {len(profiles_data)} profiles")
        
        # Debug: Print the first account and profile
        if accounts_data:
            print(f"First account sample: {json.dumps(accounts_data[0], indent=2)}")
        if profiles_data:
            print(f"First profile sample: {json.dumps(profiles_data[0], indent=2)}")
        
        # Store accounts
        for account_data in accounts_data:
            try:
                if isinstance(account_data, str):
                    # Handle case where account is just a string (username)
                    username = account_data
                    status = "active"
                    created_at = datetime.now()
                else:
                    # Handle dictionary format
                    username = account_data.get("username", "unknown")
                    status = account_data.get("status", "active")
                    created_at_str = account_data.get("created_at")
                    if created_at_str:
                        try:
                            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                        except Exception:
                            created_at = datetime.now()
                    else:
                        created_at = datetime.now()
                
                # Check if account already exists
                existing = db.query(InstagramAccount).filter_by(username=username).first()
                if not existing:
                    account = InstagramAccount(
                        username=username,
                        status=status,
                        created_at=created_at
                    )
                    db.add(account)
                    print(f"Added account: {username}")
                else:
                    print(f"Account already exists: {username}")
            except Exception as e:
                print(f"Error processing account: {e}, data: {account_data}")
        
        # Commit to get account IDs
        db.commit()
        
        # Store profiles
        for profile_data in profiles_data:
            try:
                if isinstance(profile_data, str):
                    # Skip if profile is just a string
                    print(f"Skipping string profile: {profile_data}")
                    continue
                
                # Get username from profile data
                if "username" in profile_data:
                    username = profile_data["username"]
                elif "account" in profile_data and isinstance(profile_data["account"], dict):
                    username = profile_data["account"].get("username", "unknown")
                elif "account" in profile_data and isinstance(profile_data["account"], str):
                    username = profile_data["account"]
                else:
                    print(f"Could not determine username for profile: {profile_data}")
                    continue
                
                # Get follower count
                follower_count = 0
                if "follower_count" in profile_data:
                    follower_count = profile_data["follower_count"]
                elif "followers" in profile_data:
                    follower_count = profile_data["followers"]
                
                # Get profile pic URL
                profile_pic_url = ""
                if "profile_pic_url" in profile_data:
                    profile_pic_url = profile_data["profile_pic_url"]
                elif "profile_picture" in profile_data:
                    profile_pic_url = profile_data["profile_picture"]
                
                # Get full name
                full_name = ""
                if "full_name" in profile_data:
                    full_name = profile_data["full_name"]
                elif "name" in profile_data:
                    full_name = profile_data["name"]
                
                # Get biography
                biography = ""
                if "biography" in profile_data:
                    biography = profile_data["biography"]
                elif "bio" in profile_data:
                    biography = profile_data["bio"]
                
                # Get checked_at time
                checked_at = datetime.now()
                if "checked_at" in profile_data:
                    try:
                        checked_at_str = profile_data["checked_at"]
                        checked_at = datetime.fromisoformat(checked_at_str.replace("Z", "+00:00"))
                    except Exception:
                        pass
                elif "timestamp" in profile_data:
                    try:
                        timestamp_str = profile_data["timestamp"]
                        checked_at = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    except Exception:
                        pass
                
                # Get account ID
                account = db.query(InstagramAccount).filter_by(username=username).first()
                if account:
                    # Create profile
                    profile = InstagramProfile(
                        account_id=account.id,
                        follower_count=follower_count,
                        profile_pic_url=profile_pic_url,
                        full_name=full_name,
                        biography=biography,
                        checked_at=checked_at
                    )
                    db.add(profile)
                    print(f"Added profile for: {username}")
                else:
                    print(f"Account not found for profile: {username}")
            except Exception as e:
                print(f"Error processing profile: {e}, data: {profile_data}")
        
        # Final commit
        db.commit()
        print("Data import complete!")
        
    except Exception as e:
        print(f"Error fetching or storing data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(fetch_and_store_data())