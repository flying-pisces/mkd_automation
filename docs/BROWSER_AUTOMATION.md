# Browser Automation Feature

## Overview

MKD Automation now includes powerful browser automation capabilities that enable automated interaction with web applications. This feature addresses scenarios where AI assistants cannot directly control browser interactions, providing a bridge between AI-guided assistance and actual web automation.

## Key Features

- **Browser Control**: Automate Chrome, Firefox, and Edge browsers
- **Action Recording**: Record user interactions in the browser for replay
- **Action Playback**: Replay recorded browser actions with timing control
- **Mixed Automation**: Combine browser and desktop automation in single workflows
- **Natural Language Processing**: Convert text prompts to browser actions
- **EmailJS Integration**: Specific automation for EmailJS template creation

## Installation

Install the browser automation dependencies:

```bash
pip install selenium webdriver-manager
```

The webdriver-manager package will automatically download and manage browser drivers.

## Usage

### Command Line Interface

#### Open and Record Browser Actions

```bash
# Open a URL and record actions
python -m mkd.cli.browser_cli browser open -u https://example.com --record -o recording.json

# Open in specific browser
python -m mkd.cli.browser_cli browser open -u https://example.com --browser firefox

# Run in headless mode
python -m mkd.cli.browser_cli browser open -u https://example.com --headless
```

#### Replay Recorded Actions

```bash
# Replay a recording
python -m mkd.cli.browser_cli browser replay recording.json

# Replay at different speed (2x faster)
python -m mkd.cli.browser_cli browser replay recording.json --speed 2.0
```

#### Automate from Natural Language

```bash
# Simple automation from text prompt
python -m mkd.cli.browser_cli browser auto -p "Go to google.com and search for Python tutorials"

# With starting URL
python -m mkd.cli.browser_cli browser auto -p "Click the login button and enter username" -u https://example.com
```

#### EmailJS Template Automation

```bash
# Create EmailJS template
python -m mkd.cli.browser_cli browser emailjs -t "user@example.com" -n "Contact Form"

# With custom content file
python -m mkd.cli.browser_cli browser emailjs -t "user@example.com" -c template.txt
```

### Python API

#### Basic Browser Control

```python
from mkd.browser.controller import BrowserController, BrowserConfig, BrowserType

# Configure browser
config = BrowserConfig(
    browser_type=BrowserType.CHROME,
    headless=False,
    window_size=(1920, 1080)
)

# Create and start controller
controller = BrowserController(config)
controller.start()

# Navigate and interact
controller.navigate("https://example.com")
controller.click("button#submit")
controller.type_text("input#email", "user@example.com")

# Take screenshot
controller.take_screenshot("page.png")

# Stop browser
controller.stop()
```

#### Recording Browser Actions

```python
from mkd.browser.recorder import BrowserRecorder

# Create recorder with controller
recorder = BrowserRecorder(controller)

# Start recording
recorder.start_recording()

# User performs actions in browser...

# Stop and save recording
actions = recorder.stop_recording()
recorder.save_recording("my_recording.json")
```

#### Executing Browser Actions

```python
from mkd.browser.actions import BrowserAction, BrowserActionType, BrowserActionExecutor

# Create executor
executor = BrowserActionExecutor(controller)

# Create and execute actions
action = BrowserAction(
    type=BrowserActionType.CLICK,
    target="button.submit",
    wait=True
)
executor.execute(action)

# Load and replay recording
actions = recorder.load_recording("my_recording.json")
for action in actions:
    executor.execute(action)
```

#### Mixed Browser + Desktop Automation

```python
from mkd.browser.integration import BrowserIntegration
from mkd.core.session import Session

# Create integration
session = Session()
integration = BrowserIntegration(session)

# Start browser session
browser_session = integration.start_browser_session()

# Record mixed actions
integration.start_browser_recording()
# ... perform browser actions ...
browser_actions = integration.stop_browser_recording()

# Create mixed script
script = integration.create_mixed_script("My Automation")

# Execute mixed script
integration.execute_mixed_script(script, speed=1.0)

# Clean up
integration.stop_browser_session()
```

## EmailJS Automation Example

The EmailJS automation demonstrates how MKD can handle complex web form interactions:

```python
from mkd.browser.emailjs_automation import EmailJSAutomation

# Create automation instance
automation = EmailJSAutomation()

# Start browser
automation.start()

# Configure template
template_config = {
    'template_name': 'Contact Form',
    'subject': 'New message from {{from_name}}',
    'content': 'Message from {{from_name}}: {{message}}',
    'to_email': 'admin@example.com',
    'reply_to': '{{from_email}}'
}

# Create template (handles login prompt)
template_id = automation.create_template(template_config)

if template_id:
    print(f"Template created with ID: {template_id}")

# Clean up
automation.stop()
```

