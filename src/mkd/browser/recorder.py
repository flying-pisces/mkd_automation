"""
Browser action recorder for capturing user interactions.
"""
import time
import logging
from typing import List, Optional, Callable
from threading import Thread, Event
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener

from .actions import BrowserAction, BrowserActionType

logger = logging.getLogger(__name__)


class BrowserEventListener(AbstractEventListener):
    """Listens to browser events and records actions."""
    
    def __init__(self, recorder):
        """Initialize with recorder reference."""
        self.recorder = recorder
        
    def before_navigate_to(self, url, driver):
        """Record navigation action."""
        action = BrowserAction(
            type=BrowserActionType.NAVIGATE,
            target=url,
            timestamp=time.time()
        )
        self.recorder.add_action(action)
        
    def before_click(self, element, driver):
        """Record click action."""
        selector = self._get_element_selector(element)
        if selector:
            action = BrowserAction(
                type=BrowserActionType.CLICK,
                target=selector,
                timestamp=time.time()
            )
            self.recorder.add_action(action)
            
    def before_change_value_of(self, element, driver):
        """Record value change (typing)."""
        self.recorder._before_element = element
        self.recorder._before_value = element.get_attribute('value')
        
    def after_change_value_of(self, element, driver):
        """Record the typed text."""
        if hasattr(self.recorder, '_before_element'):
            selector = self._get_element_selector(element)
            current_value = element.get_attribute('value')
            
            if selector and current_value != self.recorder._before_value:
                action = BrowserAction(
                    type=BrowserActionType.TYPE,
                    target=selector,
                    value=current_value,
                    timestamp=time.time(),
                    metadata={'clear': True}
                )
                self.recorder.add_action(action)
                
            # Clean up
            del self.recorder._before_element
            del self.recorder._before_value
            
    def _get_element_selector(self, element) -> Optional[str]:
        """Generate a CSS selector for an element."""
        try:
            # Try ID first
            elem_id = element.get_attribute('id')
            if elem_id:
                return f"#{elem_id}"
                
            # Try unique class
            classes = element.get_attribute('class')
            if classes:
                class_selector = '.' + '.'.join(classes.split())
                # Check if selector is unique
                elements = element.parent.find_elements(By.CSS_SELECTOR, class_selector)
                if len(elements) == 1:
                    return class_selector
                    
            # Try name attribute
            name = element.get_attribute('name')
            if name:
                return f"[name='{name}']"
                
            # Try other attributes
            for attr in ['data-testid', 'data-id', 'aria-label']:
                value = element.get_attribute(attr)
                if value:
                    return f"[{attr}='{value}']"
                    
            # Fall back to tag name with index
            tag = element.tag_name
            parent = element.parent
            elements = parent.find_elements(By.TAG_NAME, tag)
            index = elements.index(element)
            return f"{tag}:nth-of-type({index + 1})"
            
        except Exception as e:
            logger.error(f"Failed to get element selector: {e}")
            return None


class BrowserRecorder:
    """
    Records browser interactions for playback.
    
    This recorder captures user interactions with the browser
    and converts them into reproducible actions.
    """
    
    def __init__(self, controller=None):
        """Initialize browser recorder."""
        self.controller = controller
        self.actions: List[BrowserAction] = []
        self._recording = False
        self._event_driver: Optional[EventFiringWebDriver] = None
        self._listener: Optional[BrowserEventListener] = None
        
    def start_recording(self) -> None:
        """Start recording browser actions."""
        if self._recording:
            logger.warning("Already recording")
            return
            
        if not self.controller or not self.controller._is_active:
            raise RuntimeError("Browser controller not active")
            
        # Wrap driver with event listener
        self._listener = BrowserEventListener(self)
        self._event_driver = EventFiringWebDriver(
            self.controller.driver,
            self._listener
        )
        
        # Replace controller's driver with event-firing wrapper
        self.controller.driver = self._event_driver
        
        # Add JavaScript event listeners for additional events
        self._inject_js_listeners()
        
        self.actions.clear()
        self._recording = True
        logger.info("Started recording browser actions")
        
    def stop_recording(self) -> List[BrowserAction]:
        """Stop recording and return actions."""
        if not self._recording:
            return self.actions
            
        # Restore original driver
        if self._event_driver and self.controller:
            self.controller.driver = self._event_driver.wrapped_driver
            
        self._recording = False
        logger.info(f"Stopped recording. Captured {len(self.actions)} actions")
        
        return self.actions
        
    def add_action(self, action: BrowserAction) -> None:
        """Add an action to the recording."""
        if self._recording:
            self.actions.append(action)
            logger.debug(f"Recorded action: {action.type.value} on {action.target}")
            
    def save_recording(self, filename: str) -> None:
        """Save recorded actions to file."""
        data = {
            'version': '1.0',
            'timestamp': time.time(),
            'actions': [action.to_dict() for action in self.actions]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Saved recording to {filename}")
        
    def load_recording(self, filename: str) -> List[BrowserAction]:
        """Load recorded actions from file."""
        with open(filename, 'r') as f:
            data = json.load(f)
            
        self.actions = [
            BrowserAction.from_dict(action_data)
            for action_data in data['actions']
        ]
        
        logger.info(f"Loaded {len(self.actions)} actions from {filename}")
        return self.actions
        
    def _inject_js_listeners(self) -> None:
        """Inject JavaScript to capture additional events."""
        js_code = """
        // Capture scroll events
        let lastScrollTime = 0;
        window.addEventListener('scroll', function(e) {
            const now = Date.now();
            if (now - lastScrollTime > 500) {  // Throttle to 500ms
                lastScrollTime = now;
                window.__mkd_scroll = {
                    x: window.scrollX,
                    y: window.scrollY,
                    timestamp: now
                };
            }
        });
        
        // Capture form submits
        document.addEventListener('submit', function(e) {
            window.__mkd_submit = {
                target: e.target,
                timestamp: Date.now()
            };
        });
        
        // Capture key presses (for shortcuts)
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey || e.metaKey || e.altKey) {
                window.__mkd_keypress = {
                    key: e.key,
                    ctrl: e.ctrlKey,
                    alt: e.altKey,
                    shift: e.shiftKey,
                    meta: e.metaKey,
                    timestamp: Date.now()
                };
            }
        });
        """
        
        if self.controller and self.controller._is_active:
            self.controller.execute_script(js_code)
            
    def poll_js_events(self) -> None:
        """Poll for JavaScript events (run in separate thread)."""
        while self._recording:
            if not self.controller or not self.controller._is_active:
                break
                
            try:
                # Check for scroll events
                scroll_data = self.controller.execute_script("return window.__mkd_scroll;")
                if scroll_data:
                    action = BrowserAction(
                        type=BrowserActionType.SCROLL,
                        timestamp=scroll_data['timestamp'] / 1000,
                        metadata={'x': scroll_data['x'], 'y': scroll_data['y']}
                    )
                    self.add_action(action)
                    self.controller.execute_script("window.__mkd_scroll = null;")
                    
            except Exception as e:
                logger.debug(f"Error polling JS events: {e}")
                
            time.sleep(0.1)  # Poll every 100ms