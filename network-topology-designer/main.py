#!/usr/bin/env python3
"""
Network Topology Designer - Main Entry Point
"""
import sys
from PyQt5.QtWidgets import QApplication
from src.main_window import MainWindow

def main():
    """
    Initialize the application and start the main event loop.
    """
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
