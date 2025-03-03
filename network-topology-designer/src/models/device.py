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

class NetworkDevice(QGraphicsItemGroup):
    """Represents a network device on the canvas as a group containing both icon and label."""
    
    # Class-level counter to generate unique names
    device_counts = {}
    
    def __init__(self, device_type, x=0, y=0, size=64):
        """Create a network device with the specified type and position."""
        super().__init__()
        
        self.device_type = device_type
        self.size = size
        
        # Make the group interactive
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # Keep track of device count for this type (for auto-naming)
        if device_type not in self.device_counts:
            self.device_counts[device_type] = 1
        else:
            self.device_counts[device_type] += 1
            
        # Create a default name
        default_name = f"{device_type.capitalize()}{self.device_counts[device_type]}"
        
        # Create the icon item
        self.icon_item = self._create_icon_item()
        self.addToGroup(self.icon_item)
        
        # Create connection ports around the device
        self.ports = self._create_ports()
        
        # Create the label item below the icon
        self.label_item = QGraphicsTextItem()
        self.label_item.setPlainText(default_name)
        self.label_item.setDefaultTextColor(Qt.black)
        
        # Center the label horizontally
        label_width = self.label_item.boundingRect().width()
        label_x = (self.size - label_width) / 2
        self.label_item.setPos(label_x, self.size + 5)
        
        self.addToGroup(self.label_item)
        
        # Position the entire group at the specified coordinates
        self.setPos(x - self.size/2, y - self.size/2)
        
        # Device properties
        self.properties = {
            "name": default_name,
            "ip_address": "",
            "description": ""
        }
        
        # Track connections at each port
        self.port_connections = {port_id: [] for port_id in self.ports}
    
    def _create_icon_item(self):
        """Create a QGraphicsPixmapItem with the device icon."""
        from utils.resource_path import get_resource_path
        
        # Find the icon
        icon_path = get_resource_path(f"resources/device_icons/{self.device_type}.png")
        
        print(f"Looking for icon at: {icon_path}")
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                # Scale the pixmap to our desired size
                pixmap = pixmap.scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_item = QGraphicsPixmapItem(pixmap)
                print(f"Created icon item for {self.device_type}")
                return icon_item
            else:
                print(f"Failed to load pixmap for {self.device_type} from {icon_path}")
        else:
            print(f"Icon not found for {self.device_type} at {icon_path}")
        
        # If we get here, we need a fallback
        print(f"Using fallback icon for {self.device_type}")
        return self._create_fallback_icon()

    def _create_fallback_icon(self):
        """Create a fallback icon when the image isn't available."""
        # Create a rectangle with device type as text
        rect_item = QGraphicsRectItem(0, 0, self.size, self.size)
        
        # Use different colors for different device types
        if self.device_type.lower() == "router":
            rect_item.setBrush(QBrush(QColor(200, 200, 255)))  # Light blue
        elif self.device_type.lower() == "switch":
            rect_item.setBrush(QBrush(QColor(200, 255, 200)))  # Light green
        elif self.device_type.lower() == "firewall":
            rect_item.setBrush(QBrush(QColor(255, 200, 200)))  # Light red
        elif self.device_type.lower() == "server":
            rect_item.setBrush(QBrush(QColor(255, 255, 200)))  # Light yellow
        else:
            rect_item.setBrush(QBrush(QColor(240, 240, 240)))  # Light gray
        
        rect_item.setPen(QPen(Qt.black, 2))
        
        # Add text to the rectangle
        text_item = QGraphicsTextItem(self.device_type.upper())
        text_item.setDefaultTextColor(Qt.black)
        
        # Center the text
        text_width = text_item.boundingRect().width()
        text_height = text_item.boundingRect().height()
        text_x = (self.size - text_width) / 2
        text_y = (self.size - text_height) / 2
        text_item.setPos(text_x, text_y)
        
        # Group the rectangle and text
        group = QGraphicsItemGroup()
        group.addToGroup(rect_item)
        group.addToGroup(text_item)
        
        return group
    
    def _create_ports(self):
        """Create connection ports around the device."""
        port_radius = 6  # Size of port indicators
        
        ports = {}
        # Top ports
        for i in range(2):
            x = self.size * (i+1) / 3
            port = QGraphicsEllipseItem(x-port_radius, -port_radius*2, port_radius*2, port_radius*2, self)
            port.setBrush(QBrush(QColor(50, 150, 255)))  # Blue for available ports
            port.setPen(QPen(Qt.black, 1))
            port.setToolTip(f"Port {i+1} (Top)")
            port.setZValue(10)  # Ensure ports are above other elements
            
            # Store the default rect for size restoration
            port.default_rect = port.rect()
            
            ports[f"top_{i+1}"] = port
            
        # Bottom ports
        for i in range(2):
            x = self.size * (i+1) / 3
            port = QGraphicsEllipseItem(x-port_radius, self.size, port_radius*2, port_radius*2, self)
            port.setBrush(QBrush(QColor(50, 150, 255)))
            port.setPen(QPen(Qt.black, 1))
            port.setToolTip(f"Port {i+1} (Bottom)")
            port.setZValue(10)
            ports[f"bottom_{i+1}"] = port
            
        # Left ports
        for i in range(2):
            y = self.size * (i+1) / 3
            port = QGraphicsEllipseItem(-port_radius*2, y-port_radius, port_radius*2, port_radius*2, self)
            port.setBrush(QBrush(QColor(50, 150, 255)))
            port.setPen(QPen(Qt.black, 1))
            port.setToolTip(f"Port {i+1} (Left)")
            port.setZValue(10)
            ports[f"left_{i+1}"] = port
            
        # Right ports
        for i in range(2):
            y = self.size * (i+1) / 3
            port = QGraphicsEllipseItem(self.size, y-port_radius, port_radius*2, port_radius*2, self)
            port.setBrush(QBrush(QColor(50, 150, 255)))
            port.setPen(QPen(Qt.black, 1))
            port.setToolTip(f"Port {i+1} (Right)")
            port.setZValue(10)
            ports[f"right_{i+1}"] = port
            
        return ports
    
    def update_property(self, key, value):
        """Update a property of the device."""
        if key in self.properties:
            self.properties[key] = value
            if key == "name":
                self.label_item.setPlainText(value)
                # Re-center the label after text change
                label_width = self.label_item.boundingRect().width()
                label_x = (self.size - label_width) / 2
                self.label_item.setPos(label_x, self.size + 5)
    
    def get_port_position(self, port_id):
        """Get the absolute position of a specific port."""
        if port_id not in self.ports:
            # Return center if port doesn't exist
            return self.sceneBoundingRect().center()
            
        port = self.ports[port_id]
        port_rect = port.sceneBoundingRect()
        return port_rect.center()
        
    def get_closest_port(self, scene_position):
        """Find the closest port to the given position."""
        closest_port_id = None
        min_distance = float('inf')
        
        for port_id, port in self.ports.items():
            port_center = port.sceneBoundingRect().center()
            dx = port_center.x() - scene_position.x()
            dy = port_center.y() - scene_position.y()
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_port_id = port_id
                
        return closest_port_id, min_distance

    def highlight_closest_port(self, scene_pos, highlight=True):
        """Highlight the port closest to the given position."""
        closest_port, distance = self.get_closest_port(scene_pos)
        
        # Only highlight if within reasonable distance (30 pixels)
        if distance < 30 and closest_port and closest_port in self.ports:
            port = self.ports[closest_port]
            if highlight:
                # Highlight port - make it bigger and orange
                port.setBrush(QBrush(QColor(255, 165, 0)))  # Orange for highlight
                port.setPen(QPen(Qt.red, 2))
                # Make it slightly larger while highlighted
                rect = port.rect()
                center = rect.center()
                new_rect = QRectF(
                    center.x() - rect.width() * 0.6, 
                    center.y() - rect.height() * 0.6,
                    rect.width() * 1.2, 
                    rect.height() * 1.2
                )
                port.setRect(new_rect)
            else:
                # Reset to default appearance
                is_connected = (closest_port in self.port_connections and 
                              len(self.port_connections[closest_port]) > 0)
                
                # Set color based on connection status
                if is_connected:
                    port.setBrush(QBrush(QColor(50, 200, 50)))  # Green for connected
                else:
                    port.setBrush(QBrush(QColor(50, 150, 255)))  # Blue for available
                    
                port.setPen(QPen(Qt.black, 1))
                
                # Reset size if it was changed
                if hasattr(port, 'default_rect') and port.default_rect:
                    port.setRect(port.default_rect)
                    
            return closest_port
        
        # Reset all ports if none are close
        if not highlight:
            self.reset_port_highlights()
        
        return None

    def reset_port_highlights(self):
        """Reset all port highlights to default."""
        for port_id, port in self.ports.items():
            # Check if port has connections
            has_connections = port_id in self.port_connections and len(self.port_connections[port_id]) > 0
            
            if has_connections:
                # Connected ports: green
                port.setBrush(QBrush(QColor(50, 200, 50)))
            else:
                # Default blue
                port.setBrush(QBrush(QColor(50, 150, 255)))
                
            port.setPen(QPen(Qt.black, 1))

    def add_connection_to_port(self, port_id, connection):
        """Add a connection to the specified port and update its appearance."""
        if port_id in self.ports:
            # Track the connection for this port
            if port_id not in self.port_connections:
                self.port_connections[port_id] = []
                
            self.port_connections[port_id].append(connection)
            
            # Update port appearance to show it's connected
            port = self.ports[port_id]
            port.setBrush(QBrush(QColor(50, 200, 50)))  # Green for connected ports
            
            return True
        return False


