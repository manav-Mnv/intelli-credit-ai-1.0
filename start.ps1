# IntelliCredit AI — Quick Start Script
# Usage: .\start.ps1

Write-Host "`n🏦 Starting IntelliCredit AI..." -ForegroundColor Cyan

# Start Redis
Write-Host "`n🔴 Starting Redis..." -ForegroundColor Yellow
$redisRunning = docker ps --filter "ancestor=redis" --format "{{.ID}}" 2>&1
if (-not $redisRunning) {
    docker run -d -p 6379:6379 --name intellicredit_redis redis:7-alpine
    Write-Host "  ✅ Redis started on port 6379" -ForegroundColor Green
} else {
    Write-Host "  ✅ Redis already running" -ForegroundColor Green
}

# Start Neo4j
Write-Host "`n🔵 Starting Neo4j..." -ForegroundColor Yellow
$neo4jRunning = docker ps --filter "ancestor=neo4j" --format "{{.ID}}" 2>&1
if (-not $neo4jRunning) {
    docker run -d -p 7474:7474 -p 7687:7687 --name intellicredit_neo4j `
        -e NEO4J_AUTH=neo4j/password `
        neo4j:5-community
    Write-Host "  ✅ Neo4j started → http://localhost:7474" -ForegroundColor Green
} else {
    Write-Host "  ✅ Neo4j already running" -ForegroundColor Green
}

Write-Host "`n⚡ Starting Backend (FastAPI)..." -ForegroundColor Yellow
Write-Host "   Open a NEW terminal and run:" -ForegroundColor Gray
Write-Host "   cd backend && uvicorn app.main:app --reload --port 8000`n" -ForegroundColor White

Write-Host "⚡ Starting Frontend (Next.js)..." -ForegroundColor Yellow
Write-Host "   Open ANOTHER terminal and run:" -ForegroundColor Gray
Write-Host "   cd frontend && npm run dev`n" -ForegroundColor White

Write-Host "====================================`n" -ForegroundColor Cyan
Write-Host "🌐 Dashboard:  http://localhost:3000" -ForegroundColor Green
Write-Host "📚 API Docs:   http://localhost:8000/docs" -ForegroundColor Green
Write-Host "🗄️  Neo4j:      http://localhost:7474" -ForegroundColor Green
Write-Host ""
