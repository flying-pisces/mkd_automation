#!/usr/bin/env python3
"""
Linux Package Creator for MKD Automation
Creates .deb packages, AppImages, and portable archives for Linux.
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
import stat
import json

class LinuxPackageCreator:
    """Creates various Linux distribution packages."""
    
    def __init__(self, executable_path, version="2.0.0"):
        self.executable_path = Path(executable_path)
        self.version = version
        self.project_root = Path(__file__).parent
        self.output_dir = self.project_root / "linux_packages"
        self.output_dir.mkdir(exist_ok=True)
        
    def create_deb_package(self):
        """Create a Debian (.deb) package."""
        print("📦 Creating .deb package...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            deb_dir = Path(temp_dir) / "mkd-automation"
            
            # Create directory structure
            debian_dir = deb_dir / "DEBIAN"
            usr_bin = deb_dir / "usr" / "bin"
            usr_share_apps = deb_dir / "usr" / "share" / "applications"
            usr_share_icons = deb_dir / "usr" / "share" / "icons" / "hicolor" / "48x48" / "apps"
            usr_share_doc = deb_dir / "usr" / "share" / "doc" / "mkd-automation"
            
            for directory in [debian_dir, usr_bin, usr_share_apps, usr_share_icons, usr_share_doc]:
                directory.mkdir(parents=True, exist_ok=True)
            
            # Control file
            control_content = f"""Package: mkd-automation
Version: {self.version}
Section: utils
Priority: optional
Architecture: amd64
Depends: python3, python3-tk, libx11-6
Maintainer: MKD Automation Team <support@mkd-automation.com>
Description: Cross-platform automation tool for GUI interactions
 MKD Automation is a comprehensive tool for capturing, analyzing,
 and reproducing user interactions across desktop applications.
 .
 Key features include:
  * Real-time capture of mouse, keyboard, and screen events
  * Intelligent playback with timing control
  * Cross-platform compatibility (Linux, macOS, Windows)
  * Portable automation scripts (.mkd format)
  * Web automation capabilities
  * System tray integration
Homepage: https://github.com/flying-pisces/mkd_automation
"""
            
            (debian_dir / "control").write_text(control_content)
            
            # Copy executable
            shutil.copy2(self.executable_path, usr_bin / "mkd-automation")
            (usr_bin / "mkd-automation").chmod(0o755)
            
            # Desktop file
            desktop_content = f"""[Desktop Entry]
Name=MKD Automation
GenericName=Automation Tool
Comment=Cross-platform automation tool for GUI interactions
Exec=mkd-automation
Icon=mkd-automation
Terminal=false
Type=Application
Categories=Utility;Development;System;
Keywords=automation;gui;testing;recording;playback;
StartupNotify=true
Version={self.version}
"""
            
            (usr_share_apps / "mkd-automation.desktop").write_text(desktop_content)
            
            # Create simple icon (text-based for now)
            icon_content = self._create_simple_icon()
            if icon_content:
                (usr_share_icons / "mkd-automation.png").write_bytes(icon_content)
            
            # Documentation
            readme_content = f"""MKD Automation v{self.version}

A cross-platform automation tool for capturing and reproducing user interactions.

Usage:
  mkd-automation                    # Launch GUI interface
  mkd-automation --help            # Show command line options
  mkd-automation script.mkd        # Play automation script

For more information, visit:
https://github.com/flying-pisces/mkd_automation
"""
            
            (usr_share_doc / "README").write_text(readme_content)
            
            # Changelog
            changelog_content = f"""mkd-automation ({self.version}) stable; urgency=medium

  * Initial release
  * GUI automation capabilities
  * Cross-platform support
  * Web automation features

 -- MKD Automation Team <support@mkd-automation.com>  {self._get_rfc2822_date()}
"""
            
            (usr_share_doc / "changelog").write_text(changelog_content)
            
            # Copyright
            copyright_content = """Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: mkd-automation
Upstream-Contact: support@mkd-automation.com

Files: *
Copyright: 2024 MKD Automation Team
License: MIT
"""
            
            (usr_share_doc / "copyright").write_text(copyright_content)
            
            # Build package
            deb_file = self.output_dir / f"mkd-automation_{self.version}_amd64.deb"
            
            try:
                subprocess.run([
                    "dpkg-deb", "--build", str(deb_dir), str(deb_file)
                ], check=True, capture_output=True)
                
                print(f"   ✅ Created: {deb_file.name}")
                return deb_file
                
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"   ❌ Failed to create .deb package: {e}")
                return None
    
    def create_appimage(self):
        """Create an AppImage package."""
        print("📦 Creating AppImage...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            appdir = Path(temp_dir) / "MKD_Automation.AppDir"
            
            # Create AppDir structure
            usr_bin = appdir / "usr" / "bin"
            usr_share_apps = appdir / "usr" / "share" / "applications"
            usr_share_icons = appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps"
            
            for directory in [usr_bin, usr_share_apps, usr_share_icons]:
                directory.mkdir(parents=True, exist_ok=True)
            
            # Copy executable
            shutil.copy2(self.executable_path, usr_bin / "mkd-automation")
            (usr_bin / "mkd-automation").chmod(0o755)
            
            # AppRun script
            apprun_content = f"""#!/bin/bash
