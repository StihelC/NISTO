from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QFont

from models.device_item import DeviceItem
from models.network_device import NetworkDevice
import uuid

class SwitchDevice(NetworkDevice):
    """Model class representing a switch device."""
    
    def __init__(self, name=None, x=0, y=0):
        device_id = str(uuid.uuid4())
        name = name or f"Switch {device_id[:4]}"
        super().__init__(device_id, name, "switch", x, y)
    
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