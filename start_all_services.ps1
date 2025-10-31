# Complete Startup Script for All Services
# Runs Forecast API (8002), Tariff API (8003), and Frontend (5173)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting AI Inventory System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "d:\model_shardha"

# Start Forecast API (Port 8002)
Write-Host "Starting Forecast API (Port 8002)..." -ForegroundColor Yellow
$forecastScript = @"
Set-Location '$projectRoot'
Write-Host 'Forecast & Retrain API running on http://localhost:8002' -ForegroundColor Green
Write-Host 'Endpoints: /forecast, /retrain, /model/status, /plot' -ForegroundColor Gray
Write-Host ''
uvicorn new_full_api:app --reload --port 8002
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $forecastScript

Start-Sleep -Seconds 2

# Start Tariff API (Port 8003)
Write-Host "Starting Tariff Analyzer API (Port 8003)..." -ForegroundColor Yellow
$tariffScript = @"
Set-Location '$projectRoot'
Write-Host 'Tariff Analyzer API running on http://localhost:8003' -ForegroundColor Green
Write-Host 'Endpoints: /analyze-tariff, /health' -ForegroundColor Gray
Write-Host ''
uvicorn main2:app --reload --port 8003
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $tariffScript

Start-Sleep -Seconds 2

# Start Frontend (Port 5173)
Write-Host "Starting Frontend (Port 5173)..." -ForegroundColor Yellow
$frontendScript = @"
Set-Location '$projectRoot\frontend'
Write-Host 'Frontend running on http://localhost:5173' -ForegroundColor Green
Write-Host 'Opening browser in 5 seconds...' -ForegroundColor Gray
Write-Host ''
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

# Wait and open browser
Start-Sleep -Seconds 5
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  All Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Forecast API:  http://localhost:8002" -ForegroundColor Yellow
Write-Host "Tariff API:    http://localhost:8003" -ForegroundColor Yellow
Write-Host "Frontend:      http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "API Docs:" -ForegroundColor Cyan
Write-Host "  Forecast: http://localhost:8002/docs" -ForegroundColor Gray
Write-Host "  Tariff:   http://localhost:8003/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C in each terminal to stop services" -ForegroundColor Gray
Write-Host ""
