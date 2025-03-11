from PyQt5.QtCore import QObject, QPointF, Qt
from PyQt5.QtGui import QPen, QColor
# Fix the import to use our new model structure
try:
    from src.models.device_item import DeviceItem as NetworkDevice
except ImportError:
    # Fallback to relative imports
    from ..models.device_item import DeviceItem as NetworkDevice
# Or if you need specific functionality, use:
# from src.models.specialized_devices.router_device import RouterDevice
# from src.models.specialized_devices.switch_device import SwitchDevice

class ConnectionCreationTool(QObject):
    """Tool for creating connections between devices."""

    def __init__(self, canvas_controller, connection_manager=None):
        """Initialize the connection creation tool."""
        super().__init__()
        self.canvas_controller = canvas_controller
        self.scene = canvas_controller.scene
        
        # Store connection manager reference
        self.connection_manager = connection_manager
        
        # State tracking
        self.source_device = None
        self.source_port = None
        self.target_device = None
        self.target_port = None
        self.temp_connection = None
    
    def handle_press(self, event, scene_pos):
        """Handle mouse press events for connection creation."""
        # Find what was clicked
        view = self.canvas_controller.view
        item = view.itemAt(event.pos())
        
        # Check if we clicked on a device or port
        device = None
        port = None
        
        if isinstance(item, NetworkDevice):
            device = item
        elif hasattr(item, 'parentItem') and isinstance(item.parentItem(), NetworkDevice):
            device = item.parentItem()
            # Could be a port - check if it has a port_id
            if hasattr(item, 'port_id'):
                port = item.port_id
        
        # If we found a device, start connection
        if device:
            self.dragging = True
            self.source_device = device
            self.source_port = port
            
            # Create temporary visual feedback
            if self.temp_line:
                self.canvas_controller.scene.removeItem(self.temp_line)
            
            # Get starting point
            start_point = device.sceneBoundingRect().center() if not port else device.get_port_position(port)
            self.start_point = start_point
            
            return True
            
        return False
    
    def handle_move(self, event, scene_pos):
        """Handle mouse move events during connection creation."""
        if not self.dragging or not self.source_device:
            return False
            
        # Remove previous temp line if it exists
        if self.temp_line and self.temp_line.scene():
            self.canvas_controller.scene.removeItem(self.temp_line)
            
        # Create a new line from source to cursor
        from PyQt5.QtCore import QLineF
        
        # Use orthogonal path for temp line too
        from utils.path_routers import OrthogonalRouter
        router = OrthogonalRouter()
        path = router.create_path(self.start_point, scene_pos)
        
        # Create a temporary path item with dashed style
        from PyQt5.QtWidgets import QGraphicsPathItem
        self.temp_line = QGraphicsPathItem(path)
        
        # Use dashed blue pen for preview
        pen = QPen(QColor(0, 120, 215), 2, Qt.DashLine)
        self.temp_line.setPen(pen)
        
        # Add to scene and ensure it's visible
        self.canvas_controller.scene.addItem(self.temp_line)
        self.temp_line.setZValue(1000)
        
        return True
    
    def handle_release(self, event, scene_pos):
        """Handle mouse release events to complete connection creation."""
        if not self.dragging or not self.source_device:
            return False
            
        # Find the release target
        view = self.canvas_controller.view
        item = view.itemAt(event.pos())
        
        # Find target device and port if any
        target_device = None
        target_port = None
        
        if isinstance(item, NetworkDevice):
            target_device = item
        elif hasattr(item, 'parentItem') and isinstance(item.parentItem(), NetworkDevice):
            target_device = item.parentItem()
            if hasattr(item, 'port_id'):
                target_port = item.port_id
        
        # If we have valid source and target, create connection
        if target_device and target_device != self.source_device:
            self.connection_manager.create_connection(
                self.source_device,
                target_device,
                "ethernet",
                self.source_port,
                target_port
            )
        
        # Clean up
        if self.temp_line and self.temp_line.scene():
            self.canvas_controller.scene.removeItem(self.temp_line)
            self.temp_line = None
            
        self.dragging = False
        self.source_device = None
        self.source_port = None
        
        return True