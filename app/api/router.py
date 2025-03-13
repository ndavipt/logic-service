from fastapi import APIRouter

from app.api.v1 import accounts, profiles, analytics, scraper

router = APIRouter(prefix="/api/v1")

# Include routers with default trailing slashes
router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
router.include_router(scraper.router, prefix="/scraper", tags=["scraper"])
