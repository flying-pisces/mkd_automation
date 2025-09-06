# 🎬 MKD Web Recorder - Complete Usage Guide

## 🌐 GitHub Pages Deployment Complete!

**Live Demo**: `https://your-username.github.io/mkd-automation/`  
**Local Test**: `http://localhost:3000` (currently running)

---

## 🚀 Quick Start Guide

### 1. **Access the Recorder**
- **Online**: Visit the GitHub Pages URL (no installation required)
- **Local**: Open `docs/index.html` in any modern browser
- **Self-hosted**: Run `python -m http.server` in the docs folder

### 2. **Start Recording**
1. Click **"📹 Start Recording"**
2. **Grant screen capture permission** when browser prompts
3. **Select screen/window** to record
4. **Perform your actions** - everything is captured automatically

### 3. **Stop & Replay**
1. Click **"⏹️ Stop Recording"** when finished
2. Click **"🎬 Replay Recording"** to review
3. **Use playback controls** to navigate the recording
4. **Watch action overlays** showing your clicks and keystrokes

### 4. **Download & Share**
1. Click **"💾 Download Recording"** to save locally
2. Get **video file** (.webm) and **action data** (.json)
3. **Share recordings** with team members or clients

---

## 📋 Detailed Feature Guide

### 🎥 **Recording Features**

#### Screen Capture
- **High-Definition**: Up to 1080p 30fps recording
- **Browser Native**: Uses MediaRecorder API for optimal performance
- **Format**: WebM video with VP8 codec for broad compatibility
- **Quality Control**: Automatic bitrate adjustment based on content

#### Action Capture
```javascript
// Mouse Actions Captured
{
  "type": "mouse_down",
  "data": {
    "x": 245, "y": 167,           // Screen coordinates
    "pageX": 245, "pageY": 167,   // Page coordinates  
    "button": "left"              // left/right/middle
  },
  "timestamp": 1.234              // Seconds from recording start
}

// Keyboard Actions Captured  
{
  "type": "key_down", 
  "data": {
    "key": "Enter",               // Key pressed
    "code": "Enter",              // Key code
    "ctrlKey": false,             // Modifier keys
    "altKey": false,
    "shiftKey": false,
    "metaKey": false
  },
  "timestamp": 2.456
}
```

### 🎬 **Replay Features**

#### Visual Indicators
- **🔴 Red Circles**: Left mouse clicks
- **🔵 Blue Circles**: Right mouse clicks  
- **🟢 Green Circles**: Middle mouse clicks
- **🟡 Yellow Circles**: Mouse movements
- **⌨️ Dark Boxes**: Keyboard key presses with key labels

#### Playback Controls
- **▶️ Play/Pause**: Standard video controls
- **⏩ Speed Control**: 0.25x to 2x playback speed
- **🎯 Frame Seeking**: Click progress bar to jump to specific time
- **📊 Action Timeline**: See when actions occurred during recording

### 💾 **Storage & Export**

#### Local Storage
```javascript
// Browser localStorage structure
{
  "mkd_recordings": [           // Array of all recordings
    {
      "id": "1693834567890",
      "timestamp": "2023-09-04T10:30:00Z",
      "duration": 45.2,
      "mouseActions": 127,
      "keyActions": 89,
      "hasVideo": true
    }
  ],
  "mkd_current_recording": {...} // Most recent recording
}
```

#### Export Options
- **Video File**: High-quality WebM for sharing/editing
- **Actions JSON**: Complete action data for automation
- **Combined Package**: Both files with matching timestamps

---

## 🛠️ Technical Configuration

### 🔧 **Settings Panel**

#### Recording Settings
- **📹 Record Screen Video**: Enable/disable video capture
- **🖱️ Record Mouse & Keyboard**: Enable/disable input tracking
- **🎨 Show Action Overlays**: Enable/disable replay visualizations

#### Performance Settings
```javascript
// Configurable in recorder.js
const MOUSE_THROTTLE = 10;      // Capture every 10th mouse move
const VIDEO_BITRATE = 2500000;  // 2.5 Mbps video quality
const MAX_RECORDINGS = 10;      // Keep last 10 recordings
const STORAGE_LIMIT = 50;       // 50MB localStorage limit
```

### 🌐 **Browser Compatibility**

| Browser | Screen Capture | Video Recording | Action Overlays | Status |
|---------|---------------|-----------------|-----------------|---------|
| **Chrome 88+** | ✅ | ✅ | ✅ | Full Support |
| **Edge 88+** | ✅ | ✅ | ✅ | Full Support |
| **Firefox 87+** | ✅ | ✅ | ✅ | Full Support |
| **Safari 14+** | ⚠️ | ❌ | ✅ | Limited* |

