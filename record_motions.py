#!/usr/bin/env python
"""
Standalone Motion Recording Script

Run this file to start recording mouse and keyboard motions directly,
equivalent to clicking "Start Recording" in the Chrome extension.

Usage:
    python record_motions.py

Controls:
    - Script starts recording immediately
    - Press Ctrl+Shift+S to stop recording and save
    - Press Ctrl+Shift+Q to quit without saving
    - Press Ctrl+Shift+P to pause/resume recording
"""

import sys
import os
import time
import signal
import threading
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import keyboard
    import mouse
    HAS_INPUT_LIBS = True
except ImportError:
    HAS_INPUT_LIBS = False
    print("Warning: keyboard and mouse libraries not installed")
    print("Install with: pip install keyboard mouse")

from mkd.core.session_manager import SessionManager
from mkd.core.config_manager import ConfigManager
from mkd.data.models import Action
from mkd.data.script_storage import ScriptStorage
from mkd.platform.detector import PlatformDetector

class StandaloneRecorder:
    """Standalone motion recorder."""
    
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
        
        # Get recording settings
        self.settings = self.config_manager.get_recording_settings()
        
        print("=" * 60)
        print("MKD AUTOMATION - STANDALONE MOTION RECORDER")
        print("=" * 60)
        print(f"Platform: {self.platform_detector.get_platform()}")
        print(f"Sample Rate: {self.settings.get('sample_rate', 60)} Hz")
        print(f"Record Mouse: {self.settings.get('record_mouse', True)}")
        print(f"Record Keyboard: {self.settings.get('record_keyboard', True)}")
        print("=" * 60)
        
    def setup_hotkeys(self):
        """Setup global hotkeys for recording control."""
        if not HAS_INPUT_LIBS:
            print("Hotkeys not available - input libraries not installed")
            return
        
        try:
            # Stop and save: Ctrl+Shift+S
            keyboard.add_hotkey('ctrl+shift+s', self.stop_and_save)
            
            # Quit without saving: Ctrl+Shift+Q
            keyboard.add_hotkey('ctrl+shift+q', self.quit_without_saving)
            
            # Pause/Resume: Ctrl+Shift+P
            keyboard.add_hotkey('ctrl+shift+p', self.toggle_pause)
            
            print("Hotkeys registered:")
            print("  Ctrl+Shift+S - Stop recording and save")
            print("  Ctrl+Shift+Q - Quit without saving")
            print("  Ctrl+Shift+P - Pause/Resume recording")
            print()
        except Exception as e:
            print(f"Warning: Could not setup hotkeys: {e}")
            
    def get_current_timestamp(self):
        """Get timestamp relative to recording start."""
        if not self.start_time:
            return 0.0
        return time.time() - self.start_time
    
    def record_mouse_event(self, event):
        """Record mouse events."""
        if not self.recording or self.paused:
            return
            
        timestamp = self.get_current_timestamp()
        
        try:
            # Handle different event types based on mouse library
            if hasattr(event, 'event_type'):
                event_type = event.event_type
                
                # Check for move events (try different constant names)
                if (event_type == 'move' or 
                    (hasattr(mouse, 'MoveEvent') and isinstance(event, mouse.MoveEvent)) or
                    str(event_type).lower() == 'move'):
                    action = Action(
                        type="mouse_move",
                        data={"x": getattr(event, 'x', 0), "y": getattr(event, 'y', 0)},
                        timestamp=timestamp
                    )
                    
                # Check for button down events
                elif (event_type == 'down' or 
                      (hasattr(mouse, 'ButtonEvent') and isinstance(event, mouse.ButtonEvent) and getattr(event, 'event_type', '') == 'down')):
                    action = Action(
                        type="mouse_down",
                        data={
                            "x": getattr(event, 'x', 0), 
                            "y": getattr(event, 'y', 0), 
                            "button": getattr(event, 'button', 'unknown')
                        },
                        timestamp=timestamp
                    )
                    
                # Check for button up events  
                elif (event_type == 'up' or
                      (hasattr(mouse, 'ButtonEvent') and isinstance(event, mouse.ButtonEvent) and getattr(event, 'event_type', '') == 'up')):
                    action = Action(
                        type="mouse_up",
                        data={
                            "x": getattr(event, 'x', 0), 
                            "y": getattr(event, 'y', 0), 
                            "button": getattr(event, 'button', 'unknown')
                        },
                        timestamp=timestamp
                    )
                    
                # Check for wheel events
                elif (event_type == 'wheel' or
                      (hasattr(mouse, 'WheelEvent') and isinstance(event, mouse.WheelEvent))):
                    action = Action(
                        type="mouse_wheel",
                        data={
                            "x": getattr(event, 'x', 0), 
                            "y": getattr(event, 'y', 0), 
                            "delta": getattr(event, 'delta', 0)
                        },
                        timestamp=timestamp
                    )
                else:
                    # Unknown event type, skip
                    return
                    
                self.session_manager.add_action(action)
                self.actions_recorded += 1
                
                # Throttle move events to avoid spam
                if action.type == "mouse_move" and self.actions_recorded % 10 == 0:
                    print(f"Recorded {self.actions_recorded} actions...")
                    
        except Exception as e:
            # Silently ignore mouse event errors to prevent crash
            pass
    
    def record_keyboard_event(self, event):
        """Record keyboard events."""
        if not self.recording or self.paused:
            return
            
        timestamp = self.get_current_timestamp()
        
        if hasattr(event, 'event_type') and hasattr(event, 'name'):
            action_type = "key_down" if event.event_type == keyboard.KEY_DOWN else "key_up"
            
            action = Action(
                type=action_type,
                data={
                    "key": event.name,
                    "scan_code": getattr(event, 'scan_code', None)
                },
                timestamp=timestamp
            )
            
            self.session_manager.add_action(action)
            self.actions_recorded += 1
    
    def start_recording(self):
        """Start recording motions."""
        if self.recording:
            print("Already recording!")
            return
            
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
        
        # Setup event listeners
        if HAS_INPUT_LIBS:
            if self.settings.get('record_mouse', True):
                mouse.hook(self.record_mouse_event)
                print("Mouse recording enabled")
            
            if self.settings.get('record_keyboard', True):
                keyboard.hook(self.record_keyboard_event)
                print("Keyboard recording enabled")
        else:
            print("Input libraries not available - simulating recording")
            # Simulate some actions for testing
            threading.Thread(target=self._simulate_recording, daemon=True).start()
        
        print(f"Recording started at {datetime.now().strftime('%H:%M:%S')}")
        print("Use hotkeys to control recording or press Enter to stop manually")
        return True
    
    def _simulate_recording(self):
        """Simulate recording for testing when input libraries unavailable."""
        for i in range(10):
            if not self.recording or self.paused:
                break
            time.sleep(1)
            action = Action(
                type="simulated_action",
                data={"step": i, "message": f"Simulated action {i}"},
                timestamp=self.get_current_timestamp()
            )
            self.session_manager.add_action(action)
            self.actions_recorded += 1
    
    def stop_recording(self):
        """Stop recording."""
        if not self.recording:
            return False
            
        self.recording = False
        self.paused = False
        
        # Unhook event listeners
        if HAS_INPUT_LIBS:
            try:
                mouse.unhook_all()
                keyboard.unhook_all()
            except:
                pass
        
        # Stop session
        self.session_manager.stop_recording()
        
        duration = time.time() - self.start_time if self.start_time else 0
        print(f"\nRecording stopped after {duration:.1f} seconds")
        print(f"Recorded {self.actions_recorded} actions")
        
        return True
    
    def toggle_pause(self):
        """Toggle pause/resume recording."""
        if not self.recording:
            print("Not currently recording")
            return
            
        self.paused = not self.paused
        status = "paused" if self.paused else "resumed"
        print(f"Recording {status}")
    
    def save_recording(self, filename=None):
        """Save the recorded session to file."""
        script = self.session_manager.to_script()
        if not script or len(script.actions) == 0:
            print("No actions recorded to save")
            return None
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.mkd"
        
        # Ensure .mkd extension
        if not filename.endswith('.mkd'):
            filename += '.mkd'
            
        # Save to recordings directory
        recordings_dir = Path(__file__).parent / "recordings"
        recordings_dir.mkdir(exist_ok=True)
        filepath = recordings_dir / filename
        
        try:
            self.script_storage.save(script, str(filepath))
            print(f"Recording saved to: {filepath}")
            print(f"  Actions: {len(script.actions)}")
            print(f"  Duration: {script.actions[-1].timestamp:.1f}s" if script.actions else "0s")
            return str(filepath)
        except Exception as e:
            print(f"Error saving recording: {e}")
            return None
    
    def stop_and_save(self):
        """Stop recording and save to file."""
        if self.stop_recording():
            self.save_recording()
        self.cleanup_and_exit()
    
    def quit_without_saving(self):
        """Quit without saving."""
        if self.recording:
            self.stop_recording()
            print("Recording discarded")
        self.cleanup_and_exit()
    
    def cleanup_and_exit(self):
        """Cleanup and exit."""
        print("Exiting...")
        if HAS_INPUT_LIBS:
            try:
                keyboard.unhook_all()
                mouse.unhook_all()
            except:
                pass
        os._exit(0)
    
    def run(self):
        """Main run loop."""
        # Setup signal handlers
        signal.signal(signal.SIGINT, lambda sig, frame: self.quit_without_saving())
        
        # Setup hotkeys
        self.setup_hotkeys()
        
        # Start recording immediately
        if not self.start_recording():
            return
        
        # Keep running until stopped
        try:
            if HAS_INPUT_LIBS:
                # Wait for hotkeys
                while self.recording:
                    time.sleep(0.1)
            else:
                # Manual control when input libraries not available
                input("\nPress Enter to stop recording...")
                self.stop_and_save()
                
        except KeyboardInterrupt:
            self.quit_without_saving()

def main():
    """Main entry point."""
    print("Initializing MKD Motion Recorder...")
    
    try:
        recorder = StandaloneRecorder()
        recorder.run()
    except KeyboardInterrupt:
        print("\nRecording interrupted")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()