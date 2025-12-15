"""Login window for PekoCMS"""
import sys
import os
from PySide6 import QtWidgets, QtCore, QtGui

# Add parent directory to path for db imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import auth_db
from app.utils import get_asset_path
from app.branding import (
    LOGIN_WINDOW_TITLE, LOGIN_WINDOW_HEADING, LOGO_SVG,
    BUTTON_SIGN_IN, BUTTON_SHUTDOWN
)


class LoginWindow(QtWidgets.QMainWindow):
    """Login window with authentication and shutdown button"""
    logged_in = QtCore.Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(LOGIN_WINDOW_TITLE)
        self.setGeometry(100, 100, 500, 300)
        
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setContentsMargins(60, 40, 60, 40)
        
        box = QtWidgets.QFrame()
        box.setFrameShape(QtWidgets.QFrame.StyledPanel)
        box.setFixedWidth(400)
        box_layout = QtWidgets.QVBoxLayout(box)
        
        logo = QtWidgets.QLabel()
        pix = QtGui.QPixmap(get_asset_path(LOGO_SVG))
        if not pix.isNull():
            logo.setPixmap(pix.scaledToHeight(64, QtCore.Qt.SmoothTransformation))
        logo.setAlignment(QtCore.Qt.AlignCenter)
        
        title = QtWidgets.QLabel(LOGIN_WINDOW_HEADING)
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet('font-size:18px; font-weight:600;')
        
        form = QtWidgets.QFormLayout()
        self.username = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow('Username', self.username)
        form.addRow('Password', self.password)
        
        # Buttons layout - Sign In and Shutdown
        btn_layout = QtWidgets.QHBoxLayout()
        
        btn = QtWidgets.QPushButton(BUTTON_SIGN_IN)
        btn.setStyleSheet('font-size: 12px; padding: 8px 24px; background-color: #0078D4; color: white; font-weight: bold;')
        btn.clicked.connect(self.do_login)
        btn_layout.addWidget(btn)
        
        shutdown_btn = QtWidgets.QPushButton(BUTTON_SHUTDOWN)
        shutdown_btn.setStyleSheet('font-size: 12px; padding: 8px 24px; background-color: #D32F2F; color: white; font-weight: bold;')
        shutdown_btn.clicked.connect(self.shutdown_app)
        btn_layout.addWidget(shutdown_btn)
        
        box_layout.addWidget(logo)
        box_layout.addWidget(title)
        box_layout.addLayout(form)
        box_layout.addLayout(btn_layout)
        
        
        # Footer
        from branding import FOOTER_TEXT
        footer = QtWidgets.QLabel(FOOTER_TEXT)
        footer.setAlignment(QtCore.Qt.AlignCenter)
        footer.setStyleSheet('color: gray; font-size: 10px; margin-top: 20px;')
        
        layout.addStretch()
        layout.addWidget(box, 0, QtCore.Qt.AlignHCenter)
        layout.addWidget(footer, 0, QtCore.Qt.AlignHCenter)
        layout.addStretch()
        self.setCentralWidget(w)
    
    def do_login(self):
        """Handle login with username and password"""
        user = auth_db.get_user_by_username(self.username.text())
        if user and auth_db.check_password(user['password'], self.password.text()):
            auth_db.log_event(user['id'], 'login')
            self.logged_in.emit(user)
        else:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Invalid credentials')
    
    def shutdown_app(self):
        """Shutdown the application"""
        QtWidgets.QApplication.quit()
