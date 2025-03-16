from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QGraphicsView, QWidget, 
    QAction, QToolBar, QFileDialog, QMessageBox, QDockWidget, QListWidget
)
from PyQt5.QtGui import QIcon, QPainter, QImage
from PyQt5.QtCore import Qt, QRectF, pyqtSlot

# Import models
from models.device import Device

# Import controllers
from controllers.device_manager import DeviceManager
from controllers.connection_tool import ConnectionCreationTool
from controllers.connection_manager import ConnectionManager
from controllers.boundary_controller import BoundaryController

# Import views
from views.topology_scene import TopologyScene

# Import utils
from utils.file_handler import FileHandler

class MainWindow(QMainWindow):
    """Main window for network topology designer application."""
    
    def __init__(self):
        print("Starting MainWindow initialization...")
        super().__init__()
        
        # Set up window properties
        self.setWindowTitle("Network Topology Designer")
        self.resize(1200, 800)
        
        # Initialize state
        self.current_mode = "select_mode"
        self.selected_device_type = "router"
        
        # Set up scene and view
        self._setup_scene_view()
        
        # Set up controllers
        self._setup_controllers()
        
        # Set up UI components
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Set initial mode
        self._enable_select_mode()
        
        # Status message
        self.statusBar().showMessage("Ready")
        print("MainWindow initialized")
        print("MainWindow initialization complete")
    
    def _setup_scene_view(self):
        """Set up the scene and view."""
        # Create scene
        self.scene = TopologyScene()
        
        # Create view
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Create central widget
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setCentralWidget(central_widget)
    
    def _setup_controllers(self):
        """Set up controller objects."""
        # Device manager
        self.device_manager = DeviceManager(self.scene)
        
        # Connection manager
        self.connection_manager = ConnectionManager(self.scene)
        
        # Connection tool
        self.connection_tool = ConnectionCreationTool(self, self.connection_manager)
        
        # Boundary controller
        self.boundary_controller = BoundaryController(self, self.scene)
        
        # File handler
        self.file_handler = FileHandler(
            device_manager=self.device_manager,
            connection_manager=self.connection_manager,
            boundary_controller=self.boundary_controller
        )
    
    def _setup_ui(self):
        """Set up UI components."""
        self._create_actions()
        self._setup_toolbar()
        self._setup_menubar()
        self._setup_dock_widgets()
        self._setup_statusbar()
    
    def _create_actions(self):
        """Create actions for menus and toolbars."""
        # Mode actions
        self.select_action = QAction("Select", self)
        self.select_action.setCheckable(True)
        self.select_action.setShortcut("S")
        self.select_action.triggered.connect(self._enable_select_mode)
        
        self.device_action = QAction("Add Device", self)
        self.device_action.setCheckable(True)
        self.device_action.setShortcut("D")
        self.device_action.triggered.connect(self._enable_device_mode)
        
        self.connection_action = QAction("Add Connection", self)
        self.connection_action.setCheckable(True)
        self.connection_action.setShortcut("C")
        self.connection_action.triggered.connect(self._enable_connection_mode)
        
        self.boundary_action = QAction("Add Boundary", self)
        self.boundary_action.setCheckable(True)
        self.boundary_action.setShortcut("B")
        self.boundary_action.triggered.connect(self._enable_boundary_mode)
        
        # Device type actions
        self.router_action = QAction("Router", self)
        self.router_action.triggered.connect(lambda: self._set_device_type("router"))
        
        self.switch_action = QAction("Switch", self)
        self.switch_action.triggered.connect(lambda: self._set_device_type("switch"))
        
        self.server_action = QAction("Server", self)
        self.server_action.triggered.connect(lambda: self._set_device_type("server"))
        
        self.firewall_action = QAction("Firewall", self)
        self.firewall_action.triggered.connect(lambda: self._set_device_type("firewall"))
        
        self.cloud_action = QAction("Cloud", self)
        self.cloud_action.triggered.connect(lambda: self._set_device_type("cloud"))
        
        # File actions
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self._on_new_topology)
        
        self.open_action = QAction("&Open", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self._on_open_topology)
        
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self._on_save_topology)
        
        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self._on_save_as_topology)
        
        self.export_action = QAction("&Export as Image", self)
        self.export_action.triggered.connect(self._on_export_image)
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        
        # Edit actions
        self.delete_action = QAction("&Delete", self)
        self.delete_action.setShortcut("Delete")
        self.delete_action.triggered.connect(self._on_delete_selected)
        
        # View actions
        self.zoom_in_action = QAction("Zoom &In", self)
        self.zoom_in_action.setShortcut("Ctrl++")
        self.zoom_in_action.triggered.connect(self._on_zoom_in)
        
        self.zoom_out_action = QAction("Zoom &Out", self)
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_out_action.triggered.connect(self._on_zoom_out)
        
        self.zoom_reset_action = QAction("&Reset Zoom", self)
        self.zoom_reset_action.setShortcut("Ctrl+0")
        self.zoom_reset_action.triggered.connect(self._on_zoom_reset)
    
    def _setup_toolbar(self):
        """Set up application toolbar."""
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        
        # Mode actions
        self.toolbar.addAction(self.select_action)
        self.toolbar.addAction(self.device_action)
        self.toolbar.addAction(self.connection_action)
        self.toolbar.addAction(self.boundary_action)
        
        self.toolbar.addSeparator()
        
        # Device types
        self.toolbar.addAction(self.router_action)
        self.toolbar.addAction(self.switch_action)
        self.toolbar.addAction(self.server_action)
        self.toolbar.addAction(self.firewall_action)
        self.toolbar.addAction(self.cloud_action)
        
        self.toolbar.addSeparator()
        
        # Other actions
        self.toolbar.addAction(self.delete_action)
        
        self.addToolBar(self.toolbar)
    
    def _setup_menubar(self):
        """Set up application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.delete_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.zoom_in_action)
        view_menu.addAction(self.zoom_out_action)
        view_menu.addAction(self.zoom_reset_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _setup_dock_widgets(self):
        """Set up dock widgets."""
        # Simple device list
        self.device_list = QListWidget()
        self.device_dock = QDockWidget("Devices", self)
        self.device_dock.setWidget(self.device_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.device_dock)
        
        # We'll skip property editor since you don't want that import
    
    def _setup_statusbar(self):
        """Set up the status bar."""
        self.statusBar().showMessage("Ready")
    
    def _connect_signals(self):
        """Connect signals between components."""
        try:
            # Scene signals
            if hasattr(self.scene, 'mouse_press_signal'):
                self.scene.mouse_press_signal.connect(self._on_scene_mouse_press)
            if hasattr(self.scene, 'mouse_move_signal'):
                self.scene.mouse_move_signal.connect(self._on_scene_mouse_move)
            if hasattr(self.scene, 'mouse_release_signal'):
                self.scene.mouse_release_signal.connect(self._on_scene_mouse_release)
            
            # Device manager signals
            if hasattr(self.device_manager, 'device_added'):
                self.device_manager.device_added.connect(self._on_device_added)
            if hasattr(self.device_manager, 'device_removed'):
                self.device_manager.device_removed.connect(self._on_device_removed)
            
            # Connection manager signals
            if hasattr(self.connection_manager, 'connection_created'):
                self.connection_manager.connection_created.connect(self._on_connection_created)
            if hasattr(self.connection_manager, 'connection_removed'):
                self.connection_manager.connection_removed.connect(self._on_connection_removed)
            
            # File handler signals
            if hasattr(self.file_handler, 'file_saved'):
                self.file_handler.file_saved.connect(lambda path: self.statusBar().showMessage(f"Saved: {path}", 3000))
            if hasattr(self.file_handler, 'file_loaded'):
                self.file_handler.file_loaded.connect(lambda path: self.statusBar().showMessage(f"Loaded: {path}", 3000))
            if hasattr(self.file_handler, 'file_error'):
                self.file_handler.file_error.connect(self._show_error_message)
                
        except Exception as e:
            print(f"Error connecting signals: {e}")
            import traceback
            traceback.print_exc()
    
    def _enable_select_mode(self):
        """Enable selection mode."""
        self.current_mode = "select_mode"
        
        # Update action states
        self.select_action.setChecked(True)
        self.device_action.setChecked(False)
        self.connection_action.setChecked(False)
        self.boundary_action.setChecked(False)
        
        # Update view
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setCursor(Qt.ArrowCursor)
        
        # Deactivate tools
        if hasattr(self.connection_tool, 'deactivate'):
            self.connection_tool.deactivate()
        
        # Update status
        self.statusBar().showMessage("Select Mode: Click to select items")
    
    def _enable_device_mode(self):
        """Enable device creation mode."""
        self.current_mode = "device_mode"
        
        # Update action states
        self.select_action.setChecked(False)
        self.device_action.setChecked(True)
        self.connection_action.setChecked(False)
        self.boundary_action.setChecked(False)
        
        # Update view
        self.view.setDragMode(QGraphicsView.NoDrag)
        self.view.setCursor(Qt.CrossCursor)
        
        # Deactivate tools
        if hasattr(self.connection_tool, 'deactivate'):
            self.connection_tool.deactivate()
        
        # Update status
        self.statusBar().showMessage(f"Device Mode: Click to add {self.selected_device_type}")
    
    def _enable_connection_mode(self):
        """Enable connection creation mode."""
        self.current_mode = "connection_mode"
        
        # Update action states
        self.select_action.setChecked(False)
        self.device_action.setChecked(False)
        self.connection_action.setChecked(True)
        self.boundary_action.setChecked(False)
        
        # Update view
        self.view.setDragMode(QGraphicsView.NoDrag)
        self.view.setCursor(Qt.CrossCursor)
        
        # Activate connection tool
        if hasattr(self.connection_tool, 'activate'):
            self.connection_tool.activate()
        
        # Update status
        self.statusBar().showMessage("Connection Mode: Click and drag to connect devices")
    
    def _enable_boundary_mode(self):
        """Enable boundary creation mode."""
        self.current_mode = "boundary_mode"
        
        # Update action states
        self.select_action.setChecked(False)
        self.device_action.setChecked(False)
        self.connection_action.setChecked(False)
        self.boundary_action.setChecked(True)
        
        # Update view
        self.view.setDragMode(QGraphicsView.NoDrag)
        self.view.setCursor(Qt.CrossCursor)
        
        # Deactivate tools
        if hasattr(self.connection_tool, 'deactivate'):
            self.connection_tool.deactivate()
        
        # Update status
        self.statusBar().showMessage("Boundary Mode: Click and drag to create a boundary")
    
    def _set_device_type(self, device_type):
        """Set the current device type."""
        self.selected_device_type = device_type
        
        # Switch to device mode if not already
        if self.current_mode != "device_mode":
            self._enable_device_mode()
            
        # Update status
        self.statusBar().showMessage(f"Device Mode: Click to add {device_type}")
    
    def _on_scene_mouse_press(self, event):
        """Handle mouse press events in the scene."""
        scene_pos = event.scenePos()
        print(f"Scene mouse press at {scene_pos.x()}, {scene_pos.y()}, mode: {self.current_mode}")
        
        try:
            # Handle based on current mode
            if self.current_mode == "device_mode":
                # Create a device
                self.device_manager.create_device(
                    self.selected_device_type,
                    scene_pos.x(),
                    scene_pos.y()
                )
                
            elif self.current_mode == "connection_mode":
                # Forward to connection tool
                self.connection_tool.handle_press(event, scene_pos)
                
            elif self.current_mode == "boundary_mode":
                # Forward to boundary controller
                self.boundary_controller.handle_mouse_press(event)
                
        except Exception as e:
            print(f"Error handling mouse press: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_scene_mouse_move(self, event):
        """Handle mouse move events in the scene."""
        scene_pos = event.scenePos()
        
        try:
            # Handle based on current mode
            if self.current_mode == "select_mode":
                # Update status with position
                self.statusBar().showMessage(f"Position: ({int(scene_pos.x())}, {int(scene_pos.y())})")
                
            elif self.current_mode == "connection_mode":
                # Forward to connection tool
                self.connection_tool.handle_move(event, scene_pos)
                
            elif self.current_mode == "boundary_mode":
                # Forward to boundary controller
                self.boundary_controller.handle_mouse_move(event)
                
        except Exception as e:
            print(f"Error handling mouse move: {e}")
    
    def _on_scene_mouse_release(self, event):
        """Handle mouse release events in the scene."""
        scene_pos = event.scenePos()
        print(f"Scene mouse release at {scene_pos.x()}, {scene_pos.y()}, mode: {self.current_mode}")
        
        try:
            # Handle based on current mode
            if self.current_mode == "connection_mode":
                # Forward to connection tool
                self.connection_tool.handle_release(event, scene_pos)
                
            elif self.current_mode == "boundary_mode":
                # Forward to boundary controller
                self.boundary_controller.handle_mouse_release(event)
                
        except Exception as e:
            print(f"Error handling mouse release: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_device_added(self, device):
        """Handle device added event."""
        try:
            # Update device list
            self._update_device_list()
                
            # Update status
            self.statusBar().showMessage(f"Added {device.device_type}: {device.name}", 3000)
            
        except Exception as e:
            print(f"Error handling device added: {e}")
    
    def _on_device_removed(self, device):
        """Handle device removed event."""
        try:
            # Update device list
            self._update_device_list()
                
            # Update status
            self.statusBar().showMessage(f"Removed {device.device_type}: {device.name}", 3000)
            
        except Exception as e:
            print(f"Error handling device removed: {e}")
    
    def _update_device_list(self):
        """Update the device list widget with current devices."""
        try:
            self.device_list.clear()
            
            if hasattr(self.device_manager, 'devices'):
                for device in self.device_manager.devices.values():
                    self.device_list.addItem(f"{device.name} ({device.device_type})")
        except Exception as e:
            print(f"Error updating device list: {e}")
    
    def _on_connection_created(self, connection):
        """Handle connection created event."""
        try:
            # Get device names
            source_name = connection.source_device.name if hasattr(connection.source_device, 'name') else "Unknown"
            target_name = connection.target_device.name if hasattr(connection.target_device, 'name') else "Unknown"
            
            # Update status
            self.statusBar().showMessage(f"Created connection: {source_name} → {target_name}", 3000)
            
        except Exception as e:
            print(f"Error handling connection created: {e}")
    
    def _on_connection_removed(self, connection):
        """Handle connection removed event."""
        try:
            # Get device names if available
            source_name = "Unknown"
            target_name = "Unknown"
            
            if hasattr(connection, 'source_device') and connection.source_device:
                source_name = connection.source_device.name
                
            if hasattr(connection, 'target_device') and connection.target_device:
                target_name = connection.target_device.name
                
            # Update status
            self.statusBar().showMessage(f"Removed connection: {source_name} → {target_name}", 3000)
            
        except Exception as e:
            print(f"Error handling connection removed: {e}")
    
    def _on_delete_selected(self):
        """Delete selected items."""
        selected_items = self.scene.selectedItems()
        
        if not selected_items:
            return
            
        for item in selected_items:
            if isinstance(item, Device):
                # Remove device's connections first
                if hasattr(self.connection_manager, 'remove_device_connections'):
                    self.connection_manager.remove_device_connections(item)
                    
                # Remove device
                self.device_manager.remove_device(item.id)
                
            # Handle connection items
            elif hasattr(item, 'source_device') and hasattr(item, 'target_device'):
                if hasattr(item, 'id') and hasattr(self.connection_manager, 'remove_connection'):
                    self.connection_manager.remove_connection(item.id)
                    
            # Handle boundary items
            elif hasattr(self.boundary_controller, 'boundaries'):
                for boundary_id, boundary_data in list(self.boundary_controller.boundaries.items()):
                    if item == boundary_data.get('boundary') or item == boundary_data.get('label'):
                        # Remove boundary items from scene
                        self.scene.removeItem(boundary_data.get('boundary'))
                        if 'label' in boundary_data:
                            self.scene.removeItem(boundary_data.get('label'))
                        # Remove from controller
                        del self.boundary_controller.boundaries[boundary_id]
                        break
        
        # Update status
        self.statusBar().showMessage(f"Deleted {len(selected_items)} items", 3000)
    
    def _on_new_topology(self):
        """Create a new topology."""
        if self.scene.items():
            reply = QMessageBox.question(
                self, 
                "New Topology",
                "Create new topology? This will clear the current design.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
                
        # Use file handler to create new topology
        if hasattr(self.file_handler, 'new_topology'):
            self.file_handler.new_topology()
        else:
            # Fallback implementation
            self.scene.clear()
            if hasattr(self.device_manager, 'devices'):
                self.device_manager.devices = {}
            if hasattr(self.connection_manager, 'connections'):
                self.connection_manager.connections = {}
            if hasattr(self.boundary_controller, 'boundaries'):
                self.boundary_controller.boundaries = {}
                
        self.statusBar().showMessage("New topology created")
        self._update_device_list()
    
    def _on_open_topology(self):
        """Open a topology from file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open Topology",
            "",
            "Topology Files (*.json);;All Files (*)"
        )
        
        if filepath:
            # Use file handler to load topology
            self.file_handler.load_topology(filepath)
            self._update_device_list()
    
    def _on_save_topology(self):
        """Save the current topology."""
        if not hasattr(self.file_handler, 'current_file') or not self.file_handler.current_file:
            self._on_save_as_topology()
        else:
            self.file_handler.save_topology()
    
    def _on_save_as_topology(self):
        """Save the current topology to a new file."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Topology",
            "",
            "Topology Files (*.json);;All Files (*)"
        )
        
        if filepath:
            if not filepath.lower().endswith('.json'):
                filepath += '.json'
                
            self.file_handler.save_topology(filepath)
    
    def _on_export_image(self):
        """Export topology as image."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Image",
            "",
            "PNG Images (*.png);;JPEG Images (*.jpg);;All Files (*)"
        )
        
        if filepath:
            if not (filepath.lower().endswith('.png') or filepath.lower().endswith('.jpg')):
                filepath += '.png'
                
            try:
                # Get bounding rectangle of all items
                rect = self.scene.itemsBoundingRect()
                # Add some padding
                rect.adjust(-20, -20, 20, 20)
                
                # Create image
                image = QImage(int(rect.width()), int(rect.height()), QImage.Format_ARGB32)
                image.fill(Qt.white)
                
                # Create painter and render scene
                painter = QPainter(image)
                painter.setRenderHint(QPainter.Antialiasing)
                self.scene.render(painter, QRectF(0, 0, rect.width(), rect.height()), rect)
                painter.end()
                
                # Save image
                if image.save(filepath):
                    self.statusBar().showMessage(f"Image exported to {filepath}", 3000)
                else:
                    self.statusBar().showMessage("Failed to export image", 3000)
                    
            except Exception as e:
                self._show_error_message(f"Error exporting image: {str(e)}")
                print(f"Error exporting image: {e}")
                import traceback
                traceback.print_exc()
    
    def _on_zoom_in(self):
        """Zoom in the view."""
        self.view.scale(1.2, 1.2)
    
    def _on_zoom_out(self):
        """Zoom out the view."""
        self.view.scale(1/1.2, 1/1.2)
    
    def _on_zoom_reset(self):
        """Reset view zoom."""
        self.view.resetTransform()
    
    def _on_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Network Topology Designer",
            "Network Topology Designer\n\n"
            "A tool for creating and editing network topology diagrams."
        )
    
    def _show_error_message(self, message):
        """Show an error message."""
        QMessageBox.critical(self, "Error", message)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Check for unsaved changes
        if self.scene.items():
            reply = QMessageBox.question(
                self,
                "Exit Application",
                "Do you want to save your changes before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                # Try to save and continue if successful
                self._on_save_topology()
                if hasattr(self.file_handler, 'current_file') and self.file_handler.current_file:
                    event.accept()
                else:
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        
        # Accept the close event
        event.accept()
    
    def showEvent(self, event):
        print("MainWindow show event triggered")
        super().showEvent(event)
        print("MainWindow show event completed")


