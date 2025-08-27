"""
Day 1 Infrastructure Test - Basic validation of test setup.
This test validates that our testing infrastructure is working correctly.
"""

import pytest
import json
import tempfile
from pathlib import Path


class TestDay1Infrastructure:
    """Test Day 1 test infrastructure setup."""
    
    def test_pytest_fixtures_available(self, temp_dir, sample_config):
        """Test that pytest fixtures are working."""
        # Test temp_dir fixture
        assert temp_dir.exists()
        assert temp_dir.is_dir()
        
        # Test sample_config fixture
        assert isinstance(sample_config, dict)
        assert "recording" in sample_config
        assert "playback" in sample_config
        
    def test_mock_chrome_api(self, mock_chrome_api):
        """Test that Chrome API mocking is working."""
        # Test that chrome runtime mock exists
        assert mock_chrome_api.sendNativeMessage is not None
        assert mock_chrome_api.onMessage is not None
        
        # Test that mocks are callable
        mock_chrome_api.sendNativeMessage("test", {}, lambda x: x)
        assert mock_chrome_api.sendNativeMessage.called
        
    def test_sample_recording_events(self, sample_recording_events):
        """Test that sample recording events fixture works."""
        assert isinstance(sample_recording_events, list)
        assert len(sample_recording_events) > 0
        
        # Validate event structure
        first_event = sample_recording_events[0]
        assert "timestamp" in first_event
        assert "event_type" in first_event
        assert "coordinates" in first_event
        
    def test_performance_monitor(self, performance_monitor):
        """Test that performance monitoring fixture works."""
        import time
        
        # Start monitoring
        performance_monitor.start()
        
        # Do some work
        time.sleep(0.01)
        
        # Stop monitoring and get metrics
        metrics = performance_monitor.stop()
        
        assert "duration" in metrics
        assert metrics["duration"] > 0
        assert "cpu_usage" in metrics
        assert "memory_delta" in metrics
        
    def test_json_serialization(self, sample_config):
        """Test JSON serialization of config data."""
        # Serialize to JSON
        json_str = json.dumps(sample_config)
        
        # Deserialize back
        config_copy = json.loads(json_str)
        
        # Verify they're identical
        assert config_copy == sample_config
        
    def test_file_operations(self, temp_dir):
        """Test file operations in temporary directory."""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_content = "Hello, Day 1 testing!"
        
        # Write to file
        test_file.write_text(test_content)
        
        # Read from file
        read_content = test_file.read_text()
        
        # Verify
        assert read_content == test_content
        assert test_file.exists()
        
    def test_exception_handling(self):
        """Test that exception handling works correctly."""
        with pytest.raises(ValueError, match="Test error"):
            raise ValueError("Test error")
            
        with pytest.raises(KeyError):
            {}["nonexistent_key"]
            
    def test_parametrized_test(self):
        """Test parametrized testing capability."""
        test_data = [
            ("input1", "expected1"),
            ("input2", "expected2"),
            ("input3", "expected3")
        ]
        
        for input_val, expected in test_data:
            # Simple transformation test
            result = f"processed_{input_val}"
            assert result == f"processed_{expected.replace('expected', 'input')}"
            
    def test_mock_functionality(self):
        """Test basic mocking functionality."""
        from unittest.mock import Mock, patch
        
        # Create a mock
        mock_obj = Mock()
        mock_obj.method.return_value = "mocked_result"
        
        # Test mock
        result = mock_obj.method("test_arg")
        assert result == "mocked_result"
        assert mock_obj.method.called
        assert mock_obj.method.call_args[0][0] == "test_arg"
        
        # Test patching
        with patch('builtins.len') as mock_len:
            mock_len.return_value = 42
            assert len([1, 2, 3]) == 42
            
    def test_async_capability(self):
        """Test that async functionality can be tested."""
        import asyncio
        
        async def async_function():
            await asyncio.sleep(0.001)
            return "async_result"
        
        # Run async function in test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(async_function())
            assert result == "async_result"
        finally:
            loop.close()


class TestDay1TestValidation:
    """Validate Day 1 specific testing requirements."""
    
    def test_day1_documentation_exists(self):
        """Test that Day 1 documentation files exist."""
        project_root = Path(__file__).parent.parent.parent
        
        required_docs = [
            "docs/DAY1_TEST_PLAN.md",
            "docs/TEST_DEVELOPMENT_PLAN.md",
            "docs/ERS.md",
            "docs/ARCHITECTURE_V2.md"
        ]
        
        for doc_path in required_docs:
            doc_file = project_root / doc_path
            assert doc_file.exists(), f"Required documentation missing: {doc_path}"
            
            # Check that file has content
            content = doc_file.read_text()
            assert len(content) > 100, f"Documentation seems too short: {doc_path}"
            
    def test_test_structure_exists(self):
        """Test that test directory structure is correctly set up."""
        project_root = Path(__file__).parent.parent.parent
        tests_root = project_root / "tests"
        
        required_dirs = [
            "unit",
            "unit/chrome_extension", 
            "unit/core",
            "unit/platform",
            "fixtures"
        ]
        
        for dir_path in required_dirs:
            test_dir = tests_root / dir_path
            assert test_dir.exists(), f"Required test directory missing: {dir_path}"
            assert test_dir.is_dir(), f"Path should be directory: {dir_path}"
            
    def test_config_files_exist(self):
        """Test that configuration files exist."""
        project_root = Path(__file__).parent.parent.parent
        
        config_files = [
            "pyproject.toml",
            "package.json",
            "tests/conftest.py",
            "tests/chrome_extension/setup.js"
        ]
        
        for config_file in config_files:
            config_path = project_root / config_file
            assert config_path.exists(), f"Required config file missing: {config_file}"
            
    def test_day1_test_files_exist(self):
        """Test that Day 1 priority test files exist."""
        project_root = Path(__file__).parent.parent.parent
        tests_root = project_root / "tests"
        
        day1_tests = [
            "unit/chrome_extension/test_messaging.py",
            "unit/chrome_extension/test_ui_controls.test.js",
            "unit/core/test_message_broker.py",
            "unit/platform/test_detector.py"
        ]
        
        for test_file in day1_tests:
            test_path = tests_root / test_file
            assert test_path.exists(), f"Day 1 test file missing: {test_file}"
            
            # Check that test has content
            content = test_path.read_text()
            assert "test_" in content, f"File doesn't seem to contain tests: {test_file}"
            
    def test_test_runner_exists(self):
        """Test that Day 1 test runner script exists."""
        project_root = Path(__file__).parent.parent.parent
        
        runner_script = project_root / "scripts/run_day1_tests.py"
        assert runner_script.exists(), "Day 1 test runner script missing"
        
        # Check that it's executable
        content = runner_script.read_text()
        assert "Day1TestRunner" in content
        assert "def main()" in content