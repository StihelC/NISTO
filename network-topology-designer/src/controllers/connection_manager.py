from PyQt5.QtCore import QObject, QPointF, Qt, pyqtSignal
from PyQt5.QtGui import QPen, QColor, QPainterPath, QBrush
from utils.path_routers import OrthogonalRouter, ManhattanRouter
import math
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsLineItem, QGraphicsEllipseItem
from PyQt5.QtCore import Qt, QPointF
from models.connection import Connection
from models.device import Device
import uuid

class Connection(QGraphicsPathItem):
    """A connection between two devices."""
    
    def __init__(self, source_device, source_port, target_device, target_port, connection_type="standard"):
        """Initialize a connection between two devices."""
        super().__init__()
        
        # Generate a unique ID
        self.id = str(uuid.uuid4())[:8]
        
        # Store connection details
        self.source_device = source_device
        self.source_port = source_port
        self.target_device = target_device
        self.target_port = target_port
        self.connection_type = connection_type
        
        # Set appearance
        self.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))
        self.setZValue(-1)  # Draw behind devices
        
        # Draw the connection
        self.update_path()
        
        # Connect to device signals
        self.source_device.position_changed.connect(self.update_path)
        self.target_device.position_changed.connect(self.update_path)
        
    def update_path(self):
        """Update the connection path based on device positions."""
        try:
            # Get port positions
            source_pos = self.source_device.get_port_position(self.source_port['name'])
            target_pos = self.target_device.get_port_position(self.target_port['name'])
            
            # Create a curved path between ports
            path = QPainterPath()
            path.moveTo(source_pos)
            
            # Calculate control points for curve
            # Midpoint between devices
            mid_x = (source_pos.x() + target_pos.x()) / 2
            mid_y = (source_pos.y() + target_pos.y()) / 2
            
            # Distance between points
            dx = target_pos.x() - source_pos.x()
            dy = target_pos.y() - source_pos.y()
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Create curved path with more pronounced curve for longer distances
            curve_factor = min(50, distance / 4)
            
            # Calculate normal vector to the line
            if abs(dx) < 1 and abs(dy) < 1:
                # Points are too close, use a simple line
                path.lineTo(target_pos)
            else:
                # Normalize the direction vector
                length = math.sqrt(dx*dx + dy*dy)
                nx = -dy / length
                ny = dx / length
                
                # Control points perpendicular to the line
                ctrl1 = QPointF(source_pos.x() + dx/3 + nx*curve_factor,
                              source_pos.y() + dy/3 + ny*curve_factor)
                ctrl2 = QPointF(source_pos.x() + 2*dx/3 + nx*curve_factor,
                              source_pos.y() + 2*dy/3 + ny*curve_factor)
                
                path.cubicTo(ctrl1, ctrl2, target_pos)
            
            # Set the path
            self.setPath(path)
            
        except Exception as e:
            print(f"Error updating connection path: {e}")
            import traceback
            traceback.print_exc()
    
    def cleanup(self):
        """Disconnect signals to prevent memory leaks."""
        try:
            # Disconnect from device signals
            if self.source_device:
                self.source_device.position_changed.disconnect(self.update_path)
            if self.target_device:
                self.target_device.position_changed.disconnect(self.update_path)
        except Exception as e:
            print(f"Error cleaning up connection: {e}")
    
    def to_dict(self):
        """Convert connection to dictionary for serialization."""
        return {
            'id': self.id,
            'source_device_id': self.source_device.id,
            'source_port_name': self.source_port['name'],
            'target_device_id': self.target_device.id,
            'target_port_name': self.target_port['name'],
            'connection_type': self.connection_type
        }
    
    @classmethod
    def from_dict(cls, data, device_manager):
        """Create connection from dictionary (deserialization)."""
        # Get devices from device manager
        source_device = device_manager.get_device_by_id(data['source_device_id'])
        target_device = device_manager.get_device_by_id(data['target_device_id'])
        
        if not source_device or not target_device:
            print(f"Error creating connection: device not found")
            return None
        
        # Find ports
        source_port = next((p for p in source_device.ports if p['name'] == data['source_port_name']), None)
        target_port = next((p for p in target_device.ports if p['name'] == data['target_port_name']), None)
        
        if not source_port or not target_port:
            print(f"Error creating connection: port not found")
            return None
        
        # Create connection
        return cls(source_device, source_port, target_device, target_port, data.get('connection_type', 'standard'))


