# IntelliCredit AI — Windows Setup Script
# Run this once to set up everything
# Usage: .\install.ps1

Write-Host "`n🏦 IntelliCredit AI — Setup Script" -ForegroundColor Cyan
Write-Host "====================================`n" -ForegroundColor Cyan

# --- Check Python ---
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pyVersion = python --version 2>&1
    Write-Host "  ✅ $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python not found. Install from https://python.org" -ForegroundColor Red
    exit 1
}

# --- Check Node.js ---
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node -v 2>&1
    Write-Host "  ✅ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Node.js not found. Install from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# --- Check Docker ---
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "  ✅ $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Docker not found. Install from https://docker.com (needed for Redis/Neo4j)" -ForegroundColor Yellow
}

# --- Backend Python packages ---
Write-Host "`nInstalling backend Python packages..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Python packages installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Some packages may have failed — check output above" -ForegroundColor Yellow
}
Set-Location ..

# --- Frontend npm packages ---
Write-Host "`nInstalling frontend npm packages..." -ForegroundColor Yellow
Set-Location frontend
npm install --silent
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ npm packages installed" -ForegroundColor Green
} else {
    Write-Host "  ❌ npm install failed" -ForegroundColor Red
}
Set-Location ..

# --- Train ML model ---
Write-Host "`nTraining XGBoost credit risk model..." -ForegroundColor Yellow
Set-Location ml
python train_model.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Model trained and saved" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Model training failed — system will use heuristic fallback" -ForegroundColor Yellow
}
Set-Location ..

# --- Create .env if missing ---
if (-not (Test-Path "backend\.env")) {
    Copy-Item ".env.example" "backend\.env"
    Write-Host "`n⚠️  Created backend\.env from template." -ForegroundColor Yellow
    Write-Host "   Please edit backend\.env and add your Supabase credentials!" -ForegroundColor Yellow
} else {
    Write-Host "`n  ✅ backend\.env already exists" -ForegroundColor Green
}

Write-Host "`n====================================`n" -ForegroundColor Cyan
Write-Host "✅ Setup complete! To start the system:" -ForegroundColor Green
Write-Host ""
Write-Host "  .\start.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Or manually:" -ForegroundColor Gray
Write-Host "  1. docker run -d -p 6379:6379 redis" -ForegroundColor Gray
Write-Host "  2. cd backend && uvicorn app.main:app --reload --port 8000" -ForegroundColor Gray
Write-Host "  3. cd frontend && npm run dev" -ForegroundColor Gray
Write-Host ""
