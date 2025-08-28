# MKD Automation Platform v2.0 - Getting Started Guide

This guide will help you get started with the MKD Automation Platform v2.0, from basic setup to creating your first automation scripts.

## Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/your-org/mkd_automation.git
cd mkd_automation
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Verify installation**:
```bash
python -c "from mkd_v2.integration import SystemController; print('✅ MKD v2.0 installed successfully')"
```

### Your First Automation

Here's a simple example that records and plays back user actions:

```python
import asyncio
from mkd_v2.integration import SystemController

async def basic_automation():
    # Initialize the system
    controller = SystemController()
    await controller.initialize()
    
    print("Starting recording in 3 seconds...")
    await asyncio.sleep(3)
    
    # Start recording user actions
    await controller.start_recording()
    print("Recording started! Perform some actions, then wait 10 seconds...")
    
    # Record for 10 seconds
    await asyncio.sleep(10)
    
    # Stop recording and get actions
    actions = await controller.stop_recording()
    print(f"Recorded {len(actions)} actions")
    
    # Wait a moment, then play back
    print("Playing back in 3 seconds...")
    await asyncio.sleep(3)
    
    # Execute the recorded actions
    result = await controller.execute_actions(actions)
    print(f"Playback completed: {result.success}")
    
    # Clean shutdown
    await controller.shutdown()

# Run the automation
if __name__ == "__main__":
    asyncio.run(basic_automation())
```

## Core Concepts

### Platform Detection

MKD v2.0 automatically detects your operating system and adapts accordingly:

```python
from mkd_v2.platform import PlatformDetector

detector = PlatformDetector()
platform = detector.detect_platform()

print(f"Running on: {platform.name}")
print(f"Capabilities: {detector.get_capabilities()}")
```

### Component System

The platform uses a component-based architecture where each major function is a separate component:

```python
from mkd_v2.integration import ComponentRegistry

registry = ComponentRegistry()

# Components are automatically registered
recorder = registry.get_component("input_recorder")
executor = registry.get_component("action_executor")
```

### Event System

Components communicate through an async event bus:

```python
from mkd_v2.integration import EventBus, EventType

async def setup_event_handling():
    bus = EventBus()
    await bus.start()
    
    # Subscribe to recording events
    async def on_action_recorded(event_data):
        print(f"Action recorded: {event_data['action_type']}")
    
    bus.subscribe(EventType.ACTION_RECORDED, on_action_recorded)
    
    # Events are automatically published by components
```

## Recording Actions

### Basic Recording

```python
from mkd_v2.input import InputRecorder

async def record_actions():
    recorder = InputRecorder()
    
    # Start recording
    await recorder.start_recording()
    
    # Recording happens automatically as user interacts
    # ...
    
    # Stop and get actions
    actions = await recorder.stop_recording()
    return actions
```

### Advanced Recording Options

```python
from mkd_v2.input import InputRecorder, RecordingConfig

config = RecordingConfig(
    record_mouse=True,
    record_keyboard=True,
    record_timing=True,
    ignore_modifiers=["ctrl", "alt"],  # Don't record these modifiers
    min_action_interval=0.1,  # Minimum time between actions
    max_recording_duration=300,  # 5 minutes max
)

recorder = InputRecorder(config=config)
```

### Filtering Actions

```python
def filter_actions(actions):
    """Filter out unwanted actions"""
    filtered = []
    for action in actions:
        # Skip very short waits
        if action.action_type == ActionType.WAIT and action.duration < 0.1:
            continue
        
        # Skip modifier-only key presses
        if action.action_type == ActionType.KEY_PRESS and action.key in ["ctrl", "alt", "shift"]:
            continue
            
        filtered.append(action)
    
    return filtered
```

## Executing Actions

### Basic Execution

```python
from mkd_v2.playback import ActionExecutor

async def execute_actions(actions):
    executor = ActionExecutor()
    
    # Execute all actions
    result = await executor.execute_actions(actions)
    
    if result.success:
        print(f"Successfully executed {len(actions)} actions")
    else:
        print(f"Execution failed: {result.error}")
    
    return result
```

### Execution Options

```python
from mkd_v2.playback import ActionExecutor, ExecutionConfig

config = ExecutionConfig(
    speed_multiplier=2.0,  # 2x speed
    fail_on_error=False,   # Continue on failures
    screenshot_on_error=True,  # Take screenshots on errors
    max_retry_attempts=3,  # Retry failed actions
)

executor = ActionExecutor(config=config)
```

### Conditional Execution

```python
async def conditional_execution(actions):
    executor = ActionExecutor()
    
    for action in actions:
        # Add custom logic before each action
        if action.action_type == ActionType.CLICK:
            # Verify element exists before clicking
            screenshot = await executor.take_screenshot()
            if not verify_element_exists(screenshot, action.coordinates):
                print("Element not found, skipping click")
                continue
        
        # Execute the action
        success = await executor.execute_single_action(action)
        if not success:
            print(f"Failed to execute: {action}")
            break
```

