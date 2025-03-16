from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPen, QColor

class TopologyScene(QGraphicsScene):
    """Custom scene for the network topology."""
    
    # Add these signals if they don't exist
    mouse_press_signal = pyqtSignal(object)
    mouse_move_signal = pyqtSignal(object)
    mouse_release_signal = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.setSceneRect(-2000, -2000, 4000, 4000)
        print("TopologyScene initialized")
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        # Emit our custom signal
        self.mouse_press_signal.emit(event)
        # Let the parent class handle the event too
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        # Emit our custom signal
        self.mouse_move_signal.emit(event)
        # Let the parent class handle the event too
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        # Emit our custom signal
        self.mouse_release_signal.emit(event)
        # Let the parent class handle the event too
        super().mouseReleaseEvent(event)
        
    def drawBackground(self, painter, rect):
        """Override to prevent grid drawing."""
        # Just fill with background color
        painter.fillRect(rect, self.backgroundBrush())