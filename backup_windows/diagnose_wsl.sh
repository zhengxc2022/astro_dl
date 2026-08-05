#!/bin/bash
# WSL 环境诊断脚本

echo "=========================================="
echo "WSL 环境诊断"
echo "=========================================="
echo ""

# 检查 Python
echo "1. 检查 Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✓ Python 已安装: $PYTHON_VERSION"
else
    echo "   ✗ Python 未安装"
    echo "   请运行: sudo apt install python3"
fi

# 检查 pip
echo ""
echo "2. 检查 pip..."
if command -v pip3 &> /dev/null; then
    echo "   ✓ pip 已安装"
else
    echo "   ✗ pip 未安装"
    echo "   请运行: sudo apt install python3-pip"
fi

# 检查 Flask
echo ""
echo "3. 检查 Flask..."
if python3 -c "import flask" 2>/dev/null; then
    FLASK_VERSION=$(python3 -c "import flask; print(flask.__version__)")
    echo "   ✓ Flask 已安装: $FLASK_VERSION"
else
    echo "   ✗ Flask 未安装"
    echo "   请运行: pip3 install flask --user"
fi

# 检查 DLtools.py
echo ""
echo "4. 检查 DLtools.py..."
if [ -f "/home/zhengxc/works/my_script/DLtools.py" ]; then
    echo "   ✓ DLtools.py 存在"
else
    echo "   ✗ DLtools.py 不存在"
    echo "   路径: /home/zhengxc/works/my_script/DLtools.py"
fi

# 检查当前目录
echo ""
echo "5. 检查项目目录..."
SCRIPT_DIR="/home/zhengxc/works/my_script/dltools_web"
if [ -d "$SCRIPT_DIR" ]; then
    echo "   ✓ 项目目录存在"
    echo "   路径: $SCRIPT_DIR"
else
    echo "   ✗ 项目目录不存在"
fi

# 检查脚本权限
echo ""
echo "6. 检查脚本执行权限..."
if [ -x "$SCRIPT_DIR/start_wsl.sh" ]; then
    echo "   ✓ start_wsl.sh 可执行"
else
    echo "   ✗ start_wsl.sh 不可执行"
    echo "   请运行: chmod +x $SCRIPT_DIR/*.sh"
fi

# 检查端口
echo ""
echo "7. 检查端口 5000..."
if netstat -tulpn 2>/dev/null | grep -q ":5000"; then
    echo "   ⚠ 端口 5000 已被占用"
    echo "   占用进程:"
    netstat -tulpn 2>/dev/null | grep ":5000"
else
    echo "   ✓ 端口 5000 可用"
fi

# 检查服务状态
echo ""
echo "8. 检查服务状态..."
if pgrep -f "python.*app.py" > /dev/null; then
    PID=$(pgrep -f "python.*app.py")
    echo "   ✓ 服务正在运行 (PID: $PID)"
else
    echo "   ✗ 服务未运行"
fi

# 测试 DLtools 导入
echo ""
echo "9. 测试 DLtools 导入..."
cd /home/zhengxc/works/my_script
if python3 -c "from DLtools import img_download" 2>/dev/null; then
    echo "   ✓ DLtools 导入成功"
else
    echo "   ✗ DLtools 导入失败"
    echo "   可能缺少依赖，请检查:"
    python3 -c "from DLtools import img_download" 2>&1 | head -5
fi

echo ""
echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""
echo "如果所有检查都通过，请运行:"
echo "  cd $SCRIPT_DIR"
echo "  ./start_wsl.sh"
echo ""
echo "或使用 Windows 批处理:"
echo "  双击运行 dltools_start.bat"
echo ""
