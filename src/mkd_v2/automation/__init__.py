"""
UI Automation and Element Detection for MKD Automation Platform v2.

Provides cross-platform UI automation capabilities:
- Element detection and identification
- Window hierarchy traversal
- UI interaction primitives
- Screen coordinate mapping
"""

from .element_detector import ElementDetector, UIElementInfo, DetectionResult
from .window_manager import WindowManager, WindowInfo
from .automation_engine import AutomationEngine

__all__ = [
    "ElementDetector", "UIElementInfo", "DetectionResult",
    "WindowManager", "WindowInfo", 
    "AutomationEngine"
]