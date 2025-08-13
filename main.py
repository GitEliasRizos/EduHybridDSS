#!/usr/bin/env python3
"""
PyMOO GUI - Multi-Objective Optimization Interface
Main application entry point
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("PyMOO GUI")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PyMOO GUI")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
