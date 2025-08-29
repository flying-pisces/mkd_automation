# Chrome Extension Troubleshooting Guide

## Issue: Blank Page After Loading Extension

### Problem Identified
The original popup (`popup.html`) was showing a blank page when the extension was loaded in Chrome. This was likely caused by:

1. **Missing icon reference**: The HTML referenced `icon32.png` which wasn't initially created
2. **Complex JavaScript initialization**: The popup.js file has complex async operations that might fail silently
3. **CSS styling issues**: Potential display problems in the extensive CSS file

### Solution Implemented
Created a simplified popup (`popup-simple.html`) that:
- Uses inline CSS to avoid external file dependencies
- Has minimal JavaScript with error handling
- Includes all necessary icons (16px, 32px, 48px, 128px)
- Uses a simple, clean UI design
- Includes basic recording simulation functionality

### Files Created/Modified

1. **chrome-extension/icons/icon32.png** - Added missing 32x32 icon
2. **chrome-extension/src/popup/popup-simple.html** - Simplified popup with inline styles
3. **manifest.json** - Updated to use simplified popup
4. **chrome-extension.zip** - Updated package ready for Chrome Web Store

### Testing Instructions

1. **Load Extension Locally**:
   ```
   1. Open Chrome and go to chrome://extensions/
   2. Enable "Developer mode" (top right)
   3. Click "Load unpacked"
   4. Select the chrome-extension folder
   ```

2. **Test Functionality**:
   - Extension icon should appear in Chrome toolbar
   - Click icon to open popup - should show MKD Automation interface
   - Click "Start Recording" button - should change to "Stop Recording"
   - Status should update from "Ready" to "Recording"
   - Connection status should update after 1 second

3. **Check Console**:
   - Right-click popup → Inspect → Console tab
   - Should see: "MKD Automation popup loaded" and "MKD Automation initialized successfully"

### Original vs Simplified Popup

| Feature | Original popup.html | Simplified popup-simple.html |
|---------|-------------------|------------------------------|
| File size | Large (complex) | Small (minimal) |
| CSS | External file (404 lines) | Inline styles |
| JavaScript | Complex class-based | Simple functional |
| Dependencies | Multiple files | Self-contained |
| Error handling | Complex async | Basic try-catch |
| UI Elements | Full feature set | Core functionality |

### Next Steps for Production

1. **Replace placeholder icons** with actual PNG images
2. **Test simplified popup** in Chrome to ensure it loads correctly
3. **If working**, gradually add back features from original popup
4. **Maintain error handling** and console logging for debugging

### Alternative Approaches if Issue Persists

1. **Check manifest.json syntax** using Chrome extension validator
2. **Verify file paths** are correct relative to extension root
3. **Test with minimal manifest** (remove optional fields)
4. **Check Chrome developer console** for specific error messages
5. **Test on different Chrome versions** to isolate compatibility issues

---

## Issue: Native Messaging Host "Access Forbidden" Error

### Root Cause
macOS Gatekeeper security blocks unsigned native messaging hosts from being executed by Chrome.

### Symptoms
- Chrome extension shows: "Native host disconnected: Access to the specified native messaging host is forbidden"
- Chrome DevTools shows: "Failed to get status: Error: Native messaging error: Attempting to use a disconnected port object"
- Native host works when tested manually but fails when Chrome tries to execute it
- No logs are generated in ~/.mkd/ directory when extension is used

### Solution Requirements
The macOS security setting "Allow applications from" must be set to allow unsigned applications:
- System Settings > Privacy & Security > Security > "Allow applications from" 
- Must be set to "App Store and identified developers" or "Anywhere"

### Known Blockers
- **Corporate/MDM Managed Devices**: If you see "This setting has been configured by a profile" in System Settings > Privacy & Security, you cannot change this setting and will need to use a different device for development.
- **Gatekeeper Restrictions**: Unsigned scripts and binaries are blocked by default on macOS

### Verification Steps
1. Check if settings are managed: System Settings > Privacy & Security > Security
2. Test native host manually: 
   ```bash
   python3 -c "import sys,json,struct; msg={'id':1,'command':'GET_STATUS'}; data=json.dumps(msg).encode(); sys.stdout.buffer.write(struct.pack('=I', len(data)) + data)" | ./bin/mkd_native_host
   ```
3. Check Gatekeeper status: `spctl --status`
4. Check if files are blocked: `spctl --assess --verbose /path/to/native/host`

### Debugging Process Used
1. Verified extension ID matches native messaging manifest (✓)
2. Fixed response format mismatch in background.js (✓) 
3. Created simple test host to isolate the issue (✓)
4. Test host worked manually but not through Chrome
5. Discovered Gatekeeper was blocking execution

### Workarounds for Development
1. **Use a non-managed macOS device** (recommended)
2. Request IT department to allow specific development paths
3. Use code signing (requires Apple Developer account)
4. Temporarily disable Gatekeeper (if possible): `sudo spctl --master-disable`

### Prevention
A pre-flight check script should be added to verify system compatibility before development.

---

*Created: August 28, 2025 - Issue Resolution*
*Updated: August 28, 2025 - Added Native Messaging Troubleshooting*