#!/bin/bash
# WSL 专用启动脚本（改进版）

cd /home/zhengxc/works/my_script/dltools_web

echo "🚀 启动 Astronomical Image Downloader (WSL)..."
echo ""

# 检查是否已在运行
if pgrep -f "python.*app.py" > /dev/null; then
    echo "⚠️  服务已在运行"
    echo "📍 访问地址: http://localhost:5000"
    echo ""
    read -p "是否打开浏览器? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🌐 正在打开浏览器..."
        # 使用更可靠的方式打开浏览器
        if command -v powershell.exe &> /dev/null; then
            powershell.exe -Command "Start-Process 'http://localhost:5000'" 2>/dev/null
        elif command -v cmd.exe &> /dev/null; then
            cmd.exe /c start "" http://localhost:5000 2>/dev/null
        fi
    fi
    exit 0
fi

# 后台启动服务
echo "⏳ 正在启动服务..."
nohup python3 app.py > /tmp/dltools.log 2>&1 &
SERVICE_PID=$!

# 等待服务启动并检查是否可以访问
MAX_WAIT=10
WAIT_COUNT=0
echo -n "⏳ 等待服务启动"

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
    echo -n "."
    
    # 检查进程是否还在运行
    if ! kill -0 $SERVICE_PID 2>/dev/null; then
        echo ""
        echo "✗ 服务启动失败"
        echo "请检查日志: tail -f /tmp/dltools.log"
        exit 1
    fi
    
    # 检查 HTTP 服务是否响应
    if curl -s http://localhost:5000 > /dev/null 2>&1; then
        echo " ✓"
        break
    fi
done

# 最终检查
if pgrep -f "python.*app.py" > /dev/null; then
    echo ""
    echo "✓ 服务启动成功"
    echo "📍 访问地址: http://localhost:5000"
    echo "📝 日志文件: /tmp/dltools.log"
    echo ""
    
    # 打开浏览器
    echo "🌐 正在打开浏览器..."
    sleep 1
    
    # 使用 PowerShell（最可靠）
    if command -v powershell.exe &> /dev/null; then
        powershell.exe -Command "Start-Process 'http://localhost:5000'" 2>/dev/null
        echo "✓ 浏览器已打开"
    # 备用方案：使用 cmd
    elif command -v cmd.exe &> /dev/null; then
        cmd.exe /c start "" http://localhost:5000 2>/dev/null
        echo "✓ 浏览器已打开"
    else
        echo "⚠️  请手动打开浏览器访问: http://localhost:5000"
    fi
    
    echo ""
    echo "=========================================="
    echo "💡 使用提示:"
    echo "  - 关闭浏览器不会停止服务"
    echo "  - 要停止服务，运行: ./stop.sh"
    echo "  - 查看日志: tail -f /tmp/dltools.log"
    echo "=========================================="
else
    echo ""
    echo "✗ 服务启动失败"
    echo "请检查日志: tail -f /tmp/dltools.log"
    exit 1
fi
