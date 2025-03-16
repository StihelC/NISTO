from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QPen, QBrush, QFont, QColor
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
import uuid

class BoundaryItem(QGraphicsItemGroup):
    """A boundary region that can contain devices."""
    
    # Signals
    selection_changed = pyqtSignal(object, bool)
    
    def __init__(self, rect, name="Boundary", boundary_type="area", color=None):
        """Initialize a boundary item."""
        super().__init__()
        
        # Generate a unique ID
        self.id = str(uuid.uuid4())[:8]
        
        # Store properties
        self.name = name
        self.boundary_type = boundary_type
        self.rect = QRectF(rect)  # Make sure it's a QRectF
        
        # Set default color if none provided
        if color is None:
            color = QColor(200, 200, 255, 100)  # Light blue with transparency
        self.color = color
        
        # Set flags
        self.setFlag(QGraphicsItemGroup.ItemIsSelectable, True)
        self.setFlag(QGraphicsItemGroup.ItemIsMovable, True)
        self.setFlag(QGraphicsItemGroup.ItemSendsGeometryChanges, True)
        
        # Create visual components
        self._create_visual()
    
    def _create_visual(self):
        """Create the visual representation of the boundary."""
        try:
            # Create the background rectangle
            self.rect_item = QGraphicsRectItem(self.rect)
            self.rect_item.setPen(QPen(self.color.darker(120), 2))
            self.rect_item.setBrush(QBrush(self.color))
            self.addToGroup(self.rect_item)
            
            # Create the name label
            self.name_item = QGraphicsTextItem(self.name)
            font = QFont()
            font.setPointSize(10)
            font.setBold(True)
            self.name_item.setFont(font)
            self.name_item.setPos(self.rect.x() + 10, self.rect.y() + 10)
            self.addToGroup(self.name_item)
            
            # Create type label
            self.type_item = QGraphicsTextItem(f"Type: {self.boundary_type}")
            type_font = QFont()
            type_font.setPointSize(8)
            self.type_item.setFont(type_font)
            self.type_item.setPos(self.rect.x() + 10, self.rect.y() + 35)
            self.addToGroup(self.type_item)
            
        except Exception as e:
            print(f"Error creating boundary visual: {e}")
            import traceback
            traceback.print_exc()
    
    def itemChange(self, change, value):
        """Handle item changes like selection and position."""
        if change == QGraphicsItemGroup.ItemSelectedChange:
            # Handle selection change
            if value and hasattr(self, 'selection_changed'):
                # Add selection indicator if needed
                self.rect_item.setPen(QPen(Qt.blue, 2, Qt.DashLine))
            else:
                # Remove selection indicator
                self.rect_item.setPen(QPen(self.color.darker(120), 2))
            
            # Emit signal
            if hasattr(self, 'selection_changed'):
                self.selection_changed.emit(self, bool(value))
        
        return super().itemChange(change, value)
    
    def contains_point(self, scene_pos):
        """Check if the boundary contains the given scene position."""
        item_pos = self.mapFromScene(scene_pos)
        return self.rect_item.contains(item_pos)
    
    def get_contained_items(self, scene):
        """Get all items contained within this boundary."""
        items = []
        for item in scene.items():
            if item != self and item not in self.childItems():
                if self.contains_point(item.scenePos()):
                    items.append(item)
        return items
    
    def update_name(self, name):
        """Update the boundary name."""
        self.name = name
        self.name_item.setPlainText(name)
    
    def update_type(self, boundary_type):
        """Update the boundary type."""
        self.boundary_type = boundary_type
        self.type_item.setPlainText(f"Type: {boundary_type}")
    
    def update_color(self, color):
        """Update the boundary color."""
        self.color = color
        self.rect_item.setPen(QPen(color.darker(120), 2))
        self.rect_item.setBrush(QBrush(color))
    
    def to_dict(self):
        """Convert boundary to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.boundary_type,
            'x': self.rect.x(),
            'y': self.rect.y(),
            'width': self.rect.width(),
            'height': self.rect.height(),
            'color': {
                'r': self.color.red(),
                'g': self.color.green(),
                'b': self.color.blue(),
                'a': self.color.alpha()
            }
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create boundary from dictionary (deserialization)."""
        rect = QRectF(data['x'], data['y'], data['width'], data['height'])
        color_data = data.get('color', {'r': 200, 'g': 200, 'b': 255, 'a': 100})
        color = QColor(color_data['r'], color_data['g'], color_data['b'], color_data['a'])
        
        boundary = cls(rect, data['name'], data['type'], color)
        boundary.id = data.get('id', boundary.id)  # Use existing ID if provided
        
        return boundary