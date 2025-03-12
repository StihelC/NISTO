from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QComboBox, 
    QPushButton, QLabel, QWidget
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import os

class DeviceSelectionDialog(QDialog):
    """Simple dialog with dropdown for device selection."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Device")
        self.setMinimumWidth(300)
        self.setMinimumHeight(150)
        
        # Store selected device type
        self.selected_device_type = None
        
        # Define available device types
        self.device_types = [
            ("router", "Router"),
            ("switch", "Switch"),
            ("server", "Server"),
            ("firewall", "Firewall"),
            ("workstation", "Workstation"),
            ("cloud", "Cloud Service")
        ]
        
        # Load icons path
        self.icons_dir = self._get_icons_path()
        
        # Set up UI
        self._init_ui()
    
    def _get_icons_path(self):
        """Get path to icons directory."""
        # Try to find resources/icons directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "resources", "icons")
    
    def _init_ui(self):
        """Initialize the dialog UI."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Add instruction label
        label = QLabel("Select device type:")
        layout.addWidget(label)
        
        # Create dropdown
        self.device_dropdown = QComboBox()
        self.device_dropdown.setIconSize(QSize(24, 24))
        
        # Populate dropdown with device types
        for device_type, display_name in self.device_types:
            # Try to load icon
            icon_path = os.path.join(self.icons_dir, f"{device_type}.png")
            if os.path.exists(icon_path):
                self.device_dropdown.addItem(QIcon(icon_path), display_name, device_type)
            else:
                print(f"Icon not found: {icon_path}")
                self.device_dropdown.addItem(display_name, device_type)
        
        layout.addWidget(self.device_dropdown)
        
        # Add spacer
        layout.addStretch(1)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        
        button_layout.addStretch(1)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
    
    def accept(self):
        """Handle dialog acceptance."""
        # Get selected device type
        index = self.device_dropdown.currentIndex()
        if index >= 0:
            self.selected_device_type = self.device_dropdown.itemData(index)
        
        super().accept()
    
    @staticmethod
    def get_device_type(parent=None):
        """Show dialog and return selected device type."""
        dialog = DeviceSelectionDialog(parent)
        
        if dialog.exec_() == QDialog.Accepted:
            return dialog.selected_device_type
        return None