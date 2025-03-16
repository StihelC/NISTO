from PyQt5.QtCore import QObject, QPointF, Qt
from PyQt5.QtGui import QPen, QColor, QPainterPath
from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsPathItem, QGraphicsEllipseItem

# Import our consolidated Device class
try:
    from src.models.device import Device
except ImportError:
    # Fallback to relative imports
    from ..models.device import Device
import uuid

class ConnectionItem(QGraphicsPathItem):
    """A visual connection between two devices."""
    
    def __init__(self, source_device, source_port, target_device, target_port, connection_type="ethernet"):
        """Initialize a connection between devices."""
        super().__init__()
        
        # Store connection properties
        self.id = str(uuid.uuid4())[:8]
        self.source_device = source_device
        self.source_port = source_port
        self.target_device = target_device
        self.target_port = target_port
        self.connection_type = connection_type
        
        # Set visual appearance based on type
        if connection_type == "ethernet":
            self.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))
        elif connection_type == "wireless":
            self.setPen(QPen(QColor(0, 0, 200), 2, Qt.DashLine))
        elif connection_type == "serial":
            self.setPen(QPen(QColor(200, 0, 0), 2, Qt.SolidLine))
        else:
            self.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))
        
        # Make connections appear behind devices
        self.setZValue(-1)
        
        # Update the path
        self.update_path()
        
        # Connect to device position changed signals
        if hasattr(source_device, "position_changed"):
            self.source_device.position_changed.connect(self.update_path)
        if hasattr(target_device, "position_changed"):
            self.target_device.position_changed.connect(self.update_path)
    
    def update_path(self):
        """Update the connection path based on current device positions."""
        try:
            # Get port positions
            source_pos = self.source_device.get_port_position(self.source_port["name"])
            target_pos = self.target_device.get_port_position(self.target_port["name"])
            
            # Create path
            path = QPainterPath()
            path.moveTo(source_pos)
            
            # Calculate midpoint for control points
            mid_x = (source_pos.x() + target_pos.x()) / 2
            mid_y = (source_pos.y() + target_pos.y()) / 2
            
            # Create a curved path
            if self.connection_type == "ethernet":
                # Simple curve
                path.cubicTo(
                    mid_x, source_pos.y(),  # Control point 1
                    mid_x, target_pos.y(),  # Control point 2
                    target_pos.x(), target_pos.y()  # End point
                )
            elif self.connection_type == "wireless":
                # Straight line for wireless
                path.lineTo(target_pos)
            else:
                # Default curved path
                path.cubicTo(
                    mid_x, source_pos.y(),
                    mid_x, target_pos.y(),
                    target_pos.x(), target_pos.y()
                )
            
            # Set the path
            self.setPath(path)
            
        except Exception as e:
            print(f"Error updating connection path: {e}")
            import traceback
            traceback.print_exc()
    
    def cleanup(self):
        """Disconnect signals to prevent memory leaks."""
        try:
            if hasattr(self.source_device, "position_changed"):
                self.source_device.position_changed.disconnect(self.update_path)
            if hasattr(self.target_device, "position_changed"):
                self.target_device.position_changed.disconnect(self.update_path)
        except:
            # It's okay if disconnect fails
            pass


