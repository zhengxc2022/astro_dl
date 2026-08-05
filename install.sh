#!/bin/bash
# 安装脚本 - 可移植版本
# 自动检测脚本所在目录，便于分享给其他用户

# 获取脚本所在目录（支持软链接）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================"
echo "  Astronomical Image Downloader Installer"
echo "============================================"
echo ""
echo "Installation directory: $SCRIPT_DIR"
echo ""

# 检查 lib/DLtools.py 是否存在
if [ ! -f "$SCRIPT_DIR/lib/DLtools.py" ]; then
    echo "Error: lib/DLtools.py not found!"
    echo "Please make sure the 'lib' folder contains DLtools.py"
    exit 1
fi

echo "[1/3] Setting execute permissions..."
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null
echo "  Done."

echo ""
echo "[2/3] Adding command aliases to ~/.bashrc..."

# 使用绝对路径
BASHRC_BLOCK="# Astronomical Image Downloader - DO NOT EDIT THIS BLOCK
if [ -f '$SCRIPT_DIR/start.sh' ]; then
    alias dltools-start='cd \"$SCRIPT_DIR\" && ./start.sh'
    alias dltools-stop='cd \"$SCRIPT_DIR\" && ./stop.sh'
    alias dltools='cd \"$SCRIPT_DIR\" && ./manage.sh'
fi
# END Astronomical Image Downloader BLOCK"

# 移除旧的配置块（如果存在）
if grep -q "# Astronomical Image Downloader" ~/.bashrc 2>/dev/null; then
    # 使用 sed 删除整个配置块
    sed -i '/# Astronomical Image Downloader/,/# END Astronomical Image Downloader/d' ~/.bashrc
fi

# 添加新的配置
echo "" >> ~/.bashrc
echo "$BASHRC_BLOCK" >> ~/.bashrc
echo "  Commands added: dltools-start, dltools-stop, dltools"

echo ""
echo "[3/3] Checking dependencies..."
# 检查 Python 包
MISSING_PKGS=""
for pkg in flask astropy requests; do
    if ! python3 -c "import $pkg" 2>/dev/null; then
        MISSING_PKGS="$MISSING_PKGS $pkg"
    fi
done

if [ -n "$MISSING_PKGS" ]; then
    echo "  Warning: Missing Python packages:$MISSING_PKGS"
    echo "  Run: pip install -r $SCRIPT_DIR/requirements.txt"
else
    echo "  All dependencies satisfied."
fi

echo ""
echo "============================================"
echo "  Installation Complete!"
echo "============================================"
echo ""
echo "Usage:"
echo ""
echo "  Option 1: Terminal commands (restart terminal first)"
echo "    dltools-start    - Start service and open browser"
echo "    dltools-stop     - Stop service"
echo "    dltools status   - Check status"
echo ""
echo "  Option 2: Direct execution"
echo "    cd $SCRIPT_DIR"
echo "    ./start.sh"
echo ""
echo "To share with colleagues:"
echo "  Simply copy the entire 'dltools_web' folder"
echo "  and run ./install.sh on their machine"
echo ""
