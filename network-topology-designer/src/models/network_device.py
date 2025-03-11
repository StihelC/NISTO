class NetworkDevice:
    """Model class representing a network device in the topology."""
    
    def __init__(self, device_id, name, device_type, x=0, y=0):
        self.id = device_id
        self.name = name
        self.type = device_type
        self.x = x
        self.y = y
        self.connections = []
        self.properties = {
            'id': device_id,
            'name': name,
            'description': "",
            'ip_address': "",
            'mac_address': "",
            'status': "active",
        }
    
    def add_connection(self, connection):
        """Add a connection to this device."""
        self.connections.append(connection)
    
    def remove_connection(self, connection):
        """Remove a connection from this device."""
        if connection in self.connections:
            self.connections.remove(connection)
    
    def update_property(self, key, value):
        """Update a device property."""
        self.properties[key] = value