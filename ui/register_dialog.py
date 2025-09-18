"""
User Registration Dialog for PyMOO GUI Multi-User System
========================================================

This module provides user registration functionality for the group decision making system.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QPushButton, QLabel, QGroupBox,
                            QComboBox, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class RegisterDialog(QDialog):
    """
    User registration dialog for new users
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register New User - PyMOO GUI")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        self.user_data = None
        
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Register New User")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Registration form
        form_group = QGroupBox("User Information")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)
        
        # Full name
        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText("Enter full name")
        self.full_name_edit.setStyleSheet(self._get_input_style())
        form_layout.addRow("Full Name:", self.full_name_edit)
        
        # Username
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        self.username_edit.setStyleSheet(self._get_input_style())
        form_layout.addRow("Username:", self.username_edit)
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setStyleSheet(self._get_input_style())
        form_layout.addRow("Password:", self.password_edit)
        
        # Confirm password
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setPlaceholderText("Confirm password")
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit.setStyleSheet(self._get_input_style())
        form_layout.addRow("Confirm Password:", self.confirm_password_edit)
        
        # Role selection
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        self.role_combo.setCurrentText("user")  # Default to user
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
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.register_button.setDefault(True)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
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
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.register_button)
        
        layout.addLayout(button_layout)
        
        # Info text
        info_label = QLabel("""
        <b>Registration Notes:</b><br>
        • Username must be unique<br>
        • Password should be at least 6 characters<br>
        • Admin role allows full GUI access<br>
        • User role allows criteria comparison input only
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
        
    def _get_input_style(self):
        """Get consistent input field styling"""
        return """
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """
        
    def _connect_signals(self):
        """Connect UI signals to slots"""
        self.register_button.clicked.connect(self._handle_register)
        self.cancel_button.clicked.connect(self.reject)
        self.confirm_password_edit.returnPressed.connect(self._handle_register)
        
    def _handle_register(self):
        """Handle user registration"""
        # Get form data
        full_name = self.full_name_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        role = self.role_combo.currentText()
        
        # Validate input
        if not self._validate_input(full_name, username, password, confirm_password):
            return
            
        # Store user data
        self.user_data = {
            "full_name": full_name,
            "username": username,
            "password": password,
            "role": role
        }
        
        self.accept()
        
    def _validate_input(self, full_name, username, password, confirm_password):
        """Validate registration input"""
        # Check required fields
        if not full_name:
            self._show_error("Please enter your full name.")
            self.full_name_edit.setFocus()
            return False
            
        if not username:
            self._show_error("Please enter a username.")
            self.username_edit.setFocus()
            return False
            
        if len(username) < 3:
            self._show_error("Username must be at least 3 characters long.")
            self.username_edit.setFocus()
            return False
            
        if not password:
            self._show_error("Please enter a password.")
            self.password_edit.setFocus()
            return False
            
        if len(password) < 6:
            self._show_error("Password must be at least 6 characters long.")
            self.password_edit.setFocus()
            return False
            
        if password != confirm_password:
            self._show_error("Passwords do not match.")
            self.confirm_password_edit.setFocus()
            return False
            
        # Check for invalid characters in username
        if not username.replace("_", "").replace("-", "").isalnum():
            self._show_error("Username can only contain letters, numbers, underscores, and hyphens.")
            self.username_edit.setFocus()
            return False
            
        return True
        
    def _show_error(self, message):
        """Show error message"""
        QMessageBox.critical(self, "Registration Error", message)
        
    def get_user_data(self):
        """Get the registered user data"""
        return self.user_data