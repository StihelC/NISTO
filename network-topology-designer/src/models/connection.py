from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtGui import QPen, QColor, QPainterPath, QFont, QBrush
from PyQt5.QtCore import Qt, QPointF
import math

class NetworkConnection(QGraphicsPathItem):
    """Represents a connection/link between network devices."""
    
    # Connection types with different visual styles
    CONNECTION_TYPES = {
        "ethernet": {"color": Qt.black, "style": Qt.SolidLine, "width": 2, "dash": None},
        "fiber": {"color": QColor(0, 100, 200), "style": Qt.SolidLine, "width": 3, "dash": None},
        "wireless": {"color": QColor(0, 200, 0), "style": Qt.DashLine, "width": 2, "dash": [5, 5]},
        "wan": {"color": QColor(200, 0, 0), "style": Qt.SolidLine, "width": 3, "dash": None},
        "default": {"color": Qt.black, "style": Qt.SolidLine, "width": 2, "dash": None}
    }
    
    def __init__(self, source_device, target_device, connection_type="ethernet", 
                 source_port=None, target_port=None):
        super().__init__()
        
        self.source_device = source_device
        self.target_device = target_device
        self.connection_type = connection_type
        self.source_port = source_port
        self.target_port = target_port
        
        # Make connections selectable
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        
        # Initialize the path
        self.path = QPainterPath()
        
        # Set appearance based on connection type
        self.style = self.CONNECTION_TYPES.get(connection_type, self.CONNECTION_TYPES["default"])
        
        # Set the pen for drawing
        pen = QPen(self.style["color"], self.style["width"], self.style["style"])
        if self.style["dash"]:
            pen.setDashPattern(self.style["dash"])
        self.setPen(pen)
        
        # Create a label for the connection (bandwidth, name, etc.)
        self.label = QGraphicsTextItem("", parent=self)
        self.label.setDefaultTextColor(Qt.black)
        
        # Connection properties
        self.properties = {
            "name": f"Connection_{id(self)}",
            "bandwidth": "1 Gbps",
            "latency": "0ms",
            "description": "",
            "source_port": source_port,
            "target_port": target_port
        }
        
        # Initial update
        self.update_path()
        
    def update_property(self, key, value):
        """Update a property of the connection."""
        if key in self.properties:
            self.properties[key] = value
            
            # Update label text if needed
            self.update_label()
    
    def update_path(self):
        """Update the connection path based on device positions and ports."""
        if not self.source_device or not self.target_device:
            return
            
        # Get the source and target points based on port positions
        if self.source_port and self.source_port in self.source_device.ports:
            source_point = self.source_device.get_port_position(self.source_port)
        else:
            source_point = self.source_device.sceneBoundingRect().center()
            
        if self.target_port and self.target_port in self.target_device.ports:
            target_point = self.target_device.get_port_position(self.target_port)
        else:
            target_point = self.target_device.sceneBoundingRect().center()
        
        # Create a path from source to target
        self.path = QPainterPath()
        
        # Create a nice curve between the points
        dx = target_point.x() - source_point.x()
        dy = target_point.y() - source_point.y()
        dist = math.sqrt(dx*dx + dy*dy)
        
        # Create control points for a smooth curve
        control_dist = dist * 0.4
        
        # Basic bezier path
        self.path.moveTo(source_point)
        
        # For straight connections, use a line
        if abs(dx) < 20 or abs(dy) < 20:
            self.path.lineTo(target_point)
        else:
            # For angled connections, use a curve
            self.path.cubicTo(
                source_point.x() + dx * 0.25, source_point.y() + dy * 0.25,
                source_point.x() + dx * 0.75, source_point.y() + dy * 0.75,
                target_point.x(), target_point.y()
            )
        
        # Set the path
        self.setPath(self.path)
        
        # Update the label position
        self.update_label_position()
    
    def update_label_position(self):
        """Update the position of the connection label."""
        # Place the label at the middle of the path
        if not self.path:
            return
            
        # Get the middle point of the path
        path_length = self.path.length()
        middle_percent = 0.5  # halfway point
        middle_point = self.path.pointAtPercent(middle_percent)
        
        # Position the label at the middle point, slightly offset
        self.label.setPos(middle_point.x() - self.label.boundingRect().width()/2, 
                          middle_point.y() - self.label.boundingRect().height() - 5)
    
    def update_label(self):
        """Update the label text based on properties."""
        # Create label text from properties
        text = f"{self.properties['name']}\n{self.properties['bandwidth']}"
        
        # Update the text
        self.label.setPlainText(text)
        
        # Re-position after text change
        self.update_label_position()
    
    def paint(self, painter, option, widget=None):
        """Custom paint method to draw connection with enhancements."""
        # Draw the basic path
        super().paint(painter, option, widget)
        
        # Extract the source and target points
        if not self.source_device or not self.target_device:
            return
            
        source_center = self.mapFromScene(self.source_device.sceneBoundingRect().center())
        target_center = self.mapFromScene(self.target_device.sceneBoundingRect().center())
        
        # Draw arrows to indicate direction if needed
        if self.connection_type != "wireless":
            # Calculate the angle of the line
            dx = target_center.x() - source_center.x()
            dy = target_center.y() - source_center.y()
            angle = math.atan2(dy, dx)
            
            # Draw arrow near the target
            arrow_size = 10
            arrow_point = QPointF(
                target_center.x() - 20 * math.cos(angle),
                target_center.y() - 20 * math.sin(angle)
            )
            
            # Create the arrow path
            arrow_path = QPainterPath()
            arrow_path.moveTo(arrow_point)
            arrow_path.lineTo(
                arrow_point.x() - arrow_size * math.cos(angle - math.pi/6),
                arrow_point.y() - arrow_size * math.sin(angle - math.pi/6)
            )
            arrow_path.lineTo(
                arrow_point.x() - arrow_size * math.cos(angle + math.pi/6),
                arrow_point.y() - arrow_size * math.sin(angle + math.pi/6)
            )
            arrow_path.closeSubpath()
            
            # Fill the arrow
            painter.setBrush(QBrush(self.pen().color()))
            painter.drawPath(arrow_path)