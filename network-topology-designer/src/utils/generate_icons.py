from src.utils.device_registry import DeviceRegistry

def generate_default_icons():
    """Generate placeholder icons for default device types."""
    registry = DeviceRegistry()
    registry.create_placeholder_icons()
    print("Generated placeholder icons in:", registry.icons_dir)

if __name__ == "__main__":
    generate_default_icons()