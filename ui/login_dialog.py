"""
Login Dialog for PyMOO GUI Multi-User System
============================================

This module provides user authentication for the group decision making system:
- Admin users: Full access to PyMOO GUI functionality
- Regular users: Limited access to criteria comparison input only
- Session management and role-based access control
"""

import sys
import hashlib
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QPushButton, QLabel, QGroupBox,
                            QComboBox, QMessageBox, QCheckBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon


class LoginDialog(QDialog):
    """
    Login dialog for multi-user PyMOO GUI system
    
    Features:
    - Admin/User role selection
    - Secure password handling
    - New user registration
    - Session management
    """
    
    # Signals
    login_successful = pyqtSignal(str, str)  # username, role
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PyMOO GUI - User Login")
        self.setFixedSize(400, 350)
        self.setModal(True)
        
        # Center the dialog
        self._center_dialog()
        
        # User data (in production, this would be in a database)
        self.users = {
            "admin": {
                "password": self._hash_password("admin123"),
                "role": "admin",
                "full_name": "System Administrator"
            }
        }
        
        self.current_user = None
        self.current_role = None
        
        self._init_ui()
        self._connect_signals()
        
    def _center_dialog(self):
        """Center the dialog on screen"""
        if self.parent():
            parent_rect = self.parent().geometry()
            center_point = parent_rect.center()
            dialog_rect = self.geometry()
            dialog_rect.moveCenter(center_point)
            self.move(dialog_rect.topLeft())
    
    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("PyMOO GUI Login")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Group Decision Making System")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        layout.addWidget(subtitle_label)
        
        # Login form
        form_group = QGroupBox("User Authentication")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)
        
        # Username
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        self.username_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addRow("Username:", self.username_edit)
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setStyleSheet(self.username_edit.styleSheet())
        form_layout.addRow("Password:", self.password_edit)
        
        # Role selection
        self.role_combo = QComboBox()
        self.role_combo.addItems(["User", "Admin"])
        self.role_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addRow("Role:", self.role_combo)
        
        layout.addWidget(form_group)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setStyleSheet("margin: 5px 0px;")
        layout.addWidget(self.remember_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.register_button = QPushButton("Register New User")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.login_button.setDefault(True)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        button_layout.addWidget(self.register_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.login_button)
        
        layout.addLayout(button_layout)
        
        # Info text
        info_label = QLabel("""
        <b>User Roles:</b><br>
        • <b>Admin:</b> Full access to PyMOO GUI + Group Decision Making<br>
        • <b>User:</b> Limited access to criteria comparisons only
        """)
        info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                font-size: 10px;
                color: #495057;
            }
        """)
        layout.addWidget(info_label)
        
    def _connect_signals(self):
        """Connect UI signals to slots"""
        self.login_button.clicked.connect(self._handle_login)
        self.register_button.clicked.connect(self._handle_register)
        self.cancel_button.clicked.connect(self.reject)
        self.password_edit.returnPressed.connect(self._handle_login)
        self.username_edit.returnPressed.connect(self.password_edit.setFocus)
        
    def _handle_login(self):
        """Handle login attempt"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        role = self.role_combo.currentText().lower()
        
        if not username or not password:
            self._show_error("Please enter both username and password.")
            return
            
        # Validate credentials
        if self._validate_credentials(username, password, role):
            self.current_user = username
            self.current_role = role
            self.login_successful.emit(username, role)
            self.accept()
        else:
            self._show_error("Invalid username, password, or role combination.")
            self.password_edit.clear()
            self.password_edit.setFocus()
    
    def _handle_register(self):
        """Handle new user registration"""
        try:
            from .register_dialog import RegisterDialog
            
            register_dialog = RegisterDialog(self)
            if register_dialog.exec() == QDialog.DialogCode.Accepted:
                user_data = register_dialog.get_user_data()
                self._register_user(user_data)
        except ImportError:
            QMessageBox.warning(self, "Error", "Registration functionality not available.")
    
    def _validate_credentials(self, username, password, role):
        """Validate user credentials"""
        if username not in self.users:
            return False
            
        user_data = self.users[username]
        password_hash = self._hash_password(password)
        
        return (user_data["password"] == password_hash and 
                user_data["role"] == role)
    
    def _register_user(self, user_data):
        """Register a new user"""
        username = user_data["username"]
        
        if username in self.users:
            self._show_error(f"Username '{username}' already exists.")
            return False
            
        # Add user to database (in production, this would be saved to database)
        self.users[username] = {
            "password": self._hash_password(user_data["password"]),
            "role": user_data["role"],
            "full_name": user_data["full_name"]
        }
        
        self._show_success(f"User '{username}' registered successfully!")
        
        # Auto-fill login form
        self.username_edit.setText(username)
        self.role_combo.setCurrentText(user_data["role"].title())
        self.password_edit.setFocus()
        
        return True
    
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _show_error(self, message):
        """Show error message"""
        QMessageBox.critical(self, "Login Error", message)
    
    def _show_success(self, message):
        """Show success message"""
        QMessageBox.information(self, "Success", message)
    
    def get_current_user(self):
        """Get current logged-in user"""
        return self.current_user, self.current_role


class QuickLoginDialog(QDialog):
    """
    Simplified quick login dialog for testing/demo purposes
    """
    
    login_successful = pyqtSignal(str, str)  # username, role
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quick Login - PyMOO GUI")
        self.setFixedSize(300, 200)
        self.setModal(True)
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize quick login UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Quick Login")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Admin button
        admin_button = QPushButton("Login as Admin")
        admin_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        admin_button.clicked.connect(lambda: self._quick_login("admin", "admin"))
        layout.addWidget(admin_button)
        
        # User button
        user_button = QPushButton("Login as User")
        user_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        user_button.clicked.connect(lambda: self._quick_login("user", "user"))
        layout.addWidget(user_button)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)
        
    def _quick_login(self, username, role):
        """Handle quick login"""
        self.login_successful.emit(username, role)
        self.accept()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test the login dialog
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        user, role = login_dialog.get_current_user()
        print(f"Logged in as: {user} ({role})")
    
    app.quit()