import os
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen, QBrush, QColor
from PyQt5.QtCore import Qt

class DeviceRegistry:
    """Manages the registry of available device types and their icons."""
    
    def __init__(self, icons_dir="src/resources/device_icons"):
        """Initialize the registry with the path to device icons."""
        self.icons_dir = self._find_icons_directory(icons_dir)
        self.device_types = self._discover_device_types()
        
    def _find_icons_directory(self, relative_path):
        """Find the absolute path to the icons directory."""
        # Try relative to the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        abs_path = os.path.join(project_root, relative_path)
        
        if os.path.isdir(abs_path):
            return abs_path
        
        # Try relative to current working directory
        cwd_path = os.path.join(os.getcwd(), relative_path)
        if os.path.isdir(cwd_path):
            return cwd_path
            
        # If directory doesn't exist, create it
        os.makedirs(abs_path, exist_ok=True)
        return abs_path
        
    def _discover_device_types(self):
        """Discover available device types from icon files."""
        device_types = []
        
        # Ensure the directory exists
        if not os.path.exists(self.icons_dir):
            print(f"Warning: Icons directory {self.icons_dir} not found")
            return device_types
        
        # Get all PNG files in the directory
        for filename in os.listdir(self.icons_dir):
            if filename.lower().endswith('.png'):
                # The device type is the filename without extension
                device_type = os.path.splitext(filename)[0].lower()
                device_types.append({
                    "type": device_type,
                    "name": device_type.capitalize(),
                    "icon_path": os.path.join(self.icons_dir, filename)
                })
        
        # Add default types if no icons found
        if not device_types:
            default_types = ["router", "switch", "server", "firewall", "workstation", "laptop"]
            for device_type in default_types:
                device_types.append({
                    "type": device_type,
                    "name": device_type.capitalize(),
                    "icon_path": None  # No icon path yet
                })
        
        return device_types
    
    def get_device_types(self):
        """Get the list of available device types."""
        return self.device_types
        
    def get_icon_path(self, device_type):
        """Get the icon path for a specific device type."""
        device_type = device_type.lower()
        for device in self.device_types:
            if device["type"] == device_type:
                return device["icon_path"]
        return None
        
    def create_placeholder_icons(self):
        """Create placeholder icons for default device types."""
        import os
        
        # Define default device types with colors
        default_types = {
            "router": QColor(173, 216, 230),  # Light blue
            "switch": QColor(144, 238, 144),  # Light green
            "server": QColor(255, 182, 193),  # Light pink
            "firewall": QColor(255, 160, 122),  # Light salmon
            "workstation": QColor(221, 160, 221),  # Plum
            "laptop": QColor(200, 200, 255),   # Light purple
            "default": QColor(200, 200, 200)   # Light gray
        }
        
        # Make sure the directory exists
        try:
            os.makedirs(self.icons_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating icons directory: {e}")
            return
        
        # Fixed size - using all integers to avoid conversion issues
        size = 64  # Icon size
        
        for device_type, color in default_types.items():
            try:
                # Create the icon path
                icon_path = os.path.join(self.icons_dir, f"{device_type}.png")
                
                # Skip if file already exists
                if os.path.exists(icon_path):
                    print(f"Icon already exists: {icon_path}")
                    continue
                    
                print(f"Creating icon for {device_type}...")
                
                # Create a pixmap
                pixmap = QPixmap(size, size)
                pixmap.fill(Qt.transparent)
                
                # Set up the painter
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setPen(QPen(Qt.black, 2))
                painter.setBrush(QBrush(color))
                
                # Extremely simplified approach - no float math
                # Just basic shapes with integer coordinates
                if device_type == "router":
                    # Circle for router
                    painter.drawEllipse(4, 4, 56, 56)  # size-8 = 56
                elif device_type == "switch":
                    # Square for switch
                    painter.drawRect(4, 4, 56, 56)
                elif device_type == "server":
                    # Rectangle with horizontal lines for server
                    painter.drawRect(4, 4, 56, 56)
                    painter.drawLine(4, 21, 60, 21)  # 1/3 down
                    painter.drawLine(4, 42, 60, 42)  # 2/3 down
                elif device_type == "firewall":
                    # Shield shape for firewall
                    painter.drawRect(4, 4, 56, 56)
                    painter.drawLine(4, 4, 60, 60)  # diagonal line
                    painter.drawLine(4, 60, 60, 4)  # crossed diagonal
                elif device_type == "workstation":
                    # Monitor and base for workstation
                    painter.drawRect(10, 4, 44, 40)  # monitor
                    painter.drawRect(20, 44, 24, 16)  # base
                elif device_type == "laptop":
                    # Laptop shape
                    painter.drawRect(8, 8, 48, 32)  # screen
                    painter.drawRect(4, 40, 56, 16)  # keyboard
                else:
                    # Default is just a square
                    painter.drawRect(4, 4, 56, 56)
                
                # Add text label
                font = painter.font()
                font.setPointSize(7)
                painter.setFont(font)
                painter.drawText(4, 4, 56, 56, Qt.AlignCenter, device_type.upper())
                
                # Clean up
                painter.end()
                
                # Save the pixmap
                success = pixmap.save(icon_path)
                if not success:
                    print(f"Failed to save icon to {icon_path}")
                else:
                    print(f"Created placeholder icon: {icon_path}")
                
                # Update the device type with the new icon path
                for device in self.device_types:
                    if device["type"] == device_type:
                        device["icon_path"] = icon_path
                        
            except Exception as e:
                print(f"Failed to create placeholder icon for {device_type}: {e}")
                import traceback
                traceback.print_exc()