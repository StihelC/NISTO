from PyQt5.QtWidgets import (
    QMainWindow, 
    QGraphicsView, 
    QGraphicsScene, 
    QAction, 
    QToolBar,
    QMessageBox,
    QFileDialog,
    QGraphicsRectItem,
    QGraphicsItem
)
from PyQt5.QtGui import QIcon, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPointF
from ui.network_topo import Ui_MainWindow
from controllers.canvas_controller import CanvasController
from controllers.connection_manager import ConnectionManager
from controllers.device_manager import DeviceManager
from controllers.toolbar_manager import ToolbarManager
from controllers.action_manager import ActionManager
from controllers.view_manager import ViewManager
from controllers.mode_manager import ModeManager
from controllers.file_manager import FileManager
from controllers.mouse_handler import MouseHandler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set up the UI from PyQt Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Create better references to the UI buttons
        self._create_button_references()
        
        # Debug: Print available UI elements
        self._print_ui_elements()
        
        # Add this snippet temporarily in MainWindow.__init__
        print("\n=== UI Button Debug ===")
        for attr_name in dir(self.ui):
            attr = getattr(self.ui, attr_name)
            if hasattr(attr, 'clicked') and hasattr(attr, 'text'):
                print(f"Button: {attr_name} - Text: '{attr.text()}'")
        print("======================\n")
        
        # Create a graphics scene
        self.scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)
        
        # Create managers
        self.device_manager = DeviceManager(self.scene)
        self.connection_manager = ConnectionManager(self.scene)
        
        # Connect managers to each other
        self.device_manager.connection_manager = self.connection_manager
        
        # Create controllers
        self.canvas_controller = CanvasController(
            self.ui.graphicsView, 
            self.scene, 
            self.connection_manager,
            self.device_manager
        )
        
        # Create mode manager
        self.mode_manager = ModeManager(
            self, 
            self.ui.graphicsView, 
            self.scene, 
            self.canvas_controller
        )
        
        # Create file manager
        self.file_manager = FileManager(
            self, 
            self.scene, 
            self.device_manager, 
            self.connection_manager
        )
        
        # Create mouse handler
        self.mouse_handler = MouseHandler(
            self.ui.graphicsView, 
            self.scene, 
            self.canvas_controller,
            self.mode_manager
        )
        
        # Connect actions
        self._connect_actions()
        
        # Connect buttons
        self._connect_ui_buttons()
        
        # Connect all buttons to debug handler
        self._connect_all_buttons()
        
        # Start in selection mode
        self.set_selection_mode()
        
    def _create_button_references(self):
        """Create more meaningful references to UI buttons."""
        print("Creating button references with descriptive names")
        
        # Map buttons to meaningful names based on the debug output
        self.btn_add_device = self.ui.toolButton_9      # "Add Device"
        self.btn_add_text = self.ui.toolButton_10       # "Add Text Box"
        self.btn_add_connection = self.ui.toolButton_11 # "Add Connection"
        self.btn_add_boundary = self.ui.toolButton_12   # "Add Boundary"
        self.btn_select_mode = self.ui.toolButton_13    # "Select Mode"
        self.btn_zoom_in = self.ui.toolButton_14        # "+"
        self.btn_zoom_out = self.ui.toolButton_15       # "-"
        self.btn_delete_mode = self.ui.toolButton_16    # "Delete Mode"
        
        # Set proper tooltips
        self.btn_add_device.setToolTip("Add a network device to the topology")
        self.btn_add_text.setToolTip("Add text annotation")
        self.btn_add_connection.setToolTip("Create connection between devices")
        self.btn_add_boundary.setToolTip("Create a boundary area")
        self.btn_select_mode.setToolTip("Select and move items")
        self.btn_zoom_in.setToolTip("Zoom in")
        self.btn_zoom_out.setToolTip("Zoom out")
        self.btn_delete_mode.setToolTip("Delete items")

    def _connect_actions(self):
        """Connect UI actions to their respective handlers."""
        print("Connecting UI actions and buttons...")
        
        # Connect buttons
        self.btn_select_mode.clicked.connect(self.set_selection_mode)
        self.btn_add_device.clicked.connect(self.set_add_device_mode)
        self.btn_add_connection.clicked.connect(self.set_add_connection_mode)
        self.btn_add_text.clicked.connect(self.set_add_textbox_mode)
        self.btn_add_boundary.clicked.connect(self.set_add_boundary_mode)
        self.btn_delete_mode.clicked.connect(self.set_delete_mode)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        
        # Connect menu actions
        if hasattr(self.ui, 'actionSave'):
            self.ui.actionSave.triggered.connect(self.file_manager.save_topology)
        if hasattr(self.ui, 'actionLoad'):
            self.ui.actionLoad.triggered.connect(self.file_manager.load_topology)
        if hasattr(self.ui, 'actionSave_as_PNG'):
            self.ui.actionSave_as_PNG.triggered.connect(self.file_manager.export_as_png)
        
    # --- Mode setters (delegate to mode manager) ---
    
    def set_add_device_mode(self):
        """Set add device mode."""
        print("MainWindow.set_add_device_mode called")
        if hasattr(self, 'canvas_controller'):
            self.canvas_controller.set_mode("add_device")
        self.statusBar().showMessage("Add device mode: Click to add a device")
        self._update_button_states("add_device")
    
    def set_add_connection_mode(self):
        """Set add connection mode."""
        print("MainWindow.set_add_connection_mode called")
        if hasattr(self, 'canvas_controller'):
            self.canvas_controller.set_mode("add_connection")
        self.statusBar().showMessage("Add connection mode: Click and drag between devices")
        self._update_button_states("add_connection")
    
    def set_selection_mode(self):
        """Set the canvas to selection mode."""
        print("MainWindow.set_selection_mode called")
        
        # Update UI to show active state
        self._update_button_states("selection")
        
        # Set the mode in the controller
        if hasattr(self, 'canvas_controller'):
            print("Setting canvas controller mode to selection")
            self.canvas_controller.set_mode("selection")
        else:
            print("Error: No canvas_controller found")
        
        # Update status bar with instructions
        self.statusBar().showMessage("Selection mode: Click to select, drag to move items")
        
    def set_delete_mode(self):
        """Set delete mode."""
        print("MainWindow.set_delete_mode called")
        if hasattr(self, 'canvas_controller'):
            self.canvas_controller.set_mode("delete")
        self.statusBar().showMessage("Delete mode: Click on items to delete them")
        self._update_button_states("delete")
        
    def set_add_textbox_mode(self):
        """Set mode to add text boxes."""
        print("MainWindow.set_add_textbox_mode called")
        if hasattr(self, 'canvas_controller'):
            self.canvas_controller.set_mode("add_textbox")
        self.statusBar().showMessage("Add text mode: Click to add text annotation")
        self._update_button_states("add_textbox")
        
    def set_add_boundary_mode(self):
        """Set mode to add boundary areas."""
        print("MainWindow.set_add_boundary_mode called")
        if hasattr(self, 'canvas_controller'):
            self.canvas_controller.set_mode("add_boundary")
        self.statusBar().showMessage("Add boundary mode: Click and drag to create boundary area")
        self._update_button_states("add_boundary")
    
    # --- View operations ---
    
    def zoom_in(self):
        """Zoom in on the view."""
        print("Zooming in")
        self.ui.graphicsView.scale(1.25, 1.25)
    
    def zoom_out(self):
        """Zoom out on the view."""
        print("Zooming out")
        self.ui.graphicsView.scale(0.8, 0.8)

    def reset_view(self):
        self.ui.graphicsView.resetTransform()
        # Fit all items in view
        if self.scene.items():
            self.ui.graphicsView.fitInView(
                self.scene.itemsBoundingRect(),
                Qt.KeepAspectRatio
            )

    def _connect_buttons(self):
        """Connect button signals to their slots."""
        # Debug printing to verify method is called
        print("Connecting buttons to handlers...")
        
        # Connect toolbar buttons - adjust names to match your actual UI
        if hasattr(self.ui, 'toolButton_select'):
            print("Connecting select button")
            self.ui.toolButton_select.clicked.connect(self.set_selection_mode)
        
        if hasattr(self.ui, 'toolButton_add_device'):
            print("Connecting add device button")
            self.ui.toolButton_add_device.clicked.connect(self.set_add_device_mode)
        
        if hasattr(self.ui, 'toolButton_add_connection'):
            print("Connecting add connection button")
            self.ui.toolButton_add_connection.clicked.connect(self.set_add_connection_mode)
            
        if hasattr(self.ui, 'toolButton_add_text'):
            print("Connecting add text button")
            self.ui.toolButton_add_text.clicked.connect(self.set_add_textbox_mode)
        
        if hasattr(self.ui, 'toolButton_add_boundary'):
            print("Connecting add boundary button")
            self.ui.toolButton_add_boundary.clicked.connect(self.set_add_boundary_mode)
            
        if hasattr(self.ui, 'toolButton_delete'):
            print("Connecting delete button")
            self.ui.toolButton_delete.clicked.connect(self.set_delete_mode)
            
        # Connect any other buttons in the UI
        # ...additional button connections...

    def _connect_ui_buttons(self):
        """Connect UI buttons to their handler methods."""
        print("Connecting UI buttons...")
        
        # Connect toolbar buttons - adjust button names based on your actual UI
        # Check your .ui file or use print(dir(self.ui)) to see available button names
        
        # Selection tool
        if hasattr(self.ui, 'btn_select'):
            print("Connecting selection button")
            self.ui.btn_select.clicked.connect(self.set_selection_mode)
        
        if hasattr(self.ui, 'btn_add_device'):
            print("Connecting add device button")
            self.ui.btn_add_device.clicked.connect(self.set_add_device_mode)
        
        if hasattr(self.ui, 'btn_add_connection'):
            print("Connecting add connection button")
            self.ui.btn_add_connection.clicked.connect(self.set_add_connection_mode)
        
        if hasattr(self.ui, 'btn_add_text'):
            print("Connecting add text button")
            self.ui.btn_add_text.clicked.connect(self.set_add_textbox_mode)
        
        if hasattr(self.ui, 'btn_add_boundary'):
            print("Connecting add boundary button") 
            self.ui.btn_add_boundary.clicked.connect(self.set_add_boundary_mode)
        
        if hasattr(self.ui, 'btn_delete'):
            print("Connecting delete button")
            self.ui.btn_delete.clicked.connect(self.set_delete_mode)
        
        # Handle any other UI buttons
        # Add more button connections based on your UI

    def _print_ui_elements(self):
        """Debug method to print available UI elements."""
        print("\n=== Available UI Elements ===")
        for attr in dir(self.ui):
            if not attr.startswith('_'):  # Skip private attributes
                element = getattr(self.ui, attr)
                if hasattr(element, 'objectName'):
                    print(f"- {attr}: {element.objectName()}")
        print("===========================\n")
        
    def _connect_all_buttons(self):
        """Connect all buttons to debug handler."""
        for attr_name in dir(self.ui):
            attr = getattr(self.ui, attr_name)
            if hasattr(attr, 'clicked'):  # If it's a button-like object
                print(f"Connecting {attr_name}")
                # Use lambda to capture the button name
                attr.clicked.connect(lambda checked=False, name=attr_name: self._debug_button_click(name))

    def _debug_button_click(self, button_name):
        """Debug handler that prints which button was clicked."""
        print(f"Button clicked: {button_name}")

    def _update_button_states(self, active_mode):
        """Update button states based on active mode."""
        # Reset all buttons to not checked
        if hasattr(self, 'btn_select_mode'):
            self.btn_select_mode.setChecked(active_mode == "selection")
        if hasattr(self, 'btn_add_device'):
            self.btn_add_device.setChecked(active_mode == "add_device")
        if hasattr(self, 'btn_add_connection'):
            self.btn_add_connection.setChecked(active_mode == "add_connection")
        if hasattr(self, 'btn_add_text'):
            self.btn_add_text.setChecked(active_mode == "add_textbox")
        if hasattr(self, 'btn_add_boundary'):
            self.btn_add_boundary.setChecked(active_mode == "add_boundary") 
        if hasattr(self, 'btn_delete_mode'):
            self.btn_delete_mode.setChecked(active_mode == "delete")

