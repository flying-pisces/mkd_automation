#!/usr/bin/env python3
"""
Multi-Platform Builder for MKD Automation
Orchestrates builds for macOS, Linux, and Windows using various methods.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from datetime import datetime
import json

class MultiPlatformBuilder:
    """Orchestrates builds across multiple platforms."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.current_platform = platform.system().lower()
        self.output_dir = self.project_root / "release_multiplatform"
        self.build_log = []
        
    def log(self, message, level="INFO"):
        """Log build messages."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.build_log.append(log_entry)
        print(log_entry)
    
    def clean_outputs(self):
        """Clean previous build outputs."""
        self.log("🧹 Cleaning previous builds...")
        
        dirs_to_clean = [
            "build", "dist", "release", "release_linux", 
            "release_windows", "release_multiplatform"
        ]
        
        for dir_name in dirs_to_clean:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                self.log(f"   Removed {dir_name}/")
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
    
    def build_current_platform(self):
        """Build for the current platform."""
        self.log(f"🔨 Building for current platform: {self.current_platform}")
        
        try:
            # Use the universal builder
            result = subprocess.run([
                sys.executable, "build_universal.py"
            ], check=True, capture_output=True, text=True, cwd=self.project_root)
            
            self.log(f"✅ Current platform build successful")
            
            # Copy results to multiplatform directory
            release_dir = self.project_root / "release"
            if release_dir.exists():
                for file_path in release_dir.iterdir():
                    if file_path.is_file():
                        dest_path = self.output_dir / file_path.name
                        shutil.copy2(file_path, dest_path)
                        self.log(f"   Copied {file_path.name}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Current platform build failed: {e}", "ERROR")
            return False
    
    def build_linux_docker(self):
        """Build Linux version using Docker."""
        if not shutil.which("docker"):
            self.log("⚠️  Docker not available - skipping Linux build", "WARNING")
            return False
        
        self.log("🐧 Building Linux version with Docker...")
        
        try:
            # Make build script executable
            build_script = self.project_root / "build_linux.sh"
            build_script.chmod(0o755)
            
            # Run Linux build
            result = subprocess.run([
                str(build_script)
            ], check=True, capture_output=True, text=True, cwd=self.project_root)
            
            self.log("✅ Linux build successful")
            
            # Copy Linux results
            linux_dir = self.project_root / "release_linux"
            if linux_dir.exists():
                for file_path in linux_dir.iterdir():
                    if file_path.is_file():
                        dest_path = self.output_dir / file_path.name
                        shutil.copy2(file_path, dest_path)
                        self.log(f"   Copied Linux: {file_path.name}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Linux build failed: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Linux build error: {e}", "ERROR")
            return False
    
    def build_windows_wine(self):
        """Build Windows version using Wine (if available)."""
        if not shutil.which("wine"):
            self.log("⚠️  Wine not available - skipping Windows build", "WARNING")
            return False
        
        self.log("🍷 Building Windows version with Wine...")
        
        try:
            # This would require a complex Wine setup
            # For now, just log that it's not implemented
            self.log("⚠️  Wine build not implemented yet", "WARNING")
            return False
            
        except Exception as e:
            self.log(f"❌ Windows build error: {e}", "ERROR")
            return False
    
    def create_github_actions_config(self):
        """Create GitHub Actions workflow for automated builds."""
        self.log("⚙️  Creating GitHub Actions configuration...")
        
        workflow_content = """name: Build Multi-Platform Releases

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-macos:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pyinstaller
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Build macOS
      run: python build_universal.py
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: macos-build
        path: release/

  build-linux:
    runs-on: ubuntu-22.04
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y python3-tk libx11-dev
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pyinstaller
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Build Linux
      run: python build_universal.py
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: linux-build
        path: release/

  build-windows:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pyinstaller
        if (Test-Path requirements.txt) { pip install -r requirements.txt }
    - name: Build Windows
      run: python build_universal.py
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: windows-build
        path: release/

  create-release:
    needs: [build-macos, build-linux, build-windows]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')
    steps:
    - name: Download all artifacts
      uses: actions/download-artifact@v3
    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: |
          macos-build/*
          linux-build/*
          windows-build/*
        generate_release_notes: true
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""
        
        # Create .github/workflows directory
        github_dir = self.project_root / ".github" / "workflows"
        github_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_file = github_dir / "build-multiplatform.yml"
        workflow_file.write_text(workflow_content)
        
        self.log(f"✅ GitHub Actions workflow created: {workflow_file}")
    
    def create_build_instructions(self):
        """Create comprehensive build instructions."""
        instructions_content = f"""# MKD Automation - Multi-Platform Build Instructions

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
Last updated: {datetime.now().strftime('%Y-%m-%d')}
"""
        
        instructions_file = self.output_dir / "BUILD_INSTRUCTIONS.md"
        instructions_file.write_text(instructions_content)
        self.log(f"✅ Build instructions created: {instructions_file}")
    
    def create_build_summary(self):
        """Create build summary and statistics."""
        summary = {
            "build_date": datetime.now().isoformat(),
            "platforms": [],
            "files": [],
            "total_size": 0,
            "build_log": self.build_log
        }
        
        # Analyze output files
        for file_path in self.output_dir.iterdir():
            if file_path.is_file() and file_path.suffix in ['.zip', '.tar.gz', '.deb', '.dmg', '.exe']:
                file_size = file_path.stat().st_size
                summary["files"].append({
                    "name": file_path.name,
                    "size": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 1)
                })
                summary["total_size"] += file_size
                
                # Detect platform from filename
                if "macos" in file_path.name.lower() or "darwin" in file_path.name.lower():
                    if "macOS" not in summary["platforms"]:
                        summary["platforms"].append("macOS")
                elif "linux" in file_path.name.lower() or "ubuntu" in file_path.name.lower():
                    if "Linux" not in summary["platforms"]:
                        summary["platforms"].append("Linux")
                elif "windows" in file_path.name.lower() or "win" in file_path.name.lower():
                    if "Windows" not in summary["platforms"]:
                        summary["platforms"].append("Windows")
        
        summary["total_size_mb"] = round(summary["total_size"] / (1024 * 1024), 1)
        
        # Save summary
        summary_file = self.output_dir / "build_summary.json"
        summary_file.write_text(json.dumps(summary, indent=2))
        
        return summary
    
    def show_results(self, summary):
        """Display build results."""
        self.log("🎉 Multi-platform build complete!")
        self.log(f"📁 Output directory: {self.output_dir}")
        self.log(f"🔧 Platforms: {', '.join(summary['platforms'])}")
        self.log(f"📦 Files: {len(summary['files'])}")
        self.log(f"📈 Total size: {summary['total_size_mb']} MB")
        
        print("\n" + "="*60)
        print("📦 GENERATED FILES:")
        print("="*60)
        
        for file_info in summary["files"]:
            emoji = "📦"
            if file_info["name"].endswith('.dmg'):
                emoji = "💾"
            elif file_info["name"].endswith('.deb'):
                emoji = "📋"
            elif file_info["name"].endswith('.exe'):
                emoji = "🪟"
            
            print(f"{emoji} {file_info['name']} ({file_info['size_mb']} MB)")
        
        print("="*60)
        print("🚀 Ready for distribution!")
    
    def build(self):
        """Main build orchestrator."""
        print("🌍 MKD Automation Multi-Platform Builder")
        print("=" * 60)
        
        self.clean_outputs()
        
        # Build current platform
        current_success = self.build_current_platform()
        
        # Try Linux build if not on Linux
        linux_success = False
        if self.current_platform != 'linux':
            linux_success = self.build_linux_docker()
        
        # Try Windows build if not on Windows
        windows_success = False
        if self.current_platform != 'windows':
            windows_success = self.build_windows_wine()
        
        # Create additional resources
        self.create_github_actions_config()
        self.create_build_instructions()
        
        # Generate summary
        summary = self.create_build_summary()
        self.show_results(summary)
        
        # Return success if at least one platform built
        return current_success or linux_success or windows_success

def main():
    """Entry point."""
    builder = MultiPlatformBuilder()
    success = builder.build()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()