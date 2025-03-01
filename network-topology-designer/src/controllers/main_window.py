# Update imports
from PyQt5.QtWidgets import (
    QMainWindow, 
    QGraphicsView, 
    QGraphicsScene, 
    QAction, 
    QToolBar,
    QMessageBox,
    QFileDialog,
    QGraphicsRectItem
)
from PyQt5.QtGui import QIcon, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPointF
from ui.network_topo import Ui_MainWindow
from .canvas_controller import CanvasController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Initialize the graphics scene
        self.scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)
        
        # Add this to ensure the view displays content properly:
        self.ui.graphicsView.setRenderHint(QPainter.Antialiasing)
        self.ui.graphicsView.setRenderHint(QPainter.SmoothPixmapTransform)
        self.ui.graphicsView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.ui.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)
        self.ui.graphicsView.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.ui.graphicsView.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Add this to your MainWindow initialization
        border_rect = QGraphicsRectItem(-500, -500, 1000, 1000)
        border_rect.setPen(QPen(Qt.gray, 1, Qt.DashLine))
        self.scene.addItem(border_rect)
        
        # Add a grid to the scene for better visibility
        self.add_grid_to_scene()
        
        # Initialize canvas controller
        self.canvas = CanvasController(self.ui.graphicsView)
        
        # Connect signals to slots
        self.setup_connections()
        
        # Set up the QGraphicsView properly for item manipulation
        self.ui.graphicsView.setRenderHint(QPainter.Antialiasing)
        self.ui.graphicsView.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # This is important - allows tools like selection and drag to work
        # Use RubberBandDrag when nothing is selected, NoDrag when we're manipulating items
        self.ui.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)
        
        # These settings help with proper transformation during zoom/pan
        self.ui.graphicsView.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.ui.graphicsView.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        
        # Very important - this allows interactive items to receive mouse events directly
        self.ui.graphicsView.setInteractive(True)
        
    def setup_ui(self):
        # ... existing code ...
        
        # Add view control actions to toolbar
        self.zoom_in_action = self.toolbar.addAction("Zoom In")
        self.zoom_out_action = self.toolbar.addAction("Zoom Out")
        self.reset_view_action = self.toolbar.addAction("Reset View")
        
        # Add a selection mode button to your toolbar in MainWindow.setup_ui
        self.select_action = self.toolbar.addAction("Select")
        self.select_action.triggered.connect(lambda: self.set_canvas_interaction_mode("select"))

    def setup_connections(self):
        """Connect UI signals to their corresponding slots."""
        
        # Define a simple debug function for button clicks
        def debug_button_click(mode, button_name):
            print(f"Button clicked: {button_name} -> Setting mode to: {mode}")
            self.canvas.set_mode(mode)
        
        # CORRECTED button mappings based on your UI layout
        button_mappings = {
            'toolButton_9': lambda: debug_button_click("add_device", "toolButton_9"),  # Add device
            'toolButton_10': lambda: debug_button_click("add_textbox", "toolButton_10"),  # Add textbox
            'toolButton_11': lambda: debug_button_click("add_connection", "toolButton_11"),  # Connection
            'toolButton_12': lambda: debug_button_click("add_boundary", "toolButton_12"),  # Boundary
            'toolButton_13': lambda: debug_button_click("select", "toolButton_13"),  # Select
            'toolButton_14': lambda: self.canvas.zoom_in(),  # Zoom in
            'toolButton_15': lambda: self.canvas.zoom_out(),  # Zoom out
            'toolButton_16': lambda: debug_button_click("delete", "toolButton_16")  # Delete
        }
        
        # Connect each tool button if it exists
        for button_name, callback in button_mappings.items():
            if hasattr(self.ui, button_name):
                button = getattr(self.ui, button_name)
                button.clicked.connect(callback)
                print(f"Connected {button_name}")
            else:
                print(f"Warning: {button_name} not found in UI")
        
        # Menu actions
        actions = {
            'actionSave': self.save_topology,
            'actionLoad': self.load_topology,
            'actionSave_as_PNG': self.export_as_png,
            'actionExport_as_PNG': self.export_as_png
        }
        
        for action_name, callback in actions.items():
            if hasattr(self.ui, action_name):
                action = getattr(self.ui, action_name)
                action.triggered.connect(callback)
        
        # Connect mouse press events
        self.original_mouse_press_event = self.ui.graphicsView.mousePressEvent
        self.ui.graphicsView.mousePressEvent = self.handle_mouse_press
        print("Connected mousePressEvent")

        self.connect_actions()
    
    def connect_actions(self):
        """Connect menu actions to their handlers"""
        print("Available UI actions:", [attr for attr in dir(self.ui) if attr.startswith('action')])
        try:
            # First check if actions exist before trying to connect them
            
            # File menu actions
            if hasattr(self.ui, 'actionSave'):
                self.ui.actionSave.triggered.connect(self.save_topology)
            if hasattr(self.ui, 'actionLoad'):
                self.ui.actionLoad.triggered.connect(self.load_topology)
            if hasattr(self.ui, 'actionSave_as_PNG'):
                self.ui.actionSave_as_PNG.triggered.connect(self.export_as_png)
                
            # View menu actions - use the actions from your UI file
        
            # With these (assuming your action names in your UI file):
            if hasattr(self.ui, 'actionZoom_In'):
                self.ui.actionZoom_In.triggered.connect(self.zoom_in)
            if hasattr(self.ui, 'actionZoom_Out'):
                self.ui.actionZoom_Out.triggered.connect(self.zoom_out)
                
        except Exception as e:
            print(f"Error connecting actions: {e}")

    def set_device_mode(self, device_type):
        """Set mode to add a specific device type."""
        self.canvas.set_mode("add_device")
        self.canvas.set_item_type(device_type)
        
    def handle_mouse_press(self, event):
        """Handle mouse press events on the graphics view."""
        print(f"Mouse pressed in mode: {self.canvas.current_mode}")
        
        # Convert the mouse position to scene coordinates
        scene_pos = self.ui.graphicsView.mapToScene(event.pos())
        print(f"Scene position: ({scene_pos.x()}, {scene_pos.y()})")
        
        # Handle the click
        self.canvas.handle_click(scene_pos)
        
        # Call the original handler if it exists
        if hasattr(self, 'original_mouse_press_event') and self.original_mouse_press_event:
            self.original_mouse_press_event(event)
        
    def save_topology(self):
        """Save the current topology to a file."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Topology", "", "Topology Files (*.topo);;All Files (*)"
            )
            if filename:
                # TODO: Implement actual save logic with FileHandler
                print(f"Saving topology to {filename}")
        except Exception as e:
            print(f"Error saving topology: {e}")
    
    def load_topology(self):
        """Load a topology from a file."""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Load Topology", "", "Topology Files (*.topo);;All Files (*)"
            )
            if filename:
                # TODO: Implement actual load logic with FileHandler
                print(f"Loading topology from {filename}")
        except Exception as e:
            print(f"Error loading topology: {e}")
    
    def export_as_png(self):
        """Export the current view as a PNG image."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export as PNG", "", "PNG Files (*.png);;All Files (*)"
            )
            if filename:
                # TODO: Implement actual export logic with FileHandler
                print(f"Exporting as PNG to {filename}")
        except Exception as e:
            print(f"Error exporting as PNG: {e}")
    
    def add_grid_to_scene(self):
        """Add a background grid to the scene for better visualization."""
        grid_size = 50
        grid_color = QColor(230, 230, 230)
        
        # Draw vertical lines
        for x in range(-1000, 1000, grid_size):
            line = self.scene.addLine(x, -1000, x, 1000, QPen(grid_color))
            line.setZValue(-1)  # Put grid behind other items
        
        # Draw horizontal lines
        for y in range(-1000, 1000, grid_size):
            line = self.scene.addLine(-1000, y, 1000, y, QPen(grid_color))
            line.setZValue(-1)  # Put grid behind other items
        
        # Add coordinate axis
        x_axis = self.scene.addLine(-1000, 0, 1000, 0, QPen(Qt.red, 1))
        y_axis = self.scene.addLine(0, -1000, 0, 1000, QPen(Qt.green, 1))
        x_axis.setZValue(-0.5)
        y_axis.setZValue(-0.5)

    def zoom_in(self):
        """Zoom in the view."""
        self.ui.graphicsView.scale(1.2, 1.2)

    def zoom_out(self):
        """Zoom out the view."""
        self.ui.graphicsView.scale(1/1.2, 1/1.2)

    def reset_view(self):
        """Reset the view to default."""
        self.canvas.reset_view()

    # Add this method to toggle between different selection/interaction modes
    def set_canvas_interaction_mode(self, mode):
        """Set the canvas interaction mode."""
        if mode == "select":
            # Enable selection and dragging of items
            self.ui.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)
            self.canvas.set_mode(None)  # No special mode
            
        elif mode == "add_device":
            # Disable rubber band selection when adding devices
            self.ui.graphicsView.setDragMode(QGraphicsView.NoDrag)
            self.canvas.set_mode("add_device")
            
        elif mode == "pan":
            # Allow panning the view
            self.ui.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag)
            self.canvas.set_mode(None)
            
        # Add other modes as needed