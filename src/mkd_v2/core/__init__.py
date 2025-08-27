"""
Core components for MKD Automation Platform v2.0.

This module contains the foundational components:
- MessageBroker: Central communication hub
- SessionManager: Recording session state management
"""

from .message_broker import MessageBroker
from .session_manager import SessionManager

__all__ = ["MessageBroker", "SessionManager"]