"""
Global test configuration and fixtures for MKD Automation Platform v2.0.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any, Generator


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Provide test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
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
        mock_runtime.lastError = None
        yield mock_runtime


@pytest.fixture(scope="function")
def sample_config() -> Dict[str, Any]:
    """Provide sample configuration for tests."""
    return {
        "recording": {
            "mouse_sample_rate": 60,
            "keyboard_capture": True,
            "screen_events": True,
            "auto_save": False
        },
        "playback": {
            "default_speed": 1.0,
            "error_tolerance": "medium",
            "coordinate_mode": "relative"
        },
        "ui": {
            "theme": "system",
            "always_on_top": False,
            "minimize_to_tray": True
        },
        "security": {
            "encrypt_scripts": True,
            "require_password": False
        }
    }


@pytest.fixture(scope="function")
def sample_user_data() -> Dict[str, Any]:
    """Provide sample user data for authentication tests."""
    return {
        "username": "test_user",
        "password": "test_password_123",
        "role": "editor",
        "created_at": "2025-08-27T10:00:00Z",
        "last_login": "2025-08-27T10:00:00Z"
    }


@pytest.fixture(scope="function")
def mock_platform_detector():
    """Mock platform detector for cross-platform testing."""
    with patch('mkd_v2.platform.detector.PlatformDetector') as mock_detector:
        mock_platform = Mock()
        mock_platform.get_capabilities.return_value = {
            'input_capture': True,
            'screen_recording': True,
            'ui_automation': True
        }
        mock_detector.detect.return_value = mock_platform
        yield mock_detector


@pytest.fixture(scope="function")
def mock_native_messaging():
    """Mock native messaging for Chrome extension tests."""
    class MockPort:
        def __init__(self):
            self.postMessage = Mock()
            self.onMessage = Mock()
            self.onDisconnect = Mock()
            
    with patch('chrome.runtime.connectNative') as mock_connect:
        mock_port = MockPort()
        mock_connect.return_value = mock_port
        yield mock_port


@pytest.fixture(scope="function")
def sample_recording_events():
    """Provide sample recording events for testing."""
    return [
        {
            "timestamp": 1693825200.123,
            "event_type": "MOUSE_CLICK",
            "coordinates": [520, 380],
            "button": "left",
            "target_app": "Chrome",
            "target_window": "GitHub - MKD Automation"
        },
        {
            "timestamp": 1693825201.456,
            "event_type": "KEY_PRESS",
            "key": "ctrl+s",
            "target_app": "Chrome",
            "target_window": "GitHub - MKD Automation"
        },
        {
            "timestamp": 1693825202.789,
            "event_type": "MOUSE_MOVE",
            "coordinates": [600, 400],
            "target_app": "Chrome"
        }
    ]


# Pytest hooks for enhanced test reporting
def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their path."""
    for item in items:
        # Add unit marker to unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to integration tests
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        # Add e2e marker to end-to-end tests
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "chrome_extension: marks tests that require Chrome extension"
    )


# Performance testing helpers
@pytest.fixture(scope="function")
def performance_monitor():
    """Monitor performance metrics during tests."""
    import psutil
    import time
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.start_cpu = None
            self.start_memory = None
            
        def start(self):
            self.start_time = time.time()
            self.start_cpu = psutil.cpu_percent(interval=None)
            self.start_memory = psutil.virtual_memory().used
            
        def stop(self):
            end_time = time.time()
            end_cpu = psutil.cpu_percent(interval=None)
            end_memory = psutil.virtual_memory().used
            
            return {
                'duration': end_time - self.start_time,
                'cpu_usage': end_cpu - self.start_cpu,
                'memory_delta': end_memory - self.start_memory
            }
    
    return PerformanceMonitor()