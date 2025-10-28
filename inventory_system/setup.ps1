# Real-Time Inventory Management System - Setup Script
# Run this in PowerShell to set up the entire project

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Real-Time Inventory Management Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to project root
$projectRoot = "d:\model_shardha\inventory_system"
Set-Location $projectRoot

# Backend Setup
Write-Host "[1/4] Setting up Backend..." -ForegroundColor Yellow
Set-Location "$projectRoot\backend"

# Create virtual environment
if (!(Test-Path "venv")) {
    Write-Host "  Creating Python virtual environment..." -ForegroundColor Gray
    python -m venv venv
}

# Activate virtual environment
Write-Host "  Activating virtual environment..." -ForegroundColor Gray
& .\venv\Scripts\Activate.ps1

# Install Python dependencies
Write-Host "  Installing Python dependencies..." -ForegroundColor Gray
pip install -r requirements.txt --quiet

Write-Host "  ✓ Backend setup complete!" -ForegroundColor Green
Write-Host ""

# Frontend Setup
Write-Host "[2/4] Setting up Frontend..." -ForegroundColor Yellow
Set-Location "$projectRoot\frontend"

# Install Node dependencies
Write-Host "  Installing Node.js dependencies (this may take a while)..." -ForegroundColor Gray
npm install --silent

Write-Host "  ✓ Frontend setup complete!" -ForegroundColor Green
Write-Host ""

# Verify setup
Write-Host "[3/4] Verifying installation..." -ForegroundColor Yellow

$backendVenv = Test-Path "$projectRoot\backend\venv"
$nodeModules = Test-Path "$projectRoot\frontend\node_modules"
$inventoryCsv = Test-Path "$projectRoot\backend\inventory.csv"

if ($backendVenv) {
    Write-Host "  ✓ Backend virtual environment created" -ForegroundColor Green
} else {
    Write-Host "  ✗ Backend virtual environment missing" -ForegroundColor Red
}

if ($nodeModules) {
    Write-Host "  ✓ Frontend node_modules installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ Frontend node_modules missing" -ForegroundColor Red
}

if ($inventoryCsv) {
    Write-Host "  ✓ Inventory CSV exists" -ForegroundColor Green
} else {
    Write-Host "  ✗ Inventory CSV missing" -ForegroundColor Red
}

Write-Host ""

# Instructions
Write-Host "[4/4] Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  How to Run the Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Terminal 1 (Backend):" -ForegroundColor Yellow
Write-Host "  cd d:\model_shardha\inventory_system\backend" -ForegroundColor Gray
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "  python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Terminal 2 (Frontend):" -ForegroundColor Yellow
Write-Host "  cd d:\model_shardha\inventory_system\frontend" -ForegroundColor Gray
Write-Host "  npm start" -ForegroundColor Gray
Write-Host ""
Write-Host "Then open: http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