## Performance Optimization

### Profiling Your Automation

```python
from mkd_v2.performance import get_profiler, ProfileType

profiler = get_profiler()

# Profile a function
@profiler.profile("automation_script", ProfileType.CPU_TIME)
async def my_automation():
    # Your automation code
    pass

# Profile code blocks
async def detailed_automation():
    with profiler.profile_context("initialization"):
        await controller.initialize()
    
    with profiler.profile_context("recording"):
        actions = await record_user_actions()
    
    with profiler.profile_context("execution"):
        await execute_actions(actions)
    
    # Get performance analysis
    analysis = profiler.analyze_performance(time_window=300)
    print(f"Average duration: {analysis.summary['average_duration']:.3f}s")
    
    # Show recommendations
    for rec in analysis.recommendations:
        print(f"💡 {rec}")
```

### Using the Cache System

```python
from mkd_v2.performance import get_cache

cache = get_cache()

# Cache expensive operations
async def get_screen_analysis(screenshot_path):
    return cache.get_or_compute(
        f"analysis:{screenshot_path}",
        lambda: expensive_image_analysis(screenshot_path),
        ttl=3600  # Cache for 1 hour
    )

# Cache decorator
from mkd_v2.performance.cache_manager import memoize

@memoize(ttl=1800)  # 30 minutes
def process_template(template_data):
    # Expensive template processing
    return processed_template
```

### Resource Monitoring

```python
from mkd_v2.performance import ResourceMonitor, ResourceType, AlertLevel

async def setup_monitoring():
    monitor = ResourceMonitor()
    
    # Set up alerts
    monitor.set_threshold(ResourceType.MEMORY_USAGE, AlertLevel.WARNING, 80.0)
    monitor.set_threshold(ResourceType.CPU_USAGE, AlertLevel.CRITICAL, 90.0)
    
    def alert_handler(alert):
        print(f"🚨 Resource Alert: {alert.resource_type} at {alert.value:.1f}%")
        # Could send email, log to file, etc.
    
    monitor.add_alert_callback(alert_handler)
    
    # Start monitoring
    await monitor.start_monitoring(interval=5.0)  # Check every 5 seconds
```

## Error Handling

### Comprehensive Error Handling

```python
from mkd_v2.integration import SystemController
from mkd_v2.exceptions import RecordingError, PlaybackError, ComponentNotFoundError

async def robust_automation():
    controller = None
    try:
        # Initialize with error handling
        controller = SystemController()
        await controller.initialize()
        
        # Recording with timeout
        try:
            await controller.start_recording()
            await asyncio.wait_for(
                user_input_simulation(), 
                timeout=30.0  # 30 second timeout
            )
            actions = await controller.stop_recording()
            
        except asyncio.TimeoutError:
            print("Recording timed out")
            return
        except RecordingError as e:
            print(f"Recording failed: {e}")
            return
        
        # Execution with retry logic
        for attempt in range(3):
            try:
                result = await controller.execute_actions(actions)
                if result.success:
                    print("Automation completed successfully")
                    break
                else:
                    print(f"Attempt {attempt + 1} failed: {result.error}")
                    if attempt < 2:  # Don't wait after last attempt
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        
            except PlaybackError as e:
                print(f"Playback error on attempt {attempt + 1}: {e}")
                if attempt == 2:  # Last attempt
                    raise
                    
    except ComponentNotFoundError as e:
        print(f"System initialization failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Log full traceback in production
        import traceback
        traceback.print_exc()
    finally:
        # Always clean up
        if controller:
            await controller.shutdown()
```

### Custom Error Handling

```python
class AutomationError(Exception):
    """Custom exception for automation failures"""
    pass

async def safe_action_execution(actions):
    """Execute actions with comprehensive error handling"""
    successful_actions = []
    failed_actions = []
    
    executor = ActionExecutor()
    
    for i, action in enumerate(actions):
        try:
            success = await executor.execute_single_action(action)
            if success:
                successful_actions.append(action)
            else:
                failed_actions.append((i, action, "Execution returned False"))
                
        except Exception as e:
            failed_actions.append((i, action, str(e)))
            
            # Take screenshot on failure for debugging
            try:
                screenshot = await executor.take_screenshot()
                screenshot_path = f"error_screenshot_{i}.png"
                with open(screenshot_path, 'wb') as f:
                    f.write(screenshot)
                print(f"Error screenshot saved: {screenshot_path}")
            except:
                pass  # Don't fail because screenshot failed
    
    # Report results
    print(f"✅ Successful actions: {len(successful_actions)}")
    print(f"❌ Failed actions: {len(failed_actions)}")
    
    if failed_actions:
        print("Failed actions:")
        for i, action, error in failed_actions:
            print(f"  {i}: {action.action_type} - {error}")
    
    return len(failed_actions) == 0
```

