# 🎬 MKD Web Recorder - GitHub Pages Edition

[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-brightgreen?logo=github)](https://your-username.github.io/mkd-automation/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Browser Support](https://img.shields.io/badge/Browser-Chrome%20%7C%20Edge%20%7C%20Firefox-blue)](https://caniuse.com/mediarecorder)

**Browser-based screen recording with intelligent action replay - no installation required!**

🌐 **[Live Demo](https://your-username.github.io/mkd-automation/)** | 📖 **[Full Documentation](https://github.com/your-username/mkd-automation)** | 🚀 **[Desktop Version](https://github.com/your-username/mkd-automation/releases)**

## ✨ What This Is

A powerful **browser-only** version of the MKD Automation recording system that runs entirely on GitHub Pages. No servers, no installation, no setup - just open and record!

### 🎯 Key Features

- **🎥 High-Quality Screen Recording** - WebM video capture up to 1080p 30fps
- **🖱️ Precise Mouse Tracking** - Every click, movement, and scroll recorded
- **⌨️ Keyboard Input Capture** - All keypresses including modifier combinations  
- **🎬 Intelligent Replay** - Video playback with synchronized action overlays
- **💾 Local Storage** - Recordings saved in browser, no cloud dependencies
- **📱 Cross-Platform** - Works on Windows, Mac, Linux in any modern browser
- **🔒 Privacy First** - Everything runs locally in your browser

## 🚀 Quick Start

### Option 1: Use Live Version
Visit **[https://your-username.github.io/mkd-automation/](https://your-username.github.io/mkd-automation/)** and start recording immediately!

### Option 2: Deploy Your Own
1. **Fork this repository**
2. **Enable GitHub Pages** in repository settings
3. **Access your deployment** at `https://your-username.github.io/your-repo-name/`

### Option 3: Run Locally
```bash
git clone https://github.com/your-username/mkd-automation.git
cd mkd-automation/web_gui/github-pages-version
# Open index.html in your browser or serve with any static server
python -m http.server 8000  # Python 3
# OR
npx serve .  # Node.js
```

## 📖 How to Use

### 🎬 Recording
1. **Click "📹 Start Recording"**
2. **Grant screen capture permission** when prompted
3. **Perform your actions** - everything is captured automatically
4. **Click "⏹️ Stop Recording"** when finished

### 🎥 Replay
1. **Click "🎬 Replay Recording"** to view your session
2. **Use playback controls** to play/pause/adjust speed
3. **Watch action overlays** showing your mouse clicks and key presses
4. **See real-time correlation** between video and actions

### 💾 Download
- **Click "💾 Download Recording"** to save:
  - `recording.webm` - High-quality video file
  - `actions.json` - Detailed action data with timestamps

## 🛠️ Technical Details

### Browser Requirements
| Feature | Chrome | Edge | Firefox | Safari |
|---------|--------|------|---------|--------|
| Screen Capture | ✅ | ✅ | ✅ | ⚠️* |
| Video Recording | ✅ | ✅ | ✅ | ❌ |
| Action Overlays | ✅ | ✅ | ✅ | ✅ |
| Local Storage | ✅ | ✅ | ✅ | ✅ |

*Safari requires user gesture for screen capture and doesn't support MediaRecorder

### What's Captured
```javascript
{
  "video": "High-quality WebM screen recording",
  "actions": [
    {
      "type": "mouse_down",
      "data": { "x": 245, "y": 167, "button": "left" },
      "timestamp": 1.234
    },
    {
      "type": "key_down", 
      "data": { "key": "Enter", "ctrlKey": false },
      "timestamp": 2.456
    }
  ],
  "metadata": {
    "duration": 45.2,
    "mouseActions": 127,
    "keyActions": 89,
    "videoSize": "12.3 MB"
  }
}
```

## 🔄 Comparison with Desktop Version

| Feature | GitHub Pages | Desktop Version |
|---------|-------------|-----------------|
| **Screen Recording** | ✅ | ✅ |
| **Mouse/Keyboard Capture** | ✅ | ✅ |
| **Action Replay** | ✅ | ✅ |
| **Local Storage** | ✅ | ✅ |
| **No Installation** | ✅ | ❌ |
| **Process Monitoring** | ❌ | ✅ |
| **System Integration** | ❌ | ✅ |
| **Task Manager Control** | ❌ | ✅ |
| **Semantic Analysis** | ❌ | ✅ |
| **Cross-App Tracking** | ❌ | ✅ |

## 🌐 GitHub Pages Deployment

### Automatic Deployment
This repository includes GitHub Actions for automatic deployment:

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./web_gui/github-pages-version
```

### Manual Deployment
1. **Go to repository Settings**
2. **Scroll to "Pages" section**  
3. **Select "Deploy from a branch"**
4. **Choose "main" branch and "/web_gui/github-pages-version" folder**
5. **Save and wait for deployment**

## 🔧 Customization

### Branding
Edit `index.html` to customize:
- Page title and headers
- GitHub repository links  
- Color scheme and styling
- Feature descriptions

### Recording Settings
Modify `recorder.js` to adjust:
- Video quality and framerate
- Action throttling rates
- Storage limits
- Overlay appearance

### UI Themes
Update `styles.css` for:
- Custom color palettes
- Layout modifications
- Responsive breakpoints
- Animation effects

## 🤝 Contributing

### For Browser Version
- **Bug reports**: Issues with browser compatibility
- **Feature requests**: Browser API capabilities
- **UI improvements**: Better user experience
- **Documentation**: Usage guides and examples

### For Desktop Features
See the [main repository](https://github.com/your-username/mkd-automation) for:
- System-level monitoring
- Process integration
- Advanced automation features

## 📊 Browser Analytics

The GitHub Pages version includes optional analytics to understand usage:
- **No personal data** is collected
- **Only aggregated statistics** (browser types, feature usage)
- **Fully GDPR compliant**
- **Easily disabled** in settings

## 🐛 Known Limitations

### Browser Sandbox Restrictions
- **Cannot monitor other applications** (only browser content)
- **No system process access** (Windows Task Manager integration unavailable)
- **Limited to screen capture permissions** granted by browser
- **Storage limited to browser's localStorage** (~5-10MB depending on browser)

### Safari-Specific Issues
- **MediaRecorder not supported** - screenshot fallback only
- **Screen capture requires user gesture** - may prompt repeatedly
- **WebM not supported** - videos may not play in Safari

### Storage Considerations
- **Large recordings consume browser storage** quickly
- **Automatic cleanup** removes old recordings to prevent storage overflow
- **Download immediately** for permanent storage

## 🎯 Use Cases

### 🎓 **Education & Training**
- Create interactive tutorials with action highlights
- Record software demonstrations
- Build step-by-step guides with visual feedback

### 🧪 **Testing & QA**  
- Document bug reproduction steps
- Create test case recordings
- Capture user interaction patterns

### 📝 **Documentation**
- Generate software usage videos
- Create onboarding materials
- Build feature demonstration videos

### 🎮 **Content Creation**
- Record gameplay or software usage
- Create tutorial content
- Document workflow processes

## 🔮 Roadmap

### Short Term
- [ ] **WebRTC integration** for real-time streaming
- [ ] **Cloud storage integration** (Google Drive, Dropbox)
- [ ] **Annotation tools** for post-recording markup
- [ ] **Export formats** (MP4, GIF, other formats)

### Medium Term  
- [ ] **Browser extension** for enhanced permissions
- [ ] **Collaboration features** for shared recordings
- [ ] **AI-powered highlights** for automatic action detection
- [ ] **Mobile support** for tablet/phone recording

### Long Term
- [ ] **Electron wrapper** for desktop-like experience
- [ ] **Plugin system** for custom action handlers
- [ ] **Integration APIs** for embedding in other applications

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MediaRecorder API** for enabling browser-based video capture
- **Screen Capture API** for cross-platform screen access  
- **GitHub Pages** for free, reliable static hosting
- **Open source community** for inspiration and feedback

---

<div align="center">

**[🌐 Try Live Demo](https://your-username.github.io/mkd-automation/)** | **[📖 Full Documentation](https://github.com/your-username/mkd-automation)** | **[⭐ Star on GitHub](https://github.com/your-username/mkd-automation)**

Made with ❤️ for the automation community

</div>