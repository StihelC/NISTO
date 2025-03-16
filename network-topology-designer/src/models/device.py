# network-topology-designer/src/models/device.py
from PyQt5.QtCore import QPointF, pyqtSignal, Qt
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsRectItem
from PyQt5.QtGui import QPixmap, QFont, QPen, QBrush, QColor
import uuid
import os
from utils.resource_manager import ResourceManager

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
    
    def __init__(self, device_id=None, device_type=GENERIC, name=None, x=0, y=0):
        """Initialize a device."""
        super().__init__()
        
        # Core properties
        self.id = device_id or str(uuid.uuid4())[:8]
        self.device_type = device_type
        self.name = name or f"{device_type.capitalize()}-{self.id[-4:]}"
        self.width = 60
        self.height = 60
        
        # Visual components
        self.icon_item = None
        self.label_item = None
        self.selection_rect = None
        
        # Connection points/ports
        self.ports = []
        self.connections = []
        
        # Base properties for all devices
        self.properties = {
            'id': self.id,
            'name': self.name,
            'description': "",
            'ip_address': "",
            'mac_address': "",
            'status': "active",
        }
        
        # Add device-specific properties
        if device_type in self.DEVICE_PROPERTIES:
            # Copy only non-visual properties
            for key, value in self.DEVICE_PROPERTIES[device_type].items():
                if key != 'icon':  # Skip the icon property
                    self.properties[key] = value
        
        # Set position
        self.setPos(x, y)
        
        # Set flags
        self.setFlag(QGraphicsItemGroup.ItemIsSelectable, True)
        self.setFlag(QGraphicsItemGroup.ItemIsMovable, True)
        self.setFlag(QGraphicsItemGroup.ItemSendsGeometryChanges, True)
        
        # Create visual representation
        self._create_visual()
        self._init_ports()
        
        print(f"Device created: {self.name} ({self.device_type}) at position ({x}, {y})")
    
    @classmethod
    def create(cls, device_type, x=0, y=0, name=None):
        """Factory method to create a device of the specified type."""
        device_id = str(uuid.uuid4())[:8]
        
        if device_type not in cls.DEVICE_PROPERTIES:
            print(f"Warning: Unknown device type '{device_type}', using generic")
            device_type = cls.GENERIC
            
        if not name:
            name = f"{device_type.capitalize()}-{device_id[-4:]}"
        
        # Create the device with the proper type
        device = cls(device_id, device_type, name, x, y)
        return device
    
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
        """Handle item changes like position and selection."""
        if change == QGraphicsItemGroup.ItemPositionChange:
            # Emit signal when position changes
            if hasattr(self, 'position_changed'):
                self.position_changed.emit(self)
        
        elif change == QGraphicsItemGroup.ItemSelectedChange:
            # Handle selection change
            if value and not self.selection_rect:
                # Create selection indicator
                rect = self.boundingRect()
                self.selection_rect = QGraphicsRectItem(rect.adjusted(-5, -5, 5, 5))
                self.selection_rect.setPen(QPen(Qt.blue, 1, Qt.DashLine))
                self.selection_rect.setBrush(QBrush(Qt.transparent))
                self.addToGroup(self.selection_rect)
            
            elif not value and self.selection_rect:
                # Remove selection indicator
                self.removeFromGroup(self.selection_rect)
                self.selection_rect = None
            
            # Emit selection changed signal
            if hasattr(self, 'selection_changed'):
                self.selection_changed.emit(self, bool(value))
        
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
            device_id=data['id'],
            device_type=data['type'],
            name=data['name'],
            x=data['x'],
            y=data['y']
        )
        
        # Update properties
        if 'properties' in data:
            for key, value in data['properties'].items():
                device.properties[key] = value
        
        return device
        
    @classmethod
    def get_available_types(cls):
        """Return list of available device types."""
        return list(cls.DEVICE_PROPERTIES.keys())