from PyQt5.QtWidgets import QToolBar, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import os
from utils.resource_path import get_resource_path

class ToolbarManager:
    """Manages toolbar creation and configuration."""
    
    def __init__(self, main_window):
        self.main_window = main_window
        
    def setup_quick_add_toolbar(self):
        """Set up a toolbar with quick-add buttons for common device types."""
        # Create toolbar
        toolbar = QToolBar("Quick Add Devices")
        self.main_window.addToolBar(Qt.TopToolBarArea, toolbar)
        
        # Common device types
        device_types = ["router", "switch", "firewall", "server", "workstation"]
        
        # Add actions for each device type
        for device_type in device_types:
            # Try to load icon
            icon_path = get_resource_path(f"resources/device_icons/{device_type}.png")
            action = QAction(device_type.capitalize(), self.main_window)
            
            if os.path.exists(icon_path):
                action.setIcon(QIcon(icon_path))
            
            # Connect action to lambda function that captures device_type
            action.triggered.connect(
                lambda checked, dt=device_type: self.main_window.set_quick_add_device_mode(dt)
            )
            toolbar.addAction(action)
        
        return toolbar