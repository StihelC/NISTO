from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem
from PyQt5.QtGui import QPen, QColor, QFont
from PyQt5.QtCore import Qt

from models.device_item import DeviceItem
from models.network_device import NetworkDevice
import uuid

class ServerDevice(NetworkDevice):
    """Model class representing a server device."""
    
    def __init__(self, name=None, x=0, y=0):
        device_id = str(uuid.uuid4())
        name = name or f"Server {device_id[:4]}"
        super().__init__(device_id, name, "server", x, y)
        
        # Adjust dimensions for server
        self.width = 50
        self.height = 80
    
    def _create_visual_representation(self):
        """Create the visual representation of the server."""
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