from PyQt5.QtWidgets import QAction

class ActionManager:
    """Manages UI action connections."""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.ui = main_window.ui
        
    def connect_actions(self):
        """Connect all UI actions to their handlers."""
        try:
            self._connect_file_actions()
            self._connect_edit_actions()
            self._connect_view_actions()
            self._connect_mode_actions()
        except Exception as e:
            print(f"Error connecting actions: {e}")
            import traceback
            traceback.print_exc()
    
    def _connect_file_actions(self):
        """Connect file menu actions."""
        if hasattr(self.ui, 'actionSave'):
            self.ui.actionSave.triggered.connect(self.main_window.save_topology)
        if hasattr(self.ui, 'actionLoad'):
            self.ui.actionLoad.triggered.connect(self.main_window.load_topology)
        if hasattr(self.ui, 'actionSave_as_PNG'):
            self.ui.actionSave_as_PNG.triggered.connect(self.main_window.export_as_png)
    
    def _connect_view_actions(self):
        """Connect view menu actions."""
        if hasattr(self.ui, 'actionZoom_In'):
            self.ui.actionZoom_In.triggered.connect(self.main_window.zoom_in)
        if hasattr(self.ui, 'actionZoom_Out'):
            self.ui.actionZoom_Out.triggered.connect(self.main_window.zoom_out)
        if hasattr(self.ui, 'actionDefault_View'):
            self.ui.actionDefault_View.triggered.connect(self.main_window.reset_view)
    
    def _connect_mode_actions(self):
        """Connect mode-switching actions."""
        # Connect device add action
        self._connect_action_by_name_or_text(
            ['actionAdd_Device', 'actionAddDevice'],
            "add device",
            self.main_window.set_add_device_mode
        )
        
        # Connect connection add action
        self._connect_action_by_name_or_text(
            ['actionAdd_Connection', 'actionAddConnection'],
            "add connection",
            self.main_window.set_add_connection_mode
        )
        
        # Connect selection mode action
        self._connect_action_by_name_or_text(
            ['actionSelect_Mode', 'actionSelect', 'action_Select'],
            "select",
            self.main_window.set_selection_mode,
            exclude_text="all"
        )
    
    def _connect_action_by_name_or_text(self, name_list, text_contains, callback, exclude_text=None):
        """Connect an action by its name or text content."""
        # Try direct name access
        for name in name_list:
            if hasattr(self.ui, name):
                getattr(self.ui, name).triggered.connect(callback)
                print(f"Connected {name}")
                return True
                
        # Fallback to text search
        for action in self.main_window.findChildren(QAction):
            action_text = action.text().lower()
            if text_contains in action_text:
                if exclude_text and exclude_text in action_text:
                    continue
                action.triggered.connect(callback)
                print(f"Connected {action.objectName()} via text match")
                return True
                
        print(f"WARNING: Could not find action containing '{text_contains}'")
        return False