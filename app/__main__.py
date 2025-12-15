"""
PekoCMS - Main Entry Point

Usage:
    python -m app
    or
    python app/__main__.py
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.pyside_app import main

if __name__ == '__main__':
    main()
