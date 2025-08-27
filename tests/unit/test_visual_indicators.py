"""
Tests for visual recording indicators (red border + timer).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
from pathlib import Path
import time


class TestVisualIndicators:
    """Test visual recording indicators functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def mock_platform(self):
        """Mock platform with overlay support."""
        platform = Mock()
        platform.name = "TestPlatform"
        platform.get_capabilities.return_value = {
            'overlay_support': True,
            'multi_monitor': True
        }
        platform.get_monitor_info.return_value = [
            {
                'index': 0,
                'name': 'Test Monitor',
                'width': 1920,
                'height': 1080,
                'x': 0,
                'y': 0,
                'is_primary': True
            }
        ]
        platform.create_screen_overlay.return_value = "mock_overlay_id"
        platform.update_overlay.return_value = True
        platform.destroy_overlay.return_value = True
        return platform
    
    def test_screen_overlay_initialization(self, mock_platform):
        """Test screen overlay can be initialized."""
        from mkd_v2.ui.overlay import ScreenOverlay
        
        overlay = ScreenOverlay(mock_platform)
        
        assert overlay.platform == mock_platform
        assert overlay.state.value == 'hidden'
        assert len(overlay.border_overlays) == 0
        assert overlay.timer_overlay is None
    
    def test_border_config_creation(self):
        """Test border configuration."""
        from mkd_v2.ui.overlay import BorderConfig
        
        config = BorderConfig(
            show_border=True,
            color="#FF0000",
            width=5,
            opacity=0.8,
            style="solid"
        )
        
        assert config.show_border is True
        assert config.color == "#FF0000"
        assert config.width == 5
        assert config.opacity == 0.8
        assert config.style == "solid"
    
    def test_timer_config_creation(self):
        """Test timer configuration."""
        from mkd_v2.ui.overlay import TimerConfig
        
        config = TimerConfig(
            show_timer=True,
            position="top-right",
            font_size=16,
            format="mm:ss"
        )
        
        assert config.show_timer is True
        assert config.position == "top-right"
        assert config.font_size == 16
        assert config.format == "mm:ss"
    
    def test_show_recording_indicators(self, mock_platform):
        """Test showing recording indicators."""
        from mkd_v2.ui.overlay import ScreenOverlay, BorderConfig, TimerConfig
        
        overlay = ScreenOverlay(mock_platform)
        
        border_config = BorderConfig(show_border=True)
        timer_config = TimerConfig(show_timer=True)
        
        success = overlay.show_recording_indicators(border_config, timer_config)
        
        assert success is True
        assert overlay.state.value == 'visible'
        assert overlay.recording_start_time is not None
        
        # Verify platform calls
        mock_platform.get_monitor_info.assert_called_once()
        mock_platform.create_screen_overlay.assert_called()
    
    def test_hide_recording_indicators(self, mock_platform):
        """Test hiding recording indicators."""
        from mkd_v2.ui.overlay import ScreenOverlay, BorderConfig, TimerConfig
        
        overlay = ScreenOverlay(mock_platform)
        
        # First show indicators
        overlay.show_recording_indicators(BorderConfig(), TimerConfig())
        assert overlay.state.value == 'visible'
        
        # Then hide them
        success = overlay.hide_recording_indicators()
        
        assert success is True
        assert overlay.state.value == 'hidden'
        assert overlay.recording_start_time is None
        
        # Verify cleanup calls
        mock_platform.destroy_overlay.assert_called()
    
    def test_timer_update(self, mock_platform):
        """Test timer display updates."""
        from mkd_v2.ui.overlay import ScreenOverlay, BorderConfig, TimerConfig
        import time
        from datetime import datetime
        
        overlay = ScreenOverlay(mock_platform)
        
        # Show indicators with timer
        overlay.show_recording_indicators(
            BorderConfig(show_border=False),
            TimerConfig(show_timer=True)
        )
        
        # Set a specific start time
        test_start_time = datetime.now()
        overlay.recording_start_time = test_start_time
        
        # Create mock timer overlay
        overlay.timer_overlay = "mock_timer"
        
        # Update timer
        success = overlay.update_timer_display()
        
        assert success is True
        assert overlay.stats['timer_updates'] > 0
    
    @patch('mkd_v2.platform.detector.PlatformDetector.detect')
    def test_recording_engine_with_visual_indicators(self, mock_detect, mock_platform, temp_dir):
        """Test recording engine integration with visual indicators."""
        mock_detect.return_value = mock_platform
        
        from mkd_v2.recording.recording_engine import RecordingEngine
        from mkd_v2.core.session_manager import SessionManager, RecordingConfig
        
        session_manager = SessionManager(storage_path=temp_dir)
        engine = RecordingEngine(session_manager)
        
        # Test that overlay is initialized
        assert engine.overlay is not None
        assert hasattr(engine.overlay, 'show_recording_indicators')
        assert hasattr(engine.overlay, 'hide_recording_indicators')
        
        # Test recording start shows indicators
        user = session_manager.authenticate_user("admin", "admin123")
        config = RecordingConfig(show_border=True)
        
        # Mock the platform methods to avoid actual recording
        mock_platform.initialize.return_value = {'success': True}
        mock_platform.check_permissions.return_value = {'overall': True}
        mock_platform.start_input_capture.return_value = True
        mock_platform.stop_input_capture.return_value = True
        
        # Start recording
        result = engine.start_recording(user.id, config.__dict__)
        
        assert result['sessionId'] is not None
        assert engine.state.value == 'recording'
        
        # Verify overlay calls would have been made
        mock_platform.create_screen_overlay.assert_called()
        
        # Stop recording
        result = engine.stop_recording()
        
        assert result['eventCount'] >= 0
        assert engine.state.value == 'idle'
        
        # Verify overlay cleanup
        mock_platform.destroy_overlay.assert_called()
    
    def test_overlay_status_reporting(self, mock_platform):
        """Test overlay status reporting."""
        from mkd_v2.ui.overlay import ScreenOverlay, BorderConfig, TimerConfig
        
        overlay = ScreenOverlay(mock_platform)
        
        # Test initial status
        status = overlay.get_status()
        
        assert status['state'] == 'hidden'
        assert status['recording_active'] is False
        assert status['border_overlays_count'] == 0
        assert status['timer_overlay_active'] is False
        
        # Show indicators and check status
        overlay.show_recording_indicators(BorderConfig(), TimerConfig())
        
        status = overlay.get_status()
        
        assert status['state'] == 'visible'
        assert status['recording_active'] is True
        assert 'recording_duration' in status
        assert 'recording_start_time' in status
    
    def test_multi_monitor_support(self, mock_platform):
        """Test multi-monitor overlay support."""
        from mkd_v2.ui.overlay import ScreenOverlay, BorderConfig
        
        # Mock multiple monitors
        mock_platform.get_monitor_info.return_value = [
            {'index': 0, 'name': 'Monitor 1', 'width': 1920, 'height': 1080, 'x': 0, 'y': 0},
            {'index': 1, 'name': 'Monitor 2', 'width': 1920, 'height': 1080, 'x': 1920, 'y': 0}
        ]
        
        overlay = ScreenOverlay(mock_platform)
        
        # Test border on all monitors (default)
        border_config = BorderConfig(show_border=True)
        success = overlay.show_recording_indicators(border_config)
        
        assert success is True
        # Should create overlay for each monitor
        assert mock_platform.create_screen_overlay.call_count >= 1
        
        # Test border on specific monitors
        overlay.hide_recording_indicators()
        mock_platform.reset_mock()
        
        border_config = BorderConfig(show_border=True, monitors=[0])
        success = overlay.show_recording_indicators(border_config)
        
        assert success is True
    
    def test_overlay_error_handling(self, mock_platform):
        """Test overlay error handling."""
        from mkd_v2.ui.overlay import ScreenOverlay, BorderConfig
        
        # Mock platform failure
        mock_platform.create_screen_overlay.return_value = None
        mock_platform.get_monitor_info.return_value = []
        
        overlay = ScreenOverlay(mock_platform)
        
        # Test graceful failure
        success = overlay.show_recording_indicators(BorderConfig())
        
        assert success is False
        assert overlay.state.value == 'error'
        assert overlay.stats['errors_encountered'] > 0
    
    def test_border_blinking_animation(self, mock_platform):
        """Test border blinking animation."""
        from mkd_v2.ui.overlay import ScreenOverlay, BorderConfig
        
        overlay = ScreenOverlay(mock_platform)
        
        # Create mock border overlays
        overlay.border_overlays = ["mock_overlay_1", "mock_overlay_2"]
        overlay.border_config = BorderConfig(
            show_border=True,
            style="blinking",
            blink_interval=0.1
        )
        
        # Test blink handling
        overlay._handle_border_blinking()
        
        # Should have updated overlays
        assert mock_platform.update_overlay.call_count > 0
        assert overlay.stats['blinks_performed'] > 0