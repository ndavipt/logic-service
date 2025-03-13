# PowerShell script for setting up development environment on Windows

Write-Host "Creating virtual environment..." -ForegroundColor Green
python -m venv venv
.\venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..." -ForegroundColor Green
pip install -r requirements.txt

Write-Host "Running pydantic settings fix..." -ForegroundColor Green
python pydantic_settings_fix.py

Write-Host "Initializing database..." -ForegroundColor Green
python initialize_db.py

Write-Host "Development environment setup complete!" -ForegroundColor Green
Write-Host "To start the application, run: .\run_dev.ps1" -ForegroundColor Cyan