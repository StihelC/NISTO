import uuid

class Connection:
    """Model class for connections between devices."""
    
    def __init__(self, source_device, target_device, connection_type="standard"):
        """Initialize a connection between devices."""
        self.id = str(uuid.uuid4())
        self.source_device = source_device
        self.target_device = target_device
        self.connection_type = connection_type
        self.source_port = None
        self.target_port = None
        self.view = None  # Will be set when view is created
        
        # Properties
        self.properties = {
            'name': f"Connection-{self.id[:4]}",
            'type': connection_type,
            'bandwidth': '1 Gbps',
            'status': 'active'
        }
        
        # Add this connection to both devices
        if source_device:
            source_device.add_connection(self)
        if target_device:
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
    
    def update_position(self):
        """Update connection position based on connected devices."""
        if self.view:
            self.view.update_position()