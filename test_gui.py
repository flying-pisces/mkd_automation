"""
Test script for MKD Automation GUI with Conversation Interface.

This script tests the conversation UI functionality without requiring
full browser automation setup.
"""

import sys
import tkinter as tk
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

def test_instruction_parser():
    """Test the instruction parser functionality."""
    print("Testing Instruction Parser...")
    
    try:
        from mkd.ui.instruction_parser import InstructionParser, CommandType
        
        parser = InstructionParser()
        
        # Test instructions
        test_instructions = [
            "open google.com",
            "search for Python tutorials", 
            "click the submit button",
            'type "hello world" in the name field',
            "take screenshot",
            "start recording",
            "create emailjs template",
            "help",
            "status",
            "this is an unknown command"
        ]
        
        print("Parsing test instructions:")
        print("-" * 40)
        
        for instruction in test_instructions:
            result = parser.parse(instruction)
            print(f"'{instruction}' -> {result.type.value} (confidence: {result.confidence:.2f})")
            if result.parameters:
                print(f"  Parameters: {result.parameters}")
            if result.suggestions:
                print(f"  Suggestions: {result.suggestions[:2]}")
            print()
            
        print("✅ Instruction parser test completed")
        
    except Exception as e:
        print(f"❌ Parser test failed: {e}")
        import traceback
        traceback.print_exc()


def test_conversation_panel():
    """Test the conversation panel in isolation."""
    print("Testing Conversation Panel...")
    
    try:
        from mkd.ui.conversation_panel import ConversationPanel, Message
        from mkd.core.session import Session
        
        # Create test window
        root = tk.Tk()
        root.title("Test Conversation Panel")
        root.geometry("800x600")
        
        # Create session and panel
        session = Session()
        panel = ConversationPanel(root, session=session)
        panel.pack(fill='both', expand=True)
        
        # Add test messages
        test_messages = [
            Message("Hello! This is a test message.", "user"),
            Message("Hi there! I'm ready to help with automation tasks.", "mkd"),
            Message("Test system message", "System", message_type="system"),
            Message("Test error message", "System", message_type="error"),
            Message("Test success message", "System", message_type="success")
        ]
        
        for msg in test_messages:
            panel._add_message(msg)
            
        print("✅ Conversation panel created successfully")
        print("💡 Close the window to continue with tests...")
        
        # Run the GUI
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Conversation panel test failed: {e}")
        import traceback
        traceback.print_exc()


def test_conversation_examples():
    """Test the conversation examples."""
    print("Testing Conversation Examples...")
    
    try:
        from examples.conversation_examples import CONVERSATION_TEMPLATES, get_template_names
        
        template_names = get_template_names()
        print(f"Available templates: {template_names}")
        
        for name in template_names[:2]:  # Test first 2 templates
            template = CONVERSATION_TEMPLATES[name]
            print(f"\nTemplate: {template.name}")
            print(f"Description: {template.description}")
            print(f"Messages: {len(template.messages)}")
            
            # Show first few messages
            for msg in template.messages[:3]:
                print(f"  {msg['sender']}: {msg['content'][:50]}...")
                
        print("✅ Conversation examples test completed")
        
    except Exception as e:
        print(f"❌ Conversation examples test failed: {e}")
        import traceback
        traceback.print_exc()


def test_basic_gui():
    """Test basic GUI functionality without browser automation."""
    print("Testing Basic GUI...")
    
    try:
        # Mock the browser integration to avoid dependency issues
        class MockSession:
            def __init__(self):
                pass
                
        class MockBrowserIntegration:
            def __init__(self, session):
                self.session = session
                self.browser_session = None
                self._is_recording = False
                
            def start_browser_session(self):
                print("Mock: Browser session started")
                
            def stop_browser_session(self):
                print("Mock: Browser session stopped")
                
        # Patch imports temporarily
        sys.modules['mkd.core.session'] = type(sys)('mock_session')
        sys.modules['mkd.core.session'].Session = MockSession
        sys.modules['mkd.browser.integration'] = type(sys)('mock_integration')  
        sys.modules['mkd.browser.integration'].BrowserIntegration = MockBrowserIntegration
        
        from mkd.ui.main_gui import MKDMainGUI
        
        print("Creating GUI application...")
        app = MKDMainGUI()
        
        print("✅ GUI created successfully")
        print("💡 Close the window to finish the test...")
        
        # Run briefly
        app.root.after(2000, lambda: app.root.quit())  # Auto-close after 2 seconds
        app.run()
        
        print("✅ Basic GUI test completed")
        
    except Exception as e:
        print(f"❌ Basic GUI test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    print("🧪 MKD GUI Test Suite")
    print("=" * 40)
    
    tests = [
        ("Instruction Parser", test_instruction_parser),
        ("Conversation Examples", test_conversation_examples),
        ("Conversation Panel", test_conversation_panel),
        # ("Basic GUI", test_basic_gui),  # Uncomment to test GUI
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            test_func()
        except KeyboardInterrupt:
            print(f"\n⚠️ {test_name} test interrupted by user")
            break
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            
    print(f"\n🎉 Test suite completed!")
    print("\nTo launch the full GUI:")
    print("  python src/mkd/gui_launcher.py")
    print("\nTo test browser automation:")
    print("  python examples/browser_automation_demo.py")


if __name__ == "__main__":
    main()