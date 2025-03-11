from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QStatusBar, QToolBar, QAction, QMenu, QMenuBar, QWidget, QVBoxLayout, QGraphicsScene
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from controllers.view_factory import ViewFactory  # Use relative import
from controllers.canvas_controller import CanvasController
from controllers.device_manager import DeviceManager
from controllers.connection_manager import ConnectionManager
from src.controllers.view_manager import ViewManager
from src.controllers.mode_manager import ModeManager
from src.controllers.file_manager import FileManager

class MainWindow(QMainWindow):
    """Main window for the Network Topology Designer application."""
    
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Network Topology Designer")
        self.resize(1200, 800)
        
        # Create UI components using factory
        self.graphics_view = ViewFactory.create_graphics_view()
        self.setCentralWidget(self.graphics_view)
        
        # Initialize controllers
        self.canvas_controller = CanvasController(view=self.graphics_view)
        self.device_manager = DeviceManager(scene=self.canvas_controller.scene)
        self.connection_manager = ConnectionManager(scene=self.canvas_controller.scene)
        
        # Link everything together
        self.device_manager.view_factory = ViewFactory(self.canvas_controller.scene)
        self.device_manager.connection_manager = self.connection_manager
        self.connection_manager.device_manager = self.device_manager
        
        # Connect managers to canvas controller
        self.canvas_controller.device_manager = self.device_manager
        self.canvas_controller.connection_manager = self.connection_manager
        
        print("Creating mode manager...")
        self.mode_manager = ModeManager(
            self.canvas_controller,
            self.graphics_view,
            self.device_manager,
            self.connection_manager
        )
        
        # Set mode manager on canvas controller
        self.canvas_controller.mode_manager = self.mode_manager
        
        # Set default mode to add router
        self.mode_manager.current_device_type = "router"
        self.mode_manager.set_mode(self.mode_manager.MODE_ADD_DEVICE)
        
        # Rest of initialization...
        
        # Create view manager
        self.view_manager = ViewManager(self, self.graphics_view, self.scene)
        
        # Create file manager
        self.file_manager = FileManager(
            self,
            self.scene,
            self.device_manager,
            self.connection_manager
        )
        
        # Set up UI components
        self.setup_ui()
        
    def setup_ui(self):
        """Set up UI components."""
        # Create menu bar
        self.menu_bar = ViewFactory.create_menu_bar(self)
        self.setMenuBar(self.menu_bar)
        
        # File menu
        self.file_menu = QMenu("File", self)
        self.menu_bar.addMenu(self.file_menu)
        
        # Add file actions
        self.save_action = QAction("Save", self)
        self.save_action.triggered.connect(self.file_manager.save_topology)
        self.file_menu.addAction(self.save_action)
        
        self.load_action = QAction("Load", self)
        self.load_action.triggered.connect(self.file_manager.load_topology)
        self.file_menu.addAction(self.load_action)
        
        self.export_png_action = QAction("Export as PNG", self)
        self.export_png_action.triggered.connect(self.file_manager.export_as_png)
        self.file_menu.addAction(self.export_png_action)
        
        # Tools menu
        self.tools_menu = QMenu("Tools", self)
        self.menu_bar.addMenu(self.tools_menu)
        
        # Add tools actions
        self.add_device_action = QAction("Add Device", self)
        self.add_device_action.triggered.connect(lambda: self.mode_manager.set_mode("add_device"))
        self.tools_menu.addAction(self.add_device_action)
        
        self.add_connection_action = QAction("Add Connection", self)
        self.add_connection_action.triggered.connect(lambda: self.mode_manager.set_mode("add_connection"))
        self.tools_menu.addAction(self.add_connection_action)
        
        # View menu
        self.view_menu = QMenu("View", self)
        self.menu_bar.addMenu(self.view_menu)
        
        # Add view actions
        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.triggered.connect(self.view_manager.zoom_in)
        self.view_menu.addAction(self.zoom_in_action)
        
        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.triggered.connect(self.view_manager.zoom_out)
        self.view_menu.addAction(self.zoom_out_action)
        
        self.reset_view_action = QAction("Reset View", self)
        self.reset_view_action.triggered.connect(self.view_manager.reset_view)
        self.view_menu.addAction(self.reset_view_action)
    
    def _create_toolbars(self):
        """Create main toolbar with buttons."""
        self.main_toolbar = QToolBar("Main Toolbar", self)
        self.addToolBar(self.main_toolbar)
        
        # Add same actions as menus
        self.main_toolbar.addAction(self.add_device_action)
        self.main_toolbar.addAction(self.add_connection_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.zoom_in_action)
        self.main_toolbar.addAction(self.zoom_out_action)
        self.main_toolbar.addAction(self.reset_view_action)
    
    def _create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Will be implemented as needed
        pass

