# MKD Automation - Core API Reference

## Table of Contents

- [Overview](#overview)
- [MKD Automation Main API](#mkd-automation-main-api)
- [Configuration Manager API](#configuration-manager-api)
- [Script Manager API](#script-manager-api)
- [Session Manager API](#session-manager-api)
- [Event System API](#event-system-api)
- [Data Models](#data-models)
- [Exceptions](#exceptions)
- [Usage Examples](#usage-examples)

## Overview

The MKD Automation Core API provides the primary interface for programmatic access to the automation system. This API allows developers to integrate MKD functionality into their applications, create custom automation workflows, and extend the platform's capabilities.

### API Principles

- **Thread-Safe**: All API calls are thread-safe unless explicitly noted
- **Event-Driven**: Extensive use of event callbacks for real-time feedback
- **Extensible**: Plugin-friendly architecture for custom extensions
- **Cross-Platform**: Consistent behavior across Windows, macOS, and Linux

## MKD Automation Main API

### MKDAutomation Class

The main entry point for all MKD automation functionality.

```python
from mkd import MKDAutomation

class MKDAutomation:
    """Main interface for MKD automation functionality"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MKD automation system
        
        Args:
            config_path: Optional path to configuration file
        """
```

#### Core Methods

##### Recording Operations

```python
def start_recording(self, 
                   output_path: Optional[str] = None,
                   filters: Optional[List[str]] = None,
                   options: Optional[Dict[str, Any]] = None) -> str:
    """
    Start recording user interactions
    
    Args:
        output_path: Path where recording will be saved (optional)
        filters: List of event filters to apply ['mouse', 'keyboard', 'display']
        options: Additional recording options
            {
                'sample_rate': 60,        # Mouse sampling rate (Hz)
                'compress': True,         # Enable compression
                'encrypt': True,          # Enable encryption
                'metadata': {...}         # Additional metadata
            }
    
    Returns:
        str: Recording session ID
    
    Raises:
        RecordingAlreadyActiveError: If recording is already in progress
        PlatformNotSupportedError: If platform is not supported
        PermissionError: If required permissions are not available
    
    Example:
        >>> mkd = MKDAutomation()
        >>> session_id = mkd.start_recording(
        ...     output_path="my_automation.mkd",
        ...     filters=['mouse', 'keyboard'],
        ...     options={'sample_rate': 30}
        ... )
    """

def stop_recording(self, save: bool = True) -> Optional[str]:
    """
    Stop current recording session
    
    Args:
        save: Whether to save the recording to file
    
    Returns:
        Optional[str]: Path to saved file if save=True, None otherwise
    
    Raises:
        NoActiveRecordingError: If no recording is in progress
        FileWriteError: If unable to save recording file
    
    Example:
        >>> file_path = mkd.stop_recording(save=True)
        >>> print(f"Recording saved to: {file_path}")
    """

def pause_recording(self) -> None:
    """
    Pause current recording session
    
    Raises:
        NoActiveRecordingError: If no recording is in progress
        RecordingAlreadyPausedError: If recording is already paused
    """

def resume_recording(self) -> None:
    """
    Resume paused recording session
    
    Raises:
        NoActiveRecordingError: If no recording is in progress
        RecordingNotPausedError: If recording is not paused
    """

def get_recording_status(self) -> RecordingStatus:
    """
    Get current recording status
    
    Returns:
        RecordingStatus: Current recording state and metadata
        
    Example:
        >>> status = mkd.get_recording_status()
        >>> print(f"Recording: {status.is_active}, Duration: {status.duration}")
    """
```

##### Playback Operations

```python
def load_script(self, script_path: str, validate: bool = True) -> None:
    """
    Load automation script for playback
    
    Args:
        script_path: Path to .mkd script file
        validate: Whether to validate script before loading
    
    Raises:
        FileNotFoundError: If script file doesn't exist
        ScriptValidationError: If script validation fails
        DecryptionError: If unable to decrypt encrypted script
    
    Example:
        >>> mkd.load_script("my_automation.mkd")
    """

def play(self, 
         speed: float = 1.0,
         loop: bool = False,
         start_action: int = 0,
         end_action: Optional[int] = None) -> str:
    """
    Start playback of loaded script
    
    Args:
        speed: Playback speed multiplier (0.1 to 10.0)
        loop: Whether to loop playback continuously
        start_action: Index of first action to play (0-based)
        end_action: Index of last action to play (None for end of script)
    
    Returns:
        str: Playback session ID
    
    Raises:
        NoScriptLoadedError: If no script is loaded
        PlaybackAlreadyActiveError: If playback is already in progress
        InvalidSpeedError: If speed is outside valid range
    
    Example:
        >>> session_id = mkd.play(speed=2.0, loop=False)
    """

def pause_playback(self) -> None:
    """Pause current playback session"""

def resume_playback(self) -> None:
    """Resume paused playback session"""

def stop_playback(self) -> None:
    """Stop current playback session"""

def get_playback_status(self) -> PlaybackStatus:
    """
    Get current playback status
    
    Returns:
        PlaybackStatus: Current playback state and progress
    """
```

##### Event Handling

```python
def add_event_listener(self, 
                      event_type: str, 
                      callback: Callable[[Any], None]) -> None:
    """
    Add event listener for system events
    
    Args:
        event_type: Type of event to listen for
            - 'recording_started'
            - 'recording_stopped' 
            - 'recording_paused'
            - 'playback_started'
            - 'playback_stopped'
            - 'playback_paused'
            - 'action_executed'
            - 'error_occurred'
        callback: Function to call when event occurs
    
    Example:
        >>> def on_recording_started(event_data):
        ...     print("Recording started!")
        >>> mkd.add_event_listener('recording_started', on_recording_started)
    """

def remove_event_listener(self, event_type: str, callback: Callable) -> None:
    """Remove previously added event listener"""

def get_supported_events(self) -> List[str]:
    """Get list of supported event types"""
```

## Configuration Manager API

### ConfigManager Class

Manages application configuration and settings.

```python
from mkd.core import ConfigManager

class ConfigManager:
    """Centralized configuration management"""
    
    @classmethod
    def get_instance(cls) -> 'ConfigManager':
        """Get singleton instance of ConfigManager"""
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key (dot notation supported: 'recording.sample_rate')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Example:
            >>> config = ConfigManager.get_instance()
            >>> sample_rate = config.get('recording.sample_rate', 60)
        """
    
    def set(self, key: str, value: Any, persist: bool = True) -> None:
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Value to set
            persist: Whether to save to disk immediately
        """
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
    
    def save(self) -> None:
        """Save configuration to disk"""
    
    def load(self, config_path: Optional[str] = None) -> None:
        """Load configuration from file"""
    
    def reset_to_defaults(self) -> None:
        """Reset all configuration to default values"""
    
    def validate_config(self) -> List[str]:
        """
        Validate current configuration
        
        Returns:
            List of validation error messages (empty if valid)
        """
```

### Configuration Schema

#### Recording Configuration

```python
recording_config = {
    'sample_rate': 60,           # Mouse sampling rate (Hz)
    'keyboard_capture': True,     # Capture keyboard events
    'mouse_capture': True,        # Capture mouse events
    'display_capture': True,      # Capture display events
    'auto_save': False,          # Auto-save recordings
    'compression': True,         # Enable compression
    'filters': {
        'mouse': {
            'min_movement': 2,    # Minimum movement threshold (pixels)
            'smooth_movements': True,  # Enable movement smoothing
            'ignore_micro_movements': True
        },
        'keyboard': {
            'capture_modifiers': True,  # Capture modifier keys
            'capture_function_keys': True,
            'ignore_repetition': True
        }
    }
}
```

#### Playback Configuration

```python
playback_config = {
    'default_speed': 1.0,        # Default playback speed
    'coordinate_mode': 'relative', # 'relative' or 'absolute'
    'error_handling': {
        'retry_attempts': 3,      # Number of retry attempts
        'retry_delay': 0.5,       # Delay between retries (seconds)
        'continue_on_error': True, # Continue playback on non-critical errors
        'log_errors': True        # Log errors to file
    },
    'timing': {
        'precision_mode': 'high', # 'low', 'medium', 'high'
        'jitter_compensation': True,
        'frame_rate': 60          # Target frame rate for smooth playback
    }
}
```

## Script Manager API

### ScriptManager Class

Handles automation script operations.

```python
from mkd.core import ScriptManager

class ScriptManager:
    """Automation script lifecycle management"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize script manager with optional storage path"""
    
    def create_script(self, 
                     name: str,
                     actions: List[Dict],
                     metadata: Optional[Dict] = None) -> str:
        """
        Create new automation script
        
        Args:
            name: Script name
            actions: List of action dictionaries
            metadata: Optional script metadata
        
        Returns:
            str: Script ID
        """
    
    def save_script(self, 
                   script_id: str, 
                   file_path: str,
                   encrypt: bool = True) -> None:
        """
        Save script to file
        
        Args:
            script_id: Script identifier
            file_path: Target file path
            encrypt: Whether to encrypt the file
        """
    
    def load_script(self, file_path: str) -> str:
        """
        Load script from file
        
        Args:
            file_path: Path to script file
            
        Returns:
            str: Loaded script ID
        """
    
    def get_script(self, script_id: str) -> Dict:
        """Get script data by ID"""
    
    def delete_script(self, script_id: str) -> None:
        """Delete script by ID"""
    
    def list_scripts(self) -> List[Dict]:
        """List all loaded scripts with metadata"""
    
    def validate_script(self, script_id: str) -> ValidationResult:
        """
        Validate script structure and content
        
        Returns:
            ValidationResult: Validation results with errors/warnings
        """
    
    def get_script_info(self, script_id: str) -> ScriptInfo:
        """Get detailed script information"""
```

### Script Data Structure

```python
script_structure = {
    'version': '1.0',           # Script format version
    'metadata': {
        'name': 'My Automation',
        'description': 'Automation description',
        'created': '2024-01-01T00:00:00Z',
        'modified': '2024-01-01T00:00:00Z',
        'author': 'User Name',
        'tags': ['demo', 'testing'],
        'duration': 30.5,       # Total duration in seconds
        'platform': 'cross',   # 'windows', 'macos', 'linux', 'cross'
        'resolution': [1920, 1080]  # Screen resolution when recorded
    },
    'settings': {
        'coordinate_mode': 'relative',
        'timing_mode': 'recorded',  # 'recorded', 'fixed', 'manual'
        'error_tolerance': 'medium'
    },
    'actions': [
        {
            'type': 'mouse_move',
            'timestamp': 0.0,
            'x': 100,
            'y': 200,
            'duration': 0.5
        },
        {
            'type': 'mouse_click',
            'timestamp': 0.5,
            'x': 100,
            'y': 200,
            'button': 'left',
            'duration': 0.1
        },
        {
            'type': 'key_press',
            'timestamp': 1.0,
            'key': 'a',
            'modifiers': ['ctrl'],
            'duration': 0.1
        }
    ]
}
```

## Session Manager API

### SessionManager Class

Manages recording and playback sessions.

```python
from mkd.core import SessionManager

class SessionManager:
    """Recording and playback session management"""
    
    def create_recording_session(self, options: Dict) -> str:
        """Create new recording session"""
    
    def create_playback_session(self, script_id: str, options: Dict) -> str:
        """Create new playback session"""
    
    def get_session(self, session_id: str) -> Session:
        """Get session by ID"""
    
    def get_active_sessions(self) -> List[Session]:
        """Get all active sessions"""
    
    def terminate_session(self, session_id: str) -> None:
        """Terminate specific session"""
    
    def terminate_all_sessions(self) -> None:
        """Terminate all active sessions"""
    
    def get_session_stats(self, session_id: str) -> SessionStats:
        """Get session statistics and metrics"""
```

## Event System API

### Event Types and Payloads

```python
# Recording Events
recording_started_event = {
    'type': 'recording_started',
    'session_id': 'session_123',
    'timestamp': '2024-01-01T00:00:00Z',
    'output_path': '/path/to/recording.mkd',
    'options': {...}
}

recording_stopped_event = {
    'type': 'recording_stopped',
    'session_id': 'session_123',
    'timestamp': '2024-01-01T00:05:30Z',
    'duration': 330.5,
    'actions_recorded': 150,
    'file_size': 1024
}

# Playback Events
playback_started_event = {
    'type': 'playback_started',
    'session_id': 'playback_456',
    'script_id': 'script_789',
    'timestamp': '2024-01-01T00:10:00Z',
    'total_actions': 150,
    'estimated_duration': 330.5
}

action_executed_event = {
    'type': 'action_executed',
    'session_id': 'playback_456',
    'action_index': 42,
    'action_type': 'mouse_click',
    'timestamp': '2024-01-01T00:10:15Z',
    'success': True,
    'execution_time': 0.005
}

# Error Events
error_occurred_event = {
    'type': 'error_occurred',
    'session_id': 'session_123',
    'error_type': 'ActionExecutionError',
    'error_message': 'Unable to click at coordinates (100, 200)',
    'action_index': 42,
    'timestamp': '2024-01-01T00:10:15Z',
    'recoverable': True
}
```

## Data Models

### Core Data Models

```python
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SessionState(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class RecordingStatus:
    is_active: bool
    is_paused: bool
    duration: float
    actions_recorded: int
    session_id: Optional[str]
    output_path: Optional[str]
    start_time: Optional[datetime]
    
@dataclass  
class PlaybackStatus:
    is_active: bool
    is_paused: bool
    progress: float  # 0.0 to 1.0
    current_action: int
    total_actions: int
    session_id: Optional[str]
    script_id: Optional[str]
    elapsed_time: float
    estimated_remaining: float

@dataclass
class ScriptInfo:
    script_id: str
    name: str
    description: Optional[str]
    created: datetime
    modified: datetime
    file_size: int
    action_count: int
    duration: float
    platform: str
    tags: List[str]

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    
@dataclass
class SessionStats:
    session_id: str
    session_type: str  # 'recording' or 'playback'
    start_time: datetime
    end_time: Optional[datetime]
    duration: float
    success_rate: float
    error_count: int
    performance_metrics: Dict[str, Any]
```

### Action Models

```python
@dataclass
class BaseAction:
    type: str
    timestamp: float
    duration: Optional[float] = None

@dataclass
class MouseAction(BaseAction):
    x: int
    y: int
    
@dataclass
class MouseMoveAction(MouseAction):
    type: str = 'mouse_move'
    
@dataclass
class MouseClickAction(MouseAction):
    button: str  # 'left', 'right', 'middle'
    type: str = 'mouse_click'
    
@dataclass
class KeyboardAction(BaseAction):
    key: str
    modifiers: List[str] = None  # ['ctrl', 'alt', 'shift', 'cmd']
    
@dataclass
class KeyPressAction(KeyboardAction):
    type: str = 'key_press'
    
@dataclass
class KeyReleaseAction(KeyboardAction):
    type: str = 'key_release'
    
@dataclass
class TypeTextAction(BaseAction):
    text: str
    type: str = 'type_text'
```

## Exceptions

### Core Exceptions

```python
class MKDError(Exception):
    """Base exception for all MKD errors"""
    pass

class RecordingError(MKDError):
    """Base class for recording-related errors"""
    pass

class RecordingAlreadyActiveError(RecordingError):
    """Raised when trying to start recording while already recording"""
    pass

class NoActiveRecordingError(RecordingError):
    """Raised when trying to stop/pause recording when none is active"""
    pass

class PlaybackError(MKDError):
    """Base class for playback-related errors"""
    pass

class PlaybackAlreadyActiveError(PlaybackError):
    """Raised when trying to start playback while already playing"""
    pass

class NoScriptLoadedError(PlaybackError):
    """Raised when trying to play without loading a script"""
    pass

class ScriptError(MKDError):
    """Base class for script-related errors"""
    pass

class ScriptValidationError(ScriptError):
    """Raised when script validation fails"""
    pass

class ScriptNotFoundError(ScriptError):
    """Raised when script file is not found"""
    pass

class PlatformError(MKDError):
    """Base class for platform-related errors"""
    pass

class PlatformNotSupportedError(PlatformError):
    """Raised when current platform is not supported"""
    pass

class PermissionError(MKDError):
    """Raised when required permissions are not available"""
    pass
```

## Usage Examples

### Basic Recording and Playback

```python
from mkd import MKDAutomation

# Initialize MKD
mkd = MKDAutomation()

# Set up event listeners
def on_recording_started(event_data):
    print(f"Recording started: {event_data['session_id']}")

def on_action_executed(event_data):
    print(f"Executed action {event_data['action_index']}: {event_data['action_type']}")

mkd.add_event_listener('recording_started', on_recording_started)
mkd.add_event_listener('action_executed', on_action_executed)

# Record automation
session_id = mkd.start_recording(
    output_path="my_automation.mkd",
    options={
        'sample_rate': 30,
        'compress': True,
        'encrypt': True
    }
)

# ... perform manual actions ...

# Stop recording
file_path = mkd.stop_recording(save=True)
print(f"Recording saved to: {file_path}")

# Later, playback the recording
mkd.load_script(file_path)
mkd.play(speed=1.5, loop=False)
```

### Advanced Configuration

```python
from mkd.core import ConfigManager

# Get configuration manager
config = ConfigManager.get_instance()

# Customize recording settings
config.set('recording.sample_rate', 120)
config.set('recording.filters.mouse.min_movement', 5)
config.set('playback.error_handling.retry_attempts', 5)

# Save configuration
config.save()

# Create automation with custom config
mkd = MKDAutomation()
```

### Script Manipulation

```python
from mkd.core import ScriptManager

# Initialize script manager
script_mgr = ScriptManager()

# Create script programmatically
actions = [
    {
        'type': 'mouse_move',
        'timestamp': 0.0,
        'x': 100,
        'y': 200,
        'duration': 0.5
    },
    {
        'type': 'mouse_click',
        'timestamp': 0.5,
        'x': 100,
        'y': 200,
        'button': 'left'
    }
]

script_id = script_mgr.create_script(
    name="Custom Automation",
    actions=actions,
    metadata={
        'description': 'Programmatically created script',
        'tags': ['custom', 'api']
    }
)

# Save to file
script_mgr.save_script(script_id, "custom_automation.mkd", encrypt=True)

# Validate script
validation = script_mgr.validate_script(script_id)
if not validation.is_valid:
    print("Validation errors:", validation.errors)
```

### Session Management

```python
from mkd.core import SessionManager

# Get session manager
session_mgr = SessionManager()

# Monitor sessions
active_sessions = session_mgr.get_active_sessions()
for session in active_sessions:
    stats = session_mgr.get_session_stats(session.session_id)
    print(f"Session {session.session_id}: {stats.success_rate:.2%} success rate")

# Terminate specific session if needed
if len(active_sessions) > 0:
    session_mgr.terminate_session(active_sessions[0].session_id)
```

### Error Handling

```python
from mkd import MKDAutomation, RecordingAlreadyActiveError, PlatformNotSupportedError

mkd = MKDAutomation()

try:
    # Start recording
    session_id = mkd.start_recording()
    
    # Try to start another recording (will fail)
    another_session = mkd.start_recording()
    
except RecordingAlreadyActiveError:
    print("Recording already in progress")
    
except PlatformNotSupportedError as e:
    print(f"Platform not supported: {e}")
    
except PermissionError as e:
    print(f"Permission denied: {e}")
    print("Make sure MKD has necessary permissions for input capture")
    
finally:
    # Always clean up
    if mkd.get_recording_status().is_active:
        mkd.stop_recording()
```

This Core API reference provides comprehensive documentation for integrating MKD Automation into applications and scripts. The API is designed to be intuitive while providing powerful functionality for automation tasks.