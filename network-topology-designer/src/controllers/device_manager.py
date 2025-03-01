from PyQt5.QtCore import QObject, QPointF
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QPen, QBrush, QColor
from models.device import NetworkDevice  # Make sure you're importing NetworkDevice, not Device

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
            
            # Create the device with icon and label
            device = NetworkDevice(
                device_type=device_type,
                x=position.x(),
                y=position.y()
            )
            
            # Add device group to scene
            self.scene.addItem(device)
            print(f"Added device to scene at pos: {device.pos()}")
            
            # Add the label to the scene
            self.scene.addItem(device.label)
            
            # Position the label below the device
            self.position_label(device)
            
            # Center view on the new device
            views = self.scene.views()
            if views:
                view = views[0]
                view.centerOn(device)
                print(f"Centered view on new device at {device.pos()}")
                
                # Add temporary text indicator at origin to help orientation
                origin_text = QGraphicsTextItem("ORIGIN (0,0)")
                origin_text.setPos(0, 0)
                origin_text.setDefaultTextColor(Qt.red)
                self.scene.addItem(origin_text)
            
            # Track the device
            self.devices.append(device)
            
            return device
        except Exception as e:
            print(f"Error creating device: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def position_label(self, device):
        """Position the label centered below the device."""
        try:
            # Get device position
            device_pos = device.scenePos()
            
            # Center the label horizontally under the device
            label_width = device.label.boundingRect().width()
            label_x = device_pos.x() + (device.size/2) - (label_width/2)
            label_y = device_pos.y() + device.size + 5
            
            device.label.setPos(label_x, label_y)
        except Exception as e:
            print(f"Error positioning label: {e}")
    
    def remove_device(self, device):
        """Remove a device from the scene."""
        try:
            if device in self.devices:
                # Remove both the device and its label
                self.scene.removeItem(device.label)
                self.scene.removeItem(device)
                self.devices.remove(device)
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