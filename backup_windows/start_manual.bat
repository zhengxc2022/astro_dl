@echo off
echo ============================================
echo Simple Start (Manual Browser)
echo ============================================
echo.

echo Step 1: Starting service in background...
start /B wsl cd /home/zhengxc/works/my_script/dltools_web; python3 app.py ^> /tmp/dltools.log 2^>^&1

echo Waiting 3 seconds for service to start...
timeout /t 3 /nobreak >nul

echo.
echo Step 2: Service should be running now!
echo.
echo ============================================
echo IMPORTANT:
echo.
echo 1. Open your browser manually
echo 2. Go to: http://localhost:5000
echo.
echo If it doesn't work, run dltools_diagnose.bat
echo ============================================
echo.

REM Try to open browser
echo Attempting to open browser...
start http://localhost:5000

echo.
echo Service is running in the background.
echo Close this window will NOT stop the service.
echo.
echo To stop: Run dltools_stop.bat
echo.
pause
