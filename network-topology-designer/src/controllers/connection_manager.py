from PyQt5.QtCore import QObject, QPointF, Qt
from PyQt5.QtGui import QPen, QColor, QPainterPath, QBrush
from utils.path_routers import OrthogonalRouter, ManhattanRouter
import math
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtCore import Qt, QPointF

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
    """Manages network connections between devices."""
    
    def __init__(self, scene):
        """Initialize with a scene to manage connections in."""
        super().__init__()
        self.scene = scene
        self.connections = []
        self.router = OrthogonalRouter()  # Default router
    
    def add_connection(self, connection):
        """Add a connection to the manager."""
        if connection not in self.connections:
            self.connections.append(connection)
        return connection
    
    def create_connection(self, source_device, target_device, connection_type="ethernet", 
                         source_port=None, target_port=None):
        """Create a new connection between devices."""
        try:
            # Prevent connection to self
            if source_device is target_device:
                print("Cannot connect a device to itself")
                return None
            
            # Create connection using the ConnectionItem class defined in this file
            
            # Create connection using the ConnectionItem class
            connection = ConnectionItem(
                source_device, target_device, source_port, target_port
            )
            connection.connection_type = connection_type
            
            # Add to our list
            if not hasattr(self, 'connections'):
                self.connections = []
            self.connections.append(connection)
            
            # Force update
            self.scene.update()
            
            print(f"Created connection: {connection_type} from "
                  f"{source_device.properties.get('name', 'unnamed')} "
                  f"(port {source_port or 'center'}) to "
                  f"{target_device.properties.get('name', 'unnamed')} "
                  f"(port {target_port or 'center'})")
            
            return connection
        except Exception as e:
            print(f"Error creating connection: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def remove_connection(self, connection):
        """Remove a connection."""
        if connection in self.connections:
            self.connections.remove(connection)
            self.scene.removeItem(connection)
    
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