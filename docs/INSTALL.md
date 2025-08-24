# MKD Automation - Installation Guide

This comprehensive installation guide will help you set up MKD Automation on your system, whether you're an end user looking to automate tasks or a developer wanting to contribute to the project.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Platform-Specific Setup](#platform-specific-setup)
- [Development Environment](#development-environment)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Upgrading](#upgrading)
- [Uninstallation](#uninstallation)

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+, CentOS 7+) |
| **Python** | Python 3.9 or higher |
| **Memory** | 512 MB RAM |
| **Storage** | 100 MB free space |
| **Display** | 1024x768 resolution |

### Recommended Requirements

| Component | Recommendation |
|-----------|----------------|
| **Python** | Python 3.11+ |
| **Memory** | 2 GB RAM |
| **Storage** | 500 MB free space |
| **Display** | 1920x1080 resolution |
| **Processor** | Multi-core processor for better performance |

### Python Version Compatibility

- **Python 3.9**: Minimum supported version
- **Python 3.10**: Fully supported
- **Python 3.11**: Recommended version
- **Python 3.12**: Latest supported version

Check your Python version:
```bash
python --version
# or
python3 --version
```

## Installation Methods

### Method 1: PyPI Installation (Recommended)

Install the latest stable release from PyPI:

```bash
# Install for current user
pip install mkd-automation

# Install system-wide (may require sudo/admin)
pip install mkd-automation --user

# Install specific version
pip install mkd-automation==0.2.1
```

### Method 2: Development Installation

For developers or users who want the latest features:

```bash
# Clone the repository
git clone https://github.com/yourusername/mkd_automation.git
cd mkd_automation

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e .[dev]
```

### Method 3: Docker Installation

Use Docker for containerized deployment:

```bash
# Pull the official image
docker pull mkdautomation/mkd-automation:latest

# Run with GUI support (Linux with X11)
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd):/workspace \
    mkdautomation/mkd-automation:latest

# For macOS with XQuartz:
docker run -it --rm \
    -e DISPLAY=host.docker.internal:0 \
    -v $(pwd):/workspace \
    mkdautomation/mkd-automation:latest
```

### Method 4: Build from Source

For advanced users who want to build from source:

```bash
# Install build dependencies
pip install build twine

# Clone and build
git clone https://github.com/yourusername/mkd_automation.git
cd mkd_automation

# Build distribution packages
python -m build

# Install built package
pip install dist/mkd_automation-*.whl
```

## Platform-Specific Setup

### Windows Setup

#### Prerequisites
```powershell
# Install Python from Microsoft Store or python.org
# Ensure Python is added to PATH

# Verify installation
python --version
pip --version
```

#### Install MKD Automation
```powershell
# Install from PyPI
pip install mkd-automation

# Install platform-specific dependencies
pip install pywin32 pygetwindow pycaw
```

#### Windows-Specific Configuration
```powershell
# For advanced features, run as administrator occasionally
# This is needed for system-level automation

# Optional: Add to Windows PATH
setx PATH "%PATH%;%USERPROFILE%\AppData\Local\Programs\Python\Python311\Scripts"
```

#### Windows Permissions
- **User Account Control (UAC)**: Some automation features may require elevated privileges
- **Windows Defender**: Add MKD to exclusions if needed
- **Firewall**: Allow Python through Windows Firewall if using network features

### macOS Setup

#### Prerequisites
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python via Homebrew (recommended)
brew install python@3.11

# Or install from python.org
# Download from https://www.python.org/downloads/macos/
```

#### Install MKD Automation
```bash
# Install from PyPI
pip3 install mkd-automation

# Install macOS-specific dependencies
pip3 install pyobjc-core pyobjc-framework-Quartz pyobjc-framework-ApplicationServices
```

#### macOS Permissions Setup

MKD Automation requires accessibility permissions to function properly:

1. **System Preferences** ’ **Security & Privacy** ’ **Privacy** ’ **Accessibility**
2. Click the lock icon and enter your password
3. Click "+" and add:
   - Terminal (if running from terminal)
   - Your Python IDE (PyCharm, VS Code, etc.)
   - The MKD Automation application

#### Additional macOS Setup
```bash
# For screen recording features (optional)
# System Preferences ’ Security & Privacy ’ Privacy ’ Screen Recording
# Add the same applications as above

# Install additional tools (optional)
brew install --cask rectangle  # Window management
brew install --cask karabiner-elements  # Key remapping
```

### Linux Setup

#### Ubuntu/Debian Setup
```bash
# Update package index
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv

# Install system dependencies
sudo apt install python3-dev build-essential

# Install X11 development libraries
sudo apt install libx11-dev libxtst-dev libxrandr-dev libxss-dev

# Install additional dependencies for GUI
sudo apt install python3-tk python3-pil python3-pil.imagetk

# Install MKD Automation
pip3 install mkd-automation

# Install Linux-specific dependencies
pip3 install python-xlib pycairo pygobject
```

#### CentOS/RHEL/Fedora Setup
```bash
# CentOS/RHEL
sudo yum install python3 python3-pip python3-devel
sudo yum groupinstall "Development Tools"
sudo yum install libX11-devel libXtst-devel libXrandr-devel libXss-devel

# Fedora
sudo dnf install python3 python3-pip python3-devel
sudo dnf groupinstall "Development Tools"
sudo dnf install libX11-devel libXtst-devel libXrandr-devel libXss-devel

# Install MKD Automation
pip3 install mkd-automation --user

# Install Linux-specific dependencies
pip3 install python-xlib pycairo pygobject --user
```

#### Arch Linux Setup
```bash
# Install Python and dependencies
sudo pacman -S python python-pip python-virtualenv

# Install development tools
sudo pacman -S base-devel libx11 libxtst libxrandr libxss

# Install MKD Automation
pip install mkd-automation --user

# Install Linux-specific dependencies
pip install python-xlib pycairo pygobject --user
```

#### Linux Permissions
```bash
# Add user to input group (for device access)
sudo usermod -a -G input $USER

# Set up udev rules for input devices (if needed)
echo 'SUBSYSTEM=="input", GROUP="input", MODE="0664"' | sudo tee /etc/udev/rules.d/99-input.rules

# Reload udev rules
sudo udevadm control --reload-rules && sudo udevadm trigger

# Log out and back in for group changes to take effect
```

## Development Environment

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/mkd_automation.git
cd mkd_automation

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .
```

### Development Dependencies

The development environment includes:

- **Testing**: pytest, pytest-cov, pytest-mock
- **Linting**: pylint, flake8, mypy
- **Formatting**: black, isort
- **Documentation**: sphinx, sphinx-rtd-theme
- **Security**: bandit, safety
- **Build**: build, twine

### IDE Configuration

#### VS Code
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

#### PyCharm
1. File ’ Settings ’ Project ’ Python Interpreter
2. Add ’ Virtualenv Environment ’ Existing Environment
3. Select `venv/bin/python` (or `venv\Scripts\python.exe` on Windows)

## Configuration

### Initial Configuration

Run the initial setup:

```bash
# Initialize configuration
mkd-automation --init

# Or manually create config directory
mkdir -p ~/.config/mkd  # Linux/macOS
mkdir %APPDATA%\MKD     # Windows
```

### Configuration File Locations

| Platform | Location |
|----------|----------|
| **Windows** | `%APPDATA%\MKD\config.json` |
| **macOS** | `~/Library/Application Support/MKD/config.json` |
| **Linux** | `~/.config/mkd/config.json` |

### Default Configuration

The installer creates a default configuration file:

```json
{
    "recording": {
        "mouse_sample_rate": 60,
        "keyboard_capture": true,
        "auto_save": false,
        "output_format": "mkd",
        "compression": true,
        "encryption": false
    },
    "playback": {
        "default_speed": 1.0,
        "coordinate_mode": "relative",
        "error_tolerance": "medium",
        "retry_attempts": 3
    },
    "ui": {
        "theme": "system",
        "always_on_top": false,
        "minimize_to_tray": true,
        "show_notifications": true
    },
    "logging": {
        "level": "INFO",
        "file_logging": true,
        "max_log_size": 10485760
    }
}
```

### Environment Variables

Set optional environment variables:

```bash
# Configuration directory override
export MKD_CONFIG_DIR="/path/to/custom/config"

# Log level override
export MKD_LOG_LEVEL="DEBUG"

# Disable GUI (for headless mode)
export MKD_HEADLESS="true"

# Custom plugin directory
export MKD_PLUGIN_DIR="/path/to/plugins"
```

## Verification

### Basic Installation Test

```bash
# Test command line interface
mkd-automation --version
mkd-automation --help

# Test Python import
python -c "import mkd; print('MKD Automation installed successfully')"

# Test basic functionality
python -c "
from mkd import MKDAutomation
mkd = MKDAutomation()
status = mkd.get_recording_status()
print(f'Recording status: {status.is_active}')
"
```

### Platform-Specific Tests

#### Windows
```python
# Test Windows-specific features
python -c "
from mkd.platform import get_platform_info
info = get_platform_info()
print(f'Platform: {info.name}')
print(f'Supports automation: {info.supports_automation}')
"
```

#### macOS
```python
# Test accessibility permissions
python -c "
from mkd.platform.macos import check_accessibility_permissions
has_perms = check_accessibility_permissions()
print(f'Accessibility permissions: {has_perms}')
"
```

#### Linux
```python
# Test X11 support
python -c "
from mkd.platform.linux import check_x11_support
has_x11 = check_x11_support()
print(f'X11 support: {has_x11}')
"
```

### GUI Test

Launch the GUI to ensure everything works:

```bash
# Start GUI
mkd-automation --gui

# Or start with debug output
mkd-automation --gui --debug
```

### Recording Test

Test basic recording functionality:

```bash
# Start recording test
python -c "
from mkd import MKDAutomation
import time

mkd = MKDAutomation()
print('Starting 5-second recording test...')
mkd.start_recording('test_recording.mkd')
time.sleep(5)
script_path = mkd.stop_recording()
print(f'Test recording saved to: {script_path}')
"
```

## Troubleshooting

### Common Installation Issues

#### Permission Denied Errors
```bash
# Solution 1: Use --user flag
pip install mkd-automation --user

# Solution 2: Use virtual environment
python -m venv mkd_venv
source mkd_venv/bin/activate  # Linux/macOS
mkd_venv\Scripts\activate     # Windows
pip install mkd-automation
```

#### Python Version Issues
```bash
# Check Python version
python --version

# If Python 3.9+ is not default, use python3
python3 -m pip install mkd-automation

# Or specify Python version explicitly
python3.11 -m pip install mkd-automation
```

#### Missing System Dependencies

##### Windows
```powershell
# Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019

# Or install via chocolatey
choco install visualcpp-build-tools
```

##### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install via Homebrew
brew install python@3.11
```

##### Linux
```bash
# Ubuntu/Debian
sudo apt install python3-dev build-essential libffi-dev libssl-dev

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel libffi-devel openssl-devel

# Fedora
sudo dnf groupinstall "Development Tools"
sudo dnf install python3-devel libffi-devel openssl-devel
```

### Runtime Issues

#### Import Errors
```python
# Test individual components
try:
    from mkd.core import ConfigManager
    print("Core module: OK")
except ImportError as e:
    print(f"Core module error: {e}")

try:
    from mkd.recording import RecordingEngine
    print("Recording module: OK")
except ImportError as e:
    print(f"Recording module error: {e}")

try:
    from mkd.playback import PlaybackEngine
    print("Playback module: OK")
except ImportError as e:
    print(f"Playback module error: {e}")
```

#### Platform-Specific Issues

##### Windows: Access Denied
- Run terminal as administrator
- Check Windows Defender exclusions
- Verify UAC settings

##### macOS: Accessibility Permissions
```bash
# Reset accessibility permissions
sudo tccutil reset Accessibility

# Check system log for permission denials
log show --predicate 'subsystem == "com.apple.TCC"' --last 1h
```

##### Linux: X11/Wayland Issues
```bash
# Check display environment
echo $DISPLAY
echo $WAYLAND_DISPLAY

# Test X11 tools
xdpyinfo | head

# For Wayland users, may need XWayland
sudo apt install xwayland  # Ubuntu/Debian
```

#### Configuration Issues
```bash
# Reset configuration to defaults
mkd-automation --reset-config

# Validate configuration
mkd-automation --validate-config

# Show current configuration
mkd-automation --show-config
```

### Performance Issues

#### High CPU Usage
```json
// Adjust config.json
{
    "recording": {
        "mouse_sample_rate": 30  // Reduce from 60
    },
    "performance": {
        "cpu_usage_limit": 0.5,  // Limit CPU usage
        "memory_limit_mb": 256   // Limit memory usage
    }
}
```

#### Memory Issues
```bash
# Monitor memory usage
mkd-automation --monitor-memory

# Enable memory debugging
MKD_DEBUG_MEMORY=1 mkd-automation --gui
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Enable debug output
mkd-automation --debug

# Set environment variable
export MKD_LOG_LEVEL=DEBUG
mkd-automation

# Log to file
mkd-automation --log-file debug.log --debug
```

### Getting Help

If you continue to experience issues:

1. **Check Documentation**: Review the [troubleshooting guide](troubleshooting.md)
2. **Search Issues**: Look through [GitHub issues](https://github.com/yourusername/mkd_automation/issues)
3. **Create Issue**: Report bugs with detailed information
4. **Community Support**: Ask questions in [GitHub Discussions](https://github.com/yourusername/mkd_automation/discussions)

Include this information when reporting issues:
- Operating system and version
- Python version
- MKD Automation version
- Complete error message
- Steps to reproduce
- Configuration files (with sensitive data removed)

## Upgrading

### Upgrade from PyPI

```bash
# Upgrade to latest version
pip install --upgrade mkd-automation

# Upgrade to specific version
pip install mkd-automation==0.3.0

# Check current version
pip show mkd-automation
```

### Development Version Upgrade

```bash
# Update repository
git pull origin main

# Update dependencies
pip install -r requirements-dev.txt

# Reinstall in development mode
pip install -e .
```

### Migration Between Versions

#### Backup Configuration
```bash
# Backup current configuration
cp ~/.config/mkd/config.json ~/.config/mkd/config.json.backup

# Backup recorded scripts
cp -r ~/Documents/MKD\ Scripts ~/Documents/MKD\ Scripts.backup
```

#### Version-Specific Migration

##### From v0.1.x to v0.2.x
- Configuration format changed
- Script format updated
- New permission requirements on macOS

```bash
# Run migration tool
mkd-automation --migrate-from-v01

# Or manually update configuration
mkd-automation --update-config
```

### Rollback

If you need to rollback to a previous version:

```bash
# Uninstall current version
pip uninstall mkd-automation

# Install specific older version
pip install mkd-automation==0.1.5

# Restore configuration backup
cp ~/.config/mkd/config.json.backup ~/.config/mkd/config.json
```

## Uninstallation

### Complete Uninstallation

```bash
# Uninstall package
pip uninstall mkd-automation

# Remove configuration files
rm -rf ~/.config/mkd                    # Linux
rm -rf ~/Library/Application\ Support/MKD  # macOS
rmdir /s %APPDATA%\MKD                  # Windows

# Remove user data (optional)
rm -rf ~/Documents/MKD\ Scripts

# Remove virtual environment (if used)
rm -rf venv/
```

### Clean Development Environment

```bash
# Remove development installation
pip uninstall mkd-automation

# Remove virtual environment
deactivate  # if activated
rm -rf venv/

# Remove build artifacts
rm -rf build/ dist/ *.egg-info/

# Remove cache files
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
```

### Docker Cleanup

```bash
# Remove Docker images
docker rmi mkdautomation/mkd-automation:latest

# Remove containers
docker container prune

# Remove volumes
docker volume prune
```

---

## Quick Installation Summary

For users who want to get started quickly:

```bash
# 1. Ensure Python 3.9+ is installed
python --version

# 2. Install MKD Automation
pip install mkd-automation

# 3. Set up platform permissions (macOS/Linux)
# Follow platform-specific setup above

# 4. Test installation
mkd-automation --version

# 5. Launch GUI
mkd-automation --gui
```

That's it! You're ready to start automating with MKD Automation.

For detailed usage instructions, see the [User Guide](user_guide/basic_usage.md).