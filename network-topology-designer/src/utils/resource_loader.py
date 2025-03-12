import os
from PyQt5.QtGui import QIcon, QPixmap

def get_app_path():
    """Get the absolute path to the application root directory."""
    # Go up three levels: utils -> src -> network-topology-designer
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_resource_path(relative_path):
    """Get absolute path to a resource file."""
    app_path = get_app_path()
    resource_path = os.path.join(app_path, "src", "resources", relative_path)
    return resource_path

def load_icon(icon_name):
    """Load an icon from the resources/icons directory."""
    # Add .png extension if not provided
    if not icon_name.endswith('.png'):
        icon_name += '.png'
        
    icon_path = get_resource_path(os.path.join("icons", icon_name))
    
    # Check if file exists
    if not os.path.exists(icon_path):
        print(f"Icon not found: {icon_path}")
        return QIcon()
        
    return QIcon(icon_path)

def load_pixmap(icon_name):
    """Load a pixmap from the resources/icons directory."""
    # Add .png extension if not provided
    if not icon_name.endswith('.png'):
        icon_name += '.png'
        
    icon_path = get_resource_path(os.path.join("icons", icon_name))
    
    # Check if file exists
    if not os.path.exists(icon_path):
        print(f"Icon not found: {icon_path}")
        return QPixmap()
        
    return QPixmap(icon_path)