#!/usr/bin/env python3
import sys
import os

# Add the source directory to the Python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                     "network-topology-designer", "src")
sys.path.insert(0, src_dir)

# Import the main function from the main module
# The main function should use controllers.main_window
from controllers.main_window import MainWindow
from PyQt5.QtWidgets import QApplication

def main():
    # Create the application instance
    app = QApplication(sys.argv)
    app.setApplicationName("Network Topology Designer")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())