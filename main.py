#!/usr/bin/env python3

"""
Main Application Entry Point

This module serves as the primary entry point for the PyMOO GUI application.
It initializes the Qt application framework, configures application-level
settings, and launches the main user interface.

Application Configuration:
- Sets application metadata (name, version, organization)
- Configures the visual style theme (Fusion for modern appearance)
- Initializes the main window and event loop

Dependencies:
- PyQt6: GUI framework for cross-platform desktop applications
- Custom UI modules: Main window and associated components
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow

def main():
    """
    Initialize and launch the PyMOO GUI application.
    
    This function performs the complete application startup sequence:
    1. Creates the Qt application instance
    2. Sets application metadata and styling preferences
    3. Instantiates and displays the main window
    4. Enters the Qt event loop for user interaction
    
    The application will continue running until the user closes the main window
    or terminates the process through the operating system.
    """
    # Initialize Qt application framework
    app = QApplication(sys.argv)
    
    # Configure application metadata for system integration
    app.setApplicationName("PyMOO GUI")
    app.setApplicationVersion("1.3.2")
    app.setOrganizationName("Elias Rizos [it21490]")
    
    # Set visual style theme for consistent modern appearance
    app.setStyle('Fusion')
    
    # Create and display main application window
    window = MainWindow()
    window.show()
    
    # Enter Qt event loop and handle application exit
    sys.exit(app.exec())

# Execute main function when script is run directly
if __name__ == "__main__":
    main()