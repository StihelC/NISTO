from src.models.device_item import DeviceItem

class RouterDevice(DeviceItem):
    """Router device model."""
    
    def __init__(self, name=None):
        """Initialize a router device."""
        super().__init__(device_type="router", name=name)