*Safari: Screen capture requires user gesture, no MediaRecorder support

### 📱 **Device Support**

#### Desktop Browsers
- **Windows**: Full support in Chrome, Edge, Firefox
- **macOS**: Full support in Chrome, Edge, Firefox, Safari (limited)
- **Linux**: Full support in Chrome, Firefox

#### Mobile/Tablet
- **iOS Safari**: Screen capture not available
- **Android Chrome**: Limited screen capture support
- **Tablet**: Works but optimized for desktop usage

---

## 🎯 **Usage Scenarios**

### 🎓 **Educational Content**
```markdown
1. **Software Tutorials**
   - Record software usage with precise action tracking
   - Show exact click locations and key combinations
   - Export for video editing or direct sharing

2. **Training Materials** 
   - Create step-by-step guides with visual feedback
   - Highlight important actions with automatic overlays
   - Generate both video and data for comprehensive training

3. **Bug Reporting**
   - Document issues with exact reproduction steps
   - Provide video evidence plus detailed action data
   - Export timeline for developer analysis
```

### 🧪 **Testing & QA**
```markdown
1. **User Acceptance Testing**
   - Record user interactions during testing sessions
   - Analyze mouse/keyboard patterns for UX insights
   - Generate reports with timestamps and action counts

2. **Regression Testing**
   - Create baseline recordings for comparison
   - Export action data for automated replay scripts
   - Document test scenarios with visual evidence

3. **Performance Analysis**
   - Monitor user workflow efficiency
   - Identify bottlenecks in user interactions
   - Measure task completion times and actions
```

### 📝 **Documentation**
```markdown
1. **Feature Demonstrations**
   - Record new feature usage for documentation
   - Create interactive guides with action highlights
   - Export materials for documentation websites

2. **API Usage Examples**
   - Show real-world application usage
   - Document complex workflows visually
   - Generate training materials for developers
```

---

## 🔧 **Customization Guide**

### 🎨 **UI Customization**

#### Styling (`styles.css`)
```css
/* Custom brand colors */
:root {
  --primary-color: #your-brand-color;
  --secondary-color: #your-accent-color;
  --background: #your-background;
}

/* Custom button styles */
.btn-primary {
  background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
}
```

#### Layout Modifications
- **Panel arrangement**: Modify `.container` grid layout
- **Feature sections**: Add/remove feature cards in HTML
- **Responsive design**: Adjust breakpoints in CSS media queries

### ⚙️ **Functionality Customization**

#### Recording Settings (`recorder.js`)
```javascript
// Modify these constants for custom behavior
const CONFIG = {
  VIDEO_QUALITY: {
    width: { ideal: 1920 },     // Recording resolution
    height: { ideal: 1080 },
    frameRate: { ideal: 30 }    // FPS
  },
  
  MOUSE_THROTTLE: 10,           // Mouse capture frequency
  
  STORAGE: {
    maxRecordings: 10,          // Keep last N recordings
    maxSize: 50 * 1024 * 1024   // 50MB limit
  },
  
  OVERLAY_COLORS: {
    leftClick: '#ff4444',       // Left mouse button
    rightClick: '#4444ff',      // Right mouse button
    middleClick: '#44ff44',     // Middle mouse button
    mouseMove: '#ffff44'        // Mouse movement
  }
};
```

#### Custom Action Handlers
```javascript
// Add custom action processing
recordAction(type, data) {
    const timestamp = this.getRecordingTime();
    
    // Custom processing based on action type
    if (type === 'key_down' && data.key === 'F12') {
        // Handle special keys differently
        this.handleSpecialKey(data);
    }
    
    // Standard action recording
    this.actions.push({ type, data, timestamp });
}
```

---

## 🐛 **Troubleshooting Guide**

### ❌ **Common Issues**

#### Permission Denied
```
Error: Screen capture permission denied
```
**Solution**: 
1. Refresh the page and try again
2. Check browser settings for screen capture permissions
3. Ensure HTTPS (required for screen capture in most browsers)

