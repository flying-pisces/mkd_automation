# 🧠 MKD Intelligent System-Level Recording

## Overview

The MKD Automation Web GUI now includes **intelligent system-level monitoring** that goes far beyond simple mouse and keyboard recording. This advanced system monitors and correlates **three distinct layers** of user activity:

### 🎯 Three-Layer Architecture

1. **🖱️ Input Layer**: Mouse movements, clicks, keyboard input with precise timing
2. **📹 Visual Layer**: Screen recording/screenshots of what the user sees  
3. **🔧 System Layer**: Process launches, window changes, Task Manager integration, semantic analysis

## ✨ Key Features

### 🔍 **Intelligent Process Monitoring**
- **Real-time process tracking**: Monitors all process creation/termination
- **Application identification**: Recognizes browsers, calculators, text editors, etc.
- **Window focus tracking**: Knows which application the user is actively using
- **Parent-child relationships**: Understands how processes spawn other processes

### 🧠 **Semantic Action Analysis** 
- **Hotkey recognition**: Understands Ctrl+Alt+Del, Ctrl+Shift+Esc, Win+R, etc.
- **Context-aware actions**: Knows when you're opening a browser vs. calculator
- **Intent inference**: "User opened Calculator for calculations" vs. "User launched browser"
- **Application-specific behaviors**: Detects private browsing, file operations, etc.

### 🔧 **Task Manager Integration**
- **Auto-launch**: Automatically opens Task Manager during recording for system visibility
- **Process correlation**: Links user actions to system process changes
- **Resource monitoring**: Tracks CPU/memory usage during recording sessions
- **System impact analysis**: Understands how user actions affect system performance

### 🎬 **Intelligent Replay**
- **Multi-layer playback**: Shows video + user actions + system events simultaneously  
- **Semantic annotations**: Displays high-level meaning of user actions
- **Process timeline**: Shows what applications were launched when
- **Correlation visualization**: Links user inputs to system responses

## 🚀 How It Works

### Recording Phase
1. **User starts recording** → System monitoring begins
2. **Task Manager auto-launches** → Provides system visibility
3. **Three monitoring streams activate**:
   - Input capture (mouse/keyboard)
   - Screen capture (video/screenshots)  
   - System monitoring (processes/windows)
4. **Real-time correlation** → Actions linked to system events
5. **Semantic analysis** → Meaning extracted from low-level actions

### Analysis Phase
- **Process events**: "chrome.exe launched" → "User opened web browser"  
- **Window changes**: "Focus changed to Calculator" → "User switched to calculations"
- **Hotkey detection**: "Ctrl+Shift+Esc pressed" → "User opened Task Manager"
- **Application context**: "Typing in calc.exe" → "User performing calculations"

### Replay Phase
- **Video playback** with action overlays
- **Process timeline** showing application launches
- **Semantic annotations** explaining user intent
- **System impact visualization** showing resource usage

## 📁 File Structure

```
web_gui/
├── system_monitor.py           # Core system monitoring engine
├── backend_server.py           # Enhanced WebSocket server  
├── test_intelligent_recording.html  # Advanced test interface
├── test_combined_capture.html  # Video + action testing
├── test_screen_capture.html    # Basic screen capture test
└── index.html                  # Main MKD interface
```

## 🛠️ Technical Implementation

### System Monitor (`system_monitor.py`)
- **WMI Integration**: Uses Windows Management Instrumentation for process monitoring
- **PSUtil**: Cross-platform system and process utilities
- **Event Correlation**: Links user actions to system events within time windows
- **Semantic Analysis**: Converts low-level events to high-level meanings

### Enhanced Backend (`backend_server.py`)  
- **Async WebSocket Server**: Handles real-time communication
- **Multi-stream Recording**: Coordinates video, input, and system monitoring
- **Task Manager Control**: Programmatically launches and manages Task Manager
- **Data Correlation**: Links user actions with system events

### Intelligent UI (`test_intelligent_recording.html`)
- **Live System Dashboard**: Real-time CPU, memory, process monitoring
- **Correlation Visualization**: Shows user action → system response pairs
- **Process Management**: Live process list with resource usage
- **Event Stream**: Real-time log of all three monitoring layers

## 🎮 Usage Examples

### Example 1: Browser Launch Detection
```
User Action:    Win+R → type "chrome" → Enter
System Event:   chrome.exe process created (PID: 1234)
Semantic Result: "User launched Chrome web browser"
Recording:      Video shows Run dialog + process launch
```

