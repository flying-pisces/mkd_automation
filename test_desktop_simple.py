"""
Simple Desktop Test
Basic test to verify desktop automation works with correct API.
"""
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Run simple desktop test."""
    print("MKD Desktop Automation - Simple Test")
    print("=" * 40)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from mkd.desktop.controller import DesktopController
        from mkd.desktop.actions import DesktopAction
        from mkd.desktop.application_manager import ApplicationManager
        from mkd.desktop.file_operations import FileOperations
        print("   [OK] All imports successful")
        
        # Test controller creation
        print("2. Testing controller creation...")
        controller = DesktopController()
        print("   [OK] DesktopController created")
        
        # Test action creation
        print("3. Testing action creation...")
        move_action = DesktopAction.mouse_move(500, 300)
        print(f"   [OK] Mouse move action: {move_action.description}")
        
        click_action = DesktopAction.mouse_click(500, 300)
        print(f"   [OK] Mouse click action: {click_action.description}")
        
        type_action = DesktopAction.type_text("Test")
        print(f"   [OK] Type text action: {type_action.description}")
        
        # Test other managers
        print("4. Testing other managers...")
        app_manager = ApplicationManager()
        print("   [OK] ApplicationManager created")
        
        file_ops = FileOperations()
        print("   [OK] FileOperations created")
        
        print("\n" + "=" * 40)
        print("[SUCCESS] All tests passed!")
        print("\nDesktop automation is ready. You can now:")
        print("- Run 'python desktop_automation_demo.py' for full demo")
        print("- Use individual controllers in your automation scripts")
        print("- Launch the GUI for conversation interface")
        
        print("\nNote: To actually move mouse/type text, install dependencies:")
        print("pip install pynput pillow")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print("\nTroubleshooting:")
        print("- Make sure all files are in src/mkd/ structure")
        print("- Check that Python can find the modules")
        print("- Install missing dependencies if needed")
        return False

if __name__ == "__main__":
    main()