#### No Video Recording
```
Warning: MediaRecorder not supported, falling back to screenshots
```
**Solution**:
- Update browser to latest version
- Use Chrome/Edge/Firefox (Safari doesn't support MediaRecorder)
- Check if VP8 codec is available

#### Storage Full
```
Error: Cannot save recording - storage limit exceeded
```
**Solution**:
1. Download and delete old recordings
2. Clear browser localStorage: `localStorage.clear()`
3. Increase storage limit in settings

#### Performance Issues
```
Warning: High CPU usage during recording
```
**Solution**:
- Lower video quality in settings
- Reduce mouse capture frequency
- Close unnecessary browser tabs
- Use hardware acceleration if available

### 🔧 **Advanced Debugging**

#### Browser Console
```javascript
// Check recording status
console.log(window.recorder.isRecording);

// View stored recordings  
console.log(localStorage.getItem('mkd_recordings'));

// Monitor performance
console.log(window.recorder.recordingDuration, 'seconds');
console.log(window.recorder.actions.length, 'actions captured');
```

#### Network Issues
- **HTTPS Required**: Screen capture APIs require secure connection
- **CORS Issues**: Ensure proper file serving (use local server, not file://)
- **WebSocket Fallback**: Browser version doesn't need WebSocket connection

---

## 📊 **Performance Optimization**

### 🚀 **Recording Performance**

#### Video Quality vs Performance
```javascript
// High Quality (higher CPU usage)
const highQualityOptions = {
  videoBitsPerSecond: 5000000,  // 5 Mbps
  frameRate: { ideal: 60 }      // 60 FPS
};

// Balanced (recommended)
const balancedOptions = {
  videoBitsPerSecond: 2500000,  // 2.5 Mbps  
  frameRate: { ideal: 30 }      // 30 FPS
};

// Low Resources (lower CPU usage)
const lowResourceOptions = {
  videoBitsPerSecond: 1000000,  // 1 Mbps
  frameRate: { ideal: 15 }      // 15 FPS
};
```

#### Memory Management
- **Automatic Cleanup**: Old recordings automatically removed
- **Chunk Processing**: Video recorded in 1-second chunks
- **Action Throttling**: Mouse movements throttled to reduce memory usage

### 💾 **Storage Optimization**

#### Browser Storage Limits
- **Chrome**: ~5MB localStorage per domain
- **Firefox**: ~10MB localStorage per domain  
- **Safari**: ~5MB localStorage per domain
- **Edge**: ~5MB localStorage per domain

#### Storage Strategy
```javascript
// Automatic storage management
if (storageUsed > STORAGE_LIMIT) {
  // Remove oldest recordings first
  while (recordings.length > MAX_RECORDINGS) {
    recordings.shift();
  }
  
  // Compress action data
  compressedActions = compressActionData(actions);
}
```

---

## 🔮 **Future Enhancements**

### 📋 **Planned Features**

#### Short Term (Next Release)
- [ ] **Export to MP4**: Convert WebM to MP4 for wider compatibility
- [ ] **Cloud Storage**: Integration with Google Drive, Dropbox
- [ ] **Annotation Tools**: Add text, arrows, highlights to recordings
- [ ] **Batch Processing**: Process multiple recordings simultaneously

#### Medium Term
- [ ] **Browser Extension**: Enhanced permissions for system-level features
- [ ] **Collaboration**: Share recordings with team members
- [ ] **AI Analysis**: Automatic action pattern recognition
- [ ] **Mobile Support**: Touch gesture recording for tablets

#### Long Term
- [ ] **Desktop App**: Electron wrapper with native system access
- [ ] **Plugin System**: Custom action handlers and processors
- [ ] **Integration APIs**: Embed recorder in other applications
- [ ] **Advanced Analytics**: User behavior analysis and reporting

### 🤝 **Contributing**

#### For Developers
```bash
# Clone repository
git clone https://github.com/your-username/mkd-automation.git

# Navigate to web version
cd mkd-automation/web_gui/docs

# Start development server
python -m http.server 3000

# Make changes and test locally
# Submit pull requests for review
```

#### Feature Requests
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Share ideas and usage scenarios
- **Pull Requests**: Contribute code improvements
- **Documentation**: Help improve guides and examples

---

## 📄 **License & Credits**

### 📜 **MIT License**
This project is open source under MIT License. See [LICENSE](LICENSE) file for details.

### 🙏 **Acknowledgments**
- **MediaRecorder API**: Browser-native video recording
- **Screen Capture API**: Cross-platform screen access
- **Canvas API**: Action overlay rendering
- **Web Storage API**: Local data persistence
- **GitHub Pages**: Free, reliable static hosting

### 👥 **Community**
- **Contributors**: See [CONTRIBUTORS.md](CONTRIBUTORS.md)
- **Issues**: [GitHub Issues](https://github.com/your-username/mkd-automation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/mkd-automation/discussions)

---

<div align="center">

**[🌐 Live Demo](http://localhost:3000)** | **[📖 Documentation](README.md)** | **[⭐ Star on GitHub](https://github.com/your-username/mkd-automation)**

**Made with ❤️ for the automation community**

</div>