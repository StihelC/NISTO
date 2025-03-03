from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel
)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QPainterPath, QBrush, QColor
import math

class ConnectionPropertiesDialog(QDialog):
    """Dialog for editing connection properties."""
    
    def __init__(self, connection, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle("Connection Properties")
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Connection name
        self.name_edit = QLineEdit(self.connection.properties.get("name", ""))
        form_layout.addRow("Name:", self.name_edit)
        
        # Connection type
        self.type_combo = QComboBox()
        for conn_type in self.connection.CONNECTION_TYPES.keys():
            self.type_combo.addItem(conn_type.capitalize())
        
        # Set current type
        current_index = list(self.connection.CONNECTION_TYPES.keys()).index(self.connection.connection_type)
        self.type_combo.setCurrentIndex(current_index)
        form_layout.addRow("Type:", self.type_combo)
        
        # Source port selection
        self.source_port_combo = QComboBox()
        if self.connection.source_device and hasattr(self.connection.source_device, 'ports'):
            for port_id in self.connection.source_device.ports:
                self.source_port_combo.addItem(port_id)
                
            # Set current source port
            if self.connection.source_port in self.connection.source_device.ports:
                index = list(self.connection.source_device.ports.keys()).index(self.connection.source_port)
                self.source_port_combo.setCurrentIndex(index)
                
        form_layout.addRow("Source Port:", self.source_port_combo)
        
        # Target port selection
        self.target_port_combo = QComboBox()
        if self.connection.target_device and hasattr(self.connection.target_device, 'ports'):
            for port_id in self.connection.target_device.ports:
                self.target_port_combo.addItem(port_id)
                
            # Set current target port
            if self.connection.target_port in self.connection.target_device.ports:
                index = list(self.connection.target_device.ports.keys()).index(self.connection.target_port)
                self.target_port_combo.setCurrentIndex(index)
                
        form_layout.addRow("Target Port:", self.target_port_combo)
        
        # Bandwidth
        self.bandwidth_edit = QLineEdit(self.connection.properties.get("bandwidth", "1 Gbps"))
        form_layout.addRow("Bandwidth:", self.bandwidth_edit)
        
        # Latency
        self.latency_edit = QLineEdit(self.connection.properties.get("latency", "0ms"))
        form_layout.addRow("Latency:", self.latency_edit)
        
        # Description
        self.desc_edit = QLineEdit(self.connection.properties.get("description", ""))
        form_layout.addRow("Description:", self.desc_edit)
        
        # Add form to layout
        layout.addLayout(form_layout)
        
        # Add OK/Cancel buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def accept(self):
        """Update the connection properties when user accepts."""
        # Update connection properties
        self.connection.properties["name"] = self.name_edit.text()
        self.connection.properties["bandwidth"] = self.bandwidth_edit.text()
        self.connection.properties["latency"] = self.latency_edit.text()
        self.connection.properties["description"] = self.desc_edit.text()
        
        # Update ports if they were changed
        if self.source_port_combo.currentText():
            old_source_port = self.connection.source_port
            new_source_port = self.source_port_combo.currentText()
            
            # Only update if changed
            if old_source_port != new_source_port:
                # Remove connection from old port if it exists
                if old_source_port and hasattr(self.connection.source_device, 'port_connections'):
                    if old_source_port in self.connection.source_device.port_connections:
                        if self.connection in self.connection.source_device.port_connections[old_source_port]:
                            self.connection.source_device.port_connections[old_source_port].remove(self.connection)
                            
                        # Reset appearance if no connections left
                        if len(self.connection.source_device.port_connections[old_source_port]) == 0:
                            port = self.connection.source_device.ports.get(old_source_port)
                            if port:
                                port.setBrush(QBrush(QColor(50, 150, 255)))  # Back to default blue
                
                # Update to new port
                self.connection.source_port = new_source_port
                self.connection.properties["source_port"] = new_source_port
                
                # Add connection to new port
                if hasattr(self.connection.source_device, 'add_connection_to_port'):
                    self.connection.source_device.add_connection_to_port(new_source_port, self.connection)
        
        if self.target_port_combo.currentText():
            old_target_port = self.connection.target_port
            new_target_port = self.target_port_combo.currentText()
            
            # Only update if changed
            if old_target_port != new_target_port:
                # Remove connection from old port if it exists
                if old_target_port and hasattr(self.connection.target_device, 'port_connections'):
                    if old_target_port in self.connection.target_device.port_connections:
                        if self.connection in self.connection.target_device.port_connections[old_target_port]:
                            self.connection.target_device.port_connections[old_target_port].remove(self.connection)
                            
                        # Reset appearance if no connections left
                        if len(self.connection.target_device.port_connections[old_target_port]) == 0:
                            port = self.connection.target_device.ports.get(old_target_port)
                            if port:
                                port.setBrush(QBrush(QColor(50, 150, 255)))  # Back to default blue
                
                # Update to new port
                self.connection.target_port = new_target_port
                self.connection.properties["target_port"] = new_target_port
                
                # Add connection to new port
                if hasattr(self.connection.target_device, 'add_connection_to_port'):
                    self.connection.target_device.add_connection_to_port(new_target_port, self.connection)
        
        # Update connection type
        new_type = list(self.connection.CONNECTION_TYPES.keys())[self.type_combo.currentIndex()]
        if new_type != self.connection.connection_type:
            self.connection.connection_type = new_type
            # Update appearance
            style = self.connection.CONNECTION_TYPES[new_type]
            pen = QPen(style["color"], style["width"], style["style"])
            if style["dash"]:
                pen.setDashPattern(style["dash"])
            self.connection.setPen(pen)
        
        # Refresh the connection view
        self.connection.update_path()
        
        super().accept()
    
    @classmethod
    def edit_connection(cls, connection, parent=None):
        """Static method to create the dialog and return updated connection."""
        dialog = cls(connection, parent)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            return True
        return False

class ConnectionManager:
    def create_bezier_path(self, source_device, target_device):
        """Create a smooth Bezier curve path between devices."""
        # Get device centers
        source_center = source_device.sceneBoundingRect().center()
        target_center = target_device.sceneBoundingRect().center()
        
        # Calculate distance between devices
        dx = target_center.x() - source_center.x()
        dy = target_center.y() - source_center.y()
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Create control points for the Bezier curve
        # The control points are placed perpendicular to the direct line
        # This creates a nice curved path
        control_distance = distance * 0.4  # Adjust this factor to change curve intensity
        
        # Calculate perpendicular direction
        angle = math.atan2(dy, dx)
        perp_angle = angle + math.pi/2
        
        # Create control points
        control1 = QPointF(
            source_center.x() + control_distance * math.cos(angle),
            source_center.y() + control_distance * math.sin(angle)
        )
        
        control2 = QPointF(
            target_center.x() - control_distance * math.cos(angle),
            target_center.y() - control_distance * math.sin(angle)
        )
        
        # Create the path
        path = QPainterPath()
        path.moveTo(source_center)
        path.cubicTo(control1, control2, target_center)
        
        return path

    def avoid_crossing(self, path, other_connections):
        """Adjust path to avoid crossing other connections where possible."""
        # This is a complex algorithm - for now we'll just implement a basic version
        # that adjusts the curve intensity based on potential crossings
        
        # In a real implementation, you would need to:
        # 1. Detect potential crossings
        # 2. Use techniques like force-directed layout to adjust control points
        # 3. Implement crossing minimization algorithms
        
        # For now, return the original path
        return path

    def get_optimal_path(self, source_device, target_device):
        """Get the most aesthetically pleasing path between devices."""
        # Start with a bezier path
        path = self.create_bezier_path(source_device, target_device)
        
        # Adjust to avoid crossings with other connections
        path = self.avoid_crossing(path, self.connections)
        
        return path

class NetworkConnection:
    def __init__(self, source_device, target_device):
        self.source_device = source_device
        self.target_device = target_device
        self.update_path = self.update_bezier_path  # Use bezier paths by default

    def update_bezier_path(self):
        """Update the connection with a bezier curve path."""
        if not self.source_device or not self.target_device:
            return
            
        # Get an optimized path from the connection manager
        scene = self.scene()
        if scene:
            # Find the connection manager - this is inefficient and error-prone
            for item in scene.items():
                if hasattr(item, 'connection_manager'):
                    connection_manager = item.connection_manager
                    path = connection_manager.get_optimal_path(self.source_device, self.target_device)
                    self.setPath(path)
                    self.update_label_position()
                    return
        
        # Fallback to direct path if no connection manager found
        source_center = self.source_device.sceneBoundingRect().center()
        target_center = self.target_device.sceneBoundingRect().center()
        
        path = QPainterPath()
        path.moveTo(source_center)
        path.lineTo(target_center)
        self.setPath(path)
        self.update_label_position()
