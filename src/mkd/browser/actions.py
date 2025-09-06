"""
Browser action definitions and execution.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any, Dict
import time
import logging

from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


class BrowserActionType(Enum):
    """Types of browser actions."""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    SCRIPT = "script"
    SCROLL = "scroll"
    HOVER = "hover"
    DRAG_DROP = "drag_drop"
    SWITCH_TAB = "switch_tab"
    SWITCH_FRAME = "switch_frame"
    ALERT_HANDLE = "alert_handle"
    KEY_PRESS = "key_press"
    CLEAR = "clear"
    SUBMIT = "submit"


@dataclass
class BrowserAction:
    """Represents a single browser action."""
    type: BrowserActionType
    target: Optional[str] = None  # CSS selector or URL
    value: Optional[Any] = None  # Text to type, script to execute, etc.
    by: By = By.CSS_SELECTOR
    wait: bool = True
    timestamp: float = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary."""
        return {
            'type': self.type.value,
            'target': self.target,
            'value': self.value,
            'by': self.by.name if hasattr(self.by, 'name') else str(self.by),
            'wait': self.wait,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BrowserAction':
        """Create action from dictionary."""
        # Convert string back to By enum
        by_str = data.get('by', 'CSS_SELECTOR')
        by = getattr(By, by_str, By.CSS_SELECTOR)
        
        return cls(
            type=BrowserActionType(data['type']),
            target=data.get('target'),
            value=data.get('value'),
            by=by,
            wait=data.get('wait', True),
            timestamp=data.get('timestamp'),
            metadata=data.get('metadata', {})
        )


class BrowserActionExecutor:
    """Executes browser actions."""
    
    def __init__(self, controller):
        """Initialize with browser controller."""
        self.controller = controller
        
    def execute(self, action: BrowserAction) -> Any:
        """Execute a browser action."""
        logger.debug(f"Executing browser action: {action.type.value}")
        
        if action.type == BrowserActionType.NAVIGATE:
            return self._execute_navigate(action)
        elif action.type == BrowserActionType.CLICK:
            return self._execute_click(action)
        elif action.type == BrowserActionType.TYPE:
            return self._execute_type(action)
        elif action.type == BrowserActionType.WAIT:
            return self._execute_wait(action)
        elif action.type == BrowserActionType.SCREENSHOT:
            return self._execute_screenshot(action)
        elif action.type == BrowserActionType.SCRIPT:
            return self._execute_script(action)
        elif action.type == BrowserActionType.SCROLL:
            return self._execute_scroll(action)
        elif action.type == BrowserActionType.HOVER:
            return self._execute_hover(action)
        elif action.type == BrowserActionType.CLEAR:
            return self._execute_clear(action)
        elif action.type == BrowserActionType.SUBMIT:
            return self._execute_submit(action)
        elif action.type == BrowserActionType.SWITCH_TAB:
            return self._execute_switch_tab(action)
        elif action.type == BrowserActionType.SWITCH_FRAME:
            return self._execute_switch_frame(action)
        elif action.type == BrowserActionType.ALERT_HANDLE:
            return self._execute_alert_handle(action)
        else:
            raise ValueError(f"Unknown action type: {action.type}")
            
    def _execute_navigate(self, action: BrowserAction) -> None:
        """Execute navigate action."""
        self.controller.navigate(action.target)
        
    def _execute_click(self, action: BrowserAction) -> None:
        """Execute click action."""
        self.controller.click(action.target, action.by, action.wait)
        
    def _execute_type(self, action: BrowserAction) -> None:
        """Execute type action."""
        clear = action.metadata.get('clear', True)
        self.controller.type_text(action.target, action.value, action.by, clear, action.wait)
        
    def _execute_wait(self, action: BrowserAction) -> None:
        """Execute wait action."""
        if action.value:
            # Wait for specific duration
            time.sleep(float(action.value))
        elif action.target:
            # Wait for element
            timeout = action.metadata.get('timeout', 10)
            self.controller.wait_for_element(action.target, action.by, timeout)
            
    def _execute_screenshot(self, action: BrowserAction) -> bytes:
        """Execute screenshot action."""
        filename = action.value if action.value else None
        return self.controller.take_screenshot(filename)
        
    def _execute_script(self, action: BrowserAction) -> Any:
        """Execute JavaScript."""
        return self.controller.execute_script(action.value)
        
    def _execute_scroll(self, action: BrowserAction) -> None:
        """Execute scroll action."""
        if action.target:
            # Scroll to element
            element = self.controller._find_element(action.target, action.by, action.wait)
            self.controller.execute_script("arguments[0].scrollIntoView(true);", element)
        else:
            # Scroll by offset
            x = action.metadata.get('x', 0)
            y = action.metadata.get('y', 0)
            self.controller.execute_script(f"window.scrollBy({x}, {y});")
            
    def _execute_hover(self, action: BrowserAction) -> None:
        """Execute hover action."""
        from selenium.webdriver.common.action_chains import ActionChains
        
        element = self.controller._find_element(action.target, action.by, action.wait)
        ActionChains(self.controller.driver).move_to_element(element).perform()
        
    def _execute_clear(self, action: BrowserAction) -> None:
        """Execute clear action."""
        element = self.controller._find_element(action.target, action.by, action.wait)
        element.clear()
        
    def _execute_submit(self, action: BrowserAction) -> None:
        """Execute submit action."""
        element = self.controller._find_element(action.target, action.by, action.wait)
        element.submit()
        
    def _execute_switch_tab(self, action: BrowserAction) -> None:
        """Switch browser tab."""
        if action.value is not None:
            # Switch to specific tab index
            windows = self.controller.driver.window_handles
            if 0 <= action.value < len(windows):
                self.controller.driver.switch_to.window(windows[action.value])
        else:
            # Switch to last tab
            self.controller.driver.switch_to.window(self.controller.driver.window_handles[-1])
            
    def _execute_switch_frame(self, action: BrowserAction) -> None:
        """Switch to iframe."""
        if action.target:
            frame = self.controller._find_element(action.target, action.by, action.wait)
            self.controller.switch_to_frame(frame)
        else:
            self.controller.switch_to_default_content()
            
    def _execute_alert_handle(self, action: BrowserAction) -> str:
        """Handle alert dialog."""
        accept = action.metadata.get('accept', True)
        text = action.value if action.value else None
        return self.controller.handle_alert(accept, text)