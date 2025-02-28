from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPen, QBrush, QColor, QFont

class NetworkDevice(QGraphicsEllipseItem):
    def __init__(self, device_type, x=0, y=0, size=50):
        """Create a network device with the specified type and position."""
        super().__init__(x - size/2, y - size/2, size, size)
        
        self.device_type = device_type
        self.size = size
        
        # Setup visual appearance
        self.setPen(QPen(Qt.black, 2))
        self.setBrush(self._get_device_color())
        
        # Make it interactive
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)
        
        # Add label
        self.label = QGraphicsTextItem(self)
        self.label.setPlainText(device_type)
        self.label.setDefaultTextColor(Qt.black)
        self.center_label()
        
        # Device properties
        self.properties = {
            "name": device_type,
            "ip_address": "",
            "description": ""
        }
    
    def _get_device_color(self):
        """Return a color based on the device type."""
        colors = {
            "router": QColor(173, 216, 230),  # Light blue
            "switch": QColor(144, 238, 144),  # Light green
            "server": QColor(255, 182, 193),  # Light pink
            "firewall": QColor(255, 160, 122),  # Light salmon
            "desktop": QColor(221, 160, 221)   # Plum
        }
        return QBrush(colors.get(self.device_type.lower(), QColor(200, 200, 200)))
    
    def center_label(self):
        """Center the label within the device shape."""
        text_rect = self.label.boundingRect()
        self.label.setPos(
            (self.size - text_rect.width()) / 2,
            (self.size - text_rect.height()) / 2
        )
    
    def update_property(self, key, value):
        """Update a property of the device."""
        if key in self.properties:
            self.properties[key] = value
            if key == "name":
                self.label.setPlainText(value)
                self.center_label()
    
    def itemChange(self, change, value):
        """Handle item changes like selection and movement."""
        if change == QGraphicsItem.ItemSelectedChange:
            # Change appearance when selected
            if value:
                self.setPen(QPen(Qt.blue, 3))
            else:
                self.setPen(QPen(Qt.black, 2))
        return super().itemChange(change, value)