"""
Utility functions for locating and managing application resources.
"""
import os
import sys

def get_base_path():
    """Get the base directory of the application."""
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return sys._MEIPASS
    else:
        # We are running in a normal Python environment
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_resource_path(relative_path):
    """
    Get absolute path to a resource, works for dev and for PyInstaller.
    
    Args:
        relative_path (str): Path relative to the resources directory
                             (e.g. "icons/router.png")
                             
    Returns:
        str: Absolute path to the resource
    """
    base_path = get_base_path()
    
    # Check if resources are in the main resources dir
    resources_path = os.path.join(base_path, "resources")
    full_path = os.path.join(resources_path, relative_path)
    
    if os.path.exists(full_path):
        return full_path
    
    # Check if resources are in src/resources
    src_resources_path = os.path.join(base_path, "src", "resources")
    src_full_path = os.path.join(src_resources_path, relative_path)
    
    if os.path.exists(src_full_path):
        return src_full_path
    
    # Return the original path as fallback
    return full_path

def check_resources_exist():
    """
    Check if essential resources exist and report their status.
    
    Returns:
        dict: A dictionary containing resource paths and existence status
    """
    resource_files = {
        "icons": [
            "router.png",
            "switch.png",
            "server.png",
            "firewall.png",
            "workstation.png",
            "cloud.png",
        ],
        "styles": [
            "main.css",
        ]
    }
    
    results = {}
    
    for category, files in resource_files.items():
        category_results = {}
        for filename in files:
            path = get_resource_path(f"{category}/{filename}")
            exists = os.path.exists(path)
            category_results[filename] = {"path": path, "exists": exists}
        results[category] = category_results
    
    return results

def list_resources(directory="resources"):
    """List all resource files in the specified directory."""
    base_path = get_base_path()
    resource_dir = os.path.join(base_path, directory)
    
    resources = []
    if os.path.exists(resource_dir) and os.path.isdir(resource_dir):
        for root, dirs, files in os.walk(resource_dir):
            rel_path = os.path.relpath(root, base_path)
            for file in files:
                resources.append(os.path.join(rel_path, file))
    
    return resources