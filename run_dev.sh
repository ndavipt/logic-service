#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set environment variables for development
export PYTHONPATH=$(pwd)
export ENVIRONMENT=development

# Run the service with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000