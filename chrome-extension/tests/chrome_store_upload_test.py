#!/usr/bin/env python3
"""
Chrome Web Store Upload Test Suite

This script validates the Chrome extension package for Chrome Web Store submission.
It checks all requirements, creates the upload package, and generates a detailed report.
"""

import json
import os
import re
import zipfile
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Tuple
import subprocess
import sys

class ChromeStoreUploadTester:
    """Validates and prepares Chrome extension for store upload."""
    
    def __init__(self):
        self.extension_dir = Path(__file__).parent.parent
        self.test_results = []
        self.warnings = []
        self.errors = []
        
        # Chrome Web Store requirements
        self.MAX_PACKAGE_SIZE = 100 * 1024 * 1024  # 100MB
        self.REQUIRED_MANIFEST_FIELDS = [
            "manifest_version", "name", "version", "description"
        ]
        self.REQUIRED_ICONS = [16, 48, 128]
        self.PROHIBITED_PERMISSIONS = [
            "debugger", "experimental", "plugins"
        ]
        self.STORE_LISTING_REQUIREMENTS = {
            "screenshots": {"min": 1, "max": 5, "size": (1280, 800)},
            "description": {"min_length": 132, "max_length": 12000},
            "short_description": {"max_length": 132}
        }
    
    def run_all_tests(self) -> bool:
        """Run all upload validation tests."""
        print("\nChrome Web Store Upload Validation")
        print("=" * 50)
        
        tests = [
            ("Manifest Validation", self.test_manifest),
            ("Version Format", self.test_version_format),
            ("Permissions Check", self.test_permissions),
            ("Icons Validation", self.test_icons),
            ("Content Security Policy", self.test_csp),
            ("File Structure", self.test_file_structure),
            ("Package Size", self.test_package_size),
            ("Code Quality", self.test_code_quality),
            ("Localization", self.test_localization),
            ("Store Listing Assets", self.test_store_assets)
        ]
        
        for test_name, test_func in tests:
            print(f"\n[TEST] {test_name}")
            print("-" * 30)
            
            try:
                passed, message = test_func()
                status = "[OK]" if passed else "[FAIL]"
                print(f"{status} {message}")
                
                self.test_results.append({
                    "test": test_name,
                    "passed": passed,
                    "message": message
                })
                
                if not passed:
                    self.errors.append(f"{test_name}: {message}")
                    
            except Exception as e:
                print(f"[ERROR] Test failed with exception: {e}")
                self.errors.append(f"{test_name}: {str(e)}")
                self.test_results.append({
                    "test": test_name,
                    "passed": False,
                    "message": str(e)
                })
        
        return self.generate_report()
    
    def test_manifest(self) -> Tuple[bool, str]:
        """Validate manifest.json against Chrome Web Store requirements."""
        manifest_path = self.extension_dir / "manifest.json"
        
        if not manifest_path.exists():
            return False, "manifest.json not found"
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Check required fields
            missing_fields = []
            for field in self.REQUIRED_MANIFEST_FIELDS:
                if field not in manifest:
                    missing_fields.append(field)
            
            if missing_fields:
                return False, f"Missing required fields: {', '.join(missing_fields)}"
            
            # Check manifest version
            if manifest.get("manifest_version") != 3:
                return False, f"Manifest V3 required, found V{manifest.get('manifest_version')}"
            
            # Check name length
            name = manifest.get("name", "")
            if len(name) > 45:
                self.warnings.append(f"Extension name is {len(name)} chars (max 45 recommended)")
            
            # Check description length
            description = manifest.get("description", "")
            if len(description) > 132:
                return False, f"Description too long: {len(description)} chars (max 132)"
            
            # Check for update_url (not allowed for Chrome Web Store)
            if "update_url" in manifest:
                return False, "update_url field not allowed for Chrome Web Store"
            
            # Check for required action/browser_action
            if "action" not in manifest and "browser_action" not in manifest:
                self.warnings.append("No action/browser_action defined")
            
            return True, "Manifest validation passed"
            
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON in manifest: {e}"
        except Exception as e:
            return False, f"Error reading manifest: {e}"
    
    def test_version_format(self) -> Tuple[bool, str]:
        """Validate version number format."""
        manifest_path = self.extension_dir / "manifest.json"
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        version = manifest.get("version", "")
        
        # Chrome version format: 1-4 dot-separated integers
        version_pattern = r'^(\d+)(\.\d+){0,3}$'
        if not re.match(version_pattern, version):
            return False, f"Invalid version format: {version}"
        
        # Check each part is <= 65535
        parts = version.split('.')
        for part in parts:
            if int(part) > 65535:
                return False, f"Version part {part} exceeds maximum (65535)"
        
        return True, f"Version {version} is valid"
    
    def test_permissions(self) -> Tuple[bool, str]:
        """Check for prohibited or dangerous permissions."""
        manifest_path = self.extension_dir / "manifest.json"
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        permissions = manifest.get("permissions", [])
        host_permissions = manifest.get("host_permissions", [])
        
        # Check for prohibited permissions
        prohibited_found = []
        for perm in permissions:
            if perm in self.PROHIBITED_PERMISSIONS:
                prohibited_found.append(perm)
        
        if prohibited_found:
            return False, f"Prohibited permissions found: {', '.join(prohibited_found)}"
        
        # Warn about powerful permissions
        powerful_perms = ["<all_urls>", "activeTab", "cookies", "webRequest"]
        powerful_found = []
        
        for perm in permissions + host_permissions:
            if perm in powerful_perms or "*://*/*" in perm:
                powerful_found.append(perm)
        
        if powerful_found:
            self.warnings.append(f"Powerful permissions require justification: {', '.join(powerful_found)}")
        
        # Check for native messaging permission
        if "nativeMessaging" in permissions:
            print("  Native messaging permission present (required for MKD)")
        
        return True, f"Permissions check passed ({len(permissions)} permissions)"
    
    def test_icons(self) -> Tuple[bool, str]:
        """Validate required icon files."""
        manifest_path = self.extension_dir / "manifest.json"
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        icons = manifest.get("icons", {})
        missing_sizes = []
        
        for size in self.REQUIRED_ICONS:
            size_str = str(size)
            if size_str not in icons:
                missing_sizes.append(size_str)
            else:
                icon_path = self.extension_dir / icons[size_str]
                if not icon_path.exists():
                    return False, f"Icon file not found: {icons[size_str]}"
                
                # Check file size
                file_size = icon_path.stat().st_size
                if file_size > 1024 * 1024:  # 1MB max
                    self.warnings.append(f"Icon {size}x{size} is large: {file_size/1024:.1f}KB")
        
        if missing_sizes:
            return False, f"Missing required icon sizes: {', '.join(missing_sizes)}"
        
        return True, "All required icons present"
    
    def test_csp(self) -> Tuple[bool, str]:
        """Validate Content Security Policy."""
        manifest_path = self.extension_dir / "manifest.json"
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        csp = manifest.get("content_security_policy", {})
        
        # Check for unsafe CSP directives
        if isinstance(csp, dict):
            for context, policy in csp.items():
                if "unsafe-inline" in policy:
                    return False, f"unsafe-inline not allowed in CSP ({context})"
                if "unsafe-eval" in policy:
                    return False, f"unsafe-eval not allowed in CSP ({context})"
        
        # Check all script files for inline scripts
        js_files = list(self.extension_dir.glob("**/*.js"))
        html_files = list(self.extension_dir.glob("**/*.html"))
        
        for html_file in html_files:
            content = html_file.read_text()
            if "<script>" in content and "</script>" in content:
                # Check if it's just a script src tag
                if not re.search(r'<script[^>]*src=', content):
                    self.warnings.append(f"Inline script found in {html_file.name}")
        
        return True, "CSP validation passed"
    
    def test_file_structure(self) -> Tuple[bool, str]:
        """Validate extension file structure."""
        required_files = ["manifest.json"]
        recommended_files = ["README.md", "LICENSE"]
        
        missing_required = []
        for file in required_files:
            if not (self.extension_dir / file).exists():
                missing_required.append(file)
        
        if missing_required:
            return False, f"Missing required files: {', '.join(missing_required)}"
        
        # Check for recommended files
        for file in recommended_files:
            if not (self.extension_dir / file).exists():
                self.warnings.append(f"Recommended file missing: {file}")
        
        # Check for unnecessary files
        unnecessary_patterns = ["*.pyc", "__pycache__", ".git", ".DS_Store", "Thumbs.db"]
        unnecessary_found = []
        
        for pattern in unnecessary_patterns:
            found = list(self.extension_dir.glob(f"**/{pattern}"))
            unnecessary_found.extend(found)
        
        if unnecessary_found:
            self.warnings.append(f"Found {len(unnecessary_found)} unnecessary files that should be excluded")
        
        return True, "File structure is valid"
    
    def test_package_size(self) -> Tuple[bool, str]:
        """Check total package size."""
        total_size = 0
        file_count = 0
        
        for file in self.extension_dir.rglob("*"):
            if file.is_file() and ".git" not in str(file):
                total_size += file.stat().st_size
                file_count += 1
        
        size_mb = total_size / (1024 * 1024)
        
        if total_size > self.MAX_PACKAGE_SIZE:
            return False, f"Package too large: {size_mb:.2f}MB (max 100MB)"
        
        if size_mb > 10:
            self.warnings.append(f"Package size is {size_mb:.2f}MB - consider optimization")
        
        return True, f"Package size: {size_mb:.2f}MB ({file_count} files)"
    
    def test_code_quality(self) -> Tuple[bool, str]:
        """Basic code quality checks."""
        issues = []
        
        js_files = list(self.extension_dir.glob("**/*.js"))
        
        for js_file in js_files:
            if "node_modules" in str(js_file) or "tests" in str(js_file):
                continue
                
            content = js_file.read_text()
            
            # Check for console.log statements
            if "console.log" in content:
                count = content.count("console.log")
                self.warnings.append(f"{js_file.name} contains {count} console.log statements")
            
            # Check for debugging code
            if "debugger;" in content:
                issues.append(f"Debugger statement in {js_file.name}")
            
            # Check for TODO comments
            if "TODO" in content or "FIXME" in content:
                self.warnings.append(f"TODO/FIXME comments in {js_file.name}")
            
            # Check for API keys or secrets
            if re.search(r'api[_-]?key\s*=\s*["\'][\w\-]+["\']', content, re.IGNORECASE):
                issues.append(f"Potential API key in {js_file.name}")
        
        if issues:
            return False, f"Code quality issues: {'; '.join(issues)}"
        
        return True, f"Code quality check passed ({len(js_files)} JS files)"
    
    def test_localization(self) -> Tuple[bool, str]:
        """Check localization support."""
        locales_dir = self.extension_dir / "_locales"
        
        if not locales_dir.exists():
            self.warnings.append("No localization support (_locales directory missing)")
            return True, "Localization not configured (optional)"
        
        locales = list(locales_dir.glob("*/messages.json"))
        
        if not locales:
            return False, "_locales exists but no message files found"
        
        # Check for default locale
        manifest_path = self.extension_dir / "manifest.json"
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        default_locale = manifest.get("default_locale")
        if not default_locale:
            return False, "_locales present but default_locale not set in manifest"
        
        if not (locales_dir / default_locale / "messages.json").exists():
            return False, f"Default locale {default_locale} not found"
        
        return True, f"Localization configured ({len(locales)} locales)"
    
    def test_store_assets(self) -> Tuple[bool, str]:
        """Check for Chrome Web Store listing assets."""
        assets_dir = self.extension_dir / "store_assets"
        
        if not assets_dir.exists():
            assets_dir.mkdir(exist_ok=True)
        
        # Check for screenshots
        screenshots = list(assets_dir.glob("screenshot*.png"))
        if len(screenshots) < 1:
            self.warnings.append("No screenshots found (at least 1 required for store listing)")
        
        # Check for promotional images
        promo_sizes = {
            "small": (440, 280),
            "large": (920, 680),
            "marquee": (1400, 560)
        }
        
        for size_name, dimensions in promo_sizes.items():
            promo_file = assets_dir / f"promo_{size_name}.png"
            if not promo_file.exists():
                self.warnings.append(f"Missing {size_name} promotional image ({dimensions[0]}x{dimensions[1]})")
        
        # Create store listing template
        self.create_store_listing_template()
        
        return True, "Store assets check complete"
    
    def create_store_listing_template(self):
        """Create a template for Chrome Web Store listing."""
        listing_path = self.extension_dir / "store_assets" / "store_listing.md"
        
        template = """# Chrome Web Store Listing

## Extension Name
MKD Automation - Web Recording & Playback

## Short Description (max 132 chars)
Record and replay browser interactions for automation testing. Capture clicks, typing, and navigation with precision.

## Detailed Description

### Overview
MKD Automation is a powerful browser automation tool that records your interactions with web pages and replays them with precision. Perfect for QA engineers, developers, and anyone who needs to automate repetitive web tasks.

### Key Features
- **One-Click Recording** - Start recording with a single click
- **Smart Element Detection** - Intelligent CSS selector generation
- **Cross-Platform Support** - Works on Windows, Mac, and Linux
- **Native Integration** - Seamless connection with MKD desktop app
- **Secure & Private** - All data stored locally, no cloud uploads
- **Visual Feedback** - Real-time recording indicators and progress

### Use Cases
- Automated testing of web applications
- Repetitive form filling and data entry
- Web scraping and monitoring
- UI regression testing
- Training and documentation

### How It Works
1. Click the MKD icon in your browser toolbar
2. Press "Start Recording" to begin capturing
3. Interact with any webpage normally
4. Stop recording to save your automation script
5. Replay anytime with the MKD desktop application

### Privacy & Security
- No data leaves your computer
- No tracking or analytics
- Open source and transparent
- Minimal permissions required

### Support
- Documentation: https://github.com/flying-pisces/mkd_automation
- Issues: https://github.com/flying-pisces/mkd_automation/issues
- Email: support@mkdautomation.com

## Category
Developer Tools > Testing

## Language
English (US)

## Tags
- automation
- testing
- recording
- playback
- web-automation
- browser-automation
- qa-tools
- test-automation
- ui-testing
- regression-testing

## Support URLs
- Website: https://github.com/flying-pisces/mkd_automation
- Support: https://github.com/flying-pisces/mkd_automation/issues
"""
        
        listing_path.write_text(template)
        print(f"  Created store listing template: {listing_path}")
    
    def create_upload_package(self) -> Path:
        """Create the ZIP package for upload."""
        package_name = f"mkd-automation-{self.get_version()}.zip"
        package_path = self.extension_dir / "dist" / package_name
        
        # Create dist directory
        package_path.parent.mkdir(exist_ok=True)
        
        # Files to exclude from package
        exclude_patterns = [
            "*.pyc", "__pycache__", ".git", ".gitignore",
            "*.md", "tests", "store_assets", "dist",
            "*.py", "*.sh", "*.bat", ".DS_Store", "Thumbs.db"
        ]
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in self.extension_dir.rglob("*"):
                if file.is_file():
                    relative_path = file.relative_to(self.extension_dir)
                    
                    # Check if file should be excluded
                    exclude = False
                    for pattern in exclude_patterns:
                        if pattern.replace("*", "") in str(relative_path):
                            exclude = True
                            break
                    
                    if not exclude:
                        zipf.write(file, relative_path)
        
        # Calculate package hash
        with open(package_path, 'rb') as f:
            package_hash = hashlib.sha256(f.read()).hexdigest()
        
        size_mb = package_path.stat().st_size / (1024 * 1024)
        print(f"\n[OK] Upload package created:")
        print(f"      File: {package_path}")
        print(f"      Size: {size_mb:.2f}MB")
        print(f"      SHA256: {package_hash}")
        
        return package_path
    
    def get_version(self) -> str:
        """Get extension version from manifest."""
        manifest_path = self.extension_dir / "manifest.json"
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        return manifest.get("version", "1.0.0")
    
    def generate_report(self) -> bool:
        """Generate upload readiness report."""
        print("\n" + "=" * 50)
        print("CHROME WEB STORE UPLOAD TEST REPORT")
        print("=" * 50)
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["passed"])
        failed_tests = total_tests - passed_tests
        
        print(f"\nTest Results:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Show errors
        if self.errors:
            print(f"\n[X] Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        # Show warnings
        if self.warnings:
            print(f"\n[!] Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        # Upload readiness
        print("\n" + "-" * 50)
        if failed_tests == 0:
            print("[OK] READY FOR UPLOAD")
            print("\nNext Steps:")
            print("1. Create upload package by running: create_upload_package()")
            print("2. Sign in to Chrome Web Store Developer Dashboard")
            print("3. Upload the ZIP file from dist/ directory")
            print("4. Complete store listing with assets from store_assets/")
            print("5. Submit for review")
            
            # Create the upload package
            package_path = self.create_upload_package()
            
            return True
        else:
            print("[X] NOT READY FOR UPLOAD")
            print(f"\nFix {failed_tests} failed test(s) before uploading")
            return False
    
    def run_automated_fixes(self):
        """Attempt to automatically fix common issues."""
        print("\n[AUTO-FIX] Attempting automated fixes...")
        
        fixes_applied = []
        
        # Remove console.log statements
        js_files = list(self.extension_dir.glob("**/*.js"))
        for js_file in js_files:
            if "tests" in str(js_file):
                continue
                
            content = js_file.read_text()
            original = content
            
            # Comment out console.log statements
            content = re.sub(r'^(\s*)(console\.log\(.*?\);?)$', 
                            r'\1// \2  // Commented for production', 
                            content, flags=re.MULTILINE)
            
            if content != original:
                js_file.write_text(content)
                fixes_applied.append(f"Commented console.log in {js_file.name}")
        
        if fixes_applied:
            print(f"[OK] Applied {len(fixes_applied)} fixes:")
            for fix in fixes_applied:
                print(f"     - {fix}")
        else:
            print("[OK] No automated fixes needed")


def main():
    """Main entry point."""
    tester = ChromeStoreUploadTester()
    
    # Run all tests
    ready = tester.run_all_tests()
    
    # Attempt fixes if needed
    if not ready:
        tester.run_automated_fixes()
        print("\n[INFO] Re-running tests after fixes...")
        ready = tester.run_all_tests()
    
    sys.exit(0 if ready else 1)


if __name__ == "__main__":
    main()