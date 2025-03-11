from src.models.device_item import DeviceItem

class ClientDevice(DeviceItem):
    """Client device model."""
    
    def __init__(self, name=None):
        """Initialize a client device."""
        super().__init__(device_type="client", name=name)
    
    def _init_ports(self):
        """Initialize device ports with fewer ports for a client."""
        self.ports = [
            {'name': 'Port 1', 'position': 'east', 'connected': False},
            {'name': 'Port 2', 'position': 'south', 'connected': False},
            {'name': 'Port 3', 'position': 'west', 'connected': False},
        ]