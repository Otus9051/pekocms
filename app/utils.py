"""Utilities, constants, and helper functions for PekoCMS"""
import sys
import os
from PySide6 import QtGui

# Add parent directory to path for db imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database imports removed to avoid circular dependencies

# Import constants
from app.constants import APP_DATA_NAME, ASSETS_DIRECTORY, INVOICE_FOLDER_NAME, INVOICE_SUBDIRECTORY

# Use APP_DATA_NAME instead of APP_NAME to avoid circular import
APP_NAME = APP_DATA_NAME

# Handle PyInstaller frozen app paths
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_asset_path(filename):
    """Get path to static asset file. 
    If filename is absolute path, return it.
    Otherwise, look in bundled assets directory.
    """
    if os.path.isabs(filename) and os.path.exists(filename):
        return filename
    
    # Use branding constant
    return os.path.join(BASE_PATH, ASSETS_DIRECTORY, filename)

def get_app_data_dir():
    """Get writable application data directory"""
    if getattr(sys, 'frozen', False):
        # In frozen app, use AppData/Local/AppName
        base = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        data_dir = os.path.join(base, APP_NAME)
    else:
        # In dev, use project root
        data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_database_dir():
    """Get database directory"""
    data_dir = get_app_data_dir()
    db_dir = os.path.join(data_dir, 'databases')
    os.makedirs(db_dir, exist_ok=True)
    return db_dir

def get_config_path():
    """Get config file path"""
    if getattr(sys, 'frozen', False):
        # 1. Check next to executable (portable/admin mode)
        exe_dir = os.path.dirname(sys.executable)
        portable_cfg = os.path.join(exe_dir, 'config.yaml')
        if os.path.exists(portable_cfg):
            return portable_cfg
            
        # 2. Check AppData (user overrides)
        app_data_cfg = os.path.join(get_app_data_dir(), 'config.yaml')
        if os.path.exists(app_data_cfg):
            return app_data_cfg
            
        # 3. Fallback to default bundled config (in _MEIPASS)
        return os.path.join(sys._MEIPASS, 'config.yaml')
    else:
        # Dev mode
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.yaml')


def get_invoice_storage_dir():
    """Get invoice storage directory, create if doesn't exist"""
    if getattr(sys, 'frozen', False):
        # In frozen app, use user's documents folder
        invoice_dir = os.path.join(os.path.expanduser('~'), INVOICE_FOLDER_NAME, INVOICE_SUBDIRECTORY)
    else:
        invoice_dir = 'invoice_storage'
    
    os.makedirs(invoice_dir, exist_ok=True)
    return invoice_dir


INVOICE_STORAGE_DIR = get_invoice_storage_dir()
