﻿from fastapi import FastAPI
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
