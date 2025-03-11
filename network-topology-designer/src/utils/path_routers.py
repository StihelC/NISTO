from PyQt5.QtGui import QPainterPath
from PyQt5.QtCore import QPointF

class OrthogonalRouter:
    """Routes connections using only horizontal and vertical segments."""
    
    def create_path(self, source_point, target_point):
        """Create an orthogonal path between two points."""
        path = QPainterPath()
        
        # Start at source point
        path.moveTo(source_point)
        
        # Calculate midpoint for the orthogonal path
        mid_x = (source_point.x() + target_point.x()) / 2
        mid_y = (source_point.y() + target_point.y()) / 2
        
        # Create the orthogonal path with 90-degree angles
        # Horizontal first, then vertical
        path.lineTo(mid_x, source_point.y())  # Horizontal segment
        path.lineTo(mid_x, target_point.y())  # Vertical segment
        path.lineTo(target_point)  # Final horizontal segment
        
        return path

class ManhattanRouter(OrthogonalRouter):
    """Advanced orthogonal router with smarter path finding."""
    
    def create_path(self, source_point, target_point):
        """Create a Manhattan-style path between points."""
        path = QPainterPath()
        path.moveTo(source_point)
        
        # Determine if we should go horizontal or vertical first
        dx = abs(target_point.x() - source_point.x())
        dy = abs(target_point.y() - source_point.y())
        
        if dx > dy:
            # Go horizontal first
            path.lineTo((source_point.x() + target_point.x()) / 2, source_point.y())
            path.lineTo((source_point.x() + target_point.x()) / 2, target_point.y())
        else:
            # Go vertical first
            path.lineTo(source_point.x(), (source_point.y() + target_point.y()) / 2)
            path.lineTo(target_point.x(), (source_point.y() + target_point.y()) / 2)
        
        path.lineTo(target_point)
        return path