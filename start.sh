#!/bin/bash
# 统一启动脚本（自动检测环境，可移植版本）

# 获取脚本所在目录（支持软链接）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检测运行环境
IS_WSL=false
if grep -qi microsoft /proc/version 2>/dev/null; then
    IS_WSL=true
fi

# 检测是否为非交互模式（通过 .bat 调用）
AUTO_OPEN=true
if [ -t 0 ]; then
    AUTO_OPEN=false
fi

echo "🚀 启动 Astronomical Image Downloader..."
echo ""

# 打开浏览器的函数
open_browser() {
    if [ "$IS_WSL" = true ]; then
        # WSL 环境
        if command -v powershell.exe &> /dev/null; then
            powershell.exe -Command "Start-Process 'http://localhost:5000'" 2>/dev/null
            echo "✓ 浏览器已打开"
        elif command -v cmd.exe &> /dev/null; then
            cmd.exe /c start "" http://localhost:5000 2>/dev/null
            echo "✓ 浏览器已打开"
        else
            echo "⚠️  请手动打开浏览器访问: http://localhost:5000"
        fi
    else
        # Linux 桌面环境
        if xdg-open http://localhost:5000 2>/dev/null || open http://localhost:5000 2>/dev/null; then
            echo "✓ 浏览器已打开"
        else
            echo "⚠️  请手动打开浏览器访问: http://localhost:5000"
        fi
    fi
}

# 检查是否已在运行
if pgrep -f "python.*app.py" > /dev/null; then
    echo "⚠️  服务已在运行"
    echo "📍 访问地址: http://localhost:5000"
    echo ""
    
    if [ "$AUTO_OPEN" = true ]; then
        # 非交互模式，自动打开浏览器
        echo "🌐 正在打开浏览器..."
        sleep 1
        open_browser
    else
        # 交互模式，询问用户
        read -p "是否打开浏览器? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open_browser
        fi
    fi
    exit 0
fi

# 后台启动服务
echo "⏳ 正在启动服务..."
nohup python3 app.py > /tmp/dltools.log 2>&1 &
SERVICE_PID=$!

# 等待服务启动
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
    open_browser

    echo ""
    echo "=========================================="
    echo "💡 使用提示:"
    echo "  - 关闭浏览器不会停止服务"
    echo "  - 要停止服务，运行: dltools stop"
    echo "  - 查看日志: tail -f /tmp/dltools.log"
    echo "=========================================="
else
    echo ""
    echo "✗ 服务启动失败"
    echo "请检查日志: tail -f /tmp/dltools.log"
    exit 1
fi
