# Real-Time Inventory Management System - Start Script
# This script starts both backend and frontend servers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Inventory Management System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "d:\model_shardha\inventory_system"

# Start Backend in new window
Write-Host "Starting Backend Server (Flask-SocketIO)..." -ForegroundColor Yellow
$backendScript = @"
Set-Location '$projectRoot\backend'
& .\venv\Scripts\Activate.ps1
Write-Host 'Backend running on http://localhost:5000' -ForegroundColor Green
python main.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start Frontend in new window
Write-Host "Starting Frontend Server (React)..." -ForegroundColor Yellow
$frontendScript = @"
Set-Location '$projectRoot\frontend'
Write-Host 'Frontend will open at http://localhost:3000' -ForegroundColor Green
npm start
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Both servers are starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000 (will open automatically)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C in each terminal to stop servers" -ForegroundColor Gray
