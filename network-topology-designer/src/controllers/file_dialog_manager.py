from PyQt5.QtWidgets import QFileDialog

class FileDialogManager:
    """Manages file dialogs for opening and saving files."""
    
    def __init__(self, parent_widget):
        """Initialize the file dialog manager."""
        self.parent_widget = parent_widget
        self.current_file_path = None
    
    def get_save_path(self, title="Save File", default_dir="", file_filter="All Files (*)", extension=None, force_dialog=False):
        """Get a path for saving a file."""
        if not force_dialog and self.current_file_path:
            return self.current_file_path, True
        
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent_widget,
            title,
            default_dir,
            file_filter
        )
        
        if not file_path:
            return None, False  # User canceled
        
        # Add extension if specified and not already present
        if extension and not file_path.lower().endswith(extension):
            file_path += extension
        
        self.current_file_path = file_path
        return file_path, True
    
    def get_open_path(self, title="Open File", default_dir="", file_filter="All Files (*)"):
        """Get a path for opening a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent_widget,
            title,
            default_dir,
            file_filter
        )
        
        if not file_path:
            return None, False  # User canceled
        
        self.current_file_path = file_path
        return file_path, True
    
    def get_current_path(self):
        """Get the current file path."""
        return self.current_file_path
    
    def set_current_path(self, path):
        """Set the current file path."""
        self.current_file_path = path