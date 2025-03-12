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
        """Initialize the main window."""
        super().__init__()
        
        # Basic UI setup
        self.setWindowTitle("Network Topology Designer")
        self.resize(1200, 800)
        
        # Create central widget with graphics view
        self.graphics_view = QGraphicsView()
        self.setCentralWidget(self.graphics_view)
        
        # For backward compatibility
        self.view = self.graphics_view
        
        print("Creating canvas controller...")
        self.canvas_controller = CanvasController(self, self.graphics_view)
        
        # Now use the scene from the canvas_controller
        print("Creating device and connection managers...")
        self.device_manager = DeviceManager(self.canvas_controller.scene)
        self.connection_manager = ConnectionManager(self.canvas_controller.scene)
        
        # Link everything together
        self.device_manager.connection_manager = self.connection_manager
        self.connection_manager.device_manager = self.device_manager
        
        self.canvas_controller.device_manager = self.device_manager
        self.canvas_controller.connection_manager = self.connection_manager
        
        # Use canvas_controller.scene instead of self.scene
        print("Creating view manager...")
        self.view_manager = ViewManager(self, self.graphics_view, self.canvas_controller.scene)
        
        # Create mode manager
        print("Creating mode manager...")
        self.mode_manager = ModeManager(
            self.canvas_controller,
            self.graphics_view,
            self.device_manager,
            self.connection_manager
        )
        
        # Set on canvas controller
        self.canvas_controller.mode_manager = self.mode_manager
        
        # Set default mode to add router
        self.mode_manager.current_device_type = "router"
        self.mode_manager.set_mode(self.mode_manager.MODE_ADD_DEVICE)
        
        # Rest of initialization...
        
        # Create file manager
        self.file_manager = FileManager(
            self,
            self.canvas_controller.scene,
            self.device_manager,
            self.connection_manager
        )
        
        # Set up UI components
        self._setup_menubar()
        self._setup_toolbar()  # Add this call to set up the toolbar
        self._setup_statusbar()
        
        print("MainWindow initialization complete")
        
    def _setup_menubar(self):
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
    
    def _setup_toolbar(self):
        """Set up the application toolbar."""
        # Create main toolbar
        self.main_toolbar = QToolBar("Main Tools", self)
        self.addToolBar(Qt.TopToolBarArea, self.main_toolbar)
        
        # Add device actions
        self.add_router_action = QAction("Add Router", self)
        self.add_router_action.setIcon(QIcon.fromTheme("network-server"))
        self.add_router_action.setToolTip("Add a router to the topology")
        self.add_router_action.triggered.connect(lambda: self._set_device_mode("router"))
        self.main_toolbar.addAction(self.add_router_action)
        
        self.add_switch_action = QAction("Add Switch", self)
        self.add_switch_action.setIcon(QIcon.fromTheme("network-wired"))
        self.add_switch_action.setToolTip("Add a switch to the topology")
        self.add_switch_action.triggered.connect(lambda: self._set_device_mode("switch"))
        self.main_toolbar.addAction(self.add_switch_action)
        
        # Add separator
        self.main_toolbar.addSeparator()
        
        # Add connection tool
        self.add_connection_action = QAction("Add Connection", self)
        self.add_connection_action.setIcon(QIcon.fromTheme("network-transmit-receive"))
        self.add_connection_action.setToolTip("Add a connection between devices")
        self.add_connection_action.triggered.connect(self._set_connection_mode)
        self.main_toolbar.addAction(self.add_connection_action)
        
        # Add separator
        self.main_toolbar.addSeparator()
        
        # Add select mode
        self.select_mode_action = QAction("Select", self)
        self.select_mode_action.setIcon(QIcon.fromTheme("edit-select"))
        self.select_mode_action.setToolTip("Select and move devices")
        self.select_mode_action.triggered.connect(self._set_select_mode)
        self.main_toolbar.addAction(self.select_mode_action)
        
        # Add delete tool
        self.delete_action = QAction("Delete", self)
        self.delete_action.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_action.setToolTip("Delete selected elements")
        self.delete_action.triggered.connect(self._delete_selected)
        self.main_toolbar.addAction(self.delete_action)
        
        # Add separator
        self.main_toolbar.addSeparator()
        
        # Add grid visibility toggle
        self.toggle_grid_action = QAction("Toggle Grid", self)
        self.toggle_grid_action.setCheckable(True)
        self.toggle_grid_action.setChecked(False)  # Start with grid off
        self.toggle_grid_action.triggered.connect(self._toggle_grid)
        self.main_toolbar.addAction(self.toggle_grid_action)
    
    def _setup_statusbar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _set_device_mode(self, device_type):
        """Set the mode to add a specific device type."""
        self.mode_manager.current_device_type = device_type
        self.mode_manager.set_mode(self.mode_manager.MODE_ADD_DEVICE)

    def _set_connection_mode(self):
        """Set the mode to add connections."""
        self.mode_manager.set_mode(self.mode_manager.MODE_ADD_CONNECTION)

    def _set_select_mode(self):
        """Set the mode to selection mode."""
        self.mode_manager.set_mode(self.mode_manager.MODE_SELECT)

    def _delete_selected(self):
        """Delete selected items."""
        if hasattr(self.canvas_controller, 'delete_selected_items'):
            self.canvas_controller.delete_selected_items()
    
    def _toggle_grid(self):
        """Toggle grid visibility."""
        if hasattr(self.canvas_controller, 'toggle_grid'):
            self.canvas_controller.toggle_grid(self.toggle_grid_action.isChecked())

