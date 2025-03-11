import uuid

class Connection:
    """Model class for connections between network devices."""
    
    def __init__(self, source_device, target_device, connection_type="ethernet"):
        """Initialize a new connection between devices.
        
        Args:
            source_device: The source device
            target_device: The target device
            connection_type: Type of connection (ethernet, fiber, etc.)
        """
        self.id = str(uuid.uuid4())
        self.source_device = source_device
        self.target_device = target_device
        self.connection_type = connection_type
        self.source_port = None
        self.target_port = None
        
        # Properties dictionary for storing connection attributes
        self.properties = {
            'id': self.id,
            'name': f"Connection-{self.id[:6]}",
            'description': "",
            'bandwidth': "1 Gbps",
            'latency': "5 ms",
            'status': "active"
        }
        
        # Reference to view component (will be set by view factory)
        self.view = None
        
        # Add this connection to both devices
        if source_device and hasattr(source_device, 'add_connection'):
            source_device.add_connection(self)
            
        if target_device and hasattr(target_device, 'add_connection'):
            target_device.add_connection(self)
    
    def set_ports(self, source_port, target_port):
        """Set the source and target ports for this connection."""
        self.source_port = source_port
        self.target_port = target_port
        # Update view if it exists
        if self.view:
            self.view.update_from_model()
    
    def update_property(self, key, value):
        """Update a connection property."""
        self.properties[key] = value
        # Update view if it exists
        if self.view:
            self.view.update_from_model()