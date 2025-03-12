from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QPixmap

class DeviceView(QGraphicsItemGroup):
    """Visual representation of a network device."""
    
    # Device type colors
    COLORS = {
        "router": QColor(200, 150, 150),
        "switch": QColor(150, 200, 150),
        "server": QColor(150, 150, 200),
        "client": QColor(200, 200, 150),
        "cloud": QColor(180, 180, 220),
        "generic": QColor(200, 200, 200)
    }
    
    def __init__(self, device_model):
        """Initialize the device view."""
        super().__init__()
        
        self.device_model = device_model
        
        # Set graphics item flags
        self.setFlag(QGraphicsItemGroup.ItemIsMovable)
        self.setFlag(QGraphicsItemGroup.ItemIsSelectable)
        self.setFlag(QGraphicsItemGroup.ItemSendsGeometryChanges)
        
        # Create visual elements
        self._create_visual_elements()
        
        # Position at model coordinates
        self.setPos(device_model.x, device_model.y)
        
    def _create_visual_elements(self):
        """Create the visual representation of this device."""
        # Get color for this device type
        device_color = self.COLORS.get(
            self.device_model.device_type.lower(),
            self.COLORS["generic"]
        )
        
        # Create main rectangle
        self.rect = QGraphicsRectItem(0, 0, 80, 50)
        self.rect.setBrush(QBrush(device_color))
        self.rect.setPen(QPen(Qt.black, 1))
        
        # Create label
        self.label = QGraphicsTextItem(self.device_model.name)
        self.label.setPos(10, 15)
        self.label.setFont(QFont("Arial", 8))
        
        # Add to group
        self.addToGroup(self.rect)
        self.addToGroup(self.label)
    
    def show_ports(self, visible=True):
        """Show or hide port indicators."""
        for port in self.device_model.ports:
            if 'view_indicator' in port:
                port['view_indicator'].setVisible(visible)
    
    def update_position(self):
        """Update position from model."""
        self.setPos(self.device_model.x, self.device_model.y)
    
    def update_appearance(self):
        """Update appearance from model."""
        # Update label with model name
        self.label.setPlainText(self.device_model.name)
        
        # Center the label beneath the device
        label_width = self.label.boundingRect().width()
        label_x = (self.width - label_width) / 2
        self.label.setPos(label_x, self.height + 5)
        
        # Update status-based appearance
        status = self.device_model.properties.get('status', 'active')
        if status == 'inactive':
            self.setOpacity(0.6)
        elif status == 'error':
            # Set body border to red
            if hasattr(self, 'body'):
                self.body.setPen(QPen(QColor(255, 0, 0), 2))
        else:
            self.setOpacity(1.0)
            if hasattr(self, 'body'):
                self.body.setPen(QPen(Qt.black, 1))
    
    def itemChange(self, change, value):
        """Handle item changes like position changes."""
        if change == QGraphicsItemGroup.ItemPositionChange and self.scene():
            # Update model position when view is moved
            new_pos = value
            if self.device_model:
                self.device_model.x = new_pos.x()
                self.device_model.y = new_pos.y()
                self.device_model._update_connections()
        
        return super().itemChange(change, value)
    
    def _update_connections(self):
        """Update any connections attached to this device."""
        for connection in self.device_model.connections:
            if connection.view:
                connection.view.update_path()
    
    def get_port_position(self, port_name):
        """Get the scene position of a port by name."""
        for port in self.device_model.ports:
            if port['name'] == port_name and 'view_indicator' in port:
                # Get center of port indicator
                indicator = port['view_indicator']
                rect = indicator.rect()
                port_center = QPointF(
                    rect.x() + rect.width() / 2,
                    rect.y() + rect.height() / 2
                )
                # Convert to scene coordinates
                return self.mapToScene(port_center)
        
        # Return center of device if port not found
        return self.get_center_point()
    
    def get_center_point(self):
        """Get the center point of the device in scene coordinates."""
        return self.mapToScene(QPointF(self.width / 2, self.height / 2))
    
    def get_closest_port(self, scene_pos):
        """Get the closest port to a scene position."""
        closest_port = None
        min_distance = float('inf')
        
        for port in self.device_model.ports:
            if 'view_indicator' in port:
                indicator = port['view_indicator']
                port_pos = self.mapToScene(indicator.rect().center())
                
                # Calculate distance
                dx = port_pos.x() - scene_pos.x()
                dy = port_pos.y() - scene_pos.y()
                distance = (dx * dx + dy * dy) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_port = port
        
        return closest_port, min_distance