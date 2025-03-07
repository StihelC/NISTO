from PyQt5.QtCore import QObject, Qt, QPointF, QEvent
from PyQt5.QtGui import QPen, QColor, QMouseEvent
import traceback

class MouseHandler(QObject):
    """Handles mouse events for the network topology designer."""
    
    def __init__(self, view, scene, canvas_controller, mode_manager=None):
        """Initialize with required components."""
        super().__init__()
        self.view = view
        self.scene = scene
        self.canvas = canvas_controller
        self.mode_manager = mode_manager
        
        # State for tracking drag operations
        self.dragging = False
        self.drag_start = None
        self.drag_item = None
        self.temp_items = []  # Temporary items for visual feedback
        
        # Mouse tracking
        self.last_pos = None
        self.last_scene_pos = None
        
        # Remove any existing event filter (if needed)
        # PROBLEM LINE: if self.view.viewport().eventFilter(self):
        # This line is incorrect - you can't call eventFilter directly
        
        # First, remove any existing filter for safety
        try:
            self.view.viewport().removeEventFilter(self)
        except:
            pass  # Ignore if not already installed
        
        # Install event filter
        self.view.viewport().installEventFilter(self)
        
    def eventFilter(self, obj, event):
        """Filter events from the viewport."""
        try:
            if obj == self.view.viewport():
                from PyQt5.QtCore import QEvent, Qt
                
                if event.type() == QEvent.MouseButtonPress:
                    handled = self.handle_mouse_press(event)
                    return bool(handled)
                    
                elif event.type() == QEvent.MouseMove:
                    # Important: For boundary drawing, we need to handle all mouse moves
                    if hasattr(self.canvas, 'current_mode') and self.canvas.current_mode == "add_boundary":
                        handled = self.handle_mouse_move(event)
                        return True  # Always consume move events during boundary creation
                    else:
                        # For other modes, only track moves with button pressed
                        if event.buttons() & Qt.LeftButton:
                            handled = self.handle_mouse_move(event)
                            return bool(handled)
                    
                elif event.type() == QEvent.MouseButtonRelease:
                    handled = self.handle_mouse_release(event)
                    return bool(handled)
            
            # Let the event propagate to other handlers
            return super().eventFilter(obj, event) if hasattr(super(), 'eventFilter') else False
            
        except Exception as e:
            print(f"Error in MouseHandler.eventFilter: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def handle_mouse_press(self, event):
        """Handle mouse press events on the view."""
        try:
            # Convert to scene coordinates
            scene_pos = self.view.mapToScene(event.pos())
            
            # Get current mode from canvas controller
            current_mode = self.canvas.current_mode if hasattr(self.canvas, 'current_mode') else "selection"
            
            print(f"Mouse press in mode: {current_mode} at {scene_pos.x():.1f}, {scene_pos.y():.1f}")
            print(f"MouseHandler handling event in mode: {current_mode}")
            
            # Let canvas controller handle the event based on current mode
            if hasattr(self.canvas, 'handle_click'):
                result = self.canvas.handle_click(scene_pos)
                # Ensure we return a boolean
                return bool(result) if result is not None else False
            else:
                print("Warning: Canvas controller has no handle_click method")
                return False
        except Exception as e:
            print(f"Error in handle_mouse_press: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def handle_mouse_move(self, event):
        """Handle mouse move events."""
        try:
            # Get scene position
            scene_pos = self.view.mapToScene(event.pos())
            
            # Store last positions
            self.last_pos = event.pos()
            self.last_scene_pos = scene_pos
            
            # Always call canvas handler for boundary mode
            current_mode = self.canvas.current_mode if hasattr(self.canvas, 'current_mode') else "selection"
            
            if hasattr(self.canvas, 'handle_mouse_move'):
                result = self.canvas.handle_mouse_move(event, scene_pos)
                return bool(result) if result is not None else False
            
            return False
            
        except Exception as e:
            print(f"Error in handle_mouse_move: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def handle_mouse_release(self, event):
        """Handle mouse release events."""
        try:
            # Get scene position
            scene_pos = self.view.mapToScene(event.pos())
            
            print(f"Mouse released at scene position: ({scene_pos.x():.1f}, {scene_pos.y():.1f})")
            
            # Get current mode from canvas controller
            current_mode = self.canvas.current_mode if hasattr(self.canvas, 'current_mode') else "selection"
            print(f"Mouse released in mode: {current_mode}")
            print(f"Scene position: ({scene_pos.x():.1f}, {scene_pos.y():.1f})")
            
            # Let the canvas controller handle the release
            if hasattr(self.canvas, 'handle_mouse_release'):
                handled = self.canvas.handle_mouse_release(event, scene_pos)
                # Ensure we return a boolean value
                return bool(handled) if handled is not None else False
            else:
                print("Warning: Canvas controller has no handle_mouse_release method")
            
            return False  # Always return a boolean
            
        except Exception as e:
            print(f"Error in handle_mouse_release: {e}")
            import traceback
            traceback.print_exc()
            return False  # Return a boolean even on error
    
    def handle_wheel(self, event):
        """Handle mouse wheel events for zooming."""
        try:
            # Check if Ctrl key is pressed for zooming
            if event.modifiers() & Qt.ControlModifier:
                # Calculate zoom factor based on wheel delta
                zoom_factor = 1.2
                if event.angleDelta().y() < 0:
                    zoom_factor = 1.0 / zoom_factor
                
                # Set the anchor for zooming to the cursor position
                self.view.setTransformationAnchor(self.view.AnchorUnderMouse)
                
                # Apply zoom
                self.view.scale(zoom_factor, zoom_factor)
                
                # Prevent event from propagating
                return True
            
            # Let the default handler handle it (normal scrolling)
            return False
            
        except Exception as e:
            print(f"Error in handle_wheel: {e}")
            traceback.print_exc()
            return False
    
    def clear_temp_items(self):
        """Clear any temporary visual items."""
        for item in self.temp_items:
            if item.scene() == self.scene:
                self.scene.removeItem(item)
        self.temp_items = []