#!/usr/bin/env python3
"""
Windows Registry Installer for MKD Native Messaging Host
"""

import winreg
import sys
import json
from pathlib import Path

def install_registry_entries():
    """Install native messaging host registry entries for Windows."""
    host_name = "com.mkd.automation"
    manifest_path = Path(__file__).parent.parent / "chrome-extension" / "native-host-manifest.json"
    
    # Registry paths for Chrome and Edge
    registry_paths = {
        "Chrome": r"SOFTWARE\Google\Chrome\NativeMessagingHosts",
        "Edge": r"SOFTWARE\Microsoft\Edge\NativeMessagingHosts"
    }
    
    try:
        for browser, reg_path in registry_paths.items():
            try:
                # Open registry key (create if not exists)
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                
                # Set the manifest path
                winreg.SetValue(key, host_name, winreg.REG_SZ, str(manifest_path))
                winreg.CloseKey(key)
                
                print(f"[OK] Registered native host for {browser}")
                
            except Exception as e:
                print(f"[FAIL] Failed to register for {browser}: {e}")
                
        print("[OK] Registry installation complete")
        return True
        
    except Exception as e:
        print(f"[FAIL] Registry installation failed: {e}")
        return False

if __name__ == "__main__":
    success = install_registry_entries()
    sys.exit(0 if success else 1)
