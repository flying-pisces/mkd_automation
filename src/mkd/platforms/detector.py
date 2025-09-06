import platform

from mkd.platforms.base import BasePlatform
from mkd.platforms.macos import MacOSPlatform
from mkd.platforms.windows import WindowsPlatform
from mkd.platforms.linux import LinuxPlatform


def get_platform() -> BasePlatform:
    """Returns the platform-specific implementation."""
    system = platform.system()
    if system == "Darwin":
        return MacOSPlatform()
    elif system == "Windows":
        return WindowsPlatform()
    elif system == "Linux":
        return LinuxPlatform()
    else:
        raise NotImplementedError(f"Platform {system} is not supported.")


class PlatformDetector:
    """Wrapper class for platform detection and management"""
    
    def __init__(self):
        """Initialize the platform detector"""
        self._platform_name = None
        self._platform_implementation = None
    
    def get_platform(self) -> str:
        """
        Get the current platform name.
        
        Returns:
            Platform name (Windows, Darwin, Linux)
        """
        if self._platform_name is None:
            self._platform_name = platform.system()
        return self._platform_name
    
    def get_implementation(self) -> BasePlatform:
        """
        Get the platform-specific implementation.
        
        Returns:
            Platform-specific implementation instance
        """
        if self._platform_implementation is None:
            self._platform_implementation = get_platform()
        return self._platform_implementation
    
    def is_windows(self) -> bool:
        """Check if running on Windows"""
        return self.get_platform() == "Windows"
    
    def is_macos(self) -> bool:
        """Check if running on macOS"""
        return self.get_platform() == "Darwin"
    
    def is_linux(self) -> bool:
        """Check if running on Linux"""
        return self.get_platform() == "Linux"
    
    def get_platform_info(self) -> dict:
        """
        Get detailed platform information.
        
        Returns:
            Dictionary with platform details
        """
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "platform": platform.platform()
        }
    
    def is_supported(self) -> bool:
        """
        Check if the current platform is supported.
        
        Returns:
            True if platform is supported, False otherwise
        """
        try:
            self.get_implementation()
            return True
        except NotImplementedError:
            return False
