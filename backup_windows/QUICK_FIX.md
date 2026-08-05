# 快速启动指南（WSL）

如果双击 `dltools_start.bat` 失败，请按以下步骤操作：

---

## 🔧 方法 1: 手动启动（最可靠）

### 步骤 1: 打开 WSL 终端
- 在 Windows 开始菜单搜索 "Ubuntu" 或 "WSL"
- 或在命令提示符中输入 `wsl`

### 步骤 2: 运行启动命令
```bash
cd /home/zhengxc/works/my_script/dltools_web
python3 app.py
```

### 步骤 3: 打开浏览器
在 Windows 浏览器中访问：
```
http://localhost:5000
```

---

## 🔍 方法 2: 诊断问题

双击运行诊断工具：
```
dltools_diagnose.bat
```

或在 WSL 中运行：
```bash
cd /home/zhengxc/works/my_script/dltools_web
./diagnose_wsl.sh
```

诊断会检查：
- ✓ Python 是否安装
- ✓ Flask 是否安装
- ✓ DLtools.py 是否存在
- ✓ 端口是否被占用
- ✓ 依赖是否完整

---

## 🚀 方法 3: 使用简化启动

双击运行：
```
start_manual.bat
```

这个脚本会：
1. 后台启动服务
2. 尝试打开浏览器
3. 如果浏览器未打开，手动访问 `http://localhost:5000`

---

## 💡 常见问题解决

### 问题 1: "Python 未安装"

```bash
sudo apt update
sudo apt install python3 python3-pip
pip3 install flask --user
```

### 问题 2: "Flask 未安装"

```bash
pip3 install flask --user
```

### 问题 3: "端口被占用"

```bash
# 查看占用进程
sudo netstat -tulpn | grep 5000

# 结束进程
sudo kill -9 <PID>
```

### 问题 4: "DLtools 导入失败"

```bash
# 安装缺失依赖
pip3 install numpy astropy requests wget astroquery beautifulsoup4 pyvo --user
```

---

## 📋 检查清单

运行服务前，确保：

- [ ] WSL 已安装并运行
- [ ] Python 3 已安装（`python3 --version`）
- [ ] Flask 已安装（`python3 -c "import flask"`）
- [ ] 端口 5000 未被占用
- [ ] 在正确的目录（`cd /home/zhengxc/works/my_script/dltools_web`）

---

## 🆘 仍然无法启动？

### 收集诊断信息

在 WSL 中运行：
```bash
cd /home/zhengxc/works/my_script/dltools_web
./diagnose_wsl.sh > diagnosis.txt 2>&1
cat diagnosis.txt
```

将诊断信息发给我，我可以帮您分析问题。

### 最后的手段

如果所有方法都失败，最简单的方式：

1. 打开 WSL 终端
2. 运行：
   ```bash
   cd /home/zhengxc/works/my_script/dltools_web
   python3 app.py
   ```
3. 保持终端窗口打开
4. 在浏览器访问 `http://localhost:5000`

这虽然需要保持终端窗口打开，但是最可靠的方法。

---

## 📞 快速参考

| 操作 | 命令/文件 |
|------|----------|
| 手动启动 | WSL 终端运行 `python3 app.py` |
| 诊断问题 | 双击 `dltools_diagnose.bat` |
| 简化启动 | 双击 `start_manual.bat` |
| 停止服务 | 双击 `dltools_stop.bat` |
| 浏览器访问 | `http://localhost:5000` |

---

**先运行诊断，找出具体问题！** 🔍
