@echo off
echo ========================================
echo   LEO Digital Twin - Starting App...
echo ========================================
echo.

:: Start the backend API server
echo [1/2] Starting Backend (Flask) on http://127.0.0.1:8000 ...
start "LEO Backend" cmd /k "cd /d d:\ff && .venv\Scripts\python.exe backend_api.py"

:: Give backend a moment to initialize
ping 127.0.0.1 -n 4 >nul

:: Start the frontend dev server
echo [2/2] Starting Frontend (Vite) on http://localhost:5173 ...
start "LEO Frontend" cmd /k "cd /d d:\ff\frontend && npm run dev"

:: Wait a moment then open the browser
ping 127.0.0.1 -n 5 >nul
echo.
echo Opening browser...
start http://localhost:5173

echo.
echo ========================================
echo   Both servers are running!
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://localhost:5173
echo   Close the terminal windows to stop.
echo ========================================
