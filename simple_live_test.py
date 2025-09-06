"""
Simple Live Test - Minimal desktop automation demo
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mkd.desktop.controller import DesktopController
from mkd.desktop.actions import DesktopAction
from mkd.desktop.application_manager import ApplicationManager

def main():
    print("=== Simple Live Desktop Test ===")
    print("Starting automation in 3 seconds...")
    time.sleep(3)
    
    controller = DesktopController()
    app_manager = ApplicationManager()
    
    try:
        # 1. Launch Notepad
        print("1. Opening Notepad...")
        app_manager.launch_application("notepad")
        time.sleep(2)
        
        # 2. Type text
        print("2. Typing demonstration text...")
        text = "MKD Desktop Automation is working!\nThis text was typed automatically."
        type_action = DesktopAction.type_text(text)
        controller.execute_action(type_action)
        time.sleep(2)
        
        # 3. Select all
        print("3. Selecting all text (Ctrl+A)...")
        select_action = DesktopAction.key_combination(["ctrl", "a"])
        controller.execute_action(select_action)
        time.sleep(1)
        
        # 4. Take screenshot
        print("4. Taking screenshot...")
        screenshot_action = DesktopAction.screenshot("live_test_screenshot.png")
        result = controller.execute_action(screenshot_action)
        print(f"   Screenshot saved: {result}")
        
        # 5. Close Notepad without saving
        print("5. Closing Notepad...")
        close_action = DesktopAction.key_combination(["alt", "F4"])
        controller.execute_action(close_action)
        time.sleep(1)
        
        # Don't save
        no_save = DesktopAction.key_press("n")
        controller.execute_action(no_save)
        
        print("\n✓ Live automation test completed successfully!")
        print("The system has full mouse and keyboard control.")
        
    except Exception as e:
        print(f"Error: {e}")
        # Cleanup
        try:
            app_manager.close_application("notepad")
        except:
            pass

if __name__ == "__main__":
    main()