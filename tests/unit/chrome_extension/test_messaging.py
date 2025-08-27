"""
Unit tests for Chrome extension native messaging functionality.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
import time


class TestNativeMessaging:
    """Test Chrome extension native messaging protocol."""
    
    @pytest.fixture
    def mock_chrome_runtime(self):
        """Mock Chrome runtime API."""
        mock_runtime = Mock()
        mock_runtime.sendNativeMessage = Mock()
        mock_runtime.onMessage = Mock()
        mock_runtime.lastError = None
        return mock_runtime
    
    def test_message_serialization_valid(self):
        """Test valid message format serialization."""
        # Arrange
        message_data = {
            "command": "START_RECORDING",
            "params": {
                "captureVideo": True,
                "captureAudio": False,
                "showBorder": True,
                "borderColor": "#FF0000"
            },
            "timestamp": 1693825200000
        }
        
        # Act
        serialized = json.dumps(message_data)
        deserialized = json.loads(serialized)
        
        # Assert
        assert deserialized["command"] == "START_RECORDING"
        assert deserialized["params"]["captureVideo"] is True
        assert deserialized["timestamp"] == 1693825200000
        assert "id" not in deserialized  # Should be added by messaging layer
    
    def test_message_validation_required_fields(self):
        """Test message validation with missing required fields."""
        # Arrange
        invalid_messages = [
            {},  # Empty message
            {"params": {}},  # Missing command
            {"command": ""},  # Empty command
            {"command": "START_RECORDING", "params": None},  # Invalid params
        ]
        
        # Act & Assert
        for invalid_msg in invalid_messages:
            with pytest.raises((ValueError, TypeError, KeyError)):
                self._validate_message(invalid_msg)
    
    def test_message_id_generation(self):
        """Test automatic message ID generation."""
        # Arrange
        base_message = {
            "command": "START_RECORDING",
            "params": {"video": True}
        }
        
        # Act
        msg1 = self._add_message_id(base_message.copy())
        msg2 = self._add_message_id(base_message.copy())
        
        # Assert
        assert "id" in msg1
        assert "id" in msg2
        assert msg1["id"] != msg2["id"]
        assert len(msg1["id"]) > 0
    
    def test_native_host_connection_success(self, mock_chrome_runtime):
        """Test successful native host connection."""
        # Arrange
        test_message = {
            "command": "GET_STATUS",
            "params": {}
        }
        expected_response = {
            "status": "SUCCESS",
            "data": {"recording": False, "connected": True}
        }
        
        mock_chrome_runtime.sendNativeMessage.return_value = None
        
        def mock_callback(app_name, message, callback):
            callback(expected_response)
        
        mock_chrome_runtime.sendNativeMessage.side_effect = mock_callback
        
        # Act
        with patch('chrome.runtime', mock_chrome_runtime):
            response = self._send_native_message(test_message)
        
        # Assert
        assert response["status"] == "SUCCESS"
        assert response["data"]["connected"] is True
        mock_chrome_runtime.sendNativeMessage.assert_called_once()
    
    def test_native_host_connection_failure(self, mock_chrome_runtime):
        """Test native host connection failure handling."""
        # Arrange
        test_message = {"command": "START_RECORDING", "params": {}}
        mock_chrome_runtime.lastError = {"message": "Specified native messaging host not found."}
        
        def mock_callback(app_name, message, callback):
            callback(None)  # Chrome calls callback with null on error
        
        mock_chrome_runtime.sendNativeMessage.side_effect = mock_callback
        
        # Act & Assert
        with patch('chrome.runtime', mock_chrome_runtime):
            with pytest.raises(ConnectionError, match="native messaging host not found"):
                self._send_native_message(test_message)
    
    def test_command_routing_start_recording(self, mock_chrome_runtime):
        """Test START_RECORDING command routing."""
        # Arrange
        command_message = {
            "command": "START_RECORDING",
            "params": {
                "captureVideo": True,
                "captureAudio": False,
                "showBorder": True
            }
        }
        
        expected_response = {
            "status": "SUCCESS",
            "data": {
                "sessionId": "test-session-123",
                "recordingStarted": True
            }
        }
        
        def mock_callback(app_name, message, callback):
            # Verify the message structure
            assert message["command"] == "START_RECORDING"
            assert "id" in message
            assert "timestamp" in message
            callback(expected_response)
        
        mock_chrome_runtime.sendNativeMessage.side_effect = mock_callback
        
        # Act
        with patch('chrome.runtime', mock_chrome_runtime):
            response = self._send_native_message(command_message)
        
        # Assert
        assert response["status"] == "SUCCESS"
        assert "sessionId" in response["data"]
        assert response["data"]["recordingStarted"] is True
    
    def test_command_routing_stop_recording(self, mock_chrome_runtime):
        """Test STOP_RECORDING command routing."""
        # Arrange
        command_message = {
            "command": "STOP_RECORDING",
            "params": {"sessionId": "test-session-123"}
        }
        
        expected_response = {
            "status": "SUCCESS",
            "data": {
                "recordingStopped": True,
                "filePath": "/path/to/recording.mkd",
                "duration": 30.5
            }
        }
        
        def mock_callback(app_name, message, callback):
            assert message["command"] == "STOP_RECORDING"
            assert message["params"]["sessionId"] == "test-session-123"
            callback(expected_response)
        
        mock_chrome_runtime.sendNativeMessage.side_effect = mock_callback
        
        # Act
        with patch('chrome.runtime', mock_chrome_runtime):
            response = self._send_native_message(command_message)
        
        # Assert
        assert response["status"] == "SUCCESS"
        assert response["data"]["recordingStopped"] is True
        assert "filePath" in response["data"]
    
    def test_error_handling_invalid_command(self, mock_chrome_runtime):
        """Test handling of invalid command responses."""
        # Arrange
        invalid_command = {
            "command": "INVALID_COMMAND",
            "params": {}
        }
        
        error_response = {
            "status": "ERROR",
            "error": "Unknown command: INVALID_COMMAND"
        }
        
        def mock_callback(app_name, message, callback):
            callback(error_response)
        
        mock_chrome_runtime.sendNativeMessage.side_effect = mock_callback
        
        # Act
        with patch('chrome.runtime', mock_chrome_runtime):
            response = self._send_native_message(invalid_command)
        
        # Assert
        assert response["status"] == "ERROR"
        assert "Unknown command" in response["error"]
    
    def test_timeout_handling(self, mock_chrome_runtime):
        """Test message timeout handling."""
        # Arrange
        slow_message = {"command": "START_RECORDING", "params": {}}
        
        def slow_callback(app_name, message, callback):
            # Simulate slow response - don't call callback
            pass
        
        mock_chrome_runtime.sendNativeMessage.side_effect = slow_callback
        
        # Act & Assert
        with patch('chrome.runtime', mock_chrome_runtime):
            with pytest.raises(TimeoutError):
                self._send_native_message(slow_message, timeout=0.1)
    
    # Helper methods for testing
    def _validate_message(self, message):
        """Validate message structure."""
        if not isinstance(message, dict):
            raise TypeError("Message must be a dictionary")
        
        if "command" not in message:
            raise KeyError("Message must have 'command' field")
        
        if not message.get("command"):
            raise ValueError("Command cannot be empty")
        
        if "params" in message and not isinstance(message["params"], dict):
            raise TypeError("Params must be a dictionary")
        
        return True
    
    def _add_message_id(self, message):
        """Add unique ID to message."""
        import uuid
        message["id"] = str(uuid.uuid4())
        message["timestamp"] = int(time.time() * 1000)
        return message
    
    def _send_native_message(self, message, timeout=5.0):
        """Send message to native host with timeout."""
        import threading
        import queue
        
        # Add ID and timestamp if not present
        if "id" not in message:
            message = self._add_message_id(message)
        
        # Validate message
        self._validate_message(message)
        
        # Create response queue
        response_queue = queue.Queue()
        
        def callback(response):
            response_queue.put(response)
        
        # Send message
        chrome.runtime.sendNativeMessage(
            "com.mkd.automation",
            message,
            callback
        )
        
        # Wait for response with timeout
        try:
            response = response_queue.get(timeout=timeout)
            
            # Check for Chrome runtime error
            if response is None and chrome.runtime.lastError:
                raise ConnectionError(chrome.runtime.lastError["message"])
            
            return response
            
        except queue.Empty:
            raise TimeoutError(f"Native messaging timeout after {timeout}s")