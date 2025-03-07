from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, 
    QDialogButtonBox, QWidget, QApplication, QSizePolicy, QTextEdit  # Add QSizePolicy and QTextEdit here
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
import os

try:
    from utils.device_registry import DeviceRegistry
except ImportError:
    try:
        from src.utils.device_registry import DeviceRegistry
    except ImportError:
        print("Error importing DeviceRegistry. Check your project structure.")
        
        # Fallback minimal implementation
        class DeviceRegistry:
            def __init__(self, icons_dir=None):
                self.icons_dir = icons_dir or "icons"
                
            def get_device_types(self):
                return [
                    {"type": "router", "name": "Router", "icon_path": None},
                    {"type": "switch", "name": "Switch", "icon_path": None}
                ]
                
            def create_placeholder_icons(self):
                pass

class DeviceSelectionDialog(QDialog):
    """Dialog for selecting device type and properties."""
    
    DEVICE_TYPES = [
        "router", "switch", "firewall", "server", 
        "workstation", "cloud", "database", "wireless"
    ]
    
    def __init__(self, parent=None, device=None):
        super().__init__(parent)
        
        # Store reference to existing device (for editing)
        self.device = device
        
        # Set window title and modal behavior
        if device:
            self.setWindowTitle("Edit Device")
        else:
            self.setWindowTitle("Add Device")
        
        self.setModal(True)  # Make dialog modal
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)  # Keep on top
        
        # Set size
        self.resize(400, 300)  # Larger size for better visibility
        
        # Set up the UI
        self.setup_ui()
        
        # Use a timer to ensure the dialog appears
        QTimer.singleShot(100, self.ensure_visible)
    
    def ensure_visible(self):
        """Ensure the dialog is visible and active."""
        self.raise_()  # Bring to front
        self.activateWindow()  # Activate window
        
    def setup_ui(self):
        """Set up the dialog UI."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Device type selection with preview
        type_layout = QHBoxLayout()
        
        # Left side: type selector
        type_form = QFormLayout()
        self.type_combo = QComboBox()
        
        # Populate combo box
        for device_type in self.DEVICE_TYPES:
            self.type_combo.addItem(device_type.capitalize())
        
        # Connect change event
        self.type_combo.currentIndexChanged.connect(self.update_preview)
        
        type_form.addRow("Device Type:", self.type_combo)
        
        # Right side: icon preview
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(64, 64)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid #cccccc; background-color: white;")
        
        type_layout.addLayout(type_form)
        type_layout.addWidget(self.preview_label)
        
        main_layout.addLayout(type_layout)
        
        # Add a line separator
        line = QWidget()
        line.setFixedHeight(1)
        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line.setStyleSheet("background-color: #cccccc;")
        main_layout.addWidget(line)
        
        # Device properties
        properties_group = QWidget()
        properties_layout = QFormLayout(properties_group)
        
        # Device name
        self.name_edit = QLineEdit()
        if self.device and hasattr(self.device, 'properties') and 'name' in self.device.properties:
            self.name_edit.setText(self.device.properties['name'])
        else:
            # Auto-generate a name based on type
            self.name_edit.setText(f"{self.DEVICE_TYPES[0].capitalize()}-1")
            
        properties_layout.addRow("Name:", self.name_edit)
        
        # IP Address
        self.ip_edit = QLineEdit()
        if self.device and hasattr(self.device, 'properties') and 'ip_address' in self.device.properties:
            self.ip_edit.setText(self.device.properties['ip_address'])
        properties_layout.addRow("IP Address:", self.ip_edit)
        
        # Description
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        if self.device and hasattr(self.device, 'properties') and 'description' in self.device.properties:
            self.desc_edit.setText(self.device.properties['description'])
        properties_layout.addRow("Description:", self.desc_edit)
        
        main_layout.addWidget(properties_group)
        
        # Spacer
        main_layout.addStretch(1)
        
        # Standard buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)
        
        # Ensure only one connection for accept/reject
        self.button_box.accepted.disconnect() if self.button_box.receivers(self.button_box.accepted) > 0 else None
        self.button_box.rejected.disconnect() if self.button_box.receivers(self.button_box.rejected) > 0 else None
        
        # Reconnect once
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        # Update the preview
        self.update_preview()
        
        # If editing an existing device, set current type
        if self.device and hasattr(self.device, 'device_type'):
            try:
                index = [t.lower() for t in self.DEVICE_TYPES].index(self.device.device_type.lower())
                self.type_combo.setCurrentIndex(index)
                # Also update the name
                if hasattr(self.device, 'properties') and 'name' in self.device.properties:
                    self.name_edit.setText(self.device.properties['name'])
            except (ValueError, AttributeError) as e:
                print(f"Error setting device type: {e}")
    
    def update_preview(self):
        """Update the icon preview based on selected type."""
        device_type = self.get_device_type().lower()
        
        # Try to find the icon
        from utils.resource_path import get_resource_path
        icon_path = get_resource_path(f"resources/device_icons/{device_type}.png")
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_label.setPixmap(pixmap)
                return
                
        # If icon not found, show text
        self.preview_label.setText(device_type.capitalize())
    
    def get_device_type(self):
        """Get the selected device type."""
        index = self.type_combo.currentIndex()
        if 0 <= index < len(self.DEVICE_TYPES):
            return self.DEVICE_TYPES[index]
        return "router"  # Default
    
    def get_device_name(self):
        """Get the entered device name."""
        name = self.name_edit.text()
        if not name:
            # If empty, generate a default name
            device_type = self.get_device_type()
            name = f"{device_type.capitalize()}-1"
        return name
    
    def get_device_properties(self):
        """Get all entered device properties."""
        return {
            "name": self.get_device_name(),
            "ip_address": self.ip_edit.text(),
            "description": self.desc_edit.toPlainText()
        }
    
    @classmethod
    def get_device(cls, parent=None):
        """Static method to create and show the dialog and return results."""
        dialog = cls(parent)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            device_info = dialog.get_device_properties()
            # Explicitly ensure dialog is deleted
            dialog.deleteLater()  
            return device_info
        
        # Explicitly ensure dialog is deleted
        dialog.deleteLater()
        return None

    def accept(self):
        """Override accept to validate inputs."""
        # Perform any validation here
        device_name = self.get_device_name()
        if not device_name:
            QApplication.beep()
            self.name_edit.setFocus()
            return
        
        # Validation passed, accept the dialog
        super().accept()