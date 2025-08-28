"""
MKD Intelligence Module

Provides intelligent context detection and analysis for automation.
Includes context detection, pattern analysis, and smart recording decisions.
"""

from .context_detector import ContextDetector, ApplicationContext
from .pattern_analyzer import PatternAnalyzer, UserPattern
from .smart_recorder import SmartRecorder, RecordingDecision

__all__ = [
    'ContextDetector',
    'ApplicationContext', 
    'PatternAnalyzer',
    'UserPattern',
    'SmartRecorder',
    'RecordingDecision'
]