import os
import logging
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QRect

class ResourceManager:
    """Manages application resources like icons and images."""
    
    @staticmethod
    def get_resource_path(resource_type, filename):
        """
        Get platform-independent path to a resource.
        
        Args:
            resource_type (str): Type of resource (e.g., 'device_icons')
            filename (str): Name of the resource file
            
        Returns:
            str: Full path to the resource if found, None otherwise
        """
        # Calculate base paths
        current_file = os.path.abspath(__file__)
        utils_dir = os.path.dirname(current_file)
        src_dir = os.path.dirname(utils_dir)
        project_root = os.path.dirname(src_dir)
        
        # Define possible locations in priority order
        possible_paths = [
            os.path.join(src_dir, "resources", resource_type, filename),
            os.path.join(project_root, "resources", resource_type, filename),
            os.path.join("resources", resource_type, filename)
        ]
        
        # Try each path
        for path in possible_paths:
            if os.path.exists(path):
                logging.debug(f"Resource found: {path}")
                return path
                
        logging.warning(f"Resource not found: {resource_type}/{filename}")
        return None
    
    @staticmethod
    def load_device_icon(device_type, size=40):
        """Load an icon for a given device type."""
        try:
            # Calculate paths
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(current_dir)
            project_dir = os.path.dirname(src_dir)
            
            # Possible icon paths
            icon_filename = f"{device_type.lower()}.png"
            possible_paths = [
                os.path.join(src_dir, "resources", "device_icons", icon_filename),
                os.path.join(project_dir, "resources", "device_icons", icon_filename),
                os.path.join("resources", "device_icons", icon_filename)
            ]
            
            # Try to load from each path
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"Loading device icon from: {path}")
                    return QPixmap(path).scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Create fallback icon if no file found
            return ResourceManager.create_fallback_icon(device_type, size)
            
        except Exception as e:
            print(f"Error loading device icon: {e}")
            return ResourceManager.create_fallback_icon(device_type, size)
    
    @staticmethod
    def create_fallback_icon(device_type, size=40):
        """Create a fallback icon when the device icon file is not found."""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        
        # Choose color based on device type
        if device_type.lower() == "router":
            color = QColor(255, 100, 100)  # Red
        elif device_type.lower() == "switch":
            color = QColor(100, 100, 255)  # Blue
        elif device_type.lower() == "firewall":
            color = QColor(255, 100, 255)  # Purple
        elif device_type.lower() == "server":
            color = QColor(100, 200, 100)  # Green
        else:
            color = QColor(200, 200, 200)  # Gray
        
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.black)
        painter.drawRect(0, 0, size-1, size-1)
        painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, device_type[0].upper())
        
        painter.end()
        return pixmap
    
    @staticmethod
    def load_stylesheet(name):
        """
        Load a QSS stylesheet from file.
        
        Args:
            name (str): Name of the stylesheet file
            
        Returns:
            str: Content of the stylesheet or empty string if not found
        """
        path = ResourceManager.get_resource_path("styles", f"{name}.qss")
        if path:
            with open(path, 'r') as file:
                return file.read()
        return ""