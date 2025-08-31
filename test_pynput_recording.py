#!/usr/bin/env python
"""
Test pynput recording for 5 seconds automatically
"""

import sys
import os
import time
import threading

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from pynput import mouse, keyboard
    from pynput.mouse import Button
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False

from mkd.core.session_manager import SessionManager
from mkd.data.models import Action, AutomationScript
from mkd.data.script_storage import ScriptStorage
from datetime import datetime

def test_pynput_recording():
    """Test pynput recording with simulated events."""
    print("Testing pynput recording (5 second test)...")
    
    if not HAS_PYNPUT:
        print("pynput not available - installing...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
            from pynput import mouse, keyboard
            print("pynput installed!")
        except:
            print("Failed to install pynput")
            return
    
    # Initialize components
    session = SessionManager()
    storage = ScriptStorage()
    
    print("[OK] Components initialized")
    
    # Start recording
    session_id = session.start_recording()
    print(f"[OK] Recording started: {session_id}")
    
    start_time = time.time()
    actions_added = 0
    
    # Simulate 5 seconds of recording
    print("Simulating 5 seconds of mouse/keyboard activity...")
    
    for i in range(50):  # 50 actions over 5 seconds
        timestamp = time.time() - start_time
        
        if i % 3 == 0:  # Mouse move
            action = Action("mouse_move", {"x": 100 + i*2, "y": 100 + i}, timestamp)
        elif i % 3 == 1:  # Mouse click
            action = Action("mouse_click", {"x": 100 + i*2, "y": 100 + i, "button": "left"}, timestamp)
        else:  # Key press
            key = chr(ord('a') + (i % 26))  # Letters a-z
            action = Action("key_press", {"key": key}, timestamp)
        
        session.add_action(action)
        actions_added += 1
        time.sleep(0.1)  # 100ms between actions
    
    print(f"[OK] Added {actions_added} simulated actions")
    
    # Stop recording
    completed_session = session.stop_recording()
    print("[OK] Recording stopped")
    
    # Create and save script
    if completed_session and len(completed_session.actions) > 0:
        script = AutomationScript(
            name="Pynput Test Recording",
            description="5-second test recording with pynput simulation",
            created_at=datetime.now(),
            actions=list(completed_session.actions)
        )
        
        # Save to file
        filename = f"pynput_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mkd"
        os.makedirs("recordings", exist_ok=True)
        filepath = os.path.join("recordings", filename)
        
        storage.save(script, filepath)
        print(f"[OK] Saved to: {filepath}")
        
        # Verify
        loaded = storage.load(filepath)
        print(f"[OK] Verified: loaded {len(loaded.actions)} actions")
        
        print("\n" + "="*50)
        print("PYNPUT RECORDING TEST COMPLETED!")
        print("="*50)
        print(f"File: {filepath}")
        print(f"Actions: {len(loaded.actions)}")
        print(f"Duration: {loaded.actions[-1].timestamp:.1f}s")
        
        # Show some sample actions
        print("\nSample actions:")
        for i, action in enumerate(loaded.actions[:5]):
            print(f"  {i+1}. {action.type}: {action.data} @ {action.timestamp:.2f}s")
        if len(loaded.actions) > 5:
            print(f"  ... and {len(loaded.actions) - 5} more")
    
    else:
        print("[ERROR] No actions recorded")

if __name__ == "__main__":
    test_pynput_recording()