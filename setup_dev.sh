#!/bin/bash

# Create and activate virtual environment
echo "Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run pydantic settings fix
echo "Running pydantic settings fix..."
python pydantic_settings_fix.py

# Initialize database with sample data
echo "Initializing database..."
python initialize_db.py

echo "Development environment setup complete!"
echo "To start the application, run: ./run_dev.sh"