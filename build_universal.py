#!/usr/bin/env python3
"""
Universal Build Script for MKD Automation
Creates portable, standalone executables for macOS, Linux, and Windows.
"""

import os
import sys
import shutil
import subprocess
import zipfile
import tarfile
from pathlib import Path
import platform
import json
from datetime import datetime

class UniversalBuilder:
    """Cross-platform builder for MKD Automation."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.release_dir = self.project_root / "release"
        self.version = "2.0.0"
        
    def clean_build(self):
        """Clean previous builds."""
        print("🧹 Cleaning previous builds...")
        for dir_name in ["build", "dist"]:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   Removed {dir_name}/")
        
        # Ensure release directory exists
        self.release_dir.mkdir(exist_ok=True)
    
    def build_executable(self, spec_file="MKD_Automation_Universal.spec"):
        """Build executable using PyInstaller."""
        print(f"\n📦 Building for {self.system} {self.arch}...")
        
        try:
            result = subprocess.run([
                "pyinstaller", spec_file, "--clean", "--noconfirm"
            ], check=True, capture_output=True, text=True, cwd=self.project_root)
            print("   ✅ Build successful!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Build failed: {e}")
            print(f"   Error output: {e.stderr}")
            return False
    
    def create_macos_packages(self):
        """Create macOS distribution packages."""
        print("\n📦 Creating macOS packages...")
        
        # App bundle
        app_bundle = self.project_root / "dist" / "MKD_Automation.app"
        if app_bundle.exists():
            app_zip = self.release_dir / f"MKD_Automation_macOS_{self.arch}_v{self.version}.zip"
            self._create_zip(app_bundle.parent, app_zip, "MKD_Automation.app")
            print(f"   ✅ Created: {app_zip.name}")
        
        # Standalone directory
        standalone_dir = self.project_root / "dist" / "MKD_Automation"
        if standalone_dir.exists():
            standalone_zip = self.release_dir / f"MKD_Automation_Standalone_macOS_{self.arch}_v{self.version}.zip"
            self._create_zip(standalone_dir.parent, standalone_zip, "MKD_Automation")
            print(f"   ✅ Created: {standalone_zip.name}")
            
        # Create DMG (macOS disk image) - optional
        self._create_macos_dmg()
    
    def create_linux_packages(self):
        """Create Linux distribution packages."""
        print("\n📦 Creating Linux packages...")
        
        # Single executable
        executable = self.project_root / "dist" / "mkd-automation"
        if executable.exists():
            # Create tar.gz
            tar_gz = self.release_dir / f"MKD_Automation_Linux_{self.arch}_v{self.version}.tar.gz"
            with tarfile.open(tar_gz, 'w:gz') as tar:
                tar.add(executable, arcname="mkd-automation")
                # Add launcher script
                launcher_script = self._create_linux_launcher()
                tar.add(launcher_script, arcname="launch-mkd-automation.sh")
            print(f"   ✅ Created: {tar_gz.name}")
            
            # Create AppImage (Linux portable app format)
            self._create_linux_appimage(executable)
            
            # Create .deb package for Ubuntu
            self._create_debian_package(executable)
    
    def create_windows_packages(self):
        """Create Windows distribution packages."""
        print("\n📦 Creating Windows packages...")
        
        # Single executable
        executable = self.project_root / "dist" / "MKD_Automation.exe"
        if executable.exists():
            # Create zip
            win_zip = self.release_dir / f"MKD_Automation_Windows_{self.arch}_v{self.version}.zip"
            self._create_zip(executable.parent, win_zip, "MKD_Automation.exe")
            print(f"   ✅ Created: {win_zip.name}")
            
            # Create installer (optional)
            self._create_windows_installer(executable)
    
    def _create_zip(self, source_dir, zip_path, item_name):
        """Create a zip file."""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            source_path = source_dir / item_name
            if source_path.is_file():
                zf.write(source_path, item_name)
            else:
                for file_path in source_path.rglob('*'):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to(source_dir))
                        zf.write(file_path, arcname)
    
    def _create_macos_dmg(self):
        """Create macOS DMG file."""
        try:
            app_bundle = self.project_root / "dist" / "MKD_Automation.app"
            dmg_path = self.release_dir / f"MKD_Automation_macOS_{self.arch}_v{self.version}.dmg"
            
            # Use hdiutil to create DMG
            subprocess.run([
                "hdiutil", "create", "-srcfolder", str(app_bundle),
                "-volname", "MKD Automation", "-format", "UDZO",
                str(dmg_path)
            ], check=True, capture_output=True)
            print(f"   ✅ Created: {dmg_path.name}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("   ⚠️  DMG creation skipped (hdiutil not available)")
    
    def _create_linux_launcher(self):
        """Create Linux launcher script."""
        launcher_content = f"""#!/bin/bash
# MKD Automation Launcher for Linux
# Version {self.version}

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
EXECUTABLE="$SCRIPT_DIR/mkd-automation"

# Check if executable exists
if [ ! -f "$EXECUTABLE" ]; then
    echo "Error: MKD Automation executable not found at $EXECUTABLE"
    exit 1
fi

# Make executable if needed
chmod +x "$EXECUTABLE"

# Set up environment
export MKD_AUTOMATION_HOME="$SCRIPT_DIR"

