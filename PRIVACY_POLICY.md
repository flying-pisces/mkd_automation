# Privacy Policy for MKD Automation Chrome Extension

**Effective Date:** August 30, 2025  
**Last Updated:** August 30, 2025

## Overview

MKD Automation ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how our Chrome extension collects, uses, and safeguards your information when you use the MKD Automation browser extension.

## Information We Collect

### Data Collection Types

**1. User Interaction Data (Local Only)**
- Mouse movements, clicks, and coordinates within web pages
- Keyboard inputs and key combinations (excluding passwords)
- Web page elements you interact with (buttons, forms, links)
- Browser tab information (URLs, titles) during recording sessions
- Timestamps of user actions

**2. Configuration Data (Local Storage Only)**
- Extension settings and preferences
- Recording session metadata
- Playback configuration options

### What We DO NOT Collect

- **Personal Information:** We do not collect names, email addresses, phone numbers, or other personal identifiers
- **Passwords:** Password fields are explicitly excluded from recording and marked as [REDACTED]
- **Hidden Form Data:** Hidden form fields are not recorded
- **Sensitive Financial Information:** Credit card numbers, banking information, or similar sensitive data
- **Private Communications:** We do not access private messages, emails, or communication platforms
- **Cross-Site Data:** We only record interactions on the specific pages where recording is active

## How We Use Your Information

**Local Processing Only:**
- All recorded data is processed locally on your device
- Data is used to create automation scripts (.mkd files) stored on your computer
- No data is transmitted to external servers or third parties
- Data is used solely for the purpose of recreating your recorded actions

**Native Messaging:**
- The extension communicates with a local Python application on your computer
- All communication occurs locally through Chrome's native messaging protocol
- No external network connections are made for data processing

## Data Storage and Security

**Local Storage:**
- All extension data is stored locally in your browser's extension storage
- Recording files (.mkd files) are saved to your local file system
- You have complete control over where files are saved

**Security Measures:**
- Input validation and sanitization on all user data
- Content Security Policy (CSP) implementation
- XSS vulnerability prevention
- Secure DOM manipulation practices
- Password field redaction

**Data Retention:**
- You control all data retention - recordings are saved only when you choose
- You can delete recordings at any time from your local file system
- Browser storage can be cleared through browser settings
- No automatic data transmission or cloud storage

## Data Sharing

**We Do Not Share Your Data:**
- No data is transmitted to external servers
- No data is shared with third parties
- No analytics or tracking services are used
- No advertising networks have access to your data
- All processing occurs locally on your device

## Permissions Explained

Our extension requests the following permissions:

**1. activeTab**
- **Purpose:** Access the currently active browser tab to record user interactions
- **Scope:** Only when recording is active and only on the current tab
- **Data:** Page interactions (clicks, inputs, navigation)

**2. storage**
- **Purpose:** Save extension settings and temporary session data locally
- **Scope:** Local browser storage only
- **Data:** User preferences, recording configurations

**3. nativeMessaging**
- **Purpose:** Communicate with the local Python application
- **Scope:** Local computer only, no external network access
- **Data:** Recording commands and session management

## Content Scripts

Our content script runs on web pages to:
- Capture user interactions during recording sessions
- Apply security measures (password field protection)
- Provide real-time feedback during recording
- **Note:** Content script only activates during recording and respects user privacy

## Your Rights and Controls

**Data Control:**
- Start/stop recording at any time
- Choose which pages to record
- Delete recordings from your local storage
- Modify or disable the extension through browser settings

**Transparency:**
- View all recorded data in the extension popup
- Access source code (open-source project)
- Review all recorded actions before saving

**Privacy Settings:**
- Configure which types of interactions to record
- Enable/disable specific recording features
- Control session metadata collection

## Children's Privacy

This extension is not intended for use by children under 13. We do not knowingly collect information from children under 13. If you are a parent or guardian and believe your child has provided information to us, please contact us immediately.

## Changes to This Privacy Policy

We may update this Privacy Policy occasionally. Changes will be reflected by updating the "Last Updated" date. Continued use of the extension after changes constitutes acceptance of the updated policy.

## Compliance

This privacy policy complies with:
- Chrome Web Store Developer Program Policies
- Chrome Extension API requirements
- General privacy best practices
- Applicable data protection regulations

## Technical Implementation

**Security Measures:**
- All user input is validated and sanitized
- XSS prevention through secure DOM manipulation
- Content Security Policy enforcement
- Password field automatic redaction
- Secure native messaging protocol

**Data Minimization:**
- Only necessary interaction data is recorded
- Automatic filtering of sensitive form fields
- Configurable recording scope and granularity
- No unnecessary background data collection

## Contact Information

For questions about this Privacy Policy or our privacy practices:

- **Project:** MKD Automation
- **Repository:** https://github.com/your-org/mkd-automation (if applicable)
- **Issues:** Report privacy concerns through the extension's support channels

## Open Source Commitment

MKD Automation is committed to transparency:
- Source code is available for review
- Privacy practices are implemented in code you can verify
- No hidden data collection or transmission
- Community oversight and contributions welcome

---

**Summary:** MKD Automation respects your privacy by keeping all data local, protecting sensitive information, and giving you complete control over your recordings. We do not collect personal information, transmit data externally, or share information with third parties.