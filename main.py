#!/usr/bin/env python3

"""
Main Application Entry Point with Multi-User Authentication
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox, QMenuBar, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from ui.main_window import MainWindow
from auth.login_dialog import LoginDialog
from auth.user_management_dialog import UserManagementDialog
from core.user_manager import UserDatabaseManager

def main():
    """
    Initialize and launch the PyMOO GUI application with authentication.
    """
    # Initialize Qt application framework
    app = QApplication(sys.argv)
    
    # Configure application metadata for system integration
    app.setApplicationName("PyMOO GUI - Multi-User System")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Elias Rizos [it21490]")
    
    # Set visual style theme for consistent modern appearance
    app.setStyle('Fusion')
    
    # Show login dialog
    login_dialog = LoginDialog()
    
    # Store login result
    user_data = None
    
    def on_login_success(user_info):
        nonlocal user_data
        user_data = user_info
    
    login_dialog.login_successful.connect(on_login_success)
    
    if login_dialog.exec() != LoginDialog.DialogCode.Accepted:
        # User cancelled login
        return
    
    # Check if we got valid login data
    if not user_data:
        QMessageBox.warning(None, "Login Error", "Failed to get user information.")
        return
    
    # Launch appropriate interface based on role
    try:
        if user_data['role'] == "admin":
            # Launch full PyMOO GUI for admin
            window = MainWindow()
            window.setWindowTitle(f"PyMOO GUI - Admin Panel ({user_data['username']})")
            
            # Add user management menu for admin
            menubar = window.menuBar()
            admin_menu = menubar.addMenu("Admin")
            
            user_mgmt_action = QAction("User Management", window)
            user_mgmt_action.triggered.connect(lambda: show_user_management(user_data['username']))
            admin_menu.addAction(user_mgmt_action)
            
            window.show()
            
        else:  # role == "user" or regular user
            # Launch user interface for criteria comparison
            from ui.user_interface import UserInterface
            
            user_window = UserInterface(
                user_data=user_data,  # Pass the complete user data
                db_manager=UserDatabaseManager()
            )
            user_window.show()
            
    except Exception as e:
        QMessageBox.critical(None, "Interface Error", 
                           f"Failed to launch interface: {str(e)}")
        return
    
    def show_user_management(admin_username):
        """Show user management dialog"""
        dialog = UserManagementDialog(admin_username)
        dialog.exec()
    
    # Enter Qt event loop and handle application exit
    sys.exit(app.exec())

# Execute main function when script is run directly
if __name__ == "__main__":
    main()