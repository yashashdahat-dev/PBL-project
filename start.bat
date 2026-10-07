@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   LEO Digital Twin - Starting App...
echo ========================================
echo.

set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

:: Free up existing ports if occupied
echo Cleaning up existing instances on ports 8000, 8001, 5173...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000\> :8001\> :5173\>" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: Start the backend API server
echo [1/2] Starting Backend (Flask + WebSocket) on http://127.0.0.1:8000 ...
start "LEO Backend" cmd /k "cd /d "%ROOT_DIR%" && .venv\Scripts\python.exe backend_api.py"

:: Give backend a moment to initialize
ping 127.0.0.1 -n 4 >nul

:: Start the frontend dev server
echo [2/2] Starting Frontend (Vite) on http://localhost:5173 ...
start "LEO Frontend" cmd /k "cd /d "%ROOT_DIR%\frontend" && npm run dev -- --open"

echo.
echo Opening browser...

echo.
echo ========================================
echo   Both servers are running!
echo   Backend:  http://127.0.0.1:8000
echo   WebSocket: ws://127.0.0.1:8001
echo   Frontend: http://localhost:5173
echo   Close the terminal windows to stop.
echo ========================================
