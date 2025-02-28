from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsRectItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor
from controllers.device_manager import DeviceManager
from ui.device_dialog import DeviceSelectionDialog

class CanvasController:
    def __init__(self, scene, view):
        """Initialize the canvas controller with a QGraphicsScene and QGraphicsView."""
        self.scene = scene
        self.view = view
        self.current_mode = "select"
        self.current_item_type = None
        
        # Create specialized managers
        self.device_manager = DeviceManager(scene)
        
        # Style settings
        self.default_pen = QPen(Qt.black, 2)
        self.default_brush = QBrush(QColor(200, 200, 255))
        
    def set_mode(self, mode):
        """Set the current interaction mode."""
        self.current_mode = mode
        # Change cursor based on mode
        if mode == "select":
            self.view.setCursor(Qt.ArrowCursor)
        elif mode in ["add_device", "add_textbox", "add_connection", "add_boundary"]:
            self.view.setCursor(Qt.CrossCursor)
        elif mode == "delete":
            self.view.setCursor(Qt.ForbiddenCursor)
        
    def set_item_type(self, item_type):
        """Set the type of item to add (e.g., router, switch, server)."""
        self.current_item_type = item_type
        
    def handle_click(self, scene_pos):
        """Handle mouse clicks on the canvas based on the current mode."""
        try:
            print(f"Canvas handling click in mode: {self.current_mode}")
            
            if self.current_mode == "add_device":
                # Temporary direct device creation for testing
                print("Creating test device...")
                self.device_manager.create_device("router", scene_pos)
                # Later you can uncomment this and use the dialog
                # self.show_device_dialog(scene_pos)
            elif self.current_mode == "add_boundary":
                self.add_boundary(scene_pos)
            elif self.current_mode == "add_connection":
                self.add_connection(scene_pos)
            elif self.current_mode == "delete":
                self.delete_at_position(scene_pos)
        except Exception as e:
            print(f"Error handling mouse click: {e}")
            import traceback
            traceback.print_exc()
    
    def show_device_dialog(self, position):
        """Show device selection dialog and add the selected device."""
        print(f"Showing device dialog at position: ({position.x()}, {position.y()})")
        
        try:
            # The parent should be the main window
            parent = self.view.window()
            
            # Show the dialog
            device_info = DeviceSelectionDialog.get_device(parent)
            print(f"Dialog result: {device_info}")
            
            if device_info:
                # Create the device with the selected type
                device = self.device_manager.create_device(device_info["type"], position)
                print(f"Device created: {device}")
                
                # Update device properties if it was created successfully
                if device:
                    device.update_property("name", device_info["name"])
                    device.update_property("ip_address", device_info["ip"])
                    device.update_property("description", device_info["description"])
                    print("Device properties updated")
        except Exception as e:
            print(f"Error in show_device_dialog: {e}")
            import traceback
            traceback.print_exc()
    
    def add_boundary(self, position):
        """Add a boundary box to the scene."""
        try:
            # For now, use a different colored rectangle for boundaries
            size = 100
            boundary = QGraphicsRectItem(
                position.x() - size/2, 
                position.y() - size/2, 
                size, size
            )
            boundary.setPen(QPen(Qt.darkGreen, 2, Qt.DashLine))
            boundary.setBrush(QBrush(QColor(200, 255, 200, 100)))
            boundary.setFlag(QGraphicsItem.ItemIsMovable)
            boundary.setFlag(QGraphicsItem.ItemIsSelectable)
            boundary.setData(0, "boundary")
            
            self.scene.addItem(boundary)
            return boundary
        except Exception as e:
            print(f"Error adding boundary: {e}")
    
    def add_connection(self, position):
        """Add a connection point or line."""
        # This will need to be expanded to handle two-point connections
        try:
            point = self.scene.addEllipse(
                position.x() - 5, 
                position.y() - 5, 
                10, 10, 
                QPen(Qt.red, 2),
                QBrush(Qt.red)
            )
            point.setData(0, "connection_point")
            return point
        except Exception as e:
            print(f"Error adding connection point: {e}")
            
    def delete_at_position(self, position):
        """Delete items at the given position."""
        try:
            # First try to delete devices using the device manager
            devices = self.device_manager.get_devices_at_position(position)
            if devices:
                for device in devices:
                    self.device_manager.remove_device(device)
                return
                
            # If no devices found, try to delete other items
            items = self.scene.items(position)
            for item in items:
                if item not in self.device_manager.devices:  # Don't delete devices twice
                    self.scene.removeItem(item)
        except Exception as e:
            print(f"Error deleting item: {e}")
            
    def clear(self):
        """Clear all items from the scene."""
        try:
            self.scene.clear()
            self.device_manager.devices = []  # Reset the device list
        except Exception as e:
            print(f"Error clearing scene: {e}")
        
    def zoom_in(self):
        """Zoom in on the view."""
        try:
            self.view.scale(1.2, 1.2)
        except Exception as e:
            print(f"Error zooming in: {e}")
        
    def zoom_out(self):
        """Zoom out on the view."""
        try:
            self.view.scale(0.8, 0.8)
        except Exception as e:
            print(f"Error zooming out: {e}")