from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt

class ViewManager:
    """Manages the graphics view configuration and operations."""
    
    def __init__(self, main_window, graphics_view, scene):
        self.main_window = main_window
        self.view = graphics_view
        self.scene = scene
        
        # Configure the view for optimal rendering
        self._configure_view()
        
        # Add background elements
        self._add_grid()
        self._add_border()
    
    def _configure_view(self):
        """Configure graphics view settings."""
        # Quality settings
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # Interaction settings
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setInteractive(True)
        
        # Transformation settings
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
    
    def _add_grid(self):
        """Add a background grid to the scene."""
        grid_size = 50
        grid_color = QColor(230, 230, 230)
        
        # Draw vertical lines
        for x in range(-1000, 1000, grid_size):
            line = self.scene.addLine(x, -1000, x, 1000, QPen(grid_color))
            line.setZValue(-1)  # Put grid behind other items
        
        # Draw horizontal lines
        for y in range(-1000, 1000, grid_size):
            line = self.scene.addLine(-1000, y, 1000, y, QPen(grid_color))
            line.setZValue(-1)  # Put grid behind other items
        
        # Add coordinate axis
        x_axis = self.scene.addLine(-1000, 0, 1000, 0, QPen(Qt.red, 1))
        y_axis = self.scene.addLine(0, -1000, 0, 1000, QPen(Qt.green, 1))
        x_axis.setZValue(-0.5)
        y_axis.setZValue(-0.5)
    
    def _add_border(self):
        """Add a border to the scene."""
        from PyQt5.QtWidgets import QGraphicsRectItem
        border_rect = QGraphicsRectItem(-500, -500, 1000, 1000)
        border_rect.setPen(QPen(Qt.gray, 1, Qt.DashLine))
        self.scene.addItem(border_rect)
    
    def zoom_in(self):
        """Zoom in the view."""
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        """Zoom out the view."""
        self.view.scale(1/1.2, 1/1.2)

    def reset_view(self):
        """Reset the view to default."""
        self.view.resetTransform()
    
    def set_devices_draggable(self, draggable=True):
        """Enable or disable dragging for all devices in the scene."""
        from models.device import NetworkDevice
        from PyQt5.QtWidgets import QGraphicsItem
        
        for item in self.scene.items():
            if isinstance(item, NetworkDevice):
                item.setFlag(QGraphicsItem.ItemIsMovable, draggable)