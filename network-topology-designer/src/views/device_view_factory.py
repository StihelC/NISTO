from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsRectItem, QGraphicsEllipseItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QColor, QBrush, QFont

from src.views.connection_view import ConnectionView

class DeviceViewFactory:
    """Factory for creating views for devices and connections."""
    
    def create_device_view(self, device_model):
        """Create a view for a device model."""
        # Create base view
        device_view = DeviceView(device_model)
        
        # Set position from model
        device_view.setPos(device_model.x, device_model.y)
        
        # Add specialized visual elements based on device type
        if device_model.device_type == "router":
            self._create_router_visual(device_view)
        elif device_model.device_type == "switch":
            self._create_switch_visual(device_view)
        elif device_model.device_type == "server":
            self._create_server_visual(device_view)
        elif device_model.device_type == "client":
            self._create_client_visual(device_view)
        else:
            self._create_generic_visual(device_view)
        
        # Create port indicators
        self._create_port_indicators(device_view)
        
        return device_view
    
    def create_connection_view(self, connection_model):
        """Create a view for a connection model."""
        return ConnectionView(connection_model)
    
    def _create_generic_visual(self, device_view):
        """Create a generic device visual."""
        # Create body rectangle
        body = QGraphicsRectItem(0, 0, device_view.width, device_view.height)
        body.setPen(QPen(Qt.black, 1))
        body.setBrush(QBrush(QColor(200, 200, 255, 180)))
        device_view.addToGroup(body)
        device_view.body = body
    
    def _create_router_visual(self, device_view):
        """Create a router device visual."""
        # Create hexagon shape for router
        from PyQt5.QtGui import QPolygonF
        polygon = QPolygonF()
        polygon.append(QPointF(device_view.width / 2, 0))           # Top
        polygon.append(QPointF(device_view.width, device_view.height / 3))  # Right top
        polygon.append(QPointF(device_view.width, 2 * device_view.height / 3))  # Right bottom
        polygon.append(QPointF(device_view.width / 2, device_view.height))  # Bottom
        polygon.append(QPointF(0, 2 * device_view.height / 3))       # Left bottom
        polygon.append(QPointF(0, device_view.height / 3))           # Left top
        
        from PyQt5.QtWidgets import QGraphicsPolygonItem
        body = QGraphicsPolygonItem(polygon)
        body.setPen(QPen(Qt.black, 1))
        body.setBrush(QBrush(QColor(200, 255, 200, 180)))  # Light green
        device_view.addToGroup(body)
        device_view.body = body
    
    # Similar methods for other device types...
    
    def _create_port_indicators(self, device_view):
        """Create visual indicators for device ports."""
        device_model = device_view.device_model
        port_size = 6
        
        for port in device_model.ports:
            pos = port['position']
            x, y = 0, 0
            
            # Calculate port position
            if pos == 'north':
                x = device_view.width / 2 - port_size / 2
                y = -port_size / 2
            elif pos == 'east':
                x = device_view.width - port_size / 2
                y = device_view.height / 2 - port_size / 2
            elif pos == 'south':
                x = device_view.width / 2 - port_size / 2
                y = device_view.height - port_size / 2
            elif pos == 'west':
                x = -port_size / 2
                y = device_view.height / 2 - port_size / 2
            # Add more positions for switches with many ports
            
            # Create port indicator
            port_indicator = QGraphicsEllipseItem(x, y, port_size, port_size)
            port_indicator.setPen(QPen(Qt.black, 1))
            port_indicator.setBrush(QBrush(QColor(255, 255, 200)))
            port_indicator.setToolTip(port['name'])
            
            # Store with the port
            port['view_indicator'] = port_indicator
            device_view.addToGroup(port_indicator)


class DeviceView(QGraphicsItemGroup):
    """Base class for device views."""
    
    def __init__(self, device_model):
        """Initialize the device view."""
        super().__init__()
        
        self.device_model = device_model
        
        # Default dimensions
        self.width = 60
        self.height = 60
        
        # Set flags
        self.setFlag(QGraphicsItemGroup.ItemIsMovable)
        self.setFlag(QGraphicsItemGroup.ItemIsSelectable)
        self.setFlag(QGraphicsItemGroup.ItemSendsGeometryChanges)
        
        # Create label
        from PyQt5.QtWidgets import QGraphicsTextItem
        self.label = QGraphicsTextItem(device_model.name)
        font = QFont()
        font.setPointSize(8)
        self.label.setFont(font)
        
        # Position label beneath the device
        self.label.setPos(0, self.height + 5)
        self.addToGroup(self.label)
    
    def update_from_model(self):
        """Update visual state from model data."""
        # Update position
        self.setPos(self.device_model.x, self.device_model.y)
        
        # Update label
        self.label.setPlainText(self.device_model.name)
        
        # Center the label
        label_width = self.label.boundingRect().width()
        label_x = (self.width - label_width) / 2
        self.label.setPos(label_x, self.height + 5)
    
    def itemChange(self, change, value):
        """Handle item changes."""
        if change == QGraphicsItemGroup.ItemPositionChange:
            # Item is being moved, update the model position
            new_pos = value
            self.device_model.x = new_pos.x()
            self.device_model.y = new_pos.y()
            
            # Update connections if device has any
            self._update_connections()
        
        return super().itemChange(change, value)
    
    def _update_connections(self):
        """Update any connections attached to this device."""
        for connection in self.device_model.connections:
            if connection.view:
                connection.view.update_from_model()
    
    def get_port_position(self, port_name):
        """Get scene position of a port."""
        for port in self.device_model.ports:
            if port['name'] == port_name and 'view_indicator' in port:
                indicator = port['view_indicator']
                rect = indicator.rect()
                local_pos = QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
                return self.mapToScene(local_pos)
        
        # Return center if port not found
        return self.get_center_point()
    
    def get_center_point(self):
        """Get the center point of the device in scene coordinates."""
        return self.mapToScene(QPointF(self.width / 2, self.height / 2))