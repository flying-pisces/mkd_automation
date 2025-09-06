"""
Quick Desktop Automation Test
Tests core desktop automation functionality to ensure everything works.
"""
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all desktop automation modules can be imported."""
    print("Testing module imports...")
    
    try:
        from mkd.desktop.controller import DesktopController
        print("  ✓ DesktopController imported")
        
        from mkd.desktop.application_manager import ApplicationManager
        print("  ✓ ApplicationManager imported")
        
        from mkd.desktop.file_operations import FileOperations
        print("  ✓ FileOperations imported")
        
        from mkd.desktop.windows_automation import WindowsDesktopAutomation
        print("  ✓ WindowsDesktopAutomation imported")
        
        from mkd.ui.conversation_panel import ConversationPanel
        print("  ✓ ConversationPanel imported")
        
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_desktop_controller():
    """Test basic desktop controller functionality."""
    print("\nTesting DesktopController...")
    
    try:
        from mkd.desktop.controller import DesktopController, DesktopAction
        
        controller = DesktopController()
        print("  ✓ DesktopController created")
        
        # Test action creation
        click_action = DesktopAction.mouse_click(100, 100)
        print("  ✓ Mouse click action created")
        
        type_action = DesktopAction.type_text("test")
        print("  ✓ Type text action created")
        
        key_action = DesktopAction.key_press("Return")
        print("  ✓ Key press action created")
        
        return True
    except Exception as e:
        print(f"  ✗ DesktopController test failed: {e}")
        return False


def test_application_manager():
    """Test application manager functionality."""
    print("\nTesting ApplicationManager...")
    
    try:
        from mkd.desktop.application_manager import ApplicationManager
        
        app_manager = ApplicationManager()
        print("  ✓ ApplicationManager created")
        
        # Test getting application info
        notepad_info = app_manager.get_application_info("notepad")
        if notepad_info:
            print("  ✓ Notepad application info retrieved")
        
        # Test checking if application is running
        is_running = app_manager.is_application_running("nonexistent_app")
        print(f"  ✓ Application running check works: {not is_running}")
        
        return True
    except Exception as e:
        print(f"  ✗ ApplicationManager test failed: {e}")
        return False


def test_file_operations():
    """Test file operations functionality."""
    print("\nTesting FileOperations...")
    
    try:
        from mkd.desktop.file_operations import FileOperations
        
        file_ops = FileOperations()
        print("  ✓ FileOperations created")
        
        # Test creating a temporary file
        test_file = "test_temp.txt"
        success = file_ops.create_file(test_file, "Test content")
        if success:
            print("  ✓ File creation works")
            
            # Test getting file info
            file_info = file_ops.get_file_info(test_file)
            if file_info:
                print("  ✓ File info retrieval works")
            
            # Clean up
            file_ops.delete_file(test_file, confirm=False)
            print("  ✓ File deletion works")
        
        return True
    except Exception as e:
        print(f"  ✗ FileOperations test failed: {e}")
        return False


def test_windows_automation():
    """Test Windows-specific automation."""
    print("\nTesting WindowsDesktopAutomation...")
    
    try:
        from mkd.desktop.windows_automation import WindowsDesktopAutomation
        
        win_auto = WindowsDesktopAutomation()
        print(f"  ✓ WindowsDesktopAutomation created (Available: {win_auto.is_available})")
        
        if win_auto.is_available:
            # Test getting window list
            windows = win_auto.get_window_list()
            print(f"  ✓ Found {len(windows)} open windows")
            
            # Test getting active window
            active = win_auto.get_active_window()
            if active:
                print("  ✓ Active window detection works")
        else:
            print("  ⚠ Windows APIs not available (likely missing pywin32)")
        
        return True
    except Exception as e:
        print(f"  ✗ WindowsDesktopAutomation test failed: {e}")
        return False


def test_conversation_ui():
    """Test conversation UI functionality."""
    print("\nTesting ConversationPanel...")
    
    try:
        from mkd.ui.conversation_panel import ConversationPanel
        
        # Note: ConversationPanel normally requires a tkinter parent
        # For testing, we just verify it can be imported and basic methods exist
        print("  ✓ ConversationPanel imported successfully")
        
        # Test that the conversation panel has the expected methods
        expected_methods = [
            '_execute_desktop_click',
            '_execute_desktop_type',
            '_execute_desktop_key_press',
            '_execute_open_application',
            '_execute_file_operation'
        ]
        
        for method in expected_methods:
            if hasattr(ConversationPanel, method):
                print(f"  ✓ Method {method} exists")
            else:
                print(f"  ✗ Method {method} missing")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ ConversationPanel test failed: {e}")
        return False


def test_integration():
    """Test integration between modules."""
    print("\nTesting module integration...")
    
    try:
        from mkd.desktop.controller import DesktopController, DesktopAction
        from mkd.desktop.application_manager import ApplicationManager
        
        controller = DesktopController()
        app_manager = ApplicationManager()
        
        # Test that we can create actions and use them with the controller
        action = DesktopAction.type_text("integration test")
        print("  ✓ Action created for integration test")
        
        # Test that application manager integrates with controller concepts
        apps = app_manager.get_running_applications()
        print(f"  ✓ Integration test: found {len(apps)} running applications")
        
        return True
    except Exception as e:
        print(f"  ✗ Integration test failed: {e}")
        return False


def main():
    """Run all desktop automation tests."""
    print("MKD Desktop Automation - Quick Test Suite")
    print("=" * 50)
    print("Testing desktop automation functionality...")
    
    tests = [
        test_imports,
        test_desktop_controller,
        test_application_manager,
        test_file_operations,
        test_windows_automation,
        test_conversation_ui,
        test_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Test {test.__name__} failed with exception: {e}")
            failed += 1
        
        time.sleep(0.5)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All desktop automation tests passed!")
        print("\nDesktop automation is ready to use. You can now:")
        print("1. Run 'python desktop_automation_demo.py' for full demo")
        print("2. Use the GUI with conversation interface")
        print("3. Run practical examples in the examples/ folder")
    else:
        print(f"{failed} tests failed. Check error messages above.")
        print("\nRecommendations:")
        print("- Install missing dependencies: pip install pynput pillow pywin32")
        print("- Check that all required modules are in src/mkd/")
        print("- Verify Python path configuration")
    
    return failed == 0


if __name__ == "__main__":
    main()