# PowerShell script for running the development server on Windows

# Activate virtual environment if it exists
if (Test-Path "venv") {
    .\venv\Scripts\Activate.ps1
}

# Set environment variables for development
$env:PYTHONPATH = (Get-Location).Path
$env:ENVIRONMENT = "development"

# Run the service with auto-reload
Write-Host "Starting FastAPI development server..." -ForegroundColor Green
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000