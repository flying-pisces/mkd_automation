"""
Launch Web Demo
Opens the web browser to demonstrate the full web-based desktop automation interface.
"""
import time
import webbrowser
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mkd.desktop.controller import DesktopController
from mkd.desktop.actions import DesktopAction
from mkd.desktop.application_manager import ApplicationManager

def main():
    print("=== MKD Web UI Demo Launch ===")
    
    # Initialize desktop automation
    controller = DesktopController()
    app_manager = ApplicationManager()
    
    print("1. Web server is running at: http://localhost:5000")
    print("2. Opening web browser to display the interface...")
    
    # Wait a moment for the web server to be ready
    time.sleep(2)
    
    # Open the web interface in the default browser
    try:
        webbrowser.open('http://localhost:5000')
        print("   [OK] Web browser opened")
    except Exception as e:
        print(f"   [ERROR] Failed to open browser: {e}")
        print("   Please manually open: http://localhost:5000")
    
    print("\n3. Performing live demonstration...")
    print("   Watch the web interface - it will show real-time desktop control!")
    
    time.sleep(3)
    
    # Demonstrate some automation through the web interface
    try:
        print("\n4. Demonstrating desktop automation capabilities:")
        
        # Take a screenshot (this will be visible in the web UI)
        print("   - Taking screenshot...")
        screenshot_action = DesktopAction.screenshot("web_demo_screenshot.png")
        result = controller.execute_action(screenshot_action)
        print(f"     Screenshot saved: {result}")
        
        # Launch an application
        print("   - Launching Calculator...")
        calc_info = app_manager.launch_application("calculator")
        if calc_info:
            print(f"     Calculator launched (PID: {calc_info['pid']})")
            time.sleep(2)
            
            # Type in calculator
            print("   - Typing calculation: 123+456=")
            calc_text = "123+456="
            type_action = DesktopAction.type_text(calc_text)
            controller.execute_action(type_action)
            time.sleep(2)
            
            # Close calculator
            print("   - Closing Calculator...")
            close_action = DesktopAction.key_combination(["alt", "F4"])
            controller.execute_action(close_action)
            print("     Calculator closed")
        
        print("\n5. Web Interface Features Available:")
        print("   ✓ Natural Language Commands - Type commands like 'click at 500, 300'")
        print("   ✓ Mouse Control - Click anywhere on the mouse area to control desktop")
        print("   ✓ Keyboard Control - Type text and use keyboard shortcuts")
        print("   ✓ Application Management - Launch, close, and monitor applications")
        print("   ✓ Window Management - Minimize, maximize, close windows")
        print("   ✓ File Operations - Browse files and folders")
        print("   ✓ System Tools - Access Task Manager, Control Panel, etc.")
        print("   ✓ Screenshot Capture - Take and view desktop screenshots")
        print("   ✓ Real-time Communication - WebSocket-based live updates")
        
        print("\n6. Try these commands in the web interface:")
        example_commands = [
            "click at 800, 400",
            "type 'Hello from web interface!'",
            "open notepad",
            "take screenshot",
            "press ctrl+c",
            "open folder C:\\Users",
            "launch calculator",
            "minimize window"
        ]
        
        for i, cmd in enumerate(example_commands, 1):
            print(f"   {i}. \"{cmd}\"")
        
        print(f"\n=== WEB INTERFACE READY ===")
        print(f"Access URL: http://localhost:5000")
        print(f"The web interface provides COMPLETE desktop automation control!")
        print(f"All the desktop automation functions are now available through the web UI.")
        
    except Exception as e:
        print(f"   [ERROR] Demo error: {e}")
    
    print(f"\nWeb interface is running. Press Ctrl+C in the server terminal to stop.")

if __name__ == "__main__":
    main()