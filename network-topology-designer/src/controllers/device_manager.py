from PyQt5.QtCore import QObject, QPointF
# Use an absolute import to avoid any path issues
from src.models.device import NetworkDevice

class DeviceManager(QObject):
    def __init__(self, scene):
        """Initialize the device manager with a QGraphicsScene."""
        super().__init__()
        self.scene = scene
        self.devices = []  # List to track all devices
        
    def create_device(self, device_type, position):
        """Create a new device and add it to the scene."""
        try:
            print(f"DeviceManager: Creating {device_type} at ({position.x()}, {position.y()})")
            
            # Import the NetworkDevice class to ensure it's accessible
            from models.device import NetworkDevice
            
            # Create the device
            device = NetworkDevice(
                device_type=device_type,
                x=position.x(),
                y=position.y()
            )
            
            # Add to scene and track
            self.scene.addItem(device)
            self.devices.append(device)
            
            print(f"Device created successfully")
            return device
        except Exception as e:
            print(f"Error creating device: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def remove_device(self, device):
        """Remove a device from the scene."""
        try:
            if device in self.devices:
                self.scene.removeItem(device)
                self.devices.remove(device)
                print(f"Removed {device.device_type}")
                return True
            return False
        except Exception as e:
            print(f"Error removing device: {e}")
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