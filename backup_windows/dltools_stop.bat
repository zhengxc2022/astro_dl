@echo off
echo ============================================
echo Astronomical Image Downloader - Stopping
echo ============================================
echo.

echo Stopping service in WSL...
wsl cd /home/zhengxc/works/my_script/dltools_web; ./stop.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo Service stopped successfully!
    echo ============================================
) else (
    echo.
    echo ============================================
    echo Note: Service may already be stopped
    echo ============================================
)

echo.
pause
