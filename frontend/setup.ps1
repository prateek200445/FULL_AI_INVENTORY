# Quick Setup Script for Frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI Inventory Frontend Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to frontend directory
Set-Location "d:\model_shardha\frontend"

# Install dependencies
Write-Host "[1/3] Installing dependencies..." -ForegroundColor Yellow
npm install

Write-Host ""
Write-Host "[2/3] Verifying installation..." -ForegroundColor Yellow

# Check if node_modules exists
if (Test-Path "node_modules") {
    Write-Host "  ✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ Installation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[3/3] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  How to Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start Backend APIs:" -ForegroundColor Yellow
Write-Host "   Terminal 1: cd d:\model_shardha" -ForegroundColor Gray
Write-Host "               uvicorn new_full_api:app --reload --port 8002" -ForegroundColor Gray
Write-Host ""
Write-Host "   Terminal 2: cd d:\model_shardha" -ForegroundColor Gray
Write-Host "               uvicorn main2:app --reload --port 8003" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start Frontend:" -ForegroundColor Yellow
Write-Host "   Terminal 3: cd d:\model_shardha\frontend" -ForegroundColor Gray
Write-Host "               npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Open Browser:" -ForegroundColor Yellow
Write-Host "   http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
