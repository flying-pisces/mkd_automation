# Day 1 Test Implementation Plan
## MKD Automation Platform v2.0

**Date:** 2025-08-27  
**Focus:** Foundation setup and basic unit tests  
**Duration:** 8 hours  
**Goal:** Establish test infrastructure and core test framework

---

## Day 1 Objectives

### Primary Goals
1. **Set up test infrastructure** - Configure pytest, Jest, and CI pipeline
2. **Create test directory structure** - Implement the testing architecture
3. **Implement basic unit tests** - Core component testing foundations
4. **Establish testing conventions** - Code quality and standards
5. **Chrome extension test scaffold** - Basic extension testing setup

### Success Criteria
- [ ] Test framework operational with >90% coverage target
- [ ] CI/CD pipeline running tests automatically
- [ ] Basic unit tests for core components passing
- [ ] Chrome extension test environment functional
- [ ] Documentation for testing procedures complete

---

## Hour-by-Hour Implementation Plan

### Hour 1-2: Test Infrastructure Setup

#### Task 1.1: Configure Python Testing Framework
```bash
# Install testing dependencies
pip install pytest pytest-cov pytest-mock pytest-html pytest-benchmark
pip install pytest-timeout pytest-asyncio factory-boy faker responses
pip install freezegun memory-profiler

# Update pyproject.toml with test configuration
```

#### Task 1.2: Configure JavaScript Testing Framework
```bash
# Install Node.js testing dependencies  
npm init -y
npm install --save-dev jest @types/jest ts-jest typescript
npm install --save-dev @testing-library/jest-dom puppeteer
npm install --save-dev chrome-devtools-protocol
```

#### Task 1.3: Set up CI/CD Pipeline
```yaml
# .github/workflows/test.yml - Basic GitHub Actions
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest --cov=src/mkd --cov-report=html --cov-report=xml
```

### Hour 3-4: Test Directory Structure Creation

#### Task 3.1: Create Test Directory Structure
```
tests/
├── __init__.py
├── conftest.py                     # Global test configuration
├── unit/                           # Unit tests (70%)
│   ├── __init__.py
│   ├── chrome_extension/
│   │   ├── __init__.py
│   │   ├── test_messaging.py       # Day 1 Priority
│   │   ├── test_ui_controls.py
│   │   └── test_storage.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── test_session_manager.py # Day 1 Priority  
│   │   ├── test_config_manager.py  # Day 1 Priority
│   │   └── test_message_broker.py  # Day 1 Priority
│   └── platform/
│       ├── __init__.py
│       ├── test_detector.py        # Day 1 Priority
│       └── test_base.py            # Day 1 Priority
├── fixtures/                       # Test data
│   ├── mock_data/
│   ├── sample_configs/
│   └── test_recordings/
└── utils/                          # Test utilities
    ├── __init__.py
    ├── mock_helpers.py
    └── test_helpers.py
```

#### Task 3.2: Create Global Test Configuration
```python
# tests/conftest.py - Global test setup
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture(scope="function")
def temp_dir():
    """Provide temporary directory for each test."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")  
def mock_chrome_api():
    """Mock Chrome extension APIs."""
    with patch('chrome.runtime') as mock_runtime:
        mock_runtime.sendNativeMessage = Mock()
        mock_runtime.onMessage = Mock()
        yield mock_runtime
```

### Hour 5-6: Core Component Unit Tests

#### Task 5.1: Test Session Manager
```python
# tests/unit/core/test_session_manager.py
import pytest
from unittest.mock import Mock, patch
from mkd_v2.core.session_manager import SessionManager
from mkd_v2.core.exceptions import SessionError

class TestSessionManager:
    """Test session management functionality."""
    
    @pytest.fixture
    def session_manager(self, temp_dir):
        """Create session manager instance."""
        return SessionManager(storage_path=temp_dir)
    
    def test_create_session_success(self, session_manager):
        """Test successful session creation."""
        # Arrange
        user_id = "test_user"
        config = {"recording": True, "video": False}
        
        # Act
        session = session_manager.create_session(user_id, config)
        
        # Assert
        assert session.user_id == user_id
        assert session.config == config
        assert session.id is not None
        assert session.created_at is not None
        
    def test_create_session_duplicate_user(self, session_manager):
        """Test session creation with duplicate user."""
        # Arrange
        user_id = "test_user"
        session_manager.create_session(user_id, {})
        
        # Act & Assert
        with pytest.raises(SessionError, match="Session already exists"):
            session_manager.create_session(user_id, {})
            
    def test_get_active_session(self, session_manager):
        """Test retrieving active session."""
        # Arrange
        user_id = "test_user"
        created_session = session_manager.create_session(user_id, {})
        
        # Act
        retrieved_session = session_manager.get_active_session(user_id)
        
        # Assert
        assert retrieved_session.id == created_session.id
        assert retrieved_session.user_id == user_id
        
    def test_end_session(self, session_manager):
        """Test session termination."""
        # Arrange
        user_id = "test_user"
        session = session_manager.create_session(user_id, {})
        
        # Act
        result = session_manager.end_session(user_id)
        
        # Assert
        assert result is True
        assert session_manager.get_active_session(user_id) is None
```

