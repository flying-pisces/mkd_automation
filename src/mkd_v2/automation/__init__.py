"""
UI Automation and Element Detection for MKD Automation Platform v2.

Provides cross-platform UI automation capabilities:
- Element detection and identification
- Window hierarchy traversal
- UI interaction primitives
- Screen coordinate mapping
- Intelligent context-aware automation (Week 3)
"""

from .element_detector import ElementDetector, UIElementInfo, DetectionResult
from .window_manager import WindowManager, WindowInfo
from .automation_engine import AutomationEngine
from .intelligent_automation import IntelligentAutomationEngine

__all__ = [
    "ElementDetector", "UIElementInfo", "DetectionResult",
    "WindowManager", "WindowInfo", 
    "AutomationEngine",
    "IntelligentAutomationEngine"
]