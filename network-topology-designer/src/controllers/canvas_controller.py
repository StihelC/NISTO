from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QApplication
from PyQt5.QtCore import Qt, QPointF, QObject, QTimer
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from controllers.device_manager import DeviceManager
from ui.device_dialog import DeviceSelectionDialog
from controllers.connection_manager import ConnectionManager
from models.device import NetworkDevice

class CanvasController(QObject):
    """Controller for the canvas area."""
    
    def __init__(self, view, scene, connection_manager, device_manager=None):
        super().__init__()
        self.view = view
        self.scene = scene
        self.connection_manager = connection_manager
        self.device_manager = device_manager  # Store reference to device manager
        self.current_mode = "selection"  # Default mode
        self.temp_line = None  # Temporary line for drawing connections
        
        # IMPORTANT: Store a reference to the viewport but make it weak
        import weakref
        self._viewport_ref = weakref.ref(view.viewport())
        
        # Install event filters for mouse events
        self.view.viewport().installEventFilter(self)
        
    def __del__(self):
        """Clean up when the controller is destroyed."""
        try:
            # Remove the event filter if view still exists
            if hasattr(self, 'view') and self.view and hasattr(self.view, 'viewport'):
                viewport = self.view.viewport()
                if viewport:
                    viewport.removeEventFilter(self)
                    
            # Clear references to prevent circular references
            self.view = None
            self.scene = None
            self.connection_manager = None
            self.device_manager = None
            self.temp_line = None
        except:
            # Ignore errors during cleanup
            pass
        
    def set_mode(self, mode):
        """Set the current interaction mode."""
        self.current_mode = mode
        print(f"Mode set to: {mode}")
        
        # Reset any ongoing operations when mode changes
        if self.temp_line and self.temp_line.scene():
            self.scene.removeItem(self.temp_line)
            self.temp_line = None

    def set_quick_add_mode(self, device_type):
        """Set the mode to quickly add a device of the specified type."""
        self.current_mode = "quick_add"
        self.quick_add_type = device_type
        
    def handle_click(self, scene_pos):
        """Handle a click on the canvas based on current mode."""
        try:
            if self.current_mode == "add_device":
                # Open device selection dialog before adding a device
                self.show_device_dialog(scene_pos)
            elif self.current_mode == "quick_add" and hasattr(self, 'quick_add_type'):
                # Quick add a device of the specified type
                self.quick_add_device(scene_pos, self.quick_add_type)
        except Exception as e:
            print(f"Error in handle_click: {e}")
            import traceback
            traceback.print_exc()
    
    def show_device_dialog(self, scene_pos):
        """Show the device selection dialog and add a device if confirmed."""
        try:
            print("Opening device dialog...")
            
            # Get parent window for the dialog
            parent = None
            if hasattr(self.view, 'window'):
                parent = self.view.window()
                
            # Create the dialog
            from ui.device_dialog import DeviceSelectionDialog
            dialog = DeviceSelectionDialog(parent=parent)
            
            # Show the dialog (modal)
            if dialog.exec_():
                print("Dialog accepted")
                
                # Get the selected properties
                device_type = dialog.get_device_type().lower()  # Ensure lowercase
                device_name = dialog.get_device_name()
                properties = dialog.get_device_properties()
                
                print(f"Adding {device_type} named '{device_name}' with properties: {properties}")
                
                # Create the device using device manager
                if hasattr(self, 'device_manager') and self.device_manager:
                    device = self.device_manager.create_device(
                        device_type, 
                        scene_pos.x(), 
                        scene_pos.y(),
                        properties=properties
                    )
                    return device
                else:
                    print("Warning: No device manager available")
                    # Fallback to direct creation
                    from models.device import NetworkDevice
                    device = NetworkDevice(device_type, scene_pos.x(), scene_pos.y())
                    self.scene.addItem(device)
                    
                    # Update properties
                    for key, value in properties.items():
                        if hasattr(device, 'update_property'):
                            device.update_property(key, value)
                    
                    return device
            else:
                print("Dialog canceled")
                
        except Exception as e:
            print(f"Error showing device dialog: {e}")
            import traceback
            traceback.print_exc()
        
        return None

    def quick_add_device(self, scene_pos, device_type):
        """Quickly add a device of the specified type without a dialog."""
        try:
            print(f"Quick adding {device_type} at {scene_pos.x()}, {scene_pos.y()}")
            
            # Auto-generate a name
            import time
            device_name = f"{device_type.capitalize()}-{int(time.time()) % 1000}"
            
            # Create properties
            properties = {
                "name": device_name,
                "description": f"Auto-created {device_type}"
            }
            
            # Create the device
            if hasattr(self, 'device_manager') and self.device_manager:
                device = self.device_manager.create_device(
                    device_type, scene_pos.x(), scene_pos.y(),
                    properties=properties
                )
                
                # Reset mode to selection after adding
                self.current_mode = "selection"
                
                return device
            else:
                print("Warning: No device manager available for quick add")
                return None
        except Exception as e:
            print(f"Error in quick_add_device: {e}")
            import traceback
            traceback.print_exc()
            return None

    def add_device_at(self, scene_pos, device_type="router"):
        """Add a device at the specified position."""
        # Use device_manager if available, otherwise fall back to direct creation
        if self.device_manager:
            device = self.device_manager.create_device(device_type, scene_pos.x(), scene_pos.y())
        else:
            # Import here to avoid circular imports
            from models.device import NetworkDevice
            device = NetworkDevice(device_type, scene_pos.x(), scene_pos.y())
            self.scene.addItem(device)
            
        print(f"Added {device_type} at ({scene_pos.x()}, {scene_pos.y()})")
        return device
    
    def eventFilter(self, obj, event):
        """Handle events from the viewport."""
        try:
            # Get the current viewport safely
            viewport = self._viewport_ref()
            
            # Check if viewport still exists and matches our object
            if viewport is None or obj != viewport:
                return False
                
            # Now handle events safely
            if event.type() == event.MouseButtonPress:
                self.mouse_press_event(event)
            elif event.type() == event.MouseMove:
                self.mouse_move_event(event)
                
            return super().eventFilter(obj, event)
        except Exception as e:
            print(f"Error in eventFilter: {e}")
            return False
    
    def mouse_press_event(self, event):
        """Handle mouse press events on the canvas."""
        try:
            # Convert mouse position to scene coordinates
            scene_pos = self.view.mapToScene(event.pos())
            print(f"Mouse pressed in mode: {self.current_mode}")
            print(f"Scene position: ({scene_pos.x()}, {scene_pos.y()})")
            
            # Check if we're clicking on an item
            item = self.view.itemAt(event.pos())
            
            if self.current_mode == "add_connection":
                # Handle connection creation
                if isinstance(item, NetworkDevice):
                    # Your existing connection code...
                    pass
                else:
                    # Cancel if clicking elsewhere
                    if hasattr(self.connection_manager, 'cancel_connection'):
                        self.connection_manager.cancel_connection()
                    # Remove temporary line
                    if hasattr(self, 'temp_line') and self.temp_line and hasattr(self.temp_line, 'scene'):
                        if self.temp_line.scene():
                            self.scene.removeItem(self.temp_line)
                        self.temp_line = None
            elif self.current_mode == "add_device" and not item:
                # Only add device if clicking on empty space
                print("Calling handle_click for device creation")
                self.handle_click(scene_pos)
            
            # Call the parent class's mousePressEvent to maintain default behavior
            if hasattr(self.view.__class__, 'mousePressEvent'):
                super(self.view.__class__, self.view).mousePressEvent(event)
        except Exception as e:
            print(f"Error in mouse_press_event: {e}")
            import traceback
            traceback.print_exc()

    def mouse_move_event(self, event):
        """Handle mouse move events on the canvas."""
        try:
            # Get scene position
            scene_pos = self.view.mapToScene(event.pos())
            
            # Show temporary connection line when creating connections
            if self.current_mode == "add_connection" and self.connection_manager.source_device:
                # Get source port position
                source_device = self.connection_manager.source_device
                source_port = self.connection_manager.source_port
                
                if source_port and source_port in source_device.ports:
                    source_point = source_device.get_port_position(source_port)
                else:
                    source_point = source_device.sceneBoundingRect().center()
                
                # Remove previous temporary line if it exists
                if self.temp_line and self.temp_line.scene():
                    self.scene.removeItem(self.temp_line)
                
                # Create a new temporary line
                self.temp_line = self.scene.addLine(
                    source_point.x(), source_point.y(),
                    scene_pos.x(), scene_pos.y(),
                    QPen(QColor(100, 100, 255, 150), 2, Qt.DashLine)
                )
                # Store the end point for port selection
                self.temp_line.temp_line_end = scene_pos
                
                # Check if hovering over another device to highlight its ports
                item_at_cursor = self.view.itemAt(event.pos())
                if isinstance(item_at_cursor, NetworkDevice) and item_at_cursor != source_device:
                    # Highlight the closest port
                    item_at_cursor.highlight_closest_port(scene_pos, True)
                else:
                    # Reset highlights on all devices except source
                    for item in self.scene.items():
                        if isinstance(item, NetworkDevice) and item != source_device:
                            item.reset_port_highlights()
                        
            elif self.current_mode == "selection":
                # In selection mode, highlight ports when hovering over devices
                item_at_cursor = self.view.itemAt(event.pos())
                if isinstance(item_at_cursor, NetworkDevice):
                    item_at_cursor.highlight_closest_port(scene_pos, True)
                
            # Call the parent class's mouseMoveEvent for default behavior
            super(self.view.__class__, self.view).mouseMoveEvent(event)
        except RuntimeError as e:
            if "has been deleted" in str(e):
                print("Warning: Attempted to access deleted object")
            else:
                print(f"RuntimeError in mouse_move_event: {e}")
        except Exception as e:
            print(f"Error in mouse_move_event: {e}")
            import traceback
            traceback.print_exc()
    
    def wheel_event(self, event):
        """Handle mouse wheel events for controlled zooming."""
        # Get the current scale factor
        current_scale = self.view.transform().m11()
        
        # Define zoom factor
        zoom_factor = 1.15
        
        # Calculate new scale
        if event.angleDelta().y() > 0:
            # Zoom in
            new_scale = current_scale * zoom_factor
        else:
            # Zoom out
            new_scale = current_scale / zoom_factor
            
        # Limit the min/max zoom levels
        if 0.2 <= new_scale <= 5.0:
            # Calculate scale change
            factor = new_scale / current_scale
            
            # Apply zoom
            self.view.scale(factor, factor)
        
        # Don't pass the event to the parent class
        # Otherwise we'll get double zooming
        event.accept()
    
    def reset_view(self):
        """Reset the view to the default scale."""
        self.view.resetTransform()
        self.view.scale(self.default_scale, self.default_scale)