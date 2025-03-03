import os
import sys

def get_resource_path(relative_path):
    """Get absolute path to a resource file.
    
    This function handles different runtime environments:
    - Running from source
    - Running from a PyInstaller package
    - Running from a pip-installed package
    """
    # Check for PyInstaller environment
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        # Get the directory of this script
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Try multiple possible locations
    possible_paths = [
        os.path.join(base_path, relative_path),  # Relative to src
        os.path.join(os.path.dirname(base_path), relative_path),  # Relative to project root
        os.path.join(os.path.dirname(os.path.dirname(base_path)), relative_path),  # Up two levels
        relative_path,  # As provided
    ]
    
    # Return the first path that exists
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # If no file found, print debugging info and return the best guess
    print(f"Resource not found: {relative_path}")
    print(f"Searched paths: {possible_paths}")
    
    # Return the most likely path
    return possible_paths[0]

def list_resources(directory="resources"):
    """List all resource files in the specified directory."""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resource_dir = os.path.join(base_path, directory)
    
    resources = []
    if os.path.exists(resource_dir) and os.path.isdir(resource_dir):
        for root, dirs, files in os.walk(resource_dir):
            rel_path = os.path.relpath(root, base_path)
            for file in files:
                resources.append(os.path.join(rel_path, file))
    
    return resources