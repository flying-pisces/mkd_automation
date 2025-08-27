"""
Input Capturer - Cross-platform input event capture.

Handles keyboard and mouse event capture using platform-specific
implementations with unified event format.
"""

import logging
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from ..platform.base import PlatformInterface

logger = logging.getLogger(__name__)


class CaptureState(Enum):
    """Input capture states."""
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class InputEvent:
    """Standardized input event."""
    timestamp: float
    event_type: str  # mouse_click, mouse_move, key_press, key_release
    source: str  # mouse, keyboard
    data: Dict[str, Any]


class InputCapturer:
    """
    Cross-platform input event capturer.
    
    Features:
    - Mouse and keyboard event capture
    - Platform abstraction
    - Event filtering and throttling
    - Pause/resume functionality
    """
    
    def __init__(self, platform: PlatformInterface):
        self.platform = platform
        self.state = CaptureState.IDLE
        self.callback: Optional[Callable] = None
        
        # Event filtering
        self.filter_duplicates = True
        self.mouse_move_threshold = 5  # pixels
        self.last_mouse_position = (0, 0)
        self.last_event_time = 0
        self.min_event_interval = 0.01  # 10ms
        
        # Threading
        self._lock = threading.RLock()
        self._capture_thread: Optional[threading.Thread] = None
        
        # Statistics
        self.stats = {
            'events_captured': 0,
            'events_filtered': 0,
            'mouse_events': 0,
            'keyboard_events': 0
        }
        
        logger.info("InputCapturer initialized")
    
    def initialize(self):
        """Initialize input capturer."""
        try:
            logger.info("Initializing input capturer")
            # Platform-specific initialization handled by platform
            return True
        except Exception as e:
            logger.error(f"Failed to initialize input capturer: {e}")
            raise
    
    def start_capture(self, callback: Callable):
        """
        Start input capture.
        
        Args:
            callback: Function to call with captured events
        """
        with self._lock:
            if self.state != CaptureState.IDLE:
                raise RuntimeError(f"Cannot start capture: state is {self.state}")
            
            self.callback = callback
            
            try:
                # Start platform-specific input capture
                success = self.platform.start_input_capture(self._handle_raw_event)
                if not success:
                    raise RuntimeError("Platform input capture failed to start")
                
                self.state = CaptureState.ACTIVE
                logger.info("Input capture started")
                
            except Exception as e:
                logger.error(f"Failed to start input capture: {e}")
                self.state = CaptureState.ERROR
                raise
    
    def stop_capture(self):
        """Stop input capture."""
        with self._lock:
            if self.state not in [CaptureState.ACTIVE, CaptureState.PAUSED]:
                return
            
            try:
                # Stop platform-specific capture
                self.platform.stop_input_capture()
                
                self.state = CaptureState.IDLE
                self.callback = None
                
                logger.info("Input capture stopped")
                
            except Exception as e:
                logger.error(f"Failed to stop input capture: {e}")
                self.state = CaptureState.ERROR
                raise
    
    def pause(self):
        """Pause input capture."""
        with self._lock:
            if self.state != CaptureState.ACTIVE:
                raise RuntimeError("No active capture to pause")
            
            self.state = CaptureState.PAUSED
            logger.info("Input capture paused")
    
    def resume(self):
        """Resume input capture."""
        with self._lock:
            if self.state != CaptureState.PAUSED:
                raise RuntimeError("No paused capture to resume")
            
            self.state = CaptureState.ACTIVE
            logger.info("Input capture resumed")
    
    def _handle_raw_event(self, raw_event: Dict[str, Any]):
        """
        Handle raw event from platform.
        
        Args:
            raw_event: Raw event data from platform
        """
        if self.state != CaptureState.ACTIVE:
            return
        
        try:
            # Update statistics
            self.stats['events_captured'] += 1
            
            # Apply filtering
            if self._should_filter_event(raw_event):
                self.stats['events_filtered'] += 1
                return
            
            # Convert to standardized format
            input_event = self._standardize_event(raw_event)
            if not input_event:
                return
            
            # Update event-specific statistics
            if input_event.source == 'mouse':
                self.stats['mouse_events'] += 1
            elif input_event.source == 'keyboard':
                self.stats['keyboard_events'] += 1
            
            # Call callback with event
            if self.callback:
                event_dict = {
                    'timestamp': input_event.timestamp,
                    'type': input_event.event_type,
                    'source': input_event.source,
                    'data': input_event.data
                }
                self.callback(event_dict)
                
        except Exception as e:
            logger.error(f"Error handling input event: {e}")
    
    def _should_filter_event(self, raw_event: Dict[str, Any]) -> bool:
        """
        Check if event should be filtered.
        
        Args:
            raw_event: Raw event data
            
        Returns:
            True if event should be filtered
        """
        current_time = time.time()
        
        # Time-based throttling
        if current_time - self.last_event_time < self.min_event_interval:
            return True
        
        # Mouse move filtering
        if raw_event.get('type') == 'mouse_move':
            x = raw_event.get('x', 0)
            y = raw_event.get('y', 0)
            
            # Check movement threshold
            dx = abs(x - self.last_mouse_position[0])
            dy = abs(y - self.last_mouse_position[1])
            
            if dx < self.mouse_move_threshold and dy < self.mouse_move_threshold:
                return True
            
            self.last_mouse_position = (x, y)
        
        self.last_event_time = current_time
        return False
    
    def _standardize_event(self, raw_event: Dict[str, Any]) -> Optional[InputEvent]:
        """
        Convert raw platform event to standardized format.
        
        Args:
            raw_event: Raw event from platform
            
        Returns:
            Standardized InputEvent or None
        """
        try:
            event_type = raw_event.get('type', '')
            timestamp = raw_event.get('timestamp', time.time())
            
            # Determine source and standardize data
            if event_type.startswith('mouse'):
                source = 'mouse'
                data = {
                    'x': raw_event.get('x', 0),
                    'y': raw_event.get('y', 0),
                    'button': raw_event.get('button'),
                    'scroll_delta': raw_event.get('scroll_delta'),
                    'pressed': raw_event.get('pressed', False)
                }
            elif event_type.startswith('key'):
                source = 'keyboard'
                data = {
                    'key': raw_event.get('key'),
                    'char': raw_event.get('char'),
                    'modifiers': raw_event.get('modifiers', []),
                    'pressed': raw_event.get('pressed', False)
                }
            else:
                logger.warning(f"Unknown event type: {event_type}")
                return None
            
            return InputEvent(
                timestamp=timestamp,
                event_type=event_type,
                source=source,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Failed to standardize event: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get capture statistics."""
        with self._lock:
            return {
                'state': self.state.value,
                'stats': self.stats.copy(),
                'filter_settings': {
                    'filter_duplicates': self.filter_duplicates,
                    'mouse_move_threshold': self.mouse_move_threshold,
                    'min_event_interval': self.min_event_interval
                }
            }
    
    def cleanup(self):
        """Clean up input capturer resources."""
        logger.info("Cleaning up InputCapturer")
        
        try:
            if self.state in [CaptureState.ACTIVE, CaptureState.PAUSED]:
                self.stop_capture()
        except Exception as e:
            logger.error(f"Error stopping capture during cleanup: {e}")
        
        logger.info("InputCapturer cleanup complete")