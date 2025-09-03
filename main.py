#!/usr/bin/env python3

# ELI5: This is like the "power button" for our optimization app!
# When you run this file, it starts the whole application.

# Import statements - like getting tools from different toolboxes
import sys  # System tools (like getting command line arguments)
from PyQt6.QtWidgets import QApplication  # The main app container
from PyQt6.QtCore import Qt  # Qt framework basics
from ui.main_window import MainWindow  # Our app's main window

def main():
    """
    ELI5: This is like setting up a lemonade stand!
    We prepare everything we need, then open for business.
    """
    # Create the application - like setting up the lemonade stand structure
    app = QApplication(sys.argv)
    
    # Give our app a name and version - like putting up a sign
    app.setApplicationName("PyMOO GUI")  # What people see in their taskbar
    app.setApplicationVersion("1.3.2")   # Which version this is
    app.setOrganizationName("Elias Rizos [it21490]")  # Who made this
    
    # Make it look nice - like choosing a good tablecloth
    app.setStyle('Fusion')  # Makes buttons and windows look modern
    
    # Create our main window - like setting up the actual lemonade counter
    window = MainWindow()
    window.show()  # Open the stand for customers!
    
    # Keep the app running until someone closes it
    # Like staying at the lemonade stand until closing time
    sys.exit(app.exec())

# ELI5: This checks "am I the main file being run?"
# If yes, start the app! If no (someone imported this), don't start yet.
if __name__ == "__main__":
    main()