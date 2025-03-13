# Logic Service

## Overview
Logic Service handles calculations, caching, and API endpoints between PostgreSQL and Frontend in a microservice architecture.

## Architecture Context
- Part of microservice architecture: [Scraper-Service] → [PostgreSQL] → [Logic-Service] → [Frontend-Service]
- Logic-Service handles Instagram analytics, caching, and API endpoints

## API Endpoints
- `/api/v1/accounts/` - List all Instagram accounts
- `/api/v1/profiles/` - Get all profile data
- `/api/v1/profiles/current/{username}` - Get current follower count
- `/api/v1/profiles/history/{username}` - Get historical data
- `/api/v1/analytics/growth/{username}` - Get 12/24h growth metrics
- `/api/v1/analytics/changes/{username}` - Get follower changes
- `/api/v1/analytics/rolling-average/{username}` - Get 7-day rolling averages
- `/api/v1/analytics/compare` - Compare metrics between accounts

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run development server: `uvicorn app.main:app --reload`
