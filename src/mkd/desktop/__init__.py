"""
Desktop automation module for MKD Automation.

This module provides comprehensive desktop automation capabilities including:
- Mouse and keyboard control
- Window management
- Application launching
- File system operations
- Command prompt automation
- Screen capture and OCR
- System integration
"""

from .controller import DesktopController
from .actions import DesktopAction, DesktopActionType
from .windows_automation import WindowsDesktopAutomation
from .application_manager import ApplicationManager
from .file_operations import FileOperations

__all__ = [
    'DesktopController',
    'DesktopAction',
    'DesktopActionType',
    'WindowsDesktopAutomation',
    'ApplicationManager',
    'FileOperations',
]