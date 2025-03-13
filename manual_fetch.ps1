# PowerShell script to manually fetch data from the Scraper Service

# Activate virtual environment if it exists
if (Test-Path "venv") {
    .\venv\Scripts\Activate.ps1
}

# Get Scraper Service URL from .env or prompt for it
$scraperUrl = $null
if (Test-Path ".env") {
    $envContent = Get-Content ".env"
    foreach ($line in $envContent) {
        if ($line -match "SCRAPER_SERVICE_URL=(.+)") {
            $scraperUrl = $matches[1]
            break
        }
    }
}

if (-not $scraperUrl) {
    $scraperUrl = Read-Host -Prompt "Enter the URL of your Scraper Service (e.g., https://scraper-service-907s.onrender.com)"
}

# Set environment variable for the script
$env:SCRAPER_SERVICE_URL = $scraperUrl

# Run the Python script
Write-Host "Running data fetch script for $scraperUrl..." -ForegroundColor Green
python fetch_data.py

Write-Host "Data fetch complete. Check the output above for details." -ForegroundColor Green
Write-Host "You can now run the Logic Service to access the imported data:" -ForegroundColor Cyan
Write-Host ".\run_dev.ps1" -ForegroundColor Cyan