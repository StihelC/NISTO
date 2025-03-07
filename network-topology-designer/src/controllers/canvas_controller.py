from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QApplication
from PyQt5.QtCore import Qt, QPointF, QObject, QTimer
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from controllers.device_manager import DeviceManager
from ui.device_dialog import DeviceSelectionDialog
from controllers.connection_manager import ConnectionManager
from models.device import NetworkDevice
import math

DEBUG_BOUNDARY = True

class CanvasController(QObject):
    """Controls interactions with the canvas."""
    
    def __init__(self, view, scene, connection_manager, device_manager):
        super().__init__()
        self.view = view
        self.scene = scene
        self.connection_manager = connection_manager
        self.device_manager = device_manager
        self.current_mode = "selection"
        self.temp_line = None
        
        # Connection drag state
        self.drag_source_device = None
        self.drag_source_port = None
        self.drag_source_point = None
        self.dragging_connection = False
        
        # Install event filter
        self.view.viewport().installEventFilter(self)
        self.device_dialog_active = False  # Add this flag
    
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
        prev_mode = self.current_mode if hasattr(self, 'current_mode') else None
        self.current_mode = mode
        print(f"Canvas mode changed from {prev_mode} to {mode}")
        
        try:
            # Clean up any temporary items
            if hasattr(self, '_clear_temp_items'):
                self._clear_temp_items()
            
            # Set up mode-specific behavior
            if mode == "selection":
                # Set selection-specific state
                from PyQt5.QtWidgets import QGraphicsView
                self.view.setDragMode(QGraphicsView.RubberBandDrag)
                from PyQt5.QtCore import Qt
                self.view.setCursor(Qt.ArrowCursor)
                
            elif mode == "add_boundary":
                # Set boundary-specific state
                from PyQt5.QtWidgets import QGraphicsView
                self.view.setDragMode(QGraphicsView.NoDrag)
                from PyQt5.QtCore import Qt
                self.view.setCursor(Qt.CrossCursor)
                print("Boundary mode activated - click and drag to create a boundary")
                
            # ...other modes...
            
        except Exception as e:
            print(f"Error setting mode {mode}: {e}")
            import traceback
            traceback.print_exc()

    def _enable_item_selection(self, enable):
        """Enable or disable item selection and movement."""
        from PyQt5.QtWidgets import QGraphicsItem
        
        # Find all items in the scene that should be selectable
        from models.device import NetworkDevice
        
        for item in self.scene.items():
            # Enable selection for devices and other custom items
            if isinstance(item, NetworkDevice):
                item.setFlag(QGraphicsItem.ItemIsSelectable, enable)
                item.setFlag(QGraphicsItem.ItemIsMovable, enable)
            
            # You can add additional item types here as needed
            # elif isinstance(item, SomeOtherClass):
            #     item.setFlag(QGraphicsItem.ItemIsSelectable, enable)

    def _set_ports_visible(self, visible):
        """Show or hide all device ports."""
        from models.device import NetworkDevice
        
        for item in self.scene.items():
            if isinstance(item, NetworkDevice) and hasattr(item, 'show_all_ports'):
                item.show_all_ports(visible)

    def _set_devices_draggable(self, draggable):
        """Enable or disable device dragging."""
        from models.device import NetworkDevice
        from PyQt5.QtWidgets import QGraphicsItem
        
        for item in self.scene.items():
            if isinstance(item, NetworkDevice):
                item.setFlag(QGraphicsItem.ItemIsMovable, draggable)
    
    def set_quick_add_mode(self, device_type):
        """Set the mode to quickly add a device of the specified type."""
        self.current_mode = "quick_add"
        self.quick_add_type = device_type
        
    def handle_click(self, scene_pos):
        """Handle mouse clicks based on current mode."""
        try:
            current_mode = self.current_mode if hasattr(self, 'current_mode') else "selection"
            print(f"Canvas handling click in mode: {current_mode}")
            
            if current_mode == "add_boundary":
                print(f"Starting boundary creation at {scene_pos.x()}, {scene_pos.y()}")
                self._handle_boundary_start(scene_pos)
                return True
                
            elif current_mode == "add_device":
                self._handle_add_device_click(scene_pos)
                return True
                
            # For selection mode or other modes, let the default handler work
            return False
            
        except Exception as e:
            print(f"Error in handle_click: {e}")
            import traceback
            traceback.print_exc()
            return False

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
            if obj == self.view.viewport():
                if event.type() == event.MouseButtonPress:
                    self.mouse_press_event(event)
                elif event.type() == event.MouseMove:
                    self.mouse_move_event(event)
                elif event.type() == event.MouseButtonRelease:
                    self.mouse_release_event(event)
            return super().eventFilter(obj, event)
        except Exception as e:
            print(f"Error in eventFilter: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Modify the mouse_press_event method to better detect ports
    def mouse_press_event(self, event):
        """Handle mouse press events on the canvas."""
        try:
            # Convert mouse position to scene coordinates
            scene_pos = self.view.mapToScene(event.pos())
            print(f"Mouse pressed in mode: {self.current_mode}")
            print(f"Scene position: ({scene_pos.x()}, {scene_pos.y()})")
            
            # Get the item at the click position
            item = self.view.itemAt(event.pos())
            
            if self.current_mode == "add_connection":
                from models.device import NetworkDevice
                
                # If clicked on a device, start connection drag
                if isinstance(item, NetworkDevice):
                    event.accept()  # Accept to prevent default behavior
                    device = item
                    
                    # Initialize connection drag state
                    self.dragging_connection = False
                    self.drag_source_device = None
                    self.drag_source_port = None
                    self.drag_source_point = None
                    
                    # Find the closest port
                    closest_port = None
                    distance = float('inf')
                    
                    if hasattr(device, 'get_closest_port'):
                        closest_port, distance = device.get_closest_port(scene_pos)
                        print(f"Closest port: {closest_port}, distance: {distance}")
                    
                    # Always use a port for connection start (closest one)
                    if closest_port:
                        # Start connection from the port
                        self.drag_source_device = device
                        self.drag_source_port = closest_port
                        
                        # Get exact port position for line start
                        if hasattr(device, 'get_port_position'):
                            self.drag_source_point = device.get_port_position(closest_port)
                        else:
                            self.drag_source_point = device.sceneBoundingRect().center()
                        
                        # Highlight the selected port
                        if hasattr(device, 'highlight_port'):
                            device.highlight_port(closest_port, True)
                        
                        self.dragging_connection = True
                        
                        # Create temporary line
                        from PyQt5.QtCore import Qt
                        from PyQt5.QtGui import QPen, QColor
                        
                        self.temp_line = self.scene.addLine(
                            self.drag_source_point.x(), self.drag_source_point.y(),
                            scene_pos.x(), scene_pos.y(),
                            QPen(QColor(100, 100, 255, 200), 2, Qt.DashLine)
                        )
                        
                        print(f"Starting connection from device {device.properties.get('name', 'unnamed')}, port {closest_port}")
                        
                        return True  # Event handled
                    
                # If clicking elsewhere while dragging, cancel
                elif hasattr(self, 'dragging_connection') and self.dragging_connection:
                    # Clean up
                    if hasattr(self, 'temp_line') and self.temp_line and self.temp_line.scene():
                        self.scene.removeItem(self.temp_line)
                        self.temp_line = None
                    
                    # Reset port highlights
                    if hasattr(self, 'drag_source_device') and self.drag_source_device:
                        if hasattr(self.drag_source_device, 'reset_port_highlights'):
                            self.drag_source_device.reset_port_highlights()
                    
                    # Reset drag state
                    self.dragging_connection = False
                    self.drag_source_device = None
                    self.drag_source_port = None
                    self.drag_source_point = None
                    
                    print("Connection drag canceled")
                    return True
            
            elif self.current_mode == "add_device":
                # Only add device if clicking on empty space
                if not item:
                    self.handle_click(scene_pos)
            
            # Let default handler process for other modes/cases
            return False
            
        except Exception as e:
            print(f"Error in mouse_press_event: {e}")
            import traceback
            traceback.print_exc()
            return False

    def edit_connection(self, connection):
        """Show dialog to edit connection properties."""
        from ui.connection_dialog import ConnectionPropertiesDialog

        dialog = ConnectionPropertiesDialog(
            connection.source_device,
            connection.target_device,
            connection.connection_type,
            connection.source_port,
            connection.target_port
        )

        if dialog.exec_():
            # Update connection properties
            connection.connection_type = dialog.get_connection_type()
            connection.source_port = dialog.get_source_port()
            connection.target_port = dialog.get_target_port()
            connection.update_path()
            print(f"Updated connection: {connection.connection_type}")

    # Improve mouse_move_event to highlight port better
    def mouse_move_event(self, event):
        """Handle mouse move events on the canvas."""
        try:
            # Get scene position
            scene_pos = self.view.mapToScene(event.pos())
            
            # Update temporary connection line during dragging
            if (hasattr(self, 'dragging_connection') and self.dragging_connection and 
                hasattr(self, 'temp_line') and self.temp_line and 
                hasattr(self, 'drag_source_point') and self.drag_source_point):
                
                # Update the line endpoint
                self.temp_line.setLine(
                    self.drag_source_point.x(), self.drag_source_point.y(),
                    scene_pos.x(), scene_pos.y()
                )
                
                # Check if hovering over a device
                item_at_cursor = self.view.itemAt(event.pos())
                
                from models.device import NetworkDevice
                
                # Reset highlights on all devices except source
                for device_item in self.scene.items():
                    if (isinstance(device_item, NetworkDevice) and 
                        device_item != self.drag_source_device and
                        hasattr(device_item, 'reset_port_highlights')):
                        device_item.reset_port_highlights()
                        
                        # Hide ports on devices we're not hovering over
                        if device_item != item_at_cursor and hasattr(device_item, 'show_all_ports'):
                            device_item.show_all_ports(False)
                
                # If hovering over a device, highlight its ports
                if (isinstance(item_at_cursor, NetworkDevice) and 
                    item_at_cursor != self.drag_source_device):
                    
                    # Show this device's ports
                    if hasattr(item_at_cursor, 'show_all_ports'):
                        item_at_cursor.show_all_ports(True)
                    
                    # Highlight the closest port if within range
                    closest_port = None
                    distance = float('inf')
                    
                    if hasattr(item_at_cursor, 'get_closest_port'):
                        closest_port, distance = item_at_cursor.get_closest_port(scene_pos)
                    
                    if closest_port and distance <= 20 and hasattr(item_at_cursor, 'highlight_port'):
                        item_at_cursor.highlight_port(closest_port, True)
                        
                        # Draw the line to the exact port position
                        if hasattr(item_at_cursor, 'get_port_position'):
                            target_point = item_at_cursor.get_port_position(closest_port)
                            self.temp_line.setLine(
                                self.drag_source_point.x(), self.drag_source_point.y(),
                                target_point.x(), target_point.y()
                            )
                        
            # Call the parent class's mouseMoveEvent for default behavior
            if hasattr(self.view.__class__, 'mouseMoveEvent'):
                super(self.view.__class__, self.view).mouseMoveEvent(event)
            
        except Exception as e:
            print(f"Error in mouse_move_event: {e}")
            import traceback
            traceback.print_exc()
    
    def mouse_release_event(self, event):
        """Handle mouse release events on the canvas."""
        try:
            if not hasattr(self, 'current_mode'):
                return False
                
            # Convert mouse position to scene coordinates
            scene_pos = self.view.mapToScene(event.pos())
                
            if self.current_mode == "add_boundary" and hasattr(self, 'boundary_start'):
                self._handle_boundary_finish(scene_pos)
                return True
                
            return False
            
        except Exception as e:
            print(f"Error in handle_mouse_release: {e}")
            import traceback
            traceback.print_exc()
            return False

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

    # Add this method to toggle device drag capability
    def set_devices_draggable(self, draggable=True):
        """Enable or disable dragging for all devices in the scene."""
        from models.device import NetworkDevice
        
        for item in self.scene.items():
            if isinstance(item, NetworkDevice):
                item.setFlag(QGraphicsItem.ItemIsMovable, draggable)
                print(f"Set device {item.properties.get('name', 'unnamed')} draggable: {draggable}")
    
    def handle_mouse_press(self, event, scene_pos):
        """Handle mouse press events."""
        print(f"Mouse pressed in mode: {self.current_mode}")
        print(f"Scene position: ({scene_pos.x():.1f}, {scene_pos.y():.1f})")
        
        # Get the item at the click position
        item = self.view.itemAt(event.pos()) if event else None
        
        if self.current_mode == "add_device" and (not item or not event):
            # Add new device at the clicked position
            self._handle_add_device(scene_pos)
            return True
            
        elif self.current_mode == "add_connection":
            # Handle connection creation
            return self._handle_connection_start(event, scene_pos, item)
            
        elif self.current_mode == "add_textbox" and (not item or not event):
            # Add new text box
            self._handle_add_textbox(scene_pos)
            return True
            
        elif self.current_mode == "add_boundary" and (not item or not event):
            # Start creating boundary
            self._handle_boundary_start(scene_pos)
            return True
            
        elif self.current_mode == "delete" and item:
            # Delete the item
            self._handle_delete_item(item)
            return True
            
        return False  # Not handled
    
    def handle_mouse_move(self, event, scene_pos, delta_x=0, delta_y=0):
        """Handle mouse movement."""
        try:
            if not hasattr(self, 'current_mode'):
                return False
                
            if self.current_mode == "add_boundary" and hasattr(self, 'boundary_start'):
                # Update boundary preview during drag
                if hasattr(self, 'temp_rect') and self.temp_rect:
                    # Calculate rectangle dimensions
                    start_x = min(self.boundary_start.x(), scene_pos.x())
                    start_y = min(self.boundary_start.y(), scene_pos.y())
                    width = abs(scene_pos.x() - self.boundary_start.x())
                    height = abs(scene_pos.y() - self.boundary_start.y())
                    
                    # Update rectangle dimensions
                    self.temp_rect.setRect(start_x, start_y, width, height)
                    
                    # Make sure boundary is visible on top
                    self.temp_rect.setZValue(100)
                    
                    # Force scene to update immediately
                    self.scene.update(self.temp_rect.boundingRect())
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error in handle_mouse_move: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def handle_mouse_release(self, event, scene_pos):
        """Handle mouse release events."""
        try:
            if not hasattr(self, 'current_mode'):
                return False
                
            if self.current_mode == "add_boundary" and hasattr(self, 'boundary_start'):
                self._handle_boundary_finish(scene_pos)
                return True
                
            return False
            
        except Exception as e:
            print(f"Error in handle_mouse_release: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _handle_add_device(self, scene_pos):
        """Add a device at the specified position."""
        from PyQt5.QtWidgets import QDialog
        from ui.device_dialog import DeviceDialog
        
        dialog = DeviceDialog(self.view)
        if dialog.exec_() == QDialog.Accepted:
            device_type = dialog.selected_type
            name = dialog.name_edit.text()
            ip = dialog.ip_edit.text()
            desc = dialog.desc_edit.toPlainText()
            
            properties = {
                'name': name,
                'ip_address': ip,
                'description': desc
            }
            
            print(f"Adding {device_type} named '{name}' with properties: {properties}")
            
            self.device_manager.create_device(
                device_type, 
                scene_pos.x(), 
                scene_pos.y(),
                properties=properties
            )
            return True
        
        return False

    def _handle_boundary_start(self, scene_pos):
        """Start creating a boundary area."""
        print(f"Creating temporary rectangle at {scene_pos.x()}, {scene_pos.y()}")
        try:
            # Store the start position
            self.boundary_start = scene_pos
            
            # Create a temporary rectangle to show the boundary
            from PyQt5.QtWidgets import QGraphicsRectItem
            from PyQt5.QtGui import QPen, QBrush, QColor
            from PyQt5.QtCore import Qt, QRectF
            
            # Initial rectangle with 1x1 size (will be resized during drag)
            rect = QRectF(scene_pos.x(), scene_pos.y(), 1, 1)
            self.temp_rect = QGraphicsRectItem(rect)
            
            # Make it stand out more for better visibility
            pen = QPen(Qt.DashLine)
            pen.setWidth(2)  # Thicker border
            pen.setColor(QColor(0, 0, 255))  # Blue border
            self.temp_rect.setPen(pen)
            
            # Semi-transparent fill
            self.temp_rect.setBrush(QBrush(QColor(120, 120, 255, 80)))
            
            # Make sure it's on top
            self.temp_rect.setZValue(100)
            
            # Add to scene
            self.scene.addItem(self.temp_rect)
            
            # Store in temp items list
            if not hasattr(self, 'temp_items'):
                self.temp_items = []
            self.temp_items.append(self.temp_rect)
            
            print("Temporary rectangle created - drag to resize")
            return True
            
        except Exception as e:
            print(f"Error starting boundary: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _handle_boundary_drag(self, scene_pos):
        """Update boundary size during dragging."""
        if hasattr(self, 'temp_rect') and self.temp_rect:
            # Calculate the new rectangle
            start_x = min(self.boundary_start.x(), scene_pos.x())
            start_y = min(self.boundary_start.y(), scene_pos.y())
            width = abs(scene_pos.x() - self.boundary_start.x())
            height = abs(scene_pos.y() - self.boundary_start.y())
            
            # Update the rectangle
            self.temp_rect.setRect(start_x, start_y, width, height)

    def _handle_boundary_finish(self, scene_pos):
        """Complete the boundary creation."""
        try:
            if not hasattr(self, 'temp_rect') or not self.temp_rect:
                return False
                
            # Calculate the final rectangle dimensions
            rect = self.temp_rect.rect()
            
            # Only create if it has reasonable size
            if rect.width() > 10 and rect.height() > 10:
                from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QInputDialog
                from PyQt5.QtGui import QPen, QBrush, QColor, QFont
                from PyQt5.QtCore import Qt, QRectF
                
                # Create final rectangle
                final_rect = QGraphicsRectItem(rect)
                final_rect.setPen(QPen(Qt.DashLine))
                final_rect.setBrush(QBrush(QColor(200, 200, 255, 80)))
                
                # Add label
                try:
                    label_text, ok = QInputDialog.getText(
                        self.view, "Boundary Label", "Enter label for this boundary:",
                        text="Network Boundary"
                    )
                    
                    if ok and label_text:
                        text_item = QGraphicsTextItem(label_text)
                        text_item.setPos(rect.x(), rect.y() - 25)
                        text_item.setFont(QFont("Arial", 10, QFont.Bold))
                        self.scene.addItem(text_item)
                except Exception as dialog_err:
                    print(f"Error with dialog: {dialog_err}")
                
                # Add the rectangle to scene
                self.scene.addItem(final_rect)
            
            # Clean up temporary rectangle
            if self.temp_rect.scene() == self.scene:
                self.scene.removeItem(self.temp_rect)
            
            # Reset state
            self.temp_rect = None
            if hasattr(self, 'boundary_start'):
                delattr(self, 'boundary_start')
            
            return True
            
        except Exception as e:
            print(f"Error finishing boundary: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _clear_temp_items(self):
        """Clear any temporary visual elements."""
        # Clear temporary items list
        if hasattr(self, 'temp_items'):
            for item in self.temp_items:
                if item.scene() == self.scene:
                    self.scene.removeItem(item)
            self.temp_items = []
        
        # Clear temporary rectangle for boundary creation
        if hasattr(self, 'temp_rect') and self.temp_rect:
            if self.temp_rect.scene() == self.scene:
                self.scene.removeItem(self.temp_rect)
            self.temp_rect = None
        
        # Clear boundary start point if it exists
        if hasattr(self, 'boundary_start'):
            delattr(self, 'boundary_start')
        
        # Clear any other mode-specific temporary elements
        # ...

    def _handle_add_device_click(self, scene_pos):
        """Handle a click in add device mode."""
        print("Starting device creation flow")
        
        try:
            # Create an inline device dialog instead of importing
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout
            from PyQt5.QtWidgets import QLineEdit, QComboBox, QDialogButtonBox, QTextEdit, QLabel
            
            class SimpleDeviceDialog(QDialog):
                """Dialog for creating network devices."""
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.setWindowTitle("Add Device")
                    
                    # Default values
                    self.selected_type = "router"
                    
                    # Create layout
                    layout = QVBoxLayout()
                    self.setLayout(layout)
                    
                    # Device type selection
                    type_layout = QHBoxLayout()
                    type_layout.addWidget(QLabel("Device Type:"))
                    
                    # Combo box for device type
                    self.type_combo = QComboBox()
                    self.type_combo.addItems(["router", "switch", "firewall", "server", "workstation"])
                    self.type_combo.currentTextChanged.connect(self.on_type_changed)
                    type_layout.addWidget(self.type_combo)
                    
                    layout.addLayout(type_layout)
                    
                    # Name field
                    name_layout = QHBoxLayout()
                    name_layout.addWidget(QLabel("Name:"))
                    self.name_edit = QLineEdit()
                    name_layout.addWidget(self.name_edit)
                    layout.addLayout(name_layout)
                    
                    # IP address field
                    ip_layout = QHBoxLayout()
                    ip_layout.addWidget(QLabel("IP Address:"))
                    self.ip_edit = QLineEdit()
                    ip_layout.addWidget(self.ip_edit)
                    layout.addLayout(ip_layout)
                    
                    # Description field
                    layout.addWidget(QLabel("Description:"))
                    self.desc_edit = QTextEdit()
                    self.desc_edit.setMaximumHeight(100)
                    layout.addWidget(self.desc_edit)
                    
                    # OK/Cancel buttons
                    self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                    self.buttonBox.accepted.connect(self.accept)
                    self.buttonBox.rejected.connect(self.reject)
                    layout.addWidget(self.buttonBox)
                
                def on_type_changed(self, text):
                    """Handle device type change."""
                    self.selected_type = text
            
            # Create and show the dialog
            dialog = SimpleDeviceDialog(self.view.parent())
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                device_type = dialog.selected_type
                name = dialog.name_edit.text() if hasattr(dialog, 'name_edit') else ""
                
                # Create properties dictionary
                properties = {'name': name}
                if hasattr(dialog, 'ip_edit'):
                    properties['ip_address'] = dialog.ip_edit.text()
                if hasattr(dialog, 'desc_edit'):
                    properties['description'] = dialog.desc_edit.toPlainText()
                
                # Create the device
                print(f"Creating {device_type} at ({scene_pos.x()}, {scene_pos.y()})")
                self.device_manager.create_device(device_type, scene_pos.x(), scene_pos.y(), properties=properties)
            else:
                print("Device creation canceled by user")
        
        except Exception as e:
            print(f"Error in add device dialog: {e}")
            import traceback
            traceback.print_exc()
        
        return True  # Always return a boolean value