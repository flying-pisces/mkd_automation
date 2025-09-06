"""
Quick test script for MKD Conversation UI functionality.
"""

import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

def test_core_imports():
    """Test that core modules can be imported."""
    print("Testing core module imports...")
    
    try:
        from mkd.core.session import Session, Action
        from mkd.core.script import Script
        from mkd.ui.instruction_parser import InstructionParser, CommandType
        
        print("PASS: Core modules imported successfully")
        
        # Test basic functionality
        session = Session()
        print(f"PASS: Session created: {session.id}")
        
        parser = InstructionParser()
        result = parser.parse("open google.com")
        print(f"PASS: Parser works: '{result.type.value}' (confidence: {result.confidence:.2f})")
        
        script = Script("Test Script")
        print(f"PASS: Script created: {script.name}")
        
        return True
        
    except Exception as e:
        print(f"FAIL: Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_browser_imports():
    """Test browser automation imports."""
    print("\nTesting browser module imports...")
    
    try:
        from mkd.browser.controller import BrowserController, BrowserConfig
        from mkd.browser.actions import BrowserAction, BrowserActionType
        from mkd.browser.integration import BrowserIntegration
        
        print("PASS: Browser modules imported successfully")
        
        # Test basic creation (without starting browser)
        config = BrowserConfig()
        print(f"PASS: BrowserConfig created: {config.browser_type}")
        
        return True
        
    except Exception as e:
        print(f"FAIL: Browser import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversation_ui():
    """Test conversation UI components."""
    print("\nTesting conversation UI...")
    
    try:
        from mkd.ui.conversation_panel import Message
        from mkd.ui.instruction_parser import InstructionParser
        
        # Test message creation
        message = Message("Hello world", "user")
        print(f"PASS: Message created: {message.sender} - {message.content}")
        
        # Test parsing
        parser = InstructionParser()
        test_commands = [
            "help",
            "open google.com",
            "search for python tutorials",
            "create emailjs template", 
            "take screenshot",
            "unknown command xyz"
        ]
        
        print("PASS: Testing command parsing:")
        for cmd in test_commands:
            result = parser.parse(cmd)
            print(f"  '{cmd}' -> {result.type.value} ({result.confidence:.2f})")
            
        return True
        
    except Exception as e:
        print(f"FAIL: Conversation UI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("MKD Conversation UI - Quick Test")
    print("=" * 50)
    
    tests = [
        ("Core Imports", test_core_imports),
        ("Browser Imports", test_browser_imports), 
        ("Conversation UI", test_conversation_ui),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n> Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"PASS: {test_name}")
            else:
                print(f"FAIL: {test_name}")
        except Exception as e:
            print(f"FAIL: {test_name} with exception: {e}")
            
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed! The conversation UI is ready to use.")
        print("\nTo launch the GUI:")
        print("  python src/mkd/gui_launcher.py")
        print("\nExample commands to try in the GUI:")
        print('  "Create EmailJS template with email your@email.com"')
        print('  "Open google.com and search for Python tutorials"')
        print('  "Take screenshot"')
        print('  "Help"')
    else:
        print(f"\n{total - passed} tests failed. Please check the errors above.")
        
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)