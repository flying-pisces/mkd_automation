#!/usr/bin/env python3
"""
MKD Automation Build Summary
Shows all available build utilities and their usage.
"""

import platform
import shutil
from pathlib import Path

def show_build_summary():
    """Display comprehensive build summary."""
    
    current_platform = platform.system().lower()
    current_arch = platform.machine().lower()
    
    print("🏗️  MKD AUTOMATION BUILD SYSTEM")
    print("=" * 60)
    print(f"Current Platform: {platform.system()} {platform.machine()}")
    print(f"Python Version: {platform.python_version()}")
    print("")
    
    # Available build scripts
    build_scripts = [
        ("build_universal.py", "🌟 Universal single-platform builder", "Builds for current platform with optimal settings"),
        ("build_all_platforms.py", "🌍 Multi-platform orchestrator", "Coordinates builds across all platforms"),
        ("build_linux.sh", "🐧 Linux Docker builder", "Creates Linux builds using Docker"),
        ("create_linux_package.py", "📦 Linux package creator", "Creates .deb, AppImage, and portable packages"),
        ("build_release.py", "📋 Release packager", "Creates distribution-ready packages"),
    ]
    
    print("📋 AVAILABLE BUILD UTILITIES:")
    print("-" * 40)
    
    project_root = Path(__file__).parent
    
    for script, title, description in build_scripts:
        script_path = project_root / script
        status = "✅" if script_path.exists() else "❌"
        executable = "🚀" if script_path.exists() and script_path.stat().st_mode & 0o111 else "📄"
        
        print(f"{status} {executable} {title}")
        print(f"   File: {script}")
        print(f"   Description: {description}")
        if script_path.exists():
            print(f"   Usage: python {script}")
        print("")
    
    # Platform-specific instructions
    print("🎯 PLATFORM-SPECIFIC QUICK START:")
    print("-" * 40)
    
    if current_platform == "darwin":
        print("🍎 macOS Build:")
        print("   python build_universal.py")
        print("   → Creates .app bundle, .dmg installer, portable .zip")
        print("")
        
    elif current_platform == "linux":
        print("🐧 Linux Build:")
        print("   python build_universal.py")
        print("   → Creates single executable")
        print("   python create_linux_package.py dist/mkd-automation")
        print("   → Creates .deb, AppImage, portable archive")
        print("")
        
    elif current_platform == "windows":
        print("🪟 Windows Build:")
        print("   python build_universal.py")
        print("   → Creates .exe executable")
        print("")
    
    # Cross-platform builds
    print("🌐 CROSS-PLATFORM BUILDS:")
    print("-" * 40)
    print("Multi-platform coordinator:")
    print("   python build_all_platforms.py")
    print("")
    
    if shutil.which("docker"):
        print("Docker-based Linux build:")
        print("   ./build_linux.sh")
        print("")
    else:
        print("⚠️  Docker not available - Linux builds limited to current platform")
        print("")
    
    # Output locations
    print("📁 OUTPUT DIRECTORIES:")
    print("-" * 40)
    output_dirs = [
        ("release/", "Single platform builds"),
        ("release_multiplatform/", "Multi-platform builds"),
        ("release_linux/", "Docker Linux builds"),
        ("linux_packages/", "Linux package variants"),
    ]
    
    for dir_name, description in output_dirs:
        dir_path = project_root / dir_name
        status = "📂" if dir_path.exists() else "📁"
        print(f"{status} {dir_name:<25} {description}")
    
    print("")
    
    # Requirements check
    print("🔧 REQUIREMENTS CHECK:")
    print("-" * 40)
    
    requirements = [
        ("pyinstaller", "PyInstaller for building executables"),
        ("docker", "Docker for Linux cross-compilation"),
        ("tkinter", "GUI framework (usually pre-installed)"),
    ]
    
    for req, description in requirements:
        if req == "tkinter":
            try:
                import tkinter
                status = "✅"
            except ImportError:
                status = "❌"
        else:
            status = "✅" if shutil.which(req) else "❌"
        
        print(f"{status} {req:<15} {description}")
    
    print("")
    
    # Build examples
    print("💡 EXAMPLE WORKFLOWS:")
    print("-" * 40)
    
    examples = [
        ("Quick single build", "python build_universal.py"),
        ("Full multi-platform", "python build_all_platforms.py"),
        ("Linux-specific packages", "python build_universal.py && python create_linux_package.py dist/mkd-automation"),
        ("Docker Linux build", "./build_linux.sh"),
        ("Release preparation", "python build_release.py"),
    ]
    
    for workflow, command in examples:
        print(f"🔸 {workflow}:")
        print(f"   {command}")
        print("")
    
    # File types generated
    print("📦 GENERATED FILE TYPES:")
    print("-" * 40)
    
    file_types = [
        ("macOS", [".app (Bundle)", ".dmg (Installer)", ".zip (Portable)"]),
        ("Linux", [".deb (Package)", ".AppImage (Portable)", ".tar.gz (Archive)", "install.sh (Script)"]),
        ("Windows", [".exe (Executable)", ".zip (Portable)", ".msi (Installer)"]),
        ("Universal", ["README.md (Instructions)", "release_info.json (Metadata)"]),
    ]
    
    for platform_name, formats in file_types:
        print(f"🎯 {platform_name}:")
        for fmt in formats:
            print(f"   • {fmt}")
        print("")
    
    print("🚀 Ready to build MKD Automation for any platform!")
    print("   Choose your build script and start creating executables!")

if __name__ == "__main__":
    show_build_summary()