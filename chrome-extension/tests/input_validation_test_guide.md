# Input Validation Manual Testing Guide

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
