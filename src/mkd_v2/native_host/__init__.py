"""
Native Messaging Host for Chrome Extension Communication.

This module provides the native messaging host that allows the Chrome extension
to communicate with the Python backend.
"""

from .host import NativeHost
from .installer import NativeHostInstaller

__all__ = ["NativeHost", "NativeHostInstaller"]