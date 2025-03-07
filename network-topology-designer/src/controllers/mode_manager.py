from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem

class ModeManager:
    """Manages application modes (selection, add device, add connection, etc.)."""
    
    def __init__(self, main_window, view, scene, canvas_controller):
        """Initialize the mode manager.
        
        Args:
            main_window: Reference to the main window
            view: The QGraphicsView widget
            scene: The QGraphicsScene containing topology items
            canvas_controller: The CanvasController for handling item creation
        """
        self.main_window = main_window
        self.view = view
        self.scene = scene
        self.canvas = canvas_controller
        self.current_mode = "selection"
    
    def set_mode(self, mode, **kwargs):
        """Set the application mode.
        
        Args:
            mode: The mode name to set
            **kwargs: Additional parameters specific to the mode
        """
        # Store previous mode for possible rollback
        previous_mode = self.current_mode
        
        try:
            # Update current mode
            self.current_mode = mode
            print(f"Setting mode: {mode}")
            
            # Configure the canvas controller
            self.canvas.set_mode(mode)
            
            # Handle mode-specific setup
            if mode == "selection":
                self._setup_selection_mode()
            elif mode == "add_device":
                self._setup_add_device_mode(**kwargs)
            elif mode == "add_connection":
                self._setup_add_connection_mode()
            elif mode == "add_textbox":
                self._setup_add_textbox_mode()
            elif mode == "add_boundary":
                self._setup_add_boundary_mode()
            elif mode == "delete":
                self._setup_delete_mode()
                
            # Update status message
            self._update_status_message(mode)
            
        except Exception as e:
            # Log error and potentially roll back mode
            print(f"Error setting mode {mode}: {e}")
            import traceback
            traceback.print_exc()
            self.current_mode = previous_mode
    
    def _setup_selection_mode(self):
        """Configure UI for selection mode."""
        # Selection mode uses rubber band selection
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        
        # Enable device dragging
        self._set_devices_draggable(True)
        
        # Hide unused ports
        self._set_ports_visibility(False)
    
    def _setup_add_device_mode(self, device_type=None):
        """Configure UI for add device mode."""
        # Add device mode uses no drag
        self.view.setDragMode(QGraphicsView.NoDrag)
        
        # Set specific device type if provided
        if device_type:
            self.canvas.set_item_type(device_type)
    
    def _setup_add_connection_mode(self):
        """Configure UI for add connection mode."""
        # Connection mode needs no drag
        self.view.setDragMode(QGraphicsView.NoDrag)
        
        # Disable device dragging to prevent issues
        self._set_devices_draggable(False)
        
        # Show all ports for connection
        self._set_ports_visibility(True)
    
    def _set_devices_draggable(self, draggable=True):
        """Enable or disable dragging for all devices."""
        from models.device import NetworkDevice
        
        for item in self.scene.items():
            if isinstance(item, NetworkDevice):
                item.setFlag(QGraphicsItem.ItemIsMovable, draggable)
    
    def _set_ports_visibility(self, visible=True):
        """Show or hide device ports."""
        from models.device import NetworkDevice
        
        for item in self.scene.items():
            if isinstance(item, NetworkDevice) and hasattr(item, 'show_all_ports'):
                item.show_all_ports(visible)
    
    def _update_status_message(self, mode):
        """Update the status bar message based on mode."""
        messages = {
            "selection": "Select or move items by clicking on them",
            "add_device": "Click on the canvas to add a device",
            "add_connection": "Click and drag from a device port to another device to create a connection",
            "add_textbox": "Click on the canvas to add a text box",
            "add_boundary": "Click and drag to create a boundary area",
            "delete": "Click on items to delete them"
        }
        
        if mode in messages:
            self.main_window.statusBar().showMessage(messages[mode])