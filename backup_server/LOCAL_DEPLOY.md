# 本地部署指南

不用每次运行 `python app.py` 的便捷方案！

---

## 🚀 快速开始

### 一键安装

```bash
cd /home/zhengxc/works/my_script/dltools_web
chmod +x install_local.sh
./install_local.sh
```

安装后会创建：
- ✅ 桌面快捷方式（双击启动）
- ✅ 终端快捷命令

---

## 📱 使用方法

### 方法 1：桌面图标（最简单）

双击桌面上的 **Astronomical Image Downloader** 图标

- 自动启动服务
- 自动打开浏览器
- 关闭浏览器不会停止服务

### 方法 2：终端快捷命令

```bash
# 一键启动（自动打开浏览器）
dltools-start

# 停止服务
dltools-stop

# 管理命令
dltools start     # 启动服务
dltools stop      # 停止服务
dltools restart   # 重启服务
dltools status    # 查看状态
dltools open      # 打开浏览器
dltools log       # 查看日志
```

### 方法 3：运行脚本

```bash
cd /home/zhengxc/works/my_script/dltools_web

# 启动并打开浏览器
./start_desktop.sh

# 停止服务
./stop.sh

# 管理服务
./manage.sh status
```

---

## 🔄 开机自启动（可选）

如果想要开机自动启动：

```bash
# 复制用户服务文件
mkdir -p ~/.config/systemd/user/
cp /home/zhengxc/works/my_script/dltools_web/dltools-web-user.service ~/.config/systemd/user/

# 启用并启动
systemctl --user enable dltools-web-user
systemctl --user start dltools-web-user

# 查看状态
systemctl --user status dltools-web-user

# 管理命令
systemctl --user stop dltools-web-user     # 停止
systemctl --user restart dltools-web-user  # 重启
systemctl --user disable dltools-web-user  # 禁用开机自启
```

**注意**：开机自启动后，服务会在后台运行，访问 `http://localhost:5000`

---

## 💡 提示

### 服务管理

- **启动**：`dltools-start` 或 `dltools start`
- **停止**：`dltools-stop` 或 `dltools stop`
- **状态**：`dltools status`
- **日志**：`dltools log`

### 端口占用

如果端口 5000 被占用：

1. 编辑 `app.py`，修改最后一行：
   ```python
   app.run(debug=True, host='127.0.0.1', port=8000)  # 改为其他端口
   ```

2. 或停止占用进程：
   ```bash
   sudo lsof -i:5000
   sudo kill -9 <PID>
   ```

### 浏览器未自动打开

手动访问：`http://localhost:5000`

---

## 🗂️ 文件说明

```
dltools_web/
├── start_desktop.sh           # 一键启动脚本（推荐）
├── stop.sh                    # 停止脚本
├── manage.sh                  # 管理脚本
├── install_local.sh           # 本地安装脚本
├── AstronomicalImageDownloader.desktop  # 桌面快捷方式
└── dltools-web-user.service   # 用户服务文件（开机自启）
```

---

## 🎯 推荐方案

### 日常使用（推荐）

```bash
# 首次安装
./install_local.sh

# 之后直接用
dltools-start   # 启动
dltools-stop    # 停止
```

或双击桌面图标

### 开机自启

```bash
# 设置开机自启
systemctl --user enable dltools-web-user
systemctl --user start dltools-web-user

# 之后开机自动运行，访问 http://localhost:5000
```

---

## 🆘 常见问题

### Q: 如何知道服务是否在运行？

```bash
dltools status
```

或检查端口：
```bash
netstat -tulpn | grep 5000
```

### Q: 如何关闭服务？

```bash
dltools-stop
```

或：
```bash
./stop.sh
```

### Q: 如何查看日志？

```bash
dltools log
```

或：
```bash
tail -f /tmp/dltools.log
```

### Q: 命令找不到？

运行以下命令重新加载配置：
```bash
source ~/.bashrc
```

或重新安装：
```bash
./install_local.sh
```

---

## 📝 快速参考

| 操作 | 命令 |
|------|------|
| 一键启动 | `dltools-start` |
| 停止服务 | `dltools-stop` |
| 查看状态 | `dltools status` |
| 打开浏览器 | `dltools open` |
| 查看日志 | `dltools log` |

---

**享受便捷的天文图像下载体验！** 🚀
