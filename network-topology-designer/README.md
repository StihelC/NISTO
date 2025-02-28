# NISTO - Network Topology Designer

A powerful, intuitive application for designing, visualizing, and documenting computer network topologies. This tool allows network engineers, students, and IT professionals to create detailed network diagrams with ease.

![Network Topology Designer Screenshot](assets/screenshots/main_interface.png)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Technical Implementation](#technical-implementation)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Overview

Network Topology Designer is a cross-platform desktop application that provides a simple yet powerful interface for creating network diagrams. Whether you're planning a new network deployment, documenting an existing infrastructure, or teaching network concepts, this tool offers the flexibility and features you need.

## Features

- **Intuitive Drag-and-Drop Interface**: Easily place and position network devices
- **Diverse Device Library**: Built-in support for routers, switches, firewalls, servers, workstations, and more
- **Custom Connections**: Create various connection types with customizable bandwidth and protocol information
- **Export Options**: Save diagrams as PNG, JPG, SVG, or PDF
- **Project Saving**: Save and reload your projects for continued editing
- **Layer Support**: Organize complex networks into logical layers
- **IP Addressing**: Assign and validate IP addressing schemes
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites

- Python 3.7+
- PyQt5
- NetworkX (for topology calculations)

### Setup

1. Clone the repository:
    ```
    git clone https://github.com/yourusername/network-topology-designer.git
    cd network-topology-designer
    ```

2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

3. Run the application:
    ```
    python main.py
    ```

## Usage

### Getting Started

1. Launch the application by running `main.py`
2. Use the toolbar to add devices to your canvas
3. Connect devices by selecting the connection tool and clicking between devices
4. Right-click on devices or connections to configure their properties
5. Save your work using File → Save

### Example Workflows

#### Creating a Simple LAN

1. Add a router as your gateway device
2. Add a switch connected to the router
3. Add several workstations connected to the switch
4. Configure IP addresses for each device
5. Export your diagram as a PNG for documentation

#### Designing a Multi-Site Network

1. Create separate network zones using the grouping feature
2. Add border routers for each zone
3. Connect zones with WAN links
4. Add internal network infrastructure to each zone
5. Document with labels and annotations

## File Structure

```
network-topology-designer/
├── main.py                 # Application entry point
├── requirements.txt        # Project dependencies
├── README.md               # This documentation
├── LICENSE                 # MIT License file
├── assets/                 # Icons and resources
│   ├── icons/              # Device and UI icons
│   └── screenshots/        # Application screenshots
└── src/                    # Source code
     ├── __init__.py         # Package marker
     ├── network_topo.py     # Main UI framework
     ├── main_window.py      # Window controller and event handler
     ├── canvas_controller.py# Drawing area controller
     ├── device.py           # Device class definitions
     ├── device_manager.py   # Device creation and management
     ├── device_dialog.py    # Device configuration dialogs
     ├── file_handler.py     # Save/load functionality
     ├── utils/              # Helper utilities
     │   ├── __init__.py     # Package marker
     │   ├── ip_validator.py # IP address validation
     │   └── config.py       # Application configuration
     └── tests/              # Unit tests
          ├── __init__.py     # Package marker
          └── test_device.py  # Tests for device functionality
```

## Technical Implementation

### Core Components

#### Main Application (`main.py`)
The entry point for the application. Initializes the PyQt5 application and launches the main window.

#### User Interface (`network_topo.py`)
Builds the application interface including menus, toolbars, status bar, and the main drawing canvas. Implements the visual framework using PyQt5 widgets.

#### Application Controller (`main_window.py`)
Manages application state and coordinates between user interactions and the underlying data model. Handles events from the UI and executes the appropriate actions.

### Device Management System

#### Device Classes (`device.py`)
Defines the base Device class and specialized subclasses (Router, Switch, Server, etc.). Each device class encapsulates:
- Visual representation
- Configuration parameters
- Connectivity rules
- Behavioral characteristics

#### Device Manager (`device_manager.py`)
Factory and registry for all devices in the network topology:
- Creates device instances
- Maintains device inventory
- Handles device selection and grouping
- Manages device relationships

#### Canvas Controller (`canvas_controller.py`)
Controls the interactive drawing area:
- Manages the device placement grid
- Handles drag-and-drop operations
- Implements connection drawing logic
- Manages canvas zooming and panning

### Auxiliary Systems

#### Device Configuration Interface (`device_dialog.py`)
Provides modal dialogs for device configuration:
- Name and type selection
- IP address configuration
- Interface settings
- Custom property management

#### File Operations (`file_handler.py`)
Implements project persistence and export functionality:
- Custom file format (.nettopo) for saving projects
- Import/export capabilities for various image formats
- Project validation and error handling

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows our coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [PyQt5](https://riverbankcomputing.com/software/pyqt/intro) for the GUI framework
- [NetworkX](https://networkx.org/) for graph algorithms
- All contributors who have helped shape this project

---

**Note:** This application is designed for educational and planning purposes. Network implementation should always be verified by qualified network engineers.