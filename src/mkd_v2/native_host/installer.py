"""
Native Host Installer for Chrome Extension Integration.

Handles installation and registration of the native messaging host
with Chrome and other Chromium-based browsers.
"""

import json
import logging
import platform
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class NativeHostInstaller:
    """
    Installer for Chrome native messaging host.
    
    Handles cross-platform installation and registration of the native
    messaging host that allows Chrome extension communication.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.host_name = "com.mkd.automation"
        self.system = platform.system().lower()
        
        # Platform-specific paths
        self.install_paths = self._get_install_paths()
        
        logger.info(f"NativeHostInstaller initialized for {self.system}")
    
    def _get_install_paths(self) -> Dict[str, List[Path]]:
        """Get platform-specific installation paths."""
        if self.system == "darwin":  # macOS
            return {
                "chrome": [
                    Path.home() / "Library/Application Support/Google/Chrome/NativeMessagingHosts",
                    Path("/Library/Application Support/Google/Chrome/NativeMessagingHosts")
                ],
                "chromium": [
                    Path.home() / "Library/Application Support/Chromium/NativeMessagingHosts",
                    Path("/Library/Application Support/Chromium/NativeMessagingHosts")
                ]
            }
        elif self.system == "linux":
            return {
                "chrome": [
                    Path.home() / ".config/google-chrome/NativeMessagingHosts",
                    Path("/etc/opt/chrome/native-messaging-hosts")
                ],
                "chromium": [
                    Path.home() / ".config/chromium/NativeMessagingHosts",
                    Path("/etc/chromium/native-messaging-hosts")
                ]
            }
        elif self.system == "windows":
            # Windows uses registry, but we'll also support file-based for dev
            return {
                "chrome": [
                    Path.home() / "AppData/Local/Google/Chrome/User Data/NativeMessagingHosts"
                ],
                "chromium": [
                    Path.home() / "AppData/Local/Chromium/User Data/NativeMessagingHosts"
                ]
            }
        else:
            return {}
    
    def install(self, browsers: Optional[List[str]] = None, user_only: bool = True) -> bool:
        """
        Install the native messaging host.
        
        Args:
            browsers: List of browsers to install for (chrome, chromium)
            user_only: Install for current user only (not system-wide)
            
        Returns:
            True if installation successful
        """
        browsers = browsers or ["chrome", "chromium"]
        success = True
        
        try:
            logger.info(f"Installing native messaging host for: {', '.join(browsers)}")
            
            # Create host executable
            host_executable = self._create_host_executable()
            if not host_executable:
                return False
            
            # Install for each browser
            for browser in browsers:
                if browser not in self.install_paths:
                    logger.warning(f"Unknown browser: {browser}")
                    continue
                
                browser_success = self._install_for_browser(browser, host_executable, user_only)
                if not browser_success:
                    success = False
            
            if success:
                logger.info("Native messaging host installation completed successfully")
            else:
                logger.error("Native messaging host installation had errors")
            
            return success
            
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            return False
    
    def uninstall(self, browsers: Optional[List[str]] = None) -> bool:
        """
        Uninstall the native messaging host.
        
        Args:
            browsers: List of browsers to uninstall from
            
        Returns:
            True if uninstallation successful
        """
        browsers = browsers or ["chrome", "chromium"]
        success = True
        
        try:
            logger.info(f"Uninstalling native messaging host from: {', '.join(browsers)}")
            
            for browser in browsers:
                if browser not in self.install_paths:
                    continue
                
                for install_path in self.install_paths[browser]:
                    manifest_file = install_path / f"{self.host_name}.json"
                    
                    if manifest_file.exists():
                        try:
                            manifest_file.unlink()
                            logger.info(f"Removed manifest: {manifest_file}")
                        except Exception as e:
                            logger.error(f"Failed to remove {manifest_file}: {e}")
                            success = False
            
            # Remove host executable if it exists
            host_dir = self.project_root / "bin"
            if host_dir.exists():
                try:
                    shutil.rmtree(host_dir)
                    logger.info(f"Removed host directory: {host_dir}")
                except Exception as e:
                    logger.error(f"Failed to remove host directory: {e}")
                    success = False
            
            return success
            
        except Exception as e:
            logger.error(f"Uninstallation failed: {e}")
            return False
    
    def _create_host_executable(self) -> Optional[Path]:
        """Create the native messaging host executable."""
        try:
            # Create bin directory
            bin_dir = self.project_root / "bin"
            bin_dir.mkdir(exist_ok=True)
            
            # Path to host script
            host_script = self.project_root / "src" / "mkd_v2" / "native_host" / "host.py"
            
            if self.system == "windows":
                # Create batch file for Windows
                host_executable = bin_dir / "mkd_native_host.bat"
                batch_content = f"""@echo off
