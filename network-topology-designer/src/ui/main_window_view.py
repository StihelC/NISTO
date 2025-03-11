from PyQt5.QtWidgets import (
    QMainWindow, QGraphicsView, QGraphicsScene, QAction, QToolBar,
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QToolButton,
    QDockWidget, QLabel, QStatusBar, QGroupBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

class MainWindowView(QMainWindow):
    """Main window view for the network topology designer application."""
    
    def __init__(self):
        """Initialize the main window view."""
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("NISTO Network Topology Designer")
        self.resize(1200, 800)
        
        # Create central widget and main layout
        self._create_central_widget()
        
        # Create menus
        self._create_menus()
        
        # Create toolbar
        self._create_toolbar()
        
        # Create dock widgets
        self._create_dock_widgets()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
    
    def _create_central_widget(self):
        """Create the central widget with graphics view."""
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create graphics view for network topology
        self.graphics_view = QGraphicsView()
        self.graphics_view.setRenderHint(1)  # Antialiasing
        self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        
        main_layout.addWidget(self.graphics_view)
        self.setCentralWidget(central_widget)
    
    def _create_menus(self):
        """Create application menus."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        self.action_new = QAction("&New", self)
        self.action_new.setShortcut("Ctrl+N")
        file_menu.addAction(self.action_new)
        
        self.action_open = QAction("&Open", self)
        self.action_open.setShortcut("Ctrl+O")
        file_menu.addAction(self.action_open)
        
        self.action_save = QAction("&Save", self)
        self.action_save.setShortcut("Ctrl+S")
        file_menu.addAction(self.action_save)
        
        self.action_save_as = QAction("Save &As...", self)
        self.action_save_as.setShortcut("Ctrl+Shift+S")
        file_menu.addAction(self.action_save_as)
        
        file_menu.addSeparator()
        
        self.action_export_png = QAction("Export as &PNG", self)
        file_menu.addAction(self.action_export_png)
        
        file_menu.addSeparator()
        
        self.action_exit = QAction("E&xit", self)
        self.action_exit.setShortcut("Alt+F4")
        file_menu.addAction(self.action_exit)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")
        
        self.action_undo = QAction("&Undo", self)
        self.action_undo.setShortcut("Ctrl+Z")
        edit_menu.addAction(self.action_undo)
        
        self.action_redo = QAction("&Redo", self)
        self.action_redo.setShortcut("Ctrl+Y")
        edit_menu.addAction(self.action_redo)
        
        # View menu
        view_menu = self.menuBar().addMenu("&View")
        
        self.action_zoom_in = QAction("Zoom &In", self)
        self.action_zoom_in.setShortcut("Ctrl++")
        view_menu.addAction(self.action_zoom_in)
        
        self.action_zoom_out = QAction("Zoom &Out", self)
        self.action_zoom_out.setShortcut("Ctrl+-")
        view_menu.addAction(self.action_zoom_out)
        
        self.action_reset_view = QAction("&Reset View", self)
        view_menu.addAction(self.action_reset_view)
        
        # Tools menu
        tools_menu = self.menuBar().addMenu("&Tools")
        
        self.action_select_mode = QAction("&Select", self)
        self.action_select_mode.setCheckable(True)
        tools_menu.addAction(self.action_select_mode)
        
        self.action_add_device = QAction("Add &Device", self)
        self.action_add_device.setCheckable(True)
        tools_menu.addAction(self.action_add_device)
        
        self.action_add_connection = QAction("Add &Connection", self)
        self.action_add_connection.setCheckable(True)
        tools_menu.addAction(self.action_add_connection)
        
        self.action_add_text = QAction("Add &Text Box", self)
        self.action_add_text.setCheckable(True)
        tools_menu.addAction(self.action_add_text)
        
        self.action_add_boundary = QAction("Add &Boundary", self)
        self.action_add_boundary.setCheckable(True)
        tools_menu.addAction(self.action_add_boundary)
        
        self.action_delete_mode = QAction("&Delete", self)
        self.action_delete_mode.setCheckable(True)
        tools_menu.addAction(self.action_delete_mode)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        self.action_about = QAction("&About", self)
        help_menu.addAction(self.action_about)
    
    def _create_toolbar(self):
        """Create the main toolbar with tool buttons."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Selection tool
        self.btn_select = QToolButton()
        self.btn_select.setText("Select")
        self.btn_select.setToolTip("Select and move items")
        self.btn_select.setCheckable(True)
        toolbar.addWidget(self.btn_select)
        
        # Add device tool
        self.btn_add_device = QToolButton()
        self.btn_add_device.setText("Add Device")
        self.btn_add_device.setToolTip("Add a network device")
        self.btn_add_device.setCheckable(True)
        toolbar.addWidget(self.btn_add_device)
        
        # Add connection tool
        self.btn_add_connection = QToolButton()
        self.btn_add_connection.setText("Add Connection")
        self.btn_add_connection.setToolTip("Add a connection between devices")
        self.btn_add_connection.setCheckable(True)
        toolbar.addWidget(self.btn_add_connection)
        
        # Add text tool
        self.btn_add_text = QToolButton()
        self.btn_add_text.setText("Add Text")
        self.btn_add_text.setToolTip("Add a text annotation")
        self.btn_add_text.setCheckable(True)
        toolbar.addWidget(self.btn_add_text)
        
        # Add boundary tool
        self.btn_add_boundary = QToolButton()
        self.btn_add_boundary.setText("Add Boundary")
        self.btn_add_boundary.setToolTip("Add a boundary area")
        self.btn_add_boundary.setCheckable(True)
        toolbar.addWidget(self.btn_add_boundary)
        
        # Delete tool
        self.btn_delete = QToolButton()
        self.btn_delete.setText("Delete")
        self.btn_delete.setToolTip("Delete selected items")
        self.btn_delete.setCheckable(True)
        toolbar.addWidget(self.btn_delete)
        
        toolbar.addSeparator()
        
        # Zoom controls
        self.btn_zoom_in = QToolButton()
        self.btn_zoom_in.setText("+")
        self.btn_zoom_in.setToolTip("Zoom in")
        toolbar.addWidget(self.btn_zoom_in)
        
        self.btn_zoom_out = QToolButton()
        self.btn_zoom_out.setText("-")
        self.btn_zoom_out.setToolTip("Zoom out")
        toolbar.addWidget(self.btn_zoom_out)
        
        self.btn_reset_view = QToolButton()
        self.btn_reset_view.setText("Reset")
        self.btn_reset_view.setToolTip("Reset view")
        toolbar.addWidget(self.btn_reset_view)
    
    def _create_dock_widgets(self):
        """Create dock widgets for properties and groups."""
        # Properties dock
        properties_dock = QDockWidget("Properties", self)
        properties_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        properties_content = QWidget()
        properties_layout = QVBoxLayout(properties_content)
        properties_layout.addWidget(QLabel("No item selected"))
        properties_dock.setWidget(properties_content)
        self.properties_dock = properties_dock
        
        # Groups dock
        groups_dock = QDockWidget("Groups", self)
        groups_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        groups_content = QWidget()
        groups_layout = QVBoxLayout(groups_content)
        groups_layout.addWidget(QLabel("No groups defined"))
        groups_dock.setWidget(groups_content)
        self.groups_dock = groups_dock
        
        # Add docks to main window
        self.addDockWidget(Qt.RightDockWidgetArea, properties_dock)
        self.addDockWidget(Qt.LeftDockWidgetArea, groups_dock)