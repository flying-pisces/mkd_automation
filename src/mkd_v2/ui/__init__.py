"""
UI components for MKD Automation Platform v2.0.

This module contains user interface components:
- ScreenOverlay: Visual recording indicators  
- OverlayRenderer: Cross-platform visual overlay rendering
- Platform-specific UI implementations
"""

from .overlay import ScreenOverlay, BorderConfig, TimerConfig
from .overlay_renderer import OverlayRenderer, get_overlay_manager, create_overlay_renderer

__all__ = [
    "ScreenOverlay", "BorderConfig", "TimerConfig",
    "OverlayRenderer", "get_overlay_manager", "create_overlay_renderer"
]