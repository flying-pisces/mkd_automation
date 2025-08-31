# MKD Automation - Testing Guide
## Complete Testing Infrastructure for Chrome Web Store Development

This guide provides comprehensive testing procedures for the 3-week development plan to achieve Chrome Web Store readiness.

---

## 🚀 Quick Start Testing

### Daily Health Check
```bash
# Run daily health monitoring (recommended every day during development)
python scripts/daily_health_check.py
```

### Weekly Milestone Validation
```bash
# Validate specific week completion
python scripts/milestone_validator.py --week 1   # Week 1 milestones
python scripts/milestone_validator.py --week 2   # Week 2 milestones  
python scripts/milestone_validator.py --week 3   # Week 3 milestones

# Validate all milestones (final check before submission)
python scripts/milestone_validator.py --all
```

---

## 📋 Testing Structure

### Test Categories

#### 1. Security Tests (`tests/milestones/`)
- **`test_security_audit.py`** - XSS vulnerabilities, innerHTML usage, eval detection
- **`validate_csp.py`** - Content Security Policy compliance
- **`run_security_audit.py`** - Complete penetration testing

#### 2. Store Compliance Tests
- **`validate_icons.py`** - Icon sizes, formats, file integrity
- **`validate_store_assets.py`** - Screenshots, promotional images
- **`test_privacy_policy.py`** - Privacy policy accessibility
- **`test_store_compliance.py`** - Chrome Web Store policy adherence

#### 3. Integration Tests
- **`test_native_host_windows.py`** - Windows native messaging
- **`test_registry_integration.py`** - Windows registry entries
- **`test_message_protocol.py`** - Chrome-Python communication
- **`test_recording_integration.py`** - End-to-end recording workflow

#### 4. Cross-Platform Tests
- **`test_cross_browser.py`** - Chrome, Edge, Brave compatibility
- **`test_cross_platform_install.py`** - Windows, Mac, Linux installation

#### 5. Performance Tests
- **`test_performance.py`** - Memory, CPU, startup time benchmarks
- **`test_production_build.py`** - Production package validation

---

## 📊 Current Status Baseline

### Health Check Results (August 30, 2025)
```
[SCORE] Overall Health: 3/5 (60.0%)
[FAIR] FAIR HEALTH - Address issues soon

✅ Working:
- Extension Structure (6/6 files)
- Manifest V3 Validity
- Python Backend Functionality

❌ Needs Fixing:
- Critical Security (innerHTML usage in popup.js)
- File Integrity (placeholder icons)
```

### Deployment Readiness Score
- **Current**: 3/10
- **Target**: 10/10
- **Gap**: 7 points improvement needed

---

## 🎯 Weekly Testing Schedule

### Week 1: Security & Compliance Testing
**Daily Tests:**
```bash
python tests/milestones/test_security_audit.py      # Should show 0 vulnerabilities
python tests/milestones/validate_icons.py          # Should validate all icon sizes
python scripts/daily_health_check.py               # Should achieve >80% health
```

**Milestone Gates:**
- Day 2: Security audit must pass 100%
- Day 3: All store assets must validate
- Day 4: Privacy policy must be accessible
- Day 5: Store compliance must be 100%

### Week 2: Integration Testing  
**Daily Tests:**
```bash
python tests/milestones/test_native_host_windows.py  # Windows messaging works
python tests/milestones/test_message_protocol.py     # All 8 message types succeed
python tests/milestones/test_recording_integration.py # Chrome → Python → .mkd
```

**Milestone Gates:**
- Day 8: Native host works on Windows
- Day 10: Full Chrome-Python integration
- Day 11: Content script captures page events

### Week 3: Production Testing
**Daily Tests:**
```bash
python tests/milestones/run_e2e_tests.py            # 100% E2E coverage
python tests/milestones/test_performance.py         # <50MB RAM, <5% CPU
python tests/milestones/test_production_build.py    # <2MB package size
```

**Final Gate:**
- Day 18: All tests must pass before submission
- Day 21: Chrome Web Store package ready

---

## 🧪 Test Execution Examples

