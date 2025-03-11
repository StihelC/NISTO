import json
from PyQt5.QtWidgets import QGraphicsTextItem, QGraphicsRectItem
from PyQt5.QtCore import QRectF

class TopologySerializer:
    """Handles serialization and deserialization of network topology data."""
    
    def serialize_topology(self, scene, device_manager, connection_manager):
        """Serialize the current topology to a dictionary."""
        topology_data = {
            'devices': [],
            'connections': [],
            'textboxes': [],
            'boundaries': []
        }
        
        # Save devices
        for item in scene.items():
            try:
                # Check if it's a device
                if hasattr(item, 'device_type') and hasattr(item, 'properties'):
                    device_data = {
                        'type': item.device_type,
                        'x': item.pos().x(),
                        'y': item.pos().y(),
                        'properties': item.properties
                    }
                    topology_data['devices'].append(device_data)
                
                # Check if it's a connection
                elif hasattr(item, 'connection_type') and hasattr(item, 'source_device') and hasattr(item, 'target_device'):
                    # Ensure source and target device have id properties
                    source_id = item.source_device.properties.get('id') if hasattr(item.source_device, 'properties') else None
                    target_id = item.target_device.properties.get('id') if hasattr(item.target_device, 'properties') else None
                    
                    if source_id and target_id:
                        # Get ports safely
                        source_port = getattr(item, 'source_port', None)
                        target_port = getattr(item, 'target_port', None)
                        
                        # Handle dict serialization for ports
                        if source_port and not isinstance(source_port, (dict, str)):
                            source_port = {'name': source_port.get('name', '')} if hasattr(source_port, 'get') else None
                        
                        if target_port and not isinstance(target_port, (dict, str)):
                            target_port = {'name': target_port.get('name', '')} if hasattr(target_port, 'get') else None
                        
                        connection_data = {
                            'source_device_id': source_id,
                            'target_device_id': target_id,
                            'source_port': source_port,
                            'target_port': target_port,
                            'connection_type': item.connection_type,
                            'properties': getattr(item, 'properties', {})
                        }
                        topology_data['connections'].append(connection_data)
                
                # Check if it's a text annotation
                elif isinstance(item, QGraphicsTextItem) and item.parentItem() is None:
                    text_data = {
                        'x': item.pos().x(),
                        'y': item.pos().y(),
                        'text': item.toPlainText(),
                        'font': item.font().toString(),
                        'color': item.defaultTextColor().name()
                    }
                    topology_data['textboxes'].append(text_data)
                
                # Check if it's a boundary
                elif isinstance(item, QGraphicsRectItem) and item.parentItem() is None:
                    # Skip if it's a temporary rectangle or doesn't have the expected attributes
                    if not hasattr(item, 'rect') or not callable(getattr(item, 'rect', None)):
                        continue
                        
                    rect = item.rect()
                    
                    # Try to find an associated label
                    label_text = ""
                    for text_item in scene.items():
                        if isinstance(text_item, QGraphicsTextItem) and text_item.parentItem() is None:
                            # Check if text is positioned just above the rectangle
                            text_pos = text_item.scenePos()
                            rect_pos = item.scenePos()
                            if (abs(text_pos.x() - rect_pos.x()) < 20 and 
                                text_pos.y() < rect_pos.y() and
                                text_pos.y() > rect_pos.y() - 30):
                                label_text = text_item.toPlainText()
                                break
                    
                    # Make sure color methods exist and are callable
                    pen_color = item.pen().color().name() if hasattr(item.pen(), 'color') else "#000000"
                    brush_color = item.brush().color().name() if hasattr(item.brush(), 'color') else "#C8C8FF"
                    brush_alpha = item.brush().color().alpha() if hasattr(item.brush(), 'color') else 50
                    
                    boundary_data = {
                        'x': item.pos().x(),
                        'y': item.pos().y(),
                        'width': rect.width(),
                        'height': rect.height(),
                        'label': label_text,
                        'pen_color': pen_color,
                        'brush_color': brush_color,
                        'brush_alpha': brush_alpha
                    }
                    topology_data['boundaries'].append(boundary_data)
                    
            except Exception as e:
                print(f"Error serializing item: {e}")
                # Continue with next item rather than failing entire serialization
                continue
        
        return topology_data
    
    def save_topology_to_file(self, file_path, topology_data):
        """Save topology data to a file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(topology_data, f, indent=2)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def load_topology_from_file(self, file_path):
        """Load topology data from a file."""
        try:
            with open(file_path, 'r') as f:
                topology_data = json.load(f)
            
            # Validate the basic structure
            if not isinstance(topology_data, dict):
                return None, "Invalid file format: not a JSON object"
                
            # Ensure required sections exist
            for section in ['devices', 'connections', 'textboxes', 'boundaries']:
                if section not in topology_data:
                    topology_data[section] = []
                elif not isinstance(topology_data[section], list):
                    topology_data[section] = []
            
            return topology_data, None
        except json.JSONDecodeError:
            return None, "Invalid JSON format in file"
        except Exception as e:
            return None, str(e)