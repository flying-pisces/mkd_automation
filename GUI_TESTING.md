# GUI Recorder Testing

## Overview

A complete Python GUI application that mimics the Chrome extension interface for testing recording functionality with real-time visual feedback.

---

## 🚀 Quick Start

### Launch the GUI Test Application
```bash
# Simple launcher with dependency checking
python launch_gui_test.py

# Or run directly
python gui_recorder_test.py
```

### Required Dependencies
- **pynput** - For mouse and keyboard capture
- **tkinter** - For GUI (usually built-in with Python)

---

## ✨ Features

### 🎨 Chrome Extension-Like Interface
- **Professional UI** - Matches Chrome extension design
- **Recording Controls** - Start, Stop, Pause buttons
- **Settings Panel** - Configure capture options
- **Statistics Display** - Real-time recording metrics
- **System Information** - Platform and library status

### 🔴 Visual Recording Indicators
- **Red Boundary Frame** - Appears around entire screen during recording
- **Status Updates** - Clear visual feedback of recording state
- **Transparent Overlay** - Non-intrusive recording indicator

### 📊 Real-Time Event Monitoring
- **Live Event Dialog** - Shows captured events as they happen
- **Event Counter** - Tracks total events captured
- **Timestamped Events** - Each event shows exact capture time
- **Event Types** - Distinguishes mouse, keyboard, and other actions

### 💾 Recording Integration
- **Session Management** - Uses existing MKD recording system
- **File Export** - Saves to .mkd format
- **Multiple Recordings** - Can save and view multiple test sessions
- **Data Validation** - Verifies recording integrity

---

## 🖥️ User Interface

### Main Window Components

#### Header Section
```
┌─────────────────────────────────────────────────┐
│              MKD Automation                     │
│               v2.0 - GUI Test Mode              │
└─────────────────────────────────────────────────┘
```

#### Recording Status
```
┌─── Recording Status ────────────────────────────┐
│                ● Ready                          │
│              (● Recording)                      │
│              (⏸ Paused)                        │
│              (● Stopped)                        │
└─────────────────────────────────────────────────┘
```

#### Control Buttons
```
┌─────────────────────────────────────────────────┐
│  [▶ Start Recording] [⏹ Stop] [⏸ Pause]       │
└─────────────────────────────────────────────────┘
```

#### Settings Panel
```
┌─── Recording Settings ──────────────────────────┐
│  ☑ Capture Mouse                               │
│  ☑ Capture Keyboard                            │
│  ☑ Show Red Boundary                           │
│  ☑ Show Live Events                            │
└─────────────────────────────────────────────────┘
```

#### Live Statistics
```
┌─── Statistics ──────────────────────────────────┐
│  Recording Duration: 15.3 seconds              │
│  Actions Recorded: 127                         │
│  Capture Rate: 8.3 actions/sec                 │
│  Status: Recording                              │
│  Paused: No                                     │
│                                                 │
│  Settings:                                      │
│    Mouse Capture: On                            │
│    Keyboard Capture: On                         │
│    Red Boundary: On                             │
│    Event Monitor: On                            │
└─────────────────────────────────────────────────┘
```

---

## 🔴 Red Boundary Frame

### Visual Indicator
When recording starts:
- **Red frame appears** around entire screen perimeter
- **Semi-transparent** (70% opacity) - doesn't block view
- **Always on top** - visible over all applications
- **5 pixel thickness** - clearly visible but not intrusive

### Implementation
- **4 separate windows** - Top, Bottom, Left, Right edges
- **Automatic positioning** - Adapts to any screen resolution
- **Clean removal** - Disappears immediately when recording stops

---

## 📋 Event Monitor Dialog

### Real-Time Display
Shows live capture events as they occur:

```
┌─── Live Event Monitor ──────────────────────────┐
│              Events Captured: 45                │
│ ┌─────────────────────────────────────────────┐ │
│ │ [15:30:15.123] Mouse Move: (150, 200)      │ │
│ │ [15:30:15.145] Keyboard: A                 │ │
│ │ [15:30:15.167] Keyboard: B                 │ │
│ │ [15:30:15.189] Keyboard: C                 │ │
│ │ [15:30:15.211] Keyboard: D                 │ │
│ │ [15:30:15.233] Mouse Press: left at (150,200)│ │
│ │ [15:30:15.255] Mouse Release: left at (150,200│ │
│ │ ...                                         │ │
│ └─────────────────────────────────────────────┘ │
│                [Clear Events]                   │
└─────────────────────────────────────────────────┘
```

