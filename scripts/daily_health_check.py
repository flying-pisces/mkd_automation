#!/usr/bin/env python
"""
Daily Health Check Script
Runs critical tests to ensure extension remains in good health during development
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

class DailyHealthCheck:
    """Performs daily health checks on the Chrome extension."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.extension_dir = self.project_root / "chrome-extension"
        self.results = {}
        
    def run_all_checks(self):
        """Run all daily health checks."""
        print("[HEALTH] Daily Health Check")
        print(f"[DATE] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        checks = [
            ("Extension Structure", self.check_extension_structure),
            ("Manifest Validity", self.check_manifest_validity),
            ("Critical Security", self.check_critical_security),
            ("Python Backend", self.check_python_backend),
            ("File Integrity", self.check_file_integrity)
        ]
        
        for check_name, check_function in checks:
            print(f"\n[CHECK] {check_name}...")
            try:
                result = check_function()
                self.results[check_name] = result
                status = "[OK] HEALTHY" if result else "[FAIL] ISSUE"
                print(f"   {status}")
            except Exception as e:
                self.results[check_name] = False
                print(f"   [FAIL] ERROR: {e}")
        
        return self.generate_health_report()
    
    def check_extension_structure(self):
        """Check if extension has correct file structure."""
        required_files = [
            "manifest.json",
            "src/background.js",
            "src/content.js", 
            "src/popup/popup.html",
            "src/popup/popup.js",
            "src/popup/popup.css"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.extension_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"     Missing files: {', '.join(missing_files)}")
            return False
        
        print(f"     All {len(required_files)} required files present")
        return True
    
    def check_manifest_validity(self):
        """Check if manifest.json is valid."""
        manifest_file = self.extension_dir / "manifest.json"
        
        try:
            with open(manifest_file) as f:
                manifest = json.load(f)
            
            required_fields = ["name", "version", "manifest_version", "permissions"]
            missing_fields = [field for field in required_fields if field not in manifest]
            
            if missing_fields:
                print(f"     Missing fields: {', '.join(missing_fields)}")
                return False
            
            if manifest["manifest_version"] != 3:
                print(f"     Wrong manifest version: {manifest['manifest_version']} (should be 3)")
                return False
            
            print(f"     Valid manifest v{manifest['manifest_version']}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"     JSON decode error: {e}")
            return False
        except Exception as e:
            print(f"     Manifest error: {e}")
            return False
    
    def check_critical_security(self):
        """Check for critical security issues."""
        js_files = list(self.extension_dir.rglob("*.js"))
        issues = []
        
        for js_file in js_files:
            try:
                content = js_file.read_text()
                
                # Check for innerHTML (high priority security issue)
                if '.innerHTML' in content:
                    issues.append(f"{js_file.name}: innerHTML usage")
                
                # Check for eval
                if 'eval(' in content:
                    issues.append(f"{js_file.name}: eval() usage")
                    
            except Exception:
                pass  # Skip files that can't be read
        
        if issues:
            print(f"     Security issues found: {len(issues)}")
            for issue in issues[:3]:  # Show first 3
                print(f"       - {issue}")
            return False
        
        print(f"     No critical security issues in {len(js_files)} JS files")
        return True
    
    def check_python_backend(self):
        """Check if Python backend is functional."""
        try:
            # Run basic backend test
            result = subprocess.run(
                [sys.executable, "test_recording.py"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("     Python backend functional")
                return True
            else:
                print(f"     Backend test failed (exit code {result.returncode})")
                return False
                
        except subprocess.TimeoutExpired:
            print("     Backend test timed out")
            return False
        except Exception as e:
            print(f"     Backend test error: {e}")
            return False
    
    def check_file_integrity(self):
        """Check for file integrity issues."""
        issues = []
        
        # Check icon files aren't placeholders
        icons_dir = self.extension_dir / "icons"
        if icons_dir.exists():
            for icon_file in icons_dir.glob("*.png"):
                size = icon_file.stat().st_size
                if size < 100:  # Less than 100 bytes likely placeholder
                    issues.append(f"{icon_file.name}: placeholder file ({size} bytes)")
        
        # Check for large files that shouldn't be there
        for file in self.extension_dir.rglob("*"):
            if file.is_file():
                size = file.stat().st_size
                if size > 5 * 1024 * 1024:  # 5MB+
                    issues.append(f"{file.name}: very large file ({size//1024//1024}MB)")
        
        if issues:
            print(f"     File integrity issues: {len(issues)}")
            for issue in issues[:3]:
                print(f"       - {issue}")
            return False
        
        print("     All files have good integrity")
        return True
    
    def generate_health_report(self):
        """Generate overall health report."""
        healthy_checks = sum(1 for result in self.results.values() if result)
        total_checks = len(self.results)
        health_score = (healthy_checks / total_checks) * 100 if total_checks > 0 else 0
        
        print("\n" + "=" * 50)
        print("[REPORT] HEALTH REPORT")
        print("=" * 50)
        
        for check_name, result in self.results.items():
            status = "[OK] HEALTHY" if result else "[FAIL] NEEDS ATTENTION"
            print(f"   {status}: {check_name}")
        
        print(f"\n[SCORE] Overall Health: {healthy_checks}/{total_checks} ({health_score:.1f}%)")
        
        if health_score >= 80:
            print("[GOOD] GOOD HEALTH - Development can continue")
            return True
        elif health_score >= 60:
            print("[FAIR] FAIR HEALTH - Address issues soon")
            return False
        else:
            print("[POOR] POOR HEALTH - Fix critical issues immediately")
            return False

def main():
    """Run daily health check."""
    try:
        health_checker = DailyHealthCheck()
        success = health_checker.run_all_checks()
        return 0 if success else 1
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())