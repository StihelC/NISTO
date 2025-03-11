from PyQt5.QtCore import QPointF, QObject, pyqtSignal

class Command:
    """Base class for all undoable commands."""
    
    def __init__(self, description=""):
        """Initialize the command."""
        self.description = description
    
    def execute(self):
        """Execute the command."""
        raise NotImplementedError("Command subclasses must implement execute()")
    
    def undo(self):
        """Undo the command."""
        raise NotImplementedError("Command subclasses must implement undo()")


class AddDeviceCommand(Command):
    """Command to add a device to the scene."""
    
    def __init__(self, device_manager, device_type, position, properties=None):
        """Initialize the add device command."""
        super().__init__(f"Add {device_type}")
        self.device_manager = device_manager
        self.device_type = device_type
        self.position = position
        self.properties = properties or {}
        self.device = None  # Will be set when executed
    
    def execute(self):
        """Execute the command to add a device."""
        self.device = self.device_manager.create_device(
            self.device_type,
            self.position.x(),
            self.position.y()
        )
        
        if self.properties:
            self.device.properties.update(self.properties)
            
        return self.device
    
    def undo(self):
        """Undo the command by removing the device."""
        if self.device:
            self.device_manager.remove_device(self.device)
            self.device = None


class RemoveDeviceCommand(Command):
    """Command to remove a device from the scene."""
    
    def __init__(self, device_manager, device):
        """Initialize the remove device command."""
        super().__init__(f"Remove {device.properties.get('name', 'device')}")
        self.device_manager = device_manager
        self.device = device
        self.device_type = device.device_type
        self.position = device.pos()
        self.properties = device.properties.copy()
        self.connections = []  # Will store connected items
    
    def execute(self):
        """Execute the command to remove a device."""
        # Store connections for later restoration
        connection_manager = self.device_manager.connection_manager
        if connection_manager:
            self.connections = connection_manager.get_connections_for_device(self.device)
            # For each connection, store enough info to recreate it
            self.connection_data = []
            for conn in self.connections:
                is_source = conn.source_device == self.device
                other_device = conn.target_device if is_source else conn.source_device
                source_port = conn.source_port
                target_port = conn.target_port
                conn_type = conn.connection_type
                properties = conn.properties.copy()
                
                self.connection_data.append({
                    'is_source': is_source,
                    'other_device': other_device,
                    'source_port': source_port,
                    'target_port': target_port,
                    'connection_type': conn_type,
                    'properties': properties
                })
        
        # Remove the device
        self.device_manager.remove_device(self.device)
    
    def undo(self):
        """Undo the command by adding the device back."""
        # Recreate the device
        self.device = self.device_manager.create_device(
            self.device_type,
            self.position.x(),
            self.position.y()
        )
        
        # Restore properties
        self.device.properties = self.properties.copy()
        
        # Restore connections
        connection_manager = self.device_manager.connection_manager
        if connection_manager and hasattr(self, 'connection_data'):
            for conn_data in self.connection_data:
                other_device = conn_data['other_device']
                
                # Determine which device is source/target
                if conn_data['is_source']:
                    source_device = self.device
                    target_device = other_device
                    source_port = conn_data['source_port']
                    target_port = conn_data['target_port']
                else:
                    source_device = other_device
                    target_device = self.device
                    source_port = conn_data['source_port']
                    target_port = conn_data['target_port']
                
                # Recreate the connection
                conn = connection_manager.create_connection(
                    source_device,
                    target_device,
                    source_port,
                    target_port,
                    conn_data['connection_type']
                )
                
                # Restore connection properties
                if conn:
                    conn.properties = conn_data['properties'].copy()


class MoveDeviceCommand(Command):
    """Command to move a device in the scene."""
    
    def __init__(self, device, old_position, new_position):
        """Initialize the move device command."""
        super().__init__(f"Move {device.properties.get('name', 'device')}")
        self.device = device
        self.old_position = old_position
        self.new_position = new_position
    
    def execute(self):
        """Execute the command to move the device."""
        self.device.setPos(self.new_position)
    
    def undo(self):
        """Undo the command by moving the device back."""
        self.device.setPos(self.old_position)


