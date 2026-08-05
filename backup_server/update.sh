#!/bin/bash
# 快速修复脚本 - 重新安装和更新

echo "=========================================="
echo "修复和更新 Astronomical Image Downloader"
echo "=========================================="
echo ""

SCRIPT_DIR="/home/zhengxc/works/my_script/dltools_web"

# 1. 设置执行权限
echo "[1/3] 设置脚本执行权限..."
chmod +x "$SCRIPT_DIR"/*.sh
echo "✓ 完成"

# 2. 清理旧别名
echo ""
echo "[2/3] 清理旧配置..."
sed -i '/# Astronomical Image Downloader/,/^$/d' ~/.bashrc 2>/dev/null
sed -i '/alias dltools/d' ~/.bashrc 2>/dev/null
echo "✓ 完成"

# 3. 添加新别名
echo ""
echo "[3/3] 添加新配置..."
cat >> ~/.bashrc << 'EOF'

# Astronomical Image Downloader
alias dltools='/home/zhengxc/works/my_script/dltools_web/manage.sh'
alias dltools-start='/home/zhengxc/works/my_script/dltools_web/start.sh'
alias dltools-stop='/home/zhengxc/works/my_script/dltools_web/stop.sh'
EOF

echo "✓ 完成"

echo ""
echo "=========================================="
echo "✓ 修复完成！"
echo "=========================================="
echo ""
echo "请运行以下命令使配置生效:"
echo ""
echo "  source ~/.bashrc"
echo ""
echo "然后使用以下命令:"
echo "  dltools-start  - 启动服务"
echo "  dltools-stop   - 停止服务"
echo "  dltools status - 查看状态"
echo ""
