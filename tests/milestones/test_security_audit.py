#!/usr/bin/env python
"""
Security Audit Test - Milestone 1.1.1
Tests for XSS vulnerabilities and security best practices
"""

import os
import re
import json
from pathlib import Path

def test_security_audit():
    """Comprehensive security audit for Chrome extension."""
    results = {
        'innerHTML_usage': [],
        'eval_usage': [],
        'unsafe_patterns': [],
        'csp_violations': [],
        'xss_risks': []
    }
    
    extension_dir = Path(__file__).parent.parent.parent / "chrome-extension"
    
    print("🔍 Running Security Audit...")
    
    # Check for innerHTML usage
    print("  Checking for innerHTML usage...")
    js_files = list(extension_dir.rglob("*.js"))
    for js_file in js_files:
        content = js_file.read_text(encoding='utf-8')
        innerHTML_matches = re.findall(r'\.innerHTML\s*=', content, re.IGNORECASE)
        if innerHTML_matches:
            results['innerHTML_usage'].append({
                'file': str(js_file.relative_to(extension_dir)),
                'count': len(innerHTML_matches),
                'lines': [i+1 for i, line in enumerate(content.split('\n')) 
                         if 'innerHTML' in line]
            })
    
    # Check for eval usage
    print("  Checking for eval usage...")
    for js_file in js_files:
        content = js_file.read_text(encoding='utf-8')
        eval_matches = re.findall(r'\beval\s*\(', content, re.IGNORECASE)
        if eval_matches:
            results['eval_usage'].append({
                'file': str(js_file.relative_to(extension_dir)),
                'count': len(eval_matches)
            })
    
    # Check for unsafe patterns
    print("  Checking for unsafe patterns...")
    unsafe_patterns = [
        r'document\.write\s*\(',
        r'\.outerHTML\s*=',
        r'\.insertAdjacentHTML\s*\(',
        r'setTimeout\s*\(\s*["\']',
        r'setInterval\s*\(\s*["\']'
    ]
    
    for js_file in js_files:
        content = js_file.read_text(encoding='utf-8')
        for pattern in unsafe_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                results['unsafe_patterns'].append({
                    'file': str(js_file.relative_to(extension_dir)),
                    'pattern': pattern,
                    'count': len(matches)
                })
    
    # Check manifest for CSP
    print("  Checking Content Security Policy...")
    manifest_file = extension_dir / "manifest.json"
    if manifest_file.exists():
        manifest = json.loads(manifest_file.read_text())
        if 'content_security_policy' not in manifest:
            results['csp_violations'].append("No CSP defined in manifest")
        else:
            csp = manifest['content_security_policy']
            # Check for unsafe CSP directives
            if "'unsafe-inline'" in csp:
                results['csp_violations'].append("Unsafe inline scripts allowed")
            if "'unsafe-eval'" in csp:
                results['csp_violations'].append("Unsafe eval allowed")
    
    # Generate report
    print("\n📊 Security Audit Results:")
    print("=" * 50)
    
    total_issues = (len(results['innerHTML_usage']) + 
                   len(results['eval_usage']) + 
                   len(results['unsafe_patterns']) + 
                   len(results['csp_violations']) + 
                   len(results['xss_risks']))
    
    if total_issues == 0:
        print("✅ PASS: No security vulnerabilities found")
        return True
    else:
        print(f"❌ FAIL: {total_issues} security issues found")
        
        if results['innerHTML_usage']:
            print(f"\n⚠️  innerHTML Usage ({len(results['innerHTML_usage'])} files):")
            for item in results['innerHTML_usage']:
                print(f"  - {item['file']}: {item['count']} occurrences at lines {item['lines']}")
        
        if results['eval_usage']:
            print(f"\n⚠️  eval() Usage ({len(results['eval_usage'])} files):")
            for item in results['eval_usage']:
                print(f"  - {item['file']}: {item['count']} occurrences")
        
        if results['unsafe_patterns']:
            print(f"\n⚠️  Unsafe Patterns ({len(results['unsafe_patterns'])} findings):")
            for item in results['unsafe_patterns']:
                print(f"  - {item['file']}: {item['pattern']} ({item['count']} times)")
        
        if results['csp_violations']:
            print(f"\n⚠️  CSP Issues:")
            for violation in results['csp_violations']:
                print(f"  - {violation}")
        
        return False

def main():
    """Run security audit test."""
    success = test_security_audit()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())