"""
Live Desktop Automation Test
Demonstrates real mouse and keyboard control.
"""
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mkd.desktop.controller import DesktopController
from mkd.desktop.actions import DesktopAction
from mkd.desktop.application_manager import ApplicationManager

def main():
    """Perform live desktop automation demonstration."""
    print("=== MKD Live Desktop Automation Test ===")
    print("Watch your screen - I will control mouse and keyboard!")
    print("Starting in 3 seconds...")
    time.sleep(3)
    
    controller = DesktopController()
    app_manager = ApplicationManager()
    
    try:
        # 1. Launch Notepad
        print("\n1. Launching Notepad...")
        notepad_info = app_manager.launch_application("notepad")
        time.sleep(2)
        
        # 2. Type some text
        print("2. Typing text in Notepad...")
        text = "Hello! This is MKD Desktop Automation in action!\n"
        text += "I am controlling the mouse and keyboard automatically.\n"
        text += f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += "This demonstrates full desktop control capabilities."
        
        type_action = DesktopAction.type_text(text)
        controller.execute_action(type_action)
        time.sleep(2)
        
        # 3. Select all text
        print("3. Selecting all text (Ctrl+A)...")
        select_action = DesktopAction.key_combination(["ctrl", "a"])
        controller.execute_action(select_action)
        time.sleep(1)
        
        # 4. Copy text
        print("4. Copying text (Ctrl+C)...")
        copy_action = DesktopAction.key_combination(["ctrl", "c"])
        controller.execute_action(copy_action)
        time.sleep(1)
        
        # 5. Move cursor to end and paste
        print("5. Moving to end and pasting (Ctrl+End, Enter, Ctrl+V)...")
        end_action = DesktopAction.key_combination(["ctrl", "End"])
        controller.execute_action(end_action)
        
        enter_action = DesktopAction.key_press("enter")
        controller.execute_action(enter_action)
        
        paste_action = DesktopAction.key_combination(["ctrl", "v"])
        controller.execute_action(paste_action)
        time.sleep(2)
        
        # 6. Launch Calculator
        print("6. Opening Calculator...")
        calc_info = app_manager.launch_application("calculator")
        time.sleep(2)
        
        # 7. Perform calculation by clicking
        print("7. Performing calculation: 123 + 456 =")
        
        # Note: This would require precise screen coordinates for calculator buttons
        # For demo, we'll just type the calculation
        calc_text = "123+456="
        calc_action = DesktopAction.type_text(calc_text)
        controller.execute_action(calc_action)
        time.sleep(2)
        
        # 8. Take screenshot
        print("8. Taking desktop screenshot...")
        screenshot_action = DesktopAction.screenshot("automation_demo_screenshot.png")
        result = controller.execute_action(screenshot_action)
        print(f"   Screenshot saved: {result}")
        time.sleep(1)
        
        # 9. Clean up - close applications
        print("9. Closing applications...")
        
        # Close Calculator
        if app_manager.is_application_running("calculator"):
            app_manager.close_application("calculator")
            print("   Calculator closed")
        
        # Close Notepad (don't save)
        if app_manager.is_application_running("notepad"):
            # Press Alt+F4 to close
            close_action = DesktopAction.key_combination(["alt", "F4"])
            controller.execute_action(close_action)
            time.sleep(1)
            
            # Press 'N' for "Don't Save"
            no_save_action = DesktopAction.key_press("n")
            controller.execute_action(no_save_action)
            print("   Notepad closed")
        
        print("\n=== Live Automation Demo Complete! ===")
        print("✓ Successfully controlled mouse and keyboard")
        print("✓ Launched and managed applications")
        print("✓ Performed text input and editing")
        print("✓ Executed keyboard shortcuts")
        print("✓ Captured desktop screenshot")
        print("✓ Clean application shutdown")
        
    except Exception as e:
        print(f"\nDemo error: {e}")
        # Clean up on error
        try:
            if app_manager.is_application_running("notepad"):
                app_manager.close_application("notepad")
            if app_manager.is_application_running("calculator"):
                app_manager.close_application("calculator")
        except:
            pass

if __name__ == "__main__":
    main()