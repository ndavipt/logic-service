from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create database engine with error handling
try:
    # For SQLite (used in testing)
    if settings.DATABASE_URL.startswith("sqlite"):
        engine = create_engine(
            settings.DATABASE_URL, 
            connect_args={"check_same_thread": False}
        )
    else:
        # For PostgreSQL
        engine = create_engine(settings.DATABASE_URL)
    
    logger.info("Database connection established")
except Exception as e:
    logger.error(f"Database connection error: {e}")
    # Create a fallback SQLite in-memory database for development
    logger.warning("Using SQLite in-memory database as fallback")
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()