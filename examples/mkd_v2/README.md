# MKD Automation Platform v2.0 - Examples

This directory contains comprehensive examples demonstrating the capabilities of the MKD Automation Platform v2.0.

## Examples Overview

### 1. Basic Recording & Playback (`basic_recording_playback.py`)

The fundamental MKD v2.0 workflow demonstrating:
- System initialization and configuration
- Recording user actions (mouse clicks, keyboard input)
- Playing back recorded actions
- Error handling and troubleshooting
- Saving/loading action sequences

**Key Features:**
- Interactive recording session with user guidance
- Comprehensive error handling with helpful messages
- Action sequence analysis and display
- File-based action persistence

**Usage:**
```bash
python basic_recording_playback.py
```

### 2. Performance Optimization Demo (`performance_optimization_demo.py`)

Advanced performance optimization features including:
- Performance profiling with CPU, memory, and I/O tracking
- Intelligent caching with multiple eviction strategies
- Real-time resource monitoring with alerts
- Runtime optimization with automatic improvements

**Key Features:**
- Decorator-based and context manager profiling
- Cache hit/miss analysis with performance metrics
- Resource threshold monitoring with callbacks
- Automatic optimization rule application

**Usage:**
```bash
python performance_optimization_demo.py
```

### 3. Advanced Automation Example (`advanced_automation_example.py`)

Sophisticated automation patterns showcasing:
- Template-based workflow creation
- Multi-step workflows with conditional logic
- Variable substitution and parameterization
- Error recovery and retry mechanisms
- Workflow serialization and persistence

**Key Features:**
- Reusable workflow templates
- Dynamic variable processing
- Conditional step execution
- Comprehensive retry logic with exponential backoff
- Statistics tracking and reporting

**Usage:**
```bash
python advanced_automation_example.py
```

## Quick Start Guide

### Prerequisites

1. **Install MKD v2.0**:
```bash
# From the project root
pip install -r requirements.txt
```

2. **Set Python Path**:
```bash
export PYTHONPATH=/path/to/mkd_automation/src:$PYTHONPATH
```

### Running Examples

#### Basic Example
Start with the basic recording and playback example:
```bash
cd examples/mkd_v2
python basic_recording_playback.py
```

This will guide you through:
1. Recording your mouse and keyboard actions
2. Displaying the recorded action sequence
3. Playing back the actions automatically
4. Saving actions for future use

#### Performance Demo
Explore performance optimization features:
```bash
python performance_optimization_demo.py
```

This demonstrates:
- Caching performance improvements
- Resource usage monitoring
- Performance profiling analysis
- Optimization recommendations

#### Advanced Workflows
See sophisticated automation patterns:
```bash
python advanced_automation_example.py
```

This showcases:
- Template-based automation creation
- Multi-step workflow execution
- Error handling and recovery
- Workflow persistence

## Example Structure

Each example follows a consistent structure:

```python
#!/usr/bin/env python3
"""
Example Description

Key features and capabilities demonstrated.
"""

import asyncio
import logging
from mkd_v2.integration import SystemController

async def main():
    """Main demonstration function"""
    controller = SystemController()
    
    try:
        await controller.initialize()
        # Example logic here
    except Exception as e:
        logger.error(f"Example failed: {e}")
    finally:
        await controller.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

### Environment Variables

Configure examples using environment variables:

```bash
# Logging level
export MKD_LOG_LEVEL=DEBUG

# Performance settings
export MKD_CACHE_SIZE=2000
export MKD_PROFILING_ENABLED=true

