#!/bin/bash
# 统一管理脚本（支持 WSL 和 Linux）

cd /home/zhengxc/works/my_script/dltools_web

# 检测运行环境
IS_WSL=false
if grep -qi microsoft /proc/version 2>/dev/null; then
    IS_WSL=true
fi

open_browser() {
    if [ "$IS_WSL" = true ]; then
        # WSL 环境
        if command -v powershell.exe &> /dev/null; then
            powershell.exe -Command "Start-Process 'http://localhost:5000'" 2>/dev/null
        elif command -v cmd.exe &> /dev/null; then
            cmd.exe /c start "" http://localhost:5000 2>/dev/null
        fi
    else
        # Linux 桌面环境
        xdg-open http://localhost:5000 2>/dev/null || open http://localhost:5000 2>/dev/null
    fi
}

case "$1" in
    start)
        echo "🚀 启动服务..."
        if pgrep -f "python.*app.py" > /dev/null; then
            echo "⚠️  服务已在运行"
            echo "📍 访问: http://localhost:5000"
        else
            nohup python3 app.py > /tmp/dltools.log 2>&1 &
            SERVICE_PID=$!

            # 等待启动
            sleep 2

            # 检查是否启动成功
            if kill -0 $SERVICE_PID 2>/dev/null && curl -s http://localhost:5000 > /dev/null 2>&1; then
                echo "✓ 服务启动成功"
                echo "📍 访问: http://localhost:5000"
                echo "📝 日志: /tmp/dltools.log"
            else
                echo "✗ 启动失败，请查看日志"
                tail -20 /tmp/dltools.log
            fi
        fi
        ;;

    stop)
        echo "🛑 停止服务..."
        if pgrep -f "python.*app.py" > /dev/null; then
            pkill -f "python.*app.py"
            sleep 1
            echo "✓ 服务已停止"
        else
            echo "⚠️  服务未在运行"
        fi
        ;;

    restart)
        $0 stop
        sleep 2
        $0 start
        ;;

    status)
        echo "📊 服务状态..."
        if pgrep -f "python.*app.py" > /dev/null; then
            PID=$(pgrep -f "python.*app.py")
            echo "✓ 服务运行中"
            echo "  PID: $PID"
            echo "  端口: 5000"
            echo "  访问: http://localhost:5000"
            echo ""

            # 检查服务是否响应
            if curl -s http://localhost:5000 > /dev/null 2>&1; then
                echo "  状态: ✓ 响应正常"
            else
                echo "  状态: ⚠️  未响应"
            fi

            echo ""
            echo "📁 下载目录:"
            echo "  WSL/Linux: $(pwd)/downloads/"

            if [ "$IS_WSL" = true ] && command -v wslpath &> /dev/null; then
                echo "  Windows: $(wslpath -w "$(pwd)/downloads/")"
            fi
        else
            echo "✗ 服务未运行"
        fi
        ;;

    open)
        echo "🌐 打开浏览器..."

        # 检查服务是否运行
        if ! pgrep -f "python.*app.py" > /dev/null; then
            echo "⚠️  服务未运行，请先启动服务"
            echo "运行: dltools start"
            exit 1
        fi

        # 等待服务响应
        if ! curl -s http://localhost:5000 > /dev/null 2>&1; then
            echo "⚠️  服务未响应，请稍等片刻后重试"
            exit 1
        fi

        open_browser
        echo "✓ 浏览器已打开"
        ;;

    log)
        echo "📋 查看日志 (Ctrl+C 退出)..."
        tail -f /tmp/dltools.log
        ;;

    path)
        echo "📁 路径信息..."
        echo ""
        echo "WSL/Linux 路径:"
        echo "  项目: $(pwd)"
        echo "  下载: $(pwd)/downloads/"
        echo ""
        if [ "$IS_WSL" = true ] && command -v wslpath &> /dev/null; then
            echo "Windows 路径:"
            echo "  项目: $(wslpath -w "$(pwd)")"
            echo "  下载: $(wslpath -w "$(pwd)/downloads/")"
        fi
        ;;

    test)
        echo "🧪 测试服务..."
        if curl -s http://localhost:5000 > /dev/null 2>&1; then
            echo "✓ 服务响应正常"
            echo ""
            echo "API 测试:"
            curl -s http://localhost:5000/api/surveys | python3 -m json.tool | head -20
        else
            echo "✗ 服务未响应"
        fi
        ;;

    *)
        echo "Astronomical Image Downloader 管理工具"
        echo ""
        echo "用法: $0 {start|stop|restart|status|open|log|path|test}"
        echo ""
        echo "命令:"
        echo "  start   - 启动服务"
        echo "  stop    - 停止服务"
        echo "  restart - 重启服务"
        echo "  status  - 查看状态（包含服务响应检查）"
        echo "  open    - 打开浏览器（自动检查服务状态）"
        echo "  log     - 查看日志"
        echo "  path    - 显示路径映射"
        echo "  test    - 测试服务响应"
        exit 1
        ;;
esac