### Event Format Examples
- **Keyboard**: `[15:30:15.123] Keyboard: A`
- **Mouse Move**: `[15:30:15.145] Mouse Move: (150, 200)`
- **Mouse Click**: `[15:30:15.167] Mouse Press: left at (150, 200)`
- **Mouse Release**: `[15:30:15.189] Mouse Release: left at (150, 200)`

---

## 🧪 Testing Workflow

### 1. Start Testing Session
```bash
python launch_gui_test.py
```

### 2. Configure Settings
- ✅ Enable desired capture options
- ✅ Configure visual feedback preferences

### 3. Begin Recording
- Click **"▶ Start Recording"**
- Red frame appears around screen
- Event monitor dialog opens (if enabled)

### 4. Perform Test Actions
- **Type text**: "ABCD" → Shows "Keyboard: A", "Keyboard: B", etc.
- **Move mouse**: Shows coordinates in real-time
- **Click buttons**: Shows button presses and releases
- **Use keyboard shortcuts**: Captures special keys

### 5. Monitor Results
- Watch **live event display**
- Check **statistics updates**
- Verify **action counting**

### 6. Stop and Save
- Click **"⏹ Stop Recording"**
- Red frame disappears
- Click **"Save Test Recording"**
- File saved to `recordings/` directory

### 7. Verify Results
- Click **"View Recordings"** to see saved files
- Check file contents and action counts
- Validate timestamp accuracy

---

## 💡 Testing Scenarios

### Basic Input Testing
```
Test: Type "ABCD"
Expected Events:
- Keyboard: A
- Keyboard: B  
- Keyboard: C
- Keyboard: D

Plus corresponding key release events
```

### Mouse Interaction Testing
```
Test: Click and drag
Expected Events:
- Mouse Move: (start coordinates)
- Mouse Press: left at (coordinates)
- Mouse Move: (intermediate coordinates) [multiple]
- Mouse Release: left at (end coordinates)
```

### Mixed Input Testing
```
Test: Type while moving mouse
Expected Events:
- Interleaved keyboard and mouse events
- Proper timestamp ordering
- No event loss during concurrent input
```

### Special Keys Testing
```
Test: Ctrl+A, Alt+Tab, etc.
Expected Events:
- Keyboard: CTRL
- Keyboard: A
- Keyboard: CTRL (release)
- Keyboard: A (release)
```

---

## 📊 Success Criteria

### ✅ Visual Feedback
- [x] Red boundary frame appears during recording
- [x] Frame covers entire screen perimeter
- [x] Frame disappears when recording stops
- [x] No interference with normal computer use

### ✅ Event Capture
- [x] All keyboard input captured and displayed
- [x] Mouse movements tracked with coordinates
- [x] Mouse clicks recorded with button and position
- [x] Timestamps accurate to millisecond precision
- [x] Events appear in real-time monitor

### ✅ Data Integrity
- [x] Events saved to .mkd file format
- [x] File can be loaded back successfully
- [x] Action count matches display
- [x] No data loss during recording

### ✅ User Experience
- [x] Intuitive interface similar to Chrome extension
- [x] Clear status indicators
- [x] Responsive controls
- [x] Helpful error messages

---

## 🔧 Troubleshooting

### GUI Won't Launch
```bash
# Check Python and tkinter
python -m tkinter

# Install missing dependencies
pip install pynput
```

### No Events Captured
- Verify pynput is installed correctly
- Check recording settings are enabled
- Ensure application has input permissions

### Red Frame Issues
- Check screen resolution detection
- Verify tkinter toplevel window support
- Test with different display configurations

### Event Monitor Not Showing
- Check "Show Live Events" setting
- Verify dialog creation permissions
- Test window layering and focus

---

## 📋 Integration with Development Plan

This GUI testing tool directly supports the Chrome Web Store development plan by:

### ✅ Validating Core Functionality
- **Before Week 1**: Ensures recording system works perfectly
- **During Development**: Provides testing interface for new features
- **Pre-Submission**: Validates end-to-end recording workflow

### ✅ Supporting Milestone Testing
- **Week 1**: Security testing with controlled input
- **Week 2**: Integration testing with Python backend
- **Week 3**: Performance testing under various loads

### ✅ Quality Assurance
- **Real-time feedback** ensures immediate issue detection
- **Visual confirmation** validates recording boundaries
- **Data verification** confirms .mkd file integrity
- **User experience testing** matches Chrome extension behavior

This GUI tool provides the confidence that the core recording functionality works perfectly before proceeding with Chrome Web Store development.