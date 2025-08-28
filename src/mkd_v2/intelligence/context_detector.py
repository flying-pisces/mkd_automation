#!/usr/bin/env python3
"""
Context Detection System

Provides intelligent application context detection and UI state analysis.
Understands application types, UI patterns, and context switching events.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

from ..platform.base import PlatformInterface, WindowInfo


logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Types of application contexts."""
    UNKNOWN = "unknown"
    WEB_BROWSER = "web_browser"
    TEXT_EDITOR = "text_editor"
    TERMINAL = "terminal"
    FILE_MANAGER = "file_manager"
    MEDIA_PLAYER = "media_player"
    COMMUNICATION = "communication"
    DEVELOPMENT_IDE = "development_ide"
    SYSTEM_UTILITY = "system_utility"
    GAME = "game"


class UIState(Enum):
    """UI state classifications."""
    UNKNOWN = "unknown"
    IDLE = "idle"
    LOADING = "loading"
    MODAL_DIALOG = "modal_dialog"
    FORM_INPUT = "form_input"
    MENU_OPEN = "menu_open"
    CONTEXT_MENU = "context_menu"
    DRAG_DROP = "drag_drop"
    FULLSCREEN = "fullscreen"


@dataclass
class ApplicationContext:
    """Represents the current application context."""
    app_name: str
    process_name: str
    window_title: str
    context_type: ContextType
    ui_state: UIState
    window_bounds: Dict[str, int]
    
    # Context metadata
    confidence: float = 0.0
    detection_time: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # UI Elements detected
    ui_elements: List[Dict[str, Any]] = field(default_factory=list)
    active_element: Optional[Dict[str, Any]] = None
    
    # Context history
    previous_context: Optional['ApplicationContext'] = None
    context_switches: int = 0


@dataclass
class ContextChangeEvent:
    """Represents a context change event."""
    timestamp: float
    previous_context: Optional[ApplicationContext]
    new_context: ApplicationContext
    change_type: str  # "app_switch", "window_change", "ui_state_change"
    significance: float  # 0.0-1.0, how significant this change is


