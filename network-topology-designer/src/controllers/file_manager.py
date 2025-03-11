from controllers.file_dialog_manager import FileDialogManager
from controllers.topology_serializer import TopologySerializer
from controllers.topology_exporter import TopologyExporter
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QFont, QColor, QPen, QBrush
from PyQt5.QtCore import Qt

class FileManager:
    """Coordinates file operations for the network topology application."""
    
    def __init__(self, main_window, scene, device_manager, connection_manager):
        """Initialize the file manager."""
        self.main_window = main_window
        self.scene = scene
        self.device_manager = device_manager
        self.connection_manager = connection_manager
        
        # Initialize component managers
        self.dialog_manager = FileDialogManager(main_window.view)
        self.serializer = TopologySerializer()
        self.exporter = TopologyExporter(scene)
    
    def save_topology(self, force_dialog=False):
        """Save the current topology to a file."""
        # Get file path
        file_path, success = self.dialog_manager.get_save_path(
            title="Save Topology",
            file_filter="Network Topology Files (*.ntf);;All Files (*)",
            extension=".ntf",
            force_dialog=force_dialog
        )
        
        if not success:
            return False
        
        # Serialize topology
        topology_data = self.serializer.serialize_topology(
            self.scene,
            self.device_manager,
            self.connection_manager
        )
        
        # Save to file
        success, error = self.serializer.save_topology_to_file(file_path, topology_data)
        
        if success:
            self.main_window.statusBar().showMessage(f"Topology saved to {file_path}", 5000)
            return True
        else:
            print(f"Error saving topology: {error}")
            import traceback
            traceback.print_exc()
            self.main_window.statusBar().showMessage(f"Error saving topology: {error}", 5000)
            return False
    
    def load_topology(self):
        """Load a topology from a file."""
        # Get file path
        file_path, success = self.dialog_manager.get_open_path(
            title="Load Topology",
            file_filter="Network Topology Files (*.ntf);;All Files (*)"
        )
        
        if not success:
            return False
        
        # Load from file
        topology_data, error = self.serializer.load_topology_from_file(file_path)
        
        if topology_data is None:
            self.main_window.statusBar().showMessage(f"Error loading topology: {error}", 5000)
            return False
        
        # Clear current scene
        self.scene.clear()
        
        # Dictionary to store created devices for connection references
        created_devices = {}
        
        # Load devices
        if 'devices' in topology_data:
            for device_data in topology_data['devices']:
                device_type = device_data.get('type', 'generic')
                x = device_data.get('x', 0)
                y = device_data.get('y', 0)
                properties = device_data.get('properties', {})
                
                # Create device using device manager
                device = self.device_manager.create_device(device_type, x, y)
                
                if device:
                    # Set properties
                    device.properties = properties
                    
                    # Store in dictionary for connections
                    if 'id' in properties:
                        created_devices[properties['id']] = device
        
        # Load connections
        if 'connections' in topology_data:
            for connection_data in topology_data['connections']:
                source_id = connection_data.get('source_device_id')
                target_id = connection_data.get('target_device_id')
                
                # Find the devices
                source_device = created_devices.get(source_id)
                target_device = created_devices.get(target_id)
                
                if source_device and target_device:
                    # Create connection
                    connection = self.connection_manager.create_connection(
                        source_device, 
                        target_device
                    )
                    
                    if connection:
                        # Set properties
                        connection.properties = connection_data.get('properties', {})
                        connection.connection_type = connection_data.get('connection_type', 'ethernet')
                        connection.source_port = connection_data.get('source_port')
                        connection.target_port = connection_data.get('target_port')
                        
                        # Update visual appearance
                        connection.update_path()
        
        # Load text boxes
        if 'textboxes' in topology_data:
            for text_data in topology_data['textboxes']:
                x = text_data.get('x', 0)
                y = text_data.get('y', 0)
                text_content = text_data.get('text', '')
                
                # Create text item
                text_item = QGraphicsTextItem(text_content)
                text_item.setPos(x, y)
                
                if 'font' in text_data:
                    font = QFont()
                    font.fromString(text_data['font'])
                    text_item.setFont(font)
                
                if 'color' in text_data:
                    text_item.setDefaultTextColor(QColor(text_data['color']))
                
                self.scene.addItem(text_item)
        
        # Load boundaries
        if 'boundaries' in topology_data:
            for boundary_data in topology_data['boundaries']:
                x = boundary_data.get('x', 0)
                y = boundary_data.get('y', 0)
                width = boundary_data.get('width', 100)
                height = boundary_data.get('height', 100)
                label = boundary_data.get('label', '')
                
                # Create boundary
                rect_item = QGraphicsRectItem(0, 0, width, height)
                rect_item.setPos(x, y)
                
                # Set appearance
                pen_color = QColor(boundary_data.get('pen_color', '#000000'))
                brush_color = QColor(boundary_data.get('brush_color', '#C8C8FF'))
                
                # Apply alpha if specified
                alpha = boundary_data.get('brush_alpha', 50)
                brush_color.setAlpha(alpha)
                
                rect_item.setPen(QPen(pen_color, 1, Qt.DashLine))
                rect_item.setBrush(QBrush(brush_color))
                
                # Add label if specified
                if label:
                    text_item = QGraphicsTextItem(label)
                    text_item.setPos(x, y - 20)
                    self.scene.addItem(text_item)
                
                self.scene.addItem(rect_item)
        
        # Update status
        self.main_window.statusBar().showMessage(f"Topology loaded from {file_path}", 5000)
        return True
    
    def export_as_png(self):
        """Export the current view as a PNG image."""
        # Get file path
        file_path, success = self.dialog_manager.get_save_path(
            title="Export as PNG",
            file_filter="PNG Images (*.png);;All Files (*)",
            extension=".png"
        )
        
        if not success:
            return False
        
        # Export to PNG
        success, error = self.exporter.export_as_png(
            file_path, 
            background_color=Qt.white
        )
        
        if success:
            self.main_window.statusBar().showMessage(f"Topology exported to {file_path}", 5000)
            return True
        else:
            self.main_window.statusBar().showMessage(f"Error exporting topology: {error}", 5000)
            return False
    
    def export_as_svg(self):
        """Export the current view as an SVG image."""
        # Get file path
        file_path, success = self.dialog_manager.get_save_path(
            title="Export as SVG",
            file_filter="SVG Images (*.svg);;All Files (*)",
            extension=".svg"
        )
        
        if not success:
            return False
        
        # Export to SVG
        success, error = self.exporter.export_as_svg(file_path)
        
        if success:
            self.main_window.statusBar().showMessage(f"Topology exported to {file_path}", 5000)
            return True
        else:
            self.main_window.statusBar().showMessage(f"Error exporting topology: {error}", 5000)
            return False