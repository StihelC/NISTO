from PyQt5.QtGui import QPixmap, QIcon
import os

class ResourceManager:
    """Manager for loading and caching application resources."""
    
    def __init__(self):
        """Initialize the resource manager."""
        self.icon_cache = {}
        self.pixmap_cache = {}
        
        # Base path for resources
        self.resource_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "resources"
        )
        
        # Device icon paths
        self.device_icons = {
            "router": "icons/router.png",
            "switch": "icons/switch.png",
            "server": "icons/server.png",
            "client": "icons/client.png",
            "firewall": "icons/firewall.png",
            "cloud": "icons/cloud.png",
            "generic": "icons/generic.png"
        }
        
        # Try to preload device icons
        self._preload_device_icons()
    
    def _preload_device_icons(self):
        """Preload device icons into cache."""
        for device_type, icon_path in self.device_icons.items():
            self.get_device_pixmap(device_type)
    
    def get_device_pixmap(self, device_type, size=None):
        """Get a pixmap for a device type.
        
        Args:
            device_type: Type of device (router, switch, etc.)
            size: Optional size tuple (width, height) for scaling
            
        Returns:
            QPixmap object or None if not found
        """
        # Standardize device type
        device_type = device_type.lower()
        
        # Create cache key
        cache_key = f"{device_type}_{size}" if size else device_type
        
        # Check if already in cache
        if cache_key in self.pixmap_cache:
            return self.pixmap_cache[cache_key]
        
        # Get icon path
        icon_path = self.device_icons.get(device_type, self.device_icons.get("generic"))
        if not icon_path:
            print(f"No icon found for device type: {device_type}")
            return None
            
        # Full path
        full_path = os.path.join(self.resource_path, icon_path)
        
        # Try to load pixmap
        pixmap = QPixmap(full_path)
        if pixmap.isNull():
            print(f"Failed to load pixmap from {full_path}")
            return None
            
        # Scale if needed
        if size:
            pixmap = pixmap.scaled(size[0], size[1])
            
        # Store in cache
        self.pixmap_cache[cache_key] = pixmap
        
        return pixmap
    
    def get_icon_path(self, icon_name):
        """Get the full path to an icon."""
        return os.path.join(self.resource_path, "icons", f"{icon_name}.png")