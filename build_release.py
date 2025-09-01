#!/usr/bin/env python3
"""
Build Release Script for MKD Automation
Creates portable, standalone executables for distribution.
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
import platform

def main():
    """Main build process."""
    print("🚀 MKD Automation Release Builder")
    print("=" * 50)
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Build with PyInstaller
    print("\n📦 Building standalone executable...")
    try:
        result = subprocess.run([
            "pyinstaller", "MKD_Automation.spec", "--clean"
        ], check=True, capture_output=True, text=True)
        print("   ✅ Build successful!")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Build failed: {e}")
        print(f"   Error output: {e.stderr}")
        return False
    
    # Create release packages
    print("\n📋 Creating release packages...")
    
    release_dir = Path("release")
    release_dir.mkdir(exist_ok=True)
    
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == "darwin":
        # Create .app bundle zip for macOS
        app_zip = release_dir / f"MKD_Automation_macOS_{arch}.zip"
        with zipfile.ZipFile(app_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            app_path = Path("dist/MKD_Automation.app")
            for file_path in app_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to("dist")
                    zf.write(file_path, arcname)
        print(f"   ✅ Created: {app_zip}")
        
        # Create standalone directory zip
        standalone_zip = release_dir / f"MKD_Automation_Standalone_macOS_{arch}.zip"
        with zipfile.ZipFile(standalone_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            standalone_path = Path("dist/MKD_Automation")
            for file_path in standalone_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to("dist")
                    zf.write(file_path, arcname)
        print(f"   ✅ Created: {standalone_zip}")
        
    elif system == "windows":
        # Create Windows zip
        windows_zip = release_dir / f"MKD_Automation_Windows_{arch}.zip"
        with zipfile.ZipFile(windows_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            standalone_path = Path("dist/MKD_Automation")
            for file_path in standalone_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to("dist")
                    zf.write(file_path, arcname)
        print(f"   ✅ Created: {windows_zip}")
        
    else:  # Linux
        # Create Linux tar.gz
        import tarfile
        linux_tar = release_dir / f"MKD_Automation_Linux_{arch}.tar.gz"
        with tarfile.open(linux_tar, 'w:gz') as tar:
            standalone_path = Path("dist/MKD_Automation")
            tar.add(standalone_path, arcname="MKD_Automation")
        print(f"   ✅ Created: {linux_tar}")
    
    # Create README for releases
    readme_content = f"""# MKD Automation v2.0 - Portable Release

## Installation
1. Extract the archive to any directory
2. Run the executable:
   - **macOS**: Double-click MKD_Automation.app or run ./MKD_Automation/MKD_Automation
   - **Windows**: Double-click MKD_Automation.exe
   - **Linux**: Run ./MKD_Automation/MKD_Automation

## Features
- ✅ No Python installation required
- ✅ No dependencies to install  
- ✅ Fully portable - runs from any location
- ✅ Cross-platform automation capabilities
- ✅ GUI interface with system tray integration
- ✅ Web automation support

## System Requirements
- **macOS**: macOS 10.13+ (High Sierra or later)
- **Windows**: Windows 10/11 (64-bit)
- **Linux**: Most modern distributions with X11/Wayland

## Usage
The application provides a graphical interface for:
- Recording user interactions
- Playing back automation scripts
- Managing .mkd automation files
- System monitoring and control

## Support
For issues and support, visit: https://github.com/flying-pisces/mkd_automation

Built with ❤️ using PyInstaller {subprocess.run(['pyinstaller', '--version'], capture_output=True, text=True).stdout.strip()}
Platform: {platform.system()} {platform.machine()}
"""
    
    readme_path = release_dir / "README.txt"
    readme_path.write_text(readme_content)
    print(f"   ✅ Created: {readme_path}")
    
    # Show final summary
    print(f"\n🎉 Release build complete!")
    print(f"📁 Release files created in: {release_dir.absolute()}")
    
    for file_path in release_dir.iterdir():
        if file_path.is_file():
            size = file_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   📦 {file_path.name} ({size:.1f} MB)")
    
    print("\n✅ Ready for distribution! 🚀")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)