### Security Audit Example
```bash
$ python tests/milestones/test_security_audit.py

🔍 Running Security Audit...
  Checking for innerHTML usage...
  Checking for eval usage...
  Checking for unsafe patterns...
  Checking Content Security Policy...

📊 Security Audit Results:
==================================================
✅ PASS: No security vulnerabilities found
```

### Icon Validation Example
```bash
$ python tests/milestones/validate_icons.py

🎨 Validating Chrome Extension Icons...
  Manifest references: ['16', '48', '128']
  Checking recommended icons...
  ✅ Found recommended icon32.png
  Checking HTML icon references...

📊 Icon Validation Results:
========================================
✅ PASS: All icons are valid and properly sized
  Valid icons: 16px (2KB), 32px (1KB), 48px (3KB), 128px (8KB)
```

### Native Host Testing Example
```bash
$ python tests/milestones/test_native_host_windows.py

🖥️  Testing Windows Native Host...
  1. Checking for Windows native host executable...
  ✅ Found native host: bin/mkd_native_host.exe
  2. Checking for hardcoded paths...
  ✅ No hardcoded paths found
  3. Testing native host startup...
    Host process started...
  4. Testing ping message...
    Ping message sent...
    ✅ Ping response received

📊 Windows Native Host Test Results:
=============================================
✅ PASS: All Windows native host tests passed
  Executable: mkd_native_host.exe
  Tests passed: 5/5
```

---

## 📈 Success Metrics

### Week 1 Success Criteria
- [ ] Security audit: 0 vulnerabilities found
- [ ] Icons: All sizes present and valid
- [ ] Privacy policy: Hosted and accessible  
- [ ] Store compliance: 100% policy adherent
- [ ] Health score: ≥80%

### Week 2 Success Criteria
- [ ] Native messaging: Works on Windows/Mac/Linux
- [ ] Message protocol: All 8 message types succeed
- [ ] Integration: Chrome button → Python recording → .mkd file
- [ ] Error handling: Graceful failure in all scenarios
- [ ] Health score: ≥90%

### Week 3 Success Criteria
- [ ] E2E tests: 100% automation coverage
- [ ] Performance: <50MB RAM, <5% CPU, <2s startup
- [ ] Cross-browser: Works on Chrome/Edge/Brave  
- [ ] Production build: <2MB package, no debug artifacts
- [ ] Health score: 100%

---

## 🔧 Troubleshooting Tests

### Common Test Failures

#### Security Audit Fails
```bash
# Fix innerHTML usage
# Replace in popup.js:
element.innerHTML = content;
# With:
element.textContent = content;
```

#### Icon Validation Fails
```bash
# Create proper icons using design tool
# Required sizes: 16px, 32px, 48px, 128px, 512px
# Format: PNG, <50KB each
```

#### Native Host Fails
```bash
# Check Python path in native host script
# Remove hardcoded paths like /Users/cyin/
# Use relative paths: python -m mkd_v2.native_host.host
```

### Test Environment Setup
```bash
# Install test dependencies
pip install Pillow pytest selenium

# Set environment variables
export MKD_TEST_MODE=1
export CHROME_BINARY_PATH=/path/to/chrome

# Run specific test categories
python -m pytest tests/unit/ -v           # Unit tests
python -m pytest tests/integration/ -v   # Integration tests  
python -m pytest tests/e2e/ -v          # End-to-end tests
```

---

## 📋 Pre-Submission Checklist

Before Chrome Web Store submission, verify:

```bash
# Final validation checklist
python scripts/milestone_validator.py --all
```

**Must Pass:**
- [ ] Security audit: 0 vulnerabilities
- [ ] All icons: Valid sizes and formats
- [ ] Privacy policy: Publicly accessible
- [ ] Native messaging: Works cross-platform
- [ ] E2E workflow: Chrome → Python → .mkd file
- [ ] Performance: Meets all benchmarks
- [ ] Store compliance: 100% policy adherent

**Success Indicator:**
```
🎉 ALL MILESTONES COMPLETED!
   Extension is ready for Chrome Web Store submission
```

This comprehensive testing framework ensures systematic validation of every development milestone and provides confidence for successful Chrome Web Store submission.