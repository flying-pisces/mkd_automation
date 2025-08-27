# Week 2 Validation & Testing Suite

Comprehensive validation system for MKD Automation Platform v2.0 Week 2 features.

## 🚀 Quick Start

### Run All Tests
```bash
# From project root
python validate_week2.py

# Or run directly
python tests/week2_validation/run_all_tests.py
```

### Run Specific Test Suite
```bash
# Individual test modules
python tests/week2_validation/test_chrome_integration.py
python tests/week2_validation/test_input_capture.py
python tests/week2_validation/test_visual_overlays.py
python tests/week2_validation/test_ui_automation.py
python tests/week2_validation/test_playback_engine.py
```

### Demo Features
```bash
# Quick feature demonstration
python demo_week2_features.py
```

## 📋 Test Suites Overview

### 1. Chrome Integration Tests (`test_chrome_integration.py`)
Tests Chrome extension and native messaging functionality:
- ✅ Extension manifest validation
- ✅ Native host installation and registration
- ✅ Background script compatibility
- ✅ Cross-browser support (Chrome/Chromium)

**Expected Results:**
- Native messaging host should be installed
- Extension manifest should be valid Manifest V3
- Background scripts should load without errors

### 2. Input Capture Tests (`test_input_capture.py`) 
Tests real input capture implementation:
- ✅ Platform detection and initialization
- ✅ pynput integration and permissions
- ✅ Mouse and keyboard event capture
- ✅ Event format standardization

**Expected Results:**
- Platform should initialize successfully
- Input capture may require permissions on macOS
- Events should be captured in standardized format

### 3. Visual Overlay Tests (`test_visual_overlays.py`)
Tests cross-platform overlay rendering:
- ✅ Overlay renderer creation (tkinter/Cocoa)
- ✅ Multiple overlay management
- ✅ Overlay updates and styling
- ✅ Performance and cleanup

**Expected Results:**
- Overlays should render visibly on screen
- Multiple overlays can be managed simultaneously
- Updates and cleanup should work properly

### 4. UI Automation Tests (`test_ui_automation.py`)
Tests intelligent UI automation system:
- ✅ Window management and detection
- ✅ Element detection (computer vision/OCR)
- ✅ Context-aware interactions
- ✅ Automation engine orchestration

**Expected Results:**
- Should detect system windows
- Basic automation actions should execute
- Element detection may require OpenCV/Tesseract

### 5. Playback Engine Tests (`test_playback_engine.py`)
Tests playback system foundation:
- ✅ Sequence validation and processing
- ✅ Action execution pipeline
- ✅ Speed control and timing
- ✅ Error handling and recovery

**Expected Results:**
- Action sequences should validate properly
- Individual actions should execute successfully
- Speed control and error handling should work

## 📊 Test Results & Logging

### Log Directory Structure
```
tests/week2_validation/logs/
├── chrome_integration.log          # Chrome integration test logs
├── chrome_integration_report.json  # Detailed Chrome test results
├── input_capture.log               # Input capture test logs
├── input_capture_report.json       # Input capture results
├── visual_overlays.log             # Visual overlay test logs
├── visual_overlays_report.json     # Overlay test results
├── ui_automation.log               # UI automation test logs
├── ui_automation_report.json       # Automation test results
├── playback_engine.log             # Playback engine test logs
├── playback_engine_report.json     # Playback test results
├── master_test_runner.log          # Overall test execution logs
├── week2_latest_report.json        # Latest consolidated report
└── week2_consolidated_report_*.json # Timestamped reports
```

### Reading Test Results

**Quick Status Check:**
```bash
# Check latest results
cat tests/week2_validation/logs/week2_latest_report.json | jq '.summary'
```

**Detailed Analysis:**
```bash
# View specific test suite results
cat tests/week2_validation/logs/chrome_integration_report.json | jq '.summary'
```

## 🔧 Troubleshooting Common Issues

### Chrome Integration Issues
```bash
# Issue: Native host not installed
# Solution: Run installer
python install_native_host.py

# Issue: Extension load errors  
# Solution: Check manifest.json and restart Chrome
```

### Input Capture Issues
```bash
# Issue: Permission denied on macOS
# Solution: Grant Accessibility permissions
# System Preferences → Security & Privacy → Accessibility

# Issue: pynput not available
# Solution: Install dependency
pip install pynput
```

### Visual Overlay Issues
```bash
# Issue: No GUI/display access
# Solution: Ensure GUI environment (not SSH without X11)

# Issue: tkinter not available
# Solution: Install tkinter
# macOS: Already included
# Linux: apt-get install python3-tk
```

### UI Automation Issues
```bash
# Issue: Poor element detection
# Solution: Install optional dependencies
pip install opencv-python pytesseract

# Issue: Window management fails
# Solution: Check platform-specific permissions
```

### Playback Engine Issues
```bash
# Issue: Action execution fails
# Solution: Check system permissions and platform initialization

# Issue: Sequence validation errors
# Solution: Review action format and required fields
```

## 📈 Success Criteria

### Minimum Passing Thresholds:
- **Chrome Integration:** 80% pass rate
- **Input Capture:** 70% pass rate (permissions may fail)
- **Visual Overlays:** 75% pass rate 
- **UI Automation:** 70% pass rate (dependencies optional)
- **Playback Engine:** 75% pass rate

### Overall Week 2 Success:
- Suite success rate ≥ 80%
- Individual test success rate ≥ 70%
- No critical failures in core functionality

## 🚨 Known Issues & Limitations

### Expected Warnings:
- `Tesseract not available - OCR disabled` (optional feature)
- `Failed to create window info` (platform-specific window APIs)
- Permission prompts on macOS for Accessibility/Input Monitoring

### Acceptable Failures:
- OCR-based element detection (requires tesseract)
- Advanced window management (platform-specific APIs)
- Visual overlays in headless environments

### Critical Failures (Fix Required):
- Chrome extension manifest validation
- Native messaging host installation
- Basic input capture initialization
- Core automation engine functionality

## 🔄 Continuous Validation

### Development Workflow:
1. Make changes to Week 2 code
2. Run relevant test suite: `python tests/week2_validation/test_*.py`
3. Fix any failures
4. Run full validation: `python validate_week2.py`
5. Check consolidated report for overall status

### CI/CD Integration:
```bash
# Automated testing (headless mode)
python validate_week2.py --skip-visual --quick

# Full validation with GUI
python validate_week2.py
```

## 📞 Support

### Getting Help:
1. Check test logs in `tests/week2_validation/logs/`
2. Review error messages and recommendations
3. Run individual test suites for detailed debugging
4. Use `--debug` flag for verbose output

### Reporting Issues:
Include in bug reports:
- Test execution logs
- System information (OS, Python version)
- Consolidated test report JSON
- Steps to reproduce

---

**✨ Week 2 validation ensures all real implementations are working correctly before proceeding to Week 3 advanced features.**