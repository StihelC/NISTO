#!/usr/bin/env python3
"""
Network Topology Designer - Main Entry Point
"""
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to enable relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now import modules
from src.controllers.main_window import MainWindow
from src.utils.resource_path import get_resource_path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

def init_resources():
    """Initialize application resources."""
    try:
        # Try to import resources module if available
        try:
            import resources_rc
            logger.info("Qt resources initialized successfully")
        except ImportError:
            logger.warning("Qt resources module not found. Using filesystem resources.")
    except Exception as e:
        logger.error(f"Error initializing resources: {e}")

def check_resources():
    """Check if required resources are available."""
    # Check for device icons
    device_types = ["router", "switch", "firewall", "server", "workstation", "cloud"]
    
    for device_type in device_types:
        icon_path = get_resource_path(f"icons/{device_type}.png")
        if os.path.exists(icon_path):
            logger.info(f"✅ {device_type} icon found: {icon_path}")
        else:
            logger.warning(f"❌ {device_type} icon NOT found: {icon_path}")
    
    logger.info("Resource check complete")

def main():
    """Main application entry point."""
    logger.info("Starting Network Topology Designer")
    
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Initialize resources
    init_resources()
    
    # Check resources
    check_resources()
    
    # Create application with explicit args
    app = QApplication(sys.argv)
    app.setApplicationName("Network Topology Designer")
    app.setOrganizationName("NISTO")
    
    # Create and show main window with try/except
    try:
        logger.info("Creating main window...")
        main_window = MainWindow()
        logger.info("Showing main window...")
        main_window.show()
        logger.info("Main window shown successfully")
        
        # Process some events to ensure window appears
        app.processEvents()
        
    except Exception as e:
        logger.exception("Error creating or showing main window")
        return 1
    
    # Log before entering event loop
    logger.info("Entering Qt event loop...")
    
    # Start the event loop
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())