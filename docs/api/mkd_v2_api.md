# MKD Automation Platform v2.0 - API Reference

This document provides comprehensive API documentation for the MKD Automation Platform v2.0.

## Core Components

### Platform Detection

#### `PlatformDetector`

Automatically detects the current operating system and provides platform-specific capabilities.

```python
from mkd_v2.platform import PlatformDetector

detector = PlatformDetector()
platform = detector.detect_platform()
print(f"Platform: {platform.name}")
print(f"Version: {platform.version}")
```

**Methods:**
- `detect_platform() -> PlatformInfo`: Detects current platform
- `get_capabilities() -> List[str]`: Returns supported capabilities
- `is_supported(capability: str) -> bool`: Checks capability support

#### `BasePlatform`

Base class for platform-specific implementations.

```python
from mkd_v2.platform.base import BasePlatform

class CustomPlatform(BasePlatform):
    def get_screen_size(self) -> Tuple[int, int]:
        # Implementation
        pass
```

**Abstract Methods:**
- `get_screen_size() -> Tuple[int, int]`: Get screen dimensions
- `get_mouse_position() -> Tuple[int, int]`: Get cursor position
- `take_screenshot() -> bytes`: Capture screen
- `click(x: int, y: int, button: str = "left") -> bool`: Click at position
- `type_text(text: str) -> bool`: Type text
- `press_key(key: str, modifiers: List[str] = None) -> bool`: Press key

### Input Capture

#### `InputRecorder`

Records user input actions (mouse clicks, keyboard events, etc.).

```python
from mkd_v2.input import InputRecorder

recorder = InputRecorder()
await recorder.start_recording()
# Perform actions...
actions = await recorder.stop_recording()
```

**Methods:**
- `start_recording() -> None`: Begin recording
- `stop_recording() -> List[InputAction]`: Stop and return actions
- `pause_recording() -> None`: Pause recording
- `resume_recording() -> None`: Resume recording
- `get_recorded_actions() -> List[InputAction]`: Get current actions

### Action Playback

#### `ActionExecutor`

Executes recorded or programmatically created actions.

```python
from mkd_v2.playback import ActionExecutor

executor = ActionExecutor()
await executor.execute_actions(actions)
```

**Methods:**
- `execute_actions(actions: List[InputAction]) -> ExecutionResult`: Execute action list
- `execute_single_action(action: InputAction) -> bool`: Execute one action
- `set_speed_multiplier(multiplier: float) -> None`: Adjust playback speed
- `pause_execution() -> None`: Pause playback
- `resume_execution() -> None`: Resume playback

### Integration System

#### `ComponentRegistry`

Central registry for managing system components and their dependencies.

```python
from mkd_v2.integration import ComponentRegistry

registry = ComponentRegistry()
registry.register_component("recorder", InputRecorder)
component = registry.get_component("recorder")
```

**Methods:**
- `register_component(name: str, component_class: type) -> None`: Register component
- `get_component(name: str) -> Any`: Get component instance
- `unregister_component(name: str) -> None`: Remove component
- `list_components() -> List[str]`: List registered components
- `get_dependencies(component_name: str) -> List[str]`: Get component dependencies

#### `EventBus`

Asynchronous event system for inter-component communication.

```python
from mkd_v2.integration import EventBus, EventType

bus = EventBus()
await bus.start()

# Subscribe to events
async def handle_action(event_data):
    print(f"Action completed: {event_data}")

bus.subscribe(EventType.ACTION_COMPLETED, handle_action)

# Publish events  
await bus.publish(EventType.ACTION_STARTED, {"action": "click"})
```

**Methods:**
- `start() -> None`: Start event bus
- `stop() -> None`: Stop event bus
- `subscribe(event_type: EventType, handler: Callable) -> str`: Subscribe to events
- `unsubscribe(subscription_id: str) -> None`: Unsubscribe from events
- `publish(event_type: EventType, data: Any = None) -> None`: Publish event

#### `SystemController`

High-level system controller that manages all components and their interactions.

