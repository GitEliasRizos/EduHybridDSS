#!/usr/bin/env python3
"""
Test script specifically for the MCDA tab functionality
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

# Import the MCDA tab
from ui.mcda_tab import MCDATab

def main():
    """Test the MCDA tab independently"""
    app = QApplication(sys.argv)
    
    # Create a simple window to hold the MCDA tab
    window = QMainWindow()
    window.setWindowTitle("MCDA Tab Test")
    window.resize(1200, 800)
    
    # Create the central widget
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Create and add the MCDA tab
    mcda_tab = MCDATab()
    layout.addWidget(mcda_tab)
    
    window.setCentralWidget(central_widget)
    window.show()
    
    print("MCDA Tab test window opened!")
    print("Click 'Test with Demo Data' to load sample data and test the functionality.")
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
