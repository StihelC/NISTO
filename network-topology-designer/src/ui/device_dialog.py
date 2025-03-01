from PyQt5.QtWidgets import (
    QDialog, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QPushButton, 
    QLineEdit, 
    QFormLayout, 
    QGridLayout,
    QGroupBox, 
    QToolButton
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
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
    def __init__(self, parent=None):
        super(DeviceSelectionDialog, self).__init__(parent)
        self.setWindowTitle("Add Network Device")
        self.setMinimumWidth(400)
        self.setMinimumHeight(350)
        
        # Initialize device registry
        self.device_registry = DeviceRegistry()
        
        # Try to create placeholder icons, but don't let it crash the app
        try:
            self.device_registry.create_placeholder_icons()
        except Exception as e:
            print(f"Error creating placeholder icons: {e}")
            # Continue without icons
        
        # Initialize device selection
        self.selected_device_type = None
        self.device_buttons = {}
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Create the dialog UI with device icons."""
        try:
            main_layout = QVBoxLayout()
            
            # Device type selection group
            device_group = QGroupBox("Select Device Type")
            device_layout = QGridLayout()
            
            # Get device types from registry
            try:
                device_types = self.device_registry.get_device_types()
            except Exception as e:
                print(f"Error getting device types: {e}")
                device_types = [
                    {"type": "router", "name": "Router"},
                    {"type": "switch", "name": "Switch"}
                ]
            
            # Create a button with icon for each device type
            row, col = 0, 0
            max_cols = 3  # 3 columns in the grid
            
            for device in device_types:
                try:
                    # Create device button with vertical layout
                    device_button = QToolButton()
                    device_button.setText(device["name"])
                    device_button.setToolTip(device.get("name", device.get("type", "")))
                    device_button.setCheckable(True)
                    device_button.setMinimumSize(80, 80)
                    device_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                    
                    # Try to load icon if available
                    icon_path = device.get("icon_path")
                    if icon_path and os.path.exists(icon_path):
                        icon = QIcon(icon_path)
                        if not icon.isNull():
                            device_button.setIcon(icon)
                            device_button.setIconSize(QSize(48, 48))
                    
                    # Connect button to selection handler
                    device_info = device  # Create a local copy for the lambda
                    device_button.clicked.connect(lambda checked, d=device_info: self.on_device_selected(d))
                    
                    # Add to layout and store reference
                    device_layout.addWidget(device_button, row, col)
                    self.device_buttons[device["type"]] = device_button
                    
                    # Update grid position
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
                except Exception as e:
                    print(f"Error creating button for device {device.get('type', 'unknown')}: {e}")
                    continue
                    
            device_group.setLayout(device_layout)
            main_layout.addWidget(device_group)
            
            # Device properties form
            props_group = QGroupBox("Device Properties")
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
            
            props_group.setLayout(form_layout)
            main_layout.addWidget(props_group)
            
            # Buttons
            button_layout = QHBoxLayout()
            self.ok_button = QPushButton("Add Device")
            self.ok_button.setEnabled(False)  # Disabled until device selected
            self.ok_button.clicked.connect(self.accept)
            
            self.cancel_button = QPushButton("Cancel")
            self.cancel_button.clicked.connect(self.reject)
            
            button_layout.addWidget(self.ok_button)
            button_layout.addWidget(self.cancel_button)
            main_layout.addLayout(button_layout)
            
            self.setLayout(main_layout)
        except Exception as e:
            print(f"Error setting up device dialog UI: {e}")
            # Create a minimal UI that won't crash
            minimal_layout = QVBoxLayout()
            minimal_layout.addWidget(QLabel("Error loading device selection. Please try again."))
            
            self.cancel_button = QPushButton("Close")
            self.cancel_button.clicked.connect(self.reject)
            minimal_layout.addWidget(self.cancel_button)
            
            self.setLayout(minimal_layout)
    
    def on_device_selected(self, device_info):
        """Handle device type selection."""
        # Uncheck all buttons
        for button in self.device_buttons.values():
            button.setChecked(False)
        
        # Check the selected button
        self.device_buttons[device_info["type"]].setChecked(True)
        
        # Store the selection
        self.selected_device_type = device_info["type"]
        
        # Update the name with a default
        if not self.name_edit.text():
            self.name_edit.setText(f"{device_info['name']}-1")
        
        # Enable the OK button
        self.ok_button.setEnabled(True)
    
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