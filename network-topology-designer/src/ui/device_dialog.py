from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QListWidget, QListWidgetItem, 
                            QLineEdit, QFormLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class DeviceSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super(DeviceSelectionDialog, self).__init__(parent)
        self.setWindowTitle("Add Network Device")
        self.setMinimumWidth(300)
        self.setMinimumHeight(350)
        
        # Initialize device selection
        self.selected_device_type = None
        self.device_name = ""
        self.device_properties = {}
        
        # Set up the UI
        self.setup_ui()
        
    def setup_ui(self):
        """Create the dialog UI elements."""
        layout = QVBoxLayout()
        
        # Device type selection
        label = QLabel("Select Device Type:")
        layout.addWidget(label)
        
        # List of device types
        self.device_list = QListWidget()
        self.populate_device_list()
        self.device_list.setCurrentRow(0)  # Select first item by default
        self.device_list.itemClicked.connect(self.on_device_selected)
        layout.addWidget(self.device_list)
        
        # Device properties form
        form_layout = QFormLayout()
        
        # Device name
        self.name_edit = QLineEdit()
        form_layout.addRow("Device Name:", self.name_edit)
        
        # IP Address (optional)
        self.ip_edit = QLineEdit()
        form_layout.addRow("IP Address:", self.ip_edit)
        
        # Description (optional)
        self.desc_edit = QLineEdit()
        form_layout.addRow("Description:", self.desc_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def populate_device_list(self):
        """Add available device types to the list."""
        device_types = [
            {"name": "Router", "icon": "router.png"},
            {"name": "Switch", "icon": "switch.png"},
            {"name": "Server", "icon": "server.png"},
            {"name": "Firewall", "icon": "firewall.png"},
            {"name": "Desktop", "icon": "desktop.png"}
        ]
        
        for device in device_types:
            item = QListWidgetItem(device["name"])
            # You can add icons here once you have them
            # item.setIcon(QIcon(f"resources/icons/{device['icon']}"))
            self.device_list.addItem(item)
    
    def on_device_selected(self, item):
        """Handle device type selection."""
        self.selected_device_type = item.text().lower()
        # You could update the form fields based on the device type
        self.name_edit.setText(f"{item.text()}-1")
    
    def get_device_info(self):
        """Return the selected device information."""
        return {
            "type": self.selected_device_type,
            "name": self.name_edit.text(),
            "ip": self.ip_edit.text(),
            "description": self.desc_edit.text()
        }
    
    @classmethod
    def get_device(cls, parent=None):
        """Static method to create and show the dialog and return results."""
        dialog = cls(parent)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            return dialog.get_device_info()
        return None