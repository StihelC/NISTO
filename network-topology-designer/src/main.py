import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
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
    logger.info("Starting Network Topology Designer")
    
    # Initialize resources
    init_resources()
    
    # Check resources first
    check_resources()
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    logger.info("Application window shown")
    return app.exec_()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.exception("Unhandled exception in main")
        raise