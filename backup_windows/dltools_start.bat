@echo off
chcp 65001 >nul 2>&1
echo ============================================
echo Astronomical Image Downloader - Starting
echo ============================================
echo.

echo [1/3] Checking if service already running...
wsl pgrep -f "python.*app.py" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Service is already running!
    echo Opening browser...
    start http://localhost:5000
    goto :end
)

echo.
echo [2/3] Starting service in WSL...
wsl bash -c "cd /home/zhengxc/works/my_script/dltools_web && nohup python3 app.py > /tmp/dltools.log 2>&1 &"

echo.
echo [3/3] Waiting for service to start...

set /a count=0
:check_loop
timeout /t 1 /nobreak >nul
set /a count+=1
echo Waiting... %count%/30

curl -s http://localhost:5000 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Service is ready!
    timeout /t 1 /nobreak >nul
    start http://localhost:5000
    echo.
    echo ============================================
    echo Service started successfully!
    echo URL: http://localhost:5000
    echo Log: wsl tail -f /tmp/dltools.log
    echo Stop: dltools_stop.bat
    echo ============================================
    goto :end
)

if %count% LSS 30 goto :check_loop

echo.
echo ============================================
echo WARNING: Service not responding after 30s
echo Please check: wsl tail -f /tmp/dltools.log
echo ============================================

:end
echo.
pause
