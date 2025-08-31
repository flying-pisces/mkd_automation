"""
Action Replay Engine - Automation Mode Implementation

Executes recorded actions to reproduce user interactions
with safety controls and error handling.
"""

import time
import threading
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
import tkinter as tk
from tkinter import ttk, messagebox

try:
    from pynput import mouse, keyboard
    from pynput.mouse import Button
    from pynput.keyboard import Key
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False

import sys
import platform


class ReplayStatus(Enum):
    """Status of action replay."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class ReplayOptions:
    """Options for action replay."""
    playback_speed: float = 1.0
    use_original_timing: bool = True
    skip_mouse_moves: bool = False
    show_visual_feedback: bool = True
    emergency_stop_key: str = "esc"
    pause_on_error: bool = True
    dry_run: bool = False  # Preview without executing
    
    # Safety options
    confirm_start: bool = True
    restrict_to_window: Optional[str] = None
    max_duration: Optional[float] = None  # Maximum replay time in seconds


class SafetyMonitor:
    """Monitors and enforces safety during replay."""
    
    def __init__(self):
        self.emergency_stop = False
        self.listener = None
        self.start_time = None
        self.max_duration = None
        
    def activate(self, emergency_key: str = "esc", max_duration: Optional[float] = None):
        """Activate safety monitoring."""
        self.emergency_stop = False
        self.start_time = time.time()
        self.max_duration = max_duration
        
        if HAS_PYNPUT:
            # Listen for emergency stop key
            def on_press(key):
                try:
                    if hasattr(key, 'name') and key.name == emergency_key:
                        self.trigger_emergency_stop()
                except:
                    pass
            
            self.listener = keyboard.Listener(on_press=on_press)
            self.listener.start()
    
    def deactivate(self):
        """Deactivate safety monitoring."""
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def trigger_emergency_stop(self):
        """Trigger emergency stop."""
        self.emergency_stop = True
        print("EMERGENCY STOP TRIGGERED!")
    
    def check_safety(self) -> bool:
        """Check if it's safe to continue."""
        # Check emergency stop
        if self.emergency_stop:
            return False
        
        # Check duration limit
        if self.max_duration and self.start_time:
            if time.time() - self.start_time > self.max_duration:
                print(f"Max duration ({self.max_duration}s) exceeded")
                return False
        
        return True


