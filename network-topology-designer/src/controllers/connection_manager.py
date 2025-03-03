from PyQt5.QtCore import QObject, QPointF, Qt
from PyQt5.QtGui import QPen, QColor
from models.connection import NetworkConnection  # Change to absolute
import math

class ConnectionManager(QObject):
    """Manages connections between network devices."""
    
    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.connections = []
        self.connection_mode = None
        self.source_device = None  # For creating new connections
        self.source_port = None    # For tracking selected port
        
    def create_connection(self, source_device, target_device, connection_type="ethernet",
                         source_port=None, target_port=None):
        """Create a new connection between devices with specific ports."""
        try:
            # Make sure we're not connecting a device to itself
            if source_device is target_device:
                print("Cannot connect device to itself")
                return None
                
            # Check if this connection already exists
            for conn in self.connections:
                if ((conn.source_device is source_device and conn.target_device is target_device and
                     conn.source_port == source_port and conn.target_port == target_port) or
                    (conn.source_device is target_device and conn.target_device is source_device and
                     conn.source_port == target_port and conn.target_port == source_port)):
                    print("Connection already exists")
                    return conn
            
            # Create the new connection
            connection = NetworkConnection(source_device, target_device, connection_type, 
                                         source_port, target_port)
            
            # Add to scene
            self.scene.addItem(connection)
            
            # Track the connection
            self.connections.append(connection)
            
            # Update the path
            connection.update_path()
            
            # Update port connection tracking in devices
            if source_port:
                source_device.add_connection_to_port(source_port, connection)
                
            if target_port:
                target_device.add_connection_to_port(target_port, connection)
            
            print(f"Created connection between {source_device.properties['name']} ({source_port}) "
                  f"and {target_device.properties['name']} ({target_port})")
            return connection
        except Exception as e:
            print(f"Error creating connection: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def remove_connection(self, connection):
        """Remove a connection from the scene."""
        if connection in self.connections:
            self.scene.removeItem(connection)
            self.connections.remove(connection)
            return True
        return False
    
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
        self.connection_mode = None
        print("Connection creation canceled")
    
    def update_all_connections(self):
        """Update all connections (useful after device moves)."""
        for connection in self.connections:
            connection.update_path()
            
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