#!/usr/bin/env python3
"""
Security Audit Test Suite for MKD Automation Chrome Extension
Week 1 - Phase 1.1: Security Hardening Validation

This script validates all security requirements for Chrome Web Store submission:
- XSS vulnerability testing
- Content Security Policy validation
- Input validation verification
- Permission audit
- Store policy compliance
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Any

class SecurityAuditResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results = []
    
    def add_pass(self, test_name: str, description: str):
        self.passed += 1
        self.results.append({
            'status': 'PASS',
            'test': test_name,
            'description': description,
            'details': None
        })
        print(f"[PASS] {test_name}: {description}")
    
    def add_fail(self, test_name: str, description: str, details: str = None):
        self.failed += 1
        self.results.append({
            'status': 'FAIL',
            'test': test_name,
            'description': description,
            'details': details
        })
        print(f"[FAIL] {test_name}: {description}")
        if details:
            print(f"       Details: {details}")
    
    def add_warning(self, test_name: str, description: str, details: str = None):
        self.warnings += 1
        self.results.append({
            'status': 'WARN',
            'test': test_name,
            'description': description,
            'details': details
        })
        print(f"[WARN] {test_name}: {description}")
        if details:
            print(f"       Details: {details}")
    
    def summary(self):
        total = self.passed + self.failed + self.warnings
        print(f"\n" + "="*60)
        print(f"SECURITY AUDIT SUMMARY")
        print(f"="*60)
        print(f"Total Tests: {total}")
        print(f"Passed:      {self.passed}")
        print(f"Failed:      {self.failed}")
        print(f"Warnings:    {self.warnings}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%" if total > 0 else "N/A")
        
        if self.failed == 0:
            print(f"\n[OK] All security tests passed! Extension ready for store submission.")
        else:
            print(f"\n[FAIL] {self.failed} security issues must be fixed before submission.")
        
        return self.failed == 0

class ChromeExtensionSecurityAuditor:
    def __init__(self, extension_path: str):
        self.extension_path = Path(extension_path)
        self.result = SecurityAuditResult()
        
        # Validate extension directory exists
        if not self.extension_path.exists():
            raise FileNotFoundError(f"Extension directory not found: {extension_path}")
    
    def run_full_audit(self):
        """Run complete security audit"""
        print("MKD Automation Chrome Extension - Security Audit")
        print("="*60)
        
        # Phase 1: XSS Vulnerability Tests
        print("\nPhase 1: XSS Vulnerability Testing")
        print("-"*40)
        self.test_innerHTML_usage()
        self.test_dangerous_functions()
        self.test_input_sanitization()
        
        # Phase 2: Content Security Policy Tests
        print("\nPhase 2: Content Security Policy Testing")
        print("-"*40)
        self.test_csp_implementation()
        self.test_csp_compliance()
        
        # Phase 3: Input Validation Tests
        print("\nPhase 3: Input Validation Testing")
        print("-"*40)
        self.test_message_validation()
        self.test_parameter_validation()
        self.test_security_utils()
        
        # Phase 4: Permission Audit
        print("\nPhase 4: Permission Audit")
        print("-"*40)
        self.test_permission_minimization()
        self.test_permission_justification()
        
        # Phase 5: Store Policy Compliance
        print("\nPhase 5: Store Policy Compliance")
        print("-"*40)
        self.test_manifest_compliance()
        self.test_icon_compliance()
        self.test_privacy_policy()
        
        return self.result.summary()
    
    def test_innerHTML_usage(self):
        """Test for dangerous innerHTML usage"""
        dangerous_patterns = [
            r'\.innerHTML\s*=',
            r'\.outerHTML\s*=',
            r'document\.write\(',
            r'eval\(',
        ]
        
        js_files = list(self.extension_path.glob('**/*.js'))
        violations = []
        
        for js_file in js_files:
            try:
                content = js_file.read_text(encoding='utf-8')
                
                for pattern in dangerous_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        violations.append(f"{js_file.name}:{line_num} - {match.group()}")
            except Exception as e:
                self.result.add_warning("innerHTML_scan", f"Could not scan {js_file.name}", str(e))
        
        if violations:
            self.result.add_fail(
                "innerHTML_usage", 
                "Dangerous innerHTML usage found",
                "; ".join(violations)
            )
        else:
            self.result.add_pass("innerHTML_usage", "No dangerous innerHTML usage detected")
    
    def test_dangerous_functions(self):
        """Test for other dangerous JavaScript functions"""
        dangerous_functions = [
            r'setTimeout\s*\(\s*["\'][^"\']*["\']',  # setTimeout with string
            r'setInterval\s*\(\s*["\'][^"\']*["\']',  # setInterval with string
            r'Function\s*\(',  # Function constructor
            r'\.execCommand\(',  # Deprecated execCommand
        ]
        
        js_files = list(self.extension_path.glob('**/*.js'))
        violations = []
        
        for js_file in js_files:
            try:
                content = js_file.read_text(encoding='utf-8')
                
                for pattern in dangerous_functions:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        violations.append(f"{js_file.name}:{line_num} - {match.group()}")
            except Exception as e:
                self.result.add_warning("dangerous_functions", f"Could not scan {js_file.name}", str(e))
        
        if violations:
            self.result.add_warning(
                "dangerous_functions", 
                "Potentially dangerous functions found",
                "; ".join(violations)
            )
        else:
            self.result.add_pass("dangerous_functions", "No dangerous functions detected")
    
    def test_input_sanitization(self):
        """Test for input sanitization implementation"""
        # Look for SecurityUtils class and validation methods
        js_files = list(self.extension_path.glob('**/*.js'))
        found_security_utils = False
        found_validation = False
        
        validation_patterns = [
            r'class\s+.*SecurityUtils',
            r'validateString\s*\(',
            r'validateMessageType\s*\(',
            r'sanitize.*\(',
        ]
        
        for js_file in js_files:
            try:
                content = js_file.read_text(encoding='utf-8')
                
                if re.search(r'class\s+.*SecurityUtils', content):
                    found_security_utils = True
                
                for pattern in validation_patterns[1:]:
                    if re.search(pattern, content):
                        found_validation = True
                        break
            except Exception as e:
                self.result.add_warning("input_sanitization", f"Could not scan {js_file.name}", str(e))
        
        if found_security_utils and found_validation:
            self.result.add_pass("input_sanitization", "Input sanitization implemented")
        else:
            self.result.add_fail(
                "input_sanitization", 
                "Input sanitization not properly implemented",
                f"SecurityUtils: {found_security_utils}, Validation: {found_validation}"
            )
    
    def test_csp_implementation(self):
        """Test Content Security Policy implementation"""
        manifest_path = self.extension_path / "manifest.json"
        
        if not manifest_path.exists():
            self.result.add_fail("csp_manifest", "manifest.json not found")
            return
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            csp = manifest.get('content_security_policy', {})
            
            if not csp:
                self.result.add_fail("csp_implementation", "No Content Security Policy defined")
                return
            
            extension_pages_csp = csp.get('extension_pages', '')
            
            if not extension_pages_csp:
                self.result.add_fail("csp_extension_pages", "No CSP for extension pages")
                return
            
            # Check for required CSP directives
            required_directives = ['script-src', 'object-src']
            missing_directives = []
            
            for directive in required_directives:
                if directive not in extension_pages_csp:
                    missing_directives.append(directive)
            
            if missing_directives:
                self.result.add_fail(
                    "csp_directives", 
                    "Missing required CSP directives",
                    ", ".join(missing_directives)
                )
            else:
                self.result.add_pass("csp_implementation", "Content Security Policy properly implemented")
                
        except Exception as e:
            self.result.add_fail("csp_implementation", "Failed to parse manifest.json", str(e))
    
    def test_csp_compliance(self):
        """Test CSP compliance in code"""
        # Check for CSP violations in HTML files
        html_files = list(self.extension_path.glob('**/*.html'))
        violations = []
        
        for html_file in html_files:
            try:
                content = html_file.read_text(encoding='utf-8')
                
                # Check for inline scripts (ignore empty or external scripts)
                inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
                actual_inline = [script for script in inline_scripts if script.strip()]
                if actual_inline:
                    violations.append(f"{html_file.name}: Inline script found")
                
                # Check for inline event handlers (avoid false positives)
                inline_events = re.findall(r'\bon(?:click|load|error|submit|change|focus|blur|keypress|keydown|keyup|mousedown|mouseup|mouseover|mouseout)\s*=\s*["\'][^"\']*["\']', content, re.IGNORECASE)
                if inline_events:
                    violations.append(f"{html_file.name}: Inline event handlers found")
                    
            except Exception as e:
                self.result.add_warning("csp_compliance", f"Could not scan {html_file.name}", str(e))
        
        if violations:
            self.result.add_fail(
                "csp_compliance", 
                "CSP compliance violations found",
                "; ".join(violations)
            )
        else:
            self.result.add_pass("csp_compliance", "No CSP compliance violations found")
    
    def test_message_validation(self):
        """Test message validation in background script"""
        background_js = self.extension_path / "src" / "background.js"
        
        if not background_js.exists():
            self.result.add_fail("message_validation", "background.js not found")
            return
        
        try:
            content = background_js.read_text(encoding='utf-8')
            
            # Look for message validation patterns
            validation_checks = [
                r'if\s*\(!message\s*\|\|\s*typeof\s+message\s*!==\s*["\']object["\']',
                r'validateMessageType\s*\(',
                r'validateRecordingConfig\s*\(',
                r'validateRecordingId\s*\(',
            ]
            
            found_checks = 0
            for pattern in validation_checks:
                if re.search(pattern, content):
                    found_checks += 1
            
            if found_checks >= 3:
                self.result.add_pass("message_validation", "Message validation implemented")
            else:
                self.result.add_fail(
                    "message_validation", 
                    "Insufficient message validation",
                    f"Found {found_checks}/4 validation patterns"
                )
                
        except Exception as e:
            self.result.add_fail("message_validation", "Could not analyze background.js", str(e))
    
    def test_parameter_validation(self):
        """Test parameter validation in native messaging"""
        background_js = self.extension_path / "src" / "background.js"
        
        if not background_js.exists():
            return
        
        try:
            content = background_js.read_text(encoding='utf-8')
            
            # Look for parameter validation in sendMessage method
            validation_patterns = [
                r'typeof\s+command\s*!==\s*["\']string["\']',
                r'typeof\s+params\s*!==\s*["\']object["\']',
                r'validateRecordingConfig\s*\(',
            ]
            
            found_patterns = 0
            for pattern in validation_patterns:
                if re.search(pattern, content):
                    found_patterns += 1
            
            if found_patterns >= 2:
                self.result.add_pass("parameter_validation", "Parameter validation implemented")
            else:
                self.result.add_fail(
                    "parameter_validation", 
                    "Insufficient parameter validation",
                    f"Found {found_patterns}/3 validation patterns"
                )
                
        except Exception as e:
            self.result.add_fail("parameter_validation", "Could not analyze parameter validation", str(e))
    
    def test_security_utils(self):
        """Test SecurityUtils class implementation"""
        js_files = list(self.extension_path.glob('**/*.js'))
        security_utils_found = False
        required_methods = ['validateString', 'validateMessageType', 'validateRecordingConfig']
        found_methods = []
        
        for js_file in js_files:
            try:
                content = js_file.read_text(encoding='utf-8')
                
                if 'class SecurityUtils' in content:
                    security_utils_found = True
                
                for method in required_methods:
                    if f'static {method}' in content or f'{method}(' in content:
                        found_methods.append(method)
                        
            except Exception as e:
                continue
        
        if security_utils_found and len(set(found_methods)) >= len(required_methods):
            self.result.add_pass("security_utils", "SecurityUtils class properly implemented")
        else:
            self.result.add_fail(
                "security_utils", 
                "SecurityUtils class incomplete",
                f"Found: {security_utils_found}, Methods: {list(set(found_methods))}"
            )
    
    def test_permission_minimization(self):
        """Test that permissions are minimal and necessary"""
        manifest_path = self.extension_path / "manifest.json"
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            permissions = manifest.get('permissions', [])
            
            # Check for overly broad permissions
            dangerous_permissions = ['<all_urls>', '*://*/*', 'tabs', 'history', 'bookmarks']
            found_dangerous = [p for p in permissions if p in dangerous_permissions]
            
            # Check content script matches
            content_scripts = manifest.get('content_scripts', [])
            broad_matches = []
            for cs in content_scripts:
                matches = cs.get('matches', [])
                if '<all_urls>' in matches or '*://*/*' in matches:
                    broad_matches.extend(matches)
            
            if found_dangerous:
                self.result.add_fail(
                    "permission_minimization", 
                    "Overly broad permissions found",
                    ", ".join(found_dangerous)
                )
            elif broad_matches:
                self.result.add_warning(
                    "permission_minimization", 
                    "Content script uses broad URL matches",
                    ", ".join(broad_matches)
                )
            else:
                self.result.add_pass("permission_minimization", "Permissions are appropriately minimal")
                
        except Exception as e:
            self.result.add_fail("permission_minimization", "Could not analyze permissions", str(e))
    
    def test_permission_justification(self):
        """Test that all permissions are justified"""
        manifest_path = self.extension_path / "manifest.json"
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            permissions = manifest.get('permissions', [])
            justified_permissions = {
                'activeTab': 'Required for recording user interactions on current tab',
                'storage': 'Required for saving extension settings and session data',
                'nativeMessaging': 'Required for communication with Python backend'
            }
            
            unjustified = []
            for permission in permissions:
                if permission not in justified_permissions:
                    unjustified.append(permission)
            
            if unjustified:
                self.result.add_fail(
                    "permission_justification", 
                    "Unjustified permissions found",
                    ", ".join(unjustified)
                )
            else:
                self.result.add_pass("permission_justification", "All permissions are justified")
                
        except Exception as e:
            self.result.add_fail("permission_justification", "Could not analyze permission justification", str(e))
    
    def test_manifest_compliance(self):
        """Test manifest.json compliance with store requirements"""
        manifest_path = self.extension_path / "manifest.json"
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            required_fields = ['manifest_version', 'name', 'version', 'description']
            missing_fields = []
            
            for field in required_fields:
                if field not in manifest:
                    missing_fields.append(field)
                elif not manifest[field]:
                    missing_fields.append(f"{field} (empty)")
            
            # Check manifest version
            if manifest.get('manifest_version') != 3:
                self.result.add_fail("manifest_version", "Must use Manifest V3")
            
            if missing_fields:
                self.result.add_fail(
                    "manifest_compliance", 
                    "Missing required manifest fields",
                    ", ".join(missing_fields)
                )
            else:
                self.result.add_pass("manifest_compliance", "Manifest meets store requirements")
                
        except Exception as e:
            self.result.add_fail("manifest_compliance", "Could not validate manifest", str(e))
    
    def test_icon_compliance(self):
        """Test icon compliance with store requirements"""
        icons_dir = self.extension_path / "icons"
        required_sizes = [16, 48, 128]
        
        if not icons_dir.exists():
            self.result.add_fail("icon_compliance", "Icons directory not found")
            return
        
        missing_icons = []
        oversized_icons = []
        
        for size in required_sizes:
            icon_path = icons_dir / f"icon{size}.png"
            
            if not icon_path.exists():
                missing_icons.append(str(size))
            else:
                # Check file size (should be > 100 bytes for real icons)
                file_size = icon_path.stat().st_size
                if file_size < 100:
                    missing_icons.append(f"{size} (placeholder)")
                elif file_size > 50000:  # 50KB limit
                    oversized_icons.append(f"{size} ({file_size} bytes)")
        
        if missing_icons:
            self.result.add_fail(
                "icon_compliance", 
                "Missing or invalid icon files",
                ", ".join(missing_icons)
            )
        elif oversized_icons:
            self.result.add_warning(
                "icon_compliance", 
                "Oversized icon files",
                ", ".join(oversized_icons)
            )
        else:
            self.result.add_pass("icon_compliance", "All required icons present and valid")
    
    def test_privacy_policy(self):
        """Test privacy policy exists and is accessible"""
        privacy_policy_paths = [
            self.extension_path.parent / "PRIVACY_POLICY.md",
            self.extension_path / "PRIVACY_POLICY.md",
            self.extension_path / "privacy_policy.md"
        ]
        
        found_policy = False
        for policy_path in privacy_policy_paths:
            if policy_path.exists():
                found_policy = True
                
                # Check policy content
                try:
                    content = policy_path.read_text(encoding='utf-8')
                    
                    required_sections = [
                        'information we collect',
                        'how we use',
                        'data sharing',
                        'permissions',
                        'contact'
                    ]
                    
                    missing_sections = []
                    content_lower = content.lower()
                    
                    for section in required_sections:
                        if section not in content_lower:
                            missing_sections.append(section)
                    
                    if missing_sections:
                        self.result.add_warning(
                            "privacy_policy", 
                            "Privacy policy missing sections",
                            ", ".join(missing_sections)
                        )
                    else:
                        self.result.add_pass("privacy_policy", "Privacy policy complete and accessible")
                        
                except Exception as e:
                    self.result.add_warning("privacy_policy", "Could not validate privacy policy content", str(e))
                
                break
        
        if not found_policy:
            self.result.add_fail("privacy_policy", "Privacy policy not found")

def main():
    """Main function to run security audit"""
    import sys
    
    # Get extension path from command line or use default
    if len(sys.argv) > 1:
        extension_path = sys.argv[1]
    else:
        extension_path = Path(__file__).parent.parent
    
    try:
        auditor = ChromeExtensionSecurityAuditor(extension_path)
        success = auditor.run_full_audit()
        
        # Save results to file
        results_path = Path(__file__).parent / "security_audit_results.json"
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(auditor.result.results, f, indent=2)
        
        print(f"\nResults saved to: {results_path}")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"Security audit failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()