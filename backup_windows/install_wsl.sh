#!/bin/bash
# 统一安装脚本（支持 WSL 和 Linux）

SCRIPT_DIR="/home/zhengxc/works/my_script/dltools_web"

echo "=========================================="
echo "安装 Astronomical Image Downloader"
echo "=========================================="
echo ""

# 检测运行环境
IS_WSL=false
if grep -qi microsoft /proc/version 2>/dev/null; then
    IS_WSL=true
    echo "✓ 检测到 WSL 环境"
else
    echo "✓ 检测到 Linux 环境"
fi

echo ""

# 设置执行权限
echo "设置脚本执行权限..."
chmod +x "$SCRIPT_DIR"/*.sh

# 添加命令别名到 ~/.bashrc
echo "配置命令别名..."
BASHRC_ALIAS="# Astronomical Image Downloader
alias dltools='$SCRIPT_DIR/manage.sh'
alias dltools-start='$SCRIPT_DIR/start.sh'
alias dltools-stop='$SCRIPT_DIR/stop.sh'"

# 移除旧的别名配置
sed -i '/# Astronomical Image Downloader/,/alias dltools-stop/d' ~/.bashrc 2>/dev/null

# 添加新别名
echo "$BASHRC_ALIAS" >> ~/.bashrc
echo "✓ 命令别名已添加到 ~/.bashrc"
echo ""
echo "可用命令:"
echo "  dltools-start  - 启动服务并打开浏览器"
echo "  dltools-stop   - 停止服务"
echo "  dltools status - 查看状态"

# 如果是 WSL，创建 Windows 批处理文件
if [ "$IS_WSL" = true ]; then
    echo ""
    echo "创建 Windows 批处理文件..."

    # 创建启动批处理
    cat > "$SCRIPT_DIR/dltools_start.bat" <<'EOF'
@echo off
echo ============================================
echo Astronomical Image Downloader - Starting
echo ============================================
echo.

echo Starting service in WSL...
wsl cd /home/zhengxc/works/my_script/dltools_web; ./start.sh

if %ERRORLEVEL% EQU 0 (
    timeout /t 2 /nobreak >nul
    start http://localhost:5000
)

echo.
pause
EOF

    # 创建停止批处理
    cat > "$SCRIPT_DIR/dltools_stop.bat" <<'EOF'
@echo off
echo Stopping service...
wsl cd /home/zhengxc/works/my_script/dltools_web; ./stop.sh
echo.
pause
EOF

    echo "✓ Windows 批处理文件已创建"
    echo "  - dltools_start.bat"
    echo "  - dltools_stop.bat"
fi

# 创建下载目录
mkdir -p "$SCRIPT_DIR/downloads"

echo ""
echo "=========================================="
echo "✓ 安装完成！"
echo "=========================================="
echo ""

if [ "$IS_WSL" = true ]; then
    echo "📖 WSL 环境使用方法:"
    echo ""
    echo "方法 1: Windows 批处理（推荐）"
    echo "  双击运行: dltools_start.bat"
    echo ""
    echo "方法 2: WSL 命令行"
    echo "  运行: dltools-start"
    echo ""
else
    echo "📖 Linux 环境使用方法:"
    echo ""
    echo "  运行: dltools-start"
    echo "  或: ./start.sh"
    echo ""
fi

echo "首次使用请运行:"
echo "  source ~/.bashrc"
echo ""
