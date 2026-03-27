@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM Helix-Zero V8 Production Startup Script (Windows)
REM ═══════════════════════════════════════════════════════════════════════════
REM This script starts all three services in separate processes for local testing
REM For production, use Docker Compose or Systemd services

SETLOCAL ENABLEDELAYEDEXPANSION

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║     HELIX-ZERO V8 - Multi-Service Startup                         ║
echo ║     Consolidated Production Build                                 ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.9+
    exit /b 1
)

REM ═══════════════════════════════════════════════════════════════════════════
REM Kill Any Existing Processes on Required Ports
REM ═══════════════════════════════════════════════════════════════════════════
echo [1/6] Cleaning up existing processes on ports 5000, 5001, 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000 ^| findstr LISTEN') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5001 ^| findstr LISTEN') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 ^| findstr LISTEN') do (
    taskkill /F /PID %%a 2>nul
)
echo [✓] Port cleanup complete

REM ═══════════════════════════════════════════════════════════════════════════
REM Launch Web App (Port 5000)
REM ═══════════════════════════════════════════════════════════════════════════
echo.
echo [2/6] Starting Main Web App on http://127.0.0.1:5000...
cd web_app
start "Helix-Zero Web App" cmd /k "python app.py"
cd ..
timeout /t 3 /nobreak

REM ═══════════════════════════════════════════════════════════════════════════
REM Launch CMS Service (Port 5001)
REM ═══════════════════════════════════════════════════════════════════════════
echo [3/6] Starting CMS Service on http://127.0.0.1:5001...
cd cms_service
start "Helix-Zero CMS Service" cmd /k "python app.py"
cd ..
timeout /t 3 /nobreak

REM ═══════════════════════════════════════════════════════════════════════════
REM Launch FastAPI Backend (Port 8000)
REM ═══════════════════════════════════════════════════════════════════════════
echo [4/6] Starting FastAPI Backend on http://127.0.0.1:8000...
cd backend
start "Helix-Zero DL Backend" cmd /k "python main.py"
cd ..
timeout /t 2 /nobreak

REM ═══════════════════════════════════════════════════════════════════════════
REM Verify Services
REM ═══════════════════════════════════════════════════════════════════════════
echo.
echo [5/6] Verifying service ports...
timeout /t 3 /nobreak

setlocal
for %%i in (5000 5001 8000) do (
    netstat -ano | findstr ":%%i" | findstr "LISTENING" >nul
    if !errorlevel! equ 0 (
        echo     [✓] Port %%i is listening
    ) else (
        echo     [⚠] Port %%i is NOT listening - check service logs
    )
)
endlocal

REM ═══════════════════════════════════════════════════════════════════════════
REM Final Message
REM ═══════════════════════════════════════════════════════════════════════════
echo.
echo [6/6] Startup Complete!
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║  SERVICES RUNNING - Access Dashboard                              ║
echo ╠════════════════════════════════════════════════════════════════════╣
echo ║  🌐  Web App:         http://127.0.0.1:5000                       ║
echo ║  🧪  CMS Service:    http://127.0.0.1:5001                       ║
echo ║  ⚙️  DL Backend:      http://127.0.0.1:8000/docs                 ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo To stop all services, close the command windows or press Ctrl+C
echo.
pause
