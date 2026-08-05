# 团组服务器部署指南

本文档详细说明如何将 Astronomical Image Downloader 部署到团组服务器。

## 📋 目录

- [前置要求](#前置要求)
- [快速部署](#快速部署)
- [详细步骤](#详细步骤)
- [访问控制](#访问控制)
- [监控与日志](#监控与日志)
- [故障排查](#故障排查)

---

## 前置要求

### 服务器要求
- Linux 服务器（Ubuntu/CentOS 等）
- Python 3.7+
- 至少 2GB 可用磁盘空间
- 网络连接（用于下载天文图像）

### 权限要求
- SSH 访问权限
- Python 包安装权限（`pip install --user`）
- 如需安装系统服务：`sudo` 权限

---

## 快速部署

### 方法一：使用部署脚本（推荐）

```bash
# 1. 上传整个项目到服务器
scp -r /home/zhengxc/works/my_script/dltools_web user@server:/home/user/

# 2. SSH 登录服务器
ssh user@server

# 3. 运行部署脚本
cd /home/user/dltools_web
chmod +x deploy_server.sh
./deploy_server.sh

# 4. 启动服务器
./start_server.sh
```

### 方法二：手动部署

```bash
# 1. 安装依赖
cd /home/user/dltools_web
pip3 install -r requirements.txt --user
pip3 install gunicorn --user

# 2. 创建下载目录
mkdir -p downloads

# 3. 启动服务器
~/.local/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
```

---

## 详细步骤

### 1. 传输项目到服务器

#### 使用 scp
```bash
scp -r /home/zhengxc/works/my_script/dltools_web user@server:/home/user/
```

#### 使用 rsync（推荐，支持增量传输）
```bash
rsync -avz --progress /home/zhengxc/works/my_script/dltools_web/ user@server:/home/user/dltools_web/
```

### 2. 安装依赖

```bash
# 登录服务器
ssh user@server

# 进入项目目录
cd /home/user/dltools_web

# 安装 Python 依赖
pip3 install -r requirements.txt --user

# 安装生产服务器
pip3 install gunicorn --user
```

### 3. 配置输出目录

```bash
# 创建默认下载目录
mkdir -p /home/user/dltools_web/downloads
chmod 755 /home/user/dltools_web/downloads
```

### 4. 启动服务

#### 方式 A：直接运行（适合测试）

```bash
# 前台运行（Ctrl+C 停止）
python3 app.py

# 或使用 gunicorn
~/.local/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
```

#### 方式 B：后台运行（适合临时使用）

```bash
# 使用 nohup 后台运行
nohup ~/.local/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app > server.log 2>&1 &

# 查看日志
tail -f server.log

# 停止服务
pkill -f "gunicorn.*app:app"
```

#### 方式 C：系统服务（推荐，适合生产环境）

```bash
# 创建 systemd 服务文件
sudo nano /etc/systemd/system/dltools-web.service
```

粘贴以下内容：

```ini
[Unit]
Description=Astronomical Image Downloader Web Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/dltools_web
Environment="PATH=/home/your-username/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/your-username/.local/bin/gunicorn \
    --workers 3 \
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    --access-logfile /home/your-username/dltools_web/access.log \
    --error-logfile /home/your-username/dltools_web/error.log \
    --log-level info \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用和启动服务：

```bash
# 重载 systemd 配置
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable dltools-web

# 启动服务
sudo systemctl start dltools-web

# 查看状态
sudo systemctl status dltools-web

# 查看日志
sudo journalctl -u dltools-web -f
```

---

## 访问控制

### 🔒 安全配置（重要！）

默认情况下，服务监听所有网络接口（`0.0.0.0:5000`），这意味着局域网内的任何人都可能访问。建议配置防火墙限制访问。

#### 使用 UFW 防火墙（Ubuntu/Debian）

```bash
# 查看状态
sudo ufw status

# 允许来自特定 IP 段的访问
sudo ufw allow from 192.168.1.0/24 to any port 5000  # 允许 192.168.1.x
sudo ufw allow from 10.0.0.0/8 to any port 5000      # 允许 10.x.x.x

# 或者允许特定 IP
sudo ufw allow from 192.168.1.100 to any port 5000

# 启用防火墙
sudo ufw enable
```

#### 使用 firewalld（CentOS/RHEL）

```bash
# 开放端口给特定区域
sudo firewall-cmd --permanent --zone=trusted --add-source=192.168.1.0/24
sudo firewall-cmd --permanent --zone=trusted --add-port=5000/tcp

# 重载配置
sudo firewall-cmd --reload
```

#### 使用 iptables

```bash
# 允许特定 IP 段访问
sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 5000 -j ACCEPT

# 保存规则
sudo iptables-save > /etc/iptables/rules.v4
```

### 使用 Nginx 反向代理（可选）

如果服务器已安装 Nginx，可以使用反向代理增强安全性：

```bash
# 安装 Nginx
sudo apt install nginx  # Ubuntu/Debian
# 或
sudo yum install nginx  # CentOS/RHEL

# 复制配置文件
sudo cp /home/user/dltools_web/nginx_config.conf /etc/nginx/sites-available/dltools-web

# 创建软链接
sudo ln -s /etc/nginx/sites-available/dltools-web /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

修改 `app.py`，让 gunicorn 只监听本地：

```python
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)  # 改为 127.0.0.1
```

---

## 监控与日志

### 查看服务状态

```bash
# 使用管理脚本
./check_status.sh

# 或使用 systemctl
sudo systemctl status dltools-web
```

### 查看日志

#### 应用日志
```bash
# 访问日志
tail -f /home/user/dltools_web/access.log

# 错误日志
tail -f /home/user/dltools_web/error.log
```

#### 系统日志
```bash
# 实时查看
sudo journalctl -u dltools-web -f

# 查看最近 100 行
sudo journalctl -u dltools-web -n 100

# 查看今天的日志
sudo journalctl -u dltools-web --since today
```

### 监控资源使用

```bash
# CPU 和内存使用
top -p $(pgrep -f "gunicorn.*app:app")

# 或使用 htop
htop -p $(pgrep -f "gunicorn.*app:app")
```

---

## 故障排查

### 问题 1：端口被占用

```bash
# 查看端口占用
sudo netstat -tulpn | grep :5000
# 或
sudo ss -tulpn | grep :5000

# 结束占用进程
sudo kill -9 <PID>
```

### 问题 2：无法访问服务

检查清单：
- [ ] 服务是否启动：`sudo systemctl status dltools-web`
- [ ] 防火墙是否开放：`sudo ufw status`
- [ ] 端口是否监听：`sudo netstat -tulpn | grep 5000`
- [ ] 检查日志：`tail -f error.log`

### 问题 3：Python 依赖缺失

```bash
# 检查依赖
pip3 list | grep -E "flask|gunicorn|astropy"

# 重新安装
pip3 install -r requirements.txt --user --force-reinstall
```

### 问题 4：下载失败

检查：
- 网络连接是否正常
- 天文数据库服务是否可用
- 查看 `error.log` 获取详细错误信息
- 检查下载目录权限：`ls -ld downloads/`

---

## 性能优化

### 调整 Worker 数量

```bash
# CPU 核心数 * 2 + 1
# 例如 4 核 CPU:
gunicorn --workers 9 --bind 0.0.0.0:5000 app:app
```

### 增加超时时间

```bash
# 适合大文件下载
gunicorn --timeout 300 --bind 0.0.0.0:5000 app:app
```

### 使用多进程模式

```bash
# 预加载应用，减少内存使用
gunicorn --workers 3 --preload --bind 0.0.0.0:5000 app:app
```

---

## 日常维护

### 重启服务

```bash
# 使用 systemctl
sudo systemctl restart dltools-web

# 或使用脚本
./stop_server.sh
./start_server.sh
```

### 更新代码

```bash
# 停止服务
sudo systemctl stop dltools-web

# 更新代码（从本地上传新版本）
rsync -avz --progress /local/path/dltools_web/ user@server:/home/user/dltools_web/

# 重启服务
sudo systemctl start dltools-web
```

### 备份配置

```bash
# 备份下载的文件
tar -czf downloads_backup_$(date +%Y%m%d).tar.gz downloads/

# 备份日志
tar -czf logs_backup_$(date +%Y%m%d).tar.gz *.log
```

---

## 联系与支持

如遇问题，请查看：
1. 应用日志：`error.log`
2. 系统日志：`journalctl -u dltools-web`
3. 项目 README：`README.md`

---

**安全提示**：
- ✅ 限制访问 IP 范围
- ✅ 定期查看访问日志
- ✅ 及时更新依赖包
- ❌ 不要在公网环境直接暴露服务
- ❌ 不要使用 root 用户运行服务