# Resource monitoring
export MKD_MONITOR_INTERVAL=2.0
export MKD_CPU_THRESHOLD=80.0
export MKD_MEMORY_THRESHOLD=85.0
```

### Configuration Files

Create `config.json` for persistent settings:

```json
{
  "system": {
    "debug_mode": true,
    "save_screenshots": true,
    "screenshot_dir": "debug_screenshots"
  },
  "recording": {
    "record_mouse": true,
    "record_keyboard": true,
    "min_action_interval": 0.1
  },
  "playback": {
    "default_speed": 1.0,
    "retry_attempts": 3,
    "screenshot_on_error": true
  },
  "performance": {
    "profiling_enabled": true,
    "cache_strategy": "adaptive",
    "resource_monitoring": true
  }
}
```

## Error Handling

All examples include comprehensive error handling:

### Common Issues

1. **Permission Errors**:
   - Run with appropriate privileges
   - Check system accessibility settings
   - Verify input device permissions

2. **Module Import Errors**:
   - Ensure PYTHONPATH is set correctly
   - Install all requirements: `pip install -r requirements.txt`
   - Verify MKD v2.0 installation

3. **Recording Issues**:
   - Check input device functionality
   - Verify accessibility permissions
   - Try different recording durations

4. **Playback Issues**:
   - Ensure consistent screen layout
   - Verify application state matches recording
   - Check for timing-related issues

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or via environment
export MKD_LOG_LEVEL=DEBUG
```

## Performance Tips

### Optimization Strategies

1. **Use Caching**: Cache expensive operations
2. **Profile Regularly**: Identify bottlenecks
3. **Monitor Resources**: Set appropriate thresholds
4. **Batch Operations**: Group related actions
5. **Async Patterns**: Use async/await properly

### Best Practices

1. **Error Handling**: Always use try/finally blocks
2. **Resource Cleanup**: Properly shutdown components
3. **Logging**: Use appropriate log levels
4. **Testing**: Test workflows thoroughly
5. **Documentation**: Document custom workflows

## Integration Examples

### Web Application Automation

```python
# Template for web form automation
web_form = (WorkflowTemplate("login_form")
    .add_click_step("username_field", 200, 150)
    .add_type_step("enter_username", "{username}")
    .add_click_step("password_field", 200, 200)
    .add_type_step("enter_password", "{password}")
    .add_click_step("login_button", 200, 250)
    .set_variable("username", "user@example.com")
    .set_variable("password", "secret123")
)
```

### Desktop Application Testing

```python
# Template for desktop app testing
desktop_test = (WorkflowTemplate("app_test")
    .add_click_step("menu_file", 50, 30)
    .add_click_step("menu_new", 70, 50)
    .add_wait_step("wait_for_dialog", 1.0)
    .add_type_step("enter_filename", "{filename}")
    .add_click_step("ok_button", 300, 200)
    .set_variable("filename", "test_document.txt")
)
```

### System Administration

```python
# Template for system tasks
system_admin = (WorkflowTemplate("backup_task")
    .add_click_step("open_terminal", 100, 100)
    .add_wait_step("wait_for_terminal", 2.0)
    .add_type_step("run_backup", "backup --source {source} --dest {dest}")
    .set_variable("source", "/home/user/documents")
    .set_variable("dest", "/backup/daily")
)
```

## Extending Examples

### Custom Actions

Add custom action types:

```python
class CustomAction(InputAction):
    def __init__(self, custom_type: str, **kwargs):
        super().__init__(ActionType.CUSTOM, **kwargs)
        self.custom_type = custom_type
```

### Custom Workflows

Create domain-specific workflow builders:

```python
class WebAutomationBuilder(WorkflowTemplate):
    def navigate_to(self, url: str):
        return self.add_type_step("navigate", f"ctrl+l{url}\\n")
    
    def fill_form_field(self, selector: str, value: str):
        # Custom logic for web form interaction
        pass
```

### Integration Hooks

Add external system integration:

```python
async def database_verification_hook(workflow_result):
    """Verify workflow results in database"""
    if workflow_result.success:
        # Check database state
        pass
```

## Contributing

When adding new examples:

1. Follow the established structure
2. Include comprehensive error handling
3. Add detailed documentation
4. Provide configuration options
5. Test thoroughly across platforms

## Support

For help with examples:

1. Check the [API Reference](../../docs/api/mkd_v2_api.md)
2. Review [User Guide](../../docs/user_guide/mkd_v2_getting_started.md)
3. Examine existing examples for patterns
4. Report issues through the project tracker

---

**Happy Automating!** 🚀