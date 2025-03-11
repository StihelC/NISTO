import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.main_window import MainWindow  # Absolute import
from utils.logger import logger
from utils.init_resources import init_resources

def check_resources():
    """Check if resources are available and print their locations."""
    print("Checking resource availability...")
    import os
    from utils.resource_path import get_resource_path
    
    # Check for device icons
    device_types = ["router", "switch", "firewall", "server", "workstation", "cloud"]
    
    for device_type in device_types:
        icon_path = get_resource_path(f"resources/device_icons/{device_type}.png")
        if os.path.exists(icon_path):
            print(f"✅ {device_type} icon found: {icon_path}")
        else:
            print(f"❌ {device_type} icon NOT found: {icon_path}")
    
    print("Resource check complete")

def main():
    """Main application entry point."""
    logger.info("Starting Network Topology Designer")
    
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Initialize resources
    init_resources()
    
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