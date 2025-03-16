import uuid
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtGui import QPen, QPainterPath, QColor
from PyQt5.QtCore import Qt, QPointF

class Connection:
    """Model class for connections between devices."""
    
    def __init__(self, source_device, target_device, connection_type="standard"):
        """Initialize a connection between devices."""
        self.id = str(uuid.uuid4())
        self.source_device = source_device
        self.target_device = target_device
        self.connection_type = connection_type
        self.source_port = None
        self.target_port = None
        self.view = None  # Will be set when view is created
        
        # Properties
        self.properties = {
            'name': f"Connection-{self.id[:4]}",
            'type': connection_type,
            'bandwidth': '1 Gbps',
            'status': 'active'
        }
        
        # Add this connection to both devices
        if source_device:
            source_device.add_connection(self)
        if target_device:
            target_device.add_connection(self)
    
    def set_ports(self, source_port, target_port):
        """Set the source and target ports for this connection."""
        self.source_port = source_port
        self.target_port = target_port
        # Update view if it exists
        if self.view:
            self.view.update_from_model()
    
    def update_property(self, key, value):
        """Update a connection property."""
        self.properties[key] = value
        # Update view if it exists
        if self.view:
            self.view.update_from_model()
    
    def update_position(self):
        """Update connection position based on connected devices."""
        if self.view:
            self.view.update_position()
class ConnectionItem(QGraphicsPathItem):
    """A connection between two network devices."""
    
    def __init__(self, source_device, target_device, source_port=None, target_port=None):
        """Initialize a connection between two devices."""
        super().__init__()
        
        # Store device references
        self.source_device = source_device
        self.target_device = target_device
        self.source_port = source_port
        self.target_port = target_port
        
        # Connection properties
        self.connection_type = "ethernet"
        self.properties = {
            'bandwidth': '1 Gbps',
            'latency': '5 ms',
            'status': 'active',
            'description': ''
        }
        
        # Set appearance
        self.setZValue(-1)  # Ensure connections are below devices
        self.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        
        # Set flags
        self.setFlag(QGraphicsPathItem.ItemIsSelectable)
        
        # Create the path
        self.update_path()
    
    def update_path(self):
        """Update the connection path based on device positions."""
        if not self.source_device or not self.target_device:
            return
        
        # Get connection points
        if self.source_port:
            source_point = self.source_device.get_port_position(self.source_port['name'])
        else:
            source_point = self.source_device.mapToScene(
                QPointF(self.source_device.width / 2, self.source_device.height / 2)
            )
        
        if self.target_port:
            target_point = self.target_device.get_port_position(self.target_port['name'])
        else:
            target_point = self.target_device.mapToScene(
                QPointF(self.target_device.width / 2, self.target_device.height / 2)
            )
        
        # Create path
        path = QPainterPath()
        path.moveTo(source_point)
        
        # Determine if we need to create a curved path
        # For simplicity, let's create a slight curve for all connections
        # In a more advanced implementation, we could detect crossing connections and adjust
        
        # Calculate control points for a Bezier curve
        dx = target_point.x() - source_point.x()
        dy = target_point.y() - source_point.y()
        distance = (dx * dx + dy * dy) ** 0.5
        
        # Control point offsets (adjust these to change curve shape)
        offset_factor = min(40, distance * 0.25)
        
        if abs(dx) > abs(dy):
            # More horizontal than vertical
            ctrl1 = QPointF(source_point.x() + offset_factor, source_point.y())
            ctrl2 = QPointF(target_point.x() - offset_factor, target_point.y())
        else:
            # More vertical than horizontal
            ctrl1 = QPointF(source_point.x(), source_point.y() + offset_factor)
            ctrl2 = QPointF(target_point.x(), target_point.y() - offset_factor)
        
        # Create cubic Bezier curve
        path.cubicTo(ctrl1, ctrl2, target_point)
        
        # Set path
        self.setPath(path)
        
        # Update appearance based on connection type
        self.update_appearance()
    
    def update_appearance(self):
        """Update the connection appearance based on its type and properties."""
        # Default appearance
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        
        # Customize based on connection type
        if self.connection_type == "ethernet":
            pen.setColor(QColor(0, 0, 200))  # Blue
        elif self.connection_type == "fiber":
            pen.setColor(QColor(200, 100, 0))  # Orange
            pen.setWidth(3)
        elif self.connection_type == "wireless":
            pen.setColor(QColor(0, 150, 0))  # Green
            pen.setStyle(Qt.DashLine)
        elif self.connection_type == "wan":
            pen.setColor(QColor(150, 0, 150))  # Purple
            pen.setWidth(3)
        
        # Apply status changes
        if self.properties.get('status') == 'inactive':
            pen.setColor(QColor(150, 150, 150))  # Gray out for inactive
        elif self.properties.get('status') == 'error':
            pen.setColor(QColor(255, 0, 0))  # Red for error
        
        # Apply the pen
        self.setPen(pen)

import uuid

class ConnectionItem:
    """Model class for connections between devices."""
    
    def __init__(self, source_device, target_device, source_port=None, target_port=None):
        """Initialize a connection between devices."""
        # Basic properties
        self.id = str(uuid.uuid4())
        self.source_device = source_device
        self.target_device = target_device
        self.source_port = source_port
        self.target_port = target_port
        self.connection_type = "ethernet"
        
        # Connection properties
        self.properties = {
            'id': self.id,
            'name': f"Connection-{self.id[:4]}",
            'bandwidth': '1 Gbps',
            'latency': '5 ms',
            'status': 'active',
            'description': ''
        }
        
        # Reference to view component
        self.view = None
        
        # Add this connection to both devices
        source_device.add_connection(self)
        target_device.add_connection(self)
    
    def update_property(self, key, value):
        """Update a connection property."""
        self.properties[key] = value
        # Update view if exists
        if self.view:
            self.view.update_appearance()
            
    def update_endpoints(self, source_device=None, target_device=None, 
                        source_port=None, target_port=None):
        """Update the connection endpoints."""
        if source_device:
            self.source_device = source_device
        if target_device:
            self.target_device = target_device
        if source_port:
            self.source_port = source_port
        if target_port:
            self.target_port = target_port
            
        # Update view if exists
        if self.view:
            self.view.update_path()