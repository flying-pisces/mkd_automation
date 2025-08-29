#!/usr/bin/env python3
"""
MKD Automation System Compatibility Check

This script checks if the current macOS system is compatible with Chrome native messaging
and identifies potential blockers before development begins.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

class SystemChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []
        
    def log_pass(self, message):
        self.passed.append(f"✅ {message}")
        
    def log_warning(self, message):
        self.warnings.append(f"⚠️  {message}")
        
    def log_issue(self, message):
        self.issues.append(f"❌ {message}")
        
    def check_macos_version(self):
        """Check macOS version compatibility."""
        try:
            version = platform.mac_ver()[0]
            if version:
                major_version = int(version.split('.')[0])
                if major_version >= 11:  # macOS Big Sur and later
                    self.log_pass(f"macOS version {version} is compatible")
                else:
                    self.log_warning(f"macOS version {version} may have compatibility issues")
            else:
                self.log_issue("Could not detect macOS version")
        except Exception as e:
            self.log_issue(f"Error checking macOS version: {e}")
    
    def check_gatekeeper_status(self):
        """Check if Gatekeeper will block native messaging hosts."""
        try:
            # Check overall Gatekeeper status
            result = subprocess.run(['spctl', '--status'], 
                                  capture_output=True, text=True)
            
            if 'assessments enabled' in result.stdout:
                self.log_warning("Gatekeeper is enabled - may block unsigned native hosts")
                
                # Check if system allows unsigned applications
                try:
                    # This will fail on managed systems
                    subprocess.run(['spctl', '--master-disable'], 
                                 capture_output=True, check=False)
                    subprocess.run(['spctl', '--master-enable'], 
                                 capture_output=True, check=False)
                    self.log_pass("Gatekeeper settings can be modified")
                except:
                    self.log_issue("Gatekeeper settings cannot be modified (likely managed system)")
            else:
                self.log_pass("Gatekeeper is disabled")
                
        except FileNotFoundError:
            self.log_issue("spctl command not found - cannot check Gatekeeper status")
        except Exception as e:
            self.log_issue(f"Error checking Gatekeeper: {e}")
    
    def check_mdm_profile(self):
        """Check if system is managed by MDM/corporate profile."""
        try:
            # Check for configuration profiles
            result = subprocess.run(['profiles', 'list'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                if 'Configuration profiles' in result.stdout and len(result.stdout.strip()) > 50:
                    self.log_warning("System appears to be managed by configuration profiles")
                    self.log_warning("You may not be able to change security settings")
                else:
                    self.log_pass("No restrictive configuration profiles detected")
            else:
                self.log_warning("Could not check configuration profiles")
                
        except FileNotFoundError:
            self.log_warning("profiles command not found")
        except Exception as e:
            self.log_warning(f"Error checking profiles: {e}")
    
    def check_python_availability(self):
        """Check Python installation and accessibility."""
        pythons_to_check = [
            '/usr/bin/python3',
            '/opt/homebrew/bin/python3', 
            '/opt/homebrew/anaconda3/bin/python3',
            'python3'
        ]
        
        working_pythons = []
        
        for python_path in pythons_to_check:
            try:
                result = subprocess.run([python_path, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    working_pythons.append((python_path, result.stdout.strip()))
                    
                    # Check if this Python can be executed by Gatekeeper
                    if python_path.startswith('/'):
                        spctl_result = subprocess.run(['spctl', '--assess', '--verbose', python_path], 
                                                    capture_output=True, text=True)
                        if 'accepted' in spctl_result.stderr:
                            self.log_pass(f"Python at {python_path} is Gatekeeper-approved")
                        else:
                            self.log_warning(f"Python at {python_path} may be blocked by Gatekeeper")
                    
            except FileNotFoundError:
                continue
            except Exception as e:
                self.log_warning(f"Error checking {python_path}: {e}")
        
        if working_pythons:
            self.log_pass(f"Found {len(working_pythons)} working Python installations")
            for path, version in working_pythons:
                print(f"    {path}: {version}")
        else:
            self.log_issue("No working Python 3 installations found")
    
    def check_chrome_installation(self):
        """Check if Chrome is installed and accessible."""
        chrome_paths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chromium.app/Contents/MacOS/Chromium'
        ]
        
        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                self.log_pass(f"Chrome found at {chrome_path}")
                return
                
        self.log_issue("Chrome not found - install Google Chrome or Chromium")
    
    def check_native_messaging_directory(self):
        """Check native messaging host directory."""
        nm_dir = Path.home() / "Library/Application Support/Google/Chrome/NativeMessagingHosts"
        
        if nm_dir.exists():
            self.log_pass("Native messaging directory exists")
            
            # Check permissions
            if os.access(nm_dir, os.W_OK):
                self.log_pass("Native messaging directory is writable")
            else:
                self.log_issue("Native messaging directory is not writable")
                
        else:
            self.log_warning("Native messaging directory does not exist (will be created)")
    
    def check_project_structure(self):
        """Check if current project has the expected structure."""
        expected_files = [
            'src/mkd_v2/native_host/host.py',
            'chrome-extension/manifest.json',
            'chrome-extension/src/background.js'
        ]
        
        project_root = Path.cwd()
        missing_files = []
        
        for file_path in expected_files:
            if not (project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_warning(f"Missing expected project files: {', '.join(missing_files)}")
        else:
            self.log_pass("Project structure looks correct")
    
    def run_all_checks(self):
        """Run all system checks."""
        print("🔍 MKD Automation System Compatibility Check")
        print("=" * 50)
        
        self.check_macos_version()
        self.check_gatekeeper_status()
        self.check_mdm_profile()
        self.check_python_availability()
        self.check_chrome_installation()
        self.check_native_messaging_directory()
        self.check_project_structure()
        
        # Print results
        print("\n📊 Results:")
        print("-" * 30)
        
        for item in self.passed:
            print(item)
            
        if self.warnings:
            print()
            for item in self.warnings:
                print(item)
        
        if self.issues:
            print()
            for item in self.issues:
                print(item)
        
        # Summary
        print(f"\n📈 Summary: {len(self.passed)} passed, {len(self.warnings)} warnings, {len(self.issues)} issues")
        
        if self.issues:
            print("\n🚨 BLOCKERS DETECTED:")
            print("Your system may not be compatible with Chrome native messaging development.")
            print("Please resolve the issues above or use a different development machine.")
            return False
        elif self.warnings:
            print("\n⚠️  POTENTIAL ISSUES:")
            print("Your system may work but could encounter problems.")
            print("Consider resolving warnings before starting development.")
            return True
        else:
            print("\n🎉 ALL CHECKS PASSED:")
            print("Your system appears ready for Chrome native messaging development!")
            return True

def main():
    checker = SystemChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()