from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QPen, QBrush, QColor
from models.device import NetworkDevice

class DeviceManager(QObject):
    def __init__(self, scene):
        """Initialize the device manager with a QGraphicsScene."""
        super().__init__()
        self.scene = scene
        self.devices = []  # List to track all devices
        
    def create_device(self, device_type, position):
        """Create a new device and add it to the scene."""
        try:
            print(f"Creating {device_type} at ({position.x()}, {position.y()})")
            
            # Create the device with icon and label as a group
            device = NetworkDevice(
                device_type=device_type,
                x=position.x(),
                y=position.y()
            )
            
            # Add the grouped device to scene
            self.scene.addItem(device)
            
            # Track the device
            self.devices.append(device)
            
            return device
        except Exception as e:
            print(f"Error creating device: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def remove_device(self, device):
        """Remove a device from the scene."""
        if device in self.devices:
            self.scene.removeItem(device)  # Removes the entire group
            self.devices.remove(device)
            return True
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