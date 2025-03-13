# PowerShell script to fix settings issue

# Activate virtual environment if it exists
if (Test-Path "venv") {
    .\venv\Scripts\Activate.ps1
}

# Fix the settings module issue
Write-Host "Installing pydantic-settings..." -ForegroundColor Green
pip install pydantic-settings

Write-Host "Settings fixed!" -ForegroundColor Green