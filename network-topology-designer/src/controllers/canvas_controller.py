from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QApplication
from PyQt5.QtCore import Qt, QPointF, QObject, QTimer
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from controllers.device_manager import DeviceManager
from ui.device_dialog import DeviceSelectionDialog

class CanvasController(QObject):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.scene = view.scene()
        
        # Initialize managers
        self.device_manager = DeviceManager(self.scene)
        
        # Set the initial interaction mode
        self.current_mode = None
        
        # Set a fixed scale for the view - use 1.0 for 100% scale
        self.view.resetTransform()
        self.default_scale = 1.0
        
        # Connect the view's mouse press event
        self.view.mousePressEvent = self.mouse_press_event
        print("Connected mousePressEvent")
        
        # Add custom wheel event for controlled zooming
        self.original_wheel_event = self.view.wheelEvent
        self.view.wheelEvent = self.wheel_event
    
    def set_mode(self, mode):
        """Set the current interaction mode."""
        self.current_mode = mode
        print(f"Setting mode to: {mode}")
    
    def mouse_press_event(self, event):
        """Handle mouse press events on the canvas."""
        try:
            # Check if we're clicking on an item
            item = self.view.itemAt(event.pos())
            
            if item:
                # If we're clicking on a device, let it handle the event
                # without changing the scene mode
                print(f"Clicked on existing item: {type(item).__name__}")
                # Just pass the event to the default handler
                super(type(self.view), self.view).mousePressEvent(event)
                return
                
            # If we're not clicking on an item, convert the position and handle based on mode
            scene_pos = self.view.mapToScene(event.pos())
            print(f"Mouse pressed in mode: {self.current_mode}")
            print(f"Scene position: ({scene_pos.x()}, {scene_pos.y()})")
            
            # Handle based on current mode
            if self.current_mode:
                self.handle_click(scene_pos)
            
            # Call the parent class's mousePressEvent
            super(type(self.view), self.view).mousePressEvent(event)
        except Exception as e:
            print(f"Error in mouse_press_event: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_click(self, scene_pos):
        """Handle mouse clicks on the canvas based on the current mode."""
        try:
            print(f"Canvas handling click in mode: {self.current_mode}")
            
            if self.current_mode == "add_device":
                self.show_device_dialog(scene_pos)
            elif self.current_mode == "add_boundary":
                pass  # Not implemented yet
            elif self.current_mode == "add_connection":
                pass  # Not implemented yet
            elif self.current_mode == "delete":
                pass  # Not implemented yet
        except Exception as e:
            print(f"Error handling mouse click: {e}")
            import traceback
            traceback.print_exc()
    
    def show_device_dialog(self, position):
        """Show device selection dialog and add the selected device."""
        try:
            print(f"Showing device dialog at position: ({position.x()}, {position.y()})")
            
            # The parent should be the main window
            parent = self.view.window()
            
            # Show the dialog
            device_info = DeviceSelectionDialog.get_device(parent)
            
            if device_info:
                # Create the device with the selected type
                device = self.device_manager.create_device(device_info["type"], position)
                
                # Update device properties if it was created successfully
                if device:
                    device.update_property("name", device_info["name"])
                    device.update_property("ip_address", device_info["ip"])
                    device.update_property("description", device_info["description"])
                    
                    # No need to update label position manually since it's part of the group
                    print(f"Created device: {device_info['name']} of type {device_info['type']}")
                
        except Exception as e:
            print(f"Error in show_device_dialog: {e}")
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