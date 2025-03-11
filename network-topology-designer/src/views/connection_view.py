from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtGui import QPainterPath, QPen, QColor
from PyQt5.QtCore import Qt, QPointF

class ConnectionView(QGraphicsPathItem):
    """Visual representation of a connection between devices."""
    
    def __init__(self, connection_model):
        """Initialize the connection view."""
        super().__init__()
        
        self.connection_model = connection_model
        
        # Set appearance
        self.setZValue(-1)  # Place connections behind devices
        self.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        
        # Set flags
        self.setFlag(QGraphicsPathItem.ItemIsSelectable)
        
        # Create the path
        self.update_from_model()
    
    def update_from_model(self):
        """Update the view based on the model data."""
        if not self.connection_model:
            return
            
        # Get source and target devices
        source_device = self.connection_model.source_device
        target_device = self.connection_model.target_device
        
        if not (source_device and target_device and 
                source_device.view and target_device.view):
            return
        
        # Get connection points
        source_port = self.connection_model.source_port
        target_port = self.connection_model.target_port
        
        # Get positions from device views
        if source_port:
            source_point = source_device.view.get_port_position(source_port)
        else:
            source_point = source_device.view.get_center_point()
        
        if target_port:
            target_point = target_device.view.get_port_position(target_port)
        else:
            target_point = target_device.view.get_center_point()
        
        # Create path
        path = QPainterPath()
        path.moveTo(source_point)
        
        # Create a slight curve
        dx = target_point.x() - source_point.x()
        dy = target_point.y() - source_point.y()
        distance = (dx * dx + dy * dy) ** 0.5
        
        # Control point offsets
        offset_factor = min(40, distance * 0.25)
        
        if abs(dx) > abs(dy):
            # More horizontal than vertical
            ctrl1 = QPointF(source_point.x() + offset_factor, source_point.y())
            ctrl2 = QPointF(target_point.x() - offset_factor, target_point.y())
        else:
            # More vertical than horizontal
            ctrl1 = QPointF(source_point.x(), source_point.y() + offset_factor)
            ctrl2 = QPointF(target_point.x(), target_point.y() - offset_factor)
        
        # Create cubic Bezier curve
        path.cubicTo(ctrl1, ctrl2, target_point)
        
        # Set path
        self.setPath(path)
        
        # Update appearance based on connection type and properties
        self._update_appearance()
    
    def _update_appearance(self):
        """Update the connection appearance based on its model."""
        if not self.connection_model:
            return
            
        # Default appearance
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        
        # Customize based on connection type
        if self.connection_model.connection_type == "ethernet":
            pen.setColor(QColor(0, 0, 200))  # Blue
        elif self.connection_model.connection_type == "fiber":
            pen.setColor(QColor(200, 100, 0))  # Orange
            pen.setWidth(3)
        elif self.connection_model.connection_type == "wireless":
            pen.setColor(QColor(0, 150, 0))  # Green
            pen.setStyle(Qt.DashLine)
        elif self.connection_model.connection_type == "wan":
            pen.setColor(QColor(150, 0, 150))  # Purple
            pen.setWidth(3)
        
        # Apply status changes
        if self.connection_model.properties.get('status') == 'inactive':
            pen.setColor(QColor(150, 150, 150))  # Gray out for inactive
        elif self.connection_model.properties.get('status') == 'error':
            pen.setColor(QColor(255, 0, 0))  # Red for error
        
        # Apply the pen
        self.setPen(pen)
    
    def get_center_point(self):
        """Get the center point of the connection path."""
        path = self.path()
        if path.isEmpty():
            return QPointF(0, 0)
            
        return path.pointAtPercent(0.5)