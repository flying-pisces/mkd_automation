"""
Base Platform Interface - Abstract base class for platform-specific implementations.

Defines the contract that all platform implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum


class MouseButton(Enum):
    """Mouse button enumeration."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class KeyModifier(Enum):
    """Keyboard modifier keys."""
    CTRL = "ctrl"
    ALT = "alt"
    SHIFT = "shift"
    CMD = "cmd"  # macOS Command key
    WIN = "win"  # Windows key


@dataclass
class MouseAction:
    """Mouse action data structure."""
    action: str  # click, double_click, drag, move, scroll
    button: Optional[MouseButton] = None
    x: int = 0
    y: int = 0
    dx: int = 0  # For scroll or drag
    dy: int = 0  # For scroll or drag
    modifiers: List[KeyModifier] = None


@dataclass
class KeyboardAction:
    """Keyboard action data structure."""
    action: str  # press, release, type
    key: Optional[str] = None
    text: Optional[str] = None
    modifiers: List[KeyModifier] = None


@dataclass
class WindowInfo:
    """Window information data structure."""
    title: str
    class_name: str
    process_name: str
    pid: int
    x: int
    y: int
    width: int
    height: int
    is_active: bool
    is_visible: bool


@dataclass
class UIElement:
    """UI element information."""
    element_type: str  # button, text_field, menu, etc.
    name: str
    value: Optional[str]
    x: int
    y: int
    width: int
    height: int
    is_enabled: bool
    is_visible: bool
    properties: Dict[str, Any]


@dataclass
class OverlayConfig:
    """Screen overlay configuration."""
    color: str = "#FF0000"
    width: int = 5
    opacity: float = 0.8
    style: str = "border"  # border, fill, dashed
    monitors: List[int] = None  # None means all monitors


class PlatformInterface(ABC):
    """
    Abstract base class for platform-specific implementations.
    
    All platform implementations must inherit from this class
    and implement all abstract methods.
    """
    
    def __init__(self):
        self.name = "Unknown"
        self.version = "1.0.0"
        self._initialized = False
    
    @abstractmethod
    def initialize(self) -> Dict[str, Any]:
        """
        Initialize platform-specific resources.
        
        Returns:
            Dictionary with initialization results
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """
        Clean up platform-specific resources.
        
        Returns:
            True if cleanup successful
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, bool]:
        """
        Get platform capabilities.
        
        Returns:
            Dictionary mapping capability names to availability
        """
        pass
    
    @abstractmethod
    def check_permissions(self) -> Dict[str, Any]:
        """
        Check required permissions.
        
        Returns:
            Dictionary with permission status
        """
        pass
    
    @abstractmethod
    def request_permissions(self, permissions: List[str]) -> bool:
        """
        Request required permissions from user.
        
        Args:
            permissions: List of permission names to request
            
        Returns:
            True if all permissions granted
        """
        pass
    
    # Input Capture Methods
    
    @abstractmethod
    def start_input_capture(self, callback: Callable) -> bool:
        """
        Start capturing input events.
        
        Args:
            callback: Function to call with captured events
            
        Returns:
            True if capture started successfully
        """
        pass
    
    @abstractmethod
    def stop_input_capture(self) -> bool:
        """
        Stop capturing input events.
        
        Returns:
            True if capture stopped successfully
        """
        pass
    
    # Action Execution Methods
    
    @abstractmethod
    def execute_mouse_action(self, action: MouseAction) -> bool:
        """
        Execute a mouse action.
        
        Args:
            action: MouseAction to execute
            
        Returns:
            True if action executed successfully
        """
        pass
    
    @abstractmethod
    def execute_keyboard_action(self, action: KeyboardAction) -> bool:
        """
        Execute a keyboard action.
        
        Args:
            action: KeyboardAction to execute
            
        Returns:
            True if action executed successfully
        """
        pass
    
    # Window and UI Methods
    
    @abstractmethod
    def get_active_window_info(self) -> Optional[WindowInfo]:
        """
        Get information about the active window.
        
        Returns:
            WindowInfo object or None if no active window
        """
        pass
    
    @abstractmethod
    def get_window_list(self) -> List[WindowInfo]:
        """
        Get list of all visible windows.
        
        Returns:
            List of WindowInfo objects
        """
        pass
    
    @abstractmethod
    def get_ui_element_at_position(self, x: int, y: int) -> Optional[UIElement]:
        """
        Get UI element at screen coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            UIElement object or None if no element found
        """
        pass
    
    # Screen and Display Methods
    
    @abstractmethod
    def get_screen_resolution(self) -> Tuple[int, int]:
        """
        Get screen resolution.
        
        Returns:
            Tuple of (width, height)
        """
        pass
    
    @abstractmethod
    def get_monitor_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all monitors.
        
        Returns:
            List of monitor information dictionaries
        """
        pass
    
    @abstractmethod
    def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> bytes:
        """
        Take a screenshot.
        
        Args:
            region: Optional region as (x, y, width, height)
            
        Returns:
            Screenshot data as bytes
        """
        pass
    
    # Overlay Methods
    
    @abstractmethod
    def create_screen_overlay(self, config: OverlayConfig) -> Any:
        """
        Create a screen overlay.
        
        Args:
            config: Overlay configuration
            
        Returns:
            Platform-specific overlay object
        """
        pass
    
    @abstractmethod
    def update_overlay(self, overlay: Any, config: OverlayConfig) -> bool:
        """
        Update existing overlay.
        
        Args:
            overlay: Platform-specific overlay object
            config: New overlay configuration
            
        Returns:
            True if update successful
        """
        pass
    
    @abstractmethod
    def destroy_overlay(self, overlay: Any) -> bool:
        """
        Destroy screen overlay.
        
        Args:
            overlay: Platform-specific overlay object
            
        Returns:
            True if destruction successful
        """
        pass
    
    # System Integration Methods
    
    @abstractmethod
    def execute_shell_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute shell command.
        
        Args:
            command: Command to execute
            **kwargs: Additional execution parameters
            
        Returns:
            Dictionary with execution results
        """
        pass
    
    @abstractmethod
    def get_process_list(self) -> List[Dict[str, Any]]:
        """
        Get list of running processes.
        
        Returns:
            List of process information dictionaries
        """
        pass
    
    @abstractmethod
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            Dictionary with system information
        """
        pass
    
    # Utility Methods
    
    def is_initialized(self) -> bool:
        """Check if platform is initialized."""
        return self._initialized
    
    def get_platform_name(self) -> str:
        """Get platform name."""
        return self.name
    
    def get_platform_version(self) -> str:
        """Get platform implementation version."""
        return self.version
    
    # Context Manager Support
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        return False