@echo off
echo ========================================
echo    AI Document Agent Servers
echo ========================================
echo.
echo Starting AI Document Agent servers...
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "python simple_server.py"

echo.
echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm start -- --port 3001"

echo.
echo Servers are starting up!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3001
echo.
echo Press any key to open the demo in your browser...
pause >nul
start http://localhost:3001
