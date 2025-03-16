from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QGraphicsItemGroup
from PyQt5.QtGui import QPen, QBrush, QColor, QIcon, QPixmap, QPainter, QFont
from PyQt5.QtCore import Qt, QRectF, QPointF
import uuid

class DeviceItem(QGraphicsItemGroup):
    """Base class for all network device items in the scene."""
    
    def __init__(self, device_type="generic", name=None, parent=None):
        """Initialize a device item."""
        super().__init__(parent)
        
        # Device properties
        self.device_type = device_type
        self.properties = {
            'id': str(uuid.uuid4()),
            'name': name or f"{device_type.capitalize()} Device",
            'description': "",
            'ip_address': "",
            'mac_address': "",
            'status': "active",
        }
        
        # Device dimensions
        self.width = 60
        self.height = 60
        
        # Initialize ports
        self.ports = []
        self._init_ports()
        
        # Set flags for interaction
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # Create visual representation
        self._create_visual_representation()
    
    def _init_ports(self):
        """Initialize device ports."""
        # Default implementation: 4 ports (N, E, S, W)
        self.ports = [
            {'name': 'Port 1', 'position': 'north', 'connected': False},
            {'name': 'Port 2', 'position': 'east', 'connected': False},
            {'name': 'Port 3', 'position': 'south', 'connected': False},
            {'name': 'Port 4', 'position': 'west', 'connected': False}
        ]
    
    def _create_visual_representation(self):
        """Create the visual representation of the device."""
        from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
        
        # Create body rectangle
        self.body = QGraphicsRectItem(0, 0, self.width, self.height)
        self.body.setPen(QPen(Qt.black, 1))
        self.body.setBrush(QColor(200, 200, 255, 180))
        self.addToGroup(self.body)
        
        # Create label
        self.label = QGraphicsTextItem(self.properties['name'])
        font = QFont()
        font.setPointSize(8)
        self.label.setFont(font)
        
        # Center the label beneath the device
        label_width = self.label.boundingRect().width()
        label_x = (self.width - label_width) / 2
        self.label.setPos(label_x, self.height + 5)
        self.addToGroup(self.label)
        
        # Create port indicators
        self._create_port_indicators()
    
    def _create_port_indicators(self):
        """Create visual indicators for ports."""
        from PyQt5.QtWidgets import QGraphicsEllipseItem
        
        # Port size
        port_size = 6
        half_port = port_size / 2
        
        # Create port indicators based on port positions
        for port in self.ports:
            if port['position'] == 'north':
                x = self.width / 2 - half_port
                y = -half_port
            elif port['position'] == 'east':
                x = self.width - half_port
                y = self.height / 2 - half_port
            elif port['position'] == 'south':
                x = self.width / 2 - half_port
                y = self.height - half_port
            elif port['position'] == 'west':
                x = -half_port
                y = self.height / 2 - half_port
            else:
                continue  # Skip unknown port positions
            
            port_indicator = QGraphicsEllipseItem(x, y, port_size, port_size)
            port_indicator.setPen(QPen(Qt.black, 1))
            port_indicator.setBrush(QColor(255, 255, 200))
            port_indicator.setToolTip(port['name'])
            
            # Store reference to the indicator in the port
            port['indicator'] = port_indicator
            self.addToGroup(port_indicator)
    
    def get_port_position(self, port_name):
        """Get the scene position of a port by name."""
        for port in self.ports:
            if port['name'] == port_name:
                if 'indicator' in port:
                    # Get center of the port indicator
                    indicator = port['indicator']
                    port_rect = indicator.rect()
                    port_center = QPointF(
                        port_rect.x() + port_rect.width() / 2,
                        port_rect.y() + port_rect.height() / 2
                    )
                    # Convert to scene coordinates
                    return self.mapToScene(port_center)
        
        # Default to center if port not found
        return self.mapToScene(QPointF(self.width / 2, self.height / 2))
    
    def get_closest_port(self, scene_pos):
        """Get the closest port to a scene position."""
        closest_port = None
        min_distance = float('inf')
        
        for port in self.ports:
            if 'indicator' in port:
                # Get center of the port indicator
                indicator = port['indicator']
                port_rect = indicator.rect()
                port_center = QPointF(
                    port_rect.x() + port_rect.width() / 2,
                    port_rect.y() + port_rect.height() / 2
                )
                port_scene_pos = self.mapToScene(port_center)
                
                # Calculate distance
                dx = port_scene_pos.x() - scene_pos.x()
                dy = port_scene_pos.y() - scene_pos.y()
                distance = (dx * dx + dy * dy) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_port = port
        
        return closest_port
    
    def itemChange(self, change, value):
        """Handle item changes."""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Update connected connections
            self.update_connections()
            
            # Update label position if needed
            if hasattr(self, 'label'):
                label_width = self.label.boundingRect().width()
                label_x = (self.width - label_width) / 2
                self.label.setPos(label_x, self.height + 5)
        
        return super().itemChange(change, value)
    
    def update_connections(self):
        """Update any connections attached to this device."""
        scene = self.scene()
        if scene:
            for item in scene.items():
                if hasattr(item, 'update_path') and hasattr(item, 'source_device') and hasattr(item, 'target_device'):
                    if item.source_device == self or item.target_device == self:
                        item.update_path()