# AppRun script for MKD Automation

APPDIR="$(dirname "$(readlink -f "$0")")"
export PATH="$APPDIR/usr/bin:$PATH"
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$LD_LIBRARY_PATH"

cd "$APPDIR"
exec "$APPDIR/usr/bin/mkd-automation" "$@"
"""
            
            apprun_file = appdir / "AppRun"
            apprun_file.write_text(apprun_content)
            apprun_file.chmod(0o755)
            
            # Desktop file (root level for AppImage)
            desktop_content = f"""[Desktop Entry]
Name=MKD Automation
Exec=mkd-automation
Icon=mkd-automation
Type=Application
Categories=Utility;
Version={self.version}
"""
            
            (appdir / "mkd-automation.desktop").write_text(desktop_content)
            
            # Icon (create a simple PNG icon)
            icon_content = self._create_simple_icon()
            if icon_content:
                (appdir / "mkd-automation.png").write_bytes(icon_content)
                (usr_share_icons / "mkd-automation.png").write_bytes(icon_content)
            
            # Create AppImage using appimagetool (if available)
            appimage_file = self.output_dir / f"MKD_Automation-{self.version}-x86_64.AppImage"
            
            try:
                # Try to download appimagetool if not available
                appimagetool = self._get_appimagetool()
                if appimagetool:
                    subprocess.run([
                        str(appimagetool), str(appdir), str(appimage_file)
                    ], check=True, env={"ARCH": "x86_64"})
                    
                    print(f"   ✅ Created: {appimage_file.name}")
                    return appimage_file
                else:
                    print("   ⚠️  AppImageTool not available - creating tar.gz instead")
                    return self._create_appdir_archive(appdir)
                    
            except subprocess.CalledProcessError as e:
                print(f"   ❌ AppImage creation failed: {e}")
                return self._create_appdir_archive(appdir)
    
    def create_portable_archive(self):
        """Create a portable tar.gz archive."""
        print("📦 Creating portable archive...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_dir = Path(temp_dir) / "mkd-automation"
            archive_dir.mkdir()
            
            # Copy executable
            shutil.copy2(self.executable_path, archive_dir / "mkd-automation")
            (archive_dir / "mkd-automation").chmod(0o755)
            
            # Create launcher script
            launcher_content = f"""#!/bin/bash
# MKD Automation Portable Launcher
# Version {self.version}

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
EXECUTABLE="$SCRIPT_DIR/mkd-automation"

# Set up environment
export MKD_AUTOMATION_PORTABLE=1
export MKD_AUTOMATION_HOME="$SCRIPT_DIR"

# Check for required dependencies
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Launch application
echo "Starting MKD Automation..."
"$EXECUTABLE" "$@"
"""
            
            launcher_file = archive_dir / "launch-mkd-automation.sh"
            launcher_file.write_text(launcher_content)
            launcher_file.chmod(0o755)
            
            # README
            readme_content = f"""# MKD Automation v{self.version} - Portable Linux Version

## Quick Start
1. Extract this archive to any directory
2. Run: ./launch-mkd-automation.sh

## Direct Execution
You can also run the executable directly:
```bash
./mkd-automation
```

## System Requirements
- Linux with X11 or Wayland
- Python 3.6+ (usually pre-installed)
- Tkinter (python3-tk package)

## Installation of Dependencies
Ubuntu/Debian:
```bash
sudo apt-get install python3 python3-tk
```

CentOS/RHEL/Fedora:
```bash
sudo dnf install python3 python3-tkinter
```

## Features
- Complete GUI automation tool
- No installation required
- Runs from any location
- Full feature set included

