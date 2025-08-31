#!/usr/bin/env python3
"""
Input Validation Test Suite
Tests all input validation and sanitization mechanisms
"""

import sys
import json
from pathlib import Path

def test_malicious_inputs():
    """
    Test various malicious input scenarios that the extension should handle
    """
    print("Testing Input Validation - Malicious Input Scenarios")
    print("="*60)
    
    # Test cases for XSS attempts
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>",
        "';alert(String.fromCharCode(88,83,83))//",
        "<svg/onload=alert('XSS')>",
        "&#60;script&#62;alert('XSS')&#60;/script&#62;",
        "<iframe src='javascript:alert(`XSS`)'></iframe>",
    ]
    
    # Test cases for injection attempts
    injection_payloads = [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "../../../etc/passwd",
        "cmd.exe /c dir",
        "powershell.exe -Command Get-Process",
        "__proto__",
        "constructor",
    ]
    
    # Test cases for oversized inputs
    oversized_inputs = [
        "A" * 10000,  # Very long string
        "X" * 100000, # Extremely long string
        "\n" * 5000,  # Many newlines
    ]
    
    test_results = []
    
    print(f"XSS Payloads to test: {len(xss_payloads)}")
    for payload in xss_payloads:
        result = {
            'type': 'XSS',
            'payload': payload,
            'should_block': True,
            'description': 'XSS attempt should be sanitized or blocked'
        }
        test_results.append(result)
        print(f"  - {payload[:50]}{'...' if len(payload) > 50 else ''}")
    
    print(f"\nInjection Payloads to test: {len(injection_payloads)}")
    for payload in injection_payloads:
        result = {
            'type': 'Injection',
            'payload': payload,
            'should_block': True,
            'description': 'Injection attempt should be sanitized or blocked'
        }
        test_results.append(result)
        print(f"  - {payload}")
    
    print(f"\nOversized Input tests: {len(oversized_inputs)}")
    for i, payload in enumerate(oversized_inputs):
        result = {
            'type': 'Oversized',
            'payload': f"Large input #{i+1} ({len(payload)} chars)",
            'actual_size': len(payload),
            'should_block': True,
            'description': 'Oversized input should be truncated or rejected'
        }
        test_results.append(result)
        print(f"  - Large input #{i+1}: {len(payload)} characters")
    
    # Save test cases to file for manual testing
    test_file = Path(__file__).parent / "malicious_input_test_cases.json"
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n[INFO] Test cases saved to: {test_file}")
    print(f"[INFO] Use these test cases to manually verify input validation")
    print(f"[INFO] Total test cases: {len(test_results)}")
    
    return test_results

def generate_validation_test_guide():
    """Generate manual testing guide for input validation"""
    
    guide_content = """# Input Validation Manual Testing Guide

## Overview
This guide provides step-by-step instructions for manually testing input validation in the MKD Automation Chrome extension.

## Test Scenarios

### 1. XSS Prevention Testing

**Objective**: Verify that the extension properly sanitizes or blocks XSS attempts.

**Test Steps**:
1. Open the extension popup
2. Try to input XSS payloads in any text fields
3. Verify that dangerous scripts are sanitized or blocked
4. Check browser console for any XSS execution

**Expected Results**:
- No JavaScript execution from user input
- Dangerous HTML tags are stripped or escaped
- No script injection through DOM manipulation

### 2. Message Validation Testing

**Objective**: Test that inter-component messages are properly validated.

**Test Steps**:
1. Open browser developer tools
2. Go to extension's background page
3. Try sending malformed messages via console:
   ```javascript
   chrome.runtime.sendMessage({
     type: "<script>alert('xss')</script>",
     config: { malicious: true }
   });
   ```
4. Verify that invalid messages are rejected

**Expected Results**:
- Invalid message types are rejected
- Malformed message structures are blocked
- Security errors are logged appropriately

### 3. Native Messaging Security

**Objective**: Ensure native messaging parameters are validated.

**Test Steps**:
1. Start recording through extension
2. Monitor native messaging traffic
3. Verify that all parameters are validated before sending
4. Test with invalid parameter types

**Expected Results**:
- Invalid parameters are rejected before sending
- Type validation is enforced
- Dangerous values are sanitized

### 4. Content Script Security

**Objective**: Test content script input handling.

**Test Steps**:
1. Navigate to a test page
2. Start recording
3. Interact with page elements containing XSS payloads
4. Verify that recorded data is sanitized

**Expected Results**:
- Page interactions are recorded safely
- XSS payloads in page content are sanitized
- Password fields are properly redacted

## Automated Testing

Run the security audit script:
```bash
python chrome-extension/tests/security_audit.py
```

## Manual Verification Checklist

- [ ] XSS payloads are blocked or sanitized
- [ ] Message validation prevents malformed requests
- [ ] Parameter validation works for native messaging
- [ ] Content script sanitizes recorded data
- [ ] Password fields are redacted
- [ ] Oversized inputs are handled properly
- [ ] No dangerous innerHTML usage
- [ ] CSP prevents inline scripts
- [ ] All user inputs are validated

## Reporting Issues

If any test fails:
1. Document the specific payload that caused the failure
2. Note the expected vs actual behavior
3. Include browser console errors
4. Report through the project's issue tracking system

## Security Best Practices Verified

- Input sanitization at all entry points
- Output encoding for displayed content
- CSP implementation and compliance
- Permission minimization
- Secure message passing
- Password field protection
"""

    guide_file = Path(__file__).parent / "input_validation_test_guide.md"
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"[INFO] Manual testing guide created: {guide_file}")

def main():
    """Main function"""
    print("MKD Automation - Input Validation Testing")
    print("="*50)
    
    # Generate malicious input test cases
    test_cases = test_malicious_inputs()
    
    # Generate manual testing guide
    generate_validation_test_guide()
    
    print(f"\n[OK] Input validation test suite prepared")
    print(f"[INFO] Generated {len(test_cases)} test cases for validation")
    print(f"[INFO] Run security_audit.py for automated validation")

if __name__ == "__main__":
    main()