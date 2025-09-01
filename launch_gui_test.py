#!/usr/bin/env python
"""
Simple launcher for GUI Recorder Test

Checks dependencies and launches the GUI testing application.
"""

import sys
import subprocess
import os

def check_dependencies():
    """Check if required dependencies are available."""
    missing = []
    
    # Check pynput
    try:
        import pynput
        print("[OK] pynput library found")
    except ImportError:
        missing.append("pynput")
        print("[MISSING] pynput library - needed for input capture")
    
    # Check tkinter (usually built-in)
    try:
        import tkinter
        print("[OK] tkinter library found")
    except ImportError:
        missing.append("tkinter")
        print("[MISSING] tkinter library - needed for GUI")
    
    return missing

def install_missing(packages):
    """Install missing packages."""
    if not packages:
        return True
    
    print(f"\nInstalling missing packages: {', '.join(packages)}")
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"[INSTALLED] {package}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install {package}: {e}")
            return False
    
    return True

def main():
    """Main launcher."""
    print("=" * 50)
    print("MKD AUTOMATION GUI RECORDER TEST LAUNCHER")
    print("=" * 50)
    
    # Check dependencies
    print("\nChecking dependencies...")
    missing = check_dependencies()
    
    if missing:
        response = input(f"\nInstall missing packages? (y/n): ")
        if response.lower() == 'y':
            if not install_missing(missing):
                print("[ERROR] Failed to install dependencies")
                return 1
        else:
            print("[ERROR] Cannot run without required dependencies")
            return 1
    
    # Launch GUI
    print("\n" + "=" * 50)
    print("LAUNCHING GUI RECORDER TEST...")
    print("=" * 50)
    print()
    print("Features available:")
    print("• Chrome extension-like interface")
    print("• Red frame boundary during recording")
    print("• Real-time event display dialog")
    print("• Mouse and keyboard capture")
    print("• Save recordings to .mkd files")
    print()
    print("Instructions:")
    print("1. Click 'Start Recording' to begin")
    print("2. Red frame will appear around screen")
    print("3. Type/click to test - events shown in monitor")
    print("4. Click 'Stop Recording' when done")
    print("5. Use 'Save Test Recording' to save results")
    print()
    print("Starting GUI...")
    
    try:
        # Import and run the GUI
        from gui_recorder_test import main as gui_main
        gui_main()
        return 0
    except ImportError as e:
        print(f"[ERROR] Failed to import GUI module: {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] GUI execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())