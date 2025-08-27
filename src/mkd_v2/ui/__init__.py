"""
UI components for MKD Automation Platform v2.0.

This module contains user interface components:
- ScreenOverlay: Visual recording indicators
- Platform-specific UI implementations
"""

from .overlay import ScreenOverlay, BorderConfig, TimerConfig

__all__ = ["ScreenOverlay", "BorderConfig", "TimerConfig"]