# Chrome Web Store Upload Checklist

## Pre-Upload Validation ✅

- [x] **Manifest Validation** - All required fields present and valid
- [x] **Version Format** - Follows Chrome's version numbering (2.0.0)
- [x] **Permissions** - Only necessary permissions requested
- [x] **Icons** - All required sizes present (16x16, 48x48, 128x128)
- [x] **Content Security Policy** - No unsafe-inline or unsafe-eval
- [x] **File Structure** - Clean, no unnecessary files
- [x] **Package Size** - 0.02MB (well under 100MB limit)
- [x] **Code Quality** - No console.log or debug code in production
- [x] **ZIP Package** - Created at `dist/mkd-automation-2.0.0.zip`

## Required Store Assets

### Screenshots (1-5 required) ⚠️
- [ ] **Screenshot 1** - Main popup interface (1280x800)
- [ ] **Screenshot 2** - Recording in progress (1280x800)  
- [ ] **Screenshot 3** - Browser integration (1280x800)
- [ ] **Screenshot 4** - Settings panel (1280x800)
- [ ] **Screenshot 5** - Success completion (1280x800)

### Promotional Images ⚠️
- [ ] **Small Tile** - 440x280 pixels (`promo_small.png`)
- [ ] **Large Tile** - 920x680 pixels (`promo_large.png`)
- [ ] **Marquee** - 1400x560 pixels (`promo_marquee.png`)

### Store Listing Content ✅
- [x] **Extension Name** - "MKD Automation"
- [x] **Short Description** - Under 132 characters
- [x] **Detailed Description** - Comprehensive feature overview
- [x] **Category** - Developer Tools
- [x] **Language** - English (US)

## Upload Process

### 1. Developer Console Setup
1. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/developer/dashboard)
2. Sign in with Google account
3. Pay one-time $5 registration fee (if not already paid)

### 2. Upload Extension
1. Click "Add new item"
2. Upload `dist/mkd-automation-2.0.0.zip`
3. Wait for automatic review of package

### 3. Store Listing
1. **Product Details**
   - Name: "MKD Automation"
   - Summary: "Record and replay browser interactions for automation testing"
   - Description: (Use content from `store_listing.md`)
   - Category: Developer Tools
   - Language: English (US)

2. **Privacy Practices** 
   - Data usage: Select "Does not collect user data"
   - Permissions: Justify activeTab and nativeMessaging usage

3. **Store Assets**
   - Upload 1-5 screenshots
   - Upload promotional images
   - Add 128x128 icon (already in manifest)

### 4. Distribution
1. **Visibility**: Public (recommended) or Unlisted
2. **Regions**: Worldwide (default)
3. **Pricing**: Free

### 5. Review & Publish
1. Review all information
2. Click "Submit for review"
3. Wait for Google review (typically 1-3 business days)
4. Address any review feedback if required

## Post-Upload

### If Approved ✅
- Extension goes live on Chrome Web Store
- Users can install via store link
- Analytics available in developer dashboard

### If Rejected ❌  
- Review rejection reasons
- Fix identified issues
- Update package and resubmit
- Common issues: permissions, functionality, metadata

## Justification for Permissions

### activeTab
- **Purpose**: Record user interactions on the current webpage
- **Justification**: Core functionality requires capturing click, input, and navigation events
- **User Benefit**: Enables automation recording without requiring broad site access

### nativeMessaging
- **Purpose**: Connect to local MKD desktop application  
- **Justification**: Required for saving recordings and enabling playback functionality
- **User Benefit**: Seamless integration between browser and desktop automation tools

### storage
- **Purpose**: Save user preferences and recording settings
- **Justification**: Persist user configuration between browser sessions
- **User Benefit**: Maintains user customizations and improves experience

## Marketing Copy Templates

### Short Description (132 chars max)
"Record and replay browser interactions for automation testing. Capture clicks, typing, and navigation with precision."

### One-Liner for Social Media
"Automate your web workflows with one-click recording and precision playback! 🚀 #WebAutomation #QA #Testing"

### Key Value Props
- ⏱️ Save time on repetitive web tasks
- 🎯 Pixel-perfect automation recording  
- 🔒 100% local processing - your data never leaves your device
- 🔧 Perfect for QA testing and workflow automation
- 💻 Works across Windows, Mac, and Linux

## Support Resources

- **Website**: https://github.com/flying-pisces/mkd_automation
- **Support Email**: Create dedicated support email
- **Documentation**: GitHub wiki with setup guides
- **Video Demo**: Consider creating demo video for store listing