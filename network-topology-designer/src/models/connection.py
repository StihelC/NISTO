import uuid
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtGui import QPen, QPainterPath, QColor
from PyQt5.QtCore import Qt, QPointF, QObject
from PyQt5.QtWidgets import QGraphicsLineItem

class Connection(QObject):
    """
    Represents a connection between two network devices.
    """
    
    # Connection types
    TYPE_ETHERNET = "ethernet"
    TYPE_FIBER = "fiber"
    TYPE_WIRELESS = "wireless"
    
    def __init__(self, source_device, target_device, connection_type=None):
        """
        Initialize a connection between two devices.
        
        Args:
            source_device (Device): The source device
            target_device (Device): The target device
            connection_type (str, optional): Type of connection. Defaults to ethernet.
        """
        super().__init__()
        
        self.source_device = source_device
        self.target_device = target_device
        self.connection_type = connection_type or self.TYPE_ETHERNET
        self.properties = {}
        
        # Create visual representation
        self.line_item = ConnectionLine(self)
        
        # Register with devices
        if hasattr(source_device, 'connections'):
            source_device.connections.append(self)
        if hasattr(target_device, 'connections'):
            target_device.connections.append(self)
    
    def update_position(self):
        """Update the connection line position."""
        if self.line_item:
            self.line_item.update_position()
    
    def remove(self):
        """Remove this connection."""
        # Remove from source device
        if self.source_device and hasattr(self.source_device, 'connections'):
            if self in self.source_device.connections:
                self.source_device.connections.remove(self)
        
        # Remove from target device
        if self.target_device and hasattr(self.target_device, 'connections'):
            if self in self.target_device.connections:
                self.target_device.connections.remove(self)
        
        # Remove visual line
        if self.line_item and self.line_item.scene():
            self.line_item.scene().removeItem(self.line_item)
            self.line_item = None


class ConnectionLine(QGraphicsLineItem):
    """
    Visual representation of a connection between devices.
    """
    
    # Connection style definitions
    STYLES = {
        Connection.TYPE_ETHERNET: {"color": QColor(0, 0, 0), "width": 2, "style": Qt.SolidLine},
        Connection.TYPE_FIBER: {"color": QColor(255, 140, 0), "width": 2, "style": Qt.DashLine},
        Connection.TYPE_WIRELESS: {"color": QColor(50, 150, 50), "width": 1.5, "style": Qt.DotLine}
    }
    
    def __init__(self, connection):
        """Initialize the connection line."""
        super().__init__()
        
        self.connection = connection
        
        # Set basic properties
        self.setZValue(-10)  # Draw behind devices
        self.setFlag(QGraphicsLineItem.ItemIsSelectable)
        
        # Apply style based on connection type
        self._apply_style()
        
        # Initial position update
        self.update_position()
    
    def _apply_style(self):
        """Apply visual style based on connection type."""
        conn_type = self.connection.connection_type
        style = self.STYLES.get(conn_type, self.STYLES[Connection.TYPE_ETHERNET])
        
        pen = QPen(style["color"], style["width"], style["style"])
        self.setPen(pen)
    
    def update_position(self):
        """Update the connection position based on connected devices."""
        source = self.connection.source_device
        target = self.connection.target_device
        
        if not source or not target:
            return
        
        # Get connection points on the edges of the devices
        source_pos = source.get_connection_point(target.scenePos())
        target_pos = target.get_connection_point(source.scenePos())
        
        # Update the line
        self.setLine(source_pos.x(), source_pos.y(), 
                    target_pos.x(), target_pos.y())