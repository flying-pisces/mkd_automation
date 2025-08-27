"""
Playback Engine - Core automation sequence playback orchestration.

Manages the execution of recorded automation sequences with intelligent
context adaptation, error recovery, and timing management.
"""

import logging
import time
import threading
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

from .action_executor import ActionExecutor, ExecutionResult
from .sequence_validator import SequenceValidator, ValidationResult
from ..automation.automation_engine import AutomationEngine
from ..platform.base import PlatformInterface
from ..core.session_manager import RecordingSession

logger = logging.getLogger(__name__)


class PlaybackStatus(Enum):
    """Playback execution status."""
    IDLE = "idle"
    PREPARING = "preparing" 
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PlaybackResult:
    """Result of a playback operation."""
    success: bool
    status: PlaybackStatus
    actions_total: int
    actions_executed: int
    actions_failed: int
    execution_time: float = 0.0
    error_message: Optional[str] = None
    failed_actions: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.failed_actions is None:
            self.failed_actions = []
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.actions_total == 0:
            return 0.0
        return ((self.actions_executed - self.actions_failed) / self.actions_total) * 100.0


class PlaybackEngine:
    """
    Core playback engine for automation sequence execution.
    
    Features:
    - Sequential and parallel action execution
    - Context verification before actions
    - Intelligent retry and recovery
    - Real-time playback monitoring
    - Speed adjustment and pause/resume
    """
    
    def __init__(self, platform: PlatformInterface, automation_engine: AutomationEngine):
        self.platform = platform
        self.automation_engine = automation_engine
        
        # Core components
        self.action_executor = ActionExecutor(platform, automation_engine)
        self.sequence_validator = SequenceValidator(automation_engine)
        
        # Playback state
        self.status = PlaybackStatus.IDLE
        self.current_session: Optional[RecordingSession] = None
        self.current_sequence: List[Dict[str, Any]] = []
        self.current_action_index = 0
        
        # Execution control
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._execution_thread: Optional[threading.Thread] = None
        
        # Configuration
        self.speed_multiplier = 1.0  # 1.0 = normal speed, 2.0 = 2x speed, 0.5 = half speed
        self.verify_context = True   # Whether to verify context before actions
        self.retry_failed_actions = True
        self.max_retries = 3
        self.retry_delay = 1.0
        
        # Statistics
        self.stats = {
            'total_playbacks': 0,
            'successful_playbacks': 0,
            'total_actions_executed': 0,
            'total_execution_time': 0.0
        }
        
        # Callbacks
        self.progress_callback: Optional[Callable[[float, str], None]] = None
        self.error_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
        
        logger.info("PlaybackEngine initialized")
    
    def play_session(self, session: RecordingSession, start_from: int = 0, 
                    progress_callback: Optional[Callable] = None) -> PlaybackResult:
        """
        Play back a recorded session.
        
        Args:
            session: Session to play back
            start_from: Action index to start from (for resuming)
            progress_callback: Optional progress callback function
            
        Returns:
            PlaybackResult with execution details
        """
        with self._lock:
            if self.status not in [PlaybackStatus.IDLE, PlaybackStatus.COMPLETED, PlaybackStatus.FAILED]:
                return PlaybackResult(
                    success=False,
                    status=self.status,
                    actions_total=0,
                    actions_executed=0,
                    actions_failed=0,
                    error_message="Playback engine is busy"
                )
            
            try:
                logger.info(f"Starting playback of session: {getattr(session, 'id', 'unknown')}")
                
                # Set up playback
                self.current_session = session
                # For now, use empty actions list since RecordingSession doesn't have actions yet
                self.current_sequence = getattr(session, 'actions', [])
                self.current_action_index = start_from
                self.progress_callback = progress_callback
                
                # Validate sequence before execution
                validation_result = self._validate_sequence()
                if not validation_result.is_valid:
                    return PlaybackResult(
                        success=False,
                        status=PlaybackStatus.FAILED,
                        actions_total=len(self.current_sequence),
                        actions_executed=0,
                        actions_failed=0,
                        error_message=f"Sequence validation failed: {validation_result.error_message}"
                    )
                
                # Start execution
                self.status = PlaybackStatus.PREPARING
                self._reset_control_events()
                
                # Execute in separate thread
                self._execution_thread = threading.Thread(
                    target=self._execute_sequence,
                    name="PlaybackExecution",
                    daemon=True
                )
                self._execution_thread.start()
                
                # Wait for completion
                self._execution_thread.join()
                
                # Collect results
                result = self._collect_execution_results()
                
                # Update statistics
                self._update_statistics(result)
                
                logger.info(f"Playback completed: {result.success}, {result.actions_executed}/{result.actions_total} actions")
                return result
                
            except Exception as e:
                logger.error(f"Failed to play session: {e}")
                self.status = PlaybackStatus.FAILED
                return PlaybackResult(
                    success=False,
                    status=PlaybackStatus.FAILED,
                    actions_total=len(self.current_sequence) if self.current_sequence else 0,
                    actions_executed=0,
                    actions_failed=0,
                    error_message=str(e)
                )
    
    def pause_playback(self) -> bool:
        """Pause current playback execution."""
        with self._lock:
            if self.status == PlaybackStatus.RUNNING:
                self.status = PlaybackStatus.PAUSED
                self._pause_event.set()
                logger.info("Playback paused")
                return True
            else:
                logger.warning(f"Cannot pause playback in status: {self.status}")
                return False
    
    def resume_playback(self) -> bool:
        """Resume paused playback execution."""
        with self._lock:
            if self.status == PlaybackStatus.PAUSED:
                self.status = PlaybackStatus.RUNNING
                self._pause_event.clear()
                logger.info("Playback resumed")
                return True
            else:
                logger.warning(f"Cannot resume playback in status: {self.status}")
                return False
    
    def stop_playback(self) -> bool:
        """Stop current playback execution."""
        with self._lock:
            if self.status in [PlaybackStatus.RUNNING, PlaybackStatus.PAUSED, PlaybackStatus.PREPARING]:
                self.status = PlaybackStatus.CANCELLED
                self._stop_event.set()
                self._pause_event.clear()
                logger.info("Playback stopped")
                return True
            else:
                logger.warning(f"Cannot stop playback in status: {self.status}")
                return False
    
    def set_speed(self, multiplier: float) -> bool:
        """
        Set playback speed multiplier.
        
        Args:
            multiplier: Speed multiplier (1.0 = normal, 2.0 = 2x, 0.5 = half)
            
        Returns:
            True if speed was set successfully
        """
        if 0.1 <= multiplier <= 10.0:
            self.speed_multiplier = multiplier
            logger.info(f"Playback speed set to {multiplier}x")
            return True
        else:
            logger.error(f"Invalid speed multiplier: {multiplier}")
            return False
    
    def get_playback_status(self) -> Dict[str, Any]:
        """Get current playback status information."""
        with self._lock:
            return {
                'status': self.status.value,
                'session_name': getattr(self.current_session, 'id', None) if self.current_session else None,
                'progress': {
                    'current_action': self.current_action_index,
                    'total_actions': len(self.current_sequence) if self.current_sequence else 0,
                    'percentage': (self.current_action_index / len(self.current_sequence) * 100) if self.current_sequence else 0
                },
                'configuration': {
                    'speed_multiplier': self.speed_multiplier,
                    'verify_context': self.verify_context,
                    'retry_failed_actions': self.retry_failed_actions,
                    'max_retries': self.max_retries
                },
                'statistics': self.stats.copy()
            }
    
    def _execute_sequence(self):
        """Execute the action sequence (runs in separate thread)."""
        try:
            self.status = PlaybackStatus.RUNNING
            start_time = time.time()
            
            actions_executed = 0
            actions_failed = 0
            failed_actions = []
            
            total_actions = len(self.current_sequence)
            
            for i in range(self.current_action_index, total_actions):
                # Check for stop/pause
                if self._stop_event.is_set():
                    logger.info("Playback stopped by user")
                    break
                
                while self._pause_event.is_set():
                    time.sleep(0.1)  # Wait while paused
                    if self._stop_event.is_set():
                        break
                
                if self._stop_event.is_set():
                    break
                
                # Update current action index
                self.current_action_index = i
                
                # Get action to execute
                action = self.current_sequence[i]
                
                # Report progress
                progress = (i / total_actions) * 100
                if self.progress_callback:
                    try:
                        self.progress_callback(progress, f"Executing action {i+1}/{total_actions}")
                    except:
                        pass  # Don't fail on callback errors
                
                # Execute action with retries
                success = self._execute_action_with_retries(action)
                
                if success:
                    actions_executed += 1
                    logger.debug(f"Action {i+1} executed successfully")
                else:
                    actions_failed += 1
                    failed_actions.append({
                        'index': i,
                        'action': action,
                        'error': 'Execution failed after retries'
                    })
                    logger.error(f"Action {i+1} failed after retries")
                
                # Apply timing delay based on speed
                if 'timing' in action and 'delay_after' in action['timing']:
                    delay = action['timing']['delay_after'] / self.speed_multiplier
                    time.sleep(max(0.01, delay))  # Minimum 10ms delay
            
            # Determine final status
            execution_time = time.time() - start_time
            
            if self._stop_event.is_set():
                self.status = PlaybackStatus.CANCELLED
            elif actions_failed == 0:
                self.status = PlaybackStatus.COMPLETED
            else:
                self.status = PlaybackStatus.FAILED if actions_executed == 0 else PlaybackStatus.COMPLETED
            
            # Store execution results
            self._execution_results = {
                'actions_executed': actions_executed,
                'actions_failed': actions_failed,
                'failed_actions': failed_actions,
                'execution_time': execution_time
            }
            
            logger.info(f"Sequence execution finished: {actions_executed}/{total_actions} successful")
            
        except Exception as e:
            logger.error(f"Error during sequence execution: {e}")
            self.status = PlaybackStatus.FAILED
            self._execution_results = {
                'actions_executed': 0,
                'actions_failed': len(self.current_sequence),
                'failed_actions': [{'error': str(e)}],
                'execution_time': 0.0
            }
    
    def _execute_action_with_retries(self, action: Dict[str, Any]) -> bool:
        """Execute a single action with retry logic."""
        for attempt in range(self.max_retries if self.retry_failed_actions else 1):
            try:
                # Verify context if enabled
                if self.verify_context:
                    context_valid = self._verify_action_context(action)
                    if not context_valid:
                        logger.warning(f"Context verification failed for action (attempt {attempt + 1})")
                        if attempt == 0:  # Only wait on first attempt
                            time.sleep(self.retry_delay)
                        continue
                
                # Execute the action
                result = self.action_executor.execute_action(action)
                
                if result.success:
                    return True
                else:
                    logger.warning(f"Action execution failed: {result.error_message} (attempt {attempt + 1})")
                    
                    # Call error callback
                    if self.error_callback:
                        try:
                            self.error_callback(result.error_message, action)
                        except:
                            pass
                    
                    # Wait before retry
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                
            except Exception as e:
                logger.error(f"Exception during action execution: {e} (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        return False
    
    def _verify_action_context(self, action: Dict[str, Any]) -> bool:
        """Verify that the context is appropriate for executing the action."""
        try:
            # Basic context verification - check if target elements exist
            if action.get('type') == 'click' and 'target' in action:
                target = action['target']
                
                if 'text' in target:
                    # Try to find element by text
                    element = self.automation_engine.element_detector.find_element_by_text(
                        target['text'], fuzzy=True
                    )
                    return element is not None
                
                elif 'coordinates' in target:
                    # For coordinate clicks, assume context is valid
                    return True
            
            # For other action types, assume context is valid
            return True
            
        except Exception as e:
            logger.error(f"Error during context verification: {e}")
            return False
    
    def _validate_sequence(self) -> ValidationResult:
        """Validate the action sequence before execution."""
        try:
            if not self.current_sequence:
                return ValidationResult(
                    is_valid=False,
                    error_message="Empty action sequence"
                )
            
            # Use sequence validator
            return self.sequence_validator.validate_sequence(self.current_sequence)
            
        except Exception as e:
            logger.error(f"Error during sequence validation: {e}")
            return ValidationResult(
                is_valid=False,
                error_message=f"Validation error: {e}"
            )
    
    def _collect_execution_results(self) -> PlaybackResult:
        """Collect execution results into PlaybackResult."""
        results = getattr(self, '_execution_results', {})
        
        return PlaybackResult(
            success=self.status in [PlaybackStatus.COMPLETED],
            status=self.status,
            actions_total=len(self.current_sequence),
            actions_executed=results.get('actions_executed', 0),
            actions_failed=results.get('actions_failed', 0),
            execution_time=results.get('execution_time', 0.0),
            failed_actions=results.get('failed_actions', [])
        )
    
    def _update_statistics(self, result: PlaybackResult):
        """Update playback statistics."""
        self.stats['total_playbacks'] += 1
        if result.success:
            self.stats['successful_playbacks'] += 1
        self.stats['total_actions_executed'] += result.actions_executed
        self.stats['total_execution_time'] += result.execution_time
    
    def _reset_control_events(self):
        """Reset control events for new execution."""
        self._stop_event.clear()
        self._pause_event.clear()
    
    def cleanup(self):
        """Clean up playback engine resources."""
        try:
            logger.info("Cleaning up PlaybackEngine")
            
            # Stop any running playback
            self.stop_playback()
            
            # Wait for execution thread to finish
            if self._execution_thread and self._execution_thread.is_alive():
                self._execution_thread.join(timeout=5.0)
            
            # Clean up components
            if hasattr(self.action_executor, 'cleanup'):
                self.action_executor.cleanup()
            
            # Reset state
            self.current_session = None
            self.current_sequence = []
            self.current_action_index = 0
            self.status = PlaybackStatus.IDLE
            
            logger.info("PlaybackEngine cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during playback cleanup: {e}")