class RouterDevice(DeviceItem):
    """Router device item."""
    
    def __init__(self, name=None, parent=None):
        """Initialize a router device item."""
        super().__init__(device_type="router", name=name, parent=parent)
    
    def _create_visual_representation(self):
        """Create the visual representation of the router."""
        from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsPolygonItem
        from PyQt5.QtGui import QPolygonF
        
        # Create body polygon (router shape)
        polygon = QPolygonF()
        polygon.append(QPointF(self.width / 2, 0))           # Top
        polygon.append(QPointF(self.width, self.height / 3))  # Right top
        polygon.append(QPointF(self.width, 2 * self.height / 3))  # Right bottom
        polygon.append(QPointF(self.width / 2, self.height))  # Bottom
        polygon.append(QPointF(0, 2 * self.height / 3))       # Left bottom
        polygon.append(QPointF(0, self.height / 3))           # Left top
        
        self.body = QGraphicsPolygonItem(polygon)
        self.body.setPen(QPen(Qt.black, 1))
        self.body.setBrush(QColor(200, 255, 200, 180))  # Light green
        self.addToGroup(self.body)
        
        # Create label
        self.label = QGraphicsTextItem(self.properties['name'])
        font = QFont()
        font.setPointSize(8)
        self.label.setFont(font)
        
        # Center the label beneath the device
        label_width = self.label.boundingRect().width()
        label_x = (self.width - label_width) / 2
        self.label.setPos(label_x, self.height + 5)
        self.addToGroup(self.label)
        
        # Create port indicators
        self._create_port_indicators()


class SwitchDevice(DeviceItem):
    """Switch device item."""
    
    def __init__(self, name=None, parent=None):
        """Initialize a switch device item."""
        super().__init__(device_type="switch", name=name, parent=parent)
    
    def _init_ports(self):
        """Initialize device ports with more ports for a switch."""
        self.ports = [
            {'name': 'Port 1', 'position': 'north', 'connected': False},
            {'name': 'Port 2', 'position': 'north-east', 'connected': False},
            {'name': 'Port 3', 'position': 'east', 'connected': False},
            {'name': 'Port 4', 'position': 'south-east', 'connected': False},
            {'name': 'Port 5', 'position': 'south', 'connected': False},
            {'name': 'Port 6', 'position': 'south-west', 'connected': False},
            {'name': 'Port 7', 'position': 'west', 'connected': False},
            {'name': 'Port 8', 'position': 'north-west', 'connected': False},
        ]
    
    def _create_visual_representation(self):
        """Create the visual representation of the switch."""
        from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
        
        # Create body rectangle (a bit wider for a switch)
        self.width = 70  # Make switch wider than generic device
        self.body = QGraphicsRectItem(0, 0, self.width, self.height)
        self.body.setPen(QPen(Qt.black, 1))
        self.body.setBrush(QColor(200, 230, 255, 180))  # Light blue
        self.addToGroup(self.body)
        
        # Create label
        self.label = QGraphicsTextItem(self.properties['name'])
        font = QFont()
        font.setPointSize(8)
        self.label.setFont(font)
        
        # Center the label beneath the device
        label_width = self.label.boundingRect().width()
        label_x = (self.width - label_width) / 2
        self.label.setPos(label_x, self.height + 5)
        self.addToGroup(self.label)
        
        # Create port indicators
        self._create_port_indicators()
    
    def _create_port_indicators(self):
        """Create visual indicators for ports."""
        from PyQt5.QtWidgets import QGraphicsEllipseItem
        
        # Port size
        port_size = 6
        half_port = port_size / 2
        
        # Create port indicators based on port positions
        for port in self.ports:
            if port['position'] == 'north':
                x = self.width / 2 - half_port
                y = -half_port
            elif port['position'] == 'north-east':
                x = self.width * 0.75 - half_port
                y = -half_port
            elif port['position'] == 'east':
                x = self.width - half_port
                y = self.height / 2 - half_port
            elif port['position'] == 'south-east':
                x = self.width * 0.75 - half_port
                y = self.height - half_port
            elif port['position'] == 'south':
                x = self.width / 2 - half_port
                y = self.height - half_port
            elif port['position'] == 'south-west':
                x = self.width * 0.25 - half_port
                y = self.height - half_port
            elif port['position'] == 'west':
                x = -half_port
                y = self.height / 2 - half_port
            elif port['position'] == 'north-west':
                x = self.width * 0.25 - half_port
                y = -half_port
            else:
                continue  # Skip unknown port positions
            
            port_indicator = QGraphicsEllipseItem(x, y, port_size, port_size)
            port_indicator.setPen(QPen(Qt.black, 1))
            port_indicator.setBrush(QColor(255, 255, 200))
            port_indicator.setToolTip(port['name'])
            
            # Store reference to the indicator in the port
            port['indicator'] = port_indicator
            self.addToGroup(port_indicator)


