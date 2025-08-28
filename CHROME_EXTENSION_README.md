# MKD Automation Chrome Extension

## Overview
MKD Automation is an advanced automation recording and playback platform with intelligent context awareness for Chrome browser.

## Features
- Record mouse and keyboard interactions
- Playback recorded automation scripts
- Native messaging integration with desktop application
- Intelligent context detection
- Cross-platform support (Windows, macOS, Linux)

## Installation

### From Chrome Web Store
1. Visit the Chrome Web Store
2. Search for "MKD Automation"
3. Click "Add to Chrome"

### Manual Installation (Developer Mode)
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked"
4. Select the `chrome-extension` folder from this repository

## Usage

### Recording
1. Click the MKD Automation icon in your Chrome toolbar
2. Click "Start Recording" to begin capturing interactions
3. Perform the actions you want to automate
4. Press Ctrl+Shift+R (Cmd+Shift+R on Mac) or click "Stop Recording"

### Playback
1. Click the MKD Automation icon
2. Select a saved automation script
3. Click "Play" to execute the automation

## Native Messaging Setup

The extension communicates with the MKD desktop application via native messaging.

### Installation
Run the installer script from the main application:
```bash
python src/mkd_v2/native_host/installer.py
```

This will install the native messaging host for your platform.

## Permissions

The extension requires the following permissions:
- **activeTab**: To interact with the current tab
- **storage**: To save automation scripts and settings
- **nativeMessaging**: To communicate with the desktop application

## Support

For issues or questions, please visit our [GitHub repository](https://github.com/mkd-automation/mkd-automation).

## License
MIT License - See LICENSE file for details.