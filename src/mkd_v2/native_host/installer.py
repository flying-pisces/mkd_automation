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
    
    def install_windows_registry(self, host_executable: Path) -> bool:
        """Install Windows registry entries for native messaging host."""
        if self.system != "windows":
            return True  # Skip on non-Windows systems
            
        try:
            import winreg
            
            # Create manifest for registry
            manifest = self._create_manifest(host_executable)
            
            # Create manifest file in chrome-extension directory
            chrome_ext_dir = self.project_root / "chrome-extension"
            chrome_ext_dir.mkdir(exist_ok=True)
            
            manifest_file = chrome_ext_dir / "native-host-manifest.json"
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Registry paths for different browsers
            registry_paths = {
                "Chrome": r"SOFTWARE\Google\Chrome\NativeMessagingHosts",
                "Edge": r"SOFTWARE\Microsoft\Edge\NativeMessagingHosts",
                "Chromium": r"SOFTWARE\Chromium\NativeMessagingHosts"
            }
            
            success_count = 0
            for browser, reg_path in registry_paths.items():
                try:
                    # Create registry key for current user
                    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                    
                    # Set the manifest path
                    winreg.SetValue(key, self.host_name, winreg.REG_SZ, str(manifest_file))
                    winreg.CloseKey(key)
                    
                    logger.info(f"Registered native host for {browser} in registry")
                    success_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to register for {browser}: {e}")
                    
            return success_count > 0
            
        except ImportError:
            logger.warning("winreg module not available, skipping registry installation")
            return False
        except Exception as e:
            logger.error(f"Windows registry installation failed: {e}")
            return False

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
            if self.system == "windows":
                # Use Windows registry for better integration
                registry_success = self.install_windows_registry(host_executable)
                if not registry_success:
                    success = False
                    logger.warning("Registry installation failed, falling back to file-based")
                    # Fall back to file-based installation
                    for browser in browsers:
                        if browser not in self.install_paths:
                            logger.warning(f"Unknown browser: {browser}")
                            continue
                        
                        browser_success = self._install_for_browser(browser, host_executable, user_only)
                        if not browser_success:
                            success = False
            else:
                # Use file-based installation for Unix systems
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
                # Create enhanced batch file and Python launcher for Windows
                host_executable = bin_dir / "mkd_native_host.bat"
                
                # Enhanced batch content with error handling and logging
                batch_content = f"""@echo off
setlocal
cd /d "{self.project_root}"

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in PATH
    echo Please ensure Python 3.8+ is installed and accessible
    exit /b 1
)

:: Check if project directory exists
if not exist "{self.project_root}" (
    echo Error: Project directory not found: {self.project_root}
    exit /b 1
)

:: Set PYTHONPATH to include src directory
set PYTHONPATH={self.project_root / 'src'};%PYTHONPATH%

:: Launch the native host with logging
python -m mkd_v2.native_host.host %*

:: Exit with the same code as Python
exit /b %errorlevel%
"""
                host_executable.write_text(batch_content)
                
                # Also create a PowerShell script for better Windows integration
                ps_executable = bin_dir / "mkd_native_host.ps1"
                ps_content = f"""# MKD Automation Native Host - PowerShell Launcher
param($args)

$ErrorActionPreference = "Stop"
$ProjectRoot = "{self.project_root}"

try {{
    # Check Python availability
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {{
        Write-Error "Python not found. Please install Python 3.8+ and add to PATH."
        exit 1
    }}
    
    # Set working directory and PYTHONPATH
    Set-Location $ProjectRoot
    $env:PYTHONPATH = "$ProjectRoot\\src;$($env:PYTHONPATH)"
    
    # Launch native host
    python -m mkd_v2.native_host.host @args
    exit $LASTEXITCODE
}}
catch {{
    Write-Error "Failed to start MKD native host: $_"
    exit 1
}}
"""
                ps_executable.write_text(ps_content)
                
                # Create Windows registry installer script
                registry_installer = bin_dir / "install_registry.py"
                registry_content = '''#!/usr/bin/env python3
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
        "Chrome": r"SOFTWARE\\Google\\Chrome\\NativeMessagingHosts",
        "Edge": r"SOFTWARE\\Microsoft\\Edge\\NativeMessagingHosts"
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
'''
                registry_installer.write_text(registry_content)
                
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