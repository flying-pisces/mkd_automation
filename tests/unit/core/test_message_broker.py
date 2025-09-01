"""
Unit tests for the Message Broker component in MKD v2.0 architecture.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import json
import threading
import time
from typing import Dict, Any, Callable


class TestMessageBroker:
    """Test the central message broker for routing commands and events."""
    
    @pytest.fixture
    def message_broker(self):
        """Create a message broker instance for testing."""
        from mkd_v2.core.message_broker import MessageBroker
        return MessageBroker()
    
    @pytest.fixture
    def sample_message(self):
        """Sample application message."""
        return {
            "id": "msg-12345",
            "command": "START_RECORDING",
            "params": {
                "captureVideo": True,
                "captureAudio": False,
                "showBorder": True,
                "borderColor": "#FF0000"
            },
            "timestamp": 1693825200000
        }
    
    def test_subscribe_to_events(self, message_broker):
        """Test subscribing to events."""
        # Arrange
        event_handler = Mock()
        event_type = "RECORDING_STARTED"
        
        # Act
        message_broker.subscribe(event_type, event_handler)
        
        # Assert
        assert event_type in message_broker.subscribers
        assert event_handler in message_broker.subscribers[event_type]
    
    def test_publish_events(self, message_broker):
        """Test publishing events to subscribers."""
        # Arrange
        handler1 = Mock()
        handler2 = Mock()
        event_type = "RECORDING_STARTED"
        event_data = {"sessionId": "test-123", "timestamp": time.time()}
        
        message_broker.subscribe(event_type, handler1)
        message_broker.subscribe(event_type, handler2)
        
        # Act
        message_broker.publish(event_type, event_data)
        
        # Assert
        handler1.assert_called_once_with(event_data)
        handler2.assert_called_once_with(event_data)
    
    def test_register_command_handler(self, message_broker):
        """Test registering command handlers."""
        # Arrange
        command_handler = Mock(return_value={"status": "SUCCESS"})
        command = "START_RECORDING"
        
        # Act
        message_broker.register_command(command, command_handler)
        
        # Assert
        assert command in message_broker.command_handlers
        assert message_broker.command_handlers[command] == command_handler
    
    def test_dispatch_command_success(self, message_broker, sample_message):
        """Test successful command dispatch."""
        # Arrange
        def mock_handler(message):
            return {
                "id": message["id"],
                "status": "SUCCESS",
                "data": {"sessionId": "test-session-123"},
                "timestamp": int(time.time() * 1000)
            }
        
        message_broker.register_command("START_RECORDING", mock_handler)
        
        # Act
        response = message_broker.dispatch_command(sample_message)
        
        # Assert
        assert response["status"] == "SUCCESS"
        assert response["id"] == sample_message["id"]
        assert "data" in response
        assert "timestamp" in response
    
    def test_dispatch_command_unknown(self, message_broker):
        """Test dispatch of unknown command."""
        # Arrange
        unknown_message = {
            "id": "msg-unknown",
            "command": "UNKNOWN_COMMAND",
            "params": {}
        }
        
        # Act
        response = message_broker.dispatch_command(unknown_message)
        
        # Assert
        assert response["status"] == "ERROR"
        assert response["id"] == unknown_message["id"]
        assert "Unknown command" in response["error"]
    
    def test_dispatch_command_handler_exception(self, message_broker, sample_message):
        """Test command dispatch with handler exception."""
        # Arrange
        def failing_handler(message):
            raise ValueError("Handler failed")
        
        message_broker.register_command("START_RECORDING", failing_handler)
        
        # Act
        response = message_broker.dispatch_command(sample_message)
        
        # Assert
        assert response["status"] == "ERROR"
        assert response["id"] == sample_message["id"]
        assert "Handler failed" in response["error"]
    
    def test_async_event_publishing(self, message_broker):
        """Test asynchronous event publishing."""
        # Arrange
        async def async_handler(data):
            await asyncio.sleep(0.01)  # Simulate async work
            return f"Processed {data['value']}"
        
        sync_handler = Mock()
        event_type = "ASYNC_EVENT"
        event_data = {"value": "test"}
        
        message_broker.subscribe(event_type, async_handler)
        message_broker.subscribe(event_type, sync_handler)
        
        # Act
        message_broker.publish(event_type, event_data)
        
        # Allow async handler to complete
        time.sleep(0.05)
        
        # Assert
        sync_handler.assert_called_once_with(event_data)
        # Note: In real implementation, async handlers would be properly awaited
    
    def test_unsubscribe_from_events(self, message_broker):
        """Test unsubscribing from events."""
        # Arrange
        handler1 = Mock()
        handler2 = Mock()
        event_type = "TEST_EVENT"
        
        message_broker.subscribe(event_type, handler1)
        message_broker.subscribe(event_type, handler2)
        
        # Act
        message_broker.unsubscribe(event_type, handler1)
        message_broker.publish(event_type, {"test": "data"})
        
        # Assert
        handler1.assert_not_called()
        handler2.assert_called_once()
    
    def test_message_validation(self, message_broker):
        """Test message format validation."""
        # Arrange
        invalid_messages = [
            {},  # Empty message
            {"id": "123"},  # Missing command
            {"command": "TEST"},  # Missing ID
            {"id": "123", "command": ""},  # Empty command
            {"id": "", "command": "TEST"},  # Empty ID
        ]
        
        # Act & Assert
        for invalid_msg in invalid_messages:
            response = message_broker.dispatch_command(invalid_msg)
            assert response["status"] == "ERROR"
            assert "Invalid message format" in response["error"]
    
    def test_concurrent_command_processing(self, message_broker):
        """Test concurrent command processing."""
        # Arrange
        results = []
        
        def slow_handler(message):
            time.sleep(0.1)  # Simulate slow processing
            results.append(f"Processed {message['id']}")
            return {"status": "SUCCESS", "id": message["id"]}
        
        message_broker.register_command("SLOW_COMMAND", slow_handler)
        
        messages = [
            {"id": f"msg-{i}", "command": "SLOW_COMMAND", "params": {}}
            for i in range(3)
        ]
        
        # Act - Process messages concurrently
        threads = []
        for msg in messages:
            thread = threading.Thread(
                target=lambda m=msg: message_broker.dispatch_command(m)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert
        assert len(results) == 3
        assert all("Processed msg-" in result for result in results)
    
    def test_event_priority_handling(self, message_broker):
        """Test event handling with priorities."""
        # Arrange
        execution_order = []
        
        def high_priority_handler(data):
            execution_order.append("high")
        
        def low_priority_handler(data):
            execution_order.append("low")
        
        # Subscribe with different priorities (assuming implementation supports this)
        message_broker.subscribe("PRIORITY_EVENT", high_priority_handler, priority="high")
        message_broker.subscribe("PRIORITY_EVENT", low_priority_handler, priority="low")
        
        # Act
        message_broker.publish("PRIORITY_EVENT", {"test": "data"})
        
        # Assert
        # High priority handlers should execute first
        assert execution_order[0] == "high"
        assert execution_order[1] == "low"
    
    def test_message_broker_shutdown(self, message_broker):
        """Test graceful shutdown of message broker."""
        # Arrange
        handler = Mock()
        message_broker.subscribe("TEST_EVENT", handler)
        
        # Act
        message_broker.shutdown()
        
        # Try to publish after shutdown
        message_broker.publish("TEST_EVENT", {"test": "data"})
        
        # Assert
        handler.assert_not_called()  # Should not be called after shutdown
    
    def test_command_middleware(self, message_broker):
        """Test command middleware functionality."""
        # Arrange
        middleware_calls = []
        
        def auth_middleware(message, next_handler):
            middleware_calls.append("auth")
            if message.get("params", {}).get("authenticated"):
                return next_handler(message)
            else:
                return {
                    "id": message["id"],
                    "status": "ERROR",
                    "error": "Authentication required"
                }
        
        def logging_middleware(message, next_handler):
            middleware_calls.append("logging")
            response = next_handler(message)
            # Log the command execution
            return response
        
        def test_handler(message):
            return {"id": message["id"], "status": "SUCCESS"}
        
        # Register middleware and handler
        message_broker.add_middleware(auth_middleware)
        message_broker.add_middleware(logging_middleware)
        message_broker.register_command("PROTECTED_COMMAND", test_handler)
        
        # Act - Unauthenticated request
        unauthenticated_msg = {
            "id": "msg-unauth",
            "command": "PROTECTED_COMMAND",
            "params": {"authenticated": False}
        }
        response1 = message_broker.dispatch_command(unauthenticated_msg)
        
        # Act - Authenticated request
        authenticated_msg = {
            "id": "msg-auth",
            "command": "PROTECTED_COMMAND",
            "params": {"authenticated": True}
        }
        response2 = message_broker.dispatch_command(authenticated_msg)
        
        # Assert
        assert response1["status"] == "ERROR"
        assert "Authentication required" in response1["error"]
        
        assert response2["status"] == "SUCCESS"
        
        # Verify middleware execution order
        assert middleware_calls.count("auth") == 2
        assert middleware_calls.count("logging") == 1  # Only called for successful auth