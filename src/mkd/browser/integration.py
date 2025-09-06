"""
Integration module for browser automation with MKD core.

This module bridges the browser automation capabilities with MKD's
existing recording and playback infrastructure.
"""
import logging
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from ..core.session import Session, Action as MKDAction
from ..core.script import Script
# from ..recording.engine import RecordingEngine  # Not needed for browser integration
# from ..playback.action_executor import ActionExecutor  # Will be set externally

from .controller import BrowserController, BrowserConfig
from .actions import BrowserAction, BrowserActionType, BrowserActionExecutor
from .recorder import BrowserRecorder

logger = logging.getLogger(__name__)


@dataclass
class BrowserSession:
    """Represents a browser automation session."""
    browser_controller: BrowserController
    browser_recorder: BrowserRecorder
    browser_executor: BrowserActionExecutor
    start_time: float
    actions: List[BrowserAction]
    
    
class BrowserIntegration:
    """
    Integrates browser automation with MKD's core functionality.
    
    This integration allows:
    - Recording browser actions alongside mouse/keyboard actions
    - Replaying mixed scripts with both desktop and browser automation
    - Seamless switching between browser and desktop contexts
    """
    
    def __init__(self, session: Session = None):
        """Initialize browser integration."""
        self.session = session
        self.browser_session: Optional[BrowserSession] = None
        self._is_recording = False
        self._is_playing = False
        
    def start_browser_session(self, config: Optional[BrowserConfig] = None) -> BrowserSession:
        """Start a new browser automation session."""
        if self.browser_session:
            logger.warning("Browser session already active")
            return self.browser_session
            
        # Create browser components
        controller = BrowserController(config)
        recorder = BrowserRecorder(controller)
        executor = BrowserActionExecutor(controller)
        
        # Start the browser
        controller.start()
        
        # Create session
        self.browser_session = BrowserSession(
            browser_controller=controller,
            browser_recorder=recorder,
            browser_executor=executor,
            start_time=time.time(),
            actions=[]
        )
        
        logger.info("Browser session started")
        return self.browser_session
        
    def stop_browser_session(self) -> None:
        """Stop the current browser session."""
        if not self.browser_session:
            return
            
        # Stop recording if active
        if self._is_recording:
            self.stop_browser_recording()
            
        # Stop browser
        self.browser_session.browser_controller.stop()
        self.browser_session = None
        
        logger.info("Browser session stopped")
        
    def start_browser_recording(self) -> None:
        """Start recording browser actions."""
        if not self.browser_session:
            raise RuntimeError("No active browser session")
            
        if self._is_recording:
            logger.warning("Already recording")
            return
            
        self.browser_session.browser_recorder.start_recording()
        self._is_recording = True
        
        logger.info("Started browser recording")
        
    def stop_browser_recording(self) -> List[BrowserAction]:
        """Stop recording and return browser actions."""
        if not self.browser_session or not self._is_recording:
            return []
            
        actions = self.browser_session.browser_recorder.stop_recording()
        self.browser_session.actions.extend(actions)
        self._is_recording = False
        
        logger.info(f"Stopped browser recording. Captured {len(actions)} actions")
        return actions
        
    def execute_browser_action(self, action: BrowserAction) -> Any:
        """Execute a single browser action."""
        if not self.browser_session:
            raise RuntimeError("No active browser session")
            
        return self.browser_session.browser_executor.execute(action)
        
    def execute_browser_script(self, actions: List[BrowserAction], 
                             speed: float = 1.0) -> None:
        """Execute a sequence of browser actions."""
        if not self.browser_session:
            raise RuntimeError("No active browser session")
            
        self._is_playing = True
        
        try:
            for i, action in enumerate(actions):
                logger.info(f"Executing action {i+1}/{len(actions)}: {action.type.value}")
                
                # Execute the action
                self.execute_browser_action(action)
                
                # Add delay between actions based on speed
                if i < len(actions) - 1:
                    next_action = actions[i + 1]
                    if action.timestamp and next_action.timestamp:
                        delay = (next_action.timestamp - action.timestamp) / speed
                        if delay > 0:
                            time.sleep(min(delay, 5))  # Cap at 5 seconds
                    else:
                        time.sleep(0.5 / speed)  # Default delay
                        
        finally:
            self._is_playing = False
            
        logger.info("Browser script execution completed")
        
    def convert_to_mkd_actions(self, browser_actions: List[BrowserAction]) -> List[MKDAction]:
        """Convert browser actions to MKD script actions."""
        mkd_actions = []
        
        for action in browser_actions:
            # Create MKD action with browser-specific metadata
            mkd_action = MKDAction(
                type="browser",
                timestamp=action.timestamp,
                data={
                    'browser_type': action.type.value,
                    'target': action.target,
                    'value': action.value,
                    'by': str(action.by),
                    'wait': action.wait,
                    'metadata': action.metadata
                }
            )
            mkd_actions.append(mkd_action)
            
        return mkd_actions
        
    def convert_from_mkd_actions(self, mkd_actions: List[MKDAction]) -> List[BrowserAction]:
        """Convert MKD script actions to browser actions."""
        browser_actions = []
        
        for action in mkd_actions:
            if action.type == "browser":
                data = action.data
                browser_action = BrowserAction(
                    type=BrowserActionType(data['browser_type']),
                    target=data.get('target'),
                    value=data.get('value'),
                    wait=data.get('wait', True),
                    timestamp=action.timestamp,
                    metadata=data.get('metadata', {})
                )
                browser_actions.append(browser_action)
                
        return browser_actions
        
    def create_mixed_script(self, name: str = "Mixed Automation") -> Script:
        """
        Create a script combining browser and desktop actions.
        
        Returns:
            Script object containing both types of actions
        """
        if not self.session:
            raise RuntimeError("No MKD session available")
            
        script = Script(name=name)
        
        # Add desktop actions from current session
        if hasattr(self.session, 'current_recording'):
            desktop_actions = self.session.current_recording.actions
            script.actions.extend(desktop_actions)
            
        # Add browser actions if available
        if self.browser_session and self.browser_session.actions:
            mkd_browser_actions = self.convert_to_mkd_actions(
                self.browser_session.actions
            )
            script.actions.extend(mkd_browser_actions)
            
        # Sort actions by timestamp
        script.actions.sort(key=lambda a: a.timestamp or 0)
        
        return script
        
    def execute_mixed_script(self, script: Script, speed: float = 1.0) -> None:
        """
        Execute a script containing both browser and desktop actions.
        
        Args:
            script: Script object with mixed actions
            speed: Playback speed multiplier
        """
        browser_actions = []
        desktop_actions = []
        
        # Separate actions by type
        for action in script.actions:
            if action.type == "browser":
                browser_action = self.convert_from_mkd_actions([action])[0]
                browser_actions.append(browser_action)
            else:
                desktop_actions.append(action)
                
        # Execute in chronological order
        all_actions = [
            ('browser', a) for a in browser_actions
        ] + [
            ('desktop', a) for a in desktop_actions
        ]
        
        # Sort by timestamp
        all_actions.sort(key=lambda x: x[1].timestamp or 0)
        
        # Execute actions
        for action_type, action in all_actions:
            if action_type == 'browser':
                self.execute_browser_action(action)
            else:
                # Use MKD's action executor for desktop actions
                if self.session and hasattr(self.session, 'executor'):
                    self.session.executor.execute_action(action)
                    
            # Add appropriate delay
            time.sleep(0.1 / speed)
            
        logger.info("Mixed script execution completed")