from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QPainterPath
import math

class OrthogonalRouter:
    """
    Utility class to generate orthogonal (right-angled) connection paths
    between network elements.
    """
    
    @staticmethod
    def route(source_point, target_point, source_direction=None, target_direction=None):
        """
        Create an orthogonal route between two points.
        
        Args:
            source_point (QPointF): Starting point of the connection
            target_point (QPointF): Ending point of the connection
            source_direction (str): Direction from source ("top", "right", "bottom", "left")
            target_direction (str): Direction from target ("top", "right", "bottom", "left")
            
        Returns:
            list: List of QPointF points forming the orthogonal path
        """
        points = [source_point]
        
        # If we don't have explicit directions, infer them
        if not source_direction:
            source_direction = OrthogonalRouter._infer_direction(source_point, target_point)
        if not target_direction:
            target_direction = OrthogonalRouter._invert_direction(
                OrthogonalRouter._infer_direction(target_point, source_point)
            )
        
        # Calculate the path based on port directions
        if source_direction == "right" and target_direction == "left":
            # Simple case: ports face each other horizontally
            midpoint_x = (source_point.x() + target_point.x()) / 2
            points.append(QPointF(midpoint_x, source_point.y()))
            points.append(QPointF(midpoint_x, target_point.y()))
            
        elif source_direction == "left" and target_direction == "right":
            # Simple case: ports face each other horizontally
            midpoint_x = (source_point.x() + target_point.x()) / 2
            points.append(QPointF(midpoint_x, source_point.y()))
            points.append(QPointF(midpoint_x, target_point.y()))
            
        elif source_direction == "top" and target_direction == "bottom":
            # Simple case: ports face each other vertically
            midpoint_y = (source_point.y() + target_point.y()) / 2
            points.append(QPointF(source_point.x(), midpoint_y))
            points.append(QPointF(target_point.x(), midpoint_y))
            
        elif source_direction == "bottom" and target_direction == "top":
            # Simple case: ports face each other vertically
            midpoint_y = (source_point.y() + target_point.y()) / 2
            points.append(QPointF(source_point.x(), midpoint_y))
            points.append(QPointF(target_point.x(), midpoint_y))
            
        elif source_direction == "right":
            # Go right, then up/down, then right/left
            offset_x = min(70, abs(target_point.x() - source_point.x()) / 2)
            points.append(QPointF(source_point.x() + offset_x, source_point.y()))
            points.append(QPointF(source_point.x() + offset_x, target_point.y()))
            
        elif source_direction == "left":
            # Go left, then up/down, then right/left
            offset_x = min(70, abs(target_point.x() - source_point.x()) / 2)
            points.append(QPointF(source_point.x() - offset_x, source_point.y()))
            points.append(QPointF(source_point.x() - offset_x, target_point.y()))
            
        elif source_direction == "top":
            # Go up, then right/left, then up/down
            offset_y = min(70, abs(target_point.y() - source_point.y()) / 2)
            points.append(QPointF(source_point.x(), source_point.y() - offset_y))
            points.append(QPointF(target_point.x(), source_point.y() - offset_y))
            
        elif source_direction == "bottom":
            # Go down, then right/left, then up/down
            offset_y = min(70, abs(target_point.y() - source_point.y()) / 2)
            points.append(QPointF(source_point.x(), source_point.y() + offset_y))
            points.append(QPointF(target_point.x(), source_point.y() + offset_y))
            
        else:
            # Default case: simple L-shaped path
            points.append(QPointF(source_point.x(), target_point.y()))
        
        points.append(target_point)
        return points
    
    @staticmethod
    def create_path(source_point, target_point, source_direction=None, target_direction=None):
        """
        Create a QPainterPath for an orthogonal connection.
        
        Args:
            source_point (QPointF): Starting point of the connection
            target_point (QPointF): Ending point of the connection
            source_direction (str): Direction from source
            target_direction (str): Direction from target
            
        Returns:
            QPainterPath: A path for the connection
        """
        points = OrthogonalRouter.route(source_point, target_point, source_direction, target_direction)
        
        path = QPainterPath()
        if points:
            path.moveTo(points[0])
            for i in range(1, len(points)):
                path.lineTo(points[i])
        
        return path
        
    @staticmethod
    def _infer_direction(point_from, point_to):
        """
        Infer the most likely direction from point_from toward point_to.
        """
        dx = point_to.x() - point_from.x()
        dy = point_to.y() - point_from.y()
        
        if abs(dx) > abs(dy):
            # Horizontal direction is dominant
            return "right" if dx > 0 else "left"
        else:
            # Vertical direction is dominant
            return "bottom" if dy > 0 else "top"
            
    @staticmethod
    def _invert_direction(direction):
        """
        Return the opposite direction.
        """
        if direction == "top":
            return "bottom"
        elif direction == "bottom":
            return "top"
        elif direction == "left":
            return "right"
        elif direction == "right":
            return "left"
        return direction