class ActionExecutor:
    """Executes individual actions."""
    
    def __init__(self):
        if HAS_PYNPUT:
            self.mouse_controller = mouse.Controller()
            self.keyboard_controller = keyboard.Controller()
        else:
            self.mouse_controller = None
            self.keyboard_controller = None
    
    def execute_action(self, action: Dict, dry_run: bool = False) -> bool:
        """Execute a single action."""
        if not HAS_PYNPUT:
            print(f"[DRY RUN] Would execute: {action}")
            return True
        
        if dry_run:
            print(f"[DRY RUN] {action['type']}: {action.get('data', {})}")
            return True
        
        try:
            action_type = action['type']
            data = action.get('data', {})
            
            if action_type == 'mouse_move':
                return self._execute_mouse_move(data)
            elif action_type == 'mouse_click':
                return self._execute_mouse_click(data)
            elif action_type == 'mouse_press':
                return self._execute_mouse_press(data)
            elif action_type == 'mouse_release':
                return self._execute_mouse_release(data)
            elif action_type == 'key_press':
                return self._execute_key_press(data)
            elif action_type == 'key_release':
                return self._execute_key_release(data)
            elif action_type == 'scroll':
                return self._execute_scroll(data)
            else:
                print(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            print(f"Error executing action {action_type}: {e}")
            return False
        
        return True
    
    def _execute_mouse_move(self, data: Dict) -> bool:
        """Execute mouse move."""
        x = data.get('x', 0)
        y = data.get('y', 0)
        self.mouse_controller.position = (x, y)
        return True
    
    def _execute_mouse_click(self, data: Dict) -> bool:
        """Execute mouse click."""
        x = data.get('x', 0)
        y = data.get('y', 0)
        button_name = data.get('button', 'left')
        
        # Move to position
        self.mouse_controller.position = (x, y)
        
        # Map button name to pynput button
        button_map = {
            'left': Button.left,
            'right': Button.right,
            'middle': Button.middle
        }
        button = button_map.get(button_name.lower(), Button.left)
        
        # Click
        self.mouse_controller.click(button)
        return True
    
    def _execute_mouse_press(self, data: Dict) -> bool:
        """Execute mouse press."""
        x = data.get('x', 0)
        y = data.get('y', 0)
        button_name = data.get('button', 'left')
        
        self.mouse_controller.position = (x, y)
        
        button_map = {
            'left': Button.left,
            'right': Button.right,
            'middle': Button.middle
        }
        button = button_map.get(button_name.lower(), Button.left)
        
        self.mouse_controller.press(button)
        return True
    
    def _execute_mouse_release(self, data: Dict) -> bool:
        """Execute mouse release."""
        button_name = data.get('button', 'left')
        
        button_map = {
            'left': Button.left,
            'right': Button.right,
            'middle': Button.middle
        }
        button = button_map.get(button_name.lower(), Button.left)
        
        self.mouse_controller.release(button)
        return True
    
    def _execute_key_press(self, data: Dict) -> bool:
        """Execute key press."""
        key_name = data.get('key', '')
        
        # Handle special keys
        if key_name.startswith('Key.'):
            key_attr = key_name.split('.')[1]
            if hasattr(Key, key_attr):
                key = getattr(Key, key_attr)
                self.keyboard_controller.press(key)
                self.keyboard_controller.release(key)
        else:
            # Regular character
            if len(key_name) == 1:
                self.keyboard_controller.press(key_name)
                self.keyboard_controller.release(key_name)
        
        return True
    
    def _execute_key_release(self, data: Dict) -> bool:
        """Execute key release."""
        # Handled in key_press for simplicity
        return True
    
    def _execute_scroll(self, data: Dict) -> bool:
        """Execute scroll action."""
        dx = data.get('dx', 0)
        dy = data.get('dy', 0)
        self.mouse_controller.scroll(dx, dy)
        return True


class ActionReplayEngine:
    """Main engine for action replay."""
    
    def __init__(self):
        self.executor = ActionExecutor()
        self.safety_monitor = SafetyMonitor()
        self.status = ReplayStatus.IDLE
        self.actions: List[Dict] = []
        self.current_action_index = 0
        self.replay_thread = None
        self.options = ReplayOptions()
        
        # Callbacks
        self.on_progress: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
    
    def load_recording(self, recording_dir: Path) -> bool:
        """Load actions from recording."""
        # Load actions from metadata (simplified for demo)
        metadata_file = recording_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                data = json.load(f)
                self.actions = data.get('actions', [])
                return True
        
        # In real implementation, would load from .mkd file
        return False
    
    def start_replay(self, options: Optional[ReplayOptions] = None):
        """Start action replay."""
        if self.status == ReplayStatus.RUNNING:
            return False
        
        self.options = options or ReplayOptions()
        
        # Confirm start if required
        if self.options.confirm_start and not self.options.dry_run:
            if not self._confirm_replay_start():
                return False
        
        # Initialize
        self.status = ReplayStatus.RUNNING
        self.current_action_index = 0
        
        # Activate safety monitor
        self.safety_monitor.activate(
            self.options.emergency_stop_key,
            self.options.max_duration
        )
        
        # Start replay thread
        self.replay_thread = threading.Thread(target=self._replay_loop)
        self.replay_thread.daemon = True
        self.replay_thread.start()
        
        return True
    
    def pause_replay(self):
        """Pause replay."""
        if self.status == ReplayStatus.RUNNING:
            self.status = ReplayStatus.PAUSED
    
    def resume_replay(self):
        """Resume replay."""
        if self.status == ReplayStatus.PAUSED:
            self.status = ReplayStatus.RUNNING
    
    def stop_replay(self):
        """Stop replay."""
        self.status = ReplayStatus.STOPPED
        self.safety_monitor.deactivate()
    
    def _replay_loop(self):
        """Main replay loop."""
        start_time = time.time()
        last_timestamp = 0
        
        while self.current_action_index < len(self.actions):
            # Check status
            if self.status == ReplayStatus.STOPPED:
                break
            
            if self.status == ReplayStatus.PAUSED:
                time.sleep(0.1)
                continue
            
            # Check safety
            if not self.safety_monitor.check_safety():
                self.status = ReplayStatus.STOPPED
                if self.on_error:
                    self.on_error("Safety stop triggered")
                break
            
            # Get current action
            action = self.actions[self.current_action_index]
            
            # Skip mouse moves if configured
            if self.options.skip_mouse_moves and action['type'] == 'mouse_move':
                self.current_action_index += 1
                continue
            
            # Calculate delay
            if self.options.use_original_timing:
                target_time = action['timestamp'] / self.options.playback_speed
                elapsed = time.time() - start_time
                delay = target_time - elapsed
                
                if delay > 0:
                    time.sleep(delay)
            else:
                # Fixed delay between actions
                time.sleep(0.05 / self.options.playback_speed)
            
            # Execute action
            success = self.executor.execute_action(action, self.options.dry_run)
            
            if not success and self.options.pause_on_error:
                self.status = ReplayStatus.PAUSED
                if self.on_error:
                    self.on_error(f"Failed to execute action: {action}")
                continue
            
            # Update progress
            self.current_action_index += 1
            if self.on_progress:
                progress = self.current_action_index / len(self.actions)
                self.on_progress(progress, action)
        
        # Completed
        self.status = ReplayStatus.COMPLETED
        self.safety_monitor.deactivate()
        
        if self.on_complete:
            self.on_complete()
    
    def _confirm_replay_start(self) -> bool:
        """Show confirmation dialog."""
        root = tk.Tk()
        root.withdraw()
        
        message = (
            "Action Replay will control your mouse and keyboard.\n\n"
            f"• {len(self.actions)} actions will be executed\n"
            f"• Press {self.options.emergency_stop_key.upper()} to stop\n"
            f"• Speed: {self.options.playback_speed}x\n\n"
            "Continue?"
        )
        
        result = messagebox.askyesno(
            "Confirm Action Replay",
            message,
            icon="warning"
        )
        
        root.destroy()
        return result


class ActionReplayControlPanel:
    """Control panel for action replay."""
    
    def __init__(self, recording_dir: Path):
        self.engine = ActionReplayEngine()
        self.recording_dir = recording_dir
        
        # Create window
        self.window = tk.Toplevel()
        self.window.title("Action Replay - Automation Mode")
        self.window.geometry("500x400")
        
        # Make it stay on top
        self.window.attributes('-topmost', True)
        
        # Load recording
        if not self.engine.load_recording(recording_dir):
            messagebox.showerror("Error", "Failed to load recording")
            self.window.destroy()
            return
        
        # Set callbacks
        self.engine.on_progress = self.update_progress
        self.engine.on_complete = self.on_complete
        self.engine.on_error = self.on_error
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup control panel UI."""
        # Warning header
        warning_frame = tk.Frame(self.window, bg="yellow", height=40)
        warning_frame.pack(fill="x")
        warning_frame.pack_propagate(False)
        
        tk.Label(warning_frame, text="⚠️ AUTOMATION MODE ACTIVE",
                font=("Arial", 14, "bold"), bg="yellow").pack(pady=8)
        
        # Progress
        progress_frame = tk.Frame(self.window)
        progress_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(progress_frame, text="Progress:").pack(anchor="w")
        self.progress_bar = ttk.Progressbar(progress_frame, length=400)
        self.progress_bar.pack(fill="x", pady=5)
        
        self.progress_label = tk.Label(progress_frame, text="Ready to start")
        self.progress_label.pack(anchor="w")
        
        self.action_label = tk.Label(progress_frame, text="", fg="blue")
        self.action_label.pack(anchor="w", pady=5)
        
        # Speed control
        speed_frame = tk.Frame(self.window)
        speed_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(speed_frame, text="Speed:").pack(side="left", padx=5)
        
        self.speed_var = tk.DoubleVar(value=1.0)
        for speed in [0.5, 1.0, 2.0, 5.0]:
            tk.Radiobutton(speed_frame, text=f"{speed}x",
                          variable=self.speed_var, value=speed).pack(side="left", padx=5)
        
        # Options
        options_frame = tk.LabelFrame(self.window, text="Options")
        options_frame.pack(fill="x", padx=20, pady=10)
        
        self.use_timing = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Use original timing",
                      variable=self.use_timing).pack(anchor="w")
        
        self.skip_mouse = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Skip mouse movements",
                      variable=self.skip_mouse).pack(anchor="w")
        
        self.dry_run = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Dry run (preview only)",
                      variable=self.dry_run).pack(anchor="w")
        
        # Control buttons
        controls = tk.Frame(self.window)
        controls.pack(pady=20)
        
        self.start_btn = tk.Button(controls, text="▶ Start",
                                  command=self.start_replay,
                                  bg="green", fg="white",
                                  font=("Arial", 12, "bold"))
        self.start_btn.pack(side="left", padx=5)
        
        self.pause_btn = tk.Button(controls, text="⏸ Pause",
                                  command=self.pause_replay,
                                  state="disabled")
        self.pause_btn.pack(side="left", padx=5)
        
        self.stop_btn = tk.Button(controls, text="⏹ Stop",
                                 command=self.stop_replay,
                                 bg="red", fg="white",
                                 state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        # Emergency stop info
        info_frame = tk.Frame(self.window, bg="lightgray")
        info_frame.pack(fill="x", side="bottom")
        
        tk.Label(info_frame, text="Press ESC at any time for emergency stop",
                font=("Arial", 10, "bold"), bg="lightgray").pack(pady=5)
    
    def start_replay(self):
        """Start the replay."""
        # Create options from UI settings
        options = ReplayOptions(
            playback_speed=self.speed_var.get(),
            use_original_timing=self.use_timing.get(),
            skip_mouse_moves=self.skip_mouse.get(),
            dry_run=self.dry_run.get(),
            confirm_start=not self.dry_run.get()
        )
        
        if self.engine.start_replay(options):
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
            self.stop_btn.config(state="normal")
    
    def pause_replay(self):
        """Pause/resume replay."""
        if self.engine.status == ReplayStatus.RUNNING:
            self.engine.pause_replay()
            self.pause_btn.config(text="▶ Resume")
        else:
            self.engine.resume_replay()
            self.pause_btn.config(text="⏸ Pause")
    
    def stop_replay(self):
        """Stop replay."""
        self.engine.stop_replay()
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="⏸ Pause")
        self.stop_btn.config(state="disabled")
        self.progress_label.config(text="Stopped")
    
    def update_progress(self, progress: float, action: Dict):
        """Update progress display."""
        self.progress_bar['value'] = progress * 100
        
        action_num = self.engine.current_action_index
        total = len(self.engine.actions)
        self.progress_label.config(text=f"Action {action_num}/{total}")
        
        # Show current action
        action_text = f"Current: {action['type']}"
        if 'data' in action:
            if 'x' in action['data'] and 'y' in action['data']:
                action_text += f" at ({action['data']['x']}, {action['data']['y']})"
            elif 'key' in action['data']:
                action_text += f" - {action['data']['key']}"
        
        self.action_label.config(text=action_text)
        self.window.update()
    
    def on_complete(self):
        """Handle replay completion."""
        self.progress_bar['value'] = 100
        self.progress_label.config(text="Completed!")
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")
        
        messagebox.showinfo("Replay Complete", 
                          "Action replay completed successfully!")
    
    def on_error(self, error_msg: str):
        """Handle replay error."""
        self.progress_label.config(text=f"Error: {error_msg}")
        messagebox.showerror("Replay Error", error_msg)


def launch_action_replay(recording_dir: Path):
    """Launch action replay control panel."""
    panel = ActionReplayControlPanel(recording_dir)
    return panel