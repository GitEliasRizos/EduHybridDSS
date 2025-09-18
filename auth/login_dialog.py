from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QMessageBox, 
                             QApplication, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LoginDialog(QDialog):
    """Login dialog for PyMOO GUI multi-user system"""
    
    # Signal emitted when login is successful
    login_successful = pyqtSignal(str, str)  # username, role
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyMOO GUI - Login")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        # Center the dialog on screen
        self.center_on_screen()
        
        self.setup_ui()
        
        # Create default admin user if not exists
        self.ensure_admin_user()
        
    def center_on_screen(self):
        """Center the dialog on the screen"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("PyMOO GUI - Multi-User System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Username field
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        username_label.setMinimumWidth(80)
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText("Enter username")
        self.username_field.setMinimumHeight(30)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_field)
        layout.addLayout(username_layout)
        
        # Password field
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        password_label.setMinimumWidth(80)
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Enter password")
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setMinimumHeight(30)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_field)
        layout.addLayout(password_layout)
        
        # Role selection (for new users)
        role_layout = QHBoxLayout()
        role_label = QLabel("Role:")
        role_label.setMinimumWidth(80)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        self.role_combo.setMinimumHeight(30)
        self.role_combo.setCurrentText("user")
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_combo)
        layout.addLayout(role_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(35)
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.handle_login)
        
        self.register_button = QPushButton("Register")
        self.register_button.setMinimumHeight(35)
        self.register_button.clicked.connect(self.handle_register)
        
        self.exit_button = QPushButton("Exit")
        self.exit_button.setMinimumHeight(35)
        self.exit_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)
        
        # Info text
        info_label = QLabel("Default admin: username='admin', password='admin'")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(info_label)
        
        self.setLayout(layout)
        
        # Connect Enter key to login
        self.username_field.returnPressed.connect(self.handle_login)
        self.password_field.returnPressed.connect(self.handle_login)
        
        # Set focus to username field
        self.username_field.setFocus()
        
    def ensure_admin_user(self):
        """Ensure default admin user exists"""
        try:
            from auth.user_manager import UserManager
            user_manager = UserManager()
            
            # Check if admin exists
            if not user_manager.user_exists('admin'):
                success = user_manager.create_user('admin', 'admin', 'admin')
                if success:
                    print("Default admin user created: username='admin', password='admin'")
        except Exception as e:
            print(f"Warning: Could not create admin user: {e}")
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.username_field.text().strip()
        password = self.password_field.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Error", "Please enter both username and password.")
            return
            
        try:
            from auth.user_manager import UserManager
            user_manager = UserManager()
            
            if user_manager.verify_user(username, password):
                role = user_manager.get_user_role(username)
                self.login_successful.emit(username, role)
                self.accept()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
                self.password_field.clear()
                self.password_field.setFocus()
                
        except Exception as e:
            QMessageBox.critical(self, "Login Error", f"An error occurred during login: {str(e)}")
    
    def handle_register(self):
        """Handle user registration"""
        username = self.username_field.text().strip()
        password = self.password_field.text()
        role = self.role_combo.currentText()
        
        if not username or not password:
            QMessageBox.warning(self, "Registration Error", "Please enter both username and password.")
            return
            
        if len(password) < 3:
            QMessageBox.warning(self, "Registration Error", "Password must be at least 3 characters long.")
            return
            
        try:
            from auth.user_manager import UserManager
            user_manager = UserManager()
            
            if user_manager.user_exists(username):
                QMessageBox.warning(self, "Registration Failed", "Username already exists.")
                return
                
            if user_manager.create_user(username, password, role):
                QMessageBox.information(self, "Registration Successful", 
                                      f"User '{username}' registered successfully with role '{role}'.")
                # Auto-login after registration
                self.login_successful.emit(username, role)
                self.accept()
            else:
                QMessageBox.warning(self, "Registration Failed", "Failed to create user.")
                
        except Exception as e:
            QMessageBox.critical(self, "Registration Error", f"An error occurred during registration: {str(e)}")

# Test the dialog standalone
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    dialog = LoginDialog()
    
    def on_login_success(username, role):
        print(f"Login successful: {username} ({role})")
        app.quit()
    
    dialog.login_successful.connect(on_login_success)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        print("Dialog accepted")
    else:
        print("Dialog rejected")
        app.quit()