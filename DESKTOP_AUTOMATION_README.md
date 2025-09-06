# MKD Desktop Automation - Complete System

## Overview

MKD now provides comprehensive desktop automation capabilities, enabling full system control through natural language commands. This system delivers "human motion level" automation for Windows, macOS, and Linux.

## Quick Start

### 1. Test the System
```bash
python test_desktop_simple.py
```

### 2. Run the Demo
```bash
python desktop_automation_demo.py
```

### 3. Try Practical Examples
```bash
python examples\desktop_automation_examples.py
```

### 4. Launch GUI Interface
```bash
python src\mkd\gui_launcher.py
```

## Core Capabilities

### ✅ Mouse & Keyboard Control
- **Precise mouse movement** and clicking
- **Keyboard input simulation** with modifier keys
- **Drag and drop** operations
- **Smooth mouse animations**

### ✅ Application Management
- **Launch any application** by name or path
- **Window management** (resize, move, minimize, maximize)
- **Process monitoring** and control
- **Application lifecycle** management

### ✅ File System Operations
- **File and folder creation/deletion**
- **Copy, move, rename** operations
- **Directory browsing** and navigation
- **File properties** and metadata

### ✅ System Integration
- **Command prompt** and PowerShell automation
- **Windows system tools** (Task Manager, Control Panel)
- **Registry and service** management
- **Screen capture** and visual automation

### ✅ Natural Language Interface
- **Conversation-style commands**
- **Flexible command parsing**
- **Error handling and feedback**
- **Context-aware responses**

## Natural Language Commands

### Mouse Control
```
click at 500, 300
double click at 100, 200
right click at 800, 400
move mouse to 1000, 500
drag from 100, 100 to 200, 200
```

### Keyboard Input
```
type "Hello, World!"
press ctrl+c
press alt+tab
press windows+r
hold shift and press arrow down
```

### Application Management
```
open notepad
launch calculator
start firefox browser
close notepad
minimize the calculator
maximize the browser window
```

### File Operations
```
open folder C:\Users\Documents
create folder "New Project"
create file "readme.txt"
copy file from C:\source.txt to C:\dest.txt
delete the temporary file
```

### System Commands
```
open control panel
show task manager
take a screenshot
lock the workstation
get clipboard content
list running processes
```

## Architecture

### Core Components

1. **DesktopController** (`src/mkd/desktop/controller.py`)
   - Main automation controller
   - Action execution engine
   - Cross-platform compatibility

2. **ApplicationManager** (`src/mkd/desktop/application_manager.py`)
   - Application launching and management
   - Process monitoring and control
   - Common application registry

3. **FileOperations** (`src/mkd/desktop/file_operations.py`)
   - File system operations
   - Cross-platform file handling
   - Metadata and properties

4. **WindowsAutomation** (`src/mkd/desktop/windows_automation.py`)
   - Windows-specific features
   - Win32 API integration
   - Advanced system control

5. **ConversationPanel** (`src/mkd/ui/conversation_panel.py`)
   - Natural language processing
   - Command pattern matching
   - User interface integration

### Action System

All automation uses the action-based architecture:

```python
from mkd.desktop.controller import DesktopController
from mkd.desktop.actions import DesktopAction

controller = DesktopController()

# Create actions
click_action = DesktopAction.mouse_click(500, 300)
type_action = DesktopAction.type_text("Hello World")
key_action = DesktopAction.key_combination(["ctrl", "c"])

# Execute actions
controller.execute_action(click_action)
controller.execute_action(type_action)
controller.execute_action(key_action)
```

## Dependencies

### Required Packages
```bash
pip install pynput pillow pywin32 psutil
```

### Package Purposes
- **pynput**: Mouse and keyboard control
- **pillow**: Screen capture and image processing
- **pywin32**: Windows API integration
- **psutil**: Process and system monitoring

## Platform Support

### Windows (Primary)
- ✅ Full Win32 API integration
- ✅ Advanced window management
- ✅ System tool automation
- ✅ Registry and service control

### macOS (Supported)
- ✅ Basic mouse/keyboard control
- ✅ Application launching
- ✅ File operations
- ⚠️ Limited system integration

### Linux (Supported)
- ✅ Basic mouse/keyboard control
- ✅ Application launching
- ✅ File operations
- ⚠️ Limited system integration

## Usage Examples

### Programming Interface
```python
from mkd.desktop.controller import DesktopController
from mkd.desktop.actions import DesktopAction

controller = DesktopController()

# Launch notepad and type text
launch_action = DesktopAction.launch_app("notepad")
controller.execute_action(launch_action)

type_action = DesktopAction.type_text("Automated text!")
controller.execute_action(type_action)

# Save file
save_action = DesktopAction.key_combination(["ctrl", "s"])
controller.execute_action(save_action)
```

### GUI Interface
1. Launch `python src\mkd\gui_launcher.py`
2. Use the conversation panel
3. Type natural language commands
4. Watch automation execute in real-time

### Conversation Examples
```
User: "open calculator and type 123 + 456"
MKD: Opening calculator... Typing: 123 + 456

User: "take a screenshot of the desktop"
MKD: Screenshot saved to: screenshot_1234567890.png

User: "create a folder called Projects on the desktop"
MKD: Created folder: C:\Users\YourName\Desktop\Projects
```

## Safety Features

- **Error handling** for failed operations
- **Permission checks** for system operations
- **Safe defaults** for destructive operations
- **Logging and monitoring** of all actions

## Extending the System

### Adding New Actions
1. Define action type in `actions.py`
2. Implement execution in `controller.py`
3. Add command patterns to `conversation_panel.py`

### Platform-Specific Features
1. Extend platform modules (`windows_automation.py`, etc.)
2. Add platform detection logic
3. Implement fallback mechanisms

## Troubleshooting

### Common Issues
1. **Import errors**: Install required packages
2. **Permission denied**: Run as administrator for system operations
3. **Unicode errors**: Windows console encoding issues
4. **Mouse/keyboard not working**: Check pynput installation

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance

- **Low latency**: Direct API calls for fast execution
- **Efficient**: Minimal overhead for basic operations
- **Scalable**: Handles complex automation sequences
- **Reliable**: Robust error handling and recovery

## Security

- **Safe by design**: No credential harvesting
- **User consent**: Clear action descriptions
- **Audit trail**: Complete logging of operations
- **Sandboxed**: Isolated execution environment

---

**MKD Desktop Automation provides the foundation for comprehensive system automation through intuitive natural language commands. The system is designed for automation engineers, GUI testing, and power users who need precise desktop control.**