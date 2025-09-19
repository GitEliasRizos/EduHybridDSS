from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QWidget, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.user_manager import UserDatabaseManager

class UserManagementDialog(QDialog):
    """Dialog for admin to manage users"""
    
    def __init__(self, admin_username: str):
        super().__init__()
        self.admin_username = admin_username
        self.user_manager = UserDatabaseManager()
        
        self.setWindowTitle("User Management - Admin Only")
        self.setModal(True)
        self.resize(800, 800)
        
        self.setup_ui()
        self.load_users()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("User Management")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Create user section
        create_group = QGroupBox("Create New User")
        create_layout = QFormLayout()
        
        self.new_username = QLineEdit()
        self.new_username.setPlaceholderText("Enter username")
        create_layout.addRow("Username:", self.new_username)
        
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Enter password")
        create_layout.addRow("Password:", self.new_password)
        
        create_button_layout = QHBoxLayout()
        self.create_button = QPushButton("Create User")
        self.create_button.clicked.connect(self.create_user)
        create_button_layout.addWidget(self.create_button)
        create_button_layout.addStretch()
        
        create_layout.addRow(create_button_layout)
        create_group.setLayout(create_layout)
        layout.addWidget(create_group)
        
        # Users table section
        table_group = QGroupBox("Existing Users")
        table_layout = QVBoxLayout()
        
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["Username", "Role", "Created", "Actions"])
        
        # Make table columns resize properly
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 350)  # Fixed width for actions column
        
        table_layout.addWidget(self.users_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_users)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def create_user(self):
        """Create a new user"""
        username = self.new_username.text().strip()
        password = self.new_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return
            
        if len(password) < 3:
            QMessageBox.warning(self, "Password Error", "Password must be at least 3 characters long.")
            return
            
        if username == self.user_manager.ADMIN_USERNAME:
            QMessageBox.warning(self, "Username Error", "Cannot create user with admin username.")
            return
            
        try:
            if self.user_manager.user_exists(username):
                QMessageBox.warning(self, "User Exists", f"Username '{username}' already exists.")
                return
                
            success = self.user_manager.create_regular_user(username, password, self.admin_username)
            if success:
                QMessageBox.information(self, "Success", f"User '{username}' created successfully.")
                self.new_username.clear()
                self.new_password.clear()
                self.load_users()
            else:
                QMessageBox.warning(self, "Error", "Failed to create user.")
                
        except PermissionError as e:
            QMessageBox.critical(self, "Permission Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def load_users(self):
        """Load and display users in the table"""
        try:
            users = self.user_manager.get_all_users()
            
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                # Username
                self.users_table.setItem(row, 0, QTableWidgetItem(user['username']))
                
                # Role
                role_item = QTableWidgetItem(user['role'])
                if user['role'] == 'admin':
                    role_item.setBackground(Qt.GlobalColor.lightGray)
                self.users_table.setItem(row, 1, role_item)
                
                # Created date
                self.users_table.setItem(row, 2, QTableWidgetItem(user['created_at']))
                
                # Actions - different for main admin vs others
                if user['username'] == self.user_manager.ADMIN_USERNAME:
                    # Main admin - only allow editing own details
                    actions_widget = QWidget()
                    actions_layout = QHBoxLayout(actions_widget)
                    actions_layout.setContentsMargins(5, 2, 5, 2)
                    actions_layout.setSpacing(5)
                    
                    # Main admin label
                    admin_label = QLabel("Main Admin")
                    admin_label.setStyleSheet("color: gray; font-weight: bold; font-style: italic;")
                    actions_layout.addWidget(admin_label)
                    
                    # Edit button for admin
                    edit_button = QPushButton("Edit Profile")
                    edit_button.setFixedSize(80, 25)
                    edit_button.clicked.connect(lambda checked, u=user['username']: self.edit_user(u))
                    edit_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-size: 10px; }")
                    actions_layout.addWidget(edit_button)
                    
                    actions_layout.addStretch()
                    self.users_table.setCellWidget(row, 3, actions_widget)
                    
                else:
                    # Regular users or secondary admins - full control
                    actions_widget = QWidget()
                    actions_layout = QHBoxLayout(actions_widget)
                    actions_layout.setContentsMargins(5, 2, 5, 2)
                    actions_layout.setSpacing(3)
                    
                    # Edit button
                    edit_button = QPushButton("Edit")
                    edit_button.setFixedSize(50, 25)
                    edit_button.clicked.connect(lambda checked, u=user['username']: self.edit_user(u))
                    edit_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-size: 10px; }")
                    actions_layout.addWidget(edit_button)
                    
                    # Reset password button
                    reset_pwd_button = QPushButton("Reset")
                    reset_pwd_button.setFixedSize(50, 25)
                    reset_pwd_button.clicked.connect(lambda checked, u=user['username']: self.reset_password(u))
                    reset_pwd_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-size: 10px; }")
                    actions_layout.addWidget(reset_pwd_button)
                    
                    # Role change button
                    current_role = user['role']
                    new_role = 'user' if current_role == 'admin' else 'admin'
                    role_button = QPushButton(f"→{new_role}")
                    role_button.setFixedSize(50, 25)
                    role_button.clicked.connect(lambda checked, u=user['username'], r=new_role: self.change_role(u, r))
                    role_button.setStyleSheet("QPushButton { background-color: #FF9800; color: white; font-size: 10px; }")
                    actions_layout.addWidget(role_button)
                    
                    # Delete button
                    delete_button = QPushButton("Delete")
                    delete_button.setFixedSize(50, 25)
                    delete_button.clicked.connect(lambda checked, u=user['username']: self.delete_user(u))
                    delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; font-size: 10px; }")
                    actions_layout.addWidget(delete_button)
                    
                    actions_layout.addStretch()
                    self.users_table.setCellWidget(row, 3, actions_widget)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")
    
    def delete_user(self, username: str):
        """Delete a user"""
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete user '{username}'?\n\nThis will also delete all their AHP/TOPSIS data.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.user_manager.delete_user(username, self.admin_username)
                if success:
                    QMessageBox.information(self, "Success", f"User '{username}' deleted successfully.")
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete user.")
                    
            except PermissionError as e:
                QMessageBox.critical(self, "Permission Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def edit_user(self, username: str):
        """Edit user - routes to appropriate method based on user type"""
        # Check if this is the system admin
        if username == self.user_manager.ADMIN_USERNAME:
            self.edit_admin_profile(username)
            return
        
        # Handle regular users
        from PyQt6.QtWidgets import QInputDialog
        
        new_username, ok = QInputDialog.getText(
            self, 
            "Edit Username", 
            f"Enter new username for '{username}':",
            text=username
        )
        
        if ok and new_username.strip():
            new_username = new_username.strip()
            
            if new_username == username:
                return  # No change
            
            if new_username == self.user_manager.ADMIN_USERNAME:
                QMessageBox.warning(self, "Username Error", "Cannot use admin username.")
                return
            
            if self.user_manager.user_exists(new_username):
                QMessageBox.warning(self, "Username Error", f"Username '{new_username}' already exists.")
                return
            
            try:
                success = self.user_manager.update_username(username, new_username, self.admin_username)
                if success:
                    QMessageBox.information(self, "Success", f"Username changed from '{username}' to '{new_username}'.")
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update username.")
            except PermissionError as e:
                QMessageBox.critical(self, "Permission Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def reset_password(self, username: str):
        """Reset a user's password"""
        from PyQt6.QtWidgets import QInputDialog, QLineEdit
        
        new_password, ok = QInputDialog.getText(
            self, 
            "Reset Password", 
            f"Enter new password for '{username}':",
            echo=QLineEdit.EchoMode.Password
        )
        
        if ok and new_password:
            if len(new_password) < 3:
                QMessageBox.warning(self, "Password Error", "Password must be at least 3 characters long.")
                return
            
            try:
                success = self.user_manager.reset_password(username, new_password, self.admin_username)
                if success:
                    QMessageBox.information(self, "Success", f"Password reset for user '{username}'.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to reset password.")
            except PermissionError as e:
                QMessageBox.critical(self, "Permission Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def edit_admin_profile(self, username: str):
        """Edit admin profile (username and password)"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Admin Profile")
        dialog.setModal(True)
        dialog.resize(300, 200)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Current password (for verification)
        current_pwd = QLineEdit()
        current_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        current_pwd.setPlaceholderText("Enter current password")
        form_layout.addRow("Current Password:", current_pwd)
        
        # New username
        new_username = QLineEdit()
        new_username.setText(username)
        form_layout.addRow("New Username:", new_username)
        
        # New password
        new_password = QLineEdit()
        new_password.setEchoMode(QLineEdit.EchoMode.Password)
        new_password.setPlaceholderText("Enter new password (optional)")
        form_layout.addRow("New Password:", new_password)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save Changes")
        cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        def save_changes():
            # Verify current password
            if not self.user_manager.verify_user(username, current_pwd.text()):
                QMessageBox.warning(dialog, "Authentication Failed", "Current password is incorrect.")
                return
            
            changes_made = False
            
            # Update username if changed
            new_user = new_username.text().strip()
            if new_user and new_user != username:
                if self.user_manager.user_exists(new_user) and new_user != username:
                    QMessageBox.warning(dialog, "Username Error", f"Username '{new_user}' already exists.")
                    return
                
                try:
                    success = self.user_manager.update_admin_username(username, new_user, current_pwd.text())
                    if success:
                        changes_made = True
                        # Update the admin_username for this session
                        self.admin_username = new_user
                    else:
                        QMessageBox.warning(dialog, "Error", "Failed to update username.")
                        return
                except Exception as e:
                    QMessageBox.critical(dialog, "Error", f"Failed to update username: {str(e)}")
                    return
            
            # Update password if provided
            if new_password.text():
                if len(new_password.text()) < 3:
                    QMessageBox.warning(dialog, "Password Error", "Password must be at least 3 characters long.")
                    return
                
                try:
                    success = self.user_manager.update_admin_password(self.admin_username, new_password.text(), current_pwd.text())
                    if success:
                        changes_made = True
                        # Update the constant in UserManager
                        self.user_manager.ADMIN_PASSWORD = new_password.text()
                    else:
                        QMessageBox.warning(dialog, "Error", "Failed to update password.")
                        return
                except Exception as e:
                    QMessageBox.critical(dialog, "Error", f"Failed to update password: {str(e)}")
                    return
            
            if changes_made:
                QMessageBox.information(dialog, "Success", "Admin profile updated successfully.")
                self.load_users()
                dialog.accept()
            else:
                dialog.reject()
        
        save_button.clicked.connect(save_changes)
        cancel_button.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def change_role(self, username: str, new_role: str):
        """Change a user's role"""
        current_role = 'admin' if new_role == 'user' else 'user'  # Get current role
        
        reply = QMessageBox.question(
            self, 
            "Confirm Role Change", 
            f"Change user '{username}' from '{current_role}' to '{new_role}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.user_manager.update_user_role(username, new_role, self.admin_username)
                if success:
                    QMessageBox.information(self, "Success", f"User '{username}' role changed to '{new_role}'.")
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Error", "Failed to change user role.")
                    
            except PermissionError as e:
                QMessageBox.critical(self, "Permission Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

# Test the dialog standalone
if __name__ == "__main__":
    import sys
    import os
    from PyQt6.QtWidgets import QApplication
    
    # Add parent directory to path to find auth module
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    app = QApplication(sys.argv)
    
    # Test with admin username
    dialog = UserManagementDialog("admin")
    dialog.exec()