class ConnectionItem(QGraphicsPathItem):
    """A connection between two network devices."""
    
    def __init__(self, source_device, target_device, source_port=None, target_port=None):
        """Initialize a connection between two devices."""
        super().__init__()
        
        # Store device references
        self.source_device = source_device
        self.target_device = target_device
        self.source_port = source_port
        self.target_port = target_port
        
        # Connection properties
        self.connection_type = "ethernet"
        self.properties = {
            'bandwidth': '1 Gbps',
            'latency': '5 ms',
            'status': 'active',
            'description': ''
        }
        
        # Set appearance
        self.setZValue(-1)  # Ensure connections are below devices
        self.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        
        # Set flags
        self.setFlag(QGraphicsPathItem.ItemIsSelectable)
        
        # Create the path
        self.update_path()
    
    def update_path(self):
        """Update the connection path based on device positions."""
        if not self.source_device or not self.target_device:
            return
        
        # Get connection points
        if self.source_port:
            source_point = self.source_device.get_port_position(self.source_port['name'])
        else:
            source_point = self.source_device.mapToScene(
                QPointF(self.source_device.width / 2, self.source_device.height / 2)
            )
        
        if self.target_port:
            target_point = self.target_device.get_port_position(self.target_port['name'])
        else:
            target_point = self.target_device.mapToScene(
                QPointF(self.target_device.width / 2, self.target_device.height / 2)
            )
        
        # Create path
        path = QPainterPath()
        path.moveTo(source_point)
        
        # Determine if we need to create a curved path
        # For simplicity, let's create a slight curve for all connections
        # In a more advanced implementation, we could detect crossing connections and adjust
        
        # Calculate control points for a Bezier curve
        dx = target_point.x() - source_point.x()
        dy = target_point.y() - source_point.y()
        distance = (dx * dx + dy * dy) ** 0.5
        
        # Control point offsets (adjust these to change curve shape)
        offset_factor = min(40, distance * 0.25)
        
        if abs(dx) > abs(dy):
            # More horizontal than vertical
            ctrl1 = QPointF(source_point.x() + offset_factor, source_point.y())
            ctrl2 = QPointF(target_point.x() - offset_factor, target_point.y())
        else:
            # More vertical than horizontal
            ctrl1 = QPointF(source_point.x(), source_point.y() + offset_factor)
            ctrl2 = QPointF(target_point.x(), target_point.y() - offset_factor)
        
        # Create cubic Bezier curve
        path.cubicTo(ctrl1, ctrl2, target_point)
        
        # Set path
        self.setPath(path)
        
        # Update appearance based on connection type
        self.update_appearance()
    
    def update_appearance(self):
        """Update the connection appearance based on its type and properties."""
        # Default appearance
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        
        # Customize based on connection type
        if self.connection_type == "ethernet":
            pen.setColor(QColor(0, 0, 200))  # Blue
        elif self.connection_type == "fiber":
            pen.setColor(QColor(200, 100, 0))  # Orange
            pen.setWidth(3)
        elif self.connection_type == "wireless":
            pen.setColor(QColor(0, 150, 0))  # Green
            pen.setStyle(Qt.DashLine)
        elif self.connection_type == "wan":
            pen.setColor(QColor(150, 0, 150))  # Purple
            pen.setWidth(3)
        
        # Apply status changes
        if self.properties.get('status') == 'inactive':
            pen.setColor(QColor(150, 150, 150))  # Gray out for inactive
        elif self.properties.get('status') == 'error':
            pen.setColor(QColor(255, 0, 0))  # Red for error
        
        # Apply the pen
        self.setPen(pen)


