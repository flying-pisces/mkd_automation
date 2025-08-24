# MKD Automation - Recording Engine API Reference

## Table of Contents

- [Overview](#overview)
- [Recording Engine API](#recording-engine-api)
- [Input Capturer API](#input-capturer-api)
- [Event Processor API](#event-processor-api)
- [Motion Analyzer API](#motion-analyzer-api)
- [Filter System API](#filter-system-api)
- [Event Models](#event-models)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)

## Overview

The Recording Engine API provides low-level access to MKD's input capture and recording functionality. This API is designed for developers who need fine-grained control over the recording process or want to integrate recording capabilities into custom applications.

### Key Features

- **Real-time Input Capture**: Mouse, keyboard, and display event capture
- **Cross-platform Compatibility**: Unified API across Windows, macOS, and Linux
- **Advanced Filtering**: Customizable event filtering and processing
- **Motion Analysis**: Intelligent mouse movement pattern recognition
- **High Performance**: Optimized for minimal system impact
- **Event-driven Architecture**: Asynchronous event handling with callbacks

## Recording Engine API

### RecordingEngine Class

The main recording engine class that orchestrates all recording operations.

```python
from mkd.recording import RecordingEngine

class RecordingEngine:
    """Main recording engine for capturing user interactions"""
    
    def __init__(self, 
                 config: Optional[Dict] = None,
                 event_bus: Optional[EventBus] = None):
        """
        Initialize recording engine
        
        Args:
            config: Recording configuration dictionary
            event_bus: Event bus for inter-component communication
        """
        
    def start(self, 
              output_handler: Callable[[Event], None],
              filters: Optional[List[str]] = None,
              options: Optional[Dict] = None) -> None:
        """
        Start recording user interactions
        
        Args:
            output_handler: Function to handle captured events
            filters: List of event types to capture ['mouse', 'keyboard', 'display']
            options: Additional recording options
                {
                    'sample_rate': 60,          # Mouse sampling rate
                    'buffer_size': 1000,        # Event buffer size
                    'enable_motion_analysis': True,  # Enable motion analysis
                    'coordinate_mode': 'absolute',   # 'absolute' or 'relative'
                    'precision_mode': 'high'    # 'low', 'medium', 'high'
                }
        
        Raises:
            RecordingAlreadyActiveError: If recording is already active
            PlatformNotSupportedError: If platform doesn't support recording
            PermissionError: If required permissions aren't available
            
        Example:
            >>> def handle_event(event):
            ...     print(f"Captured: {event.type} at {event.timestamp}")
            >>> 
            >>> engine = RecordingEngine()
            >>> engine.start(
            ...     output_handler=handle_event,
            ...     filters=['mouse', 'keyboard'],
            ...     options={'sample_rate': 30}
            ... )
        """
        
    def stop(self) -> RecordingStats:
        """
        Stop recording and return statistics
        
        Returns:
            RecordingStats: Recording session statistics
            
        Raises:
            NoActiveRecordingError: If no recording is active
        """
        
    def pause(self) -> None:
        """
        Pause current recording session
        
        Raises:
            NoActiveRecordingError: If no recording is active
            RecordingAlreadyPausedError: If already paused
        """
        
    def resume(self) -> None:
        """
        Resume paused recording session
        
        Raises:
            NoActiveRecordingError: If no recording is active
            RecordingNotPausedError: If not currently paused
        """
        
    def get_status(self) -> RecordingEngineStatus:
        """
        Get current recording status
        
        Returns:
            RecordingEngineStatus: Current engine status and metrics
        """
        
    def add_filter(self, filter_func: Callable[[Event], bool]) -> str:
        """
        Add custom event filter
        
        Args:
            filter_func: Function that returns True if event should be kept
            
        Returns:
            str: Filter ID for later removal
        """
        
    def remove_filter(self, filter_id: str) -> bool:
        """
        Remove previously added filter
        
        Args:
            filter_id: ID returned by add_filter
            
        Returns:
            bool: True if filter was removed, False if not found
        """
        
    def set_event_callback(self, 
                          event_type: str, 
                          callback: Callable[[Event], None]) -> None:
        """
        Set callback for specific event types
        
        Args:
            event_type: Event type ('mouse_move', 'key_press', etc.)
            callback: Function to call when event occurs
        """
```

### Recording Configuration

```python
recording_config = {
    # Input capture settings
    'capture': {
        'mouse': {
            'enabled': True,
            'sample_rate': 60,              # Hz
            'capture_movement': True,
            'capture_clicks': True,
            'capture_scroll': True,
            'coordinate_mode': 'absolute'   # 'absolute' or 'relative'
        },
        'keyboard': {
            'enabled': True,
            'capture_keys': True,
            'capture_modifiers': True,
            'capture_function_keys': True,
            'capture_special_keys': True
        },
        'display': {
            'enabled': True,
            'capture_window_events': True,
            'capture_resolution_changes': True,
            'monitor_focus_changes': True
        }
    },
    
    # Processing settings
    'processing': {
        'buffer_size': 1000,            # Event buffer size
        'batch_size': 50,               # Events processed per batch
        'enable_filtering': True,       # Enable event filtering
        'enable_motion_analysis': True,  # Enable motion pattern analysis
        'enable_compression': True      # Compress event data
    },
    
    # Performance settings
    'performance': {
        'precision_mode': 'high',       # 'low', 'medium', 'high'
        'cpu_usage_limit': 0.1,         # Max CPU usage (0.0-1.0)
        'memory_limit_mb': 100,         # Max memory usage
        'thread_pool_size': 4           # Number of processing threads
    }
}
```

## Input Capturer API

### InputCapturer Class

Low-level input capture functionality.

```python
from mkd.recording import InputCapturer

class InputCapturer:
    """Low-level input event capture"""
    
    def __init__(self, platform_handler: PlatformInterface):
        """Initialize with platform-specific handler"""
        
    def start_capture(self, 
                     event_types: List[str],
                     callback: Callable[[RawEvent], None]) -> None:
        """
        Start capturing input events
        
        Args:
            event_types: Types of events to capture
                ['mouse_move', 'mouse_click', 'key_press', 'key_release', 'scroll']
            callback: Function to receive raw events
        """
        
    def stop_capture(self) -> None:
        """Stop input capture"""
        
    def get_capture_stats(self) -> CaptureStats:
        """Get capture statistics and performance metrics"""
        
    def set_sample_rate(self, rate: int) -> None:
        """Set mouse movement sampling rate (Hz)"""
        
    def enable_raw_mode(self, enabled: bool) -> None:
        """Enable/disable raw event mode (bypasses processing)"""
```

### Platform-Specific Handlers

```python
# Windows Implementation
class WindowsInputCapturer(InputCapturer):
    """Windows-specific input capture using Win32 API"""
    
    def _setup_mouse_hook(self) -> None:
        """Setup low-level mouse hook"""
        
    def _setup_keyboard_hook(self) -> None:
        """Setup low-level keyboard hook"""
        
    def _handle_raw_input(self, message: int, wparam: int, lparam: int) -> None:
        """Handle raw input messages"""

# macOS Implementation  
class MacOSInputCapturer(InputCapturer):
    """macOS-specific input capture using Quartz Event Services"""
    
    def _create_event_tap(self) -> None:
        """Create CGEvent tap for input monitoring"""
        
    def _handle_cg_event(self, proxy, event_type, event, refcon) -> Optional[CGEvent]:
        """Handle Core Graphics events"""

# Linux Implementation
class LinuxInputCapturer(InputCapturer):
    """Linux-specific input capture using X11/evdev"""
    
    def _setup_x11_capture(self) -> None:
        """Setup X11 event capture"""
        
    def _setup_evdev_capture(self) -> None:
        """Setup evdev input device monitoring"""
```

## Event Processor API

### EventProcessor Class

Processes and enriches captured events.

```python
from mkd.recording import EventProcessor

class EventProcessor:
    """Process and enrich captured input events"""
    
    def __init__(self, config: Dict):
        """Initialize event processor with configuration"""
        
    def process_event(self, raw_event: RawEvent) -> Optional[ProcessedEvent]:
        """
        Process raw input event
        
        Args:
            raw_event: Raw event from input capturer
            
        Returns:
            ProcessedEvent: Processed event or None if filtered out
        """
        
    def add_processor(self, 
                     processor: Callable[[RawEvent], Optional[ProcessedEvent]],
                     priority: int = 0) -> str:
        """
        Add custom event processor
        
        Args:
            processor: Processing function
            priority: Processing priority (higher = earlier)
            
        Returns:
            str: Processor ID for later removal
        """
        
    def remove_processor(self, processor_id: str) -> bool:
        """Remove event processor by ID"""
        
    def set_batch_size(self, size: int) -> None:
        """Set batch processing size"""
        
    def get_processing_stats(self) -> ProcessingStats:
        """Get event processing statistics"""
```

### Event Processing Pipeline

```python
# Processing pipeline stages
processing_pipeline = [
    'validation',        # Validate event structure and data
    'normalization',     # Normalize coordinates and timing
    'deduplication',     # Remove duplicate events
    'filtering',         # Apply user-defined filters
    'enrichment',        # Add metadata and context
    'optimization',      # Optimize for storage/transmission
    'serialization'      # Prepare for storage
]

class EventProcessingPipeline:
    """Configurable event processing pipeline"""
    
    def __init__(self):
        self.stages = []
        
    def add_stage(self, 
                  stage: Callable[[Event], Event],
                  name: str,
                  position: Optional[int] = None) -> None:
        """Add processing stage to pipeline"""
        
    def process(self, event: RawEvent) -> Optional[ProcessedEvent]:
        """Process event through all pipeline stages"""
        
    def get_stage_metrics(self) -> Dict[str, StageMetrics]:
        """Get performance metrics for each pipeline stage"""
```

## Motion Analyzer API

### MotionAnalyzer Class

Analyzes mouse movement patterns for optimization and gesture recognition.

```python
from mkd.recording import MotionAnalyzer

class MotionAnalyzer:
    """Analyze and optimize mouse movement patterns"""
    
    def __init__(self, config: Dict):
        """Initialize motion analyzer with configuration"""
        
    def analyze_movement(self, 
                        movement_sequence: List[MouseMoveEvent]) -> MotionAnalysis:
        """
        Analyze sequence of mouse movements
        
        Args:
            movement_sequence: List of mouse move events
            
        Returns:
            MotionAnalysis: Analysis results with patterns and optimizations
        """
        
    def detect_gestures(self, 
                       movement_sequence: List[MouseMoveEvent]) -> List[Gesture]:
        """
        Detect mouse gestures in movement sequence
        
        Args:
            movement_sequence: List of mouse move events
            
        Returns:
            List[Gesture]: Detected gestures
        """
        
    def optimize_path(self, 
                     movement_sequence: List[MouseMoveEvent],
                     optimization_level: str = 'medium') -> List[MouseMoveEvent]:
        """
        Optimize mouse movement path
        
        Args:
            movement_sequence: Original movement sequence
            optimization_level: 'low', 'medium', 'high'
            
        Returns:
            List[MouseMoveEvent]: Optimized movement sequence
        """
        
    def calculate_smoothness(self, 
                           movement_sequence: List[MouseMoveEvent]) -> float:
        """
        Calculate movement smoothness score (0.0 to 1.0)
        
        Args:
            movement_sequence: Mouse movement sequence
            
        Returns:
            float: Smoothness score
        """
        
    def get_movement_stats(self, 
                          movement_sequence: List[MouseMoveEvent]) -> MovementStats:
        """Get detailed movement statistics"""
```

### Motion Analysis Features

```python
@dataclass
class MotionAnalysis:
    """Results of motion analysis"""
    total_distance: float           # Total movement distance (pixels)
    average_speed: float           # Average movement speed (pixels/second)
    max_speed: float              # Maximum movement speed
    smoothness_score: float       # Movement smoothness (0.0-1.0)
    direction_changes: int        # Number of direction changes
    pause_count: int             # Number of movement pauses
    detected_patterns: List[str]  # Recognized movement patterns
    optimization_suggestions: List[str]  # Suggested optimizations

@dataclass
class Gesture:
    """Detected mouse gesture"""
    type: str                    # Gesture type (circle, line, zigzag, etc.)
    confidence: float            # Detection confidence (0.0-1.0)
    start_time: float           # Gesture start timestamp
    end_time: float             # Gesture end timestamp
    bounding_box: Tuple[int, int, int, int]  # Gesture bounding box
    parameters: Dict[str, Any]   # Gesture-specific parameters

# Supported gesture types
gesture_types = [
    'straight_line',    # Straight line movement
    'circle',          # Circular movement
    'rectangle',       # Rectangular movement
    'zigzag',          # Zigzag pattern
    'spiral',          # Spiral movement
    'free_form',       # Unrecognized free-form movement
    'click_drag',      # Click and drag gesture
    'double_click',    # Double-click gesture
    'hover',           # Hover/pause gesture
]
```

## Filter System API

### EventFilter Classes

```python
from mkd.recording.filters import EventFilter

class EventFilter(ABC):
    """Base class for event filters"""
    
    @abstractmethod
    def should_capture(self, event: RawEvent) -> bool:
        """
        Determine if event should be captured
        
        Args:
            event: Raw input event
            
        Returns:
            bool: True if event should be captured
        """
        
    @abstractmethod
    def get_filter_name(self) -> str:
        """Get human-readable filter name"""

# Built-in filters
class MinimumMovementFilter(EventFilter):
    """Filter out mouse movements below threshold"""
    
    def __init__(self, threshold_pixels: int = 2):
        self.threshold = threshold_pixels
        
    def should_capture(self, event: RawEvent) -> bool:
        if event.type == 'mouse_move':
            distance = math.sqrt(event.dx**2 + event.dy**2)
            return distance >= self.threshold
        return True

class DuplicateEventFilter(EventFilter):
    """Filter out duplicate consecutive events"""
    
    def __init__(self, time_window_ms: int = 10):
        self.time_window = time_window_ms / 1000.0
        self.last_events = {}
        
class KeyRepeatFilter(EventFilter):
    """Filter out keyboard repeat events"""
    
    def __init__(self, ignore_repeats: bool = True):
        self.ignore_repeats = ignore_repeats
        
class ApplicationFilter(EventFilter):
    """Filter events by application window"""
    
    def __init__(self, 
                 include_apps: Optional[List[str]] = None,
                 exclude_apps: Optional[List[str]] = None):
        self.include_apps = include_apps or []
        self.exclude_apps = exclude_apps or []

class RegionFilter(EventFilter):
    """Filter events by screen region"""
    
    def __init__(self, regions: List[Tuple[int, int, int, int]]):
        """
        Initialize with list of regions
        
        Args:
            regions: List of (x, y, width, height) tuples
        """
```

### Filter Configuration

```python
filter_config = {
    'mouse_filters': {
        'minimum_movement': {
            'enabled': True,
            'threshold_pixels': 2
        },
        'duplicate_events': {
            'enabled': True,
            'time_window_ms': 10
        },
        'outside_bounds': {
            'enabled': False,
            'bounds': (0, 0, 1920, 1080)
        }
    },
    'keyboard_filters': {
        'key_repeat': {
            'enabled': True,
            'ignore_auto_repeat': True
        },
        'modifier_only': {
            'enabled': False,
            'ignore_modifier_only': True
        }
    },
    'application_filters': {
        'whitelist': {
            'enabled': False,
            'applications': []
        },
        'blacklist': {
            'enabled': True,
            'applications': ['password_manager', 'secure_input']
        }
    }
}
```

## Event Models

### Core Event Models

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

@dataclass
class RawEvent:
    """Raw input event from platform layer"""
    type: str                    # Event type
    timestamp: float            # High-resolution timestamp
    platform_data: Dict[str, Any]  # Platform-specific data
    
@dataclass
class ProcessedEvent:
    """Processed event ready for storage/transmission"""
    type: str
    timestamp: float
    sequence_id: int           # Sequential event ID
    metadata: Dict[str, Any]   # Additional metadata
    
# Mouse Events
@dataclass
class MouseMoveEvent(ProcessedEvent):
    x: int                     # Screen X coordinate
    y: int                     # Screen Y coordinate
    dx: int                    # Delta X movement
    dy: int                    # Delta Y movement
    speed: float              # Movement speed (pixels/second)
    type: str = 'mouse_move'

@dataclass  
class MouseClickEvent(ProcessedEvent):
    x: int                     # Click X coordinate
    y: int                     # Click Y coordinate
    button: str               # 'left', 'right', 'middle', 'x1', 'x2'
    pressed: bool             # True for press, False for release
    click_count: int          # Number of clicks (1=single, 2=double, etc.)
    type: str = 'mouse_click'

@dataclass
class MouseScrollEvent(ProcessedEvent):
    x: int                     # Scroll X coordinate
    y: int                     # Scroll Y coordinate
    delta_x: int              # Horizontal scroll delta
    delta_y: int              # Vertical scroll delta
    type: str = 'mouse_scroll'

# Keyboard Events
@dataclass
class KeyboardEvent(ProcessedEvent):
    key: str                   # Key identifier
    key_code: int             # Platform key code
    modifiers: List[str]      # Active modifiers ['ctrl', 'alt', 'shift', 'cmd']
    pressed: bool             # True for press, False for release
    is_repeat: bool           # True if auto-repeat event
    
@dataclass
class KeyPressEvent(KeyboardEvent):
    type: str = 'key_press'
    pressed: bool = True
    
@dataclass
class KeyReleaseEvent(KeyboardEvent):
    type: str = 'key_release'
    pressed: bool = False

@dataclass
class TypeTextEvent(ProcessedEvent):
    text: str                 # Text that was typed
    type: str = 'type_text'

# Display Events
@dataclass
class WindowEvent(ProcessedEvent):
    window_id: str            # Window identifier
    window_title: str         # Window title
    application: str          # Application name
    event_type: str          # 'focus', 'minimize', 'maximize', 'close'
    
@dataclass
class ScreenEvent(ProcessedEvent):
    resolution: Tuple[int, int]  # Screen resolution (width, height)
    monitor_id: str           # Monitor identifier
    event_type: str          # 'resolution_change', 'monitor_connect', 'monitor_disconnect'
```

### Event Statistics

```python
@dataclass
class RecordingStats:
    """Recording session statistics"""
    duration: float                    # Total recording duration (seconds)
    events_captured: int              # Total events captured
    events_processed: int             # Total events processed
    events_filtered: int              # Events filtered out
    
    # Event type breakdown
    mouse_events: int
    keyboard_events: int
    display_events: int
    
    # Performance metrics
    average_events_per_second: float
    peak_events_per_second: float
    processing_latency_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    
    # Quality metrics
    smoothness_score: float           # Overall movement smoothness
    duplicate_events_filtered: int    # Duplicate events removed
    optimization_ratio: float        # Size reduction from optimization

@dataclass
class CaptureStats:
    """Input capture statistics"""
    events_captured: int
    capture_rate_hz: float
    missed_events: int
    buffer_overruns: int
    platform_errors: int

@dataclass
class ProcessingStats:
    """Event processing statistics"""
    events_processed: int
    processing_time_ms: float
    pipeline_stages_completed: int
    pipeline_stage_times: Dict[str, float]
    filtering_effectiveness: float
```

## Configuration

### Recording Engine Configuration

```python
# Complete recording engine configuration
recording_engine_config = {
    'engine': {
        'max_recording_duration': 3600,    # Max recording time (seconds)
        'auto_save_interval': 300,         # Auto-save interval (seconds)
        'event_buffer_size': 10000,        # Event buffer size
        'processing_threads': 4,           # Processing thread count
        'enable_real_time_processing': True,
        'enable_background_optimization': True
    },
    
    'input_capture': {
        'mouse': {
            'enabled': True,
            'sample_rate': 60,               # Hz
            'high_precision_mode': True,
            'capture_pressure': False,       # Capture pressure-sensitive input
            'capture_tilt': False           # Capture stylus tilt
        },
        'keyboard': {
            'enabled': True,
            'capture_timing': True,         # Capture key press/release timing
            'capture_dead_keys': True,      # Capture dead key combinations
            'international_support': True   # Support international keyboards
        },
        'display': {
            'enabled': True,
            'capture_screenshots': False,   # Capture screenshots at intervals
            'screenshot_quality': 0.8,      # JPEG quality for screenshots
            'capture_window_geometry': True # Capture window size/position changes
        }
    },
    
    'processing': {
        'filters': {
            'enable_smart_filtering': True,
            'minimum_movement_threshold': 2,
            'duplicate_time_window_ms': 10,
            'application_whitelist': [],
            'application_blacklist': ['keepass', 'lastpass'],
            'region_filters': []            # List of regions to include/exclude
        },
        'optimization': {
            'enable_path_optimization': True,
            'optimization_aggressiveness': 'medium',  # 'low', 'medium', 'high'
            'preserve_timing_accuracy': True,
            'enable_compression': True
        },
        'motion_analysis': {
            'enabled': True,
            'gesture_detection': True,
            'smoothness_analysis': True,
            'pattern_recognition': True
        }
    },
    
    'output': {
        'format_version': '1.0',
        'compression_algorithm': 'lzma',    # 'none', 'gzip', 'lzma'
        'encryption_enabled': True,
        'metadata_level': 'full',          # 'minimal', 'standard', 'full'
        'coordinate_precision': 'pixel',    # 'pixel', 'subpixel'
        'timing_precision': 'millisecond'   # 'centisecond', 'millisecond', 'microsecond'
    }
}
```

## Usage Examples

### Basic Recording Setup

```python
from mkd.recording import RecordingEngine

# Initialize recording engine
engine = RecordingEngine()

# Event handler
events_captured = []

def handle_event(event):
    events_captured.append(event)
    print(f"Captured {event.type} at {event.timestamp:.3f}")

# Start recording
engine.start(
    output_handler=handle_event,
    filters=['mouse', 'keyboard'],
    options={
        'sample_rate': 60,
        'enable_motion_analysis': True
    }
)

# ... perform actions ...

# Stop and get stats
stats = engine.stop()
print(f"Recorded {stats.events_captured} events in {stats.duration:.2f}s")
```

### Advanced Filtering

```python
from mkd.recording import RecordingEngine
from mkd.recording.filters import MinimumMovementFilter, ApplicationFilter

# Create recording engine
engine = RecordingEngine()

# Add custom filters
movement_filter = MinimumMovementFilter(threshold_pixels=5)
app_filter = ApplicationFilter(exclude_apps=['secure_app'])

engine.add_filter(movement_filter.should_capture)
engine.add_filter(app_filter.should_capture)

# Custom filter function
def custom_filter(event):
    """Only capture events during business hours"""
    from datetime import datetime
    now = datetime.now()
    return 9 <= now.hour <= 17  # 9 AM to 5 PM

filter_id = engine.add_filter(custom_filter)

# Start recording with filters applied
engine.start(handle_event)
```

### Motion Analysis

```python
from mkd.recording import MotionAnalyzer

# Initialize motion analyzer
analyzer = MotionAnalyzer({
    'gesture_detection': True,
    'optimization_level': 'high'
})

# Analyze captured mouse movements
mouse_events = [e for e in events_captured if e.type == 'mouse_move']

# Get motion analysis
analysis = analyzer.analyze_movement(mouse_events)
print(f"Movement smoothness: {analysis.smoothness_score:.2f}")
print(f"Total distance: {analysis.total_distance:.1f} pixels")
print(f"Average speed: {analysis.average_speed:.1f} px/s")

# Detect gestures
gestures = analyzer.detect_gestures(mouse_events)
for gesture in gestures:
    print(f"Detected {gesture.type} with {gesture.confidence:.2f} confidence")

# Optimize movement path
optimized_events = analyzer.optimize_path(mouse_events, 'high')
print(f"Optimized from {len(mouse_events)} to {len(optimized_events)} events")
```

### Custom Event Processing

```python
from mkd.recording import EventProcessor

# Create custom event processor
class TimestampNormalizer:
    def __init__(self):
        self.start_time = None
        
    def __call__(self, event):
        if self.start_time is None:
            self.start_time = event.timestamp
        
        # Normalize timestamp to start from 0
        event.timestamp -= self.start_time
        return event

# Initialize event processor
processor = EventProcessor({})

# Add custom processor
normalizer = TimestampNormalizer()
processor.add_processor(normalizer, priority=100)

# Process events
processed_events = []
for raw_event in captured_events:
    processed = processor.process_event(raw_event)
    if processed:
        processed_events.append(processed)
```

### Real-time Event Monitoring

```python
from mkd.recording import RecordingEngine
import threading
import time

class RealTimeMonitor:
    def __init__(self):
        self.event_count = 0
        self.start_time = time.time()
        
    def handle_event(self, event):
        self.event_count += 1
        
        # Print stats every 100 events
        if self.event_count % 100 == 0:
            elapsed = time.time() - self.start_time
            rate = self.event_count / elapsed
            print(f"Events: {self.event_count}, Rate: {rate:.1f} events/sec")
            
    def get_stats(self):
        elapsed = time.time() - self.start_time
        return {
            'events': self.event_count,
            'duration': elapsed,
            'rate': self.event_count / elapsed if elapsed > 0 else 0
        }

# Setup monitoring
monitor = RealTimeMonitor()
engine = RecordingEngine()

# Start recording with real-time monitoring
engine.start(
    output_handler=monitor.handle_event,
    options={'sample_rate': 120}  # High sample rate for monitoring
)

# Monitor in background
def print_stats():
    while engine.get_status().is_active:
        stats = monitor.get_stats()
        print(f"Real-time stats: {stats}")
        time.sleep(5)

stats_thread = threading.Thread(target=print_stats)
stats_thread.daemon = True
stats_thread.start()
```

### Platform-Specific Features

```python
from mkd.recording import RecordingEngine
from mkd.platform import get_platform_info

# Get platform-specific information
platform_info = get_platform_info()
print(f"Platform: {platform_info.name}")
print(f"Capabilities: {platform_info.capabilities}")

# Configure recording based on platform
config = {
    'sample_rate': 120 if platform_info.supports_high_precision else 60,
    'enable_pressure_sensitivity': platform_info.supports_pressure,
    'coordinate_mode': 'absolute' if platform_info.stable_coordinates else 'relative'
}

engine = RecordingEngine()
engine.start(
    output_handler=handle_event,
    options=config
)
```

This Recording Engine API provides comprehensive control over the input capture and recording process, enabling developers to create sophisticated automation recording systems tailored to their specific needs.