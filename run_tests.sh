#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set environment variables for testing
export PYTHONPATH=$(pwd)
export ENVIRONMENT=testing

# Run tests with pytest
pytest app/tests/