from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QColorDialog
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class BoundaryDialog(QDialog):
    """Dialog for configuring boundary properties."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Boundary")
        self.setMinimumWidth(350)
        
        # Default values
        self.boundary_name = "Boundary"
        self.boundary_type = "area"
        self.boundary_color = QColor(200, 200, 255, 50)
        
        # Create UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Form layout
        form = QFormLayout()
        
        # Boundary name
        self.name_edit = QLineEdit(self.boundary_name)
        form.addRow("Name:", self.name_edit)
        
        # Boundary type dropdown
        self.type_combo = QComboBox()
        self.type_combo.addItem("Area", "area")
        self.type_combo.addItem("Department", "department")
        self.type_combo.addItem("Network Segment", "network_segment")
        self.type_combo.addItem("Security Zone", "security_zone")
        self.type_combo.addItem("Cloud", "cloud")
        self.type_combo.addItem("Custom", "custom")
        form.addRow("Type:", self.type_combo)
        
        # Color selection
        color_layout = QHBoxLayout()
        
        # Color preview
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(24, 24)
        self.update_color_preview()
        
        # Color button
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self.choose_color)
        
        color_layout.addWidget(self.color_preview)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        
        form.addRow("Color:", color_layout)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("Add Boundary")
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def update_color_preview(self):
        """Update the color preview label."""
        self.color_preview.setStyleSheet(
            f"background-color: rgba({self.boundary_color.red()}, "
            f"{self.boundary_color.green()}, {self.boundary_color.blue()}, "
            f"{self.boundary_color.alpha()});"
            f"border: 1px solid black;"
        )
    
    def choose_color(self):
        """Open color dialog to choose boundary color."""
        color = QColorDialog.getColor(
            self.boundary_color, 
            self, 
            "Choose Boundary Color",
            QColorDialog.ShowAlphaChannel
        )
        
        if color.isValid():
            self.boundary_color = color
            self.update_color_preview()
    
    def get_boundary_properties(self):
        """Return the configured boundary properties."""
        return {
            "name": self.name_edit.text(),
            "type": self.type_combo.currentData(),
            "color": self.boundary_color
        }