```python
from mkd_v2.integration import SystemController

controller = SystemController()
await controller.initialize()

# Record actions
await controller.start_recording()
# ... user performs actions ...
actions = await controller.stop_recording()

# Play back actions
await controller.execute_actions(actions)
```

**Methods:**
- `initialize() -> None`: Initialize all components
- `start_recording() -> None`: Start input recording
- `stop_recording() -> List[InputAction]`: Stop recording and return actions
- `execute_actions(actions: List[InputAction]) -> ExecutionResult`: Execute actions
- `get_system_status() -> Dict[str, Any]`: Get system status
- `shutdown() -> None`: Shut down system

## Performance & Optimization

### Performance Profiler

#### `PerformanceProfiler`

Advanced profiling tools for performance analysis and optimization.

```python
from mkd_v2.performance import PerformanceProfiler, ProfileType

profiler = PerformanceProfiler()

# Decorator usage
@profiler.profile("my_function")
async def my_function():
    # Function code
    pass

# Context manager usage
with profiler.profile_context("operation", ProfileType.MEMORY_USAGE):
    # Code to profile
    pass

# Get analysis
analysis = profiler.analyze_performance(time_window=300.0)
```

**Methods:**
- `start_profiling(name: str, profile_type: ProfileType) -> str`: Start profiling
- `stop_profiling(profile_id: str) -> ProfileMetrics`: Stop profiling
- `profile(name: str, profile_type: ProfileType)`: Decorator for profiling
- `profile_context(name: str, profile_type: ProfileType)`: Context manager
- `analyze_performance(time_window: float) -> ProfileResult`: Analyze performance
- `get_system_metrics() -> Dict[str, Any]`: Get system metrics

### Cache Manager

#### `CacheManager`

Intelligent caching system with multiple eviction strategies.

```python
from mkd_v2.performance import CacheManager, CacheStrategy

cache = CacheManager(
    max_size=1000, 
    max_memory_mb=100, 
    strategy=CacheStrategy.LRU
)

# Basic caching
cache.put("key", "value", ttl=3600)
value = cache.get("key", default="not_found")

# Compute and cache
result = cache.get_or_compute("expensive_key", expensive_function)

# Async support
result = await cache.get_or_compute_async("async_key", async_function)
```

**Methods:**
- `get(key: str, default: Any = None) -> Any`: Get cached value
- `put(key: str, value: Any, ttl: float = None) -> bool`: Cache value
- `remove(key: str) -> bool`: Remove cached value
- `clear() -> None`: Clear all cache
- `get_or_compute(key: str, compute_func: Callable, ttl: float = None) -> Any`: Get or compute
- `get_cache_statistics() -> Dict[str, Any]`: Get cache statistics

### Resource Monitor

#### `ResourceMonitor`

Real-time system resource monitoring with alerting.

```python
from mkd_v2.performance import ResourceMonitor, ResourceType, AlertLevel

monitor = ResourceMonitor()

# Set thresholds
monitor.set_threshold(ResourceType.CPU_USAGE, AlertLevel.WARNING, 80.0)
monitor.set_threshold(ResourceType.MEMORY_USAGE, AlertLevel.CRITICAL, 90.0)

# Add alert callback
def alert_handler(alert):
    print(f"ALERT: {alert.resource_type} at {alert.value}%")

monitor.add_alert_callback(alert_handler)

# Start monitoring
await monitor.start_monitoring()

# Get current metrics
metrics = monitor.get_current_metrics()
```

**Methods:**
- `start_monitoring(interval: float = 1.0) -> None`: Start monitoring
- `stop_monitoring() -> None`: Stop monitoring
- `get_current_metrics() -> ResourceMetrics`: Get current resource usage
- `set_threshold(resource: ResourceType, level: AlertLevel, value: float) -> None`: Set alert threshold
- `add_alert_callback(callback: Callable) -> None`: Add alert handler
- `get_resource_history(resource: ResourceType, duration: float) -> List[float]`: Get history

### Runtime Optimizer

#### `RuntimeOptimizer`

Intelligent runtime optimization with rule-based improvements.