### Example 2: Calculator Usage
```  
User Action:    Win+R → type "calc" → Enter → "123 + 456 ="
System Event:   calc.exe process created → window focused
Semantic Result: "User opened Calculator and performed arithmetic"
Recording:      Video + keystrokes + process correlation
```

### Example 3: Task Manager Hotkey
```
User Action:    Ctrl+Shift+Esc
System Event:   taskmgr.exe process created
Semantic Result: "User opened Task Manager via hotkey"
Recording:      Hotkey detection + process launch + video
```

## 🧪 Test Scenarios

### 🌐 **Browser Test**
1. Start intelligent recording
2. Press `Win+R` (Run dialog)  
3. Type `chrome` and press Enter
4. Navigate to a website
5. See correlation: hotkey → process launch → web browsing

### 🔢 **Calculator Test**
1. Start recording
2. Press `Win+R`, type `calc`
3. Perform calculations: `2 + 2 =`
4. System understands: launched calculator + performed arithmetic

### ⌨️ **Hotkey Test**  
1. Start recording
2. Try `Ctrl+Shift+Esc` (Task Manager)
3. Try `Ctrl+Alt+D` (Show Desktop)
4. System recognizes hotkey meanings and system responses

### 🔧 **Multi-App Workflow**
1. Start recording  
2. Open multiple applications (browser, calculator, notepad)
3. Switch between them using Alt+Tab
4. See complete application workflow with timing

## 🔍 System Requirements

### Required Dependencies
```bash
pip install wmi psutil pywin32 websockets
```

### Browser Support
- **Chrome/Edge**: Full video recording + MediaRecorder API
- **Firefox**: Video recording supported
- **Safari**: Screenshot fallback mode
- **All Browsers**: Input capture and system monitoring work universally

### Windows Features
- **WMI**: Windows Management Instrumentation (built-in)
- **Task Manager**: Programmatic launch and control
- **Process Monitoring**: Real-time process creation/termination events
- **Window Tracking**: Active window and focus change detection

## 📊 Data Output

### Recording Data Structure
```json
{
  "timestamp": "2025-01-20T10:30:00Z",
  "duration": 45.2,
  "layers": {
    "user_actions": [
      {
        "type": "key_down", 
        "data": {"key": "WIN", "timestamp": 1.2},
        "semantic_meaning": "Windows key pressed"
      }
    ],
    "system_events": [
      {
        "type": "process_start",
        "process_name": "chrome.exe", 
        "semantic_action": "Opened web browser",
        "timestamp": 1.8
      }
    ],
    "video_data": "base64_encoded_webm_video",
    "correlations": [
      {
        "user_action": "Win+R hotkey",
        "system_result": "Run dialog opened",
        "time_delta": 0.6
      }
    ]
  },
  "semantic_summary": {
    "session_narrative": "User launched Chrome browser and navigated to website",
    "applications_used": ["explorer.exe", "chrome.exe"],
    "hotkeys_detected": ["win+r"],
    "system_impact": "Low resource usage, normal application workflow"
  }
}
```

## 🎯 Benefits

### For Automation Engineers
- **Complete system understanding**: Not just "click here", but "launch application X"
- **Robust replay**: System-aware playback that adapts to different environments
- **Debugging insights**: See exactly what system events your actions triggered

### For Testing Teams  
- **Full test coverage**: Visual + functional + system-level validation
- **Performance correlation**: Link user actions to system performance impact
- **Cross-application workflows**: Test complex multi-app scenarios

### For Training & Documentation
- **Rich recordings**: Show not just what happened, but why and how
- **Semantic annotations**: Self-documenting recordings with high-level explanations
- **System context**: Understand the full impact of user workflows

## 🔮 Future Enhancements

- **Machine Learning**: Predict user intent from action patterns
- **Network Monitoring**: Track network requests triggered by user actions  
- **File System Monitoring**: Monitor file operations during recording
- **Registry Monitoring**: Track Windows registry changes
- **Performance Profiling**: Detailed resource impact analysis
- **Cross-Platform Support**: Extend to macOS and Linux system monitoring

---

## 🚀 Getting Started

1. **Install Dependencies**: `pip install wmi psutil pywin32 websockets`
2. **Start Backend**: `python backend_server.py`  
3. **Open Test Page**: Open `test_intelligent_recording.html` in browser
4. **Start Recording**: Click "Start Intelligent Recording"
5. **Perform Actions**: Try the test scenarios above
6. **Analyze Results**: View correlations and semantic analysis
7. **Replay**: Watch intelligent replay with all three layers

The MKD system now provides **the most comprehensive user activity recording available**, combining traditional input/video capture with deep system-level intelligence for true understanding of user workflows.