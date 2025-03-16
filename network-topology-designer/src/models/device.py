# network-topology-designer/src/models/device.py
from PyQt5.QtCore import QPointF, pyqtSignal, Qt
from PyQt5.QtWidgets import (QGraphicsItemGroup, QGraphicsItem, QGraphicsTextItem,
                            QGraphicsRectItem, QGraphicsPathItem, QGraphicsEllipseItem,
                            QGraphicsPixmapItem)
from PyQt5.QtGui import QPixmap, QFont, QPen, QBrush, QColor, QPainterPath
import uuid
import os
from utils.resource_manager import ResourceManager
import math
import random  # For generating unique IDs

class Device(QGraphicsItemGroup):
    """Unified device class for network topology.
    
    This class handles both the data model and visual representation of network devices.
    """
    
    # Signals
    position_changed = pyqtSignal(object)
    selection_changed = pyqtSignal(object, bool)
    
    # Device types - centralized constants
    ROUTER = "router"
    SWITCH = "switch"
    SERVER = "server"
    FIREWALL = "firewall"
    CLOUD = "cloud"
    WORKSTATION = "workstation"
    GENERIC = "generic"
    
    # Device type properties
    DEVICE_PROPERTIES = {
        ROUTER: {
            'forwarding_table': {},
            'routing_protocol': 'OSPF',
            'icon': ':/icons/router.png',
        },
        SWITCH: {
            'vlan_support': True,
            'port_count': 24,
            'switching_capacity': '48 Gbps',
            'icon': ':/icons/switch.png',
        },
        SERVER: {
            'cpu': '4 cores',
            'memory': '16 GB',
            'storage': '1 TB',
            'os': 'Linux',
            'icon': ':/icons/server.png',
        },
        FIREWALL: {
            'inspection_type': 'Stateful',
            'throughput': '1 Gbps',
            'icon': ':/icons/firewall.png',
        },
        CLOUD: {
            'provider': 'Generic',
            'region': 'Default',
            'icon': ':/icons/cloud.png',
        },
        WORKSTATION: {
            'os': 'Windows',
            'cpu': '2 cores',
            'memory': '8 GB',
            'icon': ':/icons/workstation.png',
        },
        GENERIC: {
            'description': 'Generic network device',
            'icon': ':/icons/generic_device.png',
        }
    }
    
    # Counter for generating unique IDs
    _id_counter = 0
    
    def __init__(self, name, device_type):
        super().__init__()
        
        # Make sure the device is selectable, movable, and focuses on click
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        
        # Set acceptable mouse events
        self.setAcceptHoverEvents(True)
        
        # Initialize properties
        self.name = name
        self.device_type = device_type
        self.properties = self._get_default_properties()
        self.connections = []
        self.port_count = self._get_port_count()
        
        # Create visual components
        self._build_visual_representation()
        
        # Create the selection visual indicator (but keep it hidden initially)
        self._selection_indicator = self._create_selection_indicator()
        self.addToGroup(self._selection_indicator)
        self._selection_indicator.setVisible(False)
        
        # Core properties
        self.id = str(uuid.uuid4())[:8]
        self.width = 60
        self.height = 60
        
        # Visual components
        self.icon_item = None
        self.label_item = None
        self.selection_rect = None
        
        # Connection points/ports
        self.ports = []
        
        # Base properties for all devices
        self.properties.update({
            'id': self.id,
            'description': "",
            'ip_address': "",
            'mac_address': "",
            'status': "active",
        })
        
        # Add device-specific properties
        if device_type in self.DEVICE_PROPERTIES:
            # Copy only non-visual properties
            for key, value in self.DEVICE_PROPERTIES[device_type].items():
                if key != 'icon':  # Skip the icon property
                    self.properties[key] = value
        
        # Set position
        self.setPos(0, 0)
        
        # Create visual representation
        self._create_visual()
        self._init_ports()
        
        print(f"Device created: {self.name} ({self.device_type}) at position (0, 0)")
    
    @classmethod
    def create(cls, device_type, x=0, y=0, name=None):
        """
        Create a new device instance of the specified type.
        
        Args:
            device_type (str): The type of device to create
            x (float): The x position of the device
            y (float): The y position of the device
            name (str, optional): The name to give the device. Defaults to a generated name.
            
        Returns:
            Device: The created device instance
        """
        # Generate a name if none is provided
        if name is None:
            name = f"{device_type.capitalize()} {cls._get_next_id()}"
        
        # Create the device instance
        device = cls(name, device_type)
        
        # Position the device
        device.setPos(x, y)
        
        return device
    
    @classmethod
    def _get_next_id(cls):
        """
        Generate a unique ID for a new device.
        
        Returns:
            int: The next available device ID
        """
        # Use a simple incrementing counter stored in a class variable
        # If the counter doesn't exist yet, initialize it
        if not hasattr(cls, '_id_counter'):
            cls._id_counter = 0
        
        # Increment and return the counter
        cls._id_counter += 1
        return cls._id_counter

    def _create_visual(self):
        """Create visual representation of the device."""
        try:
            # Use ResourceManager to get the correct icon
            pixmap = ResourceManager.load_device_icon(self.device_type)
            
            if not pixmap.isNull():
                self.icon_item = QGraphicsPixmapItem(pixmap)
                self.icon_item.setOffset(-pixmap.width()/2, -pixmap.height()/2)
                self.addToGroup(self.icon_item)
                
                # Update size based on pixmap
                self.width = pixmap.width()
                self.height = pixmap.height()
                print(f"Icon loaded successfully: {pixmap.width()}x{pixmap.height()}")
            else:
                # Create a fallback visual
                print("Creating fallback rectangle")
                rect = QGraphicsRectItem(0, 0, 48, 48)
                rect.setBrush(QBrush(QColor(220, 220, 220)))
                rect.setPen(QPen(Qt.black))
                self.addToGroup(rect)
                
                # Add text label inside the rectangle for the device type
                type_label = QGraphicsTextItem(self.device_type[:1].upper())
                font = QFont()
                font.setPointSize(14)
                font.setBold(True)
                type_label.setFont(font)
                type_label.setPos(16, 10)  # Position in center of rectangle
                self.addToGroup(type_label)
            
            # Create label
            self.label_item = QGraphicsTextItem(self.name)
            font = QFont()
            font.setPointSize(8)
            self.label_item.setFont(font)
            
            # Center the label under the icon
            label_width = self.label_item.boundingRect().width()
            self.label_item.setPos(-label_width/2, self.height/2 + 5)
            self.addToGroup(self.label_item)
            
        except Exception as e:
            print(f"Error creating device visual: {e}")
            import traceback
            traceback.print_exc()
    
    def _init_ports(self):
        """Initialize connection ports based on device type."""
        # Basic 4 ports for all devices
        self.ports = [
            {'name': 'Port 1', 'position': 'north', 'connected': False},
            {'name': 'Port 2', 'position': 'east', 'connected': False},
            {'name': 'Port 3', 'position': 'south', 'connected': False},
            {'name': 'Port 4', 'position': 'west', 'connected': False}
        ]
        
        # Add device-specific ports
        if self.device_type == self.SWITCH:
            # Switches get more ports
            self.ports.extend([
                {'name': 'Port 5', 'position': 'north-east', 'connected': False},
                {'name': 'Port 6', 'position': 'south-east', 'connected': False},
                {'name': 'Port 7', 'position': 'south-west', 'connected': False},
                {'name': 'Port 8', 'position': 'north-west', 'connected': False},
            ])
        elif self.device_type == self.ROUTER:
            # Routers get a WAN port
            self.ports.append({'name': 'WAN', 'position': 'north-east', 'connected': False})
        elif self.device_type == self.SERVER:
            # Servers get multiple network interfaces
            self.ports.extend([
                {'name': 'NIC 1', 'position': 'east', 'connected': False},
                {'name': 'NIC 2', 'position': 'west', 'connected': False},
            ])
    
    def itemChange(self, change, value):
        """Handle item changes such as position and selection."""
        from PyQt5.QtWidgets import QGraphicsItem
        
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Position has changed, update connections
            if hasattr(self, 'connections') and self.connections:
                for connection in self.connections:
                    if connection:
                        connection.update_position()
                        
        elif change == QGraphicsItem.ItemSelectedChange:
            # Selection state is changing
            if hasattr(self, '_selection_indicator'):
                self._selection_indicator.setVisible(bool(value))
        
        # Call the parent class implementation
        return super().itemChange(change, value)
    
    def update_property(self, key, value):
        """Update a device property."""
        if key in self.properties:
            self.properties[key] = value
            
            # Update label if name changed
            if key == 'name':
                self.name = value
                if self.label_item:
                    self.label_item.setPlainText(value)
                    
                    # Re-center the label
                    label_width = self.label_item.boundingRect().width()
                    self.label_item.setPos(-label_width/2, self.height/2 + 5)
    
    def add_connection(self, connection):
        """Add a connection to this device."""
        if connection not in self.connections:
            self.connections.append(connection)
    
    def remove_connection(self, connection):
        """Remove a connection from this device."""
        if connection in self.connections:
            self.connections.remove(connection)
    
    def get_port_position(self, port_name):
        """Get the scene position of a specific port."""
        # Find the port
        port = next((p for p in self.ports if p['name'] == port_name), None)
        if not port:
            return self.scenePos()  # Default to device center if port not found
        
        # Calculate position based on port position attribute
        pos = self.scenePos()
        
        if port['position'] == 'north':
            return QPointF(pos.x(), pos.y() - self.height/2)
        elif port['position'] == 'east':
            return QPointF(pos.x() + self.width/2, pos.y())
        elif port['position'] == 'south':
            return QPointF(pos.x(), pos.y() + self.height/2)
        elif port['position'] == 'west':
            return QPointF(pos.x() - self.width/2, pos.y())
        elif port['position'] == 'north-east':
            return QPointF(pos.x() + self.width/3, pos.y() - self.height/3)
        elif port['position'] == 'south-east':
            return QPointF(pos.x() + self.width/3, pos.y() + self.height/3)
        elif port['position'] == 'south-west':
            return QPointF(pos.x() - self.width/3, pos.y() + self.height/3)
        elif port['position'] == 'north-west':
            return QPointF(pos.x() - self.width/3, pos.y() - self.height/3)
        
        return pos  # Default to device center
    
    def get_closest_port(self, scene_pos):
        """Get the port closest to the given scene position."""
        min_distance = float('inf')
        closest_port = None
        
        for port in self.ports:
            port_pos = self.get_port_position(port['name'])
            dx = port_pos.x() - scene_pos.x()
            dy = port_pos.y() - scene_pos.y()
            distance = (dx*dx + dy*dy) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_port = port
        
        return closest_port, min_distance
    
    # Compatibility methods for NetworkDevice and DeviceItem
    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name
    
    def get_type(self):
        return self.device_type
    
    def get_property(self, key):
        return self.properties.get(key)
    
    def to_dict(self):
        """Convert device to dictionary for serialization."""
        return {
            'id': self.id,
            'type': self.device_type,
            'name': self.name,
            'x': self.pos().x(),
            'y': self.pos().y(),
            'properties': self.properties.copy(),
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create device from dictionary (deserialization)."""
        device = cls(
            name=data['name'],
            device_type=data['type']
        )
        device.id = data['id']
        device.setPos(data['x'], data['y'])
        
        # Update properties
        if 'properties' in data:
            for key, value in data['properties'].items():
                device.properties[key] = value
        
        return device
        
    @classmethod
    def get_available_types(cls):
        """Return list of available device types."""
        return list(cls.DEVICE_PROPERTIES.keys())
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click events (could be used to edit properties)"""
        super().mouseDoubleClickEvent(event)
        # Optional: Emit a signal or perform an action on double-click
        
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        # Ensure the item gets focus and is selected on click
        self.setFocus()
        super().mousePressEvent(event)
    
    def _create_selection_indicator(self):
        """Create a visual indicator for when the device is selected."""
        from PyQt5.QtWidgets import QGraphicsPathItem
        from PyQt5.QtGui import QPen, QPainterPath, QColor  # QColor is in QtGui
        from PyQt5.QtCore import Qt  # Don't import QColor from here
        
        # Create a path that outlines the device shape
        path = QPainterPath()
        bounds = self.boundingRect()
        
        # Add a small padding around the device
        padding = 5
        rect = bounds.adjusted(-padding, -padding, padding, padding)
        path.addRect(rect)
        
        outline = QGraphicsPathItem(path)
        outline.setPen(QPen(QColor(0, 120, 215), 1.5, Qt.DashLine))  # Blue dashed line
        outline.setZValue(-1)  # Place behind the device
        
        return outline
    
    def _get_default_properties(self):
        """Return the default properties for this device type."""
        if self.device_type in self.DEVICE_PROPERTIES:
            # Return a copy to avoid modifying the class constants
            return dict(self.DEVICE_PROPERTIES[self.device_type])
        else:
            # Default to generic device properties if type not found
            return dict(self.DEVICE_PROPERTIES[self.GENERIC])
    
    # Simplified version that just returns a basic port count
    def _get_port_count(self):
        """Get a basic port count for connection points."""
        # Just return a simple count - we're using abstract connections
        return 4  # One for each side (north, east, south, west)
    
    def _build_visual_representation(self):
        """Build the visual components of the device."""
        # Create the main shape/icon
        icon = self._create_icon()
        self.addToGroup(icon)
        
        # Create and add the label
        self._label = self._create_label()
        self.addToGroup(self._label)
        
        # Create selection indicator (initially hidden)
        self._selection_indicator = self._create_selection_indicator()
        self.addToGroup(self._selection_indicator)
        self._selection_indicator.setVisible(False)

    def _create_icon(self):
        """Create and return a device icon based on device type."""
        from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsPixmapItem
        from PyQt5.QtGui import QPen, QBrush, QColor, QPainterPath, QPixmap
        from PyQt5.QtCore import Qt, QRectF
        import math
        
        # Try to get icon from resources if defined in properties
        icon_path = self.properties.get('icon')
        if icon_path:
            try:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    icon = QGraphicsPixmapItem(pixmap)
                    # Center the icon
                    icon_width = pixmap.width()
                    icon_height = pixmap.height()
                    icon.setPos(-icon_width / 2, -icon_height / 2)
                    return icon
            except Exception as e:
                print(f"Error loading icon from {icon_path}: {e}")
        
        # Fallback to geometric shapes
        if self.device_type == self.ROUTER:
            # Create a hexagon for router
            path = QPainterPath()
            radius = 30
            points = []
            for i in range(6):
                angle = 2 * math.pi * i / 6
                points.append(QPointF(radius * math.cos(angle), radius * math.sin(angle)))
            
            path.moveTo(points[0])
            for point in points[1:]:
                path.lineTo(point)
            path.closeSubpath()
            
            shape = QGraphicsPathItem(path)
            shape.setPen(QPen(Qt.black, 2))
            shape.setBrush(QBrush(QColor(220, 180, 180)))
            return shape
            
        elif self.device_type == self.SWITCH:
            # Rectangle for switch
            rect = QGraphicsRectItem(-40, -20, 80, 40)
            rect.setPen(QPen(Qt.black, 2))
            rect.setBrush(QBrush(QColor(180, 220, 180)))
            return rect
            
        elif self.device_type == self.SERVER:
            # Taller rectangle for server
            rect = QGraphicsRectItem(-30, -40, 60, 80)
            rect.setPen(QPen(Qt.black, 2))
            rect.setBrush(QBrush(QColor(180, 180, 220)))
            return rect
            
        elif self.device_type == self.FIREWALL:
            # Special shape for firewall
            path = QPainterPath()
            path.addRect(-35, -25, 70, 50)
            
            # Add internal lines to represent firewall
            shape = QGraphicsPathItem(path)
            shape.setPen(QPen(Qt.black, 2))
            shape.setBrush(QBrush(QColor(220, 150, 150)))
            return shape
        
        elif self.device_type == self.CLOUD:
            # Cloud-like shape
            path = QPainterPath()
            path.addEllipse(-30, -20, 40, 40)
            path.addEllipse(-10, -30, 40, 40)
            path.addEllipse(10, -20, 40, 40)
            path.addEllipse(-10, 0, 40, 40)
            
            shape = QGraphicsPathItem(path)
            shape.setPen(QPen(Qt.black, 2))
            shape.setBrush(QBrush(QColor(200, 220, 255)))
            return shape
            
        elif self.device_type == self.WORKSTATION:
            # Computer-like shape
            rect = QGraphicsRectItem(-25, -20, 50, 40)
            rect.setPen(QPen(Qt.black, 2))
            rect.setBrush(QBrush(QColor(220, 220, 180)))
            return rect
        
        else:
            # Generic circle for other devices
            circle = QGraphicsEllipseItem(-25, -25, 50, 50)
            circle.setPen(QPen(Qt.black, 2))
            circle.setBrush(QBrush(QColor(200, 200, 200)))
            return circle

    def _create_label(self):
        """Create and return a label for the device."""
        from PyQt5.QtWidgets import QGraphicsTextItem
        from PyQt5.QtGui import QFont
        from PyQt5.QtCore import Qt
        
        label = QGraphicsTextItem(self.name)
        # Center the text below the device
        font = QFont()
        font.setPointSize(9)
        label.setFont(font)
        
        # Calculate width to center the text
        text_width = label.boundingRect().width()
        label.setPos(-text_width / 2, 35)  # Position below the device
        
        # Make sure text is centered
        label.setDefaultTextColor(Qt.black)
        return label

    def _create_selection_indicator(self):
        """Create a visual indicator for when the device is selected."""
        from PyQt5.QtWidgets import QGraphicsPathItem
        from PyQt5.QtGui import QPen, QPainterPath, QColor  # QColor is in QtGui
        from PyQt5.QtCore import Qt  # Don't import QColor from here
        
        # Create a path that outlines the device shape
        path = QPainterPath()
        bounds = self.boundingRect()
        
        # Add a small padding around the device
        padding = 5
        rect = bounds.adjusted(-padding, -padding, padding, padding)
        path.addRect(rect)
        
        outline = QGraphicsPathItem(path)
        outline.setPen(QPen(QColor(0, 120, 215), 1.5, Qt.DashLine))  # Blue dashed line
        outline.setZValue(-1)  # Place behind the device
        
        return outline

    def get_connection_point(self, target_position):
        """
        Get a connection point on the edge of this device, facing toward the target position.
        
        Args:
            target_position (QPointF): The target position to connect to
            
        Returns:
            QPointF: The connection point on the edge of this device
        """
        import math
        
        # Get the device center (scene coordinates)
        device_center = self.scenePos()
        
        # Calculate direction vector to target
        dx = target_position.x() - device_center.x()
        dy = target_position.y() - device_center.y()
        
        # Avoid division by zero
        if dx == 0 and dy == 0:
            return device_center
        
        # Calculate angle
        angle = math.atan2(dy, dx)
        
        # Get device bounding rectangle
        bounds = self.boundingRect()
        width = bounds.width()
        height = bounds.height()
        
        # Convert to device's local coordinate system
        local_width = width / 2
        local_height = height / 2
        
        # Determine the intersection point with the device boundary
        if abs(dx) * local_height > abs(dy) * local_width:
            # Intersection with left or right edge
            x = local_width if dx > 0 else -local_width
            y = local_height * dy / abs(dx) if dx != 0 else 0
        else:
            # Intersection with top or bottom edge
            y = local_height if dy > 0 else -local_height
            x = local_width * dx / abs(dy) if dy != 0 else 0
        
        # Convert back to scene coordinates
        scene_point = self.mapToScene(x, y)
        return scene_point