## Architecture

### Components

1. **BrowserController**: Core browser control interface
   - Manages WebDriver lifecycle
   - Provides high-level interaction methods
   - Supports Chrome, Firefox, Edge

2. **BrowserRecorder**: Records user interactions
   - Captures clicks, typing, navigation
   - Generates reproducible action sequences
   - Saves/loads recordings as JSON

3. **BrowserActionExecutor**: Executes recorded actions
   - Replays action sequences
   - Handles timing and synchronization
   - Error recovery mechanisms

4. **BrowserIntegration**: Bridges with MKD core
   - Combines browser and desktop automation
   - Converts between action formats
   - Manages mixed scripts

### Action Types

- `NAVIGATE`: Navigate to URL
- `CLICK`: Click element
- `TYPE`: Type text into element
- `SELECT`: Select dropdown option
- `WAIT`: Wait for time or element
- `SCREENSHOT`: Capture screenshot
- `SCRIPT`: Execute JavaScript
- `SCROLL`: Scroll page or to element
- `HOVER`: Hover over element
- `DRAG_DROP`: Drag and drop elements
- `SWITCH_TAB`: Switch browser tabs
- `SWITCH_FRAME`: Switch to iframe
- `ALERT_HANDLE`: Handle JavaScript alerts
- `KEY_PRESS`: Send keyboard shortcuts
- `CLEAR`: Clear input field
- `SUBMIT`: Submit form

## Use Cases

### 1. AI Assistant Enhancement
When AI assistants cannot directly interact with web pages, MKD browser automation provides the missing capability:

```python
# AI provides instructions, MKD executes them
instructions = ai_assistant.parse_request("Create EmailJS template")
automation.execute_instructions(instructions)
```

### 2. Web Testing Automation
Create comprehensive web application tests:

```python
# Record test scenario
recorder.start_recording()
# Perform test steps manually
test_actions = recorder.stop_recording()

# Replay as automated test
for action in test_actions:
    executor.execute(action)
    # Add assertions here
```

### 3. Form Filling Automation
Automate repetitive form submissions:

```python
# Define form data
form_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'message': 'Test message'
}

# Fill and submit form
for field, value in form_data.items():
    controller.type_text(f"input[name='{field}']", value)
controller.click("button[type='submit']")
```

### 4. Web Scraping with Interaction
Extract data from dynamic websites:

```python
# Navigate to page
controller.navigate("https://example.com/data")

# Interact to load data
controller.click("button#load-more")
controller.wait_for_element(".data-loaded")

# Extract data
data = controller.execute_script("return document.querySelector('.data').innerText")
```

## Best Practices

1. **Use Explicit Waits**: Always wait for elements before interacting
2. **Handle Errors Gracefully**: Wrap automations in try-catch blocks
3. **Test Selectors**: Verify CSS selectors work across page states
4. **Record First**: Record manual interactions before scripting
5. **Add Delays**: Include realistic delays between actions
6. **Clean Up**: Always stop browser sessions properly

## Troubleshooting

### Browser Driver Issues
If you encounter driver issues, manually install drivers:
```bash
# Chrome
webdriver-manager chrome

# Firefox
webdriver-manager firefox

# Edge
webdriver-manager edge
```

### Headless Mode Issues
Some sites detect headless mode. Use these options:
```python
config = BrowserConfig(
    headless=False,  # Disable headless
    window_size=(1920, 1080)  # Set realistic size
)
```

### Element Not Found
Use more specific selectors or add waits:
```python
# Wait for element explicitly
controller.wait_for_element("#my-element", timeout=10)

# Use multiple selector strategies
selectors = ["#id", ".class", "[name='field']"]
for selector in selectors:
    try:
        controller.click(selector)
        break
    except:
        continue
```

## Security Considerations

1. **Credentials**: Never hardcode passwords in scripts
2. **Sensitive Data**: Use encryption for saved recordings with sensitive data
3. **User Consent**: Always get user permission before automating their browser
4. **Rate Limiting**: Respect website rate limits and terms of service
5. **Sandboxing**: Run automation in isolated environments when possible

## Future Enhancements

- [ ] Playwright backend support
- [ ] Cloud browser support (Browserless, etc.)
- [ ] Visual regression testing
- [ ] AI-powered element detection
- [ ] Parallel execution support
- [ ] Browser extension integration
- [ ] Mobile browser support
- [ ] Network request interception

## Contributing

To contribute to the browser automation feature:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.