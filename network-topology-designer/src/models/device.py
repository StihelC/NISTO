from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QFont
from PyQt5.QtCore import Qt, QRectF, QTimer

# Add sys path to ensure imports work
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.resource_manager import ResourceManager

class NetworkDevice(QGraphicsItem):
    """Represents a network device on the canvas."""
    
    def __init__(self, device_type, x, y, size=40):
        super().__init__()
        self.device_type = device_type
        self.size = size
        self.ports = {}
        self.properties = {}
        
        # Position device with center at click point
        self.setPos(x - size/2, y - size/2)
        
        # Load icon
        self.icon_pixmap = ResourceManager.load_device_icon(device_type, size)
        
        # Set flags
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
    
    def boundingRect(self):
        """Define the bounding rectangle for this item."""
        from PyQt5.QtCore import QRectF
        
        # Ensure bounding rectangle includes space for labels, but with LESS padding
        label_height = 0
        if hasattr(self, 'label'):
            label_height += self.label.boundingRect().height()
        if hasattr(self, 'ip_label'):
            label_height += self.ip_label.boundingRect().height()
            
        # Add less padding (reduced from +20 to +10)
        total_height = self.size + label_height + 10  # REDUCED PADDING HERE
        
        # Center the device in the bounding rect
        return QRectF(-self.size/2, -self.size/2, self.size, total_height)
    
    def paint(self, painter, option, widget):
        """Paint the device icon."""
        from PyQt5.QtCore import QRectF
        
        # Draw the device icon centered at (0,0)
        if hasattr(self, 'icon_pixmap') and not self.icon_pixmap.isNull():
            # Use QRectF to handle floating point coordinates
            target_rect = QRectF(-self.size/2, -self.size/2, self.size, self.size)
            painter.drawPixmap(target_rect, self.icon_pixmap, QRectF(self.icon_pixmap.rect()))
        
        # Draw selection rectangle if selected
        if self.isSelected():
            from PyQt5.QtGui import QPen, QColor
            from PyQt5.QtCore import Qt
            painter.setPen(QPen(QColor(0, 120, 215), 2, Qt.DashLine))
            # Create a QRectF for the selection rectangle
            selection_rect = QRectF(-self.size/2, -self.size/2, self.size, self.size)
            painter.drawRect(selection_rect)
    
    def update_property(self, key, value):
        """Update a device property and refresh display if needed."""
        if not hasattr(self, 'properties'):
            self.properties = {}
        
        self.properties[key] = value
        
        # Handle name label
        if key == 'name':
            if not hasattr(self, 'label'):
                from PyQt5.QtWidgets import QGraphicsTextItem
                from PyQt5.QtCore import Qt
                
                # Create as CHILD item instead of separate scene item
                self.label = QGraphicsTextItem(self)  # Make it a child of device
                self.label.setDefaultTextColor(Qt.black)
            
            # Update text
            self.label.setPlainText(value)
            
            # Position centered below device with LESS spacing (reduced from +5 to +2)
            label_width = self.label.boundingRect().width()
            self.label.setPos(-label_width/2, self.size/2 + 2)  # REDUCED SPACING HERE
        
        # Handle IP address label
        elif key == 'ip_address' and value:
            if not hasattr(self, 'ip_label'):
                from PyQt5.QtWidgets import QGraphicsTextItem
                from PyQt5.QtCore import Qt
                from PyQt5.QtGui import QFont
                
                # Create as CHILD item
                self.ip_label = QGraphicsTextItem(self)
                font = QFont()
                font.setPointSize(8)  # Keep small font
                self.ip_label.setFont(font)
                self.ip_label.setDefaultTextColor(Qt.darkBlue)
            
            # Update text
            self.ip_label.setPlainText(value)
            
            # Position centered below name with LESS spacing (reduced from +10 to +4)
            ip_width = self.ip_label.boundingRect().width()
            name_height = 0
            if hasattr(self, 'label'):
                name_height = self.label.boundingRect().height()
            
            # Reduced vertical spacing
            self.ip_label.setPos(-ip_width/2, self.size/2 + name_height + 4)  # REDUCED SPACING HERE
        
        # Update tooltip
        tooltip = ""
        for prop_key, prop_value in self.properties.items():
            if prop_value:
                tooltip += f"{prop_key}: {prop_value}\n"
        self.setToolTip(tooltip.strip())
        
        return True
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            # Update label positions when device moves
            QTimer.singleShot(0, self._update_label_positions)
        
        return super().itemChange(change, value)
    
    def _update_label_positions(self):
        """Update the positions of all labels when device moves."""
        if not self.scene():
            return
        
        # Update name label position
        if hasattr(self, 'label') and self.label:
            label_width = self.label.boundingRect().width()
            device_center_x = self.x() + self.size/2
            device_bottom_y = self.y() + self.size
            self.label.setPos(device_center_x - label_width/2, device_bottom_y + 5)
        
        # Update IP label position
        if hasattr(self, 'ip_label') and self.ip_label:
            ip_width = self.ip_label.boundingRect().width()
            name_height = 0
            if hasattr(self, 'label'):
                name_height = self.label.boundingRect().height()
            
            device_center_x = self.x() + self.size/2
            device_bottom_y = self.y() + self.size
            self.ip_label.setPos(device_center_x - ip_width/2, 
                                device_bottom_y + name_height + 10)
    
    def _create_ports(self):
        """Create ports around the device."""
        from PyQt5.QtWidgets import QGraphicsEllipseItem
        from PyQt5.QtGui import QBrush, QColor
        from PyQt5.QtCore import Qt, QRectF
        
        port_size = 8
        device_size = self.size
        
        # Use QRectF for all port creation to handle floating point positions
        # Example for top ports:
        spacing = device_size / (self.num_ports_per_side + 1)
        for i in range(self.num_ports_per_side):
            port_id = f"top_{i}"
            x_pos = -device_size/2 + spacing * (i + 1) - port_size/2
            y_pos = -device_size/2 - port_size/2
            
            # Use QRectF instead of direct coordinates
            port_rect = QRectF(x_pos, y_pos, port_size, port_size)
            port = QGraphicsEllipseItem(port_rect, self)
            # Rest of port creation...


