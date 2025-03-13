# PowerShell script to reset the SQLite database

# Delete the database file if it exists
if (Test-Path "instagram.db") {
    Write-Host "Removing existing database file..." -ForegroundColor Yellow
    Remove-Item "instagram.db"
}

# Run the database initialization
Write-Host "Initializing new database..." -ForegroundColor Green
python initialize_db.py

Write-Host "Database reset complete!" -ForegroundColor Green