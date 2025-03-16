"""
Main Window Controller for Network Topology Designer
"""
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, QSettings
from src.ui.network_topo import NetworkTopoUI  # Adjusted import path
from src.controllers.canvas_controller import CanvasController
from src.controllers.device_manager import DeviceManager
from src.controllers.file_handler import FileHandler

class MainWindow(QMainWindow):
    """
    Main application window that coordinates between UI components
    and the underlying data model.
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.device_manager = DeviceManager()
        self.canvas_controller = CanvasController(self.device_manager)
        self.file_handler = FileHandler(self.device_manager, self.canvas_controller)
        
        # Set up the UI
        self.ui = NetworkTopoUI(self)
        self.setCentralWidget(self.ui.central_widget)
        
        # Connect signals to slots
        self.connect_signals()
        
        # Configure the window
        self.setup_window()
        
        # Restore previous session settings
        self.restore_settings()
    
    def setup_window(self):
        """Configure the main window appearance and behavior."""
        self.setWindowTitle("NISTO - Network Topology Designer")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
    
    def connect_signals(self):
        """Connect UI signals to their respective slots."""
        # File menu actions
        self.ui.action_new.triggered.connect(self.new_project)
        self.ui.action_open.triggered.connect(self.open_project)
        self.ui.action_save.triggered.connect(self.save_project)
        self.ui.action_save_as.triggered.connect(self.save_project_as)
        self.ui.action_export.triggered.connect(self.export_diagram)
        self.ui.action_exit.triggered.connect(self.close)
        
        # Edit menu actions
        self.ui.action_undo.triggered.connect(self.undo)
        self.ui.action_redo.triggered.connect(self.redo)
        
        # View menu actions
        self.ui.action_zoom_in.triggered.connect(self.canvas_controller.zoom_in)
        self.ui.action_zoom_out.triggered.connect(self.canvas_controller.zoom_out)
        self.ui.action_zoom_reset.triggered.connect(self.canvas_controller.zoom_reset)
        
        # Canvas interactions will be connected in the NetworkTopoUI class
    
    def new_project(self):
        """Create a new empty project."""
        if self.maybe_save():
            self.canvas_controller.clear_canvas()
            self.device_manager.clear_devices()
            self.file_handler.current_file = None
            self.setWindowTitle("NISTO - Network Topology Designer")
    
    def open_project(self):
        """Open an existing project file."""
        if self.maybe_save():
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Open Network Topology",
                "",
                "Network Topology Files (*.nettopo);;All Files (*)"
            )
            if filename:
                if self.file_handler.load_project(filename):
                    self.setWindowTitle(f"NISTO - Network Topology Designer - {filename}")
                else:
                    QMessageBox.warning(
                        self,
                        "Open Project Failed",
                        "Failed to open the selected project file."
                    )
    
    def save_project(self):
        """Save the current project."""
        if not self.file_handler.current_file:
            return self.save_project_as()
        
        if self.file_handler.save_project(self.file_handler.current_file):
            self.setWindowTitle(f"NISTO - Network Topology Designer - {self.file_handler.current_file}")
            return True
        else:
            QMessageBox.warning(
                self,
                "Save Project Failed",
                "Failed to save the project file."
            )
            return False
    
    def save_project_as(self):
        """Save the current project to a new file."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Network Topology",
            "",
            "Network Topology Files (*.nettopo);;All Files (*)"
        )
        
        if filename:
            if not filename.endswith(".nettopo"):
                filename += ".nettopo"
            
            if self.file_handler.save_project(filename):
                self.setWindowTitle(f"NISTO - Network Topology Designer - {filename}")
                return True
        
        return False
    
    def export_diagram(self):
        """Export the current diagram as an image."""
        formats = "PNG Files (*.png);;JPG Files (*.jpg);;SVG Files (*.svg);;PDF Files (*.pdf)"
        filename, selected_format = QFileDialog.getSaveFileName(
            self,
            "Export Diagram",
            "",
            formats
        )
        
        if filename:
            if self.file_handler.export_diagram(filename, selected_format):
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Diagram exported to {filename}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Export Failed",
                    "Failed to export the diagram."
                )
    
    def undo(self):
        """Undo the last action."""
        self.canvas_controller.undo()
    
    def redo(self):
        """Redo the last undone action."""
        self.canvas_controller.redo()
    
    def maybe_save(self):
        """Check if the project needs to be saved before proceeding."""
        if self.canvas_controller.is_modified():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Do you want to save your changes before continuing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                return self.save_project()
            elif reply == QMessageBox.Cancel:
                return False
        
        return True
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.maybe_save():
            self.save_settings()
            event.accept()
        else:
            event.ignore()
    
    def save_settings(self):
        """Save application settings."""
        settings = QSettings("NISTO", "NetworkTopologyDesigner")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        # Save other settings as needed
    
    def restore_settings(self):
        """Restore application settings."""
        settings = QSettings("NISTO", "NetworkTopologyDesigner")
        if settings.contains("geometry"):
            self.restoreGeometry(settings.value("geometry"))
        if settings.contains("windowState"):
            self.restoreState(settings.value("windowState"))
        # Restore other settings as needed
