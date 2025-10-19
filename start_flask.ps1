#!/usr/bin/env pwsh
# start_flask.ps1
# Active l'environnement virtuel et lance `flask run`.

param(
    [string]$VenvPath = ".\\.venv",
    [int]$Port = 5000
)

if (-Not (Test-Path $VenvPath)) {
    Write-Host "Virtual environment not found at $VenvPath. Run .\\setup_env.ps1 first."; exit 1
}

Write-Host "Activating virtual environment..."
& "$VenvPath\\Scripts\\Activate.ps1"

Write-Host "Starting Flask development server on port $Port..."
# Use env vars from .env if present (flask will read .env automatically when using python-dotenv)
setx FLASK_RUN_PORT $Port | Out-Null
flask run --port $Port
