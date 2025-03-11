from src.models.device_item import DeviceItem

class ServerDevice(DeviceItem):
    """Server device model."""
    
    def __init__(self, name=None):
        """Initialize a server device."""
        super().__init__(device_type="server", name=name)