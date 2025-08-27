"""
Recording components for MKD Automation Platform v2.0.

This module contains components for capturing and processing user interactions:
- RecordingEngine: Main recording controller
- InputCapturer: Cross-platform input capture
- EventProcessor: Event filtering and processing
"""

from .recording_engine import RecordingEngine, RecordingEvent, RecordingState
from .input_capturer import InputCapturer
from .event_processor import EventProcessor

__all__ = ["RecordingEngine", "RecordingEvent", "RecordingState", "InputCapturer", "EventProcessor"]