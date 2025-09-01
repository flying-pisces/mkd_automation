#!/usr/bin/env python3
"""
Native Messaging Host Test Script

This script helps diagnose native messaging host connection issues
by checking installation, registry entries, and testing the host directly.
"""

import json
import os
import platform
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
import winreg
import time

class NativeHostTester:
    """Test and diagnose native messaging host issues."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.project_root = Path(__file__).parent
        self.host_id = "com.mkdautomation.native"
        self.results = []
    
    def log(self, status, message, details=None):
        """Log test result."""
        print(f"[{status}] {message}")
        if details:
            print(f"    {details}")
        
        self.results.append({
            "status": status,
            "message": message,
            "details": details
        })
    
    def test_python_environment(self):
        """Test Python environment and dependencies."""
        print("\n=== Python Environment ===")
        
        try:
            python_version = sys.version
            self.log("OK", f"Python version: {python_version.split()[0]}")
        except Exception as e:
            self.log("FAIL", f"Cannot determine Python version: {e}")
            return False
        
        # Test required modules
        required_modules = ['json', 'struct', 'sys', 'pathlib']
        for module in required_modules:
            try:
                __import__(module)
                self.log("OK", f"Module '{module}' available")
            except ImportError as e:
                self.log("FAIL", f"Module '{module}' missing: {e}")
                return False
        
        # Test MKD modules
        try:
            sys.path.insert(0, str(self.project_root / "src"))
            from mkd_v2.native_host import host
            self.log("OK", "MKD native host module available")
        except ImportError as e:
            self.log("FAIL", f"MKD native host module not found: {e}")
            self.log("INFO", "Run: pip install -r requirements.txt")
            return False
        
        return True
    
    def test_native_host_script(self):
        """Test if native host script exists and is executable."""
        print("\n=== Native Host Script ===")
        
        host_script = self.project_root / "src" / "mkd_v2" / "native_host" / "host.py"
        
        if not host_script.exists():
            self.log("FAIL", f"Native host script not found: {host_script}")
            return False
        
        self.log("OK", f"Native host script found: {host_script}")
        
        # Test script execution
        try:
            result = subprocess.run([
                sys.executable, str(host_script), "--test"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log("OK", "Native host script executable")
            else:
                self.log("FAIL", f"Native host script error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("WARN", "Native host script test timeout (may be normal)")
        except Exception as e:
            self.log("FAIL", f"Cannot execute native host script: {e}")
            return False
        
        return True
    
    def test_registry_entries_windows(self):
        """Test Windows registry entries."""
        if self.system != "windows":
            print("\n=== Registry Entries (Skipped - Not Windows) ===")
            return True
            
        print("\n=== Windows Registry Entries ===")
        
        registry_paths = {
            "Chrome": r"SOFTWARE\Google\Chrome\NativeMessagingHosts",
            "Edge": r"SOFTWARE\Microsoft\Edge\NativeMessagingHosts",
            "Chromium": r"SOFTWARE\Chromium\NativeMessagingHosts"
        }
        
        found_any = False
        
        for browser, base_path in registry_paths.items():
            try:
                # Try HKEY_CURRENT_USER first
                try:
                    key_path = f"{base_path}\\{self.host_id}"
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
                    manifest_path = winreg.QueryValue(key, "")
                    winreg.CloseKey(key)
                    
                    self.log("OK", f"{browser} registry entry (HKCU): {manifest_path}")
                    found_any = True
                    
                    # Verify manifest file exists
                    if Path(manifest_path).exists():
                        self.log("OK", f"{browser} manifest file exists")
                    else:
                        self.log("WARN", f"{browser} manifest file missing: {manifest_path}")
                        
                except FileNotFoundError:
                    # Try HKEY_LOCAL_MACHINE
                    try:
                        key_path = f"{base_path}\\{self.host_id}"
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                        manifest_path = winreg.QueryValue(key, "")
                        winreg.CloseKey(key)
                        
                        self.log("OK", f"{browser} registry entry (HKLM): {manifest_path}")
                        found_any = True
                        
                    except FileNotFoundError:
                        self.log("INFO", f"{browser} registry entry not found")
                        
            except Exception as e:
                self.log("WARN", f"Error checking {browser} registry: {e}")
        
        if not found_any:
            self.log("FAIL", "No native messaging host registry entries found")
            self.log("INFO", "Run: python install_native_host.py")
            return False
        
        return True
    
    def test_manifest_files(self):
        """Test native messaging manifest files."""
        print("\n=== Manifest Files ===")
        
        # Look for manifest files
        manifest_locations = []
        
        if self.system == "windows":
            # Windows locations
            manifest_locations.extend([
                Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "NativeMessagingHosts",
                Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "NativeMessagingHosts",
                self.project_root / "chrome-extension" / f"{self.host_id}.json"
            ])
        elif self.system == "darwin":
            # macOS locations
            manifest_locations.extend([
                Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "NativeMessagingHosts",
                Path.home() / "Library" / "Application Support" / "Microsoft Edge" / "NativeMessagingHosts",
            ])
        else:
            # Linux locations
            manifest_locations.extend([
                Path.home() / ".config" / "google-chrome" / "NativeMessagingHosts",
                Path.home() / ".config" / "chromium" / "NativeMessagingHosts",
            ])
        
        found_manifest = False
        
        for location in manifest_locations:
            manifest_file = location / f"{self.host_id}.json"
            if manifest_file.exists():
                self.log("OK", f"Manifest found: {manifest_file}")
                found_manifest = True
                
                # Validate manifest content
                try:
                    with open(manifest_file, 'r') as f:
                        manifest_data = json.load(f)
                    
                    required_fields = ["name", "description", "path", "type", "allowed_origins"]
                    missing_fields = [field for field in required_fields if field not in manifest_data]
                    
                    if missing_fields:
                        self.log("WARN", f"Manifest missing fields: {missing_fields}")
                    else:
                        self.log("OK", "Manifest structure valid")
                        
                        # Check if path exists
                        host_path = Path(manifest_data["path"])
                        if host_path.exists():
                            self.log("OK", f"Host executable exists: {host_path}")
                        else:
                            self.log("FAIL", f"Host executable missing: {host_path}")
                            
                except json.JSONDecodeError as e:
                    self.log("FAIL", f"Invalid JSON in manifest: {e}")
                except Exception as e:
                    self.log("FAIL", f"Error reading manifest: {e}")
            else:
                self.log("INFO", f"Manifest not found: {manifest_file}")
        
        if not found_manifest:
            self.log("FAIL", "No native messaging manifests found")
            self.log("INFO", "Run: python install_native_host.py")
            return False
        
        return True
    
    def test_direct_communication(self):
        """Test direct communication with native host."""
        print("\n=== Direct Communication Test ===")
        
        host_script = self.project_root / "src" / "mkd_v2" / "native_host" / "host.py"
        
        if not host_script.exists():
            self.log("FAIL", "Cannot test - host script not found")
            return False
        
        try:
            # Start the native host process
            process = subprocess.Popen([
                sys.executable, str(host_script), "--debug"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Send a PING message
            test_message = {
                "id": "test_ping",
                "command": "PING",
                "params": {},
                "timestamp": time.time()
            }
            
            message_json = json.dumps(test_message)
            message_bytes = message_json.encode('utf-8')
            
            # Send length header + message
            length_bytes = struct.pack('=I', len(message_bytes))
            process.stdin.write(length_bytes)
            process.stdin.write(message_bytes)
            process.stdin.flush()
            
            # Read response
            try:
                # Read length
                length_data = process.stdout.read(4)
                if len(length_data) == 4:
                    response_length = struct.unpack('=I', length_data)[0]
                    
                    # Read message
                    response_data = process.stdout.read(response_length)
                    response = json.loads(response_data.decode('utf-8'))
                    
                    if response.get('success'):
                        self.log("OK", f"Native host responded: {response}")
                    else:
                        self.log("FAIL", f"Native host error: {response.get('error', 'Unknown error')}")
                        
                else:
                    self.log("FAIL", "No response from native host")
                    
            except Exception as e:
                self.log("FAIL", f"Error reading response: {e}")
            
            # Clean up
            process.terminate()
            process.wait(timeout=5)
            
            return True
            
        except Exception as e:
            self.log("FAIL", f"Communication test failed: {e}")
            return False
    
    def test_chrome_connection(self):
        """Test Chrome extension connection (requires Chrome)."""
        print("\n=== Chrome Connection Test ===")
        
        # This would require Chrome to be running with the extension loaded
        # For now, we'll just check if the setup looks correct
        
        self.log("INFO", "Chrome connection test requires:")
        self.log("INFO", "1. Chrome browser running")
        self.log("INFO", "2. MKD extension loaded")
        self.log("INFO", "3. Extension popup opened")
        
        # Check if Chrome is installed
        chrome_paths = []
        
        if self.system == "windows":
            chrome_paths = [
                Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
                Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
                Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe"
            ]
        elif self.system == "darwin":
            chrome_paths = [
                Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
            ]
        else:
            chrome_paths = [
                Path("/usr/bin/google-chrome"),
                Path("/usr/bin/chromium-browser"),
                Path("/opt/google/chrome/chrome")
            ]
        
        chrome_found = False
        for chrome_path in chrome_paths:
            if chrome_path.exists():
                self.log("OK", f"Chrome found: {chrome_path}")
                chrome_found = True
                break
        
        if not chrome_found:
            self.log("WARN", "Chrome browser not found in standard locations")
        
        return True
    
    def generate_installation_guide(self):
        """Generate installation guide based on test results."""
        print("\n" + "="*60)
        print("INSTALLATION GUIDE")
        print("="*60)
        
        failed_tests = [r for r in self.results if r["status"] == "FAIL"]
        
        if not failed_tests:
            print("✅ All tests passed! Native messaging should be working.")
            print("\nTo test the Chrome extension:")
            print("1. Open Chrome")
            print("2. Go to chrome://extensions/")
            print("3. Enable Developer mode")
            print("4. Load the extension from chrome-extension/ folder")
            print("5. Click the MKD icon and test recording")
            return
        
        print("❌ Issues found. Follow these steps to fix:\n")
        
        step = 1
        
        # Python environment issues
        python_issues = [r for r in self.results if "Python" in r["message"] or "Module" in r["message"]]
        if python_issues:
            print(f"{step}. Fix Python Environment:")
            print("   pip install -r requirements.txt")
            step += 1
        
        # Native host script issues
        script_issues = [r for r in self.results if "script" in r["message"].lower()]
        if script_issues:
            print(f"{step}. Check Native Host Script:")
            print("   python src/mkd_v2/native_host/host.py --test")
            step += 1
        
        # Registry/manifest issues
        registry_issues = [r for r in self.results if "registry" in r["message"].lower() or "manifest" in r["message"].lower()]
        if registry_issues:
            print(f"{step}. Install Native Messaging Host:")
            print("   python install_native_host.py")
            if self.system == "windows":
                print("   (Run as Administrator if needed)")
            step += 1
        
        # Communication issues
        comm_issues = [r for r in self.results if "communication" in r["message"].lower() or "response" in r["message"].lower()]
        if comm_issues:
            print(f"{step}. Test MKD Backend:")
            print("   python -m mkd_v2.native_host.host --debug")
            print("   (Should show 'Waiting for messages...')")
            step += 1
        
        print(f"\n{step}. Restart Chrome completely")
        print(f"{step+1}. Test the extension")
        
        print("\n" + "="*60)
    
    def run_all_tests(self):
        """Run all tests."""
        print("MKD Native Messaging Host Diagnostic")
        print("="*50)
        
        tests = [
            self.test_python_environment,
            self.test_native_host_script,
            self.test_registry_entries_windows,
            self.test_manifest_files,
            self.test_direct_communication,
            self.test_chrome_connection
        ]
        
        all_passed = True
        
        for test in tests:
            try:
                result = test()
                if not result:
                    all_passed = False
            except Exception as e:
                self.log("ERROR", f"Test crashed: {test.__name__}", str(e))
                all_passed = False
        
        # Generate guide
        self.generate_installation_guide()
        
        return all_passed


def main():
    """Main entry point."""
    tester = NativeHostTester()
    success = tester.run_all_tests()
    
    print(f"\nDiagnostic complete. Success: {success}")
    
    if not success:
        print("\nFor additional help:")
        print("- Check Chrome extension console (F12 in popup)")
        print("- Run: python chrome-extension/debug/connection_diagnostic.py")
        print("- View logs with debugLogger.downloadLogs() in extension console")
    
    input("\nPress Enter to exit...")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())