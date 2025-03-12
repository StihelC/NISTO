from PyQt5.QtWidgets import QGraphicsScene

class TopologyScene(QGraphicsScene):
    def drawBackground(self, painter, rect):
        # This is likely where the grid is being drawn
        # MODIFY THIS METHOD to remove the grid drawing code
        
        # Just fill with background color
        painter.fillRect(rect, self.backgroundBrush())
        
        # Remove or comment out any code that draws lines or grid