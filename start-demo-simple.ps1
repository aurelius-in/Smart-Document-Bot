Write-Host "Starting Smart Document Bot Demo (Simple Version)..." -ForegroundColor Green
Write-Host ""

# Get the project root directory
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Project root: $projectRoot" -ForegroundColor Yellow

# Install only the most basic Python dependencies
Write-Host "Installing basic Python dependencies..." -ForegroundColor Cyan
Set-Location "$projectRoot\backend"
python -m pip install fastapi uvicorn --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python dependencies failed to install" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

# Start backend server
Write-Host "Starting backend server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\backend'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
Set-Location "$projectRoot\frontend"
npm install --legacy-peer-deps --silent
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend dependencies failed to install" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

# Start frontend server
Write-Host "Starting frontend server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\frontend'; npm start -- --port 3001" -WindowStyle Normal

Write-Host ""
Write-Host "Demo is starting up!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3001" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to open the demo in your browser..." -ForegroundColor Cyan
Read-Host

# Open browser
Start-Process "http://localhost:3001"
