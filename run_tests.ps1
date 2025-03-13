# PowerShell script for running tests on Windows

# Activate virtual environment if it exists
if (Test-Path "venv") {
    .\venv\Scripts\Activate.ps1
}

# Set environment variables for testing
$env:PYTHONPATH = (Get-Location).Path
$env:ENVIRONMENT = "testing"

# Run tests with pytest
Write-Host "Running tests..." -ForegroundColor Green
pytest app/tests/