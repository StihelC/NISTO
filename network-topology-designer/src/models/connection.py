from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtGui import QPen, QColor, QPainterPath, QFont, QBrush
from PyQt5.QtCore import Qt, QPointF
import math

class NetworkConnection(QGraphicsPathItem):
    """Represents a connection between two network devices."""
    
    def __init__(self, source_device, target_device, connection_type="ethernet",
                 source_port=None, target_port=None, parent=None):
        super().__init__(parent)
        self.source_device = source_device
        self.target_device = target_device
        self.connection_type = connection_type
        self.source_port = source_port
        self.target_port = target_port
        
        # Set appearance
        self.setPen(QPen(QColor(0, 0, 0), 2))
        self.setZValue(-1)  # Draw beneath devices
        
        # Create a path between devices
        self.path = QPainterPath()
        self.update_path()
        
        # Create a label for the connection
        self.label = QGraphicsTextItem(self)
        self.label.setPlainText(self.connection_type)
        self.label.setDefaultTextColor(QColor(0, 0, 0))
        self.update_label_position()
        
    def update_path(self):
        """Update the connection path based on device positions and ports."""
        if not self.source_device or not self.target_device:
            return
            
        # Get the source and target points based on port positions
        if self.source_port and hasattr(self.source_device, 'get_port_position'):
            source_point = self.source_device.get_port_position(self.source_port)
        else:
            source_point = self.source_device.sceneBoundingRect().center()
            
        if self.target_port and hasattr(self.target_device, 'get_port_position'):
            target_point = self.target_device.get_port_position(self.target_port)
        else:
            target_point = self.target_device.sceneBoundingRect().center()
        
        # Create a smooth path
        self.path = QPainterPath()
        self.path.moveTo(source_point)
        
        # Calculate midpoint for control points
        mid_x = (source_point.x() + target_point.x()) / 2
        mid_y = (source_point.y() + target_point.y()) / 2
        
        # Calculate distance between points
        import math
        dx = target_point.x() - source_point.x()
        dy = target_point.y() - source_point.y()
        distance = math.sqrt(dx*dx + dy*dy)
        
        # For shorter connections, use a straight line
        if distance < 100:
            self.path.lineTo(target_point)
        else:
            # For longer connections, use a curved path
            control1 = QPointF(mid_x, source_point.y())
            control2 = QPointF(mid_x, target_point.y())
            self.path.cubicTo(control1, control2, target_point)
        
        # Set the path
        self.setPath(self.path)
        
        # Update the label position
        self.update_label_position()
    
    def update_label_position(self):
        """Update the position of the connection label."""
        if not self.path or self.path.isEmpty():
            return
            
        # Position the label at the middle of the path
        percent = 0.5  # midpoint
        point = self.path.pointAtPercent(percent)
        
        # Offset the label slightly above the path
        self.label.setPos(point.x() - 20, point.y() - 15)
        
    def paint(self, painter, option, widget):
        """Override paint to customize appearance based on connection type."""
        # Style based on connection type
        if self.connection_type.lower() == "ethernet":
            self.setPen(QPen(QColor(0, 0, 200), 2))
        elif self.connection_type.lower() == "wireless":
            # Use a dashed line for wireless
            pen = QPen(QColor(0, 150, 0), 2, Qt.DashLine)
            self.setPen(pen)
        elif self.connection_type.lower() == "serial":
            self.setPen(QPen(QColor(200, 0, 0), 2))
        else:
            self.setPen(QPen(QColor(0, 0, 0), 2))
            
        # Call the parent class paint method
        super().paint(painter, option, widget)