## Support
Visit: https://github.com/flying-pisces/mkd_automation
"""
            
            (archive_dir / "README.md").write_text(readme_content)
            
            # Create tar.gz
            import tarfile
            
            archive_file = self.output_dir / f"MKD_Automation_Portable_Linux_v{self.version}.tar.gz"
            
            with tarfile.open(archive_file, 'w:gz') as tar:
                tar.add(archive_dir, arcname='mkd-automation', recursive=True)
            
            print(f"   ✅ Created: {archive_file.name}")
            return archive_file
    
    def _create_simple_icon(self):
        """Create a simple PNG icon programmatically."""
        try:
            # Try to create a simple icon using PIL if available
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a 48x48 icon
            img = Image.new('RGBA', (48, 48), (0, 100, 200, 255))
            draw = ImageDraw.Draw(img)
            
            # Draw simple automation symbol
            draw.rectangle([8, 8, 40, 40], outline=(255, 255, 255), width=2)
            draw.ellipse([16, 16, 32, 32], fill=(255, 255, 255))
            draw.text((20, 20), "M", fill=(0, 100, 200))
            
            # Save to bytes
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except ImportError:
            # PIL not available - return None to skip icon
            return None
    
    def _get_rfc2822_date(self):
        """Get current date in RFC 2822 format."""
        from email.utils import formatdate
        return formatdate(localtime=True)
    
    def _get_appimagetool(self):
        """Download or find appimagetool."""
        # Check if already available
        if shutil.which("appimagetool"):
            return Path("appimagetool")
        
        # Try to download to temp location
        appimagetool_path = self.output_dir / "appimagetool"
        
        try:
            import urllib.request
            
            print("   📥 Downloading appimagetool...")
            urllib.request.urlretrieve(
                "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage",
                str(appimagetool_path)
            )
            
            appimagetool_path.chmod(0o755)
            return appimagetool_path
            
        except Exception as e:
            print(f"   ⚠️  Could not download appimagetool: {e}")
            return None
    
    def _create_appdir_archive(self, appdir):
        """Create archive from AppDir when AppImageTool isn't available."""
        import tarfile
        
        archive_file = self.output_dir / f"MKD_Automation_AppDir_v{self.version}.tar.gz"
        
        with tarfile.open(archive_file, 'w:gz') as tar:
            tar.add(appdir, arcname='MKD_Automation.AppDir', recursive=True)
        
        print(f"   ✅ Created AppDir archive: {archive_file.name}")
        return archive_file
    
    def create_install_script(self):
        """Create installation script."""
        install_script_content = f"""#!/bin/bash
# MKD Automation Linux Installer v{self.version}

set -e

echo "🚀 MKD Automation Linux Installer"
echo "=================================="

# Check if running as root for system install
if [[ $EUID -eq 0 ]]; then
    INSTALL_DIR="/usr/local/bin"
    DESKTOP_DIR="/usr/share/applications"
    ICON_DIR="/usr/share/icons/hicolor/48x48/apps"
    echo "📁 Installing system-wide to $INSTALL_DIR"
else
    INSTALL_DIR="$HOME/.local/bin"
    DESKTOP_DIR="$HOME/.local/share/applications"
    ICON_DIR="$HOME/.local/share/icons/hicolor/48x48/apps"
    echo "📁 Installing to user directory: $INSTALL_DIR"
fi

# Create directories
mkdir -p "$INSTALL_DIR" "$DESKTOP_DIR" "$ICON_DIR"

# Install executable
echo "📦 Installing executable..."
cp mkd-automation "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/mkd-automation"

# Install desktop file
echo "🖥️  Installing desktop integration..."
cat > "$DESKTOP_DIR/mkd-automation.desktop" << EOF
[Desktop Entry]
Name=MKD Automation
GenericName=Automation Tool
Comment=Cross-platform automation tool
Exec=mkd-automation
Icon=mkd-automation
Terminal=false
Type=Application
Categories=Utility;Development;
Version={self.version}
EOF

# Update desktop database if available
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo "✅ Installation complete!"
echo ""
echo "🎯 You can now:"
echo "   • Run 'mkd-automation' from terminal"
echo "   • Find 'MKD Automation' in your applications menu"
echo ""
echo "🔧 To uninstall, run:"
echo "   rm '$INSTALL_DIR/mkd-automation'"
echo "   rm '$DESKTOP_DIR/mkd-automation.desktop'"
"""
        
        install_script = self.output_dir / "install.sh"
        install_script.write_text(install_script_content)
        install_script.chmod(0o755)
        
        print(f"✅ Created install script: {install_script.name}")
        return install_script
    
    def create_all_packages(self):
        """Create all Linux package types."""
        print(f"🐧 Creating Linux packages for {self.executable_path.name}...")
        
        packages = []
        
        # Create each package type
        deb_package = self.create_deb_package()
        if deb_package:
            packages.append(deb_package)
        
        appimage = self.create_appimage()
        if appimage:
            packages.append(appimage)
        
        portable = self.create_portable_archive()
        if portable:
            packages.append(portable)
        
        install_script = self.create_install_script()
        if install_script:
            packages.append(install_script)
        
        # Create summary
        print(f"\n✅ Created {len(packages)} Linux packages:")
        total_size = 0
        
        for package in packages:
            if package.exists():
                size = package.stat().st_size / (1024 * 1024)  # MB
                total_size += size
                print(f"   📦 {package.name} ({size:.1f} MB)")
        
        print(f"\n📈 Total size: {total_size:.1f} MB")
        print(f"📁 Output directory: {self.output_dir}")
        
        return packages

def main():
    """Entry point."""
    if len(sys.argv) != 2:
        print("Usage: python create_linux_package.py <executable_path>")
        print("Example: python create_linux_package.py dist/mkd-automation")
        sys.exit(1)
    
    executable_path = sys.argv[1]
    if not Path(executable_path).exists():
        print(f"Error: Executable not found: {executable_path}")
        sys.exit(1)
    
    creator = LinuxPackageCreator(executable_path)
    packages = creator.create_all_packages()
    
    print("\n🚀 Linux packages ready for distribution!")

if __name__ == "__main__":
    main()