cd /d "{self.project_root}"
python -m mkd_v2.native_host.host %*
"""
                host_executable.write_text(batch_content)
                
            else:
                # Create shell script for Unix systems
                host_executable = bin_dir / "mkd_native_host"
                script_content = f"""#!/bin/bash
cd "{self.project_root}"
export PYTHONPATH="{self.project_root / 'src'}:$PYTHONPATH"
python3 -m mkd_v2.native_host.host "$@"
"""
                host_executable.write_text(script_content)
                host_executable.chmod(0o755)  # Make executable
            
            logger.info(f"Created host executable: {host_executable}")
            return host_executable
            
        except Exception as e:
            logger.error(f"Failed to create host executable: {e}")
            return None
    
    def _install_for_browser(self, browser: str, host_executable: Path, user_only: bool) -> bool:
        """Install manifest for specific browser."""
        try:
            paths = self.install_paths[browser]
            
            # Use user path if user_only, otherwise try system path
            if user_only:
                install_path = paths[0]
            else:
                install_path = paths[-1] if len(paths) > 1 else paths[0]
            
            # Create install directory
            install_path.mkdir(parents=True, exist_ok=True)
            
            # Create manifest
            manifest = self._create_manifest(host_executable)
            
            # Write manifest file
            manifest_file = install_path / f"{self.host_name}.json"
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Installed manifest for {browser}: {manifest_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install for {browser}: {e}")
            return False
    
    def _create_manifest(self, host_executable: Path) -> Dict:
        """Create native messaging host manifest."""
        return {
            "name": self.host_name,
            "description": "MKD Automation Native Messaging Host",
            "path": str(host_executable.absolute()),
            "type": "stdio",
            "allowed_origins": [
                f"chrome-extension://*/"
            ]
        }
    
    def check_installation(self, browsers: Optional[List[str]] = None) -> Dict[str, Dict[str, bool]]:
        """
        Check installation status for browsers.
        
        Args:
            browsers: List of browsers to check
            
        Returns:
            Dictionary with installation status per browser
        """
        browsers = browsers or ["chrome", "chromium"]
        status = {}
        
        for browser in browsers:
            if browser not in self.install_paths:
                status[browser] = {"installed": False, "error": "Browser not supported"}
                continue
            
            browser_status = {"installed": False, "paths": []}
            
            for install_path in self.install_paths[browser]:
                manifest_file = install_path / f"{self.host_name}.json"
                path_status = {
                    "path": str(install_path),
                    "manifest_exists": manifest_file.exists(),
                    "readable": False,
                    "valid": False
                }
                
                if manifest_file.exists():
                    try:
                        # Check if manifest is readable and valid
                        with open(manifest_file) as f:
                            manifest = json.load(f)
                        
                        path_status["readable"] = True
                        path_status["valid"] = (
                            manifest.get("name") == self.host_name and
                            "path" in manifest and
                            "type" in manifest
                        )
                        
                        if path_status["valid"]:
                            browser_status["installed"] = True
                            
                    except Exception as e:
                        path_status["error"] = str(e)
                
                browser_status["paths"].append(path_status)
            
            status[browser] = browser_status
        
        return status
    
    def get_installation_info(self) -> Dict:
        """Get detailed installation information."""
        return {
            "host_name": self.host_name,
            "system": self.system,
            "project_root": str(self.project_root),
            "install_paths": {
                browser: [str(path) for path in paths]
                for browser, paths in self.install_paths.items()
            },
            "status": self.check_installation()
        }


def main():
    """CLI entry point for native host installer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MKD Automation Native Host Installer")
    parser.add_argument("action", choices=["install", "uninstall", "status"], 
                       help="Action to perform")
    parser.add_argument("--browsers", nargs="+", 
                       choices=["chrome", "chromium"], 
                       default=["chrome", "chromium"],
                       help="Browsers to install for")
    parser.add_argument("--system", action="store_true",
                       help="Install system-wide (requires admin/root)")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
    
    installer = NativeHostInstaller()
    
    if args.action == "install":
        success = installer.install(browsers=args.browsers, user_only=not args.system)
        sys.exit(0 if success else 1)
        
    elif args.action == "uninstall":
        success = installer.uninstall(browsers=args.browsers)
        sys.exit(0 if success else 1)
        
    elif args.action == "status":
        info = installer.get_installation_info()
        print(json.dumps(info, indent=2))
        sys.exit(0)


if __name__ == "__main__":
    main()