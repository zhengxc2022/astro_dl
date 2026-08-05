#!/bin/bash
# 停止服务脚本

echo "Stopping Astronomical Image Downloader..."

if pgrep -f "python.*app.py" > /dev/null; then
    pkill -f "python.*app.py"
    sleep 1
    echo "Service stopped."
else
    echo "Service is not running."
fi