## Advanced Features

### Custom Actions

```python
from mkd_v2.playback import InputAction, ActionType
import time

def create_custom_wait(seconds):
    """Create a custom wait action"""
    return InputAction(
        action_type=ActionType.WAIT,
        timestamp=time.time(),
        duration=seconds,
        metadata={"custom": True, "reason": "User-defined delay"}
    )

def create_custom_click(x, y, button="left", double=False):
    """Create a custom click action"""
    action_type = ActionType.DOUBLE_CLICK if double else ActionType.CLICK
    if button == "right":
        action_type = ActionType.RIGHT_CLICK
    
    return InputAction(
        action_type=action_type,
        timestamp=time.time(),
        coordinates=(x, y),
        button=button,
        metadata={"custom": True}
    )

# Build custom action sequence
actions = [
    create_custom_click(100, 200),
    create_custom_wait(1.0),
    create_custom_click(300, 400, button="right"),
    create_custom_wait(0.5),
    create_custom_click(200, 300, double=True),
]
```

### Automation Templates

```python
class AutomationTemplate:
    """Template for common automation patterns"""
    
    def __init__(self, name):
        self.name = name
        self.actions = []
        self.variables = {}
    
    def add_click(self, x, y, button="left"):
        self.actions.append(create_custom_click(x, y, button))
        return self
    
    def add_wait(self, seconds):
        self.actions.append(create_custom_wait(seconds))
        return self
    
    def add_type_text(self, text):
        action = InputAction(
            action_type=ActionType.TYPE_TEXT,
            timestamp=time.time(),
            text=text
        )
        self.actions.append(action)
        return self
    
    def set_variable(self, name, value):
        self.variables[name] = value
        return self
    
    def get_actions(self):
        # Process variables in actions
        processed_actions = []
        for action in self.actions:
            if action.text:
                # Replace variables in text
                text = action.text
                for var, value in self.variables.items():
                    text = text.replace(f"{{{var}}}", str(value))
                action.text = text
            processed_actions.append(action)
        return processed_actions

# Usage
template = (AutomationTemplate("login_form")
    .add_click(100, 200)  # Click username field
    .add_type_text("{username}")
    .add_click(100, 250)  # Click password field  
    .add_type_text("{password}")
    .add_click(200, 300)  # Click login button
    .add_wait(2.0)
    .set_variable("username", "user@example.com")
    .set_variable("password", "secret123")
)

actions = template.get_actions()
```

## Debugging and Troubleshooting

### Debug Mode

```python
import logging
from mkd_v2.integration import SystemController

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def debug_automation():
    controller = SystemController()
    
    # Enable debug features
    controller.config.debug_mode = True
    controller.config.save_debug_screenshots = True
    controller.config.debug_output_dir = "debug_output"
    
    await controller.initialize()
    
    # Debug information will be automatically logged
```

### Performance Analysis

```python
async def analyze_automation_performance():
    profiler = get_profiler()
    
    # Run automation with profiling
    profile_id = profiler.start_profiling("full_automation")
    
    try:
        await run_automation()
    finally:
        metrics = profiler.stop_profiling(profile_id)
    
    # Detailed analysis
    analysis = profiler.analyze_performance(time_window=600)
    
    print("🔍 Performance Analysis:")
    print(f"Total Duration: {analysis.total_duration:.3f}s")
    print(f"Average Operation Time: {analysis.summary['average_duration']:.3f}s")
    print(f"Memory Usage: {analysis.summary['max_memory_usage']:.1f}MB")
    
    print("\n📊 Top Operations by Time:")
    for op, time_spent in analysis.summary['operations_by_duration'][:5]:
        print(f"  {op}: {time_spent:.3f}s")
    
    print("\n💡 Recommendations:")
    for rec in analysis.recommendations:
        print(f"  • {rec}")
```

## Next Steps

Now that you understand the basics:

1. **Explore the [API Reference](../api/mkd_v2_api.md)** for detailed method documentation
2. **Check out [Examples](../examples/)** for real-world automation scenarios
3. **Read the [Advanced Features Guide](advanced_features.md)** for complex use cases
4. **Review [Troubleshooting](troubleshooting.md)** for common issues and solutions

## Getting Help

- **Documentation**: Check the `/docs` directory for comprehensive guides
- **Examples**: Look at `/examples` for working code samples
- **Issues**: Report bugs and request features through the project's issue tracker
- **Community**: Join discussions in the project's community channels

Happy automating! 🚀