class ConnectionManager(QObject):
    """Manages connections between devices in the network topology."""
    
    # Signals
    connection_created = pyqtSignal(object)
    connection_removed = pyqtSignal(object)
    connection_selected = pyqtSignal(object)
    connection_deselected = pyqtSignal(object)
    
    def __init__(self, scene=None):
        """Initialize the connection manager."""
        super().__init__()
        self.scene = scene
        self.connections = {}  # Dictionary of connections by ID
        self.selected_connection = None
    
    def register_connection(self, connection):
        """Register a connection with the manager."""
        if not isinstance(connection, ConnectionItem):
            print("Error: Connection must be a ConnectionItem instance")
            return False
        
        # Add to dictionary
        self.connections[connection.id] = connection
        
        # Emit signal
        self.connection_created.emit(connection)
        
        print(f"Connection registered: {connection.id}")
        return True
    
    def create_connection(self, source_device, source_port, target_device, target_port, connection_type="ethernet"):
        """Create a new connection between devices."""
        try:
            # Create connection item
            connection = ConnectionItem(
                source_device,
                source_port,
                target_device,
                target_port,
                connection_type
            )
            
            # Add to scene
            if self.scene:
                self.scene.addItem(connection)
            
            # Mark ports as connected
            source_port["connected"] = True
            target_port["connected"] = True
            
            # Add connection to devices
            if hasattr(source_device, "add_connection"):
                source_device.add_connection(connection)
            if hasattr(target_device, "add_connection"):
                target_device.add_connection(connection)
            
            # Register with manager
            self.register_connection(connection)
            
            return connection
        
        except Exception as e:
            print(f"Error creating connection: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def remove_connection(self, connection_id):
        """Remove a connection by ID."""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            
            # Mark ports as disconnected
            if connection.source_port:
                connection.source_port["connected"] = False
            if connection.target_port:
                connection.target_port["connected"] = False
            
            # Remove from devices
            if hasattr(connection.source_device, "remove_connection"):
                connection.source_device.remove_connection(connection)
            if hasattr(connection.target_device, "remove_connection"):
                connection.target_device.remove_connection(connection)
            
            # Disconnect signals
            connection.cleanup()
            
            # Remove from scene
            if self.scene and connection.scene() == self.scene:
                self.scene.removeItem(connection)
            
            # Remove from dictionary
            del self.connections[connection_id]
            
            # Reset selected connection if needed
            if self.selected_connection == connection:
                self.selected_connection = None
            
            # Emit signal
            self.connection_removed.emit(connection)
            
            print(f"Connection removed: {connection_id}")
            return True
        
        return False
    
    def remove_device_connections(self, device):
        """Remove all connections for a device."""
        connection_ids = []
        
        # Find all connections for this device
        for connection_id, connection in self.connections.items():
            if connection.source_device == device or connection.target_device == device:
                connection_ids.append(connection_id)
        
        # Remove each connection
        for connection_id in connection_ids:
            self.remove_connection(connection_id)
        
        return len(connection_ids)
    
    def select_connection(self, connection):
        """Select a connection."""
        if connection not in self.connections.values():
            return False
        
        # Deselect current selection if any
        if self.selected_connection and self.selected_connection != connection:
            old_selected = self.selected_connection
            self.selected_connection = None
            self.connection_deselected.emit(old_selected)
        
        # Update selection
        self.selected_connection = connection
        
        # Emit signal
        self.connection_selected.emit(connection)
        
        return True
    
    def deselect_connection(self):
        """Deselect the currently selected connection."""
        if self.selected_connection:
            old_selected = self.selected_connection
            self.selected_connection = None
            self.connection_deselected.emit(old_selected)
            return True
        
        return False
    
    def get_connection_by_id(self, connection_id):
        """Get a connection by ID."""
        return self.connections.get(connection_id)
    
    def get_connections_for_device(self, device):
        """Get all connections for a device."""
        return [conn for conn in self.connections.values() 
                if conn.source_device == device or conn.target_device == device]
    
    def to_dict(self):
        """Convert all connections to dictionary for serialization."""
        connections_data = []
        
        for connection in self.connections.values():
            # Only include valid connections
            if connection.source_device and connection.target_device:
                connections_data.append({
                    "id": connection.id,
                    "source_device_id": connection.source_device.id,
                    "source_port_name": connection.source_port["name"],
                    "target_device_id": connection.target_device.id,
                    "target_port_name": connection.target_port["name"],
                    "connection_type": connection.connection_type
                })
        
        return connections_data
    
    def from_dict(self, connections_data, device_manager):
        """Create connections from dictionary (deserialization)."""
        for conn_data in connections_data:
            try:
                # Get devices
                source_device = device_manager.get_device_by_id(conn_data["source_device_id"])
                target_device = device_manager.get_device_by_id(conn_data["target_device_id"])
                
                if not source_device or not target_device:
                    print(f"Cannot create connection: Device not found")
                    continue
                
                # Find ports
                source_port = next((p for p in source_device.ports 
                                   if p["name"] == conn_data["source_port_name"]), None)
                                   
                target_port = next((p for p in target_device.ports 
                                   if p["name"] == conn_data["target_port_name"]), None)
                
                if not source_port or not target_port:
                    print(f"Cannot create connection: Port not found")
                    continue
                
                # Create connection
                connection_type = conn_data.get("connection_type", "ethernet")
                connection = self.create_connection(
                    source_device,
                    source_port,
                    target_device,
                    target_port,
                    connection_type
                )
                
                # Set ID if provided
                if connection and "id" in conn_data:
                    connection.id = conn_data["id"]
                    
            except Exception as e:
                print(f"Error creating connection from data: {e}")
                import traceback
                traceback.print_exc()
    
    def clear_all_connections(self):
        """Remove all connections."""
        connection_ids = list(self.connections.keys())
        
        for connection_id in connection_ids:
            self.remove_connection(connection_id)
        
        return len(connection_ids)
    
    def handle_mouse_press(self, event):
        """Handle mouse press for connection creation."""
        try:
            # Get scene position
            pos = event.scenePos()
            
            # Get item at position
            if self.scene:
                item = self.scene.itemAt(pos, self.scene.views()[0].transform())
                
                # Check if we clicked on a Device
                if isinstance(item, Device):
                    # If we already have a source device, check if it's different
                    if self.source_device and self.source_device != item:
                        # Complete connection between source and target
                        self.create_connection(self.source_device, item)
                        
                        # Reset state
                        self.clear_temp_connection()
                        
                    else:
                        # Start new connection from this device
                        self.source_device = item
                        
                        # Find closest port
                        self.source_port, _ = item.get_closest_port(pos)
                        if not self.source_port:
                            print("No suitable port found on source device")
                            return
                        
                        # Get port position
                        source_port_pos = item.get_port_position(self.source_port['name'])
                        
                        # Create temporary line
                        self.temp_line = QGraphicsLineItem(source_port_pos.x(), source_port_pos.y(), 
                                                         pos.x(), pos.y())
                        self.temp_line.setPen(QPen(QColor(0, 100, 200), 2, Qt.DashLine))
                        self.scene.addItem(self.temp_line)
                        
                        # Show port indicators on all devices to help with targeting
                        self.show_port_indicators()
                        
                        print(f"Starting connection from {item.name}, port {self.source_port['name']}")
                
        except Exception as e:
            print(f"Error in connection mouse press: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_mouse_move(self, event):
        """Update temporary connection line during move."""
        try:
            if self.source_device and self.temp_line and self.source_port:
                # Get current mouse position
                pos = event.scenePos()
                
                # Get port position
                source_port_pos = self.source_device.get_port_position(self.source_port['name'])
                
                # Update line
                self.temp_line.setLine(source_port_pos.x(), source_port_pos.y(), pos.x(), pos.y())
                
        except Exception as e:
            print(f"Error in connection mouse move: {e}")
    
    def handle_mouse_release(self, event):
        """Complete connection on mouse release."""
        try:
            if self.source_device and self.temp_line:
                pos = event.scenePos()
                
                # Get item at release position
                if self.scene:
                    item = self.scene.itemAt(pos, self.scene.views()[0].transform())
                    
                    # Check if released on a different device
                    if isinstance(item, Device) and item != self.source_device:
                        # Create connection between devices
                        self.create_connection(self.source_device, item)
                    
                    # Clean up
                    self.clear_temp_connection()
                    
        except Exception as e:
            print(f"Error in connection mouse release: {e}")
            import traceback
            traceback.print_exc()
    
    def create_connection(self, source_device, target_device):
        """Create a connection between two devices."""
        try:
            if not isinstance(source_device, Device) or not isinstance(target_device, Device):
                print("Both items must be devices to create a connection")
                return None
            
            # Don't connect a device to itself
            if source_device == target_device:
                print("Cannot connect a device to itself")
                return None
            
            # Get source port (should already be set from mouse press)
            source_port = self.source_port
            
            # Find a suitable port on the target device
            target_pos = target_device.scenePos()
            target_port, _ = target_device.get_closest_port(target_pos)
            
            if not source_port or not target_port:
                print("Failed to find suitable ports for connection")
                return None
            
            # Mark ports as connected
            source_port['connected'] = True
            target_port['connected'] = True
            
            # Create connection
            connection = Connection(source_device, source_port, target_device, target_port)
            
            # Add to scene
            if self.scene:
                self.scene.addItem(connection)
                
            # Store connection
            self.connections[connection.id] = connection
            
            # Update devices
            source_device.add_connection(connection)
            target_device.add_connection(connection)
            
            # Emit signal
            self.connection_created.emit(connection)
            
            print(f"Created connection between {source_device.name}:{source_port['name']} and {target_device.name}:{target_port['name']}")
            
            return connection
            
        except Exception as e:
            print(f"Error creating connection: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def remove_connection(self, connection_id):
        """Remove a connection by ID."""
        try:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                
                # Mark ports as disconnected
                if connection.source_port:
                    connection.source_port['connected'] = False
                
                if connection.target_port:
                    connection.target_port['connected'] = False
                
                # Update devices
                if connection.source_device:
                    connection.source_device.remove_connection(connection)
                
                if connection.target_device:
                    connection.target_device.remove_connection(connection)
                
                # Remove from scene
                if self.scene:
                    self.scene.removeItem(connection)
                
                # Clean up the connection
                connection.cleanup()
                
                # Remove from dictionary
                del self.connections[connection_id]
                
                # Emit signal
                self.connection_removed.emit(connection)
                
                print(f"Removed connection: {connection_id}")
                return True
            
            print(f"Connection not found: {connection_id}")
            return False
            
        except Exception as e:
            print(f"Error removing connection: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def clear_temp_connection(self):
        """Clear temporary connection elements."""
        try:
            # Remove temporary line
            if self.temp_line and self.scene:
                self.scene.removeItem(self.temp_line)
                self.temp_line = None
            
            # Clear source device/port
            self.source_device = None
            self.source_port = None
            
            # Remove port indicators
            self.clear_port_indicators()
            
        except Exception as e:
            print(f"Error clearing temporary connection: {e}")
    
    def show_port_indicators(self):
        """Show visual indicators for all device ports."""
        try:
            if not self.scene:
                return
                
            # Remove any existing indicators
            self.clear_port_indicators()
            
            # Create indicators for all devices in the scene
            for item in self.scene.items():
                if isinstance(item, Device):
                    # Don't show indicators for the source device
                    if item == self.source_device:
                        continue
                        
                    # Add indicators for each port
                    for port in item.ports:
                        if not port.get('connected', False):  # Only show unconnected ports
                            pos = item.get_port_position(port['name'])
                            indicator = QGraphicsEllipseItem(pos.x() - 4, pos.y() - 4, 8, 8)
                            indicator.setPen(QPen(Qt.black, 1))
                            indicator.setBrush(QBrush(QColor(100, 200, 100)))
                            self.scene.addItem(indicator)
                            self.port_indicators.append(indicator)
                            
        except Exception as e:
            print(f"Error showing port indicators: {e}")
    
    def clear_port_indicators(self):
        """Remove all port indicators."""
        try:
            if self.scene:
                for indicator in self.port_indicators:
                    self.scene.removeItem(indicator)
            self.port_indicators = []
            
        except Exception as e:
            print(f"Error clearing port indicators: {e}")
    
    def get_connections_for_device(self, device_id):
        """Get all connections for a specific device."""
        return [c for c in self.connections.values() 
                if (c.source_device and c.source_device.id == device_id) or 
                   (c.target_device and c.target_device.id == device_id)]
    
    def can_connect(self, source_item, target_item):
        """Check if two items can be connected."""
        # Only connect Device instances
        if not isinstance(source_item, Device) or not isinstance(target_item, Device):
            return False
        
        # Don't connect to self
        if source_item == target_item:
            return False
            
        return True
    
    def handle_mouse_press(self, event):
        """Handle mouse press for connection creation."""
        try:
            pos = event.scenePos()
            item = self.scene.itemAt(pos, self.scene.views()[0].transform())
            
            # Check if clicked on a device
            if isinstance(item, Device):
                # Start connection from this device
                self.source_device = item
                
                # Get closest port
                port, _ = item.get_closest_port(pos)
                port_pos = item.get_port_position(port['name'])
                
                # Create temporary line for visual feedback
                self.temp_line = QGraphicsLineItem(port_pos.x(), port_pos.y(), pos.x(), pos.y())
                self.temp_line.setPen(QPen(QColor(0, 0, 200, 200), 2))
                self.scene.addItem(self.temp_line)
                
                print(f"Starting connection from {item.name}, port {port['name']}")
            
        except Exception as e:
            print(f"Error in connection mouse press: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_mouse_move(self, event):
        """Handle mouse move for connection creation."""
        if self.source_device and self.temp_line:
            try:
                # Update temporary line endpoint
                pos = event.scenePos()
                line = self.temp_line.line()
                self.temp_line.setLine(line.x1(), line.y1(), pos.x(), pos.y())
            except Exception as e:
                print(f"Error in connection mouse move: {e}")
    
    def handle_mouse_release(self, event):
        """Handle mouse release for connection creation."""
        if self.source_device:
            try:
                pos = event.scenePos()
                item = self.scene.itemAt(pos, self.scene.views()[0].transform())
                
                # Check if released on a device
                if isinstance(item, Device) and item != self.source_device:
                    # Create connection between devices
                    self.create_connection(self.source_device, item)
                
                # Clean up
                if self.temp_line:
                    self.scene.removeItem(self.temp_line)
                    self.temp_line = None
                
                self.source_device = None
                
            except Exception as e:
                print(f"Error in connection mouse release: {e}")
                import traceback
                traceback.print_exc()
                
                # Clean up on error
                if self.temp_line:
                    self.scene.removeItem(self.temp_line)
                    self.temp_line = None
                self.source_device = None
    
    def create_connection(self, source_device, target_device, conn_type="standard"):
        """Create a connection between devices."""
        try:
            # Create connection model
            connection = Connection(source_device, target_device, conn_type)
            
            # Add to collection
            self.connections[connection.id] = connection
            
            # Create view if we have a scene
            if self.scene:
                from views.connection_view import ConnectionView
                conn_view = ConnectionView(connection)
                self.scene.addItem(conn_view)
                connection.view = conn_view
                print(f"Created connection between {source_device.name} and {target_device.name}")
            
            # Emit signal
            self.connection_added.emit(connection)
            
            return connection
        except Exception as e:
            import traceback
            print(f"Error creating connection: {e}")
            traceback.print_exc()
            return None
    
    def remove_connection(self, connection_id):
        """Remove a connection by ID."""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            
            # Remove from scene
            if connection.view and self.scene:
                self.scene.removeItem(connection.view)
            
            # Remove from devices
            if connection.source_device:
                connection.source_device.remove_connection(connection)
            if connection.target_device:
                connection.target_device.remove_connection(connection)
            
            # Remove from collection
            del self.connections[connection_id]
            
            # Emit signal
            self.connection_removed.emit(connection_id)
            
            return True
        return False
    
    def remove_device_connections(self, device):
        """Remove all connections for a device."""
        # Create a copy of the list to avoid modification during iteration
        connections_to_remove = [c for c in self.connections.values() 
                               if c.source_device == device or c.target_device == device]
        
        for connection in connections_to_remove:
            self.remove_connection(connection.id)
    
    def add_connection(self, connection):
        """Add a connection to the manager."""
        if connection not in self.connections:
            self.connections.append(connection)
        return connection
    
    def start_connection(self, device, port=None):
        """Start a new connection from the source device and port."""
        self.source_device = device
        self.source_port = port
        self.connection_mode = "connecting"
        port_text = f" port {port}" if port else ""
        print(f"Starting connection from {device.properties['name']}{port_text}")
        
    def finish_connection(self, device):
        """Complete a connection to the target device."""
        if self.source_device and self.connection_mode == "connecting":
            # Find the closest port on the target device
            scene_pos = None
            for item in self.scene.items():
                if hasattr(item, 'temp_line_end'):
                    scene_pos = item.temp_line_end
                    break
                    
            if not scene_pos:
                # Fallback to center if no position found
                scene_pos = device.sceneBoundingRect().center()
                
            target_port, _ = device.get_closest_port(scene_pos)
            
            # Create the connection
            connection = self.create_connection(
                self.source_device, device, "ethernet", 
                self.source_port, target_port
            )
            
            self.source_device = None
            self.source_port = None
            self.connection_mode = None
            return connection
        return None
    
    def cancel_connection(self):
        """Cancel the current connection being created."""
        self.source_device = None
        self.source_port = None
        print("Connection creation canceled")
    
    def update_all_connections(self):
        """Update all connections (useful after device moves)."""
        for connection in self.connections:
            connection.update_path()
    
    def update_connections(self):
        """Update all connection paths."""
        for connection in self.connections:
            if hasattr(connection, 'update_path'):
                connection.update_path()
    
    def get_device_connections(self, device):
        """Get all connections associated with a device."""
        return [conn for conn in self.connections 
                if conn.source_device == device or conn.target_device == device]
    
    def clear_all_connections(self):
        """Remove all connections from the scene."""
        for connection in list(self.connections):
            self.remove_connection(connection)
            
    def get_advanced_path(self, source_device, target_device):
        """Calculate an aesthetically pleasing path between devices."""
        # Get device bounding rectangles
        source_rect = source_device.sceneBoundingRect()
        target_rect = target_device.sceneBoundingRect()
        
        # Get centers
        source_center = source_rect.center()
        target_center = target_rect.center()
        
        # Calculate a path with potential control points for curves
        path = []
        
        # Basic A* or path finding algorithm could be implemented here
        # For now, we'll do a simple direct path
        path.append(source_center)
        path.append(target_center)
        
        return path
    
    def auto_route_connections(self):
        """Re-route all connections for optimal layout."""
        # This would implement more sophisticated routing algorithms
        # For example, using force-directed layout for the connections
        # or implementing crossing-reduction algorithms
        
        # For now, just update existing paths
        self.update_all_connections()
        print("Auto-routing connections")
    
    def set_router_type(self, router_type):
        """Change the routing strategy for new connections."""
        if router_type == "orthogonal":
            self.router = OrthogonalRouter()
        elif router_type == "manhattan":
            self.router = ManhattanRouter()
        else:
            print(f"Unknown router type: {router_type}")
    
    def _create_ports(self):
        """Create ports around the device."""
        from PyQt5.QtWidgets import QGraphicsEllipseItem
        from PyQt5.QtGui import QBrush, QColor, QPen
        from PyQt5.QtCore import Qt, QRectF
        
        port_size = 8
        self.ports = {}
        
        # Number of ports per side
        num_ports_per_side = 2  # Adjust as needed
        
        # Create top ports
        for i in range(num_ports_per_side):
            port_id = f"top_{i}"
            spacing = self.size / (num_ports_per_side + 1)
            x_pos = spacing * (i + 1) - port_size/2
            y_pos = -port_size
            
            port_rect = QRectF(x_pos, y_pos, port_size, port_size)
            port = QGraphicsEllipseItem(port_rect, self)
            port.setBrush(QBrush(QColor(200, 200, 200)))
            port.setPen(QPen(Qt.black, 1))
            port.setVisible(False)  # Initially hidden
            
            self.ports[port_id] = port
        
        # Create bottom, left, right ports similarly...
    
    def can_connect(self, source_item, target_item):
        """Check if two items can be connected."""
        # Only connect Device instances
        if not isinstance(source_item, Device) or not isinstance(target_item, Device):
            return False
        
        # Don't connect to self
        if source_item == target_item:
            return False
            
        return True