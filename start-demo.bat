@echo off
echo ========================================
echo    AI Document Agent Demo Setup
echo ========================================
echo.
echo Starting AI Document Agent demo environment...
echo.

echo Installing Python dependencies...
cd backend
python -m pip install fastapi uvicorn pydantic python-multipart python-dotenv --quiet
if %errorlevel% neq 0 (
    echo Python dependencies failed to install
    pause
    exit /b 1
)

echo Starting backend server...
start "Backend Server" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Installing frontend dependencies...
cd ..\frontend
npm install --legacy-peer-deps --silent
if %errorlevel% neq 0 (
    echo Frontend dependencies failed to install
    pause
    exit /b 1
)

echo Starting frontend server...
start "Frontend Server" cmd /k "npm start -- --port 3001"

echo.
echo Demo is starting up!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3001
echo.
echo Press any key to open the demo in your browser...
pause >nul
start http://localhost:3001