class AddConnectionCommand(Command):
    """Command to add a connection between devices."""
    
    def __init__(self, connection_manager, source_device, target_device, 
                 source_port=None, target_port=None, connection_type="ethernet"):
        """Initialize the add connection command."""
        super().__init__("Add connection")
        self.connection_manager = connection_manager
        self.source_device = source_device
        self.target_device = target_device
        self.source_port = source_port
        self.target_port = target_port
        self.connection_type = connection_type
        self.connection = None  # Will be set when executed
    
    def execute(self):
        """Execute the command to add a connection."""
        self.connection = self.connection_manager.create_connection(
            self.source_device,
            self.target_device,
            self.source_port,
            self.target_port,
            self.connection_type
        )
        return self.connection
    
    def undo(self):
        """Undo the command by removing the connection."""
        if self.connection:
            self.connection_manager.remove_connection(self.connection)
            self.connection = None


class RemoveConnectionCommand(Command):
    """Command to remove a connection."""
    
    def __init__(self, connection_manager, connection):
        """Initialize the remove connection command."""
        super().__init__("Remove connection")
        self.connection_manager = connection_manager
        self.connection = connection
        
        # Store connection data
        self.source_device = connection.source_device
        self.target_device = connection.target_device
        self.source_port = connection.source_port
        self.target_port = connection.target_port
        self.connection_type = connection.connection_type
        self.properties = connection.properties.copy()
    
    def execute(self):
        """Execute the command to remove a connection."""
        self.connection_manager.remove_connection(self.connection)
        self.connection = None  # Mark as removed
    
    def undo(self):
        """Undo the command by adding the connection back."""
        self.connection = self.connection_manager.create_connection(
            self.source_device,
            self.target_device,
            self.source_port,
            self.target_port,
            self.connection_type
        )
        
        if self.connection:
            self.connection.properties = self.properties.copy()


class AddTextCommand(Command):
    """Command to add text to the scene."""
    
    def __init__(self, scene, position, text="New Text"):
        """Initialize the add text command."""
        super().__init__("Add text")
        self.scene = scene
        self.position = position
        self.text = text
        self.text_item = None  # Will be set when executed
    
    def execute(self):
        """Execute the command to add text."""
        from PyQt5.QtWidgets import QGraphicsTextItem
        from PyQt5.QtGui import QFont
        
        self.text_item = QGraphicsTextItem(self.text)
        self.text_item.setPos(self.position)
        font = QFont()
        font.setPointSize(10)
        self.text_item.setFont(font)
        self.scene.addItem(self.text_item)
        return self.text_item
    
    def undo(self):
        """Undo the command by removing the text."""
        if self.text_item:
            self.scene.removeItem(self.text_item)
            self.text_item = None


class AddBoundaryCommand(Command):
    """Command to add a boundary area to the scene."""
    
    def __init__(self, scene, rect, label="Boundary", color=None):
        """Initialize the add boundary command."""
        super().__init__("Add boundary")
        self.scene = scene
        self.rect = rect
        self.label = label
        self.color = color
        self.boundary_item = None  # Will be set when executed
        self.label_item = None     # Will be set when executed
    
    def execute(self):
        """Execute the command to add a boundary."""
        from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
        from PyQt5.QtGui import QPen, QBrush, QColor
        from PyQt5.QtCore import Qt
        
        # Create boundary rectangle
        self.boundary_item = QGraphicsRectItem(self.rect)
        self.boundary_item.setPen(QPen(Qt.black, 1, Qt.DashLine))
        
        # Set color
        color = self.color if self.color else QColor(200, 200, 255, 50)
        self.boundary_item.setBrush(QBrush(color))
        
        # Add to scene
        self.scene.addItem(self.boundary_item)
        
        # Create label
        self.label_item = QGraphicsTextItem(self.label)
        self.label_item.setPos(self.rect.topLeft().x(), self.rect.topLeft().y() - 20)
        self.scene.addItem(self.label_item)
        
        return self.boundary_item, self.label_item
    
    def undo(self):
        """Undo the command by removing the boundary."""
        if self.boundary_item:
            self.scene.removeItem(self.boundary_item)
            self.boundary_item = None
        
        if self.label_item:
            self.scene.removeItem(self.label_item)
            self.label_item = None


