#!/usr/bin/env python3
"""
Native Host Installer Script

Quick installer for the MKD Automation native messaging host.
This enables communication between the Chrome extension and Python backend.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Install the native messaging host."""
    print("🚀 MKD Automation Native Host Installer")
    print("=" * 50)
    
    try:
        from mkd_v2.native_host.installer import NativeHostInstaller
        
        installer = NativeHostInstaller()
        
        # Show current status
        print("\n📋 Checking current installation status...")
        status = installer.check_installation()
        
        for browser, browser_status in status.items():
            if browser_status.get("installed"):
                print(f"✅ {browser.title()}: Already installed")
            else:
                print(f"❌ {browser.title()}: Not installed")
        
        print("\n🔧 Installing native messaging host...")
        
        # Install for both Chrome and Chromium
        success = installer.install(browsers=["chrome", "chromium"], user_only=True)
        
        if success:
            print("✅ Installation completed successfully!")
            
            # Show post-installation status
            print("\n📊 Post-installation status:")
            post_status = installer.check_installation()
            
            for browser, browser_status in post_status.items():
                if browser_status.get("installed"):
                    print(f"✅ {browser.title()}: Installed and configured")
                else:
                    print(f"❌ {browser.title()}: Installation failed")
            
            print("\n🎉 Native host is ready!")
            print("\n📋 Next steps:")
            print("1. Restart Chrome/Chromium browser")
            print("2. Reload the MKD Automation extension")
            print("3. Click the extension icon - should connect successfully")
            print("4. 'Could not establish connection' error should be resolved")
            
            return True
            
        else:
            print("❌ Installation failed!")
            print("\n🔧 Troubleshooting tips:")
            print("- Make sure Chrome/Chromium is closed during installation")
            print("- Try running with admin/sudo privileges")
            print("- Check file permissions in browser profile directories")
            
            return False
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔧 Fix: Make sure you're running from the project root directory")
        return False
    
    except Exception as e:
        print(f"❌ Installation error: {e}")
        print("\n🔧 Please check the error message above and try again")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)