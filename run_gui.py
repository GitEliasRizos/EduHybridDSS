#!/usr/bin/env python3
"""
Main entry point for the PyMOO GUI application
"""

import sys
from PyQt6.QtWidgets import QApplication

# Import the main window
from ui.main_window import MainWindow

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
