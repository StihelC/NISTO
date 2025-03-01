from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsItemGroup,
    QGraphicsPixmapItem,
    QGraphicsTextItem,
    QGraphicsRectItem
)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QPixmap, QColor, QBrush
import os

class NetworkDevice(QGraphicsItemGroup):
    """Represents a network device on the canvas as a group containing both icon and label."""
    
    # Class-level counter to generate unique names
    device_counts = {}
    
    def __init__(self, device_type, x=0, y=0, size=64):
        """Create a network device with the specified type and position."""
        super().__init__()
        
        self.device_type = device_type
        self.size = size
        
        # Make the group interactive
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # Keep track of device count for this type (for auto-naming)
        if device_type not in self.device_counts:
            self.device_counts[device_type] = 1
        else:
            self.device_counts[device_type] += 1
            
        # Create a default name
        default_name = f"{device_type.capitalize()}{self.device_counts[device_type]}"
        
        # Create the icon item
        self.icon_item = self._create_icon_item()
        self.addToGroup(self.icon_item)
        
        # Create the label item below the icon
        self.label_item = QGraphicsTextItem()
        self.label_item.setPlainText(default_name)
        self.label_item.setDefaultTextColor(Qt.black)
        
        # Center the label horizontally
        label_width = self.label_item.boundingRect().width()
        label_x = (self.size - label_width) / 2
        self.label_item.setPos(label_x, self.size + 5)
        
        self.addToGroup(self.label_item)
        
        # Position the entire group at the specified coordinates
        self.setPos(x - self.size/2, y - self.size/2)
        
        # Device properties
        self.properties = {
            "name": default_name,
            "ip_address": "",
            "description": ""
        }
    
    def _create_icon_item(self):
        """Create a QGraphicsPixmapItem with the device icon."""
        # Try to load the icon for this device type
        icon_path = f"src/resources/device_icons/{self.device_type}.png"
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                # If successfully loaded, use it
                if pixmap.width() != self.size or pixmap.height() != self.size:
                    pixmap = pixmap.scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_item = QGraphicsPixmapItem(pixmap)
                return icon_item
        
        # If no icon found or loading failed, create a colored rectangle
        rect_item = QGraphicsRectItem(0, 0, self.size, self.size)
        rect_item.setBrush(QBrush(QColor(200, 200, 255)))  # Light blue
        rect_item.setPen(QPen(Qt.black, 2))
        
        # Add text to the rectangle
        text_item = QGraphicsTextItem(self.device_type)
        text_item.setDefaultTextColor(Qt.black)
        text_width = text_item.boundingRect().width()
        text_height = text_item.boundingRect().height()
        text_x = (self.size - text_width) / 2
        text_y = (self.size - text_height) / 2
        text_item.setPos(text_x, text_y)
        
        # Create a mini-group for the rectangle and its text
        rect_group = QGraphicsItemGroup()
        rect_group.addToGroup(rect_item)
        rect_group.addToGroup(text_item)
        
        return rect_group
    
    def update_property(self, key, value):
        """Update a property of the device."""
        if key in self.properties:
            self.properties[key] = value
            if key == "name":
                self.label_item.setPlainText(value)
                # Re-center the label after text change
                label_width = self.label_item.boundingRect().width()
                label_x = (self.size - label_width) / 2
                self.label_item.setPos(label_x, self.size + 5)

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