"""
CLI commands for browser automation.
"""
import click
import logging
import json
from pathlib import Path
from typing import Optional

from ..browser.controller import BrowserController, BrowserConfig, BrowserType
from ..browser.recorder import BrowserRecorder
from ..browser.actions import BrowserActionExecutor
from ..browser.emailjs_automation import EmailJSAutomation
from ..browser.integration import BrowserIntegration

logger = logging.getLogger(__name__)


@click.group()
def browser():
    """Browser automation commands."""
    pass


@browser.command()
@click.option('--url', '-u', required=True, help='URL to navigate to')
@click.option('--browser', '-b', 
              type=click.Choice(['chrome', 'firefox', 'edge']),
              default='chrome',
              help='Browser to use')
@click.option('--headless', is_flag=True, help='Run in headless mode')
@click.option('--record', '-r', is_flag=True, help='Record browser actions')
@click.option('--output', '-o', help='Output file for recording (JSON)')
def open(url: str, browser: str, headless: bool, record: bool, output: Optional[str]):
    """Open a URL in browser and optionally record actions."""
    # Configure browser
    config = BrowserConfig(
        browser_type=BrowserType(browser),
        headless=headless
    )
    
    controller = BrowserController(config)
    recorder = None
    
    try:
        # Start browser
        controller.start()
        controller.navigate(url)
        
        if record:
            recorder = BrowserRecorder(controller)
            recorder.start_recording()
            click.echo(f"🔴 Recording browser actions... Press Ctrl+C to stop")
        
        # Keep browser open
        click.echo(f"✅ Browser opened to: {url}")
        click.echo("Press Ctrl+C to close...")
        
        # Wait for user interrupt
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            pass
            
    finally:
        # Stop recording if active
        if recorder and record:
            actions = recorder.stop_recording()
            click.echo(f"\n📝 Recorded {len(actions)} actions")
            
            # Save to file if specified
            if output:
                recorder.save_recording(output)
                click.echo(f"💾 Saved recording to: {output}")
            else:
                # Print actions to console
                for i, action in enumerate(actions):
                    click.echo(f"  {i+1}. {action.type.value}: {action.target or action.value or ''}")
                    
        # Stop browser
        controller.stop()
        click.echo("Browser closed")


@browser.command()
@click.argument('recording_file', type=click.Path(exists=True))
@click.option('--browser', '-b',
              type=click.Choice(['chrome', 'firefox', 'edge']),
              default='chrome',
              help='Browser to use')
@click.option('--speed', '-s', default=1.0, help='Playback speed (1.0 = normal)')
@click.option('--headless', is_flag=True, help='Run in headless mode')
def replay(recording_file: str, browser: str, speed: float, headless: bool):
    """Replay a recorded browser automation script."""
    # Load recording
    recorder = BrowserRecorder()
    actions = recorder.load_recording(recording_file)
    
    click.echo(f"📂 Loaded {len(actions)} actions from: {recording_file}")
    
    # Configure browser
    config = BrowserConfig(
        browser_type=BrowserType(browser),
        headless=headless
    )
    
    controller = BrowserController(config)
    executor = BrowserActionExecutor(controller)
    
    try:
        # Start browser
        controller.start()
        
        # Execute actions
        click.echo(f"▶️  Replaying actions at {speed}x speed...")
        
        for i, action in enumerate(actions):
            click.echo(f"  [{i+1}/{len(actions)}] {action.type.value}: {action.target or ''}")
            executor.execute(action)
            
            # Add delay between actions
            if i < len(actions) - 1 and speed > 0:
                import time
                time.sleep(0.5 / speed)
                
        click.echo("✅ Replay completed successfully!")
        
        # Keep browser open for verification
        click.echo("Press Enter to close browser...")
        input()
        
    except Exception as e:
        click.echo(f"❌ Error during replay: {e}", err=True)
        
    finally:
        controller.stop()


@browser.command()
@click.option('--template-name', '-n', default='Contact Form', help='Template name')
@click.option('--subject', '-s', help='Email subject with variables')
@click.option('--to-email', '-t', required=True, help='Recipient email')
@click.option('--content-file', '-c', type=click.Path(exists=True), 
              help='File containing email content')
def emailjs(template_name: str, subject: str, to_email: str, content_file: Optional[str]):
    """Automate EmailJS template creation."""
    click.echo("🚀 Starting EmailJS automation...")
    
    # Read content from file if provided
    content = None
    if content_file:
        with open(content_file, 'r') as f:
            content = f.read()
    else:
        content = '''Hello,

You have received a new message from your website:

From: {{from_name}}
Email: {{from_email}}
Message:
{{message}}

Best regards,
Your Website Team'''
    
    # Set default subject if not provided
    if not subject:
        subject = 'New message from {{from_name}}'
    
    # Configure template
    template_config = {
        'template_name': template_name,
        'subject': subject,
        'content': content,
        'to_email': to_email,
        'reply_to': '{{from_email}}'
    }
    
    automation = EmailJSAutomation()
    
    try:
        # Start automation
        automation.start()
        
        click.echo("📝 Creating EmailJS template with:")
        click.echo(f"  • Name: {template_name}")
        click.echo(f"  • Subject: {subject}")
        click.echo(f"  • To: {to_email}")
        click.echo(f"  • Reply-To: {{{{from_email}}}}")
        click.echo("")
        
        # Check if user wants to see the dashboard URL
        click.echo("🌐 Opening EmailJS dashboard...")
        click.echo("⚠️  Please log in if required and press Enter to continue...")
        
        # Create template
        template_id = automation.create_template(template_config)
        
        if template_id:
            click.echo(f"✅ Template created successfully!")
            click.echo(f"📋 Template ID: {template_id}")
            click.echo(f"")
            click.echo("You can now use this template in your EmailJS integration.")
        else:
            click.echo("⚠️  Template creation may have failed.")
            click.echo("Please check the browser and complete any remaining steps.")
            
        # Keep browser open for verification
        click.echo("\nPress Enter to close the browser...")
        input()
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        
    finally:
        automation.stop()


