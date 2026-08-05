#!/bin/bash
# 一键启动脚本 - 自动打开浏览器

cd /home/zhengxc/works/my_script/dltools_web

echo "🚀 启动 Astronomical Image Downloader..."
echo "📍 访问地址: http://localhost:5000"
echo ""

# 检查是否已在运行
if pgrep -f "python.*app.py" > /dev/null; then
    echo "⚠️  服务已在运行"
    echo "正在打开浏览器..."
    xdg-open http://localhost:5000 2>/dev/null || open http://localhost:5000 2>/dev/null
    exit 0
fi

# 后台启动服务
nohup python3 app.py > /dev/null 2>&1 &
sleep 2

# 检查是否启动成功
if pgrep -f "python.*app.py" > /dev/null; then
    echo "✓ 服务启动成功"
    echo "✓ 正在打开浏览器..."
    sleep 1
    xdg-open http://localhost:5000 2>/dev/null || open http://localhost:5000 2>/dev/null
    echo ""
    echo "💡 关闭浏览器不会停止服务"
    echo "💡 要停止服务，运行: ./stop.sh"
else
    echo "✗ 启动失败"
fi
