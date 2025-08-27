"""
Platform abstraction layer for MKD Automation Platform v2.0.

This module provides cross-platform support for:
- Platform detection
- Input capture (mouse, keyboard)
- UI automation
- Screen recording
- System integration
"""

from .detector import PlatformDetector
from .base import PlatformInterface

__all__ = ["PlatformDetector", "PlatformInterface"]