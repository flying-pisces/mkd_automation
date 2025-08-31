#!/usr/bin/env python
"""
Reliable Motion Recording Script using pynput library

This version uses pynput which is more stable for cross-platform input capture.

Usage:
    python record_motions_pynput.py

Controls:
    - Press 'q' to stop recording and save
    - Press 'p' to pause/resume recording
    - Recording starts immediately when script runs
"""

import sys
import os
import time
import threading
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from pynput import mouse, keyboard
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False
    print("pynput library not found. Installing...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
        from pynput import mouse, keyboard
        HAS_PYNPUT = True
        print("pynput installed successfully!")
    except Exception as e:
        print(f"Failed to install pynput: {e}")
        print("Please run: pip install pynput")

from mkd.core.session_manager import SessionManager
from mkd.core.config_manager import ConfigManager
from mkd.data.models import Action
from mkd.data.script_storage import ScriptStorage
from mkd.platform.detector import PlatformDetector

class PynputRecorder:
    """Motion recorder using pynput library."""
    
    def __init__(self):
        """Initialize the recorder."""
        self.session_manager = SessionManager()
        self.config_manager = ConfigManager()
        self.script_storage = ScriptStorage()
        self.platform_detector = PlatformDetector()
        
        self.recording = False
        self.paused = False
        self.start_time = None
        self.actions_recorded = 0
        
        # Listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Get recording settings
        self.settings = self.config_manager.get_recording_settings()
        
        print("=" * 60)
        print("MKD AUTOMATION - PYNPUT MOTION RECORDER")
        print("=" * 60)
        print(f"Platform: {self.platform_detector.get_platform()}")
        print(f"Sample Rate: {self.settings.get('sample_rate', 60)} Hz")
        print("Controls:")
        print("  'q' - Stop recording and save")
        print("  'p' - Pause/Resume recording")
        print("=" * 60)
        
    def get_current_timestamp(self):
        """Get timestamp relative to recording start."""
        if not self.start_time:
            return 0.0
        return time.time() - self.start_time
    
    def on_mouse_move(self, x, y):
        """Handle mouse move events."""
        if not self.recording or self.paused:
            return
            
        timestamp = self.get_current_timestamp()
        action = Action(
            type="mouse_move",
            data={"x": x, "y": y},
            timestamp=timestamp
        )
        self.session_manager.add_action(action)
        self.actions_recorded += 1
        
        # Throttle output for move events
        if self.actions_recorded % 50 == 0:
            print(f"Recorded {self.actions_recorded} actions (last: move to {x}, {y})")
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        if not self.recording or self.paused:
            return
            
        timestamp = self.get_current_timestamp()
        button_name = button.name if hasattr(button, 'name') else str(button)
        
        action = Action(
            type="mouse_down" if pressed else "mouse_up",
            data={"x": x, "y": y, "button": button_name},
            timestamp=timestamp
        )
        self.session_manager.add_action(action)
        self.actions_recorded += 1
        
        status = "down" if pressed else "up"
        print(f"Mouse {button_name} {status} at ({x}, {y}) - {self.actions_recorded} actions")
    
    def on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events."""
        if not self.recording or self.paused:
            return
            
        timestamp = self.get_current_timestamp()
        action = Action(
            type="mouse_wheel",
            data={"x": x, "y": y, "dx": dx, "dy": dy},
            timestamp=timestamp
        )
        self.session_manager.add_action(action)
        self.actions_recorded += 1
        
        print(f"Mouse scroll ({dx}, {dy}) at ({x}, {y}) - {self.actions_recorded} actions")
    
    def on_key_press(self, key):
        """Handle key press events."""
        if not self.recording or self.paused:
            return
            
        try:
            # Handle control keys
            if key == keyboard.Key.esc:
                return
            elif hasattr(key, 'char') and key.char == 'q':
                print("\n'q' pressed - stopping recording...")
                self.stop_and_save()
                return False  # Stop listener
            elif hasattr(key, 'char') and key.char == 'p':
                self.toggle_pause()
                return
                
            timestamp = self.get_current_timestamp()
            
            # Get key name
            if hasattr(key, 'char') and key.char:
                key_name = key.char
            elif hasattr(key, 'name'):
                key_name = key.name
            else:
                key_name = str(key)
                
            action = Action(
                type="key_down",
                data={"key": key_name},
                timestamp=timestamp
            )
            self.session_manager.add_action(action)
            self.actions_recorded += 1
            
            print(f"Key '{key_name}' pressed - {self.actions_recorded} actions")
            
        except Exception as e:
            # Ignore key handling errors
            pass
    
    def on_key_release(self, key):
        """Handle key release events."""
        if not self.recording or self.paused:
            return
            
        try:
            timestamp = self.get_current_timestamp()
            
            # Get key name
            if hasattr(key, 'char') and key.char:
                key_name = key.char
            elif hasattr(key, 'name'):
                key_name = key.name  
            else:
                key_name = str(key)
                
            action = Action(
                type="key_up",
                data={"key": key_name},
                timestamp=timestamp
            )
            self.session_manager.add_action(action)
            self.actions_recorded += 1
            
        except Exception as e:
            # Ignore key handling errors
            pass
    
    def start_recording(self):
        """Start recording motions."""
        if self.recording:
            print("Already recording!")
            return False
            
        if not HAS_PYNPUT:
            print("pynput library not available!")
            return False
            
        print("Starting recording...")
        self.recording = True
        self.paused = False
        self.start_time = time.time()
        self.actions_recorded = 0
        
        # Start session
        success = self.session_manager.start_recording()
        if not success:
            print("Failed to start recording session")
            return False
        
        # Start listeners
        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll
        )
        self.mouse_listener.start()
        
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()
        
        print(f"Recording started at {datetime.now().strftime('%H:%M:%S')}")
        print("Move your mouse and type to record actions...")
        print("Press 'q' to stop and save, 'p' to pause/resume")
        return True
    
    def stop_recording(self):
        """Stop recording."""
        if not self.recording:
            return None
            
        self.recording = False
        self.paused = False
        
        # Stop listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # Stop session
        completed_session = self.session_manager.stop_recording()
        
        duration = time.time() - self.start_time if self.start_time else 0
        print(f"\nRecording stopped after {duration:.1f} seconds")
        print(f"Recorded {self.actions_recorded} actions")
        
        return completed_session
    
    def toggle_pause(self):
        """Toggle pause/resume recording."""
        if not self.recording:
            print("Not currently recording")
            return
            
        self.paused = not self.paused
        status = "PAUSED" if self.paused else "RESUMED"
        print(f"\nRecording {status}")
    
    def save_recording(self, completed_session, filename=None):
        """Save the recorded session to file."""
        if not completed_session or len(completed_session.actions) == 0:
            print("No actions recorded to save")
            return None
            
        # Create script from session
        from mkd.data.models import AutomationScript
        script = AutomationScript(
            name="Recorded Session",
            description=f"Recording from {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            created_at=datetime.now(),
            actions=list(completed_session.actions)
        )
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pynput_recording_{timestamp}.mkd"
        
        # Ensure .mkd extension
        if not filename.endswith('.mkd'):
            filename += '.mkd'
            
        # Save to recordings directory
        recordings_dir = Path(__file__).parent / "recordings"
        recordings_dir.mkdir(exist_ok=True)
        filepath = recordings_dir / filename
        
        try:
            self.script_storage.save(script, str(filepath))
            print(f"\nRecording saved to: {filepath}")
            print(f"  Actions: {len(script.actions)}")
            print(f"  Duration: {script.actions[-1].timestamp:.1f}s" if script.actions else "0s")
            return str(filepath)
        except Exception as e:
            print(f"Error saving recording: {e}")
            return None
    
    def stop_and_save(self):
        """Stop recording and save to file."""
        completed_session = self.stop_recording()
        if completed_session:
            self.save_recording(completed_session)
    
    def run(self):
        """Main run loop."""
        if not self.start_recording():
            return
            
        try:
            # Keep running until stopped
            while self.recording:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nRecording interrupted by user")
            self.stop_and_save()

def main():
    """Main entry point."""
    if not HAS_PYNPUT:
        print("pynput library is required but not available")
        print("Please run: pip install pynput")
        return
        
    print("Initializing MKD Pynput Recorder...")
    
    try:
        recorder = PynputRecorder()
        recorder.run()
    except KeyboardInterrupt:
        print("\nRecording interrupted")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()