class ContextDetector:
    """
    Intelligent context detection system.
    
    Analyzes active applications, UI states, and context transitions
    to provide intelligent automation decisions.
    """
    
    def __init__(self, platform: PlatformInterface):
        self.platform = platform
        self.current_context: Optional[ApplicationContext] = None
        self.context_history: List[ApplicationContext] = []
        self.change_listeners: List[callable] = []
        
        # Detection patterns
        self.app_patterns: Dict[str, ContextType] = {}
        self.ui_patterns: Dict[str, UIState] = {}
        self.detection_cache: Dict[str, ApplicationContext] = {}
        
        # Performance tracking
        self.detection_stats = {
            'detections': 0,
            'cache_hits': 0,
            'avg_detection_time': 0.0,
            'confidence_scores': []
        }
        
        self._initialize_patterns()
        logger.info("Context detector initialized")
    
    def _initialize_patterns(self):
        """Initialize application and UI detection patterns."""
        # Common application patterns
        self.app_patterns.update({
            'chrome': ContextType.WEB_BROWSER,
            'firefox': ContextType.WEB_BROWSER,
            'safari': ContextType.WEB_BROWSER,
            'edge': ContextType.WEB_BROWSER,
            'code': ContextType.DEVELOPMENT_IDE,
            'vscode': ContextType.DEVELOPMENT_IDE,
            'pycharm': ContextType.DEVELOPMENT_IDE,
            'terminal': ContextType.TERMINAL,
            'iterm': ContextType.TERMINAL,
            'finder': ContextType.FILE_MANAGER,
            'explorer': ContextType.FILE_MANAGER,
            'notepad': ContextType.TEXT_EDITOR,
            'textedit': ContextType.TEXT_EDITOR,
            'slack': ContextType.COMMUNICATION,
            'discord': ContextType.COMMUNICATION,
            'teams': ContextType.COMMUNICATION,
            'zoom': ContextType.COMMUNICATION
        })
        
        # UI state detection patterns
        self.ui_patterns.update({
            'loading': UIState.LOADING,
            'please wait': UIState.LOADING,
            'processing': UIState.LOADING,
            'dialog': UIState.MODAL_DIALOG,
            'alert': UIState.MODAL_DIALOG,
            'confirm': UIState.MODAL_DIALOG,
            'menu': UIState.MENU_OPEN,
            'context menu': UIState.CONTEXT_MENU,
            'fullscreen': UIState.FULLSCREEN
        })
    
    def detect_current_context(self, force_refresh: bool = False) -> ApplicationContext:
        """
        Detect the current application context.
        
        Args:
            force_refresh: Force fresh detection, skip cache
            
        Returns:
            Current application context
        """
        start_time = time.time()
        
        try:
            # Get active window information
            active_window = self.platform.get_active_window_info()
            
            if not active_window:
                return self._create_unknown_context()
            
            # Check cache first  
            cache_key = f"{active_window.process_name}:{active_window.pid}"
            if not force_refresh and cache_key in self.detection_cache:
                cached_context = self.detection_cache[cache_key]
                # Use cache if recent (within 5 seconds)
                if time.time() - cached_context.detection_time < 5.0:
                    self.detection_stats['cache_hits'] += 1
                    return cached_context
            
            # Perform fresh detection
            context = self._detect_context_from_window(active_window)
            
            # Update cache
            self.detection_cache[cache_key] = context
            
            # Update statistics
            detection_time = time.time() - start_time
            self._update_detection_stats(detection_time, context.confidence)
            
            # Check for context change
            if self.current_context and self._is_context_change(self.current_context, context):
                self._handle_context_change(self.current_context, context)
            
            self.current_context = context
            return context
            
        except Exception as e:
            logger.error(f"Context detection failed: {e}")
            return self._create_unknown_context()
    
    def _detect_context_from_window(self, window: WindowInfo) -> ApplicationContext:
        """Detect context from window information."""
        # Determine context type
        context_type = self._classify_application(window.process_name, window.title)
        
        # Analyze UI state
        ui_state = self._analyze_ui_state(window)
        
        # Get window bounds
        bounds = {
            'x': window.x,
            'y': window.y, 
            'width': window.width,
            'height': window.height
        }
        
        # Calculate confidence
        confidence = self._calculate_confidence(context_type, ui_state, window)
        
        # Detect UI elements (basic implementation)
        ui_elements = self._detect_ui_elements(window)
        
        # Create context
        context = ApplicationContext(
            app_name=window.title.split(' - ')[-1] if ' - ' in window.title else window.process_name,
            process_name=window.process_name,
            window_title=window.title,
            context_type=context_type,
            ui_state=ui_state,
            window_bounds=bounds,
            confidence=confidence,
            ui_elements=ui_elements,
            metadata={
                'process_id': window.pid,
                'is_active': window.is_active
            }
        )
        
        return context
    
    def _classify_application(self, process_name: str, window_title: str) -> ContextType:
        """Classify application based on process name and window title."""
        process_lower = process_name.lower()
        title_lower = window_title.lower()
        
        # Check exact matches first
        for pattern, context_type in self.app_patterns.items():
            if pattern in process_lower:
                return context_type
        
        # Check window title patterns
        if any(browser in title_lower for browser in ['http', 'www', 'chrome', 'firefox']):
            return ContextType.WEB_BROWSER
        
        if any(code in title_lower for code in ['code', 'editor', '.py', '.js', '.html']):
            return ContextType.DEVELOPMENT_IDE
        
        if any(term in title_lower for term in ['terminal', 'command', 'shell', 'bash']):
            return ContextType.TERMINAL
        
        return ContextType.UNKNOWN
    
    def _analyze_ui_state(self, window: WindowInfo) -> UIState:
        """Analyze current UI state from window information."""
        title_lower = window.title.lower()
        
        # Check for common UI state indicators
        for pattern, state in self.ui_patterns.items():
            if pattern in title_lower:
                return state
        
        # Default states based on context
        if window.width < 400 or window.height < 300:
            return UIState.MODAL_DIALOG
        
        return UIState.IDLE
    
    def _detect_ui_elements(self, window: WindowInfo) -> List[Dict[str, Any]]:
        """Detect UI elements in the current window (basic implementation)."""
        elements = []
        
        # This would integrate with element detector in a full implementation
        # For now, return basic window information as an element
        elements.append({
            'type': 'window',
            'bounds': {'x': window.x, 'y': window.y, 'width': window.width, 'height': window.height},
            'title': window.title,
            'confidence': 1.0
        })
        
        return elements
    
    def _calculate_confidence(self, context_type: ContextType, ui_state: UIState, window: WindowInfo) -> float:
        """Calculate detection confidence score."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence for known applications
        if context_type != ContextType.UNKNOWN:
            confidence += 0.3
        
        # Increase confidence for clear UI states
        if ui_state != UIState.UNKNOWN:
            confidence += 0.2
        
        # Window title quality
        if window.title and len(window.title) > 10:
            confidence += 0.1
        
        # Process name quality
        if window.process_name and window.process_name != 'unknown':
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _is_context_change(self, old_context: ApplicationContext, new_context: ApplicationContext) -> bool:
        """Check if context has significantly changed."""
        return (
            old_context.process_name != new_context.process_name or
            old_context.context_type != new_context.context_type or
            old_context.ui_state != new_context.ui_state or
            old_context.window_title != new_context.window_title
        )
    
    def _handle_context_change(self, old_context: ApplicationContext, new_context: ApplicationContext):
        """Handle context change event."""
        # Determine change type
        change_type = "ui_state_change"
        if old_context.process_name != new_context.process_name:
            change_type = "app_switch"
        elif old_context.window_title != new_context.window_title:
            change_type = "window_change"
        
        # Calculate significance
        significance = self._calculate_change_significance(old_context, new_context)
        
        # Create change event
        event = ContextChangeEvent(
            timestamp=time.time(),
            previous_context=old_context,
            new_context=new_context,
            change_type=change_type,
            significance=significance
        )
        
        # Update context history
        new_context.previous_context = old_context
        new_context.context_switches = old_context.context_switches + 1
        self.context_history.append(old_context)
        
        # Notify listeners
        self._notify_change_listeners(event)
        
        logger.info(f"Context change: {change_type} ({significance:.2f} significance)")
    
    def _calculate_change_significance(self, old_context: ApplicationContext, new_context: ApplicationContext) -> float:
        """Calculate how significant a context change is."""
        significance = 0.0
        
        # Application change is most significant
        if old_context.process_name != new_context.process_name:
            significance += 0.5
        
        # Context type change
        if old_context.context_type != new_context.context_type:
            significance += 0.3
        
        # UI state change
        if old_context.ui_state != new_context.ui_state:
            significance += 0.2
        
        # Window change within same app
        if old_context.window_title != new_context.window_title:
            significance += 0.1
        
        return min(significance, 1.0)
    
    def _notify_change_listeners(self, event: ContextChangeEvent):
        """Notify registered change listeners."""
        for listener in self.change_listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Context change listener error: {e}")
    
    def _update_detection_stats(self, detection_time: float, confidence: float):
        """Update detection statistics."""
        self.detection_stats['detections'] += 1
        
        # Update average detection time
        count = self.detection_stats['detections']
        current_avg = self.detection_stats['avg_detection_time']
        self.detection_stats['avg_detection_time'] = (current_avg * (count - 1) + detection_time) / count
        
        # Track confidence scores
        self.detection_stats['confidence_scores'].append(confidence)
        if len(self.detection_stats['confidence_scores']) > 100:
            self.detection_stats['confidence_scores'] = self.detection_stats['confidence_scores'][-100:]
    
    def _create_unknown_context(self) -> ApplicationContext:
        """Create a context for unknown/error states."""
        return ApplicationContext(
            app_name="Unknown",
            process_name="unknown",
            window_title="Unknown Window",
            context_type=ContextType.UNKNOWN,
            ui_state=UIState.UNKNOWN,
            window_bounds={'x': 0, 'y': 0, 'width': 0, 'height': 0},
            confidence=0.0
        )
    
    def add_change_listener(self, listener: callable):
        """Add a context change listener."""
        self.change_listeners.append(listener)
    
    def remove_change_listener(self, listener: callable):
        """Remove a context change listener."""
        if listener in self.change_listeners:
            self.change_listeners.remove(listener)
    
    def get_context_history(self, limit: int = 10) -> List[ApplicationContext]:
        """Get recent context history."""
        return self.context_history[-limit:]
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get detection performance statistics."""
        stats = self.detection_stats.copy()
        if stats['confidence_scores']:
            stats['avg_confidence'] = sum(stats['confidence_scores']) / len(stats['confidence_scores'])
        else:
            stats['avg_confidence'] = 0.0
        return stats
    
    def is_context_stable(self, duration: float = 2.0) -> bool:
        """Check if context has been stable for given duration."""
        if not self.current_context:
            return False
        
        return time.time() - self.current_context.detection_time >= duration
    
    def should_trigger_recording(self) -> bool:
        """Determine if current context should trigger recording."""
        if not self.current_context:
            return False
        
        # Don't record in system utilities or unknown contexts
        if self.current_context.context_type in [ContextType.SYSTEM_UTILITY, ContextType.UNKNOWN]:
            return False
        
        # Don't record during loading states
        if self.current_context.ui_state == UIState.LOADING:
            return False
        
        # Require minimum confidence
        if self.current_context.confidence < 0.6:
            return False
        
        return True
    
    def cleanup(self):
        """Clean up detector resources."""
        self.detection_cache.clear()
        self.change_listeners.clear()
        logger.info("Context detector cleaned up")