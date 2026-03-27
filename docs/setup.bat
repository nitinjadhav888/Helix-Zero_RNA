@echo off
REM ============================================
REM Helix-Zero Setup Script (Windows)
REM ============================================

echo.
echo ========================================
echo    Helix-Zero Setup Script
echo ========================================
echo.

REM Check Node.js
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed!
    echo.
    echo Please install Node.js first:
    echo   1. Go to https://nodejs.org/
    echo   2. Download the LTS version
    echo   3. Run the installer
    echo   4. Restart this script
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node -v') do set NODE_VERSION=%%i
echo [OK] Node.js installed: %NODE_VERSION%

REM Check npm
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] npm is not installed!
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('npm -v') do set NPM_VERSION=%%i
echo [OK] npm installed: %NPM_VERSION%

REM Check Git
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Git is not installed (optional for local development)
) else (
    for /f "tokens=*" %%i in ('git --version') do set GIT_VERSION=%%i
    echo [OK] %GIT_VERSION%
)

echo.
echo Installing dependencies...
echo.

call npm install

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================
    echo [SUCCESS] Dependencies installed!
    echo ========================================
    echo.
    echo Starting development server...
    echo.
    echo ======================================
    echo   Open http://localhost:5173
    echo   in your browser
    echo ======================================
    echo.
    echo Press Ctrl+C to stop the server
    echo.
    call npm run dev
) else (
    echo.
    echo [ERROR] Failed to install dependencies
    echo Try running: npm install --legacy-peer-deps
    pause
    exit /b 1
)
