from PyQt5.QtWidgets import QGraphicsLineItem
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import Qt, QLineF

class Connection(QGraphicsLineItem):
    """Represents a network connection between two devices."""
    
    def __init__(self, source_device, target_device, connection_type="ethernet", 
                 source_port=None, target_port=None):
        """Initialize a connection between two devices."""
        super().__init__()
        
        # Store connection properties
        self.source_device = source_device
        self.target_device = target_device
        self.connection_type = connection_type
        self.source_port = source_port
        self.target_port = target_port
        
        # Style based on connection type
        pen = QPen(Qt.black, 2)
        self.setPen(pen)
        
        # Make selectable
        self.setFlag(QGraphicsLineItem.ItemIsSelectable, True)
        
        # Initial position update
        self.update_position()
        
    def update_position(self):
        """Update the connection line position based on device positions."""
        if not (self.source_device and self.target_device):
            return
            
        # Get device positions & centers
        source_pos = self.source_device.pos()
        target_pos = self.target_device.pos()
        source_size = getattr(self.source_device, 'size', 40)
        target_size = getattr(self.target_device, 'size', 40)
        source_center_x = source_pos.x() + source_size/2
        source_center_y = source_pos.y() + source_size/2
        target_center_x = target_pos.x() + target_size/2
        target_center_y = target_pos.y() + target_size/2
        
        # Create line between centers
        line = QLineF(source_center_x, source_center_y, target_center_x, target_center_y)
        self.setLine(line)