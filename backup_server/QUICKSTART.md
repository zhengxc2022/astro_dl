# 快速部署参考卡

## 🚀 一键部署

```bash
# 1. 上传到服务器
rsync -avz dltools_web/ user@server:~/dltools_web/

# 2. 登录并安装
ssh user@server
cd ~/dltools_web
make install

# 3. 启动服务
make start

# 4. 检查状态
make status
```

访问: `http://server-ip:5000`

---

## 📋 常用命令

```bash
make install    # 安装依赖
make start      # 启动服务
make stop       # 停止服务
make restart    # 重启服务
make status     # 查看状态
make logs       # 查看日志
make clean      # 清理临时文件
make test       # 测试服务
```

---

## 🔧 systemd 服务（推荐生产环境）

```bash
# 安装为系统服务
make deploy

# 执行以下命令完成部署
sudo cp /tmp/dltools-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable dltools-web
sudo systemctl start dltools-web

# 管理命令
sudo systemctl status dltools-web   # 查看状态
sudo systemctl restart dltools-web  # 重启服务
sudo systemctl stop dltools-web     # 停止服务
sudo journalctl -u dltools-web -f   # 查看日志
```

---

## 🔒 防火墙配置

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow from 192.168.1.0/24 to any port 5000

# firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-source=192.168.1.0/24
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

---

## 📁 目录结构

```
dltools_web/
├── app.py              # Flask 应用
├── config.py           # 配置文件
├── templates/          # HTML 模板
│   └── index.html
├── downloads/          # 默认下载目录
├── access.log          # 访问日志
├── error.log           # 错误日志
├── Makefile            # 管理脚本
└── DEPLOYMENT.md       # 详细部署文档
```

---

## ⚙️ 配置修改

编辑 `config.py`:

```python
# 修改端口
PORT = 8000

# 修改 worker 数量
WORKERS = 5

# 修改默认下载目录
DEFAULT_OUTPUT_DIR = '/data/downloads/'

# 修改超时时间
TIMEOUT = 300  # 5分钟
```

---

## 🐛 故障排查

| 问题 | 解决方案 |
|------|---------|
| 端口被占用 | `sudo lsof -i:5000` 然后结束进程 |
| 无法访问 | 检查防火墙、查看日志 |
| 下载失败 | 查看 `error.log` |
| 依赖缺失 | `make install` 重新安装 |

---

## 📞 获取帮助

- 详细文档: `DEPLOYMENT.md`
- 使用说明: `README.md`
- 日志文件: `tail -f error.log`
