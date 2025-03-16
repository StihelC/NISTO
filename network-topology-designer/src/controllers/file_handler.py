
from models.device import Device

# Find code for saving devices:
def _serialize_devices(self):
    devices_data = []
    for device in self.device_manager.devices.values():
        device_data = {
            'id': device.id,
            'type': device.device_type,
            'name': device.name,
            'x': device.pos().x(),
            'y': device.pos().y(),
            'properties': device.properties
        }
        devices_data.append(device_data)
    return devices_data

# Replace with:
def _serialize_devices(self):
    devices_data = []
    for device in self.device_manager.devices.values():
        devices_data.append(device.to_dict())
    return devices_data

# Find code for loading devices:
def _load_devices(self, devices_data):
    for device_data in devices_data:
        device_type = device_data['type']
        x = device_data['x']
        y = device_data['y']
        device = self.device_manager.create_device(device_type, x, y)
        device.id = device_data['id']
        device.name = device_data['name']
        if 'properties' in device_data:
            device.properties.update(device_data['properties'])

# Replace with:
def _load_devices(self, devices_data):
    for device_data in devices_data:
        device = Device.from_dict(device_data)
        self.device_manager.devices[device.id] = device
        if self.device_manager.scene:
            self.device_manager.scene.addItem(device)