```python
from mkd_v2.performance import RuntimeOptimizer, OptimizationStrategy

optimizer = RuntimeOptimizer(strategy=OptimizationStrategy.BALANCED)
await optimizer.start()

# The optimizer runs automatically, or you can trigger manually
results = await optimizer._run_optimization_cycle()

# Get optimization report
report = optimizer.get_optimization_report()
print(f"Total optimizations: {report['statistics']['total_optimizations']}")
```

**Methods:**
- `start() -> None`: Start optimizer
- `stop() -> None`: Stop optimizer  
- `add_optimization_rule(rule: OptimizationRule) -> None`: Add optimization rule
- `set_strategy(strategy: OptimizationStrategy) -> None`: Change strategy
- `get_optimization_report() -> Dict[str, Any]`: Get comprehensive report

## Data Types

### InputAction

Represents a single user input action.

```python
@dataclass
class InputAction:
    action_type: ActionType
    timestamp: float
    coordinates: Optional[Tuple[int, int]] = None
    key: Optional[str] = None
    modifiers: List[str] = field(default_factory=list)
    text: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### ActionType

Enumeration of supported action types.

```python
class ActionType(Enum):
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release" 
    TYPE_TEXT = "type_text"
    SCROLL = "scroll"
    DRAG = "drag"
    WAIT = "wait"
```

### EventType

System event types for the event bus.

```python
class EventType(Enum):
    RECORDING_STARTED = "recording_started"
    RECORDING_STOPPED = "recording_stopped"
    ACTION_RECORDED = "action_recorded"
    PLAYBACK_STARTED = "playback_started"
    PLAYBACK_COMPLETED = "playback_completed"
    ACTION_EXECUTED = "action_executed"
    ERROR_OCCURRED = "error_occurred"
    SYSTEM_STARTED = "system_started"
    SYSTEM_STOPPED = "system_stopped"
```

### ProfileType

Performance profiling types.

```python
class ProfileType(Enum):
    CPU_TIME = "cpu_time"
    MEMORY_USAGE = "memory_usage" 
    IO_OPERATIONS = "io_operations"
    ASYNC_AWAIT = "async_await"
    FUNCTION_CALLS = "function_calls"
    SYSTEM_RESOURCES = "system_resources"
```

### CacheStrategy

Cache eviction strategies.

```python
class CacheStrategy(Enum):
    LRU = "lru"              # Least Recently Used
    LFU = "lfu"              # Least Frequently Used  
    TTL = "ttl"              # Time To Live
    FIFO = "fifo"            # First In First Out
    ADAPTIVE = "adaptive"     # Adaptive based on usage
```

## Error Handling

All API methods use standard Python exceptions with specific error types:

- `ComponentNotFoundError`: Component not registered
- `PlatformNotSupportedError`: Platform not supported
- `RecordingError`: Recording operation failed
- `PlaybackError`: Playback operation failed
- `DependencyError`: Dependency resolution failed

Example error handling:

```python
try:
    component = registry.get_component("nonexistent")
except ComponentNotFoundError as e:
    print(f"Component not found: {e}")
```

## Configuration

System configuration can be managed through environment variables or configuration files:

```python
# Environment variables
MKD_LOG_LEVEL=DEBUG
MKD_CACHE_SIZE=1000
MKD_OPTIMIZATION_STRATEGY=balanced

# Programmatic configuration
from mkd_v2.config import Config

config = Config()
config.set("profiler.enabled", True)
config.set("cache.max_size", 2000)
```

## Threading and Concurrency

The MKD v2.0 platform is designed with async/await patterns for optimal performance:

- All major operations are asynchronous
- Thread-safe components use proper locking
- Event bus provides async event handling
- Performance monitoring runs in background tasks

## Best Practices

1. **Always use async/await** for system operations
2. **Initialize components** through SystemController when possible
3. **Handle errors gracefully** with proper exception handling
4. **Monitor performance** using built-in profiling tools
5. **Configure alerts** for resource monitoring in production
6. **Use caching** for expensive operations
7. **Profile regularly** to identify optimization opportunities

For more detailed examples, see the [User Guide](../user_guide/) and [Examples](../examples/) directories.