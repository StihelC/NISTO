from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsRectItem, QGraphicsEllipseItem
from PyQt5.QtWidgets import QGraphicsTextItem, QGraphicsPolygonItem, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QColor, QBrush, QFont, QPolygonF

from src.views.connection_view import ConnectionView

class DeviceViewFactory:
    """Factory for creating views for devices and connections."""
    
    def create_device_view(self, device_model, resource_manager=None):
        """Create a view for a device model."""
        # Create base view
        device_view = DeviceView(device_model, resource_manager)
        
        # Set position from model
        device_view.setPos(device_model.x, device_model.y)
        
        # Add specialized visual elements based on device type
        if not resource_manager:  # If no resource manager, use shaped devices
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
        polygon = QPolygonF()
        polygon.append(QPointF(device_view.width / 2, 0))           # Top
        polygon.append(QPointF(device_view.width, device_view.height / 3))  # Right top
        polygon.append(QPointF(device_view.width, 2 * device_view.height / 3))  # Right bottom
        polygon.append(QPointF(device_view.width / 2, device_view.height))  # Bottom
        polygon.append(QPointF(0, 2 * device_view.height / 3))       # Left bottom
        polygon.append(QPointF(0, device_view.height / 3))           # Left top
        
        body = QGraphicsPolygonItem(polygon)
        body.setPen(QPen(Qt.black, 1))
        body.setBrush(QBrush(QColor(200, 255, 200, 180)))  # Light green
        device_view.addToGroup(body)
        device_view.body = body
    
    # Add methods for other device types (switch, server, client, etc.)
    
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
            
            # Store with the port - use consistent naming for indicators
            port['view_indicator'] = port_indicator
            port['indicator'] = port_indicator  # For backward compatibility
            device_view.addToGroup(port_indicator)


class DeviceView(QGraphicsItemGroup):
    """Visual representation of a network device."""
    
    # Fallback colors if icons aren't available
    COLORS = {
        "router": QColor(200, 150, 150),
        "switch": QColor(150, 200, 150),
        "server": QColor(150, 150, 200),
        "client": QColor(200, 200, 150),
        "firewall": QColor(220, 150, 150),
        "cloud": QColor(180, 180, 220),
        "generic": QColor(200, 200, 200)
    }
    
    def __init__(self, device_model, resource_manager=None):
        """Initialize the device view."""
        super().__init__()
        
        self.device_model = device_model
        self.resource_manager = resource_manager
        
        # Set graphics item flags
        self.setFlag(QGraphicsItemGroup.ItemIsMovable)
        self.setFlag(QGraphicsItemGroup.ItemIsSelectable)
        self.setFlag(QGraphicsItemGroup.ItemSendsGeometryChanges)
        
        # Default size
        self.width = 80
        self.height = 60
        
        # Create visual elements
        self._create_visual_elements()
        
        # Position at model coordinates
        self.setPos(device_model.x, device_model.y)
        
    def _create_visual_elements(self):
        """Create the visual representation of this device."""
        # Try to use icon if resource manager is available
        icon_item = None
        if self.resource_manager:
            pixmap = self.resource_manager.get_device_pixmap(
                self.device_model.device_type,
                size=(60, 40)
            )
            if pixmap and not pixmap.isNull():
                # Create icon item
                icon_item = QGraphicsPixmapItem(pixmap)
                icon_item.setPos(10, 5)
                self.addToGroup(icon_item)
                self.body = icon_item  # Store as body for consistency
        
        # If no icon, create a default colored rectangle
        if not icon_item:
            rect_color = self.COLORS.get(
                self.device_model.device_type.lower(), 
                self.COLORS["generic"]
            )
            rect_item = QGraphicsRectItem(0, 0, self.width, self.height)
            rect_item.setBrush(QBrush(rect_color))
            rect_item.setPen(QPen(Qt.black, 1))
            self.addToGroup(rect_item)
            self.body = rect_item
        
        # Add label below the icon/rectangle
        self.label = QGraphicsTextItem(self.device_model.name)
        font = QFont("Arial", 8)
        self.label.setFont(font)
        
        # Center the label
        label_width = self.label.boundingRect().width()
        label_x = (self.width - label_width) / 2
        self.label.setPos(label_x, self.height + 5)
        
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
                
                # Update connections
                self._update_connections()
        
        return super().itemChange(change, value)
    
    def _update_connections(self):
        """Update any connections attached to this device."""
        if hasattr(self.device_model, 'connections'):
            for connection in self.device_model.connections:
                if hasattr(connection, 'view') and connection.view:
                    # Support both method names
                    if hasattr(connection.view, 'update_path'):
                        connection.view.update_path()
                    elif hasattr(connection.view, 'update_position'):
                        connection.view.update_position()
    
    def get_port_position(self, port_name):
        """Get the scene position of a port by name."""
        for port in self.device_model.ports:
            if port['name']:
                # Check both naming conventions
                indicator = port.get('view_indicator') or port.get('indicator')
                if indicator:
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
            # Check both naming conventions
            indicator = port.get('view_indicator') or port.get('indicator')
            if indicator:
                port_pos = self.mapToScene(indicator.rect().center())
                
                # Calculate distance
                dx = port_pos.x() - scene_pos.x()
                dy = port_pos.y() - scene_pos.y()
                distance = (dx * dx + dy * dy) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_port = port
        
        return closest_port, min_distance
    
    def paint(self, painter, option, widget):
        """Custom painting for selection indication."""
        # Let the group items paint themselves
        super().paint(painter, option, widget)
        
        # Draw selection indicator if selected
        if self.isSelected():
            painter.setPen(QPen(Qt.blue, 2, Qt.DashLine))
            painter.drawRect(self.boundingRect().adjusted(2, 2, -2, -2))