#### Task 5.2: Test Configuration Manager
```python
# tests/unit/core/test_config_manager.py
import pytest
import json
from unittest.mock import Mock, patch, mock_open
from mkd_v2.core.config_manager import ConfigManager
from mkd_v2.core.exceptions import ConfigError

class TestConfigManager:
    """Test configuration management."""
    
    @pytest.fixture
    def config_manager(self, temp_dir):
        """Create config manager instance."""
        return ConfigManager(config_dir=temp_dir)
    
    def test_load_default_config(self, config_manager):
        """Test loading default configuration."""
        # Act
        config = config_manager.get_config()
        
        # Assert
        assert "recording" in config
        assert "playback" in config
        assert "ui" in config
        assert config["recording"]["mouse_sample_rate"] == 60
        
    def test_save_config_success(self, config_manager):
        """Test successful configuration save."""
        # Arrange
        new_config = {
            "recording": {"mouse_sample_rate": 120},
            "playback": {"default_speed": 2.0}
        }
        
        # Act
        result = config_manager.save_config(new_config)
        
        # Assert
        assert result is True
        saved_config = config_manager.get_config()
        assert saved_config["recording"]["mouse_sample_rate"] == 120
        
    def test_validate_config_invalid(self, config_manager):
        """Test configuration validation with invalid data."""
        # Arrange
        invalid_config = {
            "recording": {"mouse_sample_rate": "invalid"}
        }
        
        # Act & Assert
        with pytest.raises(ConfigError, match="Invalid configuration"):
            config_manager.validate_config(invalid_config)
            
    def test_get_config_value(self, config_manager):
        """Test retrieving specific config value."""
        # Act
        sample_rate = config_manager.get_config_value(
            "recording.mouse_sample_rate"
        )
        
        # Assert
        assert sample_rate == 60
        
    def test_set_config_value(self, config_manager):
        """Test setting specific config value."""
        # Act
        config_manager.set_config_value("recording.mouse_sample_rate", 90)
        
        # Assert
        updated_value = config_manager.get_config_value(
            "recording.mouse_sample_rate"
        )
        assert updated_value == 90
```

### Hour 7: Chrome Extension Test Scaffold

#### Task 7.1: Chrome Extension Test Setup
```javascript
// tests/chrome_extension/test_messaging.test.js
import { jest } from '@jest/globals';
import { ChromeMessageBroker } from '../../chrome-extension/src/messaging.js';

// Mock Chrome APIs
global.chrome = {
    runtime: {
        sendNativeMessage: jest.fn(),
        onMessage: {
            addListener: jest.fn(),
            removeListener: jest.fn()
        },
        lastError: null
    }
};

describe('ChromeMessageBroker', () => {
    let messageBroker;
    
    beforeEach(() => {
        messageBroker = new ChromeMessageBroker();
        jest.clearAllMocks();
    });
    
    test('should send native message successfully', async () => {
        // Arrange
        const testMessage = {
            command: 'START_RECORDING',
            params: { video: true }
        };
        
        chrome.runtime.sendNativeMessage.mockImplementation(
            (appName, message, callback) => {
                callback({ status: 'SUCCESS', id: message.id });
            }
        );
        
        // Act
        const response = await messageBroker.sendMessage(testMessage);
        
        // Assert
        expect(chrome.runtime.sendNativeMessage).toHaveBeenCalledWith(
            'com.mkd.automation',
            expect.objectContaining({
                command: 'START_RECORDING',
                params: { video: true }
            }),
            expect.any(Function)
        );
        expect(response.status).toBe('SUCCESS');
    });
    
    test('should handle native message errors', async () => {
        // Arrange
        const testMessage = { command: 'INVALID_COMMAND' };
        chrome.runtime.lastError = { message: 'Native host error' };
        
        chrome.runtime.sendNativeMessage.mockImplementation(
            (appName, message, callback) => {
                callback(null);
            }
        );
        
        // Act & Assert
        await expect(
            messageBroker.sendMessage(testMessage)
        ).rejects.toThrow('Native host error');
    });
});
```

