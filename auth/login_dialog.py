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
    login_successful = pyqtSignal(dict)  # user_data dict
    
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
        
        # Role selection
        role_layout = QHBoxLayout()
        role_label = QLabel("Role:")
        role_label.setMinimumWidth(80)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Admin", "User"])
        self.role_combo.setMinimumHeight(30)
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_combo)
        layout.addLayout(role_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(35)
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.handle_login)
        
        self.exit_button = QPushButton("Exit")
        self.exit_button.setMinimumHeight(35)
        self.exit_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)
        
        # Info text
        
        
        self.setLayout(layout)
        
        # Connect Enter key to login
        self.username_field.returnPressed.connect(self.handle_login)
        self.password_field.returnPressed.connect(self.handle_login)
        
        # Set focus to username field
        self.username_field.setFocus()
        
    def ensure_admin_user(self):
        """Ensure default admin user exists"""
        try:
            from core.user_manager import UserDatabaseManager
            user_manager = UserDatabaseManager()
            # The UserDatabaseManager automatically ensures admin user exists
            print(f"Admin user available: username='{user_manager.ADMIN_USERNAME}', password='{user_manager.ADMIN_PASSWORD}'")
        except Exception as e:
            print(f"Warning: Could not initialize user manager: {e}")
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.username_field.text().strip()
        password = self.password_field.text()
        role = self.role_combo.currentText().lower()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Error", "Please enter both username and password.")
            return
            
        try:
            from core.user_manager import UserDatabaseManager
            user_manager = UserDatabaseManager()
            
            # Use authenticate_user to get complete user data
            user_data = user_manager.authenticate_user(username, password, role)
            
            if user_data:
                self.login_successful.emit(user_data)
                self.accept()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username, password, or role.")
                self.password_field.clear()
                self.password_field.setFocus()
                
        except Exception as e:
            QMessageBox.critical(self, "Login Error", f"An error occurred during login: {str(e)}")

# Test the dialog standalone
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    dialog = LoginDialog()
    
    def on_login_success(user_data):
        print(f"Login successful: {user_data}")
        app.quit()
    
    dialog.login_successful.connect(on_login_success)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        print("Dialog accepted")
    else:
        print("Dialog rejected")
        app.quit()