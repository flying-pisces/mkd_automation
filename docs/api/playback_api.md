# MKD Automation - Playback Engine API Reference

## Table of Contents

- [Overview](#overview)
- [Playback Engine API](#playback-engine-api)
- [Action Executor API](#action-executor-api)
- [Timing Engine API](#timing-engine-api)
- [Error Handler API](#error-handler-api)
- [Validator API](#validator-api)
- [Action Models](#action-models)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)

## Overview

The Playback Engine API provides comprehensive control over automation script execution. This API enables precise reproduction of recorded user interactions with advanced timing control, error handling, and validation capabilities.

### Key Features

- **Precise Action Execution**: High-fidelity reproduction of mouse, keyboard, and display actions
- **Variable Speed Control**: Playback speed adjustment from 0.1x to 10x
- **Advanced Timing**: Frame-accurate timing with jitter compensation
- **Error Recovery**: Robust error handling with retry mechanisms and fallback strategies
- **Cross-platform Compatibility**: Consistent behavior across Windows, macOS, and Linux
- **Real-time Monitoring**: Live playback status and progress tracking
- **Action Validation**: Pre-execution validation and compatibility checking

## Playback Engine API

### PlaybackEngine Class

The main playback engine class that orchestrates script execution.

```python
from mkd.playback import PlaybackEngine

class PlaybackEngine:
    """Main playback engine for executing automation scripts"""
    
    def __init__(self, 
                 config: Optional[Dict] = None,
                 event_bus: Optional[EventBus] = None):
        """
        Initialize playback engine
        
        Args:
            config: Playback configuration dictionary
            event_bus: Event bus for inter-component communication
        """
        
    def load_script(self, 
                   script_path: str, 
                   validate: bool = True,
                   preprocess: bool = True) -> str:
        """
        Load automation script for playback
        
        Args:
            script_path: Path to .mkd script file
            validate: Whether to validate script before loading
            preprocess: Whether to preprocess actions for optimization
            
        Returns:
            str: Loaded script ID
            
        Raises:
            FileNotFoundError: If script file doesn't exist
            ScriptValidationError: If script validation fails
            DecryptionError: If unable to decrypt encrypted script
            IncompatibleScriptError: If script is incompatible with current platform
            
        Example:
            >>> engine = PlaybackEngine()
            >>> script_id = engine.load_script("automation.mkd", validate=True)
        """
        
    def play(self, 
             script_id: Optional[str] = None,
             speed: float = 1.0,
             loop: bool = False,
             start_action: int = 0,
             end_action: Optional[int] = None,
             pause_on_error: bool = False) -> str:
        """
        Start playback of loaded script
        
        Args:
            script_id: Script to play (uses last loaded if None)
            speed: Playback speed multiplier (0.1 to 10.0)
            loop: Whether to loop playback continuously
            start_action: Index of first action to play (0-based)
            end_action: Index of last action to play (None for end)
            pause_on_error: Whether to pause on non-critical errors
            
        Returns:
            str: Playback session ID
            
        Raises:
            NoScriptLoadedError: If no script is loaded
            PlaybackAlreadyActiveError: If playback is already active
            InvalidSpeedError: If speed is outside valid range
            InvalidActionRangeError: If action range is invalid
            
        Example:
            >>> session_id = engine.play(
            ...     speed=2.0,
            ...     start_action=10,
            ...     end_action=50,
            ...     pause_on_error=True
            ... )
        """
        
    def pause(self) -> None:
        """
        Pause current playback session
        
        Raises:
            NoActivePlaybackError: If no playback is active
            PlaybackAlreadyPausedError: If already paused
        """
        
    def resume(self) -> None:
        """
        Resume paused playback session
        
        Raises:
            NoActivePlaybackError: If no playback is active
            PlaybackNotPausedError: If not currently paused
        """
        
    def stop(self) -> PlaybackStats:
        """
        Stop current playback session
        
        Returns:
            PlaybackStats: Session statistics and metrics
            
        Raises:
            NoActivePlaybackError: If no playback is active
        """
        
    def seek(self, action_index: int) -> None:
        """
        Seek to specific action in script
        
        Args:
            action_index: Action index to seek to (0-based)
            
        Raises:
            NoActivePlaybackError: If no playback is active
            InvalidActionIndexError: If action index is invalid
            SeekNotSupportedError: If seeking is not supported in current mode
        """
        
    def get_status(self) -> PlaybackStatus:
        """
        Get current playback status
        
        Returns:
            PlaybackStatus: Current playback state and progress
        """
        
    def get_script_info(self, script_id: str) -> ScriptInfo:
        """Get information about loaded script"""
        
    def unload_script(self, script_id: str) -> None:
        """Unload script from memory"""
        
    def set_speed(self, speed: float) -> None:
        """
        Change playback speed during playback
        
        Args:
            speed: New playback speed (0.1 to 10.0)
        """
        
    def add_action_callback(self, 
                           callback: Callable[[ActionEvent], None]) -> str:
        """
        Add callback for action execution events
        
        Args:
            callback: Function to call when actions are executed
            
        Returns:
            str: Callback ID for later removal
        """
        
    def remove_action_callback(self, callback_id: str) -> bool:
        """Remove action callback by ID"""
```

### Playback Configuration

```python
playback_config = {
    # Execution settings
    'execution': {
        'default_speed': 1.0,           # Default playback speed
        'coordinate_mode': 'relative',   # 'absolute', 'relative', 'adaptive'
        'timing_mode': 'recorded',      # 'recorded', 'fixed', 'adaptive'
        'precision_mode': 'high',       # 'low', 'medium', 'high'
        'interpolation': True,          # Enable action interpolation
        'smooth_movement': True         # Enable smooth mouse movements
    },
    
    # Error handling
    'error_handling': {
        'retry_attempts': 3,            # Number of retry attempts
        'retry_delay': 0.5,             # Delay between retries (seconds)
        'continue_on_error': True,      # Continue on non-critical errors
        'pause_on_error': False,        # Pause on any error
        'log_errors': True,             # Log errors to file
        'error_tolerance': 'medium'     # 'strict', 'medium', 'lenient'
    },
    
    # Timing control
    'timing': {
        'frame_rate': 60,               # Target frame rate (Hz)
        'timing_precision': 'millisecond',  # 'centisecond', 'millisecond', 'microsecond'
        'jitter_compensation': True,    # Enable timing jitter compensation
        'adaptive_timing': True,        # Adapt timing based on system performance
        'minimum_delay': 0.001         # Minimum delay between actions (seconds)
    },
    
    # Validation settings
    'validation': {
        'pre_execution': True,          # Validate before execution
        'screen_resolution_check': True,  # Check screen resolution compatibility
        'application_check': False,    # Check if target applications are available
        'coordinate_bounds_check': True,  # Validate coordinate bounds
        'action_compatibility_check': True  # Check action compatibility
    }
}
```

## Action Executor API

### ActionExecutor Class

Executes individual actions with platform-specific implementations.

```python
from mkd.playback import ActionExecutor

class ActionExecutor:
    """Execute individual automation actions"""
    
    def __init__(self, 
                 platform_handler: PlatformInterface,
                 config: Dict):
        """Initialize with platform handler and configuration"""
        
    def execute_action(self, action: Action) -> ActionResult:
        """
        Execute single automation action
        
        Args:
            action: Action to execute
            
        Returns:
            ActionResult: Execution result with success/failure info
            
        Raises:
            ActionExecutionError: If action execution fails
            UnsupportedActionError: If action type is not supported
            InvalidActionDataError: If action data is invalid
        """
        
    def execute_mouse_move(self, action: MouseMoveAction) -> ActionResult:
        """
        Execute mouse movement action
        
        Args:
            action: Mouse move action to execute
            
        Returns:
            ActionResult: Execution result
        """
        
    def execute_mouse_click(self, action: MouseClickAction) -> ActionResult:
        """Execute mouse click action"""
        
    def execute_mouse_scroll(self, action: MouseScrollAction) -> ActionResult:
        """Execute mouse scroll action"""
        
    def execute_key_press(self, action: KeyPressAction) -> ActionResult:
        """Execute keyboard key press action"""
        
    def execute_key_release(self, action: KeyReleaseAction) -> ActionResult:
        """Execute keyboard key release action"""
        
    def execute_type_text(self, action: TypeTextAction) -> ActionResult:
        """Execute text typing action"""
        
    def execute_wait(self, action: WaitAction) -> ActionResult:
        """Execute wait/delay action"""
        
    def execute_screenshot(self, action: ScreenshotAction) -> ActionResult:
        """Execute screenshot capture action"""
        
    def get_execution_stats(self) -> ExecutionStats:
        """Get executor performance statistics"""
        
    def set_coordinate_mode(self, mode: str) -> None:
        """Set coordinate interpretation mode"""
        
    def enable_dry_run(self, enabled: bool) -> None:
        """Enable/disable dry run mode (no actual execution)"""
```

### Action Execution Pipeline

```python
class ActionExecutionPipeline:
    """Pipeline for processing actions before execution"""
    
    def __init__(self):
        self.processors = []
        
    def add_processor(self, 
                     processor: Callable[[Action], Action],
                     priority: int = 0) -> str:
        """Add action preprocessor"""
        
    def process_action(self, action: Action) -> Action:
        """Process action through pipeline"""
        
    def validate_action(self, action: Action) -> ValidationResult:
        """Validate action before execution"""

# Built-in processors
class CoordinateTransformer:
    """Transform coordinates between coordinate systems"""
    
    def __init__(self, 
                 source_resolution: Tuple[int, int],
                 target_resolution: Tuple[int, int]):
        self.source_resolution = source_resolution
        self.target_resolution = target_resolution
        
    def __call__(self, action: Action) -> Action:
        """Transform action coordinates"""
        if hasattr(action, 'x') and hasattr(action, 'y'):
            action.x = int(action.x * self.target_resolution[0] / self.source_resolution[0])
            action.y = int(action.y * self.target_resolution[1] / self.source_resolution[1])
        return action

class TimingAdjuster:
    """Adjust action timing for playback speed"""
    
    def __init__(self, speed_multiplier: float):
        self.speed_multiplier = speed_multiplier
        
    def __call__(self, action: Action) -> Action:
        """Adjust action timing"""
        if hasattr(action, 'duration'):
            action.duration /= self.speed_multiplier
        return action
```

## Timing Engine API

### TimingEngine Class

Controls precise timing and synchronization during playback.

```python
from mkd.playback import TimingEngine

class TimingEngine:
    """Precise timing control for action execution"""
    
    def __init__(self, config: Dict):
        """Initialize timing engine with configuration"""
        
    def schedule_action(self, 
                       action: Action,
                       execution_time: float,
                       callback: Callable[[Action], None]) -> str:
        """
        Schedule action for future execution
        
        Args:
            action: Action to schedule
            execution_time: When to execute (timestamp)
            callback: Function to call when executing
            
        Returns:
            str: Schedule ID for cancellation
        """
        
    def cancel_action(self, schedule_id: str) -> bool:
        """Cancel scheduled action"""
        
    def set_playback_speed(self, speed: float) -> None:
        """
        Set playback speed multiplier
        
        Args:
            speed: Speed multiplier (0.1 to 10.0)
        """
        
    def pause_timing(self) -> None:
        """Pause timing engine"""
        
    def resume_timing(self) -> None:
        """Resume timing engine"""
        
    def sync_to_wall_clock(self, enabled: bool) -> None:
        """Enable/disable wall clock synchronization"""
        
    def get_timing_stats(self) -> TimingStats:
        """Get timing accuracy statistics"""
        
    def calibrate_timing(self) -> CalibrationResult:
        """Calibrate timing system for current platform"""

@dataclass
class TimingStats:
    """Timing engine statistics"""
    actions_scheduled: int
    actions_executed: int
    average_timing_error_ms: float
    max_timing_error_ms: float
    timing_accuracy_percent: float
    dropped_actions: int
    
@dataclass
class CalibrationResult:
    """Timing calibration results"""
    platform_latency_ms: float
    resolution_accuracy_us: float
    recommended_frame_rate: int
    calibration_score: float  # 0.0 to 1.0
```

## Error Handler API

### ErrorHandler Class

Manages error detection, recovery, and reporting during playback.

```python
from mkd.playback import ErrorHandler

class ErrorHandler:
    """Handle errors during playback execution"""
    
    def __init__(self, config: Dict):
        """Initialize error handler with configuration"""
        
    def handle_error(self, 
                    error: Exception,
                    action: Action,
                    context: Dict) -> ErrorHandlingResult:
        """
        Handle execution error
        
        Args:
            error: Exception that occurred
            action: Action that caused the error
            context: Additional context information
            
        Returns:
            ErrorHandlingResult: How to handle the error
        """
        
    def add_error_recovery(self, 
                          error_type: Type[Exception],
                          recovery_strategy: Callable[[Exception, Action], bool]) -> str:
        """
        Add custom error recovery strategy
        
        Args:
            error_type: Type of error to handle
            recovery_strategy: Function to attempt recovery
            
        Returns:
            str: Recovery strategy ID
        """
        
    def remove_error_recovery(self, strategy_id: str) -> bool:
        """Remove error recovery strategy"""
        
    def set_error_tolerance(self, tolerance: str) -> None:
        """
        Set error tolerance level
        
        Args:
            tolerance: 'strict', 'medium', 'lenient'
        """
        
    def get_error_stats(self) -> ErrorStats:
        """Get error handling statistics"""

@dataclass
class ErrorHandlingResult:
    """Result of error handling"""
    action: str  # 'retry', 'skip', 'stop', 'pause'
    retry_delay: float  # Delay before retry (if applicable)
    modified_action: Optional[Action]  # Modified action for retry
    error_logged: bool  # Whether error was logged
    
@dataclass
class ErrorStats:
    """Error handling statistics"""
    total_errors: int
    errors_by_type: Dict[str, int]
    recovery_success_rate: float
    critical_errors: int
    errors_resolved: int
```

### Built-in Error Recovery Strategies

```python
# Common error recovery strategies
class CoordinateRecoveryStrategy:
    """Recover from coordinate-related errors"""
    
    def __call__(self, error: Exception, action: Action) -> bool:
        """Attempt to recover from coordinate error"""
        if isinstance(error, CoordinateOutOfBoundsError):
            # Clamp coordinates to screen bounds
            screen_width, screen_height = get_screen_resolution()
            if hasattr(action, 'x'):
                action.x = max(0, min(action.x, screen_width - 1))
            if hasattr(action, 'y'):
                action.y = max(0, min(action.y, screen_height - 1))
            return True
        return False

class ApplicationRecoveryStrategy:
    """Recover from application-related errors"""
    
    def __call__(self, error: Exception, action: Action) -> bool:
        """Attempt to recover from application error"""
        if isinstance(error, ApplicationNotFoundError):
            # Try to find similar application
            similar_apps = find_similar_applications(action.target_application)
            if similar_apps:
                action.target_application = similar_apps[0]
                return True
        return False

class TimingRecoveryStrategy:
    """Recover from timing-related errors"""
    
    def __call__(self, error: Exception, action: Action) -> bool:
        """Attempt to recover from timing error"""
        if isinstance(error, TimingOverrunError):
            # Add buffer time
            if hasattr(action, 'duration'):
                action.duration *= 1.5
            return True
        return False
```

## Validator API

### ActionValidator Class

Validates actions before execution for compatibility and safety.

```python
from mkd.playback import ActionValidator

class ActionValidator:
    """Validate actions before execution"""
    
    def __init__(self, config: Dict):
        """Initialize validator with configuration"""
        
    def validate_action(self, action: Action) -> ValidationResult:
        """
        Validate single action
        
        Args:
            action: Action to validate
            
        Returns:
            ValidationResult: Validation results with errors/warnings
        """
        
    def validate_script(self, script: Script) -> ScriptValidationResult:
        """Validate entire script"""
        
    def validate_coordinates(self, x: int, y: int) -> bool:
        """Validate coordinate bounds"""
        
    def validate_timing(self, action: Action) -> bool:
        """Validate action timing parameters"""
        
    def validate_application_compatibility(self, 
                                         action: Action) -> CompatibilityResult:
        """Check if action is compatible with current system"""
        
    def add_validator(self, 
                     validator: Callable[[Action], ValidationResult],
                     priority: int = 0) -> str:
        """Add custom validator"""
        
    def remove_validator(self, validator_id: str) -> bool:
        """Remove custom validator"""

@dataclass
class ValidationResult:
    """Action validation result"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    confidence_score: float  # 0.0 to 1.0

@dataclass
class CompatibilityResult:
    """Compatibility check result"""
    is_compatible: bool
    platform_support: bool
    application_available: bool
    required_permissions: List[str]
    compatibility_score: float  # 0.0 to 1.0
```

## Action Models

### Core Action Models

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from abc import ABC, abstractmethod

@dataclass
class Action(ABC):
    """Base class for all actions"""
    type: str
    timestamp: float
    duration: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    @abstractmethod
    def execute(self, executor: ActionExecutor) -> ActionResult:
        """Execute this action"""
        pass

@dataclass
class ActionResult:
    """Result of action execution"""
    success: bool
    execution_time: float
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = None

# Mouse Actions
@dataclass
class MouseMoveAction(Action):
    x: int
    y: int
    path: Optional[List[Tuple[int, int]]] = None  # Path for smooth movement
    type: str = 'mouse_move'
    
    def execute(self, executor: ActionExecutor) -> ActionResult:
        return executor.execute_mouse_move(self)

@dataclass
class MouseClickAction(Action):
    x: int
    y: int
    button: str  # 'left', 'right', 'middle', 'x1', 'x2'
    click_count: int = 1
    hold_duration: Optional[float] = None
    type: str = 'mouse_click'
    
    def execute(self, executor: ActionExecutor) -> ActionResult:
        return executor.execute_mouse_click(self)

@dataclass
class MouseScrollAction(Action):
    x: int
    y: int
    delta_x: int = 0
    delta_y: int = 0
    scroll_type: str = 'wheel'  # 'wheel', 'trackpad'
    type: str = 'mouse_scroll'

@dataclass
class MouseDragAction(Action):
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    button: str = 'left'
    drag_path: Optional[List[Tuple[int, int]]] = None
    type: str = 'mouse_drag'

# Keyboard Actions
@dataclass
class KeyPressAction(Action):
    key: str
    modifiers: List[str] = None
    hold_duration: Optional[float] = None
    type: str = 'key_press'

@dataclass
class KeyReleaseAction(Action):
    key: str
    modifiers: List[str] = None
    type: str = 'key_release'

@dataclass
class TypeTextAction(Action):
    text: str
    typing_speed: Optional[float] = None  # Characters per second
    type: str = 'type_text'

@dataclass
class HotkeyAction(Action):
    keys: List[str]  # Combination of keys
    hold_duration: Optional[float] = None
    type: str = 'hotkey'

# Special Actions
@dataclass
class WaitAction(Action):
    wait_duration: float
    wait_type: str = 'fixed'  # 'fixed', 'random', 'condition'
    condition: Optional[str] = None
    type: str = 'wait'

@dataclass
class ScreenshotAction(Action):
    save_path: Optional[str] = None
    region: Optional[Tuple[int, int, int, int]] = None
    format: str = 'png'
    quality: int = 100
    type: str = 'screenshot'

@dataclass
class WindowAction(Action):
    window_title: str
    action: str  # 'focus', 'minimize', 'maximize', 'close', 'move', 'resize'
    parameters: Dict[str, Any] = None
    type: str = 'window'

@dataclass
class ApplicationAction(Action):
    application: str
    action: str  # 'launch', 'close', 'focus'
    parameters: Dict[str, Any] = None
    type: str = 'application'
```

### Advanced Action Models

```python
@dataclass
class ConditionalAction(Action):
    """Action that executes based on condition"""
    condition: str  # Python expression or predefined condition
    true_action: Action
    false_action: Optional[Action] = None
    type: str = 'conditional'

@dataclass
class LoopAction(Action):
    """Action that loops other actions"""
    actions: List[Action]
    loop_count: int
    loop_condition: Optional[str] = None
    type: str = 'loop'

@dataclass
class VariableAction(Action):
    """Action that sets or uses variables"""
    variable_name: str
    operation: str  # 'set', 'get', 'increment', 'decrement'
    value: Any = None
    type: str = 'variable'

@dataclass
class ScriptAction(Action):
    """Action that executes another script"""
    script_path: str
    parameters: Dict[str, Any] = None
    wait_for_completion: bool = True
    type: str = 'script'
```

## Configuration

### Playback Engine Configuration

```python
# Complete playback engine configuration
playback_engine_config = {
    'engine': {
        'max_concurrent_sessions': 5,    # Maximum concurrent playback sessions
        'session_timeout': 1800,         # Session timeout (seconds)
        'memory_limit_mb': 500,          # Memory limit per session
        'cpu_usage_limit': 0.8,          # CPU usage limit (0.0-1.0)
        'enable_gpu_acceleration': False, # Use GPU for graphics operations
        'thread_pool_size': 8            # Thread pool for parallel execution
    },
    
    'execution': {
        'default_speed': 1.0,
        'min_speed': 0.1,
        'max_speed': 10.0,
        'coordinate_mode': 'adaptive',    # 'absolute', 'relative', 'adaptive'
        'timing_mode': 'recorded',        # 'recorded', 'fixed', 'adaptive'
        'interpolation': {
            'enabled': True,
            'mouse_movement': True,       # Smooth mouse movements
            'timing_adjustment': True,    # Smooth timing transitions
            'algorithm': 'bezier'         # 'linear', 'bezier', 'spline'
        },
        'coordinate_adjustment': {
            'auto_scale': True,           # Auto-scale coordinates for resolution
            'maintain_aspect_ratio': True,
            'clamp_to_screen': True,      # Clamp coordinates to screen bounds
            'relative_positioning': True   # Use relative positioning when possible
        }
    },
    
    'error_handling': {
        'retry_attempts': 3,
        'retry_delay': 0.5,
        'exponential_backoff': True,     # Use exponential backoff for retries
        'continue_on_error': True,
        'pause_on_critical_error': True,
        'log_errors': True,
        'error_tolerance': 'medium',
        'recovery_strategies': {
            'coordinate_errors': True,    # Enable coordinate error recovery
            'application_errors': True,   # Enable application error recovery
            'timing_errors': True        # Enable timing error recovery
        }
    },
    
    'timing': {
        'frame_rate': 60,
        'timing_precision': 'millisecond',
        'jitter_compensation': {
            'enabled': True,
            'algorithm': 'kalman_filter', # 'simple', 'kalman_filter', 'adaptive'
            'compensation_threshold_ms': 5,
            'max_compensation_ms': 50
        },
        'adaptive_timing': {
            'enabled': True,
            'cpu_load_adjustment': True,  # Adjust timing based on CPU load
            'system_lag_detection': True, # Detect and compensate for system lag
            'performance_monitoring': True # Monitor performance and adjust
        }
    },
    
    'validation': {
        'pre_execution_validation': True,
        'runtime_validation': True,      # Validate during execution
        'screen_resolution_check': True,
        'application_compatibility_check': True,
        'coordinate_bounds_check': True,
        'action_compatibility_check': True,
        'safety_checks': {
            'prevent_system_actions': True, # Prevent dangerous system actions
            'coordinate_sanity_check': True,
            'timing_sanity_check': True,
            'file_path_validation': True
        }
    },
    
    'monitoring': {
        'enable_performance_monitoring': True,
        'enable_action_logging': True,
        'enable_timing_analysis': True,
        'enable_error_analytics': True,
        'metrics_collection_interval': 1.0, # Seconds
        'detailed_logging': False        # Enable detailed debug logging
    }
}
```

## Usage Examples

### Basic Playback

```python
from mkd.playback import PlaybackEngine

# Initialize playback engine
engine = PlaybackEngine()

# Load and play script
script_id = engine.load_script("automation.mkd")
session_id = engine.play(speed=2.0)

# Monitor playback
while True:
    status = engine.get_status()
    if not status.is_active:
        break
    
    print(f"Progress: {status.progress:.1%}")
    print(f"Current action: {status.current_action}/{status.total_actions}")
    time.sleep(1)

# Get final stats
stats = engine.stop()
print(f"Playback completed with {stats.success_rate:.1%} success rate")
```

### Advanced Playback Control

```python
from mkd.playback import PlaybackEngine

engine = PlaybackEngine()

# Configure error handling
engine.set_error_tolerance('lenient')

# Add custom action callback
def on_action_executed(event):
    if not event.success:
        print(f"Action failed: {event.action.type} - {event.error}")
    else:
        print(f"Action succeeded: {event.action.type}")

callback_id = engine.add_action_callback(on_action_executed)

# Load script with preprocessing
script_id = engine.load_script(
    "complex_automation.mkd",
    validate=True,
    preprocess=True
)

# Play with custom settings
session_id = engine.play(
    script_id=script_id,
    speed=1.5,
    start_action=20,      # Skip first 20 actions
    end_action=100,       # Stop at action 100
    pause_on_error=True   # Pause on any error
)

# Dynamic speed adjustment
time.sleep(5)
engine.set_speed(0.5)  # Slow down

# Seek to specific action
engine.seek(75)

# Resume normal speed
engine.set_speed(1.0)
```

### Custom Error Recovery

```python
from mkd.playback import PlaybackEngine, ErrorHandler

# Create custom error recovery strategy
def custom_recovery_strategy(error, action):
    """Custom recovery for network-related errors"""
    if isinstance(error, NetworkTimeoutError):
        # Wait and retry
        time.sleep(2)
        return True
    return False

# Initialize engine with custom error handling
engine = PlaybackEngine()
error_handler = engine.get_error_handler()

# Add custom recovery strategy
strategy_id = error_handler.add_error_recovery(
    NetworkTimeoutError,
    custom_recovery_strategy
)

# Configure error handling
error_handler.set_error_tolerance('medium')

# Load and play script
script_id = engine.load_script("network_automation.mkd")
session_id = engine.play(pause_on_error=False)
```

### Real-time Playback Monitoring

```python
from mkd.playback import PlaybackEngine
import threading
import time

class PlaybackMonitor:
    def __init__(self, engine):
        self.engine = engine
        self.running = False
        
    def start_monitoring(self):
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        self.running = False
        
    def _monitor_loop(self):
        while self.running:
            status = self.engine.get_status()
            
            if status.is_active:
                print(f"Progress: {status.progress:.1%}")
                print(f"Speed: {status.current_speed}x")
                print(f"ETA: {status.estimated_remaining:.1f}s")
                print(f"Errors: {status.error_count}")
                print("-" * 30)
                
            time.sleep(1)

# Setup monitoring
engine = PlaybackEngine()
monitor = PlaybackMonitor(engine)
monitor.start_monitoring()

# Start playback
script_id = engine.load_script("long_automation.mkd")
session_id = engine.play()

# Monitor will run in background
# Stop monitoring when done
monitor.stop_monitoring()
```

### Batch Playback

```python
from mkd.playback import PlaybackEngine
from concurrent.futures import ThreadPoolExecutor
import os

def play_script(script_path, speed=1.0):
    """Play single script"""
    engine = PlaybackEngine()
    try:
        script_id = engine.load_script(script_path)
        session_id = engine.play(speed=speed)
        
        # Wait for completion
        while engine.get_status().is_active:
            time.sleep(0.1)
            
        stats = engine.stop()
        return {
            'script': script_path,
            'success': stats.success_rate > 0.9,
            'stats': stats
        }
    except Exception as e:
        return {
            'script': script_path,
            'success': False,
            'error': str(e)
        }

# Find all script files
script_files = [f for f in os.listdir("scripts") if f.endswith(".mkd")]

# Run scripts in parallel
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(play_script, f"scripts/{script}", 2.0)
        for script in script_files
    ]
    
    results = [future.result() for future in futures]

# Print results
for result in results:
    status = "SUCCESS" if result['success'] else "FAILED"
    print(f"{result['script']}: {status}")
    if 'stats' in result:
        print(f"  Success rate: {result['stats'].success_rate:.1%}")
        print(f"  Duration: {result['stats'].duration:.1f}s")
```

### Interactive Playback

```python
from mkd.playback import PlaybackEngine
import keyboard

class InteractivePlayback:
    def __init__(self):
        self.engine = PlaybackEngine()
        self.setup_hotkeys()
        
    def setup_hotkeys(self):
        """Setup keyboard shortcuts for playback control"""
        keyboard.add_hotkey('space', self.toggle_pause)
        keyboard.add_hotkey('ctrl+right', self.speed_up)
        keyboard.add_hotkey('ctrl+left', self.speed_down)
        keyboard.add_hotkey('esc', self.stop_playback)
        
    def toggle_pause(self):
        """Toggle pause/resume"""
        status = self.engine.get_status()
        if status.is_active:
            if status.is_paused:
                self.engine.resume()
                print("Resumed playback")
            else:
                self.engine.pause()
                print("Paused playback")
                
    def speed_up(self):
        """Increase playback speed"""
        status = self.engine.get_status()
        if status.is_active:
            new_speed = min(status.current_speed * 1.5, 10.0)
            self.engine.set_speed(new_speed)
            print(f"Speed: {new_speed:.1f}x")
            
    def speed_down(self):
        """Decrease playback speed"""
        status = self.engine.get_status()
        if status.is_active:
            new_speed = max(status.current_speed / 1.5, 0.1)
            self.engine.set_speed(new_speed)
            print(f"Speed: {new_speed:.1f}x")
            
    def stop_playback(self):
        """Stop playback"""
        if self.engine.get_status().is_active:
            self.engine.stop()
            print("Stopped playback")
            
    def play_interactive(self, script_path):
        """Start interactive playback"""
        print("Interactive Playback Controls:")
        print("  Space: Pause/Resume")
        print("  Ctrl+Right: Speed Up")
        print("  Ctrl+Left: Speed Down")
        print("  Esc: Stop")
        print()
        
        script_id = self.engine.load_script(script_path)
        session_id = self.engine.play()
        
        # Wait for completion or stop
        while self.engine.get_status().is_active:
            time.sleep(0.1)
            
        print("Playback finished")

# Usage
player = InteractivePlayback()
player.play_interactive("interactive_demo.mkd")
```

This Playback Engine API provides comprehensive control over automation script execution, enabling developers to create sophisticated playback systems with advanced timing, error handling, and monitoring capabilities.