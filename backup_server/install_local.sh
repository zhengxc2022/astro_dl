#!/bin/bash
# 安装桌面快捷方式和便捷脚本

SCRIPT_DIR="/home/zhengxc/works/my_script/dltools_web"

echo "🔧 安装 Astronomical Image Downloader..."
echo ""

# 设置执行权限
chmod +x "$SCRIPT_DIR"/*.sh

# 创建桌面快捷方式
DESKTOP_FILE="$HOME/Desktop/AstronomicalImageDownloader.desktop"
cp "$SCRIPT_DIR/AstronomicalImageDownloader.desktop" "$DESKTOP_FILE"
chmod +x "$DESKTOP_FILE"

echo "✓ 桌面快捷方式已创建"
echo ""

# 添加命令别名到 ~/.bashrc
BASHRC_ALIAS="# Astronomical Image Downloader
alias dltools-start='$SCRIPT_DIR/start_desktop.sh'
alias dltools-stop='$SCRIPT_DIR/stop.sh'
alias dltools='$SCRIPT_DIR/manage.sh'"

if ! grep -q "dltools-start" ~/.bashrc; then
    echo "$BASHRC_ALIAS" >> ~/.bashrc
    echo "✓ 命令别名已添加到 ~/.bashrc"
    echo ""
    echo "现在可以使用以下命令:"
    echo "  dltools-start  - 一键启动"
    echo "  dltools-stop   - 停止服务"
    echo "  dltools status - 查看状态"
else
    echo "✓ 命令别名已存在"
fi

echo ""
echo "✓ 安装完成！"
echo ""
echo "📖 使用方法:"
echo ""
echo "方法 1: 双击桌面图标"
echo "  桌面上的 'Astronomical Image Downloader' 图标"
echo ""
echo "方法 2: 使用终端命令"
echo "  dltools-start    # 启动并打开浏览器"
echo "  dltools-stop     # 停止服务"
echo "  dltools status   # 查看状态"
echo "  dltools start    # 仅启动服务"
echo "  dltools open     # 打开浏览器"
echo ""
echo "方法 3: 直接运行脚本"
echo "  cd $SCRIPT_DIR"
echo "  ./start_desktop.sh"
echo ""
