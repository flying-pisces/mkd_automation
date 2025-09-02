# MKD Automation Web GUI

A web-based interface for the MKD Automation system, providing the same functionality as the desktop application through a modern web interface.

## Features

- **Identical UI Layout**: Matches the desktop application's interface exactly
- **Real-time Recording**: Capture mouse, keyboard, and screenshot events
- **Visual Feedback**: Red boundary frame during recording
- **Replay System**: Playback recordings with speed control
- **WebSocket Backend**: Real-time communication with MKD automation system
- **Cross-platform**: Works in any modern web browser
- **Responsive Design**: Adapts to different screen sizes

## Quick Start

### Option 1: Automatic Launch (Recommended)

```bash
# Navigate to web_gui directory
cd web_gui

# Run the launcher (installs dependencies and starts everything)
python start_web_gui.py
```

The launcher will:
1. Install required dependencies (`websockets`)
2. Start the backend WebSocket server
3. Open the web interface in your default browser

### Option 2: Manual Setup

1. **Install Dependencies**:
   ```bash
   pip install websockets
   ```

2. **Start Backend Server**:
   ```bash
   python backend_server.py
   ```

3. **Open Web Interface**:
   Open `index.html` in your web browser or navigate to the file location.

## Architecture

### Frontend (Web Interface)
- **HTML**: `index.html` - Complete UI structure matching desktop app
- **CSS**: `styles.css` - Responsive styling with animations
- **JavaScript**: `script.js` - Recording logic and WebSocket communication

### Backend (Python Server)
- **WebSocket Server**: `backend_server.py` - Bridges web frontend to MKD system
- **Real-time Communication**: Handles recording, playback, and system integration
- **File Storage**: Saves recordings in MKD format (.mkd files)

## UI Components

### Header Section
- **Title**: "MKD Automation v2.0 - Web Recorder with Replay"
- **Branding**: Matches desktop application styling

### Recording Status
- **Status Indicator**: Visual dot showing current state (Ready/Recording/Stopped)
- **Real-time Updates**: Status changes reflect recording state

### Control Buttons
- **Start Recording**: Begin capturing user interactions
- **Stop Recording**: End recording and save data
- **Replay Controls**: Play back recorded sessions

### Settings Panel
- **Capture Options**: 
  - Capture Mouse movements and clicks
  - Capture Keyboard input
  - Capture Screenshots for replay
  - Show Red Boundary frame during recording

### Statistics Section
- **Recording Duration**: Real-time duration counter
- **Actions Recorded**: Number of captured interactions
- **Capture Rate**: Actions per second
- **Screenshot Count**: Number of screenshots captured

### Recent Events Log
- **Real-time Event Display**: Shows captured actions as they happen
- **Timestamp**: Each event includes precise timestamp
- **Event Types**: Mouse moves, clicks, keyboard input

### System Information
- **Platform**: Operating system/browser info
- **Browser**: Detected browser type
- **Connection Status**: WebSocket server connection state

### Replay Modal
- **Video-style Controls**: Play, pause, stop buttons
- **Speed Control**: Adjustable playback speed (0.1x to 3.0x)
- **Progress Bar**: Visual progress indicator
- **Frame Display**: Canvas-based frame rendering
- **Frame Counter**: Current frame / total frames

## WebSocket Protocol

### Client to Server Messages

```javascript
// Start recording
{
    "type": "start_recording",
    "settings": {
        "capture_mouse": true,
        "capture_keyboard": true,
        "capture_screenshots": true
    }
}

// Stop recording
{
    "type": "stop_recording"
}

// Send captured action
{
    "type": "action",
    "action": {
        "type": "mouse_move",
        "data": {"x": 100, "y": 200},
        "timestamp": 1.5
    }
}
```

### Server to Client Messages

