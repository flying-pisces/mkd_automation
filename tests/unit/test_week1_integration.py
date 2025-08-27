"""
Week 1 Integration Tests - Basic functionality validation.
Tests the core components working together.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
from pathlib import Path


class TestWeek1Integration:
    """Test Week 1 core integration functionality."""
    
    @pytest.fixture
    def mock_platform(self):
        """Mock platform interface."""
        platform = Mock()
        platform.name = "TestPlatform"
        platform.get_capabilities.return_value = {
            'input_capture': True,
            'screen_recording': True,
            'ui_automation': True
        }
        platform.initialize.return_value = {'success': True}
        platform.check_permissions.return_value = {
            'overall': True,
            'missing_permissions': []
        }
        platform.cleanup.return_value = True
        return platform
    
    def test_message_broker_creation(self):
        """Test that message broker can be created and started."""
        from mkd_v2.core.message_broker import MessageBroker
        
        broker = MessageBroker()
        assert broker is not None
        assert not broker._running
        
        # Test basic functionality
        success = broker.start()
        assert success is True
        
        success = broker.stop()
        assert success is True
    
    def test_session_manager_basic_workflow(self, temp_dir):
        """Test basic session management workflow."""
        from mkd_v2.core.session_manager import SessionManager, RecordingConfig
        
        session_manager = SessionManager(storage_path=temp_dir)
        
        # Test user authentication (using default admin)
        user = session_manager.authenticate_user("admin", "admin123")
        assert user is not None
        assert user.username == "admin"
        
        # Test session creation
        config = RecordingConfig(capture_video=True, show_border=True)
        session = session_manager.create_session(user.id, config)
        assert session is not None
        assert session.user_id == user.id
        assert session.config.capture_video is True
        
        # Test session state management
        success = session_manager.start_recording(session.id)
        assert success is True
        
        # Set session to active recording state
        session_manager.set_recording_active(session.id)
        
        success = session_manager.stop_recording(session.id)
        assert success is True
        
        success = session_manager.complete_session(session.id, event_count=10)
        assert success is True
    
    def test_platform_detector_basic_functionality(self):
        """Test that platform detector works."""
        from mkd_v2.platform.detector import PlatformDetector
        
        # Test platform info
        info = PlatformDetector.get_platform_info()
        assert isinstance(info, dict)
        assert 'system' in info
        assert 'python_version' in info
        
        # Test dependency checking
        deps = PlatformDetector.check_dependencies()
        assert isinstance(deps, dict)
        assert 'platform' in deps
        assert 'all_available' in deps
        
        # Test setup recommendations
        setup = PlatformDetector.get_recommended_setup()
        assert isinstance(setup, dict)
        assert 'platform' in setup or 'error' in setup
    
    @patch('mkd_v2.platform.detector.PlatformDetector.detect')
    def test_recording_engine_initialization(self, mock_detect, mock_platform, temp_dir):
        """Test that recording engine can be initialized."""
        mock_detect.return_value = mock_platform
        
        from mkd_v2.recording.recording_engine import RecordingEngine
        from mkd_v2.core.session_manager import SessionManager
        
        session_manager = SessionManager(storage_path=temp_dir)
        recording_engine = RecordingEngine(session_manager)
        
        assert recording_engine is not None
        assert recording_engine.session_manager is not None
        assert recording_engine.platform is not None
        
        # Test status
        status = recording_engine.get_status()
        assert isinstance(status, dict)
        assert 'state' in status
        assert 'platform' in status
        assert status['state'] == 'idle'
    
    def test_chrome_extension_manifest_valid(self):
        """Test that Chrome extension manifest is valid."""
        import json
        
        manifest_path = Path(__file__).parent.parent.parent / "chrome-extension" / "manifest.json"
        
        # Check if manifest exists
        assert manifest_path.exists(), "Chrome extension manifest not found"
        
        # Check if manifest is valid JSON
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        # Check required fields
        assert manifest['manifest_version'] == 3
        assert manifest['name'] == "MKD Automation"
        assert 'permissions' in manifest
        assert 'nativeMessaging' in manifest['permissions']
        assert 'background' in manifest
        assert 'action' in manifest
    
    def test_chrome_extension_messaging_structure(self):
        """Test that Chrome extension messaging structure is valid."""
        messaging_path = Path(__file__).parent.parent.parent / "chrome-extension" / "src" / "messaging.js"
        
        # Check if messaging file exists
        assert messaging_path.exists(), "Chrome extension messaging.js not found"
        
        # Read and basic validation
        content = messaging_path.read_text()
        
        # Check for key components
        assert 'NativeMessagingHandler' in content
        assert 'sendMessage' in content
        assert 'START_RECORDING' in content
        assert 'STOP_RECORDING' in content
        assert 'com.mkd.automation' in content
    
    def test_week1_file_structure(self):
        """Test that Week 1 file structure is complete."""
        base_path = Path(__file__).parent.parent.parent
        
        # Core v2 structure
        core_files = [
            "src/mkd_v2/__init__.py",
            "src/mkd_v2/core/__init__.py",
            "src/mkd_v2/core/message_broker.py",
            "src/mkd_v2/core/session_manager.py",
            "src/mkd_v2/platform/__init__.py",
            "src/mkd_v2/platform/detector.py",
            "src/mkd_v2/platform/base.py",
            "src/mkd_v2/recording/__init__.py",
            "src/mkd_v2/recording/recording_engine.py"
        ]
        
        for file_path in core_files:
            full_path = base_path / file_path
            assert full_path.exists(), f"Core file missing: {file_path}"
        
        # Chrome extension structure
        chrome_files = [
            "chrome-extension/manifest.json",
            "chrome-extension/src/messaging.js",
            "chrome-extension/src/background.js",
            "chrome-extension/src/popup/popup.html",
            "chrome-extension/src/popup/popup.js",
            "chrome-extension/src/popup/popup.css"
        ]
        
        for file_path in chrome_files:
            full_path = base_path / file_path
            assert full_path.exists(), f"Chrome extension file missing: {file_path}"
        
        # Documentation files
        doc_files = [
            "docs/WEEK1_IMPLEMENTATION_PLAN.md",
            "docs/ERS.md",
            "docs/ARCHITECTURE_V2.md",
            "docs/TEST_DEVELOPMENT_PLAN.md"
        ]
        
        for file_path in doc_files:
            full_path = base_path / file_path
            assert full_path.exists(), f"Documentation file missing: {file_path}"
    
    def test_import_structure_week1(self):
        """Test that Week 1 modules can be imported."""
        # Test core imports
        from mkd_v2.core.message_broker import MessageBroker
        from mkd_v2.core.session_manager import SessionManager
        
        # Test platform imports  
        from mkd_v2.platform.detector import PlatformDetector
        from mkd_v2.platform.base import PlatformInterface
        
        # Test recording imports
        from mkd_v2.recording.recording_engine import RecordingEngine
        
        # Test main module import
        import mkd_v2
        
        # Verify expected exports
        assert hasattr(mkd_v2, 'MessageBroker')
        assert hasattr(mkd_v2, 'SessionManager')
        assert hasattr(mkd_v2, 'PlatformDetector')
        assert hasattr(mkd_v2, 'RecordingEngine')
    
    @patch('mkd_v2.platform.detector.PlatformDetector.detect')
    def test_basic_integration_workflow(self, mock_detect, mock_platform, temp_dir):
        """Test basic integration workflow for Week 1."""
        mock_detect.return_value = mock_platform
        
        # Import components
        from mkd_v2.core.message_broker import MessageBroker, Message, MessageType
        from mkd_v2.core.session_manager import SessionManager
        from mkd_v2.recording.recording_engine import RecordingEngine
        
        # Initialize components
        broker = MessageBroker()
        session_manager = SessionManager(storage_path=temp_dir)
        recording_engine = RecordingEngine(session_manager)
        
        # Test broker start
        assert broker.start() is True
        
        # Test user authentication
        user = session_manager.authenticate_user("admin", "admin123")
        assert user is not None
        
        # Test recording engine status
        status = recording_engine.get_status()
        assert status['state'] == 'idle'
        assert status['platform'] == 'TestPlatform'
        
        # Test command registration
        def mock_start_recording(message):
            return {"sessionId": "test-123", "started": True}
        
        broker.register_command("START_RECORDING", mock_start_recording)
        
        # Test command dispatch
        test_message = {
            "id": "test-msg-1",
            "command": "START_RECORDING",
            "params": {"video": True}
        }
        
        response = broker.dispatch_command(test_message)
        assert response.status == "SUCCESS"
        assert response.data["sessionId"] == "test-123"
        
        # Clean up
        broker.stop()
        recording_engine.cleanup()


class TestWeek1ComponentInitialization:
    """Test that all Week 1 components can be initialized without errors."""
    
    def test_message_broker_initialization(self):
        """Test message broker initialization."""
        from mkd_v2.core.message_broker import MessageBroker
        
        broker = MessageBroker()
        assert len(broker.subscribers) == 0
        assert len(broker.command_handlers) == 0
        assert len(broker.middleware) == 0
        assert not broker._running
    
    def test_session_manager_initialization(self, temp_dir):
        """Test session manager initialization."""
        from mkd_v2.core.session_manager import SessionManager
        
        session_manager = SessionManager(storage_path=temp_dir)
        assert session_manager.storage_path == temp_dir
        assert len(session_manager.active_sessions) == 0
        assert len(session_manager.user_sessions) == 0
        
        # Test database initialization (should create default admin)
        user = session_manager.authenticate_user("admin", "admin123")
        assert user is not None
    
    def test_platform_detector_info_methods(self):
        """Test platform detector information methods."""
        from mkd_v2.platform.detector import PlatformDetector
        
        # These should not raise exceptions
        info = PlatformDetector.get_platform_info()
        assert isinstance(info, dict)
        
        deps = PlatformDetector.check_dependencies()
        assert isinstance(deps, dict)
        
        setup = PlatformDetector.get_recommended_setup()
        assert isinstance(setup, dict)
    
    @patch('mkd_v2.platform.detector.PlatformDetector.detect')
    def test_recording_engine_initialization(self, mock_detect, temp_dir):
        """Test recording engine initialization."""
        # Mock platform
        mock_platform = Mock()
        mock_platform.name = "TestPlatform"
        mock_platform.get_capabilities.return_value = {'input_capture': True}
        mock_detect.return_value = mock_platform
        
        from mkd_v2.recording.recording_engine import RecordingEngine
        from mkd_v2.core.session_manager import SessionManager
        
        session_manager = SessionManager(storage_path=temp_dir)
        engine = RecordingEngine(session_manager)
        
        assert engine.session_manager is session_manager
        assert engine.platform == mock_platform
        assert engine.state.value == 'idle'
        assert engine.event_count == 0