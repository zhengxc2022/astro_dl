#!/bin/bash
# Deployment script for Astronomical Image Downloader
# For group server deployment

set -e

echo "========================================="
echo "Astronomical Image Downloader Deployment"
echo "========================================="
echo ""

# Configuration
APP_DIR="/home/zhengxc/works/my_script/dltools_web"
SERVICE_NAME="dltools-web"
USER_NAME=$(whoami)
HOST="0.0.0.0"  # Listen on all interfaces (change to 127.0.0.1 if using nginx)
PORT="5000"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Checking Python environment...${NC}"
python3 --version

echo ""
echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"
cd "$APP_DIR"
pip3 install -r requirements.txt --user

echo ""
echo -e "${YELLOW}Step 3: Installing production WSGI server (gunicorn)...${NC}"
pip3 install gunicorn --user

echo ""
echo -e "${YELLOW}Step 4: Creating downloads directory...${NC}"
mkdir -p "$APP_DIR/downloads"
chmod 755 "$APP_DIR/downloads"

echo ""
echo -e "${YELLOW}Step 5: Creating systemd service file...${NC}"
cat > /tmp/dltools-web.service <<EOF
[Unit]
Description=Astronomical Image Downloader Web Service
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$APP_DIR
Environment="PATH=/home/$USER_NAME/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/$USER_NAME/.local/bin/gunicorn \\
    --workers 3 \\
    --bind $HOST:$PORT \\
    --timeout 120 \\
    --access-logfile $APP_DIR/access.log \\
    --error-logfile $APP_DIR/error.log \\
    --log-level info \\
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}Service file created at /tmp/dltools-web.service${NC}"
echo ""
echo -e "${YELLOW}To install as system service, run:${NC}"
echo "  sudo cp /tmp/dltools-web.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable dltools-web"
echo "  sudo systemctl start dltools-web"

echo ""
echo -e "${YELLOW}Step 6: Creating management scripts...${NC}"

# Start script
cat > "$APP_DIR/start_server.sh" <<EOF
#!/bin/bash
cd "$APP_DIR"
gunicorn --workers 3 --bind $HOST:$PORT --timeout 120 --access-logfile access.log --error-logfile error.log --log-level info app:app
EOF
chmod +x "$APP_DIR/start_server.sh"

# Stop script
cat > "$APP_DIR/stop_server.sh" <<'EOF'
#!/bin/bash
pkill -f "gunicorn.*app:app"
echo "Server stopped"
EOF
chmod +x "$APP_DIR/stop_server.sh"

# Status check script
cat > "$APP_DIR/check_status.sh" <<'EOF'
#!/bin/bash
if pgrep -f "gunicorn.*app:app" > /dev/null; then
    echo "✓ Server is running"
    echo "PID: $(pgrep -f 'gunicorn.*app:app')"
    echo "Port: $(netstat -tulpn 2>/dev/null | grep ':5000' || ss -tulpn 2>/dev/null | grep ':5000')"
else
    echo "✗ Server is not running"
fi
EOF
chmod +x "$APP_DIR/check_status.sh"

echo -e "${GREEN}✓ Management scripts created${NC}"
echo "  - start_server.sh"
echo "  - stop_server.sh"
echo "  - check_status.sh"

echo ""
echo -e "${YELLOW}Step 7: Checking firewall...${NC}"
if command -v ufw &> /dev/null; then
    echo "UFW firewall detected"
    echo "If you want to allow access from group network, run:"
    echo "  sudo ufw allow from 192.168.0.0/16 to any port 5000"
    echo "  sudo ufw allow from 10.0.0.0/8 to any port 5000"
fi

echo ""
echo "========================================="
echo -e "${GREEN}Deployment preparation completed!${NC}"
echo "========================================="
echo ""
echo "📋 Next steps:"
echo ""
echo "Option 1: Run directly (simple, for testing)"
echo "  cd $APP_DIR"
echo "  ./start_server.sh"
echo ""
echo "Option 2: Install as system service (recommended for production)"
echo "  sudo cp /tmp/dltools-web.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable dltools-web"
echo "  sudo systemctl start dltools-web"
echo "  sudo systemctl status dltools-web"
echo ""
echo "🌐 Access the tool:"
echo "  http://localhost:5000"
echo "  http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "📝 Logs:"
echo "  Access log: $APP_DIR/access.log"
echo "  Error log: $APP_DIR/error.log"
echo ""
