# PowerShell script to run the Logic Service with real data

# Activate virtual environment if it exists
if (Test-Path "venv") {
    .\venv\Scripts\Activate.ps1
}

# Run the Python script
Write-Host "Fetching data from Scraper Service and starting Logic Service..." -ForegroundColor Green
python run_with_real_data.py
