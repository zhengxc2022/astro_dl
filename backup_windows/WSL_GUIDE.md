# WSL 环境使用指南

WSL (Windows Subsystem for Linux) 环境下的使用说明和注意事项。

---

## 🔍 WSL 特性说明

### ✅ 可以正常使用的功能
- ✅ Flask Web 服务运行
- ✅ 通过浏览器访问（`http://localhost:5000`）
- ✅ 下载天文图像
- ✅ 所有 Python 功能

### ⚠️ 需要注意的地方
- 📁 文件路径：WSL 和 Windows 路径不同
- 🌐 浏览器打开：需要调用 Windows 浏览器
- 🖥️ 桌面快捷方式：`.desktop` 文件不适用
- 🔄 开机自启：需要使用 Windows 任务计划程序

---

## 🚀 WSL 环境安装

### 一键安装

```bash
cd /home/zhengxc/works/my_script/dltools_web
chmod +x install_wsl.sh
./install_wsl.sh
```

安装后会：
- ✅ 创建 WSL 专用启动脚本
- ✅ 创建 Windows 批处理文件
- ✅ 添加终端快捷命令

---

## 📱 使用方法

### 方法 1: Windows 批处理（推荐）

双击运行以下文件：
- **`dltools_start.bat`** - 启动服务
- **`dltools_stop.bat`** - 停止服务

**优点**：
- 无需打开 WSL 终端
- 双击即可运行
- 自动打开浏览器

### 方法 2: WSL 终端命令

```bash
# 启动服务并打开浏览器
dltools-start

# 停止服务
dltools-stop

# 查看状态
dltools status

# 打开浏览器
dltools open

# 查看路径映射
dltools path
```

### 方法 3: 手动运行

```bash
cd /home/zhengxc/works/my_script/dltools_web

# 启动
./start_wsl.sh

# 或直接运行
python3 app.py
```

然后在 Windows 浏览器中访问：`http://localhost:5000`

---

## 📁 文件路径映射

### WSL 和 Windows 路径对照

| 位置 | WSL 路径 | Windows 路径 |
|------|---------|--------------|
| 项目目录 | `/home/zhengxc/works/my_script/dltools_web/` | `\\wsl$\Ubuntu\home\zhengxc\works\my_script\dltools_web\` |
| 下载目录 | `./downloads/` | `\\wsl$\Ubuntu\home\zhengxc\works\my_script\dltools_web\downloads\` |

### 访问下载的文件

**方法 1: Windows 资源管理器**
1. 打开资源管理器
2. 地址栏输入：`\\wsl$\Ubuntu\home\zhengxc\works\my_script\dltools_web\downloads\`
3. 或访问：`\\wsl.localhost\Ubuntu\home\zhengxc\works\my_script\dltools_web\downloads\`

**方法 2: 在 WSL 中查看 Windows 路径**
```bash
# 查看路径映射
dltools path

# 或使用 wslpath 命令
wslpath -w "$(pwd)/downloads/"
```

---

## 🌐 浏览器访问

### 自动打开浏览器

WSL 脚本会尝试自动打开 Windows 浏览器：
```bash
# 使用 explorer.exe
explorer.exe "http://localhost:5000"

