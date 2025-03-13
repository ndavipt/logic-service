# Script to initialize the database with sample data
from app.core.utils.db_init import initialize_db

if __name__ == "__main__":
    print("Initializing database...")
    initialize_db()
    print("Database initialization complete.")