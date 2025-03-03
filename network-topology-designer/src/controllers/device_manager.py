from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QPen, QBrush, QColor
from models.device import NetworkDevice  # Change to absolute

class DeviceManager(QObject):
    """Manages network devices on the canvas."""
    
    def __init__(self, scene):
        """Initialize the device manager with a QGraphicsScene."""
        super().__init__()
        self.scene = scene
        self.devices = []  # Track all devices
        
    def create_device(self, device_type, x, y, size=64, properties=None):
        """Create a new device and add it to the scene."""
        try:
            # Create the device
            device = NetworkDevice(device_type, x, y, size)
            
            # Add it to the scene
            self.scene.addItem(device)
            
            # Track the device
            self.devices.append(device)
            
            # Update properties if provided
            if properties:
                for key, value in properties.items():
                    device.update_property(key, value)
                    
            print(f"Device created: {device_type} at ({x}, {y}) with properties: {properties}")
            return device
        except Exception as e:
            print(f"Error creating device: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    def get_device_at(self, scene_pos, margin=10):
        """Find a device at the given position."""
        for device in self.devices:
            rect = device.sceneBoundingRect()
            # Expand the rect by the margin
            rect.adjust(-margin, -margin, margin, margin)
            if rect.contains(scene_pos):
                return device
        return None
        
    def remove_device(self, device):
        """Remove a device and all its connections from the scene."""
        if device not in self.devices:
            print(f"Device not found for removal")
            return False
            
        try:
            # Remove connections first
            if hasattr(self, 'connection_manager') and self.connection_manager:
                # If we have a reference to connection manager
                connections_to_remove = []
                for conn in self.connection_manager.connections:
                    if conn.source_device is device or conn.target_device is device:
                        connections_to_remove.append(conn)
                        
                for conn in connections_to_remove:
                    self.scene.removeItem(conn)
                    self.connection_manager.connections.remove(conn)
            
            # Now remove the device itself
            self.scene.removeItem(device)
            self.devices.remove(device)
            print(f"Removed device: {device.properties.get('name', 'unnamed')}")
            return True
        except Exception as e:
            print(f"Error removing device: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_devices_at_position(self, position, device_type=None):
        """Get all devices at the given position, optionally filtered by type."""
        devices = []
        items = self.scene.items(position)
        for item in items:
            if isinstance(item, NetworkDevice):
                if device_type is None or item.device_type == device_type:
                    devices.append(item)
        return devices
    
    def get_all_devices(self, device_type=None):
        """Get all devices, optionally filtered by type."""
        if device_type is None:
            return self.devices
        return [d for d in self.devices if d.device_type == device_type]

    def device_mouse_press(self, device, event):
        """Handle mouse press on a device."""
        # Store the initial position of the device
        device._drag_start_pos = device.pos()
        # Call the parent class's mousePressEvent
        super(NetworkDevice, device).mousePressEvent(event)
        # Bring this device to the front
        device.setZValue(100)  # Higher z values are drawn on top

    def device_mouse_move(self, device, event):
        """Handle mouse movement during device drag."""
        # Call the parent class's mouseMoveEvent
        super(NetworkDevice, device).mouseMoveEvent(event)
        # Update the label position
        self.position_label(device)

    def device_mouse_release(self, device, event):
        """Handle mouse release after device drag."""
        # Call the parent class's mouseReleaseEvent
        super(NetworkDevice, device).mouseReleaseEvent(event)
        # Reset the z-value to normal
        device.setZValue(1)
        # Make sure label position is updated
        self.position_label(device)