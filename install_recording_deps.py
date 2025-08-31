#!/usr/bin/env python
"""
Install dependencies for motion recording
"""

import subprocess
import sys

def install_packages():
    """Install required packages for motion recording."""
    packages = [
        "keyboard",
        "mouse",
        "pynput"  # Alternative input library
    ]
    
    print("Installing motion recording dependencies...")
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")
        except Exception as e:
            print(f"✗ Error installing {package}: {e}")
    
    print("\nInstallation complete!")
    print("You can now run: python record_motions.py")

if __name__ == "__main__":
    install_packages()