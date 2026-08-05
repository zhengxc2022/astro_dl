# Makefile for Astronomical Image Downloader
# Simplify common operations

.PHONY: help install start stop restart status logs clean deploy

# Default target
help:
	@echo "Astronomical Image Downloader - Available Commands:"
	@echo ""
	@echo "  make install    - Install Python dependencies"
	@echo "  make start      - Start the web server"
	@echo "  make stop       - Stop the web server"
	@echo "  make restart    - Restart the web server"
	@echo "  make status     - Check server status"
	@echo "  make logs       - View live logs"
	@echo "  make clean      - Remove temporary files and logs"
	@echo "  make test       - Test server connection"
	@echo "  make deploy     - Deploy to production (systemd)"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip3 install -r requirements.txt --user
	pip3 install gunicorn --user
	@echo "✓ Installation complete"

# Start server in background
start:
	@echo "Starting server..."
	@if pgrep -f "gunicorn.*app:app" > /dev/null; then \
		echo "Server is already running"; \
	else \
		mkdir -p downloads; \
		nohup ~/.local/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 --timeout 120 --access-logfile access.log --error-logfile error.log --log-level info app:app > server.log 2>&1 & \
		sleep 2; \
		if pgrep -f "gunicorn.*app:app" > /dev/null; then \
			echo "✓ Server started on http://0.0.0.0:5000"; \
			echo "  PID: $$(pgrep -f 'gunicorn.*app:app')"; \
		else \
			echo "✗ Failed to start server"; \
		fi \
	fi

# Stop server
stop:
	@echo "Stopping server..."
	@if pgrep -f "gunicorn.*app:app" > /dev/null; then \
		pkill -f "gunicorn.*app:app"; \
		sleep 1; \
		echo "✓ Server stopped"; \
	else \
		echo "Server is not running"; \
	fi

# Restart server
restart: stop
	@sleep 1
	@$(MAKE) start

# Check server status
status:
	@echo "Checking server status..."
	@if pgrep -f "gunicorn.*app:app" > /dev/null; then \
		echo "✓ Server is running"; \
		echo "  PID: $$(pgrep -f 'gunicorn.*app:app')"; \
		echo "  Port: $$(netstat -tulpn 2>/dev/null | grep ':5000' || ss -tulpn 2>/dev/null | grep ':5000')"; \
	else \
		echo "✗ Server is not running"; \
	fi

# View logs in real-time
logs:
	@echo "Viewing logs (Ctrl+C to exit)..."
	@if [ -f access.log ]; then \
		tail -f access.log error.log; \
	else \
		echo "No log files found. Start the server first."; \
	fi

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	rm -f access.log error.log server.log nohup.out
	rm -f tmpSMSS*.csv
	@echo "✓ Cleanup complete"

# Test server
test:
	@echo "Testing server..."
	python3 test_server.py

# Deploy as systemd service (requires sudo)
deploy:
	@echo "Deploying as systemd service..."
	@if [ ! -f /etc/systemd/system/dltools-web.service ]; then \
		echo "Creating systemd service..."; \
		echo "[Unit]" > /tmp/dltools-web.service; \
		echo "Description=Astronomical Image Downloader Web Service" >> /tmp/dltools-web.service; \
		echo "After=network.target" >> /tmp/dltools-web.service; \
		echo "" >> /tmp/dltools-web.service; \
		echo "[Service]" >> /tmp/dltools-web.service; \
		echo "Type=simple" >> /tmp/dltools-web.service; \
		echo "User=$$(whoami)" >> /tmp/dltools-web.service; \
		echo "WorkingDirectory=$$(pwd)" >> /tmp/dltools-web.service; \
		echo "Environment=\"PATH=$$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin\"" >> /tmp/dltools-web.service; \
		echo "ExecStart=$$HOME/.local/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 --timeout 120 --access-logfile $$(pwd)/access.log --error-logfile $$(pwd)/error.log --log-level info app:app" >> /tmp/dltools-web.service; \
		echo "Restart=always" >> /tmp/dltools-web.service; \
		echo "RestartSec=10" >> /tmp/dltools-web.service; \
		echo "" >> /tmp/dltools-web.service; \
		echo "[Install]" >> /tmp/dltools-web.service; \
		echo "WantedBy=multi-user.target" >> /tmp/dltools-web.service; \
		echo ""; \
		echo "Run the following commands to complete deployment:"; \
		echo "  sudo cp /tmp/dltools-web.service /etc/systemd/system/"; \
		echo "  sudo systemctl daemon-reload"; \
		echo "  sudo systemctl enable dltools-web"; \
		echo "  sudo systemctl start dltools-web"; \
	else \
		echo "Service already exists. Use 'sudo systemctl restart dltools-web' to restart."; \
	fi
