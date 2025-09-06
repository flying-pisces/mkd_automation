"""
Browser automation module for MKD Automation.

This module provides browser control and automation capabilities,
allowing MKD to interact with web applications directly.
"""

from .controller import BrowserController
from .actions import BrowserAction, BrowserActionType
from .recorder import BrowserRecorder

__all__ = [
    'BrowserController',
    'BrowserAction',
    'BrowserActionType',
    'BrowserRecorder',
]