class EditPropertiesCommand(Command):
    """Command to edit properties of an item."""
    
    def __init__(self, item, old_properties, new_properties):
        """Initialize the edit properties command."""
        super().__init__("Edit properties")
        self.item = item
        self.old_properties = old_properties.copy()
        self.new_properties = new_properties.copy()
    
    def execute(self):
        """Execute the command to edit properties."""
        self.item.properties = self.new_properties.copy()
        
        # Update visual representation if needed
        if hasattr(self.item, "update_visual"):
            self.item.update_visual()
        elif hasattr(self.item, "update_appearance"):
            self.item.update_appearance()
    
    def undo(self):
        """Undo the command by restoring old properties."""
        self.item.properties = self.old_properties.copy()
        
        # Update visual representation if needed
        if hasattr(self.item, "update_visual"):
            self.item.update_visual()
        elif hasattr(self.item, "update_appearance"):
            self.item.update_appearance()


class UndoRedoManager(QObject):
    """Manages undo and redo operations."""
    
    # Signals
    undoAvailable = pyqtSignal(bool)
    redoAvailable = pyqtSignal(bool)
    commandExecuted = pyqtSignal(Command)
    commandUndone = pyqtSignal(Command)
    commandRedone = pyqtSignal(Command)
    
    def __init__(self, main_window=None):
        """Initialize the undo/redo manager."""
        super().__init__()
        self.main_window = main_window
        
        # Command stacks
        self.undo_stack = []
        self.redo_stack = []
        
        # Maximum stack size
        self.max_stack_size = 100
    
    def execute_command(self, command):
        """Execute a command and add it to the undo stack."""
        # Execute the command
        result = command.execute()
        
        # Add to undo stack
        self.undo_stack.append(command)
        
        # Clear redo stack
        self.redo_stack.clear()
        
        # Enforce stack size limit
        if len(self.undo_stack) > self.max_stack_size:
            self.undo_stack.pop(0)
        
        # Emit signals
        self.undoAvailable.emit(len(self.undo_stack) > 0)
        self.redoAvailable.emit(False)
        self.commandExecuted.emit(command)
        
        # Update status if main window exists
        if self.main_window:
            self.main_window.statusBar().showMessage(f"Action: {command.description}", 3000)
        
        return result
    
    def undo(self):
        """Undo the last command."""
        if not self.undo_stack:
            return False
        
        # Pop the last command from the undo stack
        command = self.undo_stack.pop()
        
        # Undo the command
        command.undo()
        
        # Add to redo stack
        self.redo_stack.append(command)
        
        # Emit signals
        self.undoAvailable.emit(len(self.undo_stack) > 0)
        self.redoAvailable.emit(True)
        self.commandUndone.emit(command)
        
        # Update status if main window exists
        if self.main_window:
            self.main_window.statusBar().showMessage(f"Undone: {command.description}", 3000)
        
        return True
    
    def redo(self):
        """Redo the last undone command."""
        if not self.redo_stack:
            return False
        
        # Pop the last command from the redo stack
        command = self.redo_stack.pop()
        
        # Execute the command again
        command.execute()
        
        # Add back to undo stack
        self.undo_stack.append(command)
        
        # Emit signals
        self.undoAvailable.emit(True)
        self.redoAvailable.emit(len(self.redo_stack) > 0)
        self.commandRedone.emit(command)
        
        # Update status if main window exists
        if self.main_window:
            self.main_window.statusBar().showMessage(f"Redone: {command.description}", 3000)
        
        return True
    
    def can_undo(self):
        """Check if undo is available."""
        return len(self.undo_stack) > 0
    
    def can_redo(self):
        """Check if redo is available."""
        return len(self.redo_stack) > 0
    
    def clear(self):
        """Clear both undo and redo stacks."""
        self.undo_stack.clear()
        self.redo_stack.clear()
        
        # Emit signals
        self.undoAvailable.emit(False)
        self.redoAvailable.emit(False)
    
    def get_undo_text(self):
        """Get description of the command that would be undone."""
        if self.undo_stack:
            return f"Undo {self.undo_stack[-1].description}"
        return "Undo"
    
    def get_redo_text(self):
        """Get description of the command that would be redone."""
        if self.redo_stack:
            return f"Redo {self.redo_stack[-1].description}"
        return "Redo"