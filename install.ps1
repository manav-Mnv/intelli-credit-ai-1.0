# IntelliCredit AI ? Windows Setup Script
# Run this once to set up everything
# Usage: .\install.ps1

Write-Host "IntelliCredit AI ? Setup Script" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# --- Check Python ---
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pyVersion = python --version 2>&1
    Write-Host "  OK" -ForegroundColor Green
} catch {
    Write-Host "  Error: Python not found" -ForegroundColor Red
    exit 1
}

# --- Check Node.js ---
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node -v 2>&1
    Write-Host "  OK" -ForegroundColor Green
} catch {
    Write-Host "  Error: Node.js not found." -ForegroundColor Red
    exit 1
}

# --- Check Docker ---
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "  OK" -ForegroundColor Green
} catch {
    Write-Host "  Warning: Docker not found" -ForegroundColor Yellow
}

# --- Backend Python packages ---
Write-Host "Installing backend Python packages..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK" -ForegroundColor Green
} else {
    Write-Host "  Warning: Some packages may have failed" -ForegroundColor Yellow
}
Set-Location ..

# --- Frontend npm packages ---
Write-Host "Installing frontend npm packages..." -ForegroundColor Yellow
Set-Location frontend
npm install --silent
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK" -ForegroundColor Green
} else {
    Write-Host "  Error npm install failed" -ForegroundColor Red
}
Set-Location ..

# --- Train ML model ---
Write-Host "Training XGBoost credit risk model..." -ForegroundColor Yellow
Set-Location ml
python train_model.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK" -ForegroundColor Green
} else {
    Write-Host "  Warning: Model training failed" -ForegroundColor Yellow
}
Set-Location ..

# --- Create .env if missing ---
if (-not (Test-Path "backend\.env")) {
    Copy-Item ".env.example" "backend\.env"
    Write-Host "Created backend\.env from template." -ForegroundColor Yellow
} else {
    Write-Host "backend\.env already exists" -ForegroundColor Green
}

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Setup complete To start the system:" -ForegroundColor Green
Write-Host "  .\start.ps1" -ForegroundColor White
Write-Host "Or manually:" -ForegroundColor Gray
Write-Host "  1. docker run -d -p 6379:6379 redis" -ForegroundColor Gray
Write-Host "  2. cd backend ; uvicorn app.main:app --reload --port 8000" -ForegroundColor Gray
Write-Host "  3. cd frontend ; npm run dev" -ForegroundColor Gray
Write-Host ""
