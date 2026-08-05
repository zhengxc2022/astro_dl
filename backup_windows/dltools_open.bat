@echo off
echo ============================================
echo Opening Astronomical Image Downloader
echo ============================================
echo.

echo Checking if service is running...
wsl pgrep -f "python.*app.py" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Service is not running!
    echo Please start it first: dltools_start.bat
    echo.
    pause
    exit /b 1
)

echo Service is running.
echo.
echo Opening browser...
timeout /t 1 /nobreak >nul
start http://localhost:5000

echo.
echo Browser opened: http://localhost:5000
echo.
pause