class ServerDevice(DeviceItem):
    """Server device item."""
    
    def __init__(self, name=None, parent=None):
        """Initialize a server device item."""
        super().__init__(device_type="server", name=name, parent=parent)
        
        # Adjust dimensions for server
        self.width = 50
        self.height = 80
    
    def _create_visual_representation(self):
        """Create the visual representation of the server."""
        from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem
        
        # Create body rectangle (taller for a server)
        self.body = QGraphicsRectItem(0, 0, self.width, self.height)
        self.body.setPen(QPen(Qt.black, 1))
        self.body.setBrush(QColor(255, 230, 200, 180))  # Light orange
        self.addToGroup(self.body)
        
        # Add server rack lines
        line_spacing = 10
        num_lines = int(self.height / line_spacing) - 1
        
        for i in range(1, num_lines + 1):
            y = i * line_spacing
            line = QGraphicsLineItem(0, y, self.width, y)
            line.setPen(QPen(Qt.gray, 0.5))
            self.addToGroup(line)
        
        # Create label
        self.label = QGraphicsTextItem(self.properties['name'])
        font = QFont()
        font.setPointSize(8)
        self.label.setFont(font)
        
        # Center the label beneath the device
        label_width = self.label.boundingRect().width()
        label_x = (self.width - label_width) / 2
        self.label.setPos(label_x, self.height + 5)
        self.addToGroup(self.label)
        
        # Create port indicators
        self._create_port_indicators()


