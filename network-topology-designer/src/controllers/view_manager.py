from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRectF, QPointF

class ViewManager:
    """Manages view operations such as zoom, pan, and view transformations."""
    
    def __init__(self, main_window, view, scene, canvas_controller=None):
        """Initialize the view manager."""
        self.main_window = main_window
        self.view = view
        self.scene = scene
        self.canvas_controller = canvas_controller
        
        # Initialize view settings
        self.current_zoom = 1.0
        self.zoom_factor = 1.25
        self.min_zoom = 0.25
        self.max_zoom = 4.0
        
        # Set up view
        self._setup_view()
    
    def _setup_view(self):
        """Set up the view."""
        # No need to add grid here - let canvas_controller handle it
        self._add_border()
    
    # Remove or comment out the _add_grid method, or modify it to use canvas_controller:
    # def _add_grid(self):
    #     """Add a background grid to the scene."""
    #     if self.canvas_controller:
    #         self.canvas_controller.add_grid()
    
    def _add_border(self):
        """Add a border to the scene."""
        from PyQt5.QtWidgets import QGraphicsRectItem
        border_rect = QGraphicsRectItem(-500, -500, 1000, 1000)
        border_rect.setPen(QPen(Qt.gray, 1, Qt.DashLine))
        self.scene.addItem(border_rect)
    
    def zoom_in(self):
        """Zoom in on the view."""
        # Check if we'll exceed max zoom
        if self.current_zoom * self.zoom_factor <= self.max_zoom:
            self.view.scale(self.zoom_factor, self.zoom_factor)
            self.current_zoom *= self.zoom_factor
            self._update_status()
    
    def zoom_out(self):
        """Zoom out on the view."""
        # Check if we'll exceed min zoom
        if self.current_zoom / self.zoom_factor >= self.min_zoom:
            self.view.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
            self.current_zoom /= self.zoom_factor
            self._update_status()
    
    def reset_view(self):
        """Reset view to default zoom and position."""
        # Reset transformation
        self.view.resetTransform()
        self.current_zoom = 1.0
        self._update_status()
    
    def fit_to_content(self):
        """Fit all content in view."""
        # Get the scene rect containing all items
        content_rect = self.scene.itemsBoundingRect()
        
        # Add some padding
        padding = 50
        content_rect.adjust(-padding, -padding, padding, padding)
        
        # Fit in view with some margin
        self.view.fitInView(content_rect, Qt.KeepAspectRatio)
        
        # Update current zoom based on the transformation
        transform = self.view.transform()
        # Take the average of horizontal and vertical scale factors
        self.current_zoom = (transform.m11() + transform.m22()) / 2
        
        self._update_status()
    
    def center_on_point(self, point):
        """Center the view on a specific point."""
        self.view.centerOn(point)
    
    def center_on_item(self, item):
        """Center the view on a specific item."""
        if item:
            scene_pos = item.scenePos()
            self.view.centerOn(scene_pos)
    
    def get_center_point(self):
        """Get the center point of the current view."""
        view_center = self.view.viewport().rect().center()
        return self.view.mapToScene(view_center)
    
    def map_to_scene(self, view_pos):
        """Map a view position to scene coordinates."""
        return self.view.mapToScene(view_pos)
    
    def map_from_scene(self, scene_pos):
        """Map a scene position to view coordinates."""
        return self.view.mapFromScene(scene_pos)
    
    def set_devices_draggable(self, draggable=True):
        """Enable or disable dragging for all devices in the scene."""
       
        from PyQt5.QtWidgets import QGraphicsItem
        
        for item in self.scene.items():
            if isinstance(item):
                item.setFlag(QGraphicsItem.ItemIsMovable, draggable)
    
    def _update_status(self):
        """Update status bar with zoom information."""
        zoom_percent = int(self.current_zoom * 100)
        self.main_window.statusBar().showMessage(f"Zoom: {zoom_percent}%")