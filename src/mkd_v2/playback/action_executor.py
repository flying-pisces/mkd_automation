"""
Action Executor - Executes individual automation actions during playback.

Handles the execution of recorded actions with proper error handling,
timing, and platform-specific adaptations.
"""

import logging
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

from ..automation.automation_engine import AutomationEngine
from ..platform.base import PlatformInterface, MouseAction, KeyboardAction

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Action execution status."""
    SUCCESS = "success"
    FAILED = "failed" 
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class ExecutionResult:
    """Result of action execution."""
    success: bool
    status: ExecutionStatus
    execution_time: float
    error_message: Optional[str] = None
    action_type: Optional[str] = None
    
    @property
    def failed(self) -> bool:
        """Check if execution failed."""
        return not self.success


class ActionExecutor:
    """
    Executes individual automation actions during playback.
    
    Supports:
    - Mouse clicks and movements
    - Keyboard input and shortcuts
    - UI element interactions
    - Timing and delays
    - Context-aware execution
    """
    
    def __init__(self, platform: PlatformInterface, automation_engine: AutomationEngine):
        self.platform = platform
        self.automation_engine = automation_engine
        
        # Execution configuration
        self.default_timeout = 5.0
        self.click_timeout = 2.0
        self.type_timeout = 3.0
        
        # Statistics
        self.stats = {
            'actions_executed': 0,
            'actions_successful': 0,
            'actions_failed': 0,
            'total_execution_time': 0.0,
            'action_types': {}
        }
        
        logger.info("ActionExecutor initialized")
    
    def execute_action(self, action: Dict[str, Any]) -> ExecutionResult:
        """
        Execute a single automation action.
        
        Args:
            action: Action dictionary from recorded session
            
        Returns:
            ExecutionResult with execution details
        """
        start_time = time.time()
        action_type = action.get('type', 'unknown')
        
        try:
            logger.debug(f"Executing action: {action_type}")
            
            # Update statistics
            self.stats['actions_executed'] += 1
            self.stats['action_types'][action_type] = self.stats['action_types'].get(action_type, 0) + 1
            
            # Route to appropriate handler
            result = self._route_action(action)
            
            # Update execution time
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            result.action_type = action_type
            
            # Update statistics
            self.stats['total_execution_time'] += execution_time
            if result.success:
                self.stats['actions_successful'] += 1
            else:
                self.stats['actions_failed'] += 1
            
            logger.debug(f"Action {action_type} completed: {result.status.value} in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error executing action {action_type}: {e}")
            
            self.stats['actions_failed'] += 1
            self.stats['total_execution_time'] += execution_time
            
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                execution_time=execution_time,
                error_message=str(e),
                action_type=action_type
            )
    
    def _route_action(self, action: Dict[str, Any]) -> ExecutionResult:
        """Route action to appropriate execution handler."""
        action_type = action.get('type', '').lower()
        
        if action_type == 'mouse_click' or action_type == 'click':
            return self._execute_mouse_click(action)
        
        elif action_type == 'mouse_move':
            return self._execute_mouse_move(action)
        
        elif action_type == 'key_press' or action_type == 'keyboard':
            return self._execute_keyboard_action(action)
        
        elif action_type == 'type_text' or action_type == 'type':
            return self._execute_type_text(action)
        
        elif action_type == 'delay' or action_type == 'wait':
            return self._execute_delay(action)
        
        elif action_type == 'click_element':
            return self._execute_click_element(action)
        
        elif action_type == 'scroll':
            return self._execute_scroll(action)
        
        else:
            logger.warning(f"Unknown action type: {action_type}")
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                execution_time=0.0,
                error_message=f"Unknown action type: {action_type}"
            )
    
    def _execute_mouse_click(self, action: Dict[str, Any]) -> ExecutionResult:
        """Execute mouse click action."""
        try:
            # Extract click parameters
            if 'coordinates' in action:
                x, y = action['coordinates']
            elif 'x' in action and 'y' in action:
                x, y = action['x'], action['y']
            else:
                return ExecutionResult(
                    success=False,
                    status=ExecutionStatus.FAILED,
                    execution_time=0.0,
                    error_message="Missing coordinates for mouse click"
                )
            
            button = action.get('button', 'left')
            
            # Execute click using automation engine
            success = self.automation_engine.click_at_coordinates(x, y, button)
            
            if success:
                return ExecutionResult(
                    success=True,
                    status=ExecutionStatus.SUCCESS,
                    execution_time=0.0
                )
            else:
                return ExecutionResult(
                    success=False,
                    status=ExecutionStatus.FAILED,
                    execution_time=0.0,
                    error_message="Mouse click execution failed"
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                execution_time=0.0,
                error_message=f"Mouse click error: {e}"
            )
    
    def _execute_mouse_move(self, action: Dict[str, Any]) -> ExecutionResult:
        """Execute mouse move action."""
        try:
            # Extract move parameters
            if 'coordinates' in action:
                x, y = action['coordinates']
            elif 'x' in action and 'y' in action:
                x, y = action['x'], action['y']
            else:
                return ExecutionResult(
                    success=False,
                    status=ExecutionStatus.FAILED,
                    execution_time=0.0,
                    error_message="Missing coordinates for mouse move"
                )
            
            # Create mouse move action
            mouse_action = MouseAction(
                action="move",
                x=x, y=y
            )
            
            # Execute move
            success = self.platform.execute_mouse_action(mouse_action)
            
            if success:
                return ExecutionResult(
                    success=True,
                    status=ExecutionStatus.SUCCESS,
                    execution_time=0.0
                )
            else:
                return ExecutionResult(
                    success=False,
                    status=ExecutionStatus.FAILED,
                    execution_time=0.0,
                    error_message="Mouse move execution failed"
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                execution_time=0.0,
                error_message=f"Mouse move error: {e}"
            )
    
    def _execute_keyboard_action(self, action: Dict[str, Any]) -> ExecutionResult:
        """Execute keyboard action (key press/release)."""
        try:
            key = action.get('key')
            if not key:
                return ExecutionResult(
                    success=False,
                    status=ExecutionStatus.FAILED,
                    execution_time=0.0,
                    error_message="Missing key for keyboard action"
                )
            
            key_action = action.get('action', 'press')  # press, release, or combination
            
            if key_action == 'combination' and 'keys' in action:
                # Handle key combination (e.g., Ctrl+C)
                keys = action['keys']
                keyboard_action = KeyboardAction(
                    action="key_combination",
                    keys=keys
                )
            else:
                # Single key press/release
                keyboard_action = KeyboardAction(
                    action=key_action,
                    key=key
                )
            
            # Execute keyboard action
            success = self.platform.execute_keyboard_action(keyboard_action)
            
            if success:
                return ExecutionResult(
                    success=True,
                    status=ExecutionStatus.SUCCESS,
                    execution_time=0.0
                )
            else:
                return ExecutionResult(
                    success=False,
                    status=ExecutionStatus.FAILED,
                    execution_time=0.0,
                    error_message="Keyboard action execution failed"
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                execution_time=0.0,
                error_message=f"Keyboard action error: {e}"
            )
    
    def _execute_type_text(self, action: Dict[str, Any]) -> ExecutionResult:
        """Execute text typing action."""
        try:
            text = action.get('text')
            if text is None:
                return ExecutionResult(
                    success=False,
                    status=ExecutionStatus.FAILED,
                    execution_time=0.0,
                    error_message="Missing text for type action"
                )
            
            clear_first = action.get('clear_first', False)
            
            # Execute text typing using automation engine
            success = self.automation_engine.type_text(text, clear_first=clear_first)
            
            if success:
                return ExecutionResult(
                    success=True,
                    status=ExecutionStatus.SUCCESS,
                    execution_time=0.0
                )
            else:
                return ExecutionResult(
                    success=False,
                    status=ExecutionStatus.FAILED,
                    execution_time=0.0,
                    error_message="Text typing execution failed"
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                execution_time=0.0,
                error_message=f"Type text error: {e}"
            )
    
    def _execute_delay(self, action: Dict[str, Any]) -> ExecutionResult:
        """Execute delay/wait action."""
        try:
            duration = action.get('duration', action.get('delay', 1.0))
            
            if duration > 0:
                time.sleep(duration)
            
            return ExecutionResult(
                success=True,
                status=ExecutionStatus.SUCCESS,
                execution_time=duration
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                execution_time=0.0,
                error_message=f"Delay error: {e}"
            )
    
    def _execute_click_element(self, action: Dict[str, Any]) -> ExecutionResult:
        """Execute click on element by text or other identifier."""
        try:
            target = action.get('target', {})
            
            if 'text' in target:
                # Click element by text
                text = target['text']
                fuzzy = target.get('fuzzy', True)
                timeout = target.get('timeout', self.click_timeout)
                
                success = self.automation_engine.click_element_by_text(
                    text, fuzzy=fuzzy, timeout=timeout
                )
                
                if success:
                    return ExecutionResult(
                        success=True,
                        status=ExecutionStatus.SUCCESS,
                        execution_time=0.0
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        status=ExecutionStatus.FAILED,
                        execution_time=0.0,
                        error_message=f"Element not found or click failed: '{text}'"
                    )
            
            elif 'coordinates' in target:
                # Click at coordinates
                x, y = target['coordinates']
                return self._execute_mouse_click({'x': x, 'y': y})
            
            else:
                return ExecutionResult(
                    success=False,
                    status=ExecutionStatus.FAILED,
                    execution_time=0.0,
                    error_message="Invalid target specification for click_element"
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                execution_time=0.0,
                error_message=f"Click element error: {e}"
            )
    
    def _execute_scroll(self, action: Dict[str, Any]) -> ExecutionResult:
        """Execute scroll action."""
        try:
            # Extract scroll parameters
            x = action.get('x', 0)
            y = action.get('y', 0)
            dx = action.get('dx', 0)
            dy = action.get('dy', 0)
            
            # Create mouse scroll action
            mouse_action = MouseAction(
                action="scroll",
                x=x, y=y,
                dx=dx, dy=dy
            )
            
            # Execute scroll
            success = self.platform.execute_mouse_action(mouse_action)
            
            if success:
                return ExecutionResult(
                    success=True,
                    status=ExecutionStatus.SUCCESS,
                    execution_time=0.0
                )
            else:
                return ExecutionResult(
                    success=False,
                    status=ExecutionStatus.FAILED,
                    execution_time=0.0,
                    error_message="Scroll execution failed"
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                execution_time=0.0,
                error_message=f"Scroll error: {e}"
            )
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get action execution statistics."""
        total_actions = self.stats['actions_executed']
        success_rate = (self.stats['actions_successful'] / total_actions * 100) if total_actions > 0 else 0.0
        avg_execution_time = (self.stats['total_execution_time'] / total_actions) if total_actions > 0 else 0.0
        
        return {
            'total_actions': total_actions,
            'successful_actions': self.stats['actions_successful'],
            'failed_actions': self.stats['actions_failed'],
            'success_rate': success_rate,
            'total_execution_time': self.stats['total_execution_time'],
            'average_execution_time': avg_execution_time,
            'action_types': self.stats['action_types'].copy()
        }
    
    def reset_stats(self):
        """Reset execution statistics."""
        self.stats = {
            'actions_executed': 0,
            'actions_successful': 0,
            'actions_failed': 0,
            'total_execution_time': 0.0,
            'action_types': {}
        }
        logger.info("Action execution statistics reset")
    
    def cleanup(self):
        """Clean up action executor resources."""
        logger.info("ActionExecutor cleanup complete")