from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsItemGroup,
    QGraphicsPixmapItem,
    QGraphicsTextItem,
    QGraphicsRectItem,
    QGraphicsEllipseItem
)
from PyQt5.QtCore import Qt, QPointF, QRectF  # Add QRectF here
from PyQt5.QtGui import QPen, QPixmap, QColor, QBrush, QFont, QPainterPath
import os
import math
from utils.resource_path import get_resource_path

class NetworkDevice(QGraphicsItemGroup):  # Change to QGraphicsItemGroup
    """Represents a network device in the topology."""
    
    def __init__(self, device_type, x, y, size=64, properties=None):
        super().__init__()  # Call the parent constructor
        self.device_type = device_type.lower()
        self.size = size
        self.properties = properties or {}
        self.setPos(x, y)
        
        # Connection tracking
        self.port_connections = {}  # Maps port_id -> list of connections
        
        # Ports dictionary (port_id -> port item)
        self.ports = {}
        
        # Set up the visual appearance
        self.setup_visuals()
        
        # Allow item to be moved by mouse
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
    
    def setup_visuals(self):
        """Set up the visual appearance of the device."""
        from utils.resource_path import get_resource_path
        import os
        
        # Create icon
        icon_path = get_resource_path(f'resources/device_icons/{self.device_type}.png')
        if not os.path.exists(icon_path):
            print(f"Icon not found: {icon_path}, using default")
            icon_path = get_resource_path('resources/device_icons/default.png')
        
        pixmap = QPixmap(icon_path).scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_item = QGraphicsPixmapItem(pixmap)
        self.icon_item.setPos(-self.size/2, -self.size/2)  # Center the icon
        self.addToGroup(self.icon_item)  # This will work now with QGraphicsItemGroup
        
        # Create ports
        self._create_ports()
        
        # Create label for the device name
        from PyQt5.QtWidgets import QGraphicsTextItem
        name = self.properties.get('name', 'Device')
        self.label = QGraphicsTextItem(name)  # Use the passed-in name
        self.label.setPos(-self.label.boundingRect().width()/2, self.size/2)  # Position below the icon
        self.addToGroup(self.label)
        
        # Show label for debugging
        print(f"Created device label with name: {name}")
    
    def _create_ports(self):
        """Create ports around the device."""
        port_size = 8
        device_size = self.size
        
        # Create ports on all four sides
        # Top ports
        for i in range(3):
            port = QGraphicsRectItem(-port_size/2, -device_size/2 - port_size, port_size, port_size)
            port_x = (i - 1) * (device_size/3)
            port.setPos(port_x, 0)
            port.setBrush(QBrush(QColor(50, 150, 255)))  # Blue for port
            port.setPen(QPen(Qt.black, 1))
            port.setVisible(False)  # Initially hidden
            
            # Store port reference with ID
            port_id = f"top_{i}"
            self.ports[port_id] = port
            
            # Store original rect for reset
            port.default_rect = QRectF(port.rect())
            
            # Add to group
            self.addToGroup(port)
        
        # Bottom ports
        for i in range(3):
            port = QGraphicsRectItem(-port_size/2, device_size/2, port_size, port_size)
            port_x = (i - 1) * (device_size/3)
            port.setPos(port_x, 0)
            port.setBrush(QBrush(QColor(50, 150, 255)))  # Blue for port
            port.setPen(QPen(Qt.black, 1))
            port.setVisible(False)  # Initially hidden
            
            # Store port reference with ID
            port_id = f"bottom_{i}"
            self.ports[port_id] = port
            
            # Store original rect for reset
            port.default_rect = QRectF(port.rect())
            
            # Add to group
            self.addToGroup(port)
        
        # Left ports
        for i in range(3):
            port = QGraphicsRectItem(-device_size/2 - port_size, -port_size/2, port_size, port_size)
            port_y = (i - 1) * (device_size/3)
            port.setPos(0, port_y)
            port.setBrush(QBrush(QColor(50, 150, 255)))  # Blue for port
            port.setPen(QPen(Qt.black, 1))
            port.setVisible(False)  # Initially hidden
            
            # Store port reference with ID
            port_id = f"left_{i}"
            self.ports[port_id] = port
            
            # Store original rect for reset
            port.default_rect = QRectF(port.rect())
            
            # Add to group
            self.addToGroup(port)
        
        # Right ports
        for i in range(3):
            port = QGraphicsRectItem(device_size/2, -port_size/2, port_size, port_size)
            port_y = (i - 1) * (device_size/3)
            port.setPos(0, port_y)
            port.setBrush(QBrush(QColor(50, 150, 255)))  # Blue for port
            port.setPen(QPen(Qt.black, 1))
            port.setVisible(False)  # Initially hidden
            
            # Store port reference with ID
            port_id = f"right_{i}"
            self.ports[port_id] = port
            
            # Store original rect for reset
            port.default_rect = QRectF(port.rect())
            
            # Add to group
            self.addToGroup(port)
    
    def get_closest_port(self, scene_pos):
        """Get the closest port to a scene position."""
        device_pos = self.scenePos()
        closest_port = None
        min_distance = float('inf')
        
        for port_id, port in self.ports.items():
            port_scene_pos = self.mapToScene(port.pos())
            dx = scene_pos.x() - port_scene_pos.x()
            dy = scene_pos.y() - port_scene_pos.y()
            distance = (dx*dx + dy*dy)**0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_port = port_id
        
        return closest_port, min_distance
    
    def get_port_position(self, port_id):
        """Get the scene position of a port."""
        if port_id not in self.ports:
            return self.sceneBoundingRect().center()
            
        port = self.ports[port_id]
        port_center = port.sceneBoundingRect().center()
        return port_center
    
    def highlight_port(self, port_id, highlight=True):
        """Highlight a specific port by ID."""
        if port_id not in self.ports:
            return
            
        port = self.ports[port_id]
        
        if highlight:
            # Highlight port - make it bigger and orange
            port.setBrush(QBrush(QColor(255, 165, 0)))  # Orange for highlight
            port.setPen(QPen(Qt.red, 2))
            
            # Make it slightly larger while highlighted
            rect = port.rect()
            center = rect.center()
            
            # Use existing rect to create new one
            new_rect = QRectF(
                center.x() - rect.width() * 0.6,
                center.y() - rect.height() * 0.6,
                rect.width() * 1.2,
                rect.height() * 1.2
            )
            port.setRect(new_rect)
        else:
            # Reset to default appearance
            is_connected = False
            if hasattr(self, 'port_connections') and port_id in self.port_connections:
                is_connected = len(self.port_connections[port_id]) > 0
            
            # Set color based on connection status
            if is_connected:
                port.setBrush(QBrush(QColor(50, 200, 50)))  # Green for connected
            else:
                port.setBrush(QBrush(QColor(50, 150, 255)))  # Blue for available
                
            port.setPen(QPen(Qt.black, 1))
            
            # Reset size to default
            if hasattr(port, 'default_rect'):
                port.setRect(port.default_rect)
    
    def reset_port_highlights(self):
        """Reset all port highlights to default."""
        for port_id in self.ports:
            self.highlight_port(port_id, False)
    
    def show_all_ports(self, visible=True):
        """Make all ports visible/invisible."""
        for port_id, port in self.ports.items():
            if visible:
                # Make ports more prominent
                port.setBrush(QBrush(QColor(50, 150, 255)))  # Blue for available
                port.setPen(QPen(Qt.black, 1))
                port.setVisible(True)
            else:
                # Check if port is connected
                is_connected = False
                if hasattr(self, 'port_connections') and port_id in self.port_connections:
                    is_connected = len(self.port_connections[port_id]) > 0
                
                if is_connected:
                    # Keep connected ports visible but subtle
                    port.setBrush(QBrush(QColor(50, 200, 50)))  # Green for connected
                    port.setPen(QPen(Qt.black, 1))
                    port.setVisible(True)
                else:
                    # Hide unused ports in normal mode
                    port.setVisible(False)
    
    def itemChange(self, change, value):
        """Handle changes to the item."""
        if change == QGraphicsItem.ItemPositionChange:
            # When position changes, update connections
            return value
        
        if change == QGraphicsItem.ItemPositionHasChanged:
            # After position change, update all connections
            self.update_connections()
            return value
        
        return value
    
    def update_connections(self):
        """Update all connections attached to this device."""
        if hasattr(self, 'port_connections'):
            for port_id, connections in self.port_connections.items():
                for connection in connections:
                    if connection:
                        connection.update_path()


