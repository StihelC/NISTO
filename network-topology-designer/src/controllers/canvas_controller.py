from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem
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
        
        # Connect the view's mouse press event
        self.view.mousePressEvent = self.mouse_press_event
        print("Connected mousePressEvent")
    
    def set_mode(self, mode):
        """Set the current interaction mode."""
        self.current_mode = mode
        print(f"Setting mode to: {mode}")
    
    def mouse_press_event(self, event):
        """Handle mouse press events on the canvas."""
        try:
            # Convert mouse position to scene coordinates
            scene_pos = self.view.mapToScene(event.pos())
            print(f"Mouse pressed in mode: {self.current_mode}")
            print(f"Scene position: ({scene_pos.x()}, {scene_pos.y()})")
            
            # Handle based on current mode
            if self.current_mode:
                self.handle_click(scene_pos)
            
            # Call the parent class's mousePressEvent to maintain default behavior
            super(self.view.__class__, self.view).mousePressEvent(event)
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
        except Exception as e:
            print(f"Error in show_device_dialog: {e}")
            import traceback
            traceback.print_exc()