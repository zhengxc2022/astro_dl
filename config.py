"""
Configuration file for Astronomical Image Downloader
You can modify these settings before deployment
"""

import os

# 获取配置文件所在目录（可移植）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    # Server settings
    HOST = '0.0.0.0'  # Listen on all interfaces (change to '127.0.0.1' if using nginx)
    PORT = 5000       # Web server port
    DEBUG = False     # Debug mode (set to True for development)
    
    # Gunicorn settings
    WORKERS = 3       # Number of worker processes (CPU cores * 2 + 1)
    TIMEOUT = 120     # Request timeout in seconds (increase for slow downloads)
    MAX_REQUESTS = 1000  # Restart workers after this many requests (prevent memory leaks)
    
    # Download settings
    DEFAULT_OUTPUT_DIR = './downloads/'  # Default download directory
    MAX_FILE_SIZE = 500 * 1024 * 1024   # 500 MB max file size
    
    # Logging
    LOG_LEVEL = 'info'  # debug, info, warning, error, critical
    ACCESS_LOG = 'access.log'
    ERROR_LOG = 'error.log'
    
    # Security (optional, for future use)
    # SECRET_KEY = 'your-secret-key-here'  # For session management
    # ALLOWED_IPS = ['192.168.1.0/24', '10.0.0.0/8']  # IP whitelist
    
    # External dependencies paths (使用相对路径，可移植)
    DLTOOLS_PATH = os.path.join(SCRIPT_DIR, 'lib')  # Path to DLtools.py
    
    # CASDA (ATNF OPAL) credentials for RACS/EMU downloads
    # Set via environment variables CASDA_USERNAME / CASDA_PASSWORD
    # or fill them in here. Keep this file secure if you hard-code credentials.
    CASDA_USERNAME = os.environ.get('CASDA_USERNAME', '')
    CASDA_PASSWORD = os.environ.get('CASDA_PASSWORD', '')
    
    # Survey-specific settings
    SURVEYS = {
        'lotss': {
            'default_dr': 2,  # Default data release
        },
        'vlass': {
            'default_epoch': 1,  # Default epoch
        },
        'racs': {
            'require_auth': True,  # Requires CASDA authentication
        }
    }


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'debug'


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'info'
    # Increase workers for production
    WORKERS = 5


# Active configuration
config = ProductionConfig()