```javascript
// Recording started confirmation
{
    "type": "recording_started",
    "session_id": "abc123"
}

// Recording stopped with stats
{
    "type": "recording_stopped",
    "duration": 30.5,
    "actions": 150,
    "screenshots": 60
}

// Real-time screenshot count
{
    "type": "screenshot_captured",
    "count": 25
}
```

## Event Capture

The web interface captures the following events:

### Mouse Events
- **Movement**: Throttled to reduce data volume (every 10th event)
- **Clicks**: Left, middle, right button presses and releases
- **Coordinates**: Screen-relative positions

### Keyboard Events
- **Key Presses**: All keyboard input with key names
- **Special Keys**: Modifiers, function keys, etc.
- **Timing**: Precise timestamp for each event

### Screenshots (Simulated)
- **Frequency**: 2 FPS (configurable)
- **Format**: Would be PNG in full implementation
- **Storage**: Organized by recording session

## File Storage

### Recording Structure
```
web_recordings/
├── web_recording_20241201_143022/
│   ├── recording.mkd          # MKD format script file
│   └── screenshots/           # Screenshot frames (if enabled)
│       ├── frame_0001.png
│       ├── frame_0002.png
│       └── ...
└── web_recording_20241201_143055/
    └── ...
```

### MKD File Format
- **Binary Format**: Uses msgpack serialization
- **Compression**: LZ4 compression for efficiency
- **Encryption**: Optional AES-256 encryption
- **Compatibility**: Works with desktop MKD application

## Browser Compatibility

### Supported Browsers
- ✅ **Chrome 90+**: Full support including WebSocket
- ✅ **Firefox 85+**: Full support
- ✅ **Safari 14+**: Full support
- ✅ **Edge 90+**: Full support

### Required Features
- **WebSocket Support**: For real-time communication
- **Canvas API**: For replay visualization
- **ES6+ JavaScript**: Modern JavaScript features
- **CSS Grid/Flexbox**: Layout support

## Development

### Local Development Setup
1. **Clone Repository**: Get the MKD automation codebase
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Start Backend**: `python web_gui/backend_server.py`
4. **Open Frontend**: Open `web_gui/index.html` in browser

### Customization
- **Styling**: Modify `styles.css` for appearance changes
- **Functionality**: Extend `script.js` for new features
- **Backend**: Add endpoints in `backend_server.py`

### Integration
- **MKD Core**: Integrates with existing MKD session management
- **Platform Support**: Uses MKD platform detection
- **Storage**: Compatible with MKD script storage system

## Troubleshooting

### Common Issues

1. **"Connection Error"**
   - Ensure backend server is running
   - Check if port 8765 is available
   - Verify WebSocket support in browser

2. **"MKD modules not available"**
   - Install MKD automation system
   - Check Python path includes MKD source

3. **Recording not working**
   - Check browser permissions for input capture
   - Verify WebSocket connection established
   - Look for JavaScript console errors

4. **Replay not showing frames**
   - Ensure screenshots were captured during recording
   - Check if recording directory exists
   - Verify canvas API support

### Debug Mode
Enable browser developer tools (F12) to see:
- WebSocket connection status
- JavaScript console logs
- Network requests and errors

## Security Considerations

### Data Privacy
- **Local Processing**: All data stays on your machine
- **No External Servers**: Direct WebSocket to localhost only
- **Encrypted Storage**: Optional encryption for sensitive recordings

### Browser Permissions
- **Input Capture**: Limited to page focus and user interaction
- **File Access**: Uses standard browser file APIs
- **Network**: WebSocket connection to localhost only

## Future Enhancements

### Planned Features
- **Screen Recording**: Full screen capture integration
- **Multi-monitor Support**: Handle multiple displays
- **Cloud Sync**: Optional cloud storage for recordings
- **Mobile Interface**: Touch-optimized version
- **Plugin System**: Extension architecture

### API Extensions
- **REST API**: HTTP endpoints for external integration
- **Webhook Support**: Event notifications to external systems
- **Export Formats**: Additional export options beyond MKD

## License

Same as MKD Automation project - see main repository LICENSE file.