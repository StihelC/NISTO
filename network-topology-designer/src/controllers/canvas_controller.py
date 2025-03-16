from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QApplication, QGraphicsTextItem, QMessageBox, QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF, QObject, QTimer, QRectF, QSizeF, pyqtSignal
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QFont
from controllers.device_manager import DeviceManager
from models.device import Device
from src.models.connection import Connection
from ui.device_dialog import DeviceSelectionDialog
from controllers.connection_manager import ConnectionManager
from src.controllers.connection_tool import ConnectionCreationTool
from src.views.topology_scene import TopologyScene

class CanvasController(QObject):
    """Controls the canvas and handles drawing operations."""
    
    mode_changed = pyqtSignal(str)
    
    # Mode constants
    SELECT_MODE = "select_mode"
    DEVICE_MODE = "device_mode"
    CONNECTION_MODE = "connection_mode"
    BOUNDARY_MODE = "boundary_mode"
    
    def __init__(self, device_manager):
        super().__init__()
        self.device_manager = device_manager
        self.mode = self.SELECT_MODE
        self.selected_device_type = Device.ROUTER  # Default device type
    
    def set_mode(self, mode):
        """Set the canvas interaction mode."""
        self.mode = mode
        
        # Update cursor based on mode
        if mode == self.MODE_SELECT:
            self.view.setCursor(Qt.ArrowCursor)
            self._enable_device_dragging(True)
        elif mode == self.MODE_DEVICE:
            self.view.setCursor(Qt.CrossCursor)
            self._enable_device_dragging(True)
        elif mode == self.MODE_CONNECT:
            self.view.setCursor(Qt.PointingHandCursor)
            self._enable_device_dragging(False)  # Disable dragging in connect mode
        elif mode == self.MODE_DELETE:
            self.view.setCursor(Qt.ForbiddenCursor)
            self._enable_device_dragging(True)
        
        # Emit mode changed signal if you have one
        if hasattr(self, 'mode_changed'):
            self.mode_changed.emit(mode)

    def _enable_device_dragging(self, enable):
        """Enable or disable dragging for all devices in the scene."""
        from PyQt5.QtWidgets import QGraphicsItem
        from src.models.device import Device
        
        # Iterate through all items in the scene
        for item in self.scene.items():
            # Check if it's a Device instance
            if isinstance(item, Device):
                item.setFlag(QGraphicsItem.ItemIsMovable, enable)
    
    def set_device_type(self, device_type):
        """Set the device type for device creation."""
        if device_type in Device.get_available_types():
            self.selected_device_type = device_type
            self.device_manager.set_selected_device_type(device_type)
            print(f"Selected device type: {device_type}")
            return True
        
        print(f"Unknown device type: {device_type}")
        return False
    
    def handle_mouse_press(self, event):
        """Handle mouse press events on the canvas."""
        scene_pos = self.view.mapToScene(event.pos())
        
        if self.mode == self.MODE_CONNECT:
            # Handle connection mode
            item = self.scene.itemAt(scene_pos, self.view.transform())
            if item and isinstance(item, Device):
                # Start connection from this device
                self.connection_manager.start_connection(item)
        # ... rest of the method
    
    def handle_mouse_release(self, event):
        """Handle mouse release events on the canvas."""
        scene_pos = self.view.mapToScene(event.pos())
        
        if self.mode == self.MODE_CONNECT:
            # Complete connection
            item = self.scene.itemAt(scene_pos, self.view.transform())
            if item and hasattr(item, 'name'):  # Simple check if it's a device
                # Complete connection to this device
                connection = self.connection_manager.complete_connection(item)
                if connection:
                    print(f"Created connection from {connection.source_device.name} to {connection.target_device.name}")
                
                # Optional: Reset to select mode after creating a connection
                # self.set_mode(self.MODE_SELECT)
        # ... rest of the method
    
    def __init__(self, main_window=None, view=None):
        """Initialize canvas controller.
        
        Args:
            main_window: The main window instance
            view: QGraphicsView to control
        """
        super().__init__(main_window)  # Set parent for memory management
        
        self.main_window = main_window
        self.view = view
        
        # Create scene
        self.scene = TopologyScene()
        if view:
            view.setScene(self.scene)
        
        # References to other controllers/managers
        self.device_manager = None
        self.connection_manager = None
        self.mode_manager = None
        
        # Temporary items for interaction
        self.temp_connection = None
        self.temp_rectangle = None
        self.selected_items = []
        
        print("CanvasController initialized successfully")
        
        # Configure view
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Setup scene
        self._setup_scene()
        
        # Initialize with empty references
        self.mode_manager = None
        self.connection_tool = None
        
        # Initialize connection tracking attributes
        self.temp_connection = None  # Add this missing attribute
        
        # Grid tracking
        self.grid_visible = False
        self.grid_items = []
        
    def _setup_scene(self):
        """Configure the scene."""
        if not self.scene:
            return
            
        # Set scene size
        self.scene.setSceneRect(-2000, -2000, 4000, 4000)
        
        # Use a plain white background
        self.scene.setBackgroundBrush(QColor(255, 255, 255))
        
        # IMPORTANT: If you have grid drawing code here, remove it
        # Look for any code that creates lines or dots and comment it out
        
        # Example grid code that might be present and should be removed:
        # for x in range(-2000, 2000, 50):
        #     self.scene.addLine(x, -2000, x, 2000, QPen(Qt.gray, 0.5))
        # for y in range(-2000, 2000, 50):
        #     self.scene.addLine(-2000, y, 2000, y, QPen(Qt.gray, 0.5))
    
    # --- Override to fix the issue ---
    def mouse_move_event(self, event):
        """Handle mouse move events."""
        # Get scene position
        scene_pos = self.view.mapToScene(event.pos())
        
        # Define a simple function to prevent accessing non-existent attributes
        def has_attr(obj, attr_name):
            return hasattr(obj, attr_name) and getattr(obj, attr_name) is not None
        
        # Safe access to connection_tool and mode_manager
        try:
            # Check connection tool with safer method
            if has_attr(self, 'connection_tool'):
                if has_attr(self, 'mode_manager'):
                    if self.mode_manager.current_mode == "add_connection":  # Use string directly
                        if has_attr(self.connection_tool, 'mouse_move_event'):
                            self.connection_tool.mouse_move_event(scene_pos, event)
            
            # Forward to mode manager if available
            if has_attr(self, 'mode_manager'):
                if has_attr(self.mode_manager, 'handle_mouse_move'):
                    self.mode_manager.handle_mouse_move(scene_pos, event)
        except Exception as e:
            # Log error but don't crash
            print(f"Error in mouse_move_event: {e}")
        
        # Return False to allow event propagation
        return False
    
    def setup_managers(self):
        """Set up device and connection managers."""
        # Create managers
        from controllers.device_manager import DeviceManager
        from controllers.connection_manager import ConnectionManager
        
        self.device_manager = DeviceManager(self.scene)
        self.connection_manager = ConnectionManager(self.scene)
        
        # Track connection state
        self.dragging_connection = False
        self.drag_source_device = None
        self.drag_source_port = None
        self.temp_line = None
        
        print("Managers initialized")
        
        # Create the connection tool
        self.connection_tool = ConnectionCreationTool(self)  # Remove the extra parameter
        
        # If ConnectionCreationTool needs access to connection_manager, set it separately
        if hasattr(self.connection_tool, 'connection_manager'):
            self.connection_tool.connection_manager = self.connection_manager
        
        # Set the initial interaction mode
        self.current_mode = None
        self.temp_line = None  # For showing connection in progress
        
        # Set a fixed scale for the view - use 1.0 for 100% scale
        self.view.resetTransform()
        self.default_scale = 1.0
        
        # Connect the view's mouse press event
        self.view.mousePressEvent = self.mouse_press_event
        self.view.mouseMoveEvent = self.mouse_move_event
        self.view.mouseReleaseEvent = self.mouse_release_event
        print("Connected mouse events")
        
        # Add custom wheel event for controlled zooming
        self.original_wheel_event = self.view.wheelEvent
        self.view.wheelEvent = self.wheel_event
    
    def set_mode(self, mode):
        """Set the current editing mode."""
        print(f"Setting mode to: {mode}")
        
        # Remember previous mode
        previous_mode = self.current_mode
        
        # Update mode
        self.current_mode = mode
        
        # Mode-specific setup
        if mode == "add_connection":
            self._show_all_device_ports()
        else:
            self._hide_all_device_ports()
        
        # Clean up any temporary objects
        if hasattr(self, 'temp_line') and self.temp_line:
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
        
        # Reset state when changing modes
        self.dragging_connection = False
        self.drag_source_device = None
        self.drag_source_port = None
        
        print(f"Mode changed from {previous_mode} to {mode}")

    def _show_all_device_ports(self):
        """Make all device ports visible."""
        if hasattr(self, 'device_manager') and self.device_manager:
            for device in self.device_manager.devices:
                if hasattr(device, 'show_all_ports'):
                    device.show_all_ports(True)
                    print(f"Showing ports on device {device}")

    def _hide_all_device_ports(self):
        """Hide all device ports."""
        if hasattr(self, 'device_manager') and self.device_manager:
            for device in self.device_manager.devices:
                if hasattr(device, 'show_all_ports'):
                    device.show_all_ports(False)

    def _clean_temporary_objects(self):
        """Remove any temporary visual objects."""
        if hasattr(self, 'temp_line') and self.temp_line:
            if self.temp_line in self.scene.items():
                self.scene.removeItem(self.temp_line)
            self.temp_line = None
    
    def set_connection_mode(self):
        """Enter connection creation mode."""
        self.current_mode = "add_connection"
        print(f"Mode changed to: {self.current_mode}")
    
    def mouse_press_event(self, event):
        """Handle mouse press events based on current mode."""
        try:
            # Convert to scene coordinates
            scene_pos = self.view.mapToScene(event.pos())
            print(f"Mouse press at {scene_pos.x()}, {scene_pos.y()} in mode {self.current_mode}")
            
            # Get clicked item
            item = self.view.itemAt(event.pos())
            
            # Handle based on current mode
            if self.current_mode == "add_device":
                self.handle_click(scene_pos)
                return True
                
            elif self.current_mode == "add_connection":
                # Find if we're clicking on a device
                device = None
                
                if isinstance(item, Device):
                    device = item
                elif hasattr(item, 'parentItem') and isinstance(item.parentItem(), Device):
                    device = item.parentItem()
                    
                if device:
                    if not hasattr(self, 'drag_source_device') or not self.drag_source_device:
                        # Start connection
                        closest_port, distance = device.get_closest_port(scene_pos)
                        if closest_port and distance < 15:  # Close enough to a port
                            self.drag_source_device = device
                            self.drag_source_port = closest_port
                            self.dragging_connection = True
                            self.drag_source_point = device.get_port_position(closest_port)
                            
                            # Highlight selected port
                            device.highlight_port(closest_port, True)
                            
                            print(f"Starting connection from device {device.properties.get('name', 'unnamed')} port {closest_port}")
                            return True
                            
            # Let the parent handle other cases
            super(type(self.view), self.view).mousePressEvent(event)
            return False
        
        except Exception as e:
            print(f"Error in mouse_press_event: {e}")
            import traceback
            traceback.print_exc()
            return False

    def mouse_release_event(self, event):
        """Handle mouse release events based on current mode."""
        try:
            scene_pos = self.view.mapToScene(event.pos())
            print(f"Mouse release at {scene_pos.x()}, {scene_pos.y()} in mode {self.current_mode}")
            
            # Handle connection completion
            if self.current_mode == "add_connection" and hasattr(self, 'dragging_connection') and self.dragging_connection:
                # Find what we're releasing over
                item_at_release = self.view.itemAt(event.pos())
                target_device = None
                
                # Find if we're releasing over a device
                if isinstance(item_at_release, Device):
                    target_device = item_at_release
                elif hasattr(item_at_release, 'parentItem') and isinstance(item_at_release.parentItem(), Device):
                    target_device = item_at_release.parentItem()
                
                # Create connection if we have valid source and target
                if (target_device and self.drag_source_device and 
                    target_device != self.drag_source_device):
                    
                    # Find closest port on target device
                    target_port, distance = target_device.get_closest_port(scene_pos)
                    
                    if target_port and distance < 15:  # Close enough to port
                        # Create the connection
                        connection = self.connection_manager.create_connection(
                            self.drag_source_device,
                            target_device,
                            "ethernet",  # Default type
                            self.drag_source_port,
                            target_port
                        )
                        
                        print(f"Created connection between {self.drag_source_device.properties.get('name', 'unnamed')} "
                              f"port {self.drag_source_port} and {target_device.properties.get('name', 'unnamed')} "
                              f"port {target_port}")
                
                # Clean up temporary objects
                if hasattr(self, 'temp_line') and self.temp_line:
                    self.scene.removeItem(self.temp_line)
                    self.temp_line = None
                
                # Reset highlighting on all ports
                if hasattr(self, 'device_manager'):
                    for device in self.device_manager.devices:
                        if hasattr(device, 'ports'):
                            for port_id in device.ports:
                                device.highlight_port(port_id, False)
                
                # Reset state
                self.dragging_connection = False
                self.drag_source_device = None
                self.drag_source_port = None
                
                return True
            
            # Let parent handle other cases
            super(type(self.view), self.view).mouseReleaseEvent(event)
            return False
            
        except Exception as e:
            print(f"Error in mouse_release_event: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _update_temp_connection(self, start_point, end_point):
        """Update the temporary connection line."""
        try:
            # Remove previous line if it exists
            if hasattr(self, 'temp_line') and self.temp_line:
                self.scene.removeItem(self.temp_line)
                self.temp_line = None
            
            # Create a path for the line
            from PyQt5.QtGui import QPainterPath, QPen, QColor
            from PyQt5.QtCore import Qt
            
            path = QPainterPath()
            path.moveTo(start_point)
            
            # Create orthogonal path
            mid_x = (start_point.x() + end_point.x()) / 2
            path.lineTo(mid_x, start_point.y())  # Horizontal segment
            path.lineTo(mid_x, end_point.y())    # Vertical segment
            path.lineTo(end_point)               # Final segment
            
            # Create a path item
            from PyQt5.QtWidgets import QGraphicsPathItem
            self.temp_line = QGraphicsPathItem(path)
            
            # Set style - dashed blue line
            pen = QPen(QColor(0, 120, 215), 2, Qt.DashLine)
            self.temp_line.setPen(pen)
            
            # Add to scene
            self.scene.addItem(self.temp_line)
            
            # Ensure it's visible on top
            self.temp_line.setZValue(1000)
            
        except Exception as e:
            print(f"Error updating temporary connection: {e}")
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

    def reset(self):
        """Reset the canvas to its initial state."""
        # Clear any temporary objects
        if hasattr(self, 'temp_line') and self.temp_line:
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
        
        # Reset connection state
        self.dragging_connection = False
        self.drag_source_device = None
        self.drag_source_port = None
        self.drag_source_point = None
        
        # Reset mode
        self.current_mode = "selection"
        
        print("Canvas controller reset")
    
    def start_pan(self, scene_pos):
        """Start panning the canvas."""
        self.is_panning = True
        self.last_pan_point = scene_pos
        
        # Change cursor to indicate panning
        self.view.viewport().setCursor(Qt.ClosedHandCursor)
    
    def pan(self, scene_pos):
        """Pan the canvas."""
        if not self.is_panning or not self.last_pan_point:
            return
        
        # Calculate the delta
        delta = self.view.mapToScene(scene_pos) - self.view.mapToScene(self.last_pan_point)
        
        # Pan the view
        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )
        
        # Update the last pan point
        self.last_pan_point = scene_pos
    
    def end_pan(self):
        """End panning the canvas."""
        self.is_panning = False
        self.last_pan_point = None
        
        # Reset cursor
        self.view.viewport().setCursor(Qt.ArrowCursor)
    
    def start_selection(self, scene_pos):
        """Start a selection rectangle."""
        self.is_selecting = True
        self.selection_start = scene_pos
    
    def update_selection(self, scene_pos):
        """Update the selection rectangle."""
        if not self.is_selecting or not self.selection_start:
            return
        
        # Calculate the selection rectangle
        x1 = min(self.selection_start.x(), scene_pos.x())
        y1 = min(self.selection_start.x(), scene_pos.y())
        x2 = max(self.selection_start.x(), scene_pos.x())
        y2 = max(self.selection_start.x(), scene_pos.y())
        
        selection_rect = QRectF(x1, y1, x2 - x1, y2 - y1)
        
        # Find items in the selection rectangle
        selected = self.scene.items(selection_rect)
        
        # Update selection state
        for item in self.scene.items():
            if hasattr(item, 'setSelected'):
                item.setSelected(item in selected)
        
        # Store selected items
        self.selected_items = selected
    
    def end_selection(self):
        """End the selection process."""
        self.is_selecting = False
        self.selection_start = None
    
    def start_connection(self, device, port):
        """Start creating a connection from a specific device and port."""
        self.connection_start_device = device
        self.connection_start_port = port
        
        # Change cursor to indicate connection creation
        self.view.viewport().setCursor(Qt.CrossCursor)
    
    def complete_connection(self, target_device, target_port):
        """Complete the connection to a target device and port."""
        if not self.connection_start_device or not target_device:
            return None
        
        if self.connection_start_device == target_device:
            # Don't allow connections to the same device
            return None
        
        # Create connection
        if self.connection_manager:
            connection = self.connection_manager.create_connection(
                self.connection_start_device,
                target_device,
                self.connection_start_port,
                target_port
            )
            
            # Reset connection state
            self.connection_start_device = None
            self.connection_start_port = None
            
            # Reset cursor
            self.view.viewport().setCursor(Qt.ArrowCursor)
            
            return connection
        
        return None
    
    def cancel_connection(self):
        """Cancel the current connection creation."""
        self.connection_start_device = None
        self.connection_start_port = None
        
        # Reset cursor
        self.view.viewport().setCursor(Qt.ArrowCursor)
    
    def start_drag(self, item, scene_pos):
        """Start dragging an item."""
        self.is_dragging = True
        self.dragged_item = item
        self.drag_start_pos = scene_pos
        
        # Change cursor to indicate dragging
        self.view.viewport().setCursor(Qt.DragMoveCursor)
    
    def drag(self, scene_pos):
        """Drag the current item to a new position."""
        if not self.is_dragging or not self.dragged_item or not self.drag_start_pos:
            return
        
        # Calculate the delta
        delta = scene_pos - self.drag_start_pos
        
        # Update item position
        self.dragged_item.setPos(
            self.dragged_item.pos() + delta
        )
        
        # Update drag start position
        self.drag_start_pos = scene_pos
    
    def end_drag(self):
        """End dragging the current item."""
        self.is_dragging = False
        self.dragged_item = None
        self.drag_start_pos = None
        
        # Reset cursor
        self.view.viewport().setCursor(Qt.ArrowCursor)
    
    def get_scene_position(self, view_pos):
        """Convert a view position to a scene position."""
        return self.view.mapToScene(view_pos)
    
    def get_view_position(self, scene_pos):
        """Convert a scene position to a view position."""
        return self.view.mapFromScene(scene_pos)
    
    def zoom_in(self, factor=1.2):
        """Zoom in the view."""
        self.view.scale(factor, factor)
    
    def zoom_out(self, factor=1.2):
        """Zoom out the view."""
        self.view.scale(1.0 / factor, 1.0 / factor)
    
    def reset_zoom(self):
        """Reset the zoom level."""
        self.view.resetTransform()
    
    def add_text(self, pos, text="New Text"):
        """Add a text item at the specified position."""
        text_item = QGraphicsTextItem(text)
        text_item.setPos(pos)
        text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        font = QFont()
        font.setPointSize(10)
        text_item.setFont(font)
        self.scene.addItem(text_item)
        text_item.setFocus()  # Start editing
        return text_item
    
    def add_boundary(self, rect, label="Boundary", color=QColor(200, 200, 255, 50)):
        """Add a boundary area with a label."""
        # Create the boundary rectangle
        boundary = QGraphicsRectItem(rect)
        boundary.setPen(QPen(Qt.black, 1, Qt.DashLine))
        boundary.setBrush(QBrush(color))
        boundary.setFlag(QGraphicsRectItem.ItemIsMovable)
        boundary.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.scene.addItem(boundary)
        
        # Add label above the boundary
        text_item = QGraphicsTextItem(label)
        text_item.setPos(rect.topLeft().x(), rect.topLeft().y() - 20)
        text_item.setFlag(QGraphicsTextItem.ItemIsMovable)
        text_item.setFlag(QGraphicsTextItem.ItemIsSelectable)
        self.scene.addItem(text_item)
        
        return boundary, text_item
    
    def start_temp_connection(self, source_device, source_port=None):
        """Start creating a temporary connection."""
        self.temp_connection_source = source_device
        self.temp_connection_source_port = source_port
        
        # Create a temporary line
        from PyQt5.QtWidgets import QGraphicsLineItem
        start_pos = source_device.mapToScene(source_device.width / 2, source_device.height / 2)
        if source_port:
            start_pos = source_device.get_port_position(source_port['name'])
        
        self.temp_connection = QGraphicsLineItem(start_pos.x(), start_pos.y(), start_pos.x(), start_pos.y())
        self.temp_connection.setPen(QPen(QColor(100, 100, 255), 2, Qt.DashLine))
        self.scene.addItem(self.temp_connection)
    
    def update_temp_connection(self, scene_pos):
        """Update the temporary connection endpoint."""
        if self.temp_connection:
            line = self.temp_connection.line()
            self.temp_connection.setLine(line.x1(), line.y1(), scene_pos.x(), scene_pos.y())
    
    def finish_temp_connection(self, target_device, target_port=None):
        """Finish creating a temporary connection."""
        if self.temp_connection:
            # Remove temporary line
            self.scene.removeItem(self.temp_connection)
            self.temp_connection = None
            
            # Create the actual connection
            if self.temp_connection_source and target_device:
                return self.add_connection(
                    self.temp_connection_source, 
                    target_device,
                    self.temp_connection_source_port,
                    target_port
                )
        
        return None
    
    def cancel_temp_connection(self):
        """Cancel any temporary connection being drawn."""
        # Make this method defensive against missing attributes
        if hasattr(self, 'temp_connection') and self.temp_connection:
            # Remove the temporary connection from the scene
            self.scene.removeItem(self.temp_connection)
            self.temp_connection = None
            return True
        return False
    
    def start_temp_rectangle(self, start_pos):
        """Start creating a temporary rectangle."""
        self.temp_rectangle = QGraphicsRectItem(QRectF(start_pos, QSizeF(0, 0)))
        self.temp_rectangle.setPen(QPen(Qt.black, 1, Qt.DashLine))
        self.temp_rectangle.setBrush(QBrush(QColor(200, 200, 255, 50)))
        self.scene.addItem(self.temp_rectangle)
        self.temp_rectangle_start = start_pos
    
    def update_temp_rectangle(self, end_pos):
        """Update the temporary rectangle."""
        if self.temp_rectangle:
            # Create rectangle from start to current
            x = min(self.temp_rectangle_start.x(), end_pos.x())
            y = min(self.temp_rectangle_start.y(), end_pos.y())
            width = abs(end_pos.x() - self.temp_rectangle_start.x())
            height = abs(end_pos.y() - self.temp_rectangle_start.y())
            
            self.temp_rectangle.setRect(x, y, width, height)
    
    def finish_temp_rectangle(self):
        """Finish creating a temporary rectangle."""
        if self.temp_rectangle:
            rect = self.temp_rectangle.rect()
            
            # Only create if it has some size
            if rect.width() >= 10 and rect.height() >= 10:
                boundary, label = self.add_boundary(rect)
                self.scene.removeItem(self.temp_rectangle)
                self.temp_rectangle = None
                return boundary
            else:
                self.cancel_temp_rectangle()
        
        return None
    
    def cancel_temp_rectangle(self):
        """Cancel creating a temporary rectangle."""
        if self.temp_rectangle:
            self.scene.removeItem(self.temp_rectangle)
            self.temp_rectangle = None
    
    def get_item_at(self, scene_pos, item_type=None):
        """Get an item at the specified position."""
        items = self.scene.items(scene_pos)
        
        if item_type:
            for item in items:
                if isinstance(item, item_type):
                    return item
            return None
        
        return items[0] if items else None
    
    def delete_selected_items(self):
        """Delete all selected items."""
        for item in self.scene.selectedItems():
            # Check if it's a device
            if hasattr(item, 'device_type') and self.device_manager:
                self.device_manager.remove_device(item)
            
            # Check if it's a connection
            elif hasattr(item, 'source_device') and hasattr(item, 'target_device') and self.connection_manager:
                self.connection_manager.remove_connection(item)
            
            # Otherwise generic item
            else:
                self.scene.removeItem(item)
    
    def clear_selection(self):
        """Clear the current selection."""
        for item in self.scene.selectedItems():
            item.setSelected(False)
        
        self.selected_items = []
        self.last_selected_item = None
    
    def select_all(self):
        """Select all items in the scene."""
        for item in self.scene.items():
            if item.flags() & QGraphicsItem.ItemIsSelectable:
                item.setSelected(True)
        
        self.selected_items = self.scene.selectedItems()
        self.last_selected_item = self.selected_items[0] if self.selected_items else None
    
    def reset(self):
        """Reset the canvas controller state."""
        self.cancel_temp_connection()
        self.cancel_temp_rectangle()
        self.clear_selection()
        self.selected_items = []
        self.last_selected_item = None

    def add_device(self, device_type, scene_pos):
        """Add a new device to the scene.
        
        Args:
            device_type: Type of device to add (router, switch, etc.)
            scene_pos: QPointF position in scene coordinates
        
        Returns:
            The created device or None if creation failed
        """
        try:
            # Check if we have access to a device manager
            if not hasattr(self, 'device_manager') or not self.device_manager:
                print("Cannot add device: No device manager available")
                return None
            
            # Get position coordinates
            x = scene_pos.x()
            y = scene_pos.y()
            
            print(f"Adding {device_type} device at position ({x}, {y})")
            
            # Create the device through the device manager
            device = self.device_manager.create_device(device_type, x, y)
            
            # Notify about the new device
            if hasattr(self, 'main_window') and self.main_window:
                self.main_window.statusBar().showMessage(f"Added {device_type} device", 3000)
            
            return device
        except Exception as e:
            import traceback
            print(f"Error adding device: {e}")
            traceback.print_exc()
            return None

    def start_temp_connection(self, source_device):
        """Start creating a temporary connection from source device."""
        self.source_device = source_device
        
        # Create a temporary line
        self.temp_connection = QGraphicsLineItem()
        self.temp_connection.setPen(QPen(QColor(100, 100, 100), 2, Qt.DashLine))
        
        # Get source position
        source_pos = QPointF(source_device.x + 40, source_device.y + 25)
        
        # Set initial line position
        self.temp_connection.setLine(
            source_pos.x(), source_pos.y(),
            source_pos.x(), source_pos.y()
        )
        
        # Add to scene
        self.scene.addItem(self.temp_connection)
        
        return self.temp_connection
    
    def update_temp_connection(self, target_pos):
        """Update temporary connection to follow mouse."""
        if not self.temp_connection or not self.source_device:
            return
            
        # Get source position
        source_pos = QPointF(self.source_device.x + 40, self.source_device.y + 25)
        
        # Update line
        self.temp_connection.setLine(
            source_pos.x(), source_pos.y(),
            target_pos.x(), target_pos.y()
        )
    
    def finish_temp_connection(self, target_device):
        """Complete the temporary connection to the target device."""
        if not self.temp_connection or not self.source_device or not target_device:
            return self.cancel_temp_connection()
            
        # Remove temporary line
        if self.temp_connection:
            self.scene.removeItem(self.temp_connection)
            self.temp_connection = None
        
        # Create actual connection
        if self.connection_manager:
            connection = self.connection_manager.create_connection(
                self.source_device, target_device)
            self.source_device = None
            return connection
        
        return None
    
    def cancel_temp_connection(self):
        """Cancel temporary connection creation."""
        if self.temp_connection:
            self.scene.removeItem(self.temp_connection)
            self.temp_connection = None
        self.source_device = None
        return True

    def clear_grid(self):
        """Remove any grid lines from the scene."""
        if not self.scene:
            return
        
        # Remove any items that might be grid lines
        grid_items = []
        for item in self.scene.items():
            # Check if this item looks like a grid line
            if isinstance(item, QGraphicsLineItem):
                # Check if it's a grid line (usually thin, gray, in a regular pattern)
                pen = item.pen()
                if pen.width() <= 1 and pen.color() == Qt.gray:
                    grid_items.append(item)
        
        # Remove them all
        for item in grid_items:
            self.scene.removeItem(item)
        
        print(f"Removed {len(grid_items)} grid lines")
    
    def toggle_grid(self, visible):
        """Toggle grid visibility."""
        if visible:
            self.add_grid()
        else:
            self.clear_grid()
    
    def add_grid(self):
        """Add a grid to the scene."""
        self.clear_grid()  # Clear existing grid first
        
        if not self.scene:
            return
            
        grid_size = 50
        grid_color = QColor(230, 230, 230)
        
        # Draw vertical lines
        for x in range(-1000, 1000, grid_size):
            line = QGraphicsLineItem(x, -1000, x, 1000)
            line.setPen(Qt.gray)
            line.setZValue(-1)  # Put grid behind other items
            self.scene.addItem(line)
            self.grid_items.append(line)
        
        # Draw horizontal lines
        for y in range(-1000, 1000, grid_size):
            line = QGraphicsLineItem(-1000, y, 1000, y)
            line.setPen(Qt.gray)
            line.setZValue(-1)  # Put grid behind other items
            self.scene.addItem(line)
            self.grid_items.append(line)
        
        self.grid_visible = True

    def handle_scene_mouse_press(self, event):
        """Handle mouse press events on the scene."""
        if self.mode == "device_mode":
            # Create a device at the click location
            pos = event.scenePos()
            device = self.device_manager.create_device(
                self.selected_device_type,
                pos.x(), 
                pos.y()
            )
            print(f"Created device: {device.id} at ({pos.x()}, {pos.y()})")