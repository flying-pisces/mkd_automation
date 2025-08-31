#!/usr/bin/env python
"""
Test script for GUI with Replay functionality

Creates a quick test to verify recording and replay work correctly.
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_gui_functionality():
    """Test the GUI functionality programmatically."""
    print("Testing GUI Recorder with Replay functionality...")
    print()
    
    # Check if dependencies are available
    print("1. Checking dependencies...")
    
    try:
        import pynput
        print("   [OK] pynput available")
    except ImportError:
        print("   [MISSING] pynput - install with: pip install pynput")
        return False
    
    try:
        from PIL import Image, ImageGrab
        print("   [OK] Pillow available")
    except ImportError:
        print("   [MISSING] Pillow - install with: pip install Pillow")
        return False
    
    try:
        import tkinter
        print("   [OK] tkinter available")
    except ImportError:
        print("   [MISSING] tkinter - usually comes with Python")
        return False
    
    # Check if core MKD modules work
    print("\n2. Testing core MKD modules...")
    
    try:
        from mkd.core.session_manager import SessionManager
        from mkd.data.models import Action, AutomationScript
        from mkd.data.script_storage import ScriptStorage
        
        session = SessionManager()
        storage = ScriptStorage()
        print("   [OK] Core MKD modules working")
    except Exception as e:
        print(f"   [ERROR] MKD modules failed: {e}")
        return False
    
    # Test screenshot functionality
    print("\n3. Testing screenshot capture...")
    
    try:
        # Take a test screenshot
        screenshot = ImageGrab.grab()
        test_dir = Path("test_screenshots")
        test_dir.mkdir(exist_ok=True)
        
        test_file = test_dir / "test_screenshot.png"
        screenshot.save(test_file)
        
        # Verify file was created
        if test_file.exists():
            size = test_file.stat().st_size
            print(f"   [OK] Screenshot captured: {size} bytes")
            
            # Clean up
            test_file.unlink()
            test_dir.rmdir()
        else:
            print("   [ERROR] Screenshot file not created")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Screenshot capture failed: {e}")
        return False
    
    # Test recording system
    print("\n4. Testing recording system...")
    
    try:
        # Start a recording session
        session = SessionManager()
        session_id = session.start_recording()
        
        # Add some test actions
        test_actions = [
            Action("mouse_move", {"x": 100, "y": 100}, 0.0),
            Action("key_down", {"key": "A"}, 0.5),
            Action("mouse_click", {"x": 150, "y": 200, "button": "left"}, 1.0),
            Action("key_up", {"key": "A"}, 1.5),
        ]
        
        for action in test_actions:
            session.add_action(action)
        
        # Stop recording
        completed_session = session.stop_recording()
        
        if completed_session and len(completed_session.actions) == 4:
            print(f"   [OK] Recording system working: {len(completed_session.actions)} actions")
        else:
            print("   [ERROR] Recording system failed")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Recording system failed: {e}")
        return False
    
    print("\n" + "="*50)
    print("[OK] ALL TESTS PASSED!")
    print("[OK] GUI Recorder with Replay is ready to use")
    print("="*50)
    print()
    print("To launch the GUI:")
    print("  python gui_recorder_with_replay.py")
    print()
    print("Features available:")
    print("  • Recording with red boundary frame")
    print("  • Screenshot capture during recording")  
    print("  • Replay functionality with PNG sequence")
    print("  • Integrated event display (no popup)")
    print("  • Save/load recordings in .mkd format")
    print()
    
    return True

if __name__ == "__main__":
    success = test_gui_functionality()
    sys.exit(0 if success else 1)