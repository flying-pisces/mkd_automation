"""
Unit tests for platform detection and capabilities in MKD v2.0.
"""

import pytest
from unittest.mock import Mock, patch
import sys


class TestPlatformDetector:
    """Test platform detection functionality."""
    
    @pytest.fixture
    def mock_platform_modules(self):
        """Mock platform-specific modules."""
        with patch.dict('sys.modules', {
            'win32gui': Mock(),
            'win32api': Mock(),
            'pywin32': Mock(),
            'Cocoa': Mock(),
            'Quartz': Mock(),
            'python-xlib': Mock(),
            'gi': Mock()
        }):
            yield
    
    def test_detect_windows_platform(self, mock_platform_modules):
        """Test Windows platform detection."""
        # Arrange
        with patch('sys.platform', 'win32'):
            from mkd_v2.platform.detector import PlatformDetector
            
            # Act
            platform = PlatformDetector.detect()
            
            # Assert
            assert platform.name == "Windows"
            assert hasattr(platform, 'start_input_capture')
            assert hasattr(platform, 'execute_mouse_action')
            assert hasattr(platform, 'execute_keyboard_action')
    
    def test_detect_macos_platform(self, mock_platform_modules):
        """Test macOS platform detection."""
        # Arrange
        with patch('sys.platform', 'darwin'):
            from mkd_v2.platform.detector import PlatformDetector
            
            # Act
            platform = PlatformDetector.detect()
            
            # Assert
            assert platform.name == "macOS"
            assert hasattr(platform, 'start_input_capture')
            assert hasattr(platform, 'get_active_window_info')
            assert hasattr(platform, 'create_screen_overlay')
    
    def test_detect_linux_platform(self, mock_platform_modules):
        """Test Linux platform detection."""
        # Arrange
        with patch('sys.platform', 'linux'):
            from mkd_v2.platform.detector import PlatformDetector
            
            # Act
            platform = PlatformDetector.detect()
            
            # Assert
            assert platform.name == "Linux"
            assert hasattr(platform, 'start_input_capture')
            assert hasattr(platform, 'execute_shell_command')
    
    def test_unsupported_platform(self, mock_platform_modules):
        """Test handling of unsupported platform."""
        # Arrange
        with patch('sys.platform', 'unsupported_os'):
            from mkd_v2.platform.detector import PlatformDetector
            
            # Act & Assert
            with pytest.raises(NotImplementedError, match="Unsupported platform"):
                PlatformDetector.detect()
    
    def test_get_platform_capabilities_windows(self, mock_platform_modules):
        """Test Windows platform capabilities."""
        # Arrange
        with patch('sys.platform', 'win32'):
            from mkd_v2.platform.detector import PlatformDetector
            platform = PlatformDetector.detect()
            
            # Act
            capabilities = platform.get_capabilities()
            
            # Assert
            expected_capabilities = {
                'input_capture': True,
                'screen_recording': True,
                'ui_automation': True,
                'shell_commands': True,
                'window_management': True,
                'hotkey_support': True,
                'overlay_support': True,
                'audio_capture': True
            }
            
            for capability, expected in expected_capabilities.items():
                assert capabilities.get(capability) == expected
    
    def test_get_platform_capabilities_macos(self, mock_platform_modules):
        """Test macOS platform capabilities."""
        # Arrange
        with patch('sys.platform', 'darwin'):
            from mkd_v2.platform.detector import PlatformDetector
            platform = PlatformDetector.detect()
            
            # Act
            capabilities = platform.get_capabilities()
            
            # Assert
            expected_capabilities = {
                'input_capture': True,
                'screen_recording': True,
                'ui_automation': True,
                'shell_commands': True,
                'accessibility_required': True,
                'applescript_support': True
            }
            
            for capability, expected in expected_capabilities.items():
                assert capabilities.get(capability) == expected
    
    def test_check_permissions_success(self, mock_platform_modules):
        """Test successful permission check."""
        # Arrange
        with patch('sys.platform', 'win32'):
            from mkd_v2.platform.detector import PlatformDetector
            platform = PlatformDetector.detect()
            
            # Mock successful permission checks
            with patch.object(platform, '_check_input_permissions', return_value=True), \
                 patch.object(platform, '_check_screen_permissions', return_value=True):
                
                # Act
                permissions = platform.check_permissions()
                
                # Assert
                assert permissions['input_capture'] is True
                assert permissions['screen_recording'] is True
                assert permissions['overall'] is True
    
    def test_check_permissions_failure(self, mock_platform_modules):
        """Test permission check failure."""
        # Arrange
        with patch('sys.platform', 'darwin'):
            from mkd_v2.platform.detector import PlatformDetector
            platform = PlatformDetector.detect()
            
            # Mock failed permission checks
            with patch.object(platform, '_check_accessibility_permissions', return_value=False):
                
                # Act
                permissions = platform.check_permissions()
                
                # Assert
                assert permissions['accessibility'] is False
                assert permissions['overall'] is False
                assert 'missing_permissions' in permissions
    
    def test_request_permissions(self, mock_platform_modules):
        """Test permission request functionality."""
        # Arrange
        with patch('sys.platform', 'darwin'):
            from mkd_v2.platform.detector import PlatformDetector
            platform = PlatformDetector.detect()
            
            # Mock permission request
            with patch.object(platform, '_request_accessibility_permission', return_value=True):
                
                # Act
                result = platform.request_permissions(['accessibility'])
                
                # Assert
                assert result is True
    
    def test_get_platform_info(self, mock_platform_modules):
        """Test platform information retrieval."""
        # Arrange
        with patch('sys.platform', 'win32'), \
             patch('platform.system', return_value='Windows'), \
             patch('platform.release', return_value='10'), \
             patch('platform.version', return_value='10.0.19041'):
            
            from mkd_v2.platform.detector import PlatformDetector
            platform = PlatformDetector.detect()
            
            # Act
            info = platform.get_platform_info()
            
            # Assert
            assert info['system'] == 'Windows'
            assert info['release'] == '10'
            assert 'version' in info
            assert 'architecture' in info
    
    def test_get_available_features(self, mock_platform_modules):
        """Test available features detection."""
        # Arrange
        with patch('sys.platform', 'win32'):
            from mkd_v2.platform.detector import PlatformDetector
            platform = PlatformDetector.detect()
            
            # Act
            features = platform.get_available_features()
            
            # Assert
            assert 'basic_recording' in features
            assert 'video_recording' in features
            assert 'ui_automation' in features
            assert 'process_management' in features
    
    def test_platform_compatibility_check(self, mock_platform_modules):
        """Test platform compatibility verification."""
        # Arrange
        with patch('sys.platform', 'win32'):
            from mkd_v2.platform.detector import PlatformDetector
            platform = PlatformDetector.detect()
            
            # Act
            compatibility = platform.check_compatibility()
            
            # Assert
            assert isinstance(compatibility, dict)
            assert 'compatible' in compatibility
            assert 'missing_dependencies' in compatibility
            assert 'warnings' in compatibility
    
    def test_dependency_verification_success(self, mock_platform_modules):
        """Test successful dependency verification."""
        # Arrange
        with patch('sys.platform', 'win32'):
            from mkd_v2.platform.detector import PlatformDetector
            platform = PlatformDetector.detect()
            
            # Mock successful imports
            with patch('importlib.import_module') as mock_import:
                mock_import.return_value = Mock()
                
                # Act
                dependencies = platform.verify_dependencies()
                
                # Assert
                assert dependencies['all_available'] is True
                assert len(dependencies['missing']) == 0
    
    def test_dependency_verification_failure(self, mock_platform_modules):
        """Test dependency verification with missing modules."""
        # Arrange
        with patch('sys.platform', 'win32'):
            from mkd_v2.platform.detector import PlatformDetector
            platform = PlatformDetector.detect()
            
            # Mock failed imports
            def mock_import(module_name):
                if module_name == 'win32gui':
                    raise ImportError(f"No module named '{module_name}'")
                return Mock()
            
            with patch('importlib.import_module', side_effect=mock_import):
                
                # Act
                dependencies = platform.verify_dependencies()
                
                # Assert
                assert dependencies['all_available'] is False
                assert 'win32gui' in dependencies['missing']
    
    def test_platform_initialization(self, mock_platform_modules):
        """Test platform initialization process."""
        # Arrange
        with patch('sys.platform', 'win32'):
            from mkd_v2.platform.detector import PlatformDetector
            platform = PlatformDetector.detect()
            
            # Act
            initialization_result = platform.initialize()
            
            # Assert
            assert initialization_result['success'] is True
            assert 'initialized_components' in initialization_result
    
    def test_platform_cleanup(self, mock_platform_modules):
        """Test platform cleanup process."""
        # Arrange
        with patch('sys.platform', 'win32'):
            from mkd_v2.platform.detector import PlatformDetector
            platform = PlatformDetector.detect()
            
            # Initialize first
            platform.initialize()
            
            # Act
            cleanup_result = platform.cleanup()
            
            # Assert
            assert cleanup_result is True


class TestPlatformInterface:
    """Test the abstract platform interface."""
    
    def test_interface_methods_required(self):
        """Test that all required interface methods are defined."""
        from mkd_v2.platform.base import PlatformInterface
        
        # Act - Try to instantiate interface directly
        with pytest.raises(TypeError):
            PlatformInterface()
    
    def test_interface_method_signatures(self, mock_platform_modules):
        """Test that platform implementations have correct method signatures."""
        # Arrange
        with patch('sys.platform', 'win32'):
            from mkd_v2.platform.detector import PlatformDetector
            platform = PlatformDetector.detect()
            
            # Act & Assert - Check required methods exist
            required_methods = [
                'start_input_capture',
                'stop_input_capture', 
                'execute_mouse_action',
                'execute_keyboard_action',
                'get_active_window_info',
                'create_screen_overlay',
                'execute_shell_command'
            ]
            
            for method_name in required_methods:
                assert hasattr(platform, method_name)
                assert callable(getattr(platform, method_name))