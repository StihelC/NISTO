import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_resources():
    """Check if resources are available and print their locations."""
    print("Checking resource availability...")
    import os
    from src.utils.resource_path import get_resource_path
    
    # Check for device icons
    device_types = ["router", "switch", "firewall", "server", "workstation", "cloud"]
    
    for device_type in device_types:
        icon_path = get_resource_path(f"resources/icons/{device_type}.png")
        if os.path.exists(icon_path):
            print(f"✅ {device_type} icon found: {icon_path}")
        else:
            print(f"❌ {device_type} icon NOT found: {icon_path}")
    
    print("Resource check complete")

def main():
    """Main application entry point."""
    logger.info("Starting Network Topology Designer")
    # Create main window class
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Network Topology Designer")
            self.resize(1024, 768)
    
    # Check resources first
    
    # Initialize resources (commented out as it's not defined yet)
    # init_resources()
    
    # Check resources first
    check_resources()
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Network Topology Designer")
    app.setOrganizationName("NISTO")
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    logger.info("Application window shown")
    
    # Start the event loop
    return app.exec_()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.exception("Unhandled exception in main")
        raise