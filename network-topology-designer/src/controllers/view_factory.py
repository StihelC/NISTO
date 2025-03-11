from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QToolBar, QAction, 
    QMenu, QMenuBar, QStatusBar, QDockWidget, QVBoxLayout,
    QWidget, QLabel, QPushButton, QComboBox, QLineEdit
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPainter

class ViewFactory:
    """Factory class for creating UI components.
    
    Following SRP, this class has the single responsibility of creating
    UI components without handling their behavior.
    """
    
    @staticmethod
    def create_graphics_view():
        """Create and configure a QGraphicsView for the network topology."""
        view = QGraphicsView()
        view.setRenderHint(QPainter.Antialiasing)
        view.setDragMode(QGraphicsView.RubberBandDrag)
        view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        return view
    
    @staticmethod
    def create_graphics_scene():
        """Create and configure a QGraphicsScene."""
        scene = QGraphicsScene()
        scene.setSceneRect(-5000, -5000, 10000, 10000)
        return scene
    
    @staticmethod
    def create_menu_bar(parent):
        """Create the main menu bar."""
        menu_bar = QMenuBar(parent)
        return menu_bar
    
    @staticmethod
    def create_file_menu(parent, menu_bar):
        """Create the file menu and its actions."""
        file_menu = QMenu("&File", parent)
        menu_bar.addMenu(file_menu)
        
        # Create actions
        new_action = QAction("&New", parent)
        open_action = QAction("&Open", parent)
        save_action = QAction("&Save", parent)
        save_as_action = QAction("Save &As", parent)
        export_action = QAction("&Export", parent)
        
        # Add to menu
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(export_action)
        
        return {
            "menu": file_menu,
            "actions": {
                "new": new_action,
                "open": open_action,
                "save": save_action,
                "save_as": save_as_action,
                "export": export_action
            }
        }
    
    @staticmethod
    def create_edit_menu(parent, menu_bar):
        """Create the edit menu and its actions."""
        edit_menu = QMenu("&Edit", parent)
        menu_bar.addMenu(edit_menu)
        
        # Create actions
        undo_action = QAction("&Undo", parent)
        redo_action = QAction("&Redo", parent)
        cut_action = QAction("Cu&t", parent)
        copy_action = QAction("&Copy", parent)
        paste_action = QAction("&Paste", parent)
        delete_action = QAction("&Delete", parent)
        
        # Add to menu
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addSeparator()