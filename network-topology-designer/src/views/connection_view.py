from PyQt5.QtWidgets import QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QColor

class ConnectionView(QGraphicsLineItem):
    """Visual representation of a connection between devices."""
    
    # Connection type styles
    STYLES = {
        "standard": {"color": Qt.black, "width": 1, "style": Qt.SolidLine},
        "ethernet": {"color": QColor(0, 0, 200), "width": 2, "style": Qt.SolidLine},
        "fiber": {"color": QColor(255, 165, 0), "width": 2, "style": Qt.DashLine},
        "wireless": {"color": QColor(0, 150, 0), "width": 1, "style": Qt.DotLine}
    }
    
    def __init__(self, connection_model):
        """Initialize the connection view."""
        super().__init__()
        
        self.connection_model = connection_model
        
        # Set flags
        self.setFlag(QGraphicsLineItem.ItemIsSelectable)
        
        # Apply style based on connection type
        self._apply_style()
        
        # Update position
        self.update_position()
    
    def _apply_style(self):
        """Apply visual style based on connection type."""
        conn_type = self.connection_model.connection_type.lower()
        style = self.STYLES.get(conn_type, self.STYLES["standard"])
        
        pen = QPen(style["color"], style["width"], style["style"])
        self.setPen(pen)
    
    def update_position(self):
        """Update the connection position based on connected devices."""
        source = self.connection_model.source_device
        target = self.connection_model.target_device
        
        if not source or not target:
            return
            
        # Get device center points
        source_center = QPointF(source.x + 40, source.y + 25)  # Half of the 80x50 rectangle
        target_center = QPointF(target.x + 40, target.y + 25)
        
        # Update line position
        self.setLine(source_center.x(), source_center.y(),
                    target_center.x(), target_center.y())