# 或使用 cmd.exe
cmd.exe /c start http://localhost:5000
```

### 手动访问

如果自动打开失败，在 Windows 浏览器中访问：
```
http://localhost:5000
```

---

## 🔄 开机自启动（可选）

WSL 不支持 systemd 开机自启，但可以使用 Windows 任务计划程序：

### 步骤 1: 创建启动脚本

创建 `C:\Scripts\start_dltools.bat`：
```batch
@echo off
wsl cd /home/zhengxc/works/my_script/dltools_web ^&^& ./start_wsl.sh
```

### 步骤 2: 创建计划任务

1. 打开 **任务计划程序**（搜索 "Task Scheduler"）
2. 创建基本任务
3. 触发器：**计算机启动时**
4. 操作：**启动程序**
   - 程序：`C:\Scripts\start_dltools.bat`
5. 完成

### 步骤 3: 设置为后台运行

修改 `C:\Scripts\start_dltools.bat`：
```batch
@echo off
start /B wsl cd /home/zhengxc/works/my_script/dltools_web ^&^& nohup python3 app.py ^> /tmp/dltools.log 2^>^&1 ^&
```

---

## ⚙️ 配置建议

### 下载目录设置

**选项 1: 使用 WSL 文件系统（默认）**
```
下载目录: ./downloads/
Windows 访问: \\wsl$\Ubuntu\home\zhengxc\works\my_script\dltools_web\downloads\
```

**选项 2: 使用 Windows 文件系统（更快）**
```
下载目录: /mnt/c/Users/YourName/Downloads/dltools/
Windows 访问: C:\Users\YourName\Downloads\dltools\
```

修改方法：
1. 在 Web 界面的 "Output Settings" 中设置下载目录
2. 或修改 `config.py`:
   ```python
   DEFAULT_OUTPUT_DIR = '/mnt/c/Users/YourName/Downloads/dltools/'
   ```

### 端口修改

如果端口冲突，修改 `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)  # 改为其他端口
```

---

## 🐛 常见问题

### Q1: 浏览器无法访问？

检查：
```bash
# 1. 检查服务状态
dltools status

# 2. 检查端口
netstat -tulpn | grep 5000

# 3. 查看日志
dltools log
```

### Q2: 下载的文件在哪里？

```bash
# 查看路径映射
dltools path

# 或在 Windows 资源管理器中访问
# \\wsl$\Ubuntu\home\zhengxc\works\my_script\dltools_web\downloads\
```

### Q3: WSL 服务无法启动？

```bash
# 检查 Python
python3 --version

# 检查依赖
pip3 list | grep flask

# 查看错误日志
tail -f /tmp/dltools.log
```

### Q4: 如何在 Windows 中编辑 WSL 文件？

**方法 1**: VS Code
```bash
code /home/zhengxc/works/my_script/dltools_web/
```

**方法 2**: Windows 资源管理器
- 地址栏输入：`\\wsl$\Ubuntu\home\zhengxc\works\my_script\dltools_web\`

### Q5: 性能慢？

- WSL 2 比 WSL 1 快很多
- 文件操作建议使用 Windows 文件系统（`/mnt/c/`）
- 或将项目移到 Windows 文件系统

---

## 📊 WSL 1 vs WSL 2

| 特性 | WSL 1 | WSL 2 |
|------|-------|-------|
| 文件系统性能 | 较慢 | 快 |
| 内存占用 | 低 | 较高 |
| systemd 支持 | ❌ | ✅ |
| 网络性能 | 快 | 稍慢 |
| 兼容性 | 高 | 更高 |

### 检查 WSL 版本

```bash
wsl --list --verbose
```

### 升级到 WSL 2

```powershell
# 在 Windows PowerShell 中运行
wsl --set-version Ubuntu 2
```

---

## 🎯 最佳实践

### 1. 使用 Windows 批处理启动

双击 `dltools_start.bat` 最方便

### 2. 下载文件存到 Windows

在 Web 界面设置：
```
下载目录: /mnt/c/Users/YourName/Downloads/dltools/
```

好处：
- ✅ Windows 直接访问
- ✅ 性能更好
- ✅ 方便管理

### 3. 使用 VS Code 开发

```bash
# 在 WSL 中打开项目
code .
```

VS Code 会自动连接 WSL，提供完整的开发体验。

---

## 📝 快速参考

| 操作 | 方法 |
|------|------|
| 启动服务 | 双击 `dltools_start.bat` |
| 停止服务 | 双击 `dltools_stop.bat` |
| 查看状态 | `dltools status` |
| 查看路径 | `dltools path` |
| 访问文件 | `\\wsl$\Ubuntu\home\zhengxc\works\my_script\dltools_web\` |
| 浏览器访问 | `http://localhost:5000` |

---

## 🔗 有用的资源

- [WSL 官方文档](https://docs.microsoft.com/zh-cn/windows/wsl/)
- [WSL 文件系统访问](https://docs.microsoft.com/zh-cn/windows/wsl/filesystems)
- [VS Code WSL 扩展](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl)

---

**在 WSL 中享受天文图像下载体验！** 🚀
