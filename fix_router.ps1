# PowerShell script to fix the router issue

# Activate virtual environment if it exists
if (Test-Path "venv") {
    .\venv\Scripts\Activate.ps1
}

# Create a simpler router without the complex endpoint_kwargs logic
$simpleRouter = @"
from fastapi import APIRouter

from app.api.v1 import accounts, profiles, analytics, scraper

router = APIRouter(prefix="/api/v1")

# Include routers with default trailing slashes
router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
router.include_router(scraper.router, prefix="/scraper", tags=["scraper"])
"@

# Write the simpler router
$simpleRouter | Out-File -FilePath "app/api/router.py" -Encoding utf8

# Create a FastAPI main file without redirect_slashes
$mainFastAPI = @"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.router import router as api_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Logic Service API for Instagram data analytics",
    version="0.1.0",
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Logic Service API",
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": settings.PROJECT_NAME
    }
"@

# Write the main FastAPI file
$mainFastAPI | Out-File -FilePath "app/main.py" -Encoding utf8

Write-Host "Fixed router issues. You can now restart the Logic Service." -ForegroundColor Green
Write-Host "Run: .\run_with_real_data.ps1" -ForegroundColor Cyan