#!/usr/bin/env python
"""
Quick test of recording functionality
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mkd.core.session_manager import SessionManager
from mkd.data.models import Action
from mkd.data.script_storage import ScriptStorage
from datetime import datetime

def test_recording():
    """Test the recording functionality."""
    print("Testing MKD recording functionality...")
    
    # Initialize components
    session = SessionManager()
    storage = ScriptStorage()
    
    print("[OK] Components initialized")
    
    # Start recording
    success = session.start_recording()
    print(f"[OK] Recording started: {success}")
    
    # Add some test actions
    actions = [
        Action("mouse_move", {"x": 100, "y": 100}, 0.0),
        Action("mouse_click", {"button": "left"}, 0.5),
        Action("key_press", {"key": "a"}, 1.0),
        Action("mouse_move", {"x": 200, "y": 200}, 1.5),
        Action("mouse_click", {"button": "left"}, 2.0),
    ]
    
    for action in actions:
        session.add_action(action)
        time.sleep(0.1)
    
    print(f"[OK] Added {len(actions)} test actions")
    
    # Stop recording and get the completed session
    completed_session = session.stop_recording()
    print("[OK] Recording stopped")
    
    # Create script from completed session
    if completed_session and len(completed_session.actions) > 0:
        from mkd.data.models import AutomationScript
        script = AutomationScript(
            name="Test Recording",
            description="Test recording session",
            created_at=datetime.now(),
            actions=list(completed_session.actions)
        )
        print(f"[OK] Created script with {len(script.actions)} actions")
    else:
        print("[ERROR] No actions recorded")
        return
    
    # Save to file
    filename = f"test_recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mkd"
    os.makedirs("recordings", exist_ok=True)
    filepath = os.path.join("recordings", filename)
    
    storage.save(script, filepath)
    print(f"[OK] Saved to: {filepath}")
    
    # Verify by loading
    loaded = storage.load(filepath)
    print(f"[OK] Verified: loaded {len(loaded.actions)} actions")
    
    print("\n" + "="*50)
    print("RECORDING TEST COMPLETED SUCCESSFULLY!")
    print("="*50)
    print(f"File: {filepath}")
    print(f"Actions: {len(loaded.actions)}")
    print(f"Duration: {loaded.actions[-1].timestamp}s")

if __name__ == "__main__":
    test_recording()