from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QColor, QFont

import uuid

class DeviceItem:
    """Model class for network devices."""
    
    def __init__(self, device_id, device_type="generic", x=0, y=0, name="Device"):
        """Initialize a device model."""
        self.id = device_id
        self.device_type = device_type
        self.x = x
        self.y = y
        self.name = name
        self.connections = []
        self.ports = []
        self.view = None  # Will be set when view is created
        
        # Properties dictionary
        self.properties = {
            'name': name,
            'type': device_type,
            'status': 'active',
            'ip_address': '',
        }
    
    def set_position(self, x, y):
        """Set the device position."""
        self.x = x
        self.y = y
        
        # Update view if it exists
        if self.view:
            self.view.setPos(x, y)
    
    def add_port(self, port):
        """Add a port to this device."""
        self.ports.append(port)
    
    def add_connection(self, connection):
        """Add a connection to this device."""
        if connection not in self.connections:
            self.connections.append(connection)
    
    def remove_connection(self, connection):
        """Remove a connection from this device."""
        if connection in self.connections:
            self.connections.remove(connection)
    
    def update_property(self, key, value):
        """Update a device property."""
        self.properties[key] = value
        if key == 'name':
            self.name = value
        # Update view if exists
        if self.view:
            self.view.update_from_model()