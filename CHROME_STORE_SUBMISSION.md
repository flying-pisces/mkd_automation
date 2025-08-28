# Chrome Store Submission Checklist

## Package Information
- **Extension Name**: MKD Automation
- **Version**: 2.0.0
- **Package File**: chrome-extension.zip (29KB)
- **Manifest Version**: 3

## Pre-submission Checklist

### ✅ Required Files
- [x] manifest.json with required fields
- [x] Icons (16x16, 48x48, 128x128) - Note: Replace placeholder icons with actual PNG images
- [x] Service worker (background.js)
- [x] Popup HTML/CSS/JS
- [x] Native messaging integration

### ✅ Permissions
- activeTab (for current tab interaction)
- storage (for saving settings)
- nativeMessaging (for desktop app communication)

### ⚠️ Before Submission
1. **Replace placeholder icons** with actual PNG images:
   - 16x16 icon for toolbar
   - 48x48 icon for extensions page
   - 128x128 icon for store listing

2. **Prepare Store Listing Assets**:
   - Screenshot 1280x800 or 640x400 (minimum 1, maximum 5)
   - Promotional tile 440x280 (optional)
   - Small promotional tile 920x680 (optional)
   - Marquee promotional tile 1400x560 (optional)

3. **Store Listing Information**:
   - Detailed description (up to 1000 characters)
   - Category: Developer Tools or Productivity
   - Language: English
   - Support website/email

## Submission Steps

1. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
2. Sign in with Google account
3. Pay one-time developer registration fee ($5 USD) if not already registered
4. Click "New Item"
5. Upload chrome-extension.zip
6. Fill in store listing details
7. Add screenshots and promotional images
8. Set visibility (Public/Unlisted/Private)
9. Submit for review

## Post-Submission

- Review typically takes 1-3 business days
- Check email for approval/rejection notices
- If rejected, address feedback and resubmit
- Once approved, extension will be available in Chrome Web Store

## Testing Before Submission

Load the extension locally to test:
1. Open Chrome and go to `chrome://extensions/`
2. Enable Developer mode
3. Click "Load unpacked"
4. Select the `chrome-extension` folder
5. Test all functionality

## Important Notes

- The native messaging host must be installed separately on user machines
- Users will need to run the installer script from the main application
- Consider creating an installer or setup guide for the native messaging component