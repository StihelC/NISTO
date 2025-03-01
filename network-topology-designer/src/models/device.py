from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsRectItem,  # Make sure this is imported
    QGraphicsPixmapItem, 
    QGraphicsTextItem,
    QMenu,  # Include if you use context menus
    QGraphicsSceneContextMenuEvent  # Include if you handle context menu events
)
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPen, QPixmap, QColor, QBrush, QFont, QPainter
import os

# First class - NetworkDevice for icon-based devices
class NetworkDevice(QGraphicsPixmapItem):
    """Represents a network device on the canvas using an icon."""
    
    def __init__(self, device_type, x=0, y=0, size=64):
        # Load the device icon
        icon_path = f"src/resources/device_icons/{device_type}.png"
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
        else:
            # Create a simple colored square as fallback
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(200, 200, 255))
        
        # Initialize with the pixmap
        super().__init__(pixmap)
        
        # Make it interactive
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        
        # Position the device (centered on the provided coordinates)
        self.setPos(x - size/2, y - size/2)
        
        # Store device info
        self.device_type = device_type
        self.size = size
        
        # Create a label for the device
        self.label = QGraphicsTextItem(device_type)
        self.label.setDefaultTextColor(Qt.black)
        
        # Device properties
        self.properties = {
            "name": device_type,
            "ip_address": "",
            "description": ""
        }
    
    def update_property(self, key, value):
        """Update a property of the device."""
        if key in self.properties:
            self.properties[key] = value
            if key == "name":
                self.label.setPlainText(value)

# Second class - Device for rectangle-based devices
# You can keep this if needed or remove it if not used
class Device(QGraphicsRectItem):
    """Represents a network device on the canvas using a rectangle."""
    
    def __init__(self, x, y, device_type, name=None):
        super().__init__(x, y, 80, 80)
        self.device_type = device_type
        self.name = name or f"{device_type}_{id(self)}"
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # Set appearance
        self.setBrush(QBrush(QColor(200, 230, 255)))
        self.setPen(QPen(Qt.black, 2))
        
    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        
        # Draw the device type and name
        painter.setFont(QFont("Arial", 10))
        rect = self.boundingRect()
        painter.drawText(rect, Qt.AlignCenter, f"{self.device_type}\n{self.name}")