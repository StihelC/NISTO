from controllers.file_dialog_manager import FileDialogManager
from controllers.topology_serializer import TopologySerializer
from controllers.topology_exporter import TopologyExporter
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QFileDialog, QMessageBox
from PyQt5.QtGui import QFont, QColor, QPen, QBrush, QImage, QPainter
from PyQt5.QtCore import Qt, QObject, QPointF
import json
import os
from models.device import Device
class FileManager(QObject):
    """Manages saving and loading topology files."""
    
    def __init__(self, main_window):
        """Initialize the file manager."""
        super().__init__()
        self.main_window = main_window
        self.device_manager = None
        self.connection_manager = None
        self.last_saved_file = None
    
    def save_topology(self):
        """Save the current topology to a file."""
        try:
            if not self.last_saved_file:
                return self.save_topology_as()
                
            # Save to the last used file
            return self._save_to_file(self.last_saved_file)
        
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error Saving", f"Could not save topology: {str(e)}")
            return False
    
    def save_topology_as(self):
        """Save the current topology to a new file."""
        try:
            # Get file path from user
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save Topology",
                "",
                "Network Topology Files (*.ntd);;All Files (*)"
            )
            
            if not file_path:
                return False  # User canceled
            
            # Add extension if not present
            if not file_path.endswith('.ntd'):
                file_path += '.ntd'
            
            # Save to the selected file
            success = self._save_to_file(file_path)
            
            if success:
                self.last_saved_file = file_path
            
            return success
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error Saving", f"Could not save topology: {str(e)}")
            return False
    
    def _save_to_file(self, file_path):
        """Save topology data to the specified file."""
        if not self.device_manager or not hasattr(self.main_window, 'scene'):
            QMessageBox.warning(self.main_window, "Warning", "No data to save.")
            return False
        
        # Prepare data structure
        topology_data = {
            'version': '1.0',
            'devices': [],
            'connections': [],
            'boundaries': []
        }
        
        # Export devices
        for device_id, device in self.device_manager.devices.items():
            device_data = {
                'id': device.id,
                'type': device.device_type,
                'name': device.name,
                'x': device.pos().x(),
                'y': device.pos().y(),
                'properties': device.properties
            }
            topology_data['devices'].append(device_data)
        
        # Export connections if available
        if self.connection_manager and hasattr(self.connection_manager, 'connections'):
            for connection_id, connection in self.connection_manager.connections.items():
                conn_data = {
                    'id': connection_id,
                    'source_device_id': connection.source_device.id if connection.source_device else None,
                    'target_device_id': connection.target_device.id if connection.target_device else None,
                    'type': connection.connection_type,
                    'properties': {}
                }
                
                # Add properties if available
                if hasattr(connection, 'properties'):
                    conn_data['properties'] = connection.properties
                
                topology_data['connections'].append(conn_data)
        
        # Save to file as JSON
        with open(file_path, 'w') as f:
            json.dump(topology_data, f, indent=2)
        
        self.main_window.statusBar().showMessage(f"Topology saved to {file_path}", 3000)
        return True
    
    def load_topology(self):
        """Load a topology from a file."""
        try:
            # Get file path from user
            file_path, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "Open Topology",
                "",
                "Network Topology Files (*.ntd);;All Files (*)"
            )
            
            if not file_path:
                return False  # User canceled
            
            # Clear current topology
            self._clear_current_topology()
            
            # Load from file
            with open(file_path, 'r') as f:
                topology_data = json.load(f)
            
            # Process devices
            device_map = {}  # Map old IDs to new device objects
            
            for device_data in topology_data['devices']:
                # Create device
                device = self.device_manager.create_device(
                    device_data['type'],
                    device_data['x'],
                    device_data['y']
                )
                
                if device:
                    # Update properties
                    for key, value in device_data['properties'].items():
                        device.update_property(key, value)
                    
                    # Store in map for connections
                    device_map[device_data['id']] = device
            
            # Process connections
            for conn_data in topology_data.get('connections', []):
                # Get devices by ID
                source_device = device_map.get(conn_data['source_device_id'])
                target_device = device_map.get(conn_data['target_device_id'])
                
                if source_device and target_device and self.connection_manager:
                    # Create connection
                    connection = self.connection_manager.create_connection(
                        source_device,
                        target_device,
                        conn_data.get('type', 'standard')
                    )
                    
                    # Update properties if available
                    if connection and 'properties' in conn_data:
                        if hasattr(connection, 'properties'):
                            for key, value in conn_data['properties'].items():
                                connection.properties[key] = value
            
            # Update status
            self.last_saved_file = file_path
            self.main_window.statusBar().showMessage(f"Topology loaded from {file_path}", 3000)
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error Loading", f"Could not load topology: {str(e)}")
            return False
    
    def _clear_current_topology(self):
        """Clear the current topology."""
        # Clear connections
        if self.connection_manager:
            if hasattr(self.connection_manager, 'clear_all_connections'):
                self.connection_manager.clear_all_connections()
        
        # Clear devices
        if self.device_manager:
            if hasattr(self.device_manager, 'clear_all_devices'):
                self.device_manager.clear_all_devices()
            else:
                # Fallback if method doesn't exist
                scene = self.main_window.scene
                if scene:
                    scene.clear()
    
    def export_as_png(self):
        """Export the current topology as PNG image."""
        try:
            # Get file path from user
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Export as PNG",
                "",
                "PNG Images (*.png);;All Files (*)"
            )
            
            if not file_path:
                return False  # User canceled
            
            # Add extension if not present
            if not file_path.endswith('.png'):
                file_path += '.png'
            
            # Get view and scene
            view = self.main_window.graphics_view
            scene = self.main_window.scene
            
            if not view or not scene:
                QMessageBox.warning(self.main_window, "Warning", "No topology to export.")
                return False
            
            # Create a image of the current scene
            image = QImage(scene.sceneRect().size().toSize(), QImage.Format_ARGB32)
            image.fill(0xFFFFFFFF)  # White background
            
            # Paint the scene onto the image
            painter = QPainter(image)
            scene.render(painter)
            painter.end()
            
            # Save the image
            image.save(file_path)
            
            self.main_window.statusBar().showMessage(f"Topology exported to {file_path}", 3000)
            return True
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error Exporting", f"Could not export image: {str(e)}")
            return False


    # Find code for saving devices:
    def _serialize_devices(self):
        devices_data = []
        for device in self.device_manager.devices.values():
            device_data = {
                'id': device.id,
                'type': device.device_type,
                'name': device.name,
                'x': device.pos().x(),
                'y': device.pos().y(),
                'properties': device.properties
            }
            devices_data.append(device_data)
        return devices_data

    # Replace with:
    def _serialize_devices(self):
        devices_data = []
        for device in self.device_manager.devices.values():
            devices_data.append(device.to_dict())
        return devices_data

    # Find code for loading devices:
    def _load_devices(self, devices_data):
        for device_data in devices_data:
            device_type = device_data['type']
            x = device_data['x']
            y = device_data['y']
            device = self.device_manager.create_device(device_type, x, y)
            device.id = device_data['id']
            device.name = device_data['name']
            if 'properties' in device_data:
                device.properties.update(device_data['properties'])

    # Replace with:
    def _load_devices(self, devices_data):
        for device_data in devices_data:
            device = Device.from_dict(device_data)
            self.device_manager.devices[device.id] = device
            if self.device_manager.scene:
                self.device_manager.scene.addItem(device)