from PyQt5.QtWidgets import (
    QDialog, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QPushButton, 
    QLineEdit, 
    QFormLayout,
    QComboBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from utils.device_registry import DeviceRegistry

class DeviceSelectionDialog(QDialog):
    """Dialog for selecting and configuring network devices."""
    
    def __init__(self, parent=None):
        super(DeviceSelectionDialog, self).__init__(parent)
        self.setWindowTitle("Add Network Device")
        self.setMinimumWidth(400)
        
        # Initialize device registry
        self.device_registry = DeviceRegistry()
        
        # Initialize device selection
        self.selected_device_type = None
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Create the dialog UI with device dropdown."""
        main_layout = QVBoxLayout()
        
        # Device type selection dropdown
        self.device_type_combo = QComboBox()
        device_types = self.device_registry.get_device_types()
        for device in device_types:
            self.device_type_combo.addItem(device["name"], device["type"])
        
        main_layout.addWidget(QLabel("Select Device Type:"))
        main_layout.addWidget(self.device_type_combo)
        
        # Device properties form
        form_layout = QFormLayout()
        
        # Device name
        self.name_edit = QLineEdit()
        form_layout.addRow("Name:", self.name_edit)
        
        # IP Address
        self.ip_edit = QLineEdit()
        form_layout.addRow("IP Address:", self.ip_edit)
        
        # Description
        self.desc_edit = QLineEdit()
        form_layout.addRow("Description:", self.desc_edit)
        
        main_layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Add Device")
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def get_device_info(self):
        """Return the selected device information."""
        return {
            "type": self.device_type_combo.currentData(),
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
            device_info = dialog.get_device_info()
            # Explicitly ensure dialog is deleted
            dialog.deleteLater()  
            return device_info
        
        # Explicitly ensure dialog is deleted
        dialog.deleteLater()
        return None

    def accept(self):
        """Override accept to validate before closing."""
        # You can add validation here if needed
        super().accept()