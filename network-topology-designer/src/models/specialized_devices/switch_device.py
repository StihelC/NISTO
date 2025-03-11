from src.models.device_item import DeviceItem

class SwitchDevice(DeviceItem):
    """Switch device model."""
    
    def __init__(self, name=None):
        """Initialize a switch device."""
        super().__init__(device_type="switch", name=name)
    
    def _init_ports(self):
        """Initialize device ports with more ports for a switch."""
        self.ports = [
            {'name': 'Port 1', 'position': 'north', 'connected': False},
            {'name': 'Port 2', 'position': 'north-east', 'connected': False},
            {'name': 'Port 3', 'position': 'east', 'connected': False},
            {'name': 'Port 4', 'position': 'south-east', 'connected': False},
            {'name': 'Port 5', 'position': 'south', 'connected': False},
            {'name': 'Port 6', 'position': 'south-west', 'connected': False},
            {'name': 'Port 7', 'position': 'west', 'connected': False},
            {'name': 'Port 8', 'position': 'north-west', 'connected': False},
        ]