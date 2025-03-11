from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsTextItem
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPolygonF, QPen, QColor, QFont

from models.network_device import NetworkDevice
import uuid

class RouterDevice(NetworkDevice):
    """Model class representing a router device."""
    
    def __init__(self, name=None, x=0, y=0):
        device_id = str(uuid.uuid4())
        name = name or f"Router {device_id[:4]}"
        super().__init__(device_id, name, "router", x, y)
    
    def _create_visual_representation(self):
        """Create the visual representation of the router."""
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