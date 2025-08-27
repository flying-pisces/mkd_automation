"""
UI Automation Engine - High-level automation orchestration.

Coordinates element detection, window management, and user interactions
to provide intelligent UI automation capabilities.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass

from .element_detector import ElementDetector, UIElementInfo, DetectionResult, create_element_detector
from .window_manager import WindowManager, WindowInfo, create_window_manager
from ..platform.base import PlatformInterface

logger = logging.getLogger(__name__)


@dataclass
class AutomationContext:
    """Context information for automation operations."""
    target_window: Optional[WindowInfo] = None
    screenshot: Optional[bytes] = None
    detected_elements: List[UIElementInfo] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if self.detected_elements is None:
            self.detected_elements = []


class AutomationEngine:
    """
    High-level UI automation engine.
    
    Provides intelligent automation capabilities by combining:
    - Element detection and recognition
    - Window management and focus
    - Context-aware interactions
    - Smart waiting and retries
    """
    
    def __init__(self, platform: PlatformInterface):
        self.platform = platform
        self.window_manager = create_window_manager()
        self.element_detector = create_element_detector(
            screenshot_func=self.platform.take_screenshot
        )
        
        # Automation state
        self.current_context: Optional[AutomationContext] = None
        self.operation_history: List[Dict[str, Any]] = []
        
        # Configuration
        self.default_timeout = 10.0  # seconds
        self.retry_interval = 0.5    # seconds
        self.element_confidence_threshold = 0.5
        
        logger.info("AutomationEngine initialized")
    
    def click_element_by_text(self, text: str, fuzzy: bool = True, timeout: float = None) -> bool:
        """
        Click on an element containing specific text.
        
        Args:
            text: Text to search for in elements
            fuzzy: Whether to use fuzzy text matching
            timeout: Maximum time to wait for element (uses default if None)
            
        Returns:
            True if element was found and clicked successfully
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        logger.info(f"Attempting to click element with text: '{text}'")
        
        while time.time() - start_time < timeout:
            try:
                # Update context
                self._update_automation_context()
                
                # Find element by text
                element = self.element_detector.find_element_by_text(text, fuzzy=fuzzy)
                
                if element and element.confidence >= self.element_confidence_threshold:
                    # Click on the element
                    success = self._click_element(element)
                    
                    # Record operation
                    self._record_operation({
                        'action': 'click_by_text',
                        'text': text,
                        'element': element,
                        'success': success,
                        'timestamp': time.time()
                    })
                    
                    if success:
                        logger.info(f"Successfully clicked element: '{text}'")
                        return True
                    else:
                        logger.warning(f"Failed to click element: '{text}'")
                
                # Wait before retry
                time.sleep(self.retry_interval)
                
            except Exception as e:
                logger.error(f"Error during click_element_by_text: {e}")
                time.sleep(self.retry_interval)
        
        logger.error(f"Timeout waiting for element with text: '{text}'")
        return False
    
    def click_at_coordinates(self, x: int, y: int, button: str = "left") -> bool:
        """
        Click at specific screen coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button to click (left, right, middle)
            
        Returns:
            True if click was executed successfully
        """
        try:
            from ..platform.base import MouseAction
            
            # Create mouse action
            action = MouseAction(
                action="click",
                x=x, y=y,
                button=button
            )
            
            # Execute click
            success = self.platform.execute_mouse_action(action)
            
            # Record operation
            self._record_operation({
                'action': 'click_coordinates',
                'coordinates': (x, y),
                'button': button,
                'success': success,
                'timestamp': time.time()
            })
            
            if success:
                logger.info(f"Successfully clicked at ({x}, {y})")
            else:
                logger.error(f"Failed to click at ({x}, {y})")
            
            return success
            
        except Exception as e:
            logger.error(f"Error during click_at_coordinates: {e}")
            return False
    
    def type_text(self, text: str, clear_first: bool = False) -> bool:
        """
        Type text using keyboard input.
        
        Args:
            text: Text to type
            clear_first: Whether to clear existing text first (Cmd+A, Delete)
            
        Returns:
            True if text was typed successfully
        """
        try:
            from ..platform.base import KeyboardAction
            
            success = True
            
            # Clear existing text if requested
            if clear_first:
                # Select all (Cmd+A on macOS, Ctrl+A on others)
                if self.platform.name == "macOS":
                    select_all = KeyboardAction(action="key_combination", keys=["cmd", "a"])
                else:
                    select_all = KeyboardAction(action="key_combination", keys=["ctrl", "a"])
                
                success &= self.platform.execute_keyboard_action(select_all)
                
                # Delete selected text
                delete_action = KeyboardAction(action="press", key="Delete")
                success &= self.platform.execute_keyboard_action(delete_action)
            
            # Type the text
            if success:
                type_action = KeyboardAction(action="type", text=text)
                success = self.platform.execute_keyboard_action(type_action)
            
            # Record operation
            self._record_operation({
                'action': 'type_text',
                'text': text,
                'clear_first': clear_first,
                'success': success,
                'timestamp': time.time()
            })
            
            if success:
                logger.info(f"Successfully typed text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            else:
                logger.error("Failed to type text")
            
            return success
            
        except Exception as e:
            logger.error(f"Error during type_text: {e}")
            return False
    
    def wait_for_element_by_text(self, text: str, timeout: float = None) -> Optional[UIElementInfo]:
        """
        Wait for an element containing specific text to appear.
        
        Args:
            text: Text to search for
            timeout: Maximum time to wait
            
        Returns:
            UIElementInfo if found, None if timeout
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        logger.info(f"Waiting for element with text: '{text}'")
        
        while time.time() - start_time < timeout:
            try:
                # Update context
                self._update_automation_context()
                
                # Search for element
                element = self.element_detector.find_element_by_text(text, fuzzy=True)
                
                if element and element.confidence >= self.element_confidence_threshold:
                    logger.info(f"Found element with text: '{text}'")
                    return element
                
                # Wait before retry
                time.sleep(self.retry_interval)
                
            except Exception as e:
                logger.error(f"Error while waiting for element: {e}")
                time.sleep(self.retry_interval)
        
        logger.error(f"Timeout waiting for element with text: '{text}'")
        return None
    
    def focus_window_by_title(self, title: str, partial: bool = True) -> bool:
        """
        Focus window containing specific title text.
        
        Args:
            title: Window title to search for
            partial: Whether to match partial title
            
        Returns:
            True if window was found and focused
        """
        try:
            # Get all windows
            windows = self.window_manager.get_window_list()
            
            # Search for matching window
            target_window = None
            search_title = title.lower()
            
            for window in windows:
                window_title = window.title.lower()
                
                if partial and search_title in window_title:
                    target_window = window
                    break
                elif not partial and window_title == search_title:
                    target_window = window
                    break
            
            if target_window:
                success = self.window_manager.focus_window(target_window.window_id)
                
                # Record operation
                self._record_operation({
                    'action': 'focus_window',
                    'title': title,
                    'window': target_window,
                    'success': success,
                    'timestamp': time.time()
                })
                
                if success:
                    logger.info(f"Successfully focused window: '{target_window.title}'")
                    # Update context with new active window
                    self.current_context = AutomationContext(target_window=target_window)
                    return True
                else:
                    logger.error(f"Failed to focus window: '{target_window.title}'")
            else:
                logger.error(f"Window not found with title: '{title}'")
            
            return False
            
        except Exception as e:
            logger.error(f"Error during focus_window_by_title: {e}")
            return False
    
    def get_elements_in_region(self, x: int, y: int, width: int, height: int) -> List[UIElementInfo]:
        """
        Get all UI elements in a specific screen region.
        
        Args:
            x: Region X coordinate
            y: Region Y coordinate
            width: Region width
            height: Region height
            
        Returns:
            List of detected UI elements
        """
        try:
            # Update context
            self._update_automation_context()
            
            # Detect elements in region
            result = self.element_detector.detect_elements_in_region(x, y, width, height)
            
            if result.success:
                # Filter by confidence threshold
                filtered_elements = [
                    element for element in result.elements
                    if element.confidence >= self.element_confidence_threshold
                ]
                
                logger.info(f"Found {len(filtered_elements)} elements in region ({x}, {y}, {width}, {height})")
                return filtered_elements
            else:
                logger.error(f"Failed to detect elements in region: {result.error_message}")
                return []
                
        except Exception as e:
            logger.error(f"Error during get_elements_in_region: {e}")
            return []
    
    def get_automation_status(self) -> Dict[str, Any]:
        """Get current automation engine status."""
        return {
            'platform': self.platform.name,
            'context': {
                'has_context': self.current_context is not None,
                'target_window': self.current_context.target_window.title if self.current_context and self.current_context.target_window else None,
                'detected_elements_count': len(self.current_context.detected_elements) if self.current_context else 0
            },
            'configuration': {
                'default_timeout': self.default_timeout,
                'retry_interval': self.retry_interval,
                'confidence_threshold': self.element_confidence_threshold
            },
            'history': {
                'operations_count': len(self.operation_history),
                'recent_operations': self.operation_history[-5:] if self.operation_history else []
            }
        }
    
    def _click_element(self, element: UIElementInfo) -> bool:
        """Click on a detected UI element."""
        try:
            # Get center point of element
            center_x, center_y = element.center_point
            
            # Execute click at center point
            return self.click_at_coordinates(center_x, center_y)
            
        except Exception as e:
            logger.error(f"Error clicking element {element.element_id}: {e}")
            return False
    
    def _update_automation_context(self):
        """Update current automation context with fresh information."""
        try:
            # Get active window
            active_window = self.window_manager.get_active_window()
            
            # Take screenshot
            screenshot = self.platform.take_screenshot()
            
            # Create new context
            self.current_context = AutomationContext(
                target_window=active_window,
                screenshot=screenshot
            )
            
        except Exception as e:
            logger.error(f"Failed to update automation context: {e}")
    
    def _record_operation(self, operation: Dict[str, Any]):
        """Record automation operation in history."""
        try:
            self.operation_history.append(operation)
            
            # Keep only last 100 operations
            if len(self.operation_history) > 100:
                self.operation_history = self.operation_history[-100:]
                
        except Exception as e:
            logger.error(f"Failed to record operation: {e}")
    
    def cleanup(self):
        """Clean up automation engine resources."""
        try:
            logger.info("Cleaning up AutomationEngine")
            
            if hasattr(self.element_detector, 'cleanup'):
                self.element_detector.cleanup()
            
            self.current_context = None
            self.operation_history.clear()
            
            logger.info("AutomationEngine cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during automation cleanup: {e}")