#### Task 7.2: Platform Detection Tests
```python
# tests/unit/platform/test_detector.py
import pytest
from unittest.mock import Mock, patch
from mkd_v2.platform.detector import PlatformDetector
from mkd_v2.platform.windows import WindowsPlatform
from mkd_v2.platform.macos import MacOSPlatform
from mkd_v2.platform.linux import LinuxPlatform

class TestPlatformDetector:
    """Test platform detection functionality."""
    
    def test_detect_windows(self):
        """Test Windows platform detection."""
        # Arrange & Act
        with patch('sys.platform', 'win32'):
            platform = PlatformDetector.detect()
        
        # Assert
        assert isinstance(platform, WindowsPlatform)
        
    def test_detect_macos(self):
        """Test macOS platform detection."""
        # Arrange & Act
        with patch('sys.platform', 'darwin'):
            platform = PlatformDetector.detect()
        
        # Assert
        assert isinstance(platform, MacOSPlatform)
        
    def test_detect_linux(self):
        """Test Linux platform detection."""
        # Arrange & Act
        with patch('sys.platform', 'linux'):
            platform = PlatformDetector.detect()
        
        # Assert
        assert isinstance(platform, LinuxPlatform)
        
    def test_get_platform_capabilities(self):
        """Test platform capability detection."""
        # Arrange
        with patch('sys.platform', 'win32'):
            platform = PlatformDetector.detect()
        
        # Act
        capabilities = platform.get_capabilities()
        
        # Assert
        assert 'input_capture' in capabilities
        assert 'screen_recording' in capabilities
        assert 'ui_automation' in capabilities
        assert capabilities['input_capture'] is True
```

### Hour 8: Documentation and Validation

#### Task 8.1: Create Test Running Scripts
```python
# scripts/run_tests.py
#!/usr/bin/env python3
"""
Test runner script for MKD Automation Platform.
"""
import sys
import subprocess
from pathlib import Path

def run_unit_tests():
    """Run unit tests with coverage."""
    cmd = [
        'python', '-m', 'pytest', 
        'tests/unit/',
        '--cov=src/mkd_v2',
        '--cov-report=html',
        '--cov-report=term-missing',
        '--cov-fail-under=90',
        '-v'
    ]
    return subprocess.run(cmd).returncode

def run_chrome_tests():
    """Run Chrome extension tests."""
    cmd = ['npm', 'test', '--', '--coverage']
    return subprocess.run(cmd).returncode

def main():
    """Run all test suites."""
    print("🧪 Running MKD Automation Test Suite")
    print("=" * 50)
    
    # Run Python unit tests
    print("\n📦 Running Python Unit Tests...")
    python_result = run_unit_tests()
    
    # Run Chrome extension tests
    print("\n🌐 Running Chrome Extension Tests...")
    chrome_result = run_chrome_tests()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Python Tests: {'✅ PASSED' if python_result == 0 else '❌ FAILED'}")
    print(f"Chrome Tests: {'✅ PASSED' if chrome_result == 0 else '❌ FAILED'}")
    
    return python_result + chrome_result

if __name__ == "__main__":
    sys.exit(main())
```

#### Task 8.2: Update Documentation
```markdown
# Testing Quick Start Guide

## Running Tests

### All Tests
```bash
python scripts/run_tests.py
```

### Unit Tests Only
```bash
pytest tests/unit/ --cov=src/mkd_v2 --cov-report=html
```

### Chrome Extension Tests
```bash
npm test
```

### Specific Test File
```bash
pytest tests/unit/core/test_session_manager.py -v
```

## Test Coverage
- Target: >90% unit test coverage
- Current: Run `pytest --cov=src/mkd_v2 --cov-report=term` to check
- HTML Report: `htmlcov/index.html` after running tests

## Writing New Tests
1. Follow naming convention: `test_*.py`
2. Use descriptive test names: `test_should_create_session_when_valid_user`
3. Follow AAA pattern: Arrange, Act, Assert
4. Mock external dependencies
5. Use fixtures for common setup
```

---

## Day 1 Validation Checklist

### Infrastructure ✅
- [ ] pytest configured with coverage >90% target
- [ ] Jest configured for Chrome extension tests
- [ ] CI/CD pipeline running tests on commit
- [ ] Test directory structure created

### Unit Tests ✅
- [ ] `test_session_manager.py` - 5+ test cases
- [ ] `test_config_manager.py` - 5+ test cases  
- [ ] `test_platform_detector.py` - 4+ test cases
- [ ] `test_messaging.js` - Chrome extension messaging tests

### Quality Assurance ✅
- [ ] All Day 1 tests passing
- [ ] Coverage report generated
- [ ] Test documentation complete
- [ ] Testing conventions established

### Next Steps Preview 🔄
- Day 2: Recording engine unit tests
- Day 3: Playback engine unit tests
- Day 4: Integration test foundation
- Week 2: Chrome extension integration tests

---

## Commands Summary

```bash
# Day 1 Test Setup Commands
pip install -r requirements-dev.txt
npm install
python scripts/run_tests.py

# Continuous Testing
pytest --cov=src/mkd_v2 --cov-report=html tests/unit/
npm run test:watch

# Coverage Check
pytest --cov=src/mkd_v2 --cov-report=term-missing
```

This Day 1 plan establishes a solid testing foundation with measurable success criteria and clear next steps for continued development.