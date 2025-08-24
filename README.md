# MKD Automation

**M**ouse **K**eyboard **D**isplay automation tool - A lazy automation engineer's best friend for capturing and reproducing user interactions.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9+-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-In%20Development-orange.svg)

## 🚀 Overview

MKD Automation is a cross-platform desktop application designed for design engineers and automation professionals who need to capture, analyze, and reproduce complex user interactions. Whether you're testing GUI applications, creating demos, or automating repetitive tasks, MKD provides an intuitive solution for recording and playing back mouse movements, keyboard inputs, and display actions.

## ✨ Key Features

### 🎯 Core Functionality
- **Real-time Capture**: Background recording of mouse movements, clicks, keyboard inputs, and screen events
- **Intelligent Analysis**: Motion pattern recognition and gesture detection
- **Precise Playback**: Accurate reproduction of recorded actions with timing control
- **Portable Scripts**: Save automation sequences as executable `.mkd` files

### 🖥️ User Interface
- **Movable Control Dialog**: START/STOP controls that can be positioned anywhere on screen
- **System Tray Integration**: Minimal background presence with quick access
- **Minimizable Design**: Non-intrusive recording experience
- **Real-time Status**: Live feedback during recording and playback

### 🔒 Security & Reliability
- **Encrypted Storage**: AES-256 encryption for sensitive automation scripts
- **Error Recovery**: Robust playback with retry mechanisms
- **Cross-platform**: Native support for Windows, macOS, and Linux
- **Performance Optimized**: Minimal system impact during recording

## 🎯 Use Cases

### For Design Engineers
- **GUI Testing**: Automate repetitive testing workflows
- **Demo Creation**: Record complex interaction sequences for presentations
- **Camera Control**: Capture images through camera GUI applications
- **Manual Process Documentation**: Record and share operational procedures

### For Automation Engineers
- **Workflow Automation**: Convert manual processes into reproducible scripts
- **Quality Assurance**: Create consistent test scenarios
- **Training Materials**: Generate interactive tutorials and guides
- **System Integration**: Bridge between different applications and systems

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Quick Install
```bash
# Clone the repository
git clone https://github.com/yourusername/mkd_automation.git
cd mkd_automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run with debugging
python src/main.py --debug
```

## 📖 Quick Start

### Recording Your First Automation

1. **Launch MKD**: Run `python src/main.py`
2. **Start Recording**: Click the START button in the control dialog
3. **Perform Actions**: Execute your desired mouse and keyboard actions
4. **Stop Recording**: Click STOP when finished
5. **Save Script**: Choose a location to save your `.mkd` file
6. **Playback**: Load and execute your saved automation script

### Basic Usage Example
```python
from mkd import MKDAutomation

# Initialize MKD
mkd = MKDAutomation()

# Start recording
mkd.start_recording()

# Your manual actions are captured here...

# Stop and save
script_path = mkd.stop_recording("my_automation.mkd")

# Later, playback the recorded actions
mkd.playback(script_path)
```

## 🏗️ Architecture

MKD follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐
│   Control GUI   │    │ Recording Engine│    │Playback Engine│
│  - Start/Stop   │◄──►│ - Input Capture │◄──►│- Action Exec  │
│  - Settings     │    │ - Motion Analysis│    │- Timing Control│
└─────────────────┘    └─────────────────┘    └──────────────┘
         │                       │                      │
         └───────────────────────┼──────────────────────┘
                                 ▼
                    ┌─────────────────────┐
                    │  Platform Layer     │
                    │ - Windows/macOS/Linux│
                    │ - OS-specific APIs  │
                    └─────────────────────┘
```

### Core Modules
- **Recording Engine**: Captures and processes user input events
- **Playback Engine**: Reproduces recorded actions with precision
- **UI Layer**: Control dialogs and system tray integration
- **Platform Layer**: OS-specific implementations for maximum compatibility
- **Data Layer**: Secure storage and serialization of automation scripts

## 🔧 Configuration

### Settings File
MKD uses JSON configuration files located in:
- **Windows**: `%APPDATA%/MKD/config.json`
- **macOS**: `~/Library/Application Support/MKD/config.json`
- **Linux**: `~/.config/mkd/config.json`

### Example Configuration
```json
{
  "recording": {
    "mouse_sample_rate": 60,
    "keyboard_capture": true,
    "screen_events": true,
    "auto_save": false
  },
  "playback": {
    "default_speed": 1.0,
    "error_tolerance": "medium",
    "coordinate_mode": "relative"
  },
  "ui": {
    "theme": "system",
    "always_on_top": false,
    "minimize_to_tray": true
  },
  "security": {
    "encrypt_scripts": true,
    "require_password": false
  }
}
```

## 🧪 Testing

MKD includes comprehensive test coverage:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mkd --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/platform/      # Platform-specific tests
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Maintain test coverage above 90%
- Document public APIs

## 📊 Project Status

### Current Version: 0.1.0-alpha

### Roadmap
- [x] Project architecture design
- [x] Core module scaffolding
- [ ] Basic input capture implementation
- [ ] Simple playback functionality
- [ ] Cross-platform input simulation
- [ ] GUI control dialog
- [ ] File format specification
- [ ] Encryption and security features
- [ ] Advanced motion analysis
- [ ] Plugin system
- [ ] Cloud synchronization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by automation tools like AutoHotkey, PyAutoGUI, and Sikuli
- Built with Python and cross-platform compatibility in mind
- Thanks to the open-source community for foundational libraries

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mkd_automation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mkd_automation/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/mkd_automation/wiki)

## 🔗 Related Projects

- [PyAutoGUI](https://github.com/asweigart/pyautogui) - Cross-platform GUI automation
- [AutoHotkey](https://github.com/AutoHotkey/AutoHotkey) - Windows automation scripting
- [SikuliX](https://github.com/RaiMan/SikuliX1) - Image-based automation
- [Robot Framework](https://github.com/robotframework/robotframework) - Test automation framework

---

**Made with ❤️ by automation engineers, for automation engineers.**
