import json
from PyQt5.QtWidgets import QFileDialog, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QColor, QPen
from PyQt5.QtCore import Qt, QRectF

class FileManager:
    """Manages file operations for topology saving, loading and exporting."""
    
    def __init__(self, main_window, scene, device_manager, connection_manager):
        self.main_window = main_window
        self.scene = scene
        self.device_manager = device_manager
        self.connection_manager = connection_manager
    
    def save_topology(self):
        """Save the current topology to a file."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self.main_window, "Save Topology", "", "Topology Files (*.topo);;All Files (*)"
            )
            if filename:
                # Ensure filename has .topo extension
                if not filename.lower().endswith('.topo'):
                    filename += '.topo'
                
                # Create data structure for topology
                topology_data = {
                    'devices': [],
                    'connections': [],
                    'textboxes': [],
                    'boundaries': []
                }
                
                # Process all items in the scene
                device_map = {}  # Map device objects to IDs
                device_id_counter = 1
                
                for item in self.scene.items():
                    # Handle different item types
                    from models.device import NetworkDevice
                    from models.connection import NetworkConnection
                    
                    if isinstance(item, NetworkDevice):
                        # Save device data
                        device_id = f"device_{device_id_counter}"
                        device_id_counter += 1
                        
                        device_data = {
                            'id': device_id,
                            'type': item.device_type,
                            'x': item.scenePos().x(),
                            'y': item.scenePos().y(),
                            'size': item.size,
                            'properties': item.properties,
                            'rotation': item.rotation()
                        }
                        
                        topology_data['devices'].append(device_data)
                        device_map[item] = device_id
                    
                    elif isinstance(item, NetworkConnection):
                        # Skip connections for now (we'll process after all devices)
                        pass
                    
                    elif isinstance(item, QGraphicsTextItem) and item.parentItem() is None:
                        # Standalone text items (not labels for other objects)
                        text_data = {
                            'content': item.toPlainText(),
                            'x': item.scenePos().x(),
                            'y': item.scenePos().y(),
                            'font': item.font().toString(),
                            'color': item.defaultTextColor().name()
                        }
                        topology_data['textboxes'].append(text_data)
                    
                    elif isinstance(item, QGraphicsRectItem) and item.parentItem() is None:
                        # Probably a boundary box
                        rect = item.rect()
                        
                        # Try to find an associated label
                        label_text = ""
                        for text_item in self.scene.items():
                            if isinstance(text_item, QGraphicsTextItem) and text_item.parentItem() is None:
                                # Check if text is positioned just above the rectangle
                                text_pos = text_item.scenePos()
                                rect_pos = item.scenePos()
                                if (abs(text_pos.x() - rect_pos.x()) < 20 and 
                                    text_pos.y() < rect_pos.y() and
                                    text_pos.y() > rect_pos.y() - 30):
                                    label_text = text_item.toPlainText()
                                    break
                        
                        boundary_data = {
                            'x': item.scenePos().x(),
                            'y': item.scenePos().y(),
                            'width': rect.width(),
                            'height': rect.height(),
                            'label': label_text,
                            'pen_color': item.pen().color().name(),
                            'brush_color': item.brush().color().name(),
                            'brush_alpha': item.brush().color().alpha()
                        }
                        topology_data['boundaries'].append(boundary_data)
                
                # Now process connections
                for item in self.scene.items():
                    from models.connection import NetworkConnection
                    
                    if isinstance(item, NetworkConnection):
                        # Only save connections where we have both endpoints
                        if item.source_device in device_map and item.target_device in device_map:
                            conn_data = {
                                'source_id': device_map[item.source_device],
                                'target_id': device_map[item.target_device],
                                'type': item.connection_type,
                                'source_port': item.source_port,
                                'target_port': item.target_port
                            }
                            topology_data['connections'].append(conn_data)
                
                # Save to file
                with open(filename, 'w') as file:
                    json.dump(topology_data, file, indent=2)
                
                self.main_window.statusBar().showMessage(f"Topology saved to {filename}", 5000)
                print(f"Topology saved to {filename}")
                
        except Exception as e:
            print(f"Error saving topology: {e}")
            import traceback
            traceback.print_exc()
            self.main_window.statusBar().showMessage(f"Error saving topology: {str(e)}", 5000)
    
    def load_topology(self):
        """Load a topology from a file."""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self.main_window, "Load Topology", "", "Topology Files (*.topo);;All Files (*)"
            )
            if filename:
                # Clear existing scene
                self.scene.clear()
                
                # Open the file and load topology data
                with open(filename, 'r') as file:
                    topology_data = json.load(file)
                
                # Process the loaded data
                if 'devices' in topology_data:
                    # Load devices first
                    device_map = {}  # Map saved device IDs to newly created devices
                    
                    for device_data in topology_data['devices']:
                        # Create device with saved properties
                        device_type = device_data.get('type', 'router')
                        x = device_data.get('x', 0)
                        y = device_data.get('y', 0)
                        properties = device_data.get('properties', {})
                        
                        # Create the device
                        device = self.device_manager.create_device(
                            device_type, x, y, 
                            size=device_data.get('size', 64),
                            properties=properties
                        )
                        
                        if device:
                            # Store mapping from saved ID to new device
                            device_map[device_data.get('id')] = device
                            
                            # If device has custom positioning, restore it
                            if 'rotation' in device_data:
                                device.setRotation(device_data['rotation'])
                
                if 'connections' in topology_data:
                    # Now load connections
                    for conn_data in topology_data['connections']:
                        # Get source and target devices from our mapping
                        source_id = conn_data.get('source_id')
                        target_id = conn_data.get('target_id')
                        
                        if source_id in device_map and target_id in device_map:
                            source_device = device_map[source_id]
                            target_device = device_map[target_id]
                            conn_type = conn_data.get('type', 'ethernet')
                            source_port = conn_data.get('source_port')
                            target_port = conn_data.get('target_port')
                            
                            # Create the connection
                            self.connection_manager.create_connection(
                                source_device, target_device, conn_type,
                                source_port, target_port
                            )
                
                if 'textboxes' in topology_data:
                    # Load text annotations
                    for text_data in topology_data['textboxes']:
                        x = text_data.get('x', 0)
                        y = text_data.get('y', 0)
                        content = text_data.get('content', '')
                        
                        # Create text item
                        text_item = QGraphicsTextItem(content)
                        text_item.setPos(x, y)
                        
                        # Set font and color if specified
                        if 'font' in text_data:
                            from PyQt5.QtGui import QFont
                            font = QFont()
                            font.fromString(text_data['font'])
                            text_item.setFont(font)
                            
                        if 'color' in text_data:
                            from PyQt5.QtGui import QColor
                            text_item.setDefaultTextColor(QColor(text_data['color']))
                        
                        self.scene.addItem(text_item)
                
                if 'boundaries' in topology_data:
                    # Load boundary boxes
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
                        
                        # Add label
                        if label:
                            text_item = QGraphicsTextItem(label)
                            text_item.setPos(x, y - 20)  # Position above rectangle
                            self.scene.addItem(text_item)
                        
                        self.scene.addItem(rect_item)
                
                # Reset view to fit contents
                self.main_window.ui.graphicsView.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                
                self.main_window.statusBar().showMessage(f"Topology loaded from {filename}", 5000)
                print(f"Topology loaded from {filename}")
                
        except json.JSONDecodeError as e:
            print(f"Error parsing topology file: {e}")
            self.main_window.statusBar().showMessage("Error: Invalid topology file format", 5000)
        except Exception as e:
            print(f"Error loading topology: {e}")
            import traceback
            traceback.print_exc()
            self.main_window.statusBar().showMessage(f"Error loading topology: {str(e)}", 5000)
    
    def export_as_png(self):
        """Export the current view as a PNG image."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self.main_window, "Export as PNG", "", "PNG Files (*.png);;All Files (*)"
            )
            
            if not filename:
                return  # User canceled
                
            # Ensure filename has .png extension
            if not filename.lower().endswith('.png'):
                filename += '.png'
            
            # Determine the area to export
            if self.scene.items():
                # Get bounding rect of all items with some padding
                rect = self.scene.itemsBoundingRect()
                # Add padding
                padding = 20
                rect.adjust(-padding, -padding, padding, padding)
            else:
                # Default size if scene is empty
                rect = QRectF(-300, -300, 600, 600)
            
            # Create a pixmap with appropriate size
            pixmap = QPixmap(rect.width(), rect.height())
            pixmap.fill(Qt.white)  # White background
            
            # Create painter for the pixmap
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            # Render the scene onto the pixmap
            self.scene.render(
                painter,
                pixmap.rect(),
                rect,
                Qt.KeepAspectRatio
            )
            
            # Clean up
            painter.end()
            
            # Save the pixmap to file
            if pixmap.save(filename):
                self.main_window.statusBar().showMessage(f"Topology exported to {filename}", 5000)
                print(f"Topology exported to {filename}")
            else:
                self.main_window.statusBar().showMessage("Error: Failed to save PNG file", 5000)
                print(f"Failed to save PNG to {filename}")
                
        except Exception as e:
            print(f"Error exporting as PNG: {e}")
            import traceback
            traceback.print_exc()
            self.main_window.statusBar().showMessage(f"Error exporting as PNG: {str(e)}", 5000)