#!/bin/bash
# 管理脚本 - 统一管理服务状态

# 获取脚本所在目录（支持软链接）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PID_FILE="/tmp/dltools.pid"
LOG_FILE="/tmp/dltools.log"
SERVICE_NAME="Astronomical Image Downloader"

# 检查服务是否在运行
is_running() {
    pgrep -f "python.*app.py" > /dev/null 2>&1
}

# 获取服务PID
get_pid() {
    pgrep -f "python.*app.py" 2>/dev/null
}

# 检查服务是否真正响应
is_responsive() {
    curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ 2>/dev/null | grep -q "200"
}

case "$1" in
    status)
        echo "============================================"
        echo "  $SERVICE_NAME - Status"
        echo "============================================"
        echo ""

        if is_running; then
            PID=$(get_pid)
            echo "  Status:  ✓ Running"
            echo "  PID:     $PID"

            if is_responsive; then
                echo "  HTTP:    ✓ Responding (http://localhost:5000)"
            else
                echo "  HTTP:    ✗ Not responding (starting up?)"
            fi

            # 显示运行时间
            if [ -n "$PID" ]; then
                RUNTIME=$(ps -o etime= -p "$PID" 2>/dev/null | tr -d ' ')
                if [ -n "$RUNTIME" ]; then
                    echo "  Uptime:  $RUNTIME"
                fi
            fi

            # 显示内存占用
            if [ -n "$PID" ]; then
                MEM=$(ps -o rss= -p "$PID" 2>/dev/null | awk '{printf "%.1f MB", $1/1024}')
                if [ -n "$MEM" ]; then
                    echo "  Memory:  $MEM"
                fi
            fi
        else
            echo "  Status:  ✗ Stopped"
        fi

        echo ""
        echo "  Log:     $LOG_FILE"
        echo "============================================"
        ;;

    start)
        ./start.sh
        ;;

    stop)
        ./stop.sh
        ;;

    restart)
        echo "Restarting $SERVICE_NAME..."
        if is_running; then
            pkill -f "python.*app.py"
            sleep 2
        fi
        ./start.sh
        ;;

    log)
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            echo "Log file not found: $LOG_FILE"
            exit 1
        fi
        ;;

    *)
        echo "Usage: dltools {status|start|stop|restart|log}"
        echo ""
        echo "Commands:"
        echo "  status   - Show service status"
        echo "  start    - Start the service"
        echo "  stop     - Stop the service"
        echo "  restart  - Restart the service"
        echo "  log      - Tail the log file"
        exit 1
        ;;
esac
