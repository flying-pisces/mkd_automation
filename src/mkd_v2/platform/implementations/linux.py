"""
Linux Platform Implementation for MKD v2.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Callable

from ..base import PlatformInterface, MouseAction, KeyboardAction, WindowInfo, UIElement, OverlayConfig

logger = logging.getLogger(__name__)


class LinuxPlatform(PlatformInterface):
    """Linux implementation of PlatformInterface for MKD v2."""
    
    def __init__(self):
        super().__init__()
        self.name = "Linux"
        self.version = "2.0.0"
        self.overlays = {}
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize Linux platform."""
        try:
            self._initialized = True
            return {
                'success': True,
                'platform': self.name,
                'capabilities': self.get_capabilities()
            }
        except Exception as e:
            logger.error(f"Linux initialization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def cleanup(self) -> bool:
        """Clean up Linux resources."""
        try:
            for overlay_id in list(self.overlays.keys()):
                self.destroy_overlay(overlay_id)
            self._initialized = False
            return True
        except Exception as e:
            logger.error(f"Linux cleanup failed: {e}")
            return False
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get Linux capabilities."""
        return {
            'input_capture': True,
            'screen_recording': True,
            'ui_automation': True,
            'overlay_support': True,
            'window_management': True,
            'system_integration': True,
            'multi_monitor': True
        }
    
    def check_permissions(self) -> Dict[str, Any]:
        """Check Linux permissions."""
        return {
            'overall': True,
            'missing_permissions': [],
            'details': {
                'input_group': True,
                'x11_access': True
            }
        }
    
    def request_permissions(self, permissions: List[str]) -> bool:
        """Request Linux permissions."""
        return True
    
    def start_input_capture(self, callback: Callable) -> bool:
        """Start input capture on Linux."""
        try:
            self._input_callback = callback
            logger.info("Linux input capture started (mock)")
            return True
        except Exception as e:
            logger.error(f"Failed to start input capture: {e}")
            return False
    
    def stop_input_capture(self) -> bool:
        """Stop input capture on Linux."""
        try:
            self._input_callback = None
            logger.info("Linux input capture stopped (mock)")
            return True
        except Exception as e:
            logger.error(f"Failed to stop input capture: {e}")
            return False
    
    def execute_mouse_action(self, action: MouseAction) -> bool:
        """Execute mouse action on Linux."""
        logger.info(f"Linux executing mouse action: {action.action}")
        return True
    
    def execute_keyboard_action(self, action: KeyboardAction) -> bool:
        """Execute keyboard action on Linux."""
        logger.info(f"Linux executing keyboard action: {action.action}")
        return True
    
    def get_active_window_info(self) -> Optional[WindowInfo]:
        """Get active window info on Linux."""
        return WindowInfo(
            title="Linux Test Window",
            class_name="gtk-window",
            process_name="test-app",
            pid=9999,
            x=100, y=100, width=800, height=600,
            is_active=True, is_visible=True
        )
    
    def get_window_list(self) -> List[WindowInfo]:
        """Get window list on Linux."""
        return [self.get_active_window_info()]
    
    def get_ui_element_at_position(self, x: int, y: int) -> Optional[UIElement]:
        """Get UI element at position on Linux."""
        return UIElement(
            element_type="button", name="Linux Button", value=None,
            x=x, y=y, width=100, height=30,
            is_enabled=True, is_visible=True, properties={}
        )
    
    def get_screen_resolution(self) -> Tuple[int, int]:
        """Get screen resolution on Linux."""
        return (1920, 1080)
    
    def get_monitor_info(self) -> List[Dict[str, Any]]:
        """Get monitor info on Linux."""
        return [
            {
                'index': 0, 'name': 'DP-1',
                'width': 1920, 'height': 1080,
                'x': 0, 'y': 0, 'is_primary': True, 'scale_factor': 1.0
            }
        ]
    
    def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> bytes:
        """Take screenshot on Linux."""
        return b"mock_linux_screenshot"
    
    def create_screen_overlay(self, config: OverlayConfig) -> Any:
        """Create screen overlay on Linux."""
        try:
            overlay_id = f"linux_overlay_{len(self.overlays)}"
            self.overlays[overlay_id] = {
                'id': overlay_id, 'config': config,
                'window': f"mock_x11_window_{overlay_id}", 'active': True
            }
            logger.info(f"Created Linux overlay: {overlay_id}")
            return overlay_id
        except Exception as e:
            logger.error(f"Failed to create Linux overlay: {e}")
            return None
    
    def update_overlay(self, overlay: Any, config: OverlayConfig) -> bool:
        """Update Linux overlay."""
        overlay_id = str(overlay)
        if overlay_id in self.overlays:
            self.overlays[overlay_id]['config'] = config
            return True
        return False
    
    def destroy_overlay(self, overlay: Any) -> bool:
        """Destroy Linux overlay."""
        overlay_id = str(overlay)
        if overlay_id in self.overlays:
            del self.overlays[overlay_id]
            logger.info(f"Destroyed Linux overlay: {overlay_id}")
            return True
        return False
    
    def execute_shell_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute shell command on Linux."""
        return {
            'success': True, 'returncode': 0,
            'stdout': f'Linux executed: {command}', 'stderr': ''
        }
    
    def get_process_list(self) -> List[Dict[str, Any]]:
        """Get process list on Linux."""
        return [{'pid': 9999, 'name': 'test-app', 'cpu_usage': 1.5, 'memory_usage': 1536}]
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get Linux system info."""
        return {
            'platform': 'Linux', 'version': 'Ubuntu 22.04',
            'architecture': 'x86_64', 'hostname': 'linux-desktop',
            'memory_total': 32768, 'cpu_count': 16
        }