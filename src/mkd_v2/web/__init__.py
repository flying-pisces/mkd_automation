"""
MKD Web Enhancement Module

Provides advanced web automation capabilities:
- Deep DOM inspection and manipulation
- Browser automation and management
- Multi-tab coordination and management
- JavaScript injection and custom scripting
- Unified web automation engine
"""

from .dom_inspector import DOMInspector, ElementInfo, DOMQuery, DetectionStrategy
from .browser_controller import BrowserController, BrowserSession, TabManager, BrowserType
from .javascript_injector import JavaScriptInjector, ScriptResult, ScriptContext, ScriptType
from .web_automation_engine import WebAutomationEngine, WebAction, WebWorkflow, InteractionMode

__all__ = [
    'DOMInspector',
    'ElementInfo',
    'DOMQuery',
    'DetectionStrategy',
    'BrowserController', 
    'BrowserSession',
    'TabManager',
    'BrowserType',
    'JavaScriptInjector',
    'ScriptResult',
    'ScriptContext',
    'ScriptType',
    'WebAutomationEngine',
    'WebAction',
    'WebWorkflow',
    'InteractionMode'
]