@browser.command()
@click.option('--prompt', '-p', required=True, help='Natural language task description')
@click.option('--url', '-u', help='Starting URL')
@click.option('--browser', '-b',
              type=click.Choice(['chrome', 'firefox', 'edge']),
              default='chrome',
              help='Browser to use')
@click.option('--save', '-s', help='Save actions to file')
def auto(prompt: str, url: Optional[str], browser: str, save: Optional[str]):
    """
    Automate browser tasks from natural language prompts.
    
    Example:
        mkd browser auto -p "Go to google.com and search for Python tutorials"
        mkd browser auto -p "Fill out the contact form with test data" -u https://example.com/contact
    """
    click.echo(f"🤖 Browser Task Automation")
    click.echo(f"📝 Task: {prompt}")
    
    # Parse the prompt to extract actions
    actions = parse_browser_prompt(prompt, url)
    
    if not actions:
        click.echo("❌ Could not parse task. Please be more specific.", err=True)
        return
        
    click.echo(f"📋 Parsed {len(actions)} actions:")
    for i, action in enumerate(actions, 1):
        click.echo(f"  {i}. {action.type.value}: {action.target or action.value or ''}")
        
    # Ask for confirmation
    if not click.confirm("\n▶️  Execute these actions?"):
        click.echo("Cancelled")
        return
        
    # Configure browser
    config = BrowserConfig(
        browser_type=BrowserType(browser),
        headless=False
    )
    
    controller = BrowserController(config)
    executor = BrowserActionExecutor(controller)
    
    try:
        # Start browser
        controller.start()
        
        # Execute actions
        click.echo("\n🚀 Executing actions...")
        
        for i, action in enumerate(actions):
            click.echo(f"  [{i+1}/{len(actions)}] {action.type.value}")
            try:
                executor.execute(action)
                import time
                time.sleep(0.5)  # Small delay between actions
            except Exception as e:
                click.echo(f"    ⚠️ Error: {e}", err=True)
                if not click.confirm("Continue with next action?"):
                    break
                    
        click.echo("✅ Task completed!")
        
        # Save if requested
        if save:
            recorder = BrowserRecorder(controller)
            recorder.actions = actions
            recorder.save_recording(save)
            click.echo(f"💾 Saved actions to: {save}")
            
        # Keep browser open
        click.echo("\nPress Enter to close browser...")
        input()
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        
    finally:
        controller.stop()


def parse_browser_prompt(prompt: str, url: Optional[str] = None):
    """
    Parse natural language prompt into browser actions.
    
    This is a simple implementation - could be enhanced with NLP/AI.
    """
    from ..browser.actions import BrowserAction, BrowserActionType
    
    actions = []
    prompt_lower = prompt.lower()
    
    # Extract URL if mentioned
    if not url:
        import re
        url_match = re.search(r'(?:go to|navigate to|open)\s+([^\s]+)', prompt_lower)
        if url_match:
            url = url_match.group(1)
            if not url.startswith('http'):
                url = f"https://{url}"
                
    # Add navigation action if URL found
    if url:
        actions.append(BrowserAction(
            type=BrowserActionType.NAVIGATE,
            target=url
        ))
        
    # Parse common actions
    if 'click' in prompt_lower:
        # Extract what to click
        import re
        click_match = re.search(r'click (?:on |the )?([^,\.]+)', prompt_lower)
        if click_match:
            target = click_match.group(1).strip()
            actions.append(BrowserAction(
                type=BrowserActionType.CLICK,
                target=f"button:contains('{target}'), a:contains('{target}'), [aria-label*='{target}']"
            ))
            
    if 'type' in prompt_lower or 'enter' in prompt_lower or 'fill' in prompt_lower:
        # Extract what to type
        import re
        type_match = re.search(r'(?:type|enter|fill in)\s+"([^"]+)"', prompt)
        if type_match:
            text = type_match.group(1)
            # Try to find target field
            field_match = re.search(r'(?:in|into) (?:the )?([^,\.]+)', prompt_lower)
            if field_match:
                field = field_match.group(1).strip()
                actions.append(BrowserAction(
                    type=BrowserActionType.TYPE,
                    target=f"input[placeholder*='{field}'], input[name*='{field}'], textarea[placeholder*='{field}']",
                    value=text
                ))
                
    if 'search' in prompt_lower:
        # Extract search term
        import re
        search_match = re.search(r'search (?:for )?"?([^"]+)"?', prompt_lower)
        if search_match:
            search_term = search_match.group(1).strip()
            # Add search actions
            actions.append(BrowserAction(
                type=BrowserActionType.TYPE,
                target="input[type='search'], input[name='q'], input[placeholder*='Search']",
                value=search_term
            ))
            actions.append(BrowserAction(
                type=BrowserActionType.SUBMIT,
                target="input[type='search'], input[name='q']"
            ))
            
    if 'screenshot' in prompt_lower:
        actions.append(BrowserAction(
            type=BrowserActionType.SCREENSHOT,
            value="screenshot.png"
        ))
        
    if 'wait' in prompt_lower:
        import re
        wait_match = re.search(r'wait (?:for )?(\d+)', prompt_lower)
        if wait_match:
            seconds = int(wait_match.group(1))
            actions.append(BrowserAction(
                type=BrowserActionType.WAIT,
                value=seconds
            ))
            
    return actions


# Register commands with main CLI
def register_commands(cli):
    """Register browser commands with the main CLI."""
    cli.add_command(browser)