"""
Linux Platform Implementation - Updated for visual overlay support.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Callable

from mkd.platforms.base import BasePlatform

logger = logging.getLogger(__name__)


class LinuxPlatform(BasePlatform):
    """Linux-specific implementation with overlay support."""
    
    def __init__(self):
        super().__init__()
        self.name = "Linux"
        self.overlays = {}

    def start_capture(self, on_event):
        """Starts capturing input events."""
        # TODO: Implement using pynput
        print("Starting capture on Linux")

    def stop_capture(self):
        """Stops capturing input events."""
        # TODO: Implement using pynput
        print("Stopping capture on Linux")

    def execute_action(self, action):
        """Executes a single action."""
        # TODO: Implement using pynput
        print(f"Executing action on Linux: {action}")
    
    def create_screen_overlay(self, config) -> Any:
        """Create screen overlay on Linux."""
        try:
            overlay_id = f"overlay_{len(self.overlays)}"
            
            overlay_info = {
                'id': overlay_id,
                'config': config.__dict__ if hasattr(config, '__dict__') else config,
                'window': f"mock_window_{overlay_id}",
                'active': True
            }
            
            self.overlays[overlay_id] = overlay_info
            logger.info(f"Created screen overlay: {overlay_id}")
            return overlay_id
            
        except Exception as e:
            logger.error(f"Failed to create screen overlay: {e}")
            return None
    
    def update_overlay(self, overlay: Any, config) -> bool:
        """Update existing overlay."""
        try:
            overlay_id = str(overlay)
            if overlay_id not in self.overlays:
                return False
            
            self.overlays[overlay_id]['config'] = config.__dict__ if hasattr(config, '__dict__') else config
            logger.info(f"Updated overlay: {overlay_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update overlay: {e}")
            return False
    
    def destroy_overlay(self, overlay: Any) -> bool:
        """Destroy screen overlay."""
        try:
            overlay_id = str(overlay)
            if overlay_id in self.overlays:
                del self.overlays[overlay_id]
                logger.info(f"Destroyed overlay: {overlay_id}")
                return True
            return False
                
        except Exception as e:
            logger.error(f"Failed to destroy overlay: {e}")
            return False
    
    def get_monitor_info(self) -> List[Dict[str, Any]]:
        """Get monitor information."""
        return [
            {
                'index': 0,
                'name': 'Primary Monitor',
                'width': 1920,
                'height': 1080,
                'x': 0,
                'y': 0,
                'is_primary': True,
                'scale_factor': 1.0
            }
        ]
