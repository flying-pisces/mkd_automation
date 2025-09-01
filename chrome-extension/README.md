# MKD Automation Chrome Extension

A powerful browser automation tool that records your interactions with web pages and replays them with precision. Perfect for QA engineers, developers, and anyone who needs to automate repetitive web tasks.

## Features

- **One-Click Recording** - Start recording with a single click
- **Smart Element Detection** - Intelligent CSS selector generation  
- **Cross-Platform Support** - Works on Windows, Mac, and Linux
- **Native Integration** - Seamless connection with MKD desktop app
- **Secure & Private** - All data stored locally, no cloud uploads
- **Visual Feedback** - Real-time recording indicators and progress

## Installation

### From Chrome Web Store (Recommended)
1. Visit the [Chrome Web Store](https://chrome.google.com/webstore) (link pending)
2. Search for "MKD Automation"
3. Click "Add to Chrome"
4. Follow the installation prompts

### Manual Installation (Developer Mode)
1. Download the latest release from [GitHub](https://github.com/flying-pisces/mkd_automation)
2. Open Chrome and go to `chrome://extensions/`
3. Enable "Developer mode" in the top right
4. Click "Load unpacked" and select the `chrome-extension` directory
5. The extension will appear in your toolbar

## Quick Start

1. **Install Native Host**: Run the installer script to enable Chrome-Python communication
   ```bash
   python install_native_host.py
   ```

2. **Start Recording**: Click the MKD icon in your browser toolbar and press "Start Recording"

3. **Interact with Pages**: Navigate and interact with web pages normally - all actions are captured

4. **Stop Recording**: Click "Stop Recording" to save your automation script

5. **Playback**: Use the MKD desktop application to replay your recorded actions

## Requirements

- **Chrome/Chromium** 88+ (Manifest V3 support)
- **Native Messaging Host** - MKD Python backend
- **Operating System** - Windows 10+, macOS 10.14+, or Linux

## Permissions

The extension requires the following permissions:

- **activeTab** - Record interactions on the current webpage
- **storage** - Save recording settings and preferences  
- **nativeMessaging** - Connect to MKD desktop application

## Privacy & Security

- **Local Processing** - All recording data stays on your device
- **No Tracking** - No analytics, telemetry, or user tracking
- **Secure Communication** - Native messaging uses OS-level security
- **Open Source** - Full source code available for audit

## Development

### Setup
```bash
git clone https://github.com/flying-pisces/mkd_automation
cd mkd_automation/chrome-extension
```

### Testing
```bash
# Run upload validation tests
python tests/chrome_store_upload_test.py

# Run unit tests  
python tests/test_suite.js

# Run end-to-end tests
python tests/e2e_test.py
```

### Building
```bash
# Create distribution package
python tests/chrome_store_upload_test.py
# Output: dist/mkd-automation-{version}.zip
```

## Troubleshooting

### Extension Icon Shows Warning
- Ensure native messaging host is installed: `python install_native_host.py`
- Check that MKD desktop application is running
- Verify Windows registry entries (Windows only)

### Recording Not Working
- Check that activeTab permission is granted
- Ensure you're on a supported webpage (not chrome:// pages)
- Try refreshing the page and restarting recording

### Connection Issues
- Restart the MKD desktop application
- Check firewall/antivirus settings
- Run connection test: `python chrome-extension/tests/test_chrome_connection.py`

## Support

- **Documentation**: [GitHub Wiki](https://github.com/flying-pisces/mkd_automation/wiki)
- **Issues**: [GitHub Issues](https://github.com/flying-pisces/mkd_automation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/flying-pisces/mkd_automation/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](../CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Changelog

### Version 2.0.0
- Manifest V3 compatibility
- Enhanced UI with visual feedback
- Comprehensive error handling
- Native messaging integration
- Cross-platform installer
- Security improvements

### Version 1.0.0
- Initial release
- Basic recording functionality
- Chrome extension foundation