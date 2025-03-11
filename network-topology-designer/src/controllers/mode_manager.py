from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem
from PyQt5.QtCore import Qt, QEvent, QPointF, QObject
from PyQt5.QtWidgets import QApplication
import weakref
import traceback

class ModeManager(QObject):
    """Manager for handling different interaction modes in the canvas."""
    
    # Mode constants
    MODE_SELECT = "select"
    MODE_ADD_DEVICE = "add_device"
    MODE_ADD_CONNECTION = "add_connection"
    MODE_DELETE = "delete"
    MODE_ADD_TEXT = "add_text"
    MODE_ADD_BOUNDARY = "add_boundary"
    
    def __init__(self, canvas_controller, view, device_manager, connection_manager):
        """Initialize the mode manager."""
        # Set parent to canvas_controller for proper lifecycle management
        super().__init__(canvas_controller)
        
        self.canvas_controller = canvas_controller
        self._view_ref = weakref.ref(view) if view else None
        self._viewport_ref = weakref.ref(view.viewport()) if view and hasattr(view, 'viewport') else None
        
        self.device_manager = device_manager
        self.connection_manager = connection_manager
        
        # Current mode
        self.current_mode = self.MODE_SELECT
        
        # Current device type (for add device mode)
        self.current_device_type = "router"
        
        # Mouse state tracking
        self.left_button_pressed = False
        self.right_button_pressed = False
        self.middle_button_pressed = False
        self.last_mouse_pos = None
        self.drag_start_pos = None
        
        self.source_device = None
        self.source_port = None  
        self.is_dragging = False
        
        # Install event filter on the view's viewport if available
        self._install_event_filter()
        
        print("ModeManager initialized successfully")
    
    def _install_event_filter(self):
        """Safely install the event filter."""
        viewport = self.get_viewport()
        if viewport:
            try:
                viewport.installEventFilter(self)
                print("Event filter installed successfully")
            except Exception as e:
                print(f"Failed to install event filter: {e}")
                traceback.print_exc()
    
    def get_view(self):
        """Get the view safely."""
        try:
            return self._view_ref() if self._view_ref else None
        except Exception:
            self._view_ref = None
            return None
    
    def get_viewport(self):
        """Get the viewport safely."""
        try:
            return self._viewport_ref() if self._viewport_ref else None
        except Exception:
            self._viewport_ref = None
            return None
    
    def set_mode(self, mode):
        """Set the current interaction mode."""
        try:
            # Exit current mode first
            self._exit_current_mode()
            
            # Set the new mode if valid
            if mode in [self.MODE_SELECT, self.MODE_ADD_DEVICE, self.MODE_ADD_CONNECTION, 
                       self.MODE_DELETE, self.MODE_ADD_TEXT, self.MODE_ADD_BOUNDARY]:
                self.current_mode = mode
                print(f"Mode set to: {mode}")
                
                # Enter the new mode
                self._enter_current_mode()
                
                return True
            else:
                print(f"Invalid mode: {mode}")
                return False
        except Exception as e:
            print(f"Error setting mode: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def set_device_type(self, device_type):
        """Set the current device type for add_device mode."""
        self.current_device_type = device_type
    
    def _exit_current_mode(self):
        """Clean up resources when exiting the current mode."""
        try:
            # If in connection mode, cancel any temp connection
            if self.current_mode == self.MODE_ADD_CONNECTION:
                if hasattr(self, 'canvas_controller') and self.canvas_controller:
                    # Call the method only if it exists
                    if hasattr(self.canvas_controller, 'cancel_temp_connection'):
                        self.canvas_controller.cancel_temp_connection()
                    # Alternative if the method doesn't exist but there's a connection_tool
                    elif hasattr(self.canvas_controller, 'connection_tool') and \
                         self.canvas_controller.connection_tool and \
                         hasattr(self.canvas_controller.connection_tool, 'cancel_connection'):
                        self.canvas_controller.connection_tool.cancel_connection()
            
            # Clean up other mode-specific resources
            # ...
        except Exception as e:
            print(f"Error in _exit_current_mode: {e}")
            import traceback
            traceback.print_exc()
    
    def _enter_current_mode(self):
        """Set up resources for the new mode."""
        try:
            # Mode-specific setup
            if self.current_mode == self.MODE_ADD_CONNECTION:
                # Initialize connection tool if needed
                pass
            elif self.current_mode == self.MODE_ADD_DEVICE:
                # Set cursor or other visual indicators
                pass
            # Other modes...
        except Exception as e:
            print(f"Error in _enter_current_mode: {e}")
            import traceback
            traceback.print_exc()
    
    def eventFilter(self, obj, event):
        """Filter events from the view."""
        try:
            # Get viewport safely
            viewport = self.get_viewport()
            
            # Safety check - if viewport is None or doesn't match obj, don't process
            if not viewport or obj is not viewport:
                return False
            
            if event.type() == QEvent.MouseButtonPress:
                return self._handle_mouse_press(event)
                
            elif event.type() == QEvent.MouseButtonRelease:
                return self._handle_mouse_release(event)
                
            elif event.type() == QEvent.MouseMove:
                return self._handle_mouse_move(event)
                    
            elif event.type() == QEvent.KeyPress:
                return self._handle_key_press(event)
        except AttributeError as e:
            print(f"AttributeError in event filter: {e}")
            traceback.print_exc()
            return False
        except RuntimeError as e:
            print(f"RuntimeError in event filter: {e}")
            self.cleanup()
            return False
        except Exception as e:
            print(f"Exception in event filter: {e}")
            traceback.print_exc()
            return False
                
        # Pass through all unhandled events
        return False
    
    # Implement safe cleanup if needed
    def cleanup(self):
        """Remove event filters and clean up resources."""
        print("Cleaning up ModeManager...")
        try:
            viewport = self.get_viewport()
            if viewport:
                try:
                    viewport.removeEventFilter(self)
                    print("Event filter removed successfully")
                except Exception as e:
                    print(f"Error removing event filter: {e}")
            
            # Clear references
            self._view_ref = None
            self._viewport_ref = None
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def _handle_mouse_press(self, event):
        """Handle mouse press events."""
        if not event:
            return False
            
        try:
            if event.button() == Qt.LeftButton:
                self.left_button_pressed = True
                
                # Get scene position and call handler
                view = self.get_view()
                if view:
                    scene_pos = view.mapToScene(event.pos())
                    return self.handle_mouse_press(event, scene_pos)
                
            # Rest of the method...
        except Exception as e:
            print(f"Error in _handle_mouse_press: {e}")
            traceback.print_exc()
            
        return False
    
    def _handle_mouse_release(self, event):
        """Handle mouse release events."""
        if not event:
            return False
            
        try:
            if event.button() == Qt.LeftButton:
                self.left_button_pressed = False
            elif event.button() == Qt.RightButton:
                self.right_button_pressed = False
            elif event.button() == Qt.MiddleButton:
                self.middle_button_pressed = False
        except Exception as e:
            print(f"Error in _handle_mouse_release: {e}")
            
        return False
    
    def _handle_mouse_move(self, event):
        """Handle mouse move events."""
        if not event:
            return False
            
        try:
            # Update last mouse position
            self.last_mouse_pos = event.pos()
            
            # Pan the view with middle button or left+right buttons
            if self.middle_button_pressed or (self.left_button_pressed and self.right_button_pressed):
                self._pan_view(event)
                return True
        except Exception as e:
            print(f"Error in _handle_mouse_move: {e}")
            traceback.print_exc()
            
        # Always let the event propagate
        return False
    
    def _handle_key_press(self, event):
        """Handle key press events."""
        return self.handle_key_press(event)
    
    def handle_mouse_press(self, event, scene_pos):
        """Handle mouse press event based on current mode."""
        if self.current_mode == self.MODE_SELECT:
            # Default selection behavior
            self.drag_start_pos = scene_pos
            return False  # Let the view handle selection
        
        elif self.current_mode == self.MODE_ADD_DEVICE:
            # Add new device at click position
            self.canvas_controller.add_device(self.current_device_type, scene_pos)
            return True
        
        elif self.current_mode == self.MODE_ADD_CONNECTION:
            # Start connection if clicked on a device
            if self.device_manager: 
                device, port = self.device_manager.get_port_at_pos(scene_pos)
                if device:
                    self.source_device = device
                    self.source_port = port
                    self.canvas_controller.start_temp_connection(device, port)
                    return True
        
        elif self.current_mode == self.MODE_ADD_TEXT:
            # Start drawing boundary rectangle
            self.drag_start_pos = scene_pos
            self.canvas_controller.start_temp_rectangle(scene_pos)
            self.is_dragging = True
            return True
        
        elif self.current_mode == self.MODE_DELETE:
            # Delete item at click position
            item = self.canvas_controller.get_item_at(scene_pos)
            if item:
                if hasattr(item, 'device_type') and self.device_manager:
                    self.device_manager.remove_device(item)
                elif hasattr(item, 'source_device') and self.connection_manager:
                    self.connection_manager.remove_connection(item)
                else:
                    self.scene.removeItem(item)
            return True
        
        elif self.current_mode == self.MODE_ADD_BOUNDARY:
            # Start drawing boundary rectangle
            self.drag_start_pos = scene_pos
            self.canvas_controller.start_temp_rectangle(scene_pos)
            self.is_dragging = True
            return True
        
        return False
    
    def handle_mouse_move(self, event, scene_pos):
        """Handle mouse move event based on current mode."""
        if self.current_mode == self.MODE_SELECT:
            # Default selection behavior
            return False
        
        elif self.current_mode == self.MODE_ADD_CONNECTION and self.source_device:
            # Update temporary connection
            self.canvas_controller.update_temp_connection(scene_pos)
            return True
        
        elif self.current_mode == self.MODE_ADD_BOUNDARY and self.is_dragging:
            # Update temporary rectangle
            self.canvas_controller.update_temp_rectangle(scene_pos)
            return True
        
        return False
    
    def handle_mouse_release(self, event, scene_pos):
        """Handle mouse release event based on current mode."""
        if self.current_mode == self.MODE_SELECT:
            # Default selection behavior
            self.drag_start_pos = None
            return False
        
        elif self.current_mode == self.MODE_ADD_CONNECTION and self.source_device:
            # Finish creating connection
            if self.device_manager:
                target_device, target_port = self.device_manager.get_port_at_pos(scene_pos)
                if target_device and target_device != self.source_device:
                    self.canvas_controller.finish_temp_connection(target_device, target_port)
                else:
                    self.canvas_controller.cancel_temp_connection()
            else:
                self.canvas_controller.cancel_temp_connection()
            self.source_device = None
            self.source_port = None
            return True
        
        elif self.current_mode == self.MODE_ADD_BOUNDARY and self.is_dragging:
            # Finish creating boundary
            self.canvas_controller.finish_temp_rectangle()
            self.is_dragging = False
            self.drag_start_pos = None
            return True
        
        return False
    
    def handle_key_press(self, event):
        """Handle key press event based on current mode."""
        if event.key() == Qt.Key_Escape:
            if self.current_mode == self.MODE_ADD_CONNECTION and self.source_device:
                self.canvas_controller.cancel_temp_connection()
                self.source_device = None
                self.source_port = None
                return True
            elif self.current_mode == self.MODE_ADD_BOUNDARY and self.is_dragging:
                self.canvas_controller.cancel_temp_rectangle()
                self.is_dragging = False
                self.drag_start_pos = None
                return True
        
        elif event.key() == Qt.Key_Delete:
            # Delete selected items in any mode
            self.canvas_controller.delete_selected_items()
            return True
        
        return False
    
    def _pan_view(self, event):
        """Pan the view based on mouse movement."""
        try:
            view = self.get_view()
            if not view or not hasattr(view, 'horizontalScrollBar') or not self.last_mouse_pos:
                return
                
            # Calculate delta
            delta = event.pos() - self.last_mouse_pos
            
            # Apply translation
            h_scrollbar = view.horizontalScrollBar()
            v_scrollbar = view.verticalScrollBar()
            
            if h_scrollbar and v_scrollbar:
                h_scrollbar.setValue(h_scrollbar.value() - delta.x())
                v_scrollbar.setValue(v_scrollbar.value() - delta.y())
                
            # Update position
            self.last_mouse_pos = event.pos()
        except Exception as e:
            print(f"Error in _pan_view: {e}")
            traceback.print_exc()