class ConnectionCreationTool(QObject):
    """Tool for creating connections between devices."""

    def __init__(self, canvas_controller, connection_manager=None):
        """Initialize the connection creation tool."""
        super().__init__()
        self.canvas_controller = canvas_controller
        self.scene = canvas_controller.scene if canvas_controller else None
        
        # Store connection manager reference
        self.connection_manager = connection_manager
        
        # State tracking
        self.source_device = None
        self.source_port = None
        self.target_device = None
        self.target_port = None
        self.temp_line = None
        self.dragging = False
        self.start_point = None
        
        # Port indicators for visual feedback
        self.port_indicators = []
    
    def handle_press(self, event, scene_pos):
        """Handle mouse press events for connection creation."""
        if not self.scene:
            return False
            
        try:
            # Find what was clicked
            item = self.scene.itemAt(scene_pos, self.scene.views()[0].transform())
            
            # Check if we clicked on a device
            if isinstance(item, Device):
                self.dragging = True
                self.source_device = item
                
                # Find closest port to click position
                port, _ = item.get_closest_port(scene_pos)
                self.source_port = port
                
                # Get port position
                start_point = item.get_port_position(port["name"]) if port else item.scenePos()
                self.start_point = start_point
                
                # Create temporary visual feedback
                if self.temp_line and self.temp_line.scene() == self.scene:
                    self.scene.removeItem(self.temp_line)
                
                # Create new temp line
                self.temp_line = QGraphicsLineItem(
                    start_point.x(), start_point.y(), 
                    scene_pos.x(), scene_pos.y()
                )
                self.temp_line.setPen(QPen(QColor(0, 120, 215), 2, Qt.DashLine))
                self.scene.addItem(self.temp_line)
                
                # Show port indicators on other devices
                self.show_port_indicators()
                
                print(f"Starting connection from {item.name}, port {port['name'] if port else 'default'}")
                return True
            
        except Exception as e:
            print(f"Error in connection press: {e}")
            import traceback
            traceback.print_exc()
            
        return False
    
    def handle_move(self, event, scene_pos):
        """Handle mouse move events during connection creation."""
        if not self.dragging or not self.source_device or not self.temp_line:
            return False
            
        try:
            # Update the temp line
            source_pos = self.start_point
            self.temp_line.setLine(
                source_pos.x(), source_pos.y(),
                scene_pos.x(), scene_pos.y()
            )
            return True
            
        except Exception as e:
            print(f"Error in connection move: {e}")
            
        return False
    
    def handle_release(self, event, scene_pos):
        """Handle mouse release events to complete connection creation."""
        if not self.dragging or not self.source_device:
            return False
            
        try:
            # Find what's under the cursor at release
            item = self.scene.itemAt(scene_pos, self.scene.views()[0].transform())
            
            # Check if we released on a device
            if isinstance(item, Device) and item != self.source_device:
                # Find closest port to release position
                target_port, _ = item.get_closest_port(scene_pos)
                
                if self.source_port and target_port:
                    # Create the connection
                    self.create_connection(item, target_port)
            
            # Clean up
            self.clear_temp_connection()
            return True
            
        except Exception as e:
            print(f"Error in connection release: {e}")
            import traceback
            traceback.print_exc()
            
            # Clean up on error
            self.clear_temp_connection()
            
        return False
    
    def create_connection(self, target_device, target_port, connection_type="ethernet"):
        """Create a connection between source and target devices."""
        try:
            if not self.source_device or not self.source_port or not target_device or not target_port:
                print("Missing required elements for connection")
                return None
                
            # Create the connection item
            connection = ConnectionItem(
                self.source_device,
                self.source_port,
                target_device,
                target_port,
                connection_type
            )
            
            # Add to scene
            if self.scene:
                self.scene.addItem(connection)
                
            # Update port connected status
            self.source_port["connected"] = True
            target_port["connected"] = True
            
            # Update device connections if they have the methods
            if hasattr(self.source_device, "add_connection"):
                self.source_device.add_connection(connection)
            if hasattr(target_device, "add_connection"):
                target_device.add_connection(connection)
                
            # Delegate to connection manager if available
            if self.connection_manager:
                self.connection_manager.register_connection(connection)
                
            print(f"Created {connection_type} connection: {self.source_device.name}:{self.source_port['name']} → {target_device.name}:{target_port['name']}")
            
            return connection
            
        except Exception as e:
            print(f"Error creating connection: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def clear_temp_connection(self):
        """Clean up temporary connection elements."""
        try:
            # Remove temporary line
            if self.temp_line and self.scene:
                self.scene.removeItem(self.temp_line)
                self.temp_line = None
                
            # Remove port indicators
            self.clear_port_indicators()
                
            # Reset state
            self.dragging = False
            self.source_device = None
            self.source_port = None
            self.start_point = None
            
        except Exception as e:
            print(f"Error clearing temporary connection: {e}")
    
    def show_port_indicators(self):
        """Show visual indicators for available ports on devices."""
        try:
            if not self.scene:
                return
                
            # Clear existing indicators
            self.clear_port_indicators()
            
            # Find all devices in the scene
            for item in self.scene.items():
                if isinstance(item, Device) and item != self.source_device:
                    # Add indicators for all unconnected ports
                    for port in item.ports:
                        if not port.get("connected", False):
                            # Get port position
                            pos = item.get_port_position(port["name"])
                            
                            # Create indicator
                            indicator = QGraphicsEllipseItem(pos.x()-4, pos.y()-4, 8, 8)
                            indicator.setPen(QPen(Qt.black, 1))
                            indicator.setBrush(QColor(100, 200, 100, 150))
                            indicator.setZValue(1000)  # Keep above other items
                            
                            # Add to scene
                            self.scene.addItem(indicator)
                            self.port_indicators.append(indicator)
                    
        except Exception as e:
            print(f"Error showing port indicators: {e}")
    
    def clear_port_indicators(self):
        """Remove all port indicators."""
        try:
            if self.scene:
                for indicator in self.port_indicators:
                    if indicator.scene() == self.scene:
                        self.scene.removeItem(indicator)
            self.port_indicators = []
            
        except Exception as e:
            print(f"Error clearing port indicators: {e}")