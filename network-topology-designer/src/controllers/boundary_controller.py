from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QDialog
from PyQt5.QtCore import QObject, QRectF, Qt
from PyQt5.QtGui import QPen, QBrush, QColor
from utils.debug_log import debug
from models.device import Device
import uuid

# Import BoundaryItem - adjust the path if needed
from models.boundary_item import BoundaryItem

# Import BoundaryDialog - either use the one you created or define inline
class BoundaryDialog(QDialog):
    # The boundary dialog implementation as shown previously
    def __init__(self, parent=None):
        super().__init__(parent)
        # Placeholder for dialog implementation
        
    def get_boundary_properties(self):
        # Return default properties
        return {
            "name": "Boundary",
            "type": "Default",
            "color": QColor(200, 200, 255, 100)
        }

class BoundaryController(QObject):
    """Controller for creating and managing boundary regions."""
    
    def __init__(self, parent=None, scene=None, view=None):
        """Initialize the boundary controller."""
        super().__init__()
        self.parent = parent
        self.scene = scene
        self.view = view
        self.is_active = False
        self.start_point = None
        self.temp_boundary = None
        self.boundaries = {}  # Dictionary of boundaries by ID
        debug("BoundaryController initialized")
    
    def set_scene_and_view(self, scene, view):
        """Set scene and view references."""
        debug("BoundaryController: setting scene and view")
        self.scene = scene
        self.view = view
    
    def activate(self):
        """Activate boundary drawing mode."""
        debug("BoundaryController: ACTIVATING")
        self.is_active = True
        
        # Set cursor
        if self.view:
            self.view.setCursor(Qt.CrossCursor)
            debug("BoundaryController: cursor set to CrossCursor")
        else:
            debug("BoundaryController: WARNING - view is None, can't set cursor")
    
    def deactivate(self):
        """Deactivate boundary drawing mode."""
        debug("BoundaryController: DEACTIVATING")
        self.is_active = False
        
        # Reset cursor
        if self.view:
            self.view.setCursor(Qt.ArrowCursor)
    
    def handle_mouse_press(self, event):
        """Handle mouse press for boundary drawing."""
        debug(f"BoundaryController.handle_mouse_press - is_active: {self.is_active}")
        
        if not self.is_active:
            return False
        
        # Get press position
        pos = event.scenePos()
        debug(f"Starting boundary at {pos.x()}, {pos.y()}")
        
        # Store start point
        self.start_point = pos
        
        # Create temporary boundary rectangle
        rect = QRectF(pos, pos)
        self.temp_boundary = QGraphicsRectItem(rect)
        self.temp_boundary.setPen(QPen(Qt.black, 1, Qt.DashLine))
        self.temp_boundary.setBrush(QBrush(QColor(200, 200, 255, 50)))
        
        # Add to scene
        if self.scene:
            debug(f"Adding temp rectangle to scene: {self.scene}")
            self.scene.addItem(self.temp_boundary)
        else:
            debug("ERROR: Scene is None, can't add temporary boundary")
        
        return True
    
    def handle_mouse_move(self, event):
        """Handle mouse move for boundary drawing."""
        if not self.is_active or not self.start_point or not self.temp_boundary:
            return False
        
        # Update rectangle size
        current_pos = event.scenePos()
        rect = QRectF(self.start_point, current_pos).normalized()
        self.temp_boundary.setRect(rect)
        
        return True
    
    def handle_mouse_release(self, event):
        """Handle mouse release for boundary drawing."""
        debug(f"BoundaryController.handle_mouse_release - is_active: {self.is_active}")
        
        if not self.is_active or not self.start_point or not self.temp_boundary:
            debug("Not in active drawing state")
            return False
        
        # Get final rectangle
        end_point = event.scenePos()
        debug(f"Ending boundary at {end_point.x()}, {end_point.y()}")
        
        rect = QRectF(self.start_point, end_point).normalized()
        debug(f"Final rect: {rect.width()}x{rect.height()} at ({rect.x()}, {rect.y()})")
        
        # Remove temporary rectangle
        if self.scene:
            debug("Removing temporary boundary")
            self.scene.removeItem(self.temp_boundary)
        self.temp_boundary = None
        
        # Create final boundary if large enough
        if rect.width() > 20 and rect.height() > 20:
            debug("Rectangle large enough, creating boundary")
            self.create_boundary(rect)
        else:
            debug(f"Rectangle too small ({rect.width()}x{rect.height()}), ignoring")
        
        # Reset state
        self.start_point = None
        
        return True
    
    def create_boundary(self, rect):
        """Create a boundary with the given rectangle."""
        try:
            # Show dialog to get boundary properties
            dialog = BoundaryDialog(self.parent)
            result = dialog.exec_()
            
            if result:  # Just check for truthy value instead of comparing to QDialog.Accepted
                # Get properties from dialog
                props = dialog.get_boundary_properties()
                
                # Create the boundary item
                boundary = BoundaryItem(
                    rect, 
                    name=props["name"],
                    boundary_type=props["type"],
                    color=props["color"]
                )
                
                # Add to scene
                if self.scene:
                    self.scene.addItem(boundary)
                    print(f"Added boundary to scene: {props['name']} ({props['type']})")
                else:
                    print("WARNING: No scene available to add boundary")
                
                # Add to collection
                self.boundaries[boundary.id] = boundary
                return boundary
            
            return None
        except Exception as e:
            print(f"Error creating boundary: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_devices_in_boundary(self, boundary):
        devices = []
        for item in self.scene.items():
            if isinstance(item, Device) and boundary.contains(item.sceneBoundingRect()):
                devices.append(item)
        return devices

    def get_routers_in_boundary(self, boundary):
        return [d for d in self.get_devices_in_boundary(boundary) if d.device_type == Device.ROUTER]