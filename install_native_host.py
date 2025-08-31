#!/usr/bin/env python3
"""
Cross-Platform Native Host Installer for MKD Automation Chrome Extension

This script provides a unified installer for the MKD Automation native messaging host
that works across Windows, macOS, and Linux platforms.

Usage:
    python install_native_host.py install
    python install_native_host.py uninstall
    python install_native_host.py status
"""

import argparse
import json
import logging
import platform
import sys
from pathlib import Path

# Add src to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

try:
    from mkd_v2.native_host.installer import NativeHostInstaller
except ImportError as e:
    print(f"Error: Failed to import MKD modules: {e}")
    print("Please ensure you're running this from the project root directory")
    sys.exit(1)


class UnifiedInstaller:
    """Unified cross-platform installer for MKD Automation native host."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.installer = NativeHostInstaller(project_root)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_format = "%(levelname)-8s %(message)s"
        logging.basicConfig(level=logging.INFO, format=log_format)
        self.logger = logging.getLogger(__name__)
    
    def install(self, browsers=None, system_wide=False):
        """
        Install the native messaging host.
        
        Args:
            browsers: List of browsers to install for
            system_wide: Install system-wide (requires admin privileges)
        """
        browsers = browsers or ["chrome", "chromium"]
        
        print("MKD Automation Native Host Installer")
        print("=" * 50)
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Project Root: {project_root}")
        print(f"Browsers: {', '.join(browsers)}")
        print(f"Scope: {'System-wide' if system_wide else 'User-only'}")
        print()
        
        # Pre-installation checks
        if not self.pre_install_checks():
            return False
        
        # Install the native host
        print("Installing native messaging host...")
        success = self.installer.install(
            browsers=browsers, 
            user_only=not system_wide
        )
        
        if success:
            print("\n[OK] Installation completed successfully!")
            print("\nNext steps:")
            print("1. Install the Chrome extension from chrome-extension/ directory")
            print("2. Test the connection using: python -m mkd_v2.native_host.host")
            print("3. Check status with: python install_native_host.py status")
            
            # Show installation details
            print("\nInstallation Details:")
            self.show_status()
            
        else:
            print("\n[FAIL] Installation failed!")
            print("Check the logs above for error details.")
            return False
        
        return True
    
    def uninstall(self, browsers=None):
        """
        Uninstall the native messaging host.
        
        Args:
            browsers: List of browsers to uninstall from
        """
        browsers = browsers or ["chrome", "chromium"]
        
        print("MKD Automation Native Host Uninstaller")
        print("=" * 50)
        print(f"Removing from browsers: {', '.join(browsers)}")
        print()
        
        success = self.installer.uninstall(browsers=browsers)
        
        # Also clean up Windows registry if applicable
        if self.system == "windows":
            self.cleanup_windows_registry()
        
        if success:
            print("\n[OK] Uninstallation completed successfully!")
        else:
            print("\n[FAIL] Uninstallation had errors!")
            print("Check the logs above for details.")
        
        return success
    
    def show_status(self):
        """Show installation status."""
        print("MKD Automation Native Host Status")
        print("=" * 50)
        
        # Get installation info
        info = self.installer.get_installation_info()
        
        print(f"Host Name: {info['host_name']}")
        print(f"System: {info['system']}")
        print(f"Project Root: {info['project_root']}")
        print()
        
        # Show status for each browser
        for browser, status in info['status'].items():
            print(f"{browser.title()}:")
            if status.get('installed'):
                print("  [OK] Installed")
            else:
                print("  [NO] Not installed")
            
            for path_info in status.get('paths', []):
                path = path_info['path']
                manifest_exists = path_info['manifest_exists']
                valid = path_info.get('valid', False)
                
                print(f"    Path: {path}")
                print(f"    Manifest: {'[OK]' if manifest_exists else '[NO]'}")
                print(f"    Valid: {'[OK]' if valid else '[NO]'}")
                
                if 'error' in path_info:
                    print(f"    Error: {path_info['error']}")
            print()
        
        # Test native host availability
        self.test_native_host()
    
    def test_native_host(self):
        """Test if the native host can be started."""
        print("Testing Native Host:")
        try:
            import subprocess
            import tempfile
            import json
            
            # Try to start the native host and send a ping message
            host_script = project_root / "src" / "mkd_v2" / "native_host" / "host.py"
            
            if not host_script.exists():
                print("  [FAIL] Host script not found")
                return False
            
            # Simple test - just try to import the host module
            try:
                from mkd_v2.native_host.host import NativeHost
                print("  [OK] Native host module imports successfully")
                
                # Test basic instantiation
                host = NativeHost(storage_path=tempfile.mkdtemp())
                print("  [OK] Native host instantiates successfully")
                
                return True
                
            except Exception as e:
                print(f"  [FAIL] Native host test failed: {e}")
                return False
                
        except Exception as e:
            print(f"  [FAIL] Test error: {e}")
            return False
    
    def pre_install_checks(self):
        """Perform pre-installation checks."""
        print("Pre-installation checks:")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            print("  [FAIL] Python 3.8+ required")
            return False
        print(f"  [OK] Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check project structure
        required_paths = [
            project_root / "src" / "mkd_v2" / "native_host" / "host.py",
            project_root / "chrome-extension" / "manifest.json",
        ]
        
        for path in required_paths:
            if not path.exists():
                print(f"  [FAIL] Missing: {path}")
                return False
            print(f"  [OK] Found: {path.name}")
        
        # Check dependencies
        try:
            import struct
            import json
            import threading
            print("  [OK] Core dependencies available")
        except ImportError as e:
            print(f"  [FAIL] Missing dependency: {e}")
            return False
        
        # Platform-specific checks
        if self.system == "windows":
            try:
                import winreg
                print("  [OK] Windows registry access available")
            except ImportError:
                print("  [WARN] Windows registry not available (will use file-based)")
        
        print("  [OK] All pre-installation checks passed")
        print()
        return True
    
    def cleanup_windows_registry(self):
        """Clean up Windows registry entries."""
        if self.system != "windows":
            return
        
        try:
            import winreg
            
            registry_paths = [
                r"SOFTWARE\Google\Chrome\NativeMessagingHosts",
                r"SOFTWARE\Microsoft\Edge\NativeMessagingHosts",
                r"SOFTWARE\Chromium\NativeMessagingHosts"
            ]
            
            host_name = "com.mkd.automation"
            
            for reg_path in registry_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS)
                    winreg.DeleteValue(key, host_name)
                    winreg.CloseKey(key)
                    print(f"  [OK] Cleaned registry: {reg_path}")
                except FileNotFoundError:
                    # Key doesn't exist, which is fine
                    pass
                except Exception as e:
                    print(f"  [WARN] Registry cleanup warning: {e}")
                    
        except ImportError:
            print("  [WARN] Windows registry not available for cleanup")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MKD Automation Native Host Cross-Platform Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python install_native_host.py install
    python install_native_host.py install --browsers chrome edge --system
    python install_native_host.py uninstall
    python install_native_host.py status
        """
    )
    
    parser.add_argument(
        "action", 
        choices=["install", "uninstall", "status"],
        help="Action to perform"
    )
    
    parser.add_argument(
        "--browsers", 
        nargs="+",
        choices=["chrome", "chromium", "edge"],
        default=["chrome", "chromium"],
        help="Browsers to install for (default: chrome chromium)"
    )
    
    parser.add_argument(
        "--system", 
        action="store_true",
        help="Install system-wide (requires admin privileges)"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    installer = UnifiedInstaller()
    
    try:
        if args.action == "install":
            success = installer.install(
                browsers=args.browsers,
                system_wide=args.system
            )
            sys.exit(0 if success else 1)
            
        elif args.action == "uninstall":
            success = installer.uninstall(browsers=args.browsers)
            sys.exit(0 if success else 1)
            
        elif args.action == "status":
            installer.show_status()
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()