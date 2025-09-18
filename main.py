#!/usr/bin/env python3

"""
Main Application Entry Point with Multi-User Authentication

This module serves as the primary entry point for the PyMOO GUI application
with multi-user group decision making capabilities. It initializes the Qt 
application framework, handles user authentication, and launches the 
appropriate interface based on user role.

Application Configuration:
- Sets application metadata (name, version, organization)
- Configures the visual style theme (Fusion for modern appearance)
- Handles user authentication and role-based access control
- Initializes the appropriate interface (admin or user)

User Roles:
- Admin: Full access to PyMOO GUI + Group Decision Making
- User: Limited access to criteria comparison input only

Dependencies:
- PyQt6: GUI framework for cross-platform desktop applications
- Custom UI modules: Main window, login dialog, user interface
- Core modules: User database manager
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
from auth.login_dialog import LoginDialog
from ui.group_decision.user_interface import UserInterface
from ui.group_decision.group_decision_tab import GroupDecisionTab

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
    username = None
    role = None
    
    def on_login_success(user, user_role):
        nonlocal username, role
        username = user
        role = user_role
    
    login_dialog.login_successful.connect(on_login_success)
    
    if login_dialog.exec() != LoginDialog.DialogCode.Accepted:
        # User cancelled login
        return
    
    # Check if we got valid login data
    if not username or not role:
        QMessageBox.warning(None, "Login Error", "Failed to get user information.")
        return
    
    # Launch appropriate interface based on role
    try:
        if role == "admin":
            # Launch full PyMOO GUI with group decision making
            window = MainWindow()
            
            # Add group decision making tab to the admin interface
            group_tab = GroupDecisionTab()
            window.tab_widget.addTab(group_tab, "Group Decision Making")
            
            window.setWindowTitle(f"PyMOO GUI - Admin Panel ({username})")
            window.show()
            
        else:  # role == "user" or regular user
            # Launch simplified user interface
            window = UserInterface(username, role)
            window.show()
            
    except Exception as e:
        QMessageBox.critical(None, "Interface Error", 
                           f"Failed to launch interface: {str(e)}")
        return
    
    # Enter Qt event loop and handle application exit
    sys.exit(app.exec())

# Execute main function when script is run directly
if __name__ == "__main__":
    main()