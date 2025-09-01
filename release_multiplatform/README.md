# MKD Automation v2.0.0 - Universal Release

## Platform-Specific Downloads

### macOS
- **MKD_Automation_macOS_*.dmg** - Native macOS installer (double-click to install)
- **MKD_Automation_macOS_*.zip** - App bundle (extract and drag to Applications)
- **MKD_Automation_Standalone_macOS_*.zip** - Portable version

### Linux (Ubuntu 22+)
- **mkd-automation_*_amd64.deb** - Ubuntu/Debian package (sudo dpkg -i package.deb)
- **MKD_Automation_Linux_*.tar.gz** - Portable version (extract and run)
- **MKD_Automation_Linux_*.AppImage** - Universal Linux app (chmod +x and run)

### Windows
- **MKD_Automation_Windows_*.zip** - Portable version (extract and run .exe)
- **MKD_Automation_Windows_*.exe** - Windows installer

## Installation Instructions

### macOS
1. Download the .dmg file
2. Double-click to mount
3. Drag MKD Automation to Applications folder
4. Launch from Launchpad or Applications

**Alternative (Portable):**
1. Download the .zip file
2. Extract anywhere
3. Double-click MKD_Automation.app

### Linux Ubuntu 22+
**Method 1 (Package Manager):**
```bash
sudo dpkg -i mkd-automation_*.deb
mkd-automation
```

**Method 2 (Portable):**
```bash
tar -xzf MKD_Automation_Linux_*.tar.gz
chmod +x mkd-automation
./mkd-automation
```

**Method 3 (AppImage):**
```bash
chmod +x MKD_Automation_*.AppImage
./MKD_Automation_*.AppImage
```

### Windows
**Method 1 (Installer):**
1. Download the .exe installer
2. Run as Administrator
3. Follow installation wizard
4. Launch from Start Menu

**Method 2 (Portable):**
1. Download the .zip file
2. Extract to any folder
3. Run MKD_Automation.exe

## Features
- ✅ **Zero Dependencies** - No Python or additional software required
- ✅ **Fully Portable** - Run from USB drive or any location
- ✅ **Cross-Platform** - Same features on macOS, Linux, and Windows
- ✅ **GUI Interface** - Intuitive graphical user interface
- ✅ **System Integration** - System tray, native dialogs, file associations
- ✅ **Automation Scripts** - Record, edit, and replay .mkd automation files
- ✅ **Web Automation** - Advanced web browser automation capabilities

## System Requirements

### macOS
- macOS 10.13 (High Sierra) or later
- Intel x64 or Apple Silicon (ARM64)

### Linux
- Ubuntu 22.04+ or equivalent distribution
- X11 or Wayland display server
- glibc 2.31+

### Windows
- Windows 10/11 (64-bit)
- .NET Framework 4.7.2+ (usually pre-installed)

## Build Information
- **Version**: 2.0.0
- **Build Date**: 2025-09-01
- **Python**: 3.12.7
- **Platform**: darwin_arm64

## Support & Documentation
- **GitHub**: https://github.com/flying-pisces/mkd_automation
- **Documentation**: https://mkd-automation.readthedocs.io
- **Issues**: https://github.com/flying-pisces/mkd_automation/issues

## Security Note
All executables are unsigned. You may need to allow execution in your system's security settings:
- **macOS**: System Preferences > Security & Privacy > Allow apps downloaded from anywhere
- **Linux**: chmod +x for executable files
- **Windows**: Windows Defender SmartScreen > More info > Run anyway

---
Built with ❤️ using PyInstaller • Cross-platform automation made easy
