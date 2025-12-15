
import sys
import os
import requests
import webbrowser
from packaging import version
from PySide6 import QtCore, QtWidgets

# Current App Version
APP_VERSION = "1.0.0"
GITHUB_REPO = "otus9051/pekocms"

class UpdateCheckerThread(QtCore.QThread):
    """Thread to check for updates in background"""
    update_available = QtCore.Signal(str, str) # version, url
    error_occurred = QtCore.Signal(str)
    
    def run(self):
        try:
            api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                latest_tag = data.get('tag_name', '0.0.0').lstrip('v')
                html_url = data.get('html_url', '')
                
                # Compare versions
                if version.parse(latest_tag) > version.parse(APP_VERSION):
                    self.update_available.emit(latest_tag, html_url)
            else:
                self.error_occurred.emit(f"Failed to check updates: {response.status_code}")
                
        except Exception as e:
            self.error_occurred.emit(str(e))

def check_for_updates_gui(parent):
    """Trigger update check with UI feedback"""
    
    # Progress dialog (optional, or just status bar)
    # For now, we'll silently check or show a message if manually triggered
    
    thread = UpdateCheckerThread(parent)
    
    def on_update(new_ver, url):
        reply = QtWidgets.QMessageBox.question(
            parent, 
            "Update Available",
            f"A new version ({new_ver}) is available!\n\nDo you want to download it now?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            webbrowser.open(url)
            
    thread.update_available.connect(on_update)
    thread.start()
    return thread
