"""
MKD Automation Platform v2.0

A modern Chrome extension-integrated automation platform for capturing,
analyzing, and reproducing user interactions across desktop applications.

This module provides:
- Chrome extension integration via native messaging
- Intelligent context-aware recording
- Cross-platform input simulation
- Visual feedback and monitoring
- Secure user authentication and role management
"""

__version__ = "2.0.0"
__author__ = "MKD Automation Team"

# Core components
from .core.message_broker import MessageBroker
from .core.session_manager import SessionManager

# Platform detection
from .platform.detector import PlatformDetector

# Recording components
from .recording.recording_engine import RecordingEngine

__all__ = [
    "MessageBroker",
    "SessionManager", 
    "PlatformDetector",
    "RecordingEngine",
    "__version__",
]