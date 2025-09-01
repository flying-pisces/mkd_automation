# MKD Automation - Multi-Platform Build Instructions

## Quick Start
```bash
# Build for current platform
python build_universal.py

# Build for all available platforms
python build_all_platforms.py

# Linux-specific build (requires Docker)
./build_linux.sh
```

## Platform-Specific Instructions

### macOS
**Requirements:**
- macOS 10.13+
- Python 3.9+
- Xcode Command Line Tools

**Build:**
```bash
pip install pyinstaller
python build_universal.py
```

**Output:** `.app` bundle, `.dmg` installer, portable `.zip`

### Linux (Ubuntu 22+)
**Requirements:**
- Ubuntu 22.04 or equivalent
- Python 3.9+
- Development tools

**Build:**
```bash
sudo apt-get update
sudo apt-get install python3-tk libx11-dev build-essential
pip install pyinstaller
python build_universal.py
```

**Output:** Single executable, `.deb` package, `.tar.gz` archive

**Docker Build (Recommended):**
```bash
./build_linux.sh
```

### Windows
**Requirements:**
- Windows 10/11
- Python 3.9+
- Visual Studio Build Tools

**Build:**
```bash
pip install pyinstaller
python build_universal.py
```

**Output:** Single `.exe`, installer package

## Automated Builds

### GitHub Actions
The project includes automated build workflows for all platforms.
Push a tag to trigger multi-platform builds:

```bash
git tag v2.0.0
git push origin v2.0.0
```

### Docker Builds
Use Docker for consistent Linux builds:

```bash
docker build -f docker/Dockerfile.ubuntu22 -t mkd-linux-builder .
docker run -v $(pwd)/release:/output mkd-linux-builder
```

## Build Output

All builds create the following structure:
```
release/
├── MKD_Automation_macOS_*.zip      # macOS app bundle
├── MKD_Automation_macOS_*.dmg      # macOS installer
├── MKD_Automation_Linux_*.tar.gz   # Linux portable
├── mkd-automation_*.deb            # Linux package
├── MKD_Automation_Windows_*.zip    # Windows portable
├── MKD_Automation_Windows_*.exe    # Windows installer
├── README.md                       # User instructions
└── release_info.json              # Build metadata
```

## Troubleshooting

### Common Issues
1. **Import Errors**: Install all dependencies from `requirements.txt`
2. **Permission Errors**: Run `chmod +x` on shell scripts
3. **Docker Issues**: Ensure Docker is running and accessible
4. **Platform Dependencies**: Install platform-specific development tools

### Platform-Specific Issues

**macOS:**
- Code signing errors: Use `--osx-bundle-identifier`
- App bundle issues: Check Info.plist configuration

**Linux:**
- X11 errors: Install `libx11-dev` and related packages
- Font issues: Install system fonts package
- AppImage creation: Install `AppImageTool`

**Windows:**
- Missing DLLs: Include Visual C++ Redistributable
- Antivirus warnings: Expected for unsigned executables

## Contributing

To add a new platform:
1. Create platform-specific `.spec` file
2. Add platform detection in `build_universal.py`
3. Update CI/CD workflows
4. Test on target platform

## Support

For build issues:
- Check logs in `build.log`
- Review PyInstaller warnings
- Test on clean virtual environment
- Report issues with platform details

---
Last updated: 2025-09-01
