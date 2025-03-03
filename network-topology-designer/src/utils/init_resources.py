import os
import urllib.request
import shutil

def init_resources():
    """Initialize all resources for the application."""
    print("Initializing resources...")
    
    # Create resource directories
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon_dir = os.path.join(base_dir, "resources", "device_icons")
    
    os.makedirs(icon_dir, exist_ok=True)
    
    # Check for device icons and download if missing
    download_default_icons(icon_dir)
    
    # List all resources
    print("Resources initialized. Available files:")
    for root, dirs, files in os.walk(os.path.join(base_dir, "resources")):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), base_dir)
            print(f" - {rel_path}")

def download_default_icons(icon_dir):
    """Download default device icons if they don't exist."""
    # Define default icons to download
    default_icons = {
        "router": "https://raw.githubusercontent.com/cisco-icons/cisco-icons/master/symbols_svg/router_solid.svg",
        "switch": "https://raw.githubusercontent.com/cisco-icons/cisco-icons/master/symbols_svg/switch_solid.svg",
        "server": "https://raw.githubusercontent.com/cisco-icons/cisco-icons/master/symbols_svg/server_solid.svg",
        "firewall": "https://raw.githubusercontent.com/cisco-icons/cisco-icons/master/symbols_svg/firewall_solid.svg",
        "workstation": "https://raw.githubusercontent.com/cisco-icons/cisco-icons/master/symbols_svg/pc_solid.svg",
        "cloud": "https://raw.githubusercontent.com/cisco-icons/cisco-icons/master/symbols_svg/cloud_solid.svg",
        "wireless": "https://raw.githubusercontent.com/cisco-icons/cisco-icons/master/symbols_svg/wireless_solid.svg",
        "database": "https://raw.githubusercontent.com/cisco-icons/cisco-icons/master/symbols_svg/database_solid.svg"
    }
    
    # Local fallback icons path
    local_fallback_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                     "resources", "fallback_icons")
                                     
    # Download each icon if it doesn't exist
    for device_type, url in default_icons.items():
        icon_path = os.path.join(icon_dir, f"{device_type}.png")
        
        # Skip if the icon already exists
        if os.path.exists(icon_path):
            print(f"Icon already exists: {device_type}")
            continue
            
        print(f"Attempting to download icon for {device_type}...")
        
        # Try downloading from URL
        try:
            # Download and save
            urllib.request.urlretrieve(url, icon_path)
            print(f"Downloaded {device_type} icon from {url}")
        except Exception as e:
            print(f"Failed to download {device_type} icon: {e}")
            
            # Try copying from fallback location
            fallback_path = os.path.join(local_fallback_dir, f"{device_type}.png")
            if os.path.exists(fallback_path):
                try:
                    shutil.copy(fallback_path, icon_path)
                    print(f"Copied fallback icon for {device_type}")
                except Exception as e2:
                    print(f"Failed to copy fallback icon: {e2}")