import json
import os
from PyQt5.QtCore import QObject, pyqtSignal, QPointF, QRectF
from PyQt5.QtGui import QColor
import traceback

class FileHandler(QObject):
    """Handles file operations for the topology designer."""
    
    # Signals
    file_saved = pyqtSignal(str)
    file_loaded = pyqtSignal(str)
    file_error = pyqtSignal(str)
    
    def __init__(self, device_manager=None, connection_manager=None, boundary_controller=None):
        super().__init__()
        self.device_manager = device_manager
        self.connection_manager = connection_manager
        self.boundary_controller = boundary_controller
        self.current_file = None
    
    def save_topology(self, filepath=None):
        """Save the current topology to a file."""
        try:
            if not filepath:
                filepath = self.current_file
                
            if not filepath:
                self.file_error.emit("No file path specified")
                return False
            
            # Create data structure
            topology_data = {
                "version": "1.0",
                "devices": self._export_devices(),
                "connections": self._export_connections(),
                "boundaries": self._export_boundaries()
            }
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(topology_data, f, indent=2)
                
            self.current_file = filepath
            self.file_saved.emit(filepath)
            print(f"Topology saved to {filepath}")
            return True
            
        except Exception as e:
            error_msg = f"Error saving topology: {str(e)}"
            self.file_error.emit(error_msg)
            print(error_msg)
            traceback.print_exc()
            return False
    
    def load_topology(self, filepath):
        """Load a topology from a file."""
        try:
            if not os.path.exists(filepath):
                self.file_error.emit(f"File not found: {filepath}")
                return False
            
            # Read from file
            with open(filepath, 'r') as f:
                topology_data = json.load(f)
            
            # Check version if needed
            file_version = topology_data.get("version", "unknown")
            
            # Clear existing topology
            self._clear_current_topology()
            
            # Import topology data
            self._import_devices(topology_data.get("devices", []))
            self._import_connections(topology_data.get("connections", []))
            self._import_boundaries(topology_data.get("boundaries", []))
            
            self.current_file = filepath
            self.file_loaded.emit(filepath)
            print(f"Topology loaded from {filepath}")
            return True
            
        except Exception as e:
            error_msg = f"Error loading topology: {str(e)}"
            self.file_error.emit(error_msg)
            print(error_msg)
            traceback.print_exc()
            return False
    
    def _export_devices(self):
        """Export devices to serializable format."""
        devices_data = []
        
        if self.device_manager:
            for device in self.device_manager.devices.values():
                # Use the device's to_dict method if available
                if hasattr(device, "to_dict") and callable(device.to_dict):
                    device_data = device.to_dict()
                else:
                    # Manual serialization as fallback
                    device_data = {
                        "id": device.id,
                        "type": device.device_type,
                        "name": device.name,
                        "x": device.scenePos().x(),
                        "y": device.scenePos().y(),
                        "properties": getattr(device, "properties", {})
                    }
                
                devices_data.append(device_data)
        
        return devices_data
    
    def _export_connections(self):
        """Export connections to serializable format."""
        connections_data = []
        
        if self.connection_manager:
            # Use the connection manager's to_dict method if available
            if hasattr(self.connection_manager, "to_dict") and callable(self.connection_manager.to_dict):
                return self.connection_manager.to_dict()
            
            # Manual serialization as fallback
            for connection in self.connection_manager.connections.values():
                if (not hasattr(connection, "source_device") or 
                    not hasattr(connection, "target_device")):
                    continue
                    
                # Skip invalid connections
                if not connection.source_device or not connection.target_device:
                    continue
                    
                connection_data = {
                    "id": connection.id,
                    "source_device_id": connection.source_device.id,
                    "source_port_name": connection.source_port["name"],
                    "target_device_id": connection.target_device.id,
                    "target_port_name": connection.target_port["name"],
                    "connection_type": getattr(connection, "connection_type", "ethernet")
                }
                
                connections_data.append(connection_data)
        
        return connections_data
    
    def _export_boundaries(self):
        """Export boundaries to serializable format."""
        boundaries_data = []
        
        if self.boundary_controller and hasattr(self.boundary_controller, "boundaries"):
            for boundary in self.boundary_controller.boundaries.values():
                # Use boundary's to_dict method if available
                if hasattr(boundary, "to_dict") and callable(boundary.to_dict):
                    boundary_data = boundary.to_dict()
                else:
                    # Manual serialization as fallback
                    rect = boundary.rect if hasattr(boundary, "rect") else boundary.boundingRect()
                    color = boundary.color if hasattr(boundary, "color") else QColor(200, 200, 255, 100)
                    
                    boundary_data = {
                        "id": getattr(boundary, "id", str(id(boundary))),
                        "name": getattr(boundary, "name", "Boundary"),
                        "type": getattr(boundary, "boundary_type", "area"),
                        "x": rect.x(),
                        "y": rect.y(),
                        "width": rect.width(),
                        "height": rect.height(),
                        "color": {
                            "r": color.red(),
                            "g": color.green(),
                            "b": color.blue(),
                            "a": color.alpha()
                        }
                    }
                
                boundaries_data.append(boundary_data)
        
        return boundaries_data
    
    def _clear_current_topology(self):
        """Clear the current topology."""
        if self.connection_manager:
            if hasattr(self.connection_manager, "clear_all_connections"):
                self.connection_manager.clear_all_connections()
            else:
                # Fallback method
                connection_ids = list(getattr(self.connection_manager, "connections", {}).keys())
                for connection_id in connection_ids:
                    self.connection_manager.remove_connection(connection_id)
        
        if self.device_manager:
            # Remove all devices
            device_ids = list(getattr(self.device_manager, "devices", {}).keys())
            for device_id in device_ids:
                self.device_manager.remove_device(device_id)
        
        if self.boundary_controller and hasattr(self.boundary_controller, "boundaries"):
            # Clear boundaries
            boundary_ids = list(self.boundary_controller.boundaries.keys())
            for boundary_id in boundary_ids:
                # Remove from scene
                boundary = self.boundary_controller.boundaries[boundary_id]
                if self.boundary_controller.scene:
                    self.boundary_controller.scene.removeItem(boundary)
            
            self.boundary_controller.boundaries = {}
    
    def _import_devices(self, devices_data):
        """Import devices from serialized data."""
        if not self.device_manager:
            print("No device manager available for importing devices")
            return
        
        try:
            from models.device import Device
            
            for device_data in devices_data:
                # Check if Device class has a from_dict method
                if hasattr(Device, "from_dict") and callable(Device.from_dict):
                    # Create device using from_dict class method
                    device = Device.from_dict(device_data)
                    
                    # Add to scene & manager
                    if device and self.device_manager.scene:
                        self.device_manager.scene.addItem(device)
                        self.device_manager.devices[device.id] = device
                else:
                    # Create device manually
                    device_id = device_data.get("id")
                    device_type = device_data.get("type", "generic")
                    name = device_data.get("name", f"{device_type}-{device_id[:4]}")
                    x = device_data.get("x", 0)
                    y = device_data.get("y", 0)
                    
                    # Create the device
                    device = Device(device_id, device_type, name, QPointF(x, y))
                    
                    # Set properties if available
                    if "properties" in device_data:
                        device.properties = device_data["properties"]
                    
                    # Add to scene & manager
                    if self.device_manager.scene:
                        self.device_manager.scene.addItem(device)
                    self.device_manager.devices[device.id] = device
        
        except Exception as e:
            print(f"Error importing devices: {str(e)}")
            traceback.print_exc()
    
    def _import_connections(self, connections_data):
        """Import connections from serialized data."""
        if not self.connection_manager:
            print("No connection manager available for importing connections")
            return
        
        try:
            from models.connection import Connection
            
            for connection_data in connections_data:
                source_device_id = connection_data.get("source_device_id")
                target_device_id = connection_data.get("target_device_id")
                
                source_device = self.device_manager.devices.get(source_device_id)
                target_device = self.device_manager.devices.get(target_device_id)
                
                if not source_device or not target_device:
                    print(f"Skipping connection with missing devices: {connection_data}")
                    continue
                
                # Create connection
                connection = Connection(
                    id=connection_data.get("id"),
                    source_device=source_device,
                    source_port={"name": connection_data.get("source_port_name")},
                    target_device=target_device,
                    target_port={"name": connection_data.get("target_port_name")},
                    connection_type=connection_data.get("connection_type", "ethernet")
                )
                
                # Add to manager
                self.connection_manager.connections[connection.id] = connection
        
        except Exception as e:
            print(f"Error importing connections: {str(e)}")
            traceback.print_exc()
    
    def _import_boundaries(self, boundaries_data):
        """Import boundaries from serialized data."""
        if not self.boundary_controller:
            print("No boundary controller available for importing boundaries")
            return
        
        try:
            from models.boundary_item import Boundary
            
            for boundary_data in boundaries_data:
                # Check if Boundary class has a from_dict method
                if hasattr(Boundary, "from_dict") and callable(Boundary.from_dict):
                    # Create boundary using from_dict class method
                    boundary = Boundary.from_dict(boundary_data)
                    
                    # Add to scene & controller
                    if boundary and self.boundary_controller.scene:
                        self.boundary_controller.scene.addItem(boundary)
                        self.boundary_controller.boundaries[boundary.id] = boundary
                else:
                    # Create boundary manually
                    boundary_id = boundary_data.get("id", str(id(boundary_data)))
                    name = boundary_data.get("name", "Boundary")
                    boundary_type = boundary_data.get("type", "area")
                    x = boundary_data.get("x", 0)
                    y = boundary_data.get("y", 0)
                    width = boundary_data.get("width", 100)
                    height = boundary_data.get("height", 100)
                    color_data = boundary_data.get("color", {"r": 200, "g": 200, "b": 255, "a": 100})
                    color = QColor(color_data["r"], color_data["g"], color_data["b"], color_data["a"])
                    
                    # Create the boundary
                    boundary = Boundary(boundary_id, name, boundary_type, QRectF(x, y, width, height), color)
                    
                    # Add to scene & controller
                    if self.boundary_controller.scene:
                        self.boundary_controller.scene.addItem(boundary)
                    self.boundary_controller.boundaries[boundary.id] = boundary
        
        except Exception as e:
            print(f"Error importing boundaries: {str(e)}")
            traceback.print_exc()