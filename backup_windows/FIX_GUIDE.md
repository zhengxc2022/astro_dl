# 快速修复指南

## 🔧 问题：dltools-start 命令失败

### 原因
- `start_desktop.sh` 不适合 WSL 环境
- 别名配置混乱

---

## ✅ 解决方案

### 步骤 1: 运行修复脚本

在 WSL 终端中运行：

```bash
cd /home/zhengxc/works/my_script/dltools_web
./update.sh
```

### 步骤 2: 重新加载配置

```bash
source ~/.bashrc
```

### 步骤 3: 验证

```bash
# 测试命令
dltools status
```

---

## 🚀 现在可以使用的命令

```bash
# 启动服务（自动打开浏览器）
dltools-start

# 停止服务
dltools-stop

# 查看状态
dltools status

# 打开浏览器
dltools open

# 查看日志
dltools log
```

---

## 📋 修改说明

### 统一了脚本

- ✅ `start.sh` - 自动检测 WSL/Linux，统一启动
- ✅ `manage.sh` - 统一管理命令
- ✅ `stop.sh` - 停止服务
- ❌ 删除了混乱的 `start_desktop.sh` 和 `start_wsl.sh`

### 清晰的别名

```bash
dltools-start → start.sh   # 统一启动
dltools-stop  → stop.sh    # 停止服务
dltools       → manage.sh  # 管理命令
```

---

## 🎯 Windows 批处理文件

仍然可以双击运行：
- `dltools_start.bat` - 启动服务
- `dltools_stop.bat` - 停止服务

---

## 🆘 仍然有问题？

### 手动启动（最可靠）

```bash
cd /home/zhengxc/works/my_script/dltools_web
./start.sh
```

### 查看日志

```bash
tail -f /tmp/dltools.log
```

### 检查服务

```bash
curl http://localhost:5000
```

---

## 📝 快速命令参考

| 操作 | 命令 |
|------|------|
| 启动服务 | `dltools-start` |
| 停止服务 | `dltools-stop` |
| 查看状态 | `dltools status` |
| 打开浏览器 | `dltools open` |
| 查看日志 | `dltools log` |
| 重启服务 | `dltools restart` |

---

## 🔍 故障排查

### 问题: 命令找不到

```bash
# 确保运行了修复脚本
./update.sh

# 重新加载配置
source ~/.bashrc

# 验证别名
alias | grep dltools
```

### 问题: 服务启动失败

```bash
# 检查端口
netstat -tulpn | grep 5000

# 查看错误
tail -f /tmp/dltools.log

# 手动运行测试
python3 app.py
```

### 问题: 浏览器不打开

```bash
# 手动打开
dltools open

# 或直接访问
# http://localhost:5000
```

---

**运行 `./update.sh` 后一切应该都正常了！** ✅
