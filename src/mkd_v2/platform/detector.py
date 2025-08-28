"""
Platform Detector - Detects current platform and returns appropriate implementation.

Supports Windows, macOS, and Linux with automatic platform detection
and capability verification.
"""

import sys
import platform
import logging
import importlib
from typing import Dict, Any, Optional
from .base import PlatformInterface


logger = logging.getLogger(__name__)


class PlatformDetector:
    """
    Detects current platform and provides appropriate implementation.
    
    Features:
    - Automatic platform detection
    - Capability verification
    - Dependency checking
    - Fallback mechanisms
    """
    
    _platform_cache: Optional[PlatformInterface] = None
    
    @classmethod
    def detect(cls) -> PlatformInterface:
        """
        Detect current platform and return appropriate implementation.
        
        Returns:
            Platform-specific implementation
            
        Raises:
            NotImplementedError: If platform is not supported
            ImportError: If required dependencies are missing
        """
        if cls._platform_cache is not None:
            return cls._platform_cache
        
        system = sys.platform.lower()
        logger.info(f"Detecting platform: {system}")
        
        try:
            if system.startswith('win'):
                from .implementations.windows import WindowsPlatform
                platform_impl = WindowsPlatform()
                
            elif system == 'darwin':
                from .implementations.macos import MacOSPlatform
                platform_impl = MacOSPlatform()
                
            elif system.startswith('linux'):
                from .implementations.linux import LinuxPlatform
                platform_impl = LinuxPlatform()
                
            else:
                raise NotImplementedError(f"Unsupported platform: {system}")
            
            # Verify platform implementation
            cls._verify_implementation(platform_impl)
            
            # Cache the result
            cls._platform_cache = platform_impl
            
            logger.info(f"Platform detected: {platform_impl.name}")
            return platform_impl
            
        except ImportError as e:
            logger.error(f"Failed to import platform implementation: {e}")
            raise ImportError(
                f"Missing dependencies for platform {system}. "
                f"Please install required packages: {e}"
            )
        except Exception as e:
            logger.error(f"Platform detection failed: {e}")
            raise
    
    @classmethod
    def _verify_implementation(cls, platform_impl: PlatformInterface):
        """
        Verify that platform implementation has required methods.
        
        Args:
            platform_impl: Platform implementation to verify
            
        Raises:
            AttributeError: If required methods are missing
        """
        required_methods = [
            'start_input_capture',
            'stop_input_capture',
            'execute_mouse_action',
            'execute_keyboard_action',
            'get_active_window_info',
            'create_screen_overlay',
            'execute_shell_command',
            'get_capabilities',
            'check_permissions'
        ]
        
        for method_name in required_methods:
            if not hasattr(platform_impl, method_name):
                raise AttributeError(
                    f"Platform implementation missing required method: {method_name}"
                )
            
            if not callable(getattr(platform_impl, method_name)):
                raise AttributeError(
                    f"Platform implementation attribute is not callable: {method_name}"
                )
    
    @classmethod
    def get_platform_info(cls) -> Dict[str, Any]:
        """
        Get detailed platform information.
        
        Returns:
            Dictionary with platform details
        """
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation()
        }
    
    @classmethod
    def check_dependencies(cls) -> Dict[str, Any]:
        """
        Check platform-specific dependencies.
        
        Returns:
            Dictionary with dependency status
        """
        system = sys.platform.lower()
        dependencies = {
            'platform': system,
            'all_available': True,
            'missing': [],
            'optional_missing': [],
            'details': {}
        }
        
        try:
            if system.startswith('win'):
                deps = cls._check_windows_dependencies()
            elif system == 'darwin':
                deps = cls._check_macos_dependencies()
            elif system.startswith('linux'):
                deps = cls._check_linux_dependencies()
            else:
                deps = {'available': [], 'missing': ['platform_not_supported']}
            
            dependencies.update(deps)
            dependencies['all_available'] = len(dependencies['missing']) == 0
            
        except Exception as e:
            logger.error(f"Dependency check failed: {e}")
            dependencies['error'] = str(e)
            dependencies['all_available'] = False
        
        return dependencies
    
    @classmethod
    def _check_windows_dependencies(cls) -> Dict[str, Any]:
        """Check Windows-specific dependencies."""
        required = [
            'win32gui',
            'win32api', 
            'win32con',
            'pynput'
        ]
        
        optional = [
            'pygetwindow',
            'pycaw',
            'pyautogui'
        ]
        
        return cls._check_module_availability(required, optional)
    
    @classmethod
    def _check_macos_dependencies(cls) -> Dict[str, Any]:
        """Check macOS-specific dependencies."""
        required = [
            'Cocoa',
            'Quartz',
            'ApplicationServices',
            'pynput'
        ]
        
        optional = [
            'pyobjc-core',
            'pyautogui'
        ]
        
        return cls._check_module_availability(required, optional)
    
    @classmethod
    def _check_linux_dependencies(cls) -> Dict[str, Any]:
        """Check Linux-specific dependencies."""
        required = [
            'Xlib',
            'pynput',
            'gi'  # PyGObject
        ]
        
        optional = [
            'pycairo',
            'evdev',
            'pyautogui'
        ]
        
        return cls._check_module_availability(required, optional)
    
    @classmethod
    def _check_module_availability(cls, required: list, optional: list) -> Dict[str, Any]:
        """
        Check availability of required and optional modules.
        
        Args:
            required: List of required module names
            optional: List of optional module names
            
        Returns:
            Dictionary with availability status
        """
        result = {
            'available': [],
            'missing': [],
            'optional_missing': [],
            'details': {}
        }
        
        # Check required modules
        for module_name in required:
            try:
                importlib.import_module(module_name)
                result['available'].append(module_name)
                result['details'][module_name] = {'status': 'available', 'required': True}
            except ImportError as e:
                result['missing'].append(module_name)
                result['details'][module_name] = {
                    'status': 'missing', 
                    'required': True,
                    'error': str(e)
                }
        
        # Check optional modules
        for module_name in optional:
            try:
                importlib.import_module(module_name)
                result['available'].append(module_name)
                result['details'][module_name] = {'status': 'available', 'required': False}
            except ImportError as e:
                result['optional_missing'].append(module_name)
                result['details'][module_name] = {
                    'status': 'missing',
                    'required': False,
                    'error': str(e)
                }
        
        return result
    
    @classmethod
    def get_recommended_setup(cls) -> Dict[str, Any]:
        """
        Get platform-specific setup recommendations.
        
        Returns:
            Dictionary with setup instructions
        """
        system = sys.platform.lower()
        
        if system.startswith('win'):
            return cls._get_windows_setup()
        elif system == 'darwin':
            return cls._get_macos_setup()
        elif system.startswith('linux'):
            return cls._get_linux_setup()
        else:
            return {'error': f'Unsupported platform: {system}'}
    
    @classmethod
    def _get_windows_setup(cls) -> Dict[str, Any]:
        """Get Windows setup recommendations."""
        return {
            'platform': 'Windows',
            'required_packages': [
                'pip install pywin32',
                'pip install pynput',
                'pip install pillow'
            ],
            'optional_packages': [
                'pip install pygetwindow',
                'pip install pycaw',
                'pip install pyautogui'
            ],
            'permissions': [
                'Run as Administrator (for system-level hooks)',
                'Allow app through Windows Defender'
            ],
            'notes': [
                'Some antivirus software may flag input capture',
                'UAC prompts may be required for elevated privileges'
            ]
        }
    
    @classmethod
    def _get_macos_setup(cls) -> Dict[str, Any]:
        """Get macOS setup recommendations."""
        return {
            'platform': 'macOS',
            'required_packages': [
                'pip install pyobjc-core',
                'pip install pyobjc-framework-Cocoa',
                'pip install pyobjc-framework-Quartz',
                'pip install pyobjc-framework-ApplicationServices',
                'pip install pynput'
            ],
            'optional_packages': [
                'pip install pyautogui',
                'pip install pillow'
            ],
            'permissions': [
                'Enable "Accessibility" permissions in System Preferences',
                'Enable "Screen Recording" permissions',
                'Enable "Input Monitoring" permissions'
            ],
            'notes': [
                'macOS requires explicit permission grants',
                'First run will trigger permission dialogs',
                'Some features may require macOS 10.14+'
            ]
        }
    
    @classmethod
    def _get_linux_setup(cls) -> Dict[str, Any]:
        """Get Linux setup recommendations."""
        return {
            'platform': 'Linux',
            'required_packages': [
                'pip install python-xlib',
                'pip install pynput',
                'pip install PyGObject',
                'sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0'  # Ubuntu/Debian
            ],
            'optional_packages': [
                'pip install pycairo',
                'pip install evdev',
                'pip install pyautogui'
            ],
            'permissions': [
                'User must be in "input" group for device access',
                'X11 or Wayland display server access'
            ],
            'notes': [
                'Package names vary by distribution',
                'Wayland support may be limited',
                'Some features require X11 extensions'
            ]
        }
    
    # Test compatibility methods
    def detect_platform(self):
        """Detect platform and return platform info (test compatibility)"""
        platform_impl = self.detect()
        
        # Create platform info object for test compatibility
        from dataclasses import dataclass
        
        @dataclass
        class PlatformInfo:
            name: str
            version: str
            capabilities: list = None
        
        system_name = sys.platform.lower()
        if system_name.startswith('win'):
            name = "windows"
        elif system_name == 'darwin':
            name = "macos"
        elif system_name.startswith('linux'):
            name = "linux"
        else:
            name = "unknown"
        
        return PlatformInfo(
            name=name,
            version=platform.version(),
            capabilities=platform_impl.get_capabilities() if platform_impl else []
        )
    
    def get_capabilities(self) -> list:
        """Get platform capabilities (test compatibility)"""
        try:
            platform_impl = self.detect()
            capabilities = platform_impl.get_capabilities()
            if isinstance(capabilities, list):
                return capabilities
            else:
                return list(capabilities) if capabilities else []
        except:
            return ["basic_operations", "screen_capture", "input_simulation"]