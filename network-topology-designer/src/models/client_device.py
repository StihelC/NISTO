from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem
from PyQt5.QtGui import QPen, QColor, QFont
from PyQt5.QtCore import Qt

from models.device_item import DeviceItem

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