class ClientDevice(DeviceItem):
    """Client device (PC/Workstation) item."""
    
    def __init__(self, name=None, parent=None):
        """Initialize a client device item."""
        super().__init__(device_type="client", name=name, parent=parent)
    
    def _init_ports(self):
        """Initialize device ports with fewer ports for a client."""
        self.ports = [
            {'name': 'Port 1', 'position': 'east', 'connected': False},
            {'name': 'Port 2', 'position': 'south', 'connected': False},
            {'name': 'Port 3', 'position': 'west', 'connected': False},
        ]
    
    def _create_visual_representation(self):
        """Create the visual representation of the client device."""
        from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem
        
        # Create monitor
        monitor_width = self.width
        monitor_height = self.height * 0.6
        self.monitor = QGraphicsRectItem(0, 0, monitor_width, monitor_height)
        self.monitor.setPen(QPen(Qt.black, 1))
        self.monitor.setBrush(QColor(255, 200, 255, 180))  # Light purple
        self.addToGroup(self.monitor)
        
        # Create screen
        screen_margin = 3
        screen_width = monitor_width - 2 * screen_margin
        screen_height = monitor_height - 2 * screen_margin
        self.screen = QGraphicsRectItem(
            screen_margin, 
            screen_margin, 
            screen_width, 
            screen_height
        )
        self.screen.setPen(QPen(Qt.black, 0.5))
        self.screen.setBrush(QColor(230, 230, 255, 180))  # Light blue for screen
        self.addToGroup(self.screen)
        
        # Create base
        base_width = monitor_width * 0.6
        base_height = self.height * 0.15
        base_x = (monitor_width - base_width) / 2
        base_y = monitor_height
        self.base = QGraphicsRectItem(base_x, base_y, base_width, base_height)
        self.base.setPen(QPen(Qt.black, 1))
        self.base.setBrush(QColor(200, 200, 200, 180))  # Gray
        self.addToGroup(self.base)
        
        # Create base support
        support_width = base_width * 0.8
        support_height = self.height * 0.25
        support_x = (monitor_width - support_width) / 2
        support_y = base_y + base_height
        self.support = QGraphicsRectItem(support_x, support_y, support_width, support_height)
        self.support.setPen(QPen(Qt.black, 1))
        self.support.setBrush(QColor(180, 180, 180, 180))  # Darker gray
        self.addToGroup(self.support)
        
        # Create label
        self.label = QGraphicsTextItem(self.properties['name'])
        font = QFont()
        font.setPointSize(8)
        self.label.setFont(font)
        
        # Center the label beneath the device
        label_width = self.label.boundingRect().width()
        label_x = (self.width - label_width) / 2
        self.label.setPos(label_x, self.height + 5)
        self.addToGroup(self.label)
        
        # Create port indicators
        self._create_port_indicators()


from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QPointF

# Use absolute imports for models
try:
    from src.models.device import Device

except ImportError:
    # Fallback to relative imports if absolute imports fail
    from ..models.device import Device

import uuid
from PyQt5.QtCore import QObject

class DeviceManager(QObject):
    """Manages the creation and tracking of devices in the network topology."""
    
    # Signals
    device_added = pyqtSignal(object)
    device_removed = pyqtSignal(object)
    device_selected = pyqtSignal(object)
    
    def __init__(self, scene=None):
        super().__init__()
        self.devices = {}  # Dictionary of devices by ID
        self.scene = scene
        self.selected_device = None
        self.selected_device_type = Device.ROUTER  # Default device type
    
    def create_device(self, device_type, x, y, name=None):
        """Create a device of the specified type at the given position."""
        try:
            # Use the Device class factory method
            device = Device.create(device_type, x, y, name)
            
            # Add to devices dictionary
            self.devices[device.id] = device
            
            # Add to scene if available
            if self.scene:
                self.scene.addItem(device)
                
                # Connect device signals
                device.selection_changed.connect(self._handle_device_selection)
                
                print(f"Created {device_type} at ({x}, {y})")
            else:
                print("Warning: No scene available to add device")
            
            # Emit signal
            self.device_added.emit(device)
            
            return device
        except Exception as e:
            print(f"Error creating device: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def remove_device(self, device_id):
        """Remove a device by ID."""
        if device_id in self.devices:
            device = self.devices[device_id]
            
            # Remove from scene
            if self.scene and device in self.scene.items():
                self.scene.removeItem(device)
            
            # Remove from dictionary
            del self.devices[device_id]
            
            # Update selected device if needed
            if self.selected_device and self.selected_device.id == device_id:
                self.selected_device = None
            
            # Emit signal
            self.device_removed.emit(device)
            
            print(f"Removed device: {device_id}")
            return True
        
        return False
    
    def _handle_device_selection(self, device, is_selected):
        """Handle device selection changes."""
        if is_selected:
            self.selected_device = device
            self.device_selected.emit(device)
            print(f"Selected device: {device.name}")
        elif self.selected_device == device:
            self.selected_device = None
    
    def get_device_by_id(self, device_id):
        """Get a device by ID."""
        return self.devices.get(device_id)
    
    def get_devices_by_type(self, device_type):
        """Get all devices of a specific type."""
        return [d for d in self.devices.values() if d.device_type == device_type]
    
    def set_selected_device_type(self, device_type):
        """Set the currently selected device type for creation."""
        if device_type in Device.get_available_types():
            self.selected_device_type = device_type
            print(f"Selected device type: {device_type}")
            return True
        
        print(f"Unknown device type: {device_type}")
        return False