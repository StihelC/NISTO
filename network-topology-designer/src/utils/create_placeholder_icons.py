from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRect
import os

def create_placeholder_icon(device_type, color, size=64):
    """Create a simple placeholder icon for a device type."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Draw different shapes based on device type
    if device_type == "router":
        # Draw a circle
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(4, 4, size-8, size-8)
    elif device_type == "switch":
        # Draw a rectangle
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(color))
        painter.drawRect(4, 4, size-8, size-8)
    elif device_type == "server":
        # Draw a server-like shape
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(color))
        painter.drawRect(4, 8, size-8, size-16)
        painter.drawLine(4, size/3, size-4, size/3)
        painter.drawLine(4, 2*size/3, size-4, 2*size/3)
    elif device_type == "firewall":
        # Draw a shield-like shape
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(color))
        painter.drawRect(4, 4, size-8, size-8)
        painter.drawLine(4, 4, size-4, size-4)  # X
        painter.drawLine(4, size-4, size-4, 4)
    elif device_type == "workstation":
        # Draw a monitor-like shape
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(color))
        painter.drawRect(8, 4, size-16, 3*size/4-8)
        painter.drawRect(size/3, 3*size/4, size/3, size/4-4)
    elif device_type == "laptop":
        # Draw a laptop-like shape
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(color))
        painter.drawRect(8, 8, size-16, size/2)
        painter.drawRect(4, size/2+8, size-8, size/4)
    
    painter.end()
    
    # Create directory if it doesn't exist
    icons_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 
                               '..', 'resources', 'icons'))
    os.makedirs(icons_dir, exist_ok=True)
    
    # Save the pixmap
    filename = os.path.join(icons_dir, f"{device_type}.png")
    pixmap.save(filename)
    print(f"Created placeholder icon: {filename}")

# Create icons for different device types
if __name__ == "__main__":
    create_placeholder_icon("router", QColor(173, 216, 230))  # Light blue
    create_placeholder_icon("switch", QColor(144, 238, 144))  # Light green
    create_placeholder_icon("server", QColor(255, 182, 193))  # Light pink
    create_placeholder_icon("firewall", QColor(255, 160, 122))  # Light salmon
    create_placeholder_icon("workstation", QColor(221, 160, 221))  # Plum
    create_placeholder_icon("laptop", QColor(200, 200, 255))  # Light purple