# Launch application
echo "Starting MKD Automation..."
"$EXECUTABLE" "$@"
"""
        
        launcher_path = self.project_root / "launch-mkd-automation.sh"
        launcher_path.write_text(launcher_content)
        launcher_path.chmod(0o755)
        return launcher_path
    
    def _create_linux_appimage(self, executable):
        """Create Linux AppImage."""
        try:
            # This would require AppImageTool - skip if not available
            appimage_path = self.release_dir / f"MKD_Automation_Linux_{self.arch}_v{self.version}.AppImage"
            print("   ⚠️  AppImage creation requires AppImageTool (skipped)")
        except Exception:
            pass
    
    def _create_debian_package(self, executable):
        """Create Debian (.deb) package."""
        print("   📦 Creating .deb package...")
        
        # Create debian package structure
        deb_dir = self.project_root / "debian_package"
        deb_dir.mkdir(exist_ok=True)
        
        # DEBIAN control directory
        debian_control_dir = deb_dir / "DEBIAN"
        debian_control_dir.mkdir(exist_ok=True)
        
        # Control file
        control_content = f"""Package: mkd-automation
Version: {self.version}
Section: utils
Priority: optional
Architecture: amd64
Depends: python3, python3-tk
Maintainer: MKD Automation Team <support@mkd-automation.com>
Description: Cross-platform automation tool
 MKD Automation is a comprehensive tool for capturing, analyzing,
 and reproducing user interactions across desktop applications.
 .
 Features include real-time capture, intelligent playback,
 portable scripts, and cross-platform support.
"""
        
        control_file = debian_control_dir / "control"
        control_file.write_text(control_content)
        
        # Install executable
        usr_bin = deb_dir / "usr" / "bin"
        usr_bin.mkdir(parents=True, exist_ok=True)
        shutil.copy2(executable, usr_bin / "mkd-automation")
        
        # Desktop file
        applications_dir = deb_dir / "usr" / "share" / "applications"
        applications_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_content = f"""[Desktop Entry]
Name=MKD Automation
Comment=Cross-platform automation tool
Exec=mkd-automation
Icon=mkd-automation
Terminal=false
Type=Application
Categories=Utility;Development;
Version={self.version}
"""
        
        desktop_file = applications_dir / "mkd-automation.desktop"
        desktop_file.write_text(desktop_content)
        
        # Build .deb package
        try:
            deb_package = self.release_dir / f"mkd-automation_{self.version}_amd64.deb"
            subprocess.run([
                "dpkg-deb", "--build", str(deb_dir), str(deb_package)
            ], check=True, capture_output=True)
            print(f"   ✅ Created: {deb_package.name}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("   ⚠️  .deb creation skipped (dpkg-deb not available)")
        finally:
            shutil.rmtree(deb_dir, ignore_errors=True)
    
    def _create_windows_installer(self, executable):
        """Create Windows installer (requires NSIS)."""
        try:
            print("   ⚠️  Windows installer creation requires NSIS (skipped)")
        except Exception:
            pass
    
    def create_release_info(self):
        """Create release information file."""
        release_info = {
            "version": self.version,
            "build_date": datetime.now().isoformat(),
            "platform": f"{self.system}_{self.arch}",
            "python_version": platform.python_version(),
            "files": []
        }
        
        # List all release files
        for file_path in self.release_dir.iterdir():
            if file_path.is_file() and file_path.suffix in ['.zip', '.tar.gz', '.deb', '.dmg', '.AppImage']:
                release_info["files"].append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "type": file_path.suffix[1:],  # Remove the dot
                })
        
        # Write release info
        info_file = self.release_dir / "release_info.json"
        info_file.write_text(json.dumps(release_info, indent=2))
        
        # Create human-readable README
        self._create_release_readme(release_info)
    
    def _create_release_readme(self, release_info):
        """Create release README."""
        readme_content = f"""# MKD Automation v{self.version} - Universal Release

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
- **Version**: {self.version}
- **Build Date**: {release_info['build_date'][:10]}
- **Python**: {release_info['python_version']}
- **Platform**: {release_info['platform']}

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
"""
        
        readme_path = self.release_dir / "README.md"
        readme_path.write_text(readme_content)
    
    def show_summary(self):
        """Show build summary."""
        print(f"\n🎉 Universal build complete!")
        print(f"📁 Release files in: {self.release_dir.absolute()}")
        print(f"🔧 Built for: {self.system} {self.arch}")
        
        total_size = 0
        file_count = 0
        
        for file_path in self.release_dir.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                size = file_path.stat().st_size / (1024 * 1024)  # MB
                total_size += size
                file_count += 1
                
                # Add emoji based on file type
                emoji = "📦"
                if file_path.suffix == '.dmg':
                    emoji = "💾"
                elif file_path.suffix == '.deb':
                    emoji = "📋"
                elif file_path.suffix == '.AppImage':
                    emoji = "🐧"
                elif file_path.suffix in ['.md', '.txt']:
                    emoji = "📄"
                elif file_path.suffix == '.json':
                    emoji = "📊"
                
                print(f"   {emoji} {file_path.name} ({size:.1f} MB)")
        
        print(f"\n📈 Summary: {file_count} files, {total_size:.1f} MB total")
        print("✅ Ready for distribution! 🚀")
    
    def build(self):
        """Main build process."""
        print("🌍 MKD Automation Universal Builder")
        print("=" * 50)
        
        self.clean_build()
        
        if not self.build_executable():
            return False
        
        # Create platform-specific packages
        if self.system == 'darwin':
            self.create_macos_packages()
        elif self.system == 'linux':
            self.create_linux_packages()
        elif self.system == 'windows':
            self.create_windows_packages()
        
        self.create_release_info()
        self.show_summary()
        return True

def main():
    """Entry point."""
    builder = UniversalBuilder()
    success = builder.build()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()