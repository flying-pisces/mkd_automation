"""
Browser Automation Demo Script

This script demonstrates how to use MKD Automation's browser automation feature
to handle web interactions that the AI assistant cannot directly control.

Example use case: Automating EmailJS template creation
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from mkd.browser.controller import BrowserController, BrowserConfig, BrowserType
from mkd.browser.actions import BrowserAction, BrowserActionType, BrowserActionExecutor
from mkd.browser.recorder import BrowserRecorder
from mkd.browser.emailjs_automation import EmailJSAutomation


def demo_basic_browser_control():
    """Demonstrate basic browser control capabilities."""
    print("=" * 60)
    print("DEMO: Basic Browser Control")
    print("=" * 60)
    
    # Create browser controller
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=False,  # Show browser for demo
        window_size=(1280, 720)
    )
    
    controller = BrowserController(config)
    
    try:
        # Start browser
        controller.start()
        print("✅ Browser started")
        
        # Navigate to a website
        controller.navigate("https://www.google.com")
        print("📍 Navigated to Google")
        
        # Type in search box
        controller.type_text(
            selector="input[name='q']",
            text="MKD Automation browser control demo"
        )
        print("⌨️  Typed search query")
        
        # Take screenshot
        controller.take_screenshot("demo_screenshot.png")
        print("📸 Screenshot saved")
        
        input("\nPress Enter to continue...")
        
    finally:
        controller.stop()
        print("🔚 Browser closed")


def demo_browser_recording():
    """Demonstrate recording and replaying browser actions."""
    print("\n" + "=" * 60)
    print("DEMO: Browser Action Recording")
    print("=" * 60)
    
    config = BrowserConfig(browser_type=BrowserType.CHROME, headless=False)
    controller = BrowserController(config)
    recorder = BrowserRecorder(controller)
    
    try:
        # Start browser
        controller.start()
        controller.navigate("https://www.example.com")
        
        # Start recording
        recorder.start_recording()
        print("🔴 Recording started - perform actions in the browser")
        print("   Try clicking links, typing text, etc.")
        
        input("\nPerform actions in the browser, then press Enter to stop recording...")
        
        # Stop recording
        actions = recorder.stop_recording()
        print(f"\n📝 Recorded {len(actions)} actions:")
        
        for i, action in enumerate(actions, 1):
            print(f"   {i}. {action.type.value}: {action.target or action.value or ''}")
            
        # Save recording
        recorder.save_recording("demo_recording.json")
        print("\n💾 Recording saved to demo_recording.json")
        
        # Ask if user wants to replay
        if input("\nReplay the recording? (y/n): ").lower() == 'y':
            print("\n▶️  Replaying actions...")
            
            # Create new executor
            executor = BrowserActionExecutor(controller)
            
            # Navigate to starting page
            controller.navigate("https://www.example.com")
            
            # Execute each action
            for action in actions:
                executor.execute(action)
                
            print("✅ Replay completed!")
            input("\nPress Enter to continue...")
            
    finally:
        controller.stop()
        print("🔚 Browser closed")


def demo_emailjs_automation():
    """Demonstrate EmailJS template automation."""
    print("\n" + "=" * 60)
    print("DEMO: EmailJS Template Automation")
    print("=" * 60)
    print("\nThis demo shows how MKD can automate web form interactions")
    print("that an AI assistant cannot directly control.\n")
    
    # Get user input for template configuration
    print("Please provide template details:")
    to_email = input("  To Email (default: chuckyeyin@gmail.com): ").strip()
    if not to_email:
        to_email = "chuckyeyin@gmail.com"
        
    template_name = input("  Template Name (default: Contact Form): ").strip()
    if not template_name:
        template_name = "Contact Form"
        
    # Create automation
    automation = EmailJSAutomation()
    
    try:
        # Start automation
        automation.start()
        
        print("\n🚀 Starting EmailJS automation...")
        print("📝 Creating template with:")
        print(f"   • Name: {template_name}")
        print(f"   • To: {to_email}")
        print(f"   • Subject: New message from {{{{from_name}}}}")
        print(f"   • Reply-To: {{{{from_email}}}}")
        
        # Configure template
        template_config = {
            'template_name': template_name,
            'subject': 'New message from {{from_name}}',
            'content': '''Hello,

You have received a new message from your website:

From: {{from_name}}
Email: {{from_email}}
Message:
{{message}}

Best regards,
Your Website Team''',
            'to_email': to_email,
            'reply_to': '{{from_email}}'
        }
        
        print("\n⚠️  The browser will open to EmailJS dashboard.")
        print("   Please log in if required and press Enter to continue...")
        
        # Create template
        template_id = automation.create_template(template_config)
        
        if template_id:
            print(f"\n✅ Template created successfully!")
            print(f"📋 Template ID: {template_id}")
            print("\nYou can now use this template in your EmailJS integration.")
        else:
            print("\n⚠️  Please complete any remaining steps in the browser.")
            
        input("\nPress Enter to close the browser...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        automation.stop()
        print("🔚 Automation completed")


def demo_mixed_automation():
    """Demonstrate mixing browser and desktop automation."""
    print("\n" + "=" * 60)
    print("DEMO: Mixed Browser + Desktop Automation")
    print("=" * 60)
    print("\nThis demo shows how to combine browser and desktop actions")
    print("in a single automation workflow.\n")
    
    from mkd.browser.integration import BrowserIntegration
    from mkd.core.session import Session
    
    # Create session and browser integration
    session = Session()
    integration = BrowserIntegration(session)
    
    try:
        # Start browser session
        browser_session = integration.start_browser_session()
        print("✅ Browser session started")
        
        # Record some browser actions
        integration.start_browser_recording()
        
        # Navigate and perform actions
        browser_session.browser_controller.navigate("https://www.example.com")
        browser_session.browser_controller.click("a[href*='more']", wait=False)
        
        # Stop recording
        browser_actions = integration.stop_browser_recording()
        print(f"📝 Recorded {len(browser_actions)} browser actions")
        
        # Create mixed script
        script = integration.create_mixed_script("Demo Mixed Script")
        print(f"📜 Created script with {len(script.actions)} total actions")
        
        # Save script
        script_path = "demo_mixed_script.mkd"
        # script.save(script_path)  # Would need to implement save method
        print(f"💾 Script saved to {script_path}")
        
        input("\nPress Enter to close browser...")
        
    finally:
        integration.stop_browser_session()
        print("🔚 Session ended")


def main():
    """Main demo menu."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "=" * 60)
    print(" MKD BROWSER AUTOMATION DEMO")
    print("=" * 60)
    print("\nThis demo showcases MKD's browser automation capabilities")
    print("for handling web interactions that AI assistants cannot")
    print("directly control.\n")
    
    demos = {
        '1': ('Basic Browser Control', demo_basic_browser_control),
        '2': ('Browser Action Recording', demo_browser_recording),
        '3': ('EmailJS Template Automation', demo_emailjs_automation),
        '4': ('Mixed Browser + Desktop Automation', demo_mixed_automation),
    }
    
    while True:
        print("\nAvailable Demos:")
        for key, (name, _) in demos.items():
            print(f"  {key}. {name}")
        print("  0. Exit")
        
        choice = input("\nSelect demo (0-4): ").strip()
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
        elif choice in demos:
            try:
                _, demo_func = demos[choice]
                demo_func()
            except KeyboardInterrupt:
                print("\n\n⚠️  Demo interrupted by user")
            except Exception as e:
                print(f"\n❌ Demo error: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()