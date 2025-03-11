from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QGroupBox, QSpinBox, QColorDialog,
    QHBoxLayout, QCheckBox
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor

class PropertyEditorFactory:
    """Factory to create property editors based on property type."""
    
    @staticmethod
    def create_editor(property_name, property_value, parent=None):
        """Create an appropriate editor for a property."""
        # Determine editor type based on value type and property name
        if isinstance(property_value, bool):
            # Boolean editor (checkbox)
            editor = QCheckBox(parent)
            editor.setChecked(property_value)
            return editor
        
        elif isinstance(property_value, int):
            # Integer editor (spinbox)
            editor = QSpinBox(parent)
            editor.setMinimum(-1000000)
            editor.setMaximum(1000000)
            editor.setValue(property_value)
            return editor
        
        elif isinstance(property_value, float):
            # Float editor (specialized spinbox)
            from PyQt5.QtWidgets import QDoubleSpinBox
            editor = QDoubleSpinBox(parent)
            editor.setMinimum(-1000000.0)
            editor.setMaximum(1000000.0)
            editor.setValue(property_value)
            return editor
        
        elif property_name.lower().endswith('color'):
            # Color editor (button that opens color dialog)
            button = QPushButton(parent)
            
            # Try to parse the color
            try:
                color = QColor(property_value)
                
                # Set button background to color
                button.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'}")
                button.setText(color.name())
            except:
                button.setText("Select Color")
            
            return button
        
        elif property_name.lower() == 'status' or property_name.lower().endswith('_type'):
            # Enum editor (combobox)
            combo = QComboBox(parent)
            
            # Add standard options based on property name
            if property_name.lower() == 'status':
                options = ["active", "inactive", "error", "warning", "unknown"]
            elif property_name.lower() == 'connection_type':
                options = ["ethernet", "fiber", "wireless", "wan", "serial", "custom"]
            elif property_name.lower() == 'device_type':
                options = ["router", "switch", "server", "client", "firewall", "gateway", "custom"]
            else:
                options = [property_value]
            
            combo.addItems(options)
            
            # Set current value
            index = combo.findText(property_value)
            if index >= 0:
                combo.setCurrentIndex(index)
            
            return combo
        
        else:
            # Default to text editor
            editor = QLineEdit(parent)
            editor.setText(str(property_value))
            return editor
    
    @staticmethod
    def get_editor_value(editor):
        """Get the value from a property editor."""
        if isinstance(editor, QCheckBox):
            return editor.isChecked()
        elif isinstance(editor, QSpinBox):
            return editor.value()
        elif hasattr(editor, 'doubleValue'):  # QDoubleSpinBox
            return editor.value()
        elif isinstance(editor, QComboBox):
            return editor.currentText()
        elif isinstance(editor, QPushButton) and editor.styleSheet():
            # Color button
            return editor.text()  # Returns the color name
        else:
            return editor.text()


class PropertiesPanel(QWidget):
    """Panel for editing properties of selected items."""
    
    # Signal emitted when properties change
    propertiesChanged = pyqtSignal(object, dict)
    
    def __init__(self, parent=None):
        """Initialize the properties panel."""
        super().__init__(parent)
        
        self.current_item = None
        self.editors = {}
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Header label
        self.header_label = QLabel("No Item Selected")
        self.header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(self.header_label)
        
        # Properties form
        self.properties_group = QGroupBox("Properties")
        self.properties_layout = QFormLayout(self.properties_group)
        
        main_layout.addWidget(self.properties_group)
        
        # Initial message when no item is selected
        self.no_selection_label = QLabel("Select an item to edit its properties.")
        self.properties_layout.addRow(self.no_selection_label)
        
        # Button to apply changes
        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply_changes)
        
        main_layout.addWidget(self.apply_button)
        
        # Add stretch to push everything to the top
        main_layout.addStretch()
    
    def set_item(self, item):
        """Set the item whose properties will be edited."""
        self.current_item = item
        self.editors.clear()
        
        # Clear previous form
        while self.properties_layout.rowCount() > 0:
            self.properties_layout.removeRow(0)
        
        if not item:
            # No item selected
            self.header_label.setText("No Item Selected")
            self.no_selection_label = QLabel("Select an item to edit its properties.")
            self.properties_layout.addRow(self.no_selection_label)
            self.apply_button.setEnabled(False)
            return
        
        # Update header
        if hasattr(item, 'device_type'):
            self.header_label.setText(f"{item.device_type.title()} Properties")
        elif hasattr(item, 'connection_type'):
            self.header_label.setText("Connection Properties")
        else:
            self.header_label.setText("Item Properties")
        
        # Add property editors
        if hasattr(item, 'properties') and isinstance(item.properties, dict):
            for name, value in item.properties.items():
                # Skip certain properties
                if name == 'id':
                    label = QLabel(str(value))
                    self.properties_layout.addRow("ID:", label)
                    continue
                
                # Create appropriate editor for the property
                editor = PropertyEditorFactory.create_editor(name, value, self)
                
                # Special handling for color editor
                if isinstance(editor, QPushButton) and name.lower().endswith('color'):
                    # Connect color button to color dialog
                    editor.clicked.connect(
                        lambda checked, btn=editor: self._select_color(btn)
                    )
                
                # Store editor for later retrieval
                self.editors[name] = editor
                
                # Add to form
                self.properties_layout.addRow(f"{name.replace('_', ' ').title()}:", editor)
        
        # Additional properties for specific item types
        if hasattr(item, 'device_type'):
            # Device specific properties
            type_editor = PropertyEditorFactory.create_editor('device_type', item.device_type, self)
            self.editors['device_type'] = type_editor
            self.properties_layout.addRow("Device Type:", type_editor)
        
        elif hasattr(item, 'connection_type'):
            # Connection specific properties
            conn_editor = PropertyEditorFactory.create_editor('connection_type', item.connection_type, self)
            self.editors['connection_type'] = conn_editor
            self.properties_layout.addRow("Connection Type:", conn_editor)
        
        # Enable apply button
        self.apply_button.setEnabled(True)
    
    def _select_color(self, button):
        """Open color dialog when a color button is clicked."""
        # Get current color
        current_color = QColor(button.text())
        
        # Open color dialog
        color = QColorDialog.getColor(
            current_color,
            self,
            "Select Color",
            QColorDialog.ShowAlphaChannel
        )
        
        if color.isValid():
            # Update button
            button.setText(color.name())
            button.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'}")
    
    def apply_changes(self):
        """Apply the edited properties to the current item."""
        if not self.current_item:
            return
        
        # Collect new property values
        new_properties = {}
        
        if hasattr(self.current_item, 'properties') and isinstance(self.current_item.properties, dict):
            # Start with copy of existing properties
            new_properties = self.current_item.properties.copy()
            
            # Update with edited values
            for name, editor in self.editors.items():
                if name in new_properties or name in ('device_type', 'connection_type'):
                    new_properties[name] = PropertyEditorFactory.get_editor_value(editor)
        
        # Update special properties
        if hasattr(self.current_item, 'device_type') and 'device_type' in self.editors:
            device_type = PropertyEditorFactory.get_editor_value(self.editors['device_type'])
            if device_type != self.current_item.device_type:
                # Device type changed - this may require special handling
                # For simplicity, we just update the property here
                self.current_item.device_type = device_type
        
        if hasattr(self.current_item, 'connection_type') and 'connection_type' in self.editors:
            connection_type = PropertyEditorFactory.get_editor_value(self.editors['connection_type'])
            if connection_type != self.current_item.connection_type:
                # Connection type changed
                self.current_item.connection_type = connection_type
                # Update appearance
                if hasattr(self.current_item, 'update_appearance'):
                    self.current_item.update_appearance()
        
        # Emit signal for change
        if new_properties != self.current_item.properties:
            # Clone the old properties
            old_properties = self.current_item.properties.copy()
            
            # For undo/redo - the receiver should create an EditPropertiesCommand
            self.propertiesChanged.emit(self.current_item, new_properties)