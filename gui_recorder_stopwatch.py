#!/usr/bin/env python
"""
GUI Recorder with Minimized Stopwatch Display

Features:
- Main UI minimizes to corner stopwatch during recording
- Stopwatch shows elapsed time with pause/stop controls
- Click stopwatch to pause/resume
- X button to stop recording
- Black font for all main UI buttons
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
from datetime import datetime
from pathlib import Path
import glob

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from pynput import mouse, keyboard
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False

try:
    from PIL import Image, ImageTk
    import PIL.ImageGrab as ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from mkd.core.session_manager import SessionManager
from mkd.core.config_manager import ConfigManager
from mkd.data.models import Action, AutomationScript
from mkd.data.script_storage import ScriptStorage
from mkd.platform.detector import PlatformDetector


class StopwatchWindow:
    """Minimized stopwatch display shown during recording."""
    
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.window = None
        self.is_paused = False
        self.start_time = 0
        self.pause_time = 0
        self.total_pause_duration = 0
        
    def show(self):
        """Create and show the stopwatch window."""
        self.window = tk.Toplevel()
        self.window.title("Recording")
        self.window.geometry("200x60")
        
        # Position in top-right corner
        self.window.geometry("+{}+20".format(self.window.winfo_screenwidth() - 220))
        
        # Make it stay on top
        self.window.attributes('-topmost', True)
        
        # Prevent resizing
        self.window.resizable(False, False)
        
        # Main frame
        main_frame = tk.Frame(self.window, bg="white", relief="raised", bd=2)
        main_frame.pack(fill="both", expand=True)
        
        # Timer display (clickable for pause/resume)
        self.timer_label = tk.Label(main_frame, text="00:00:00", 
                                   font=("Arial", 18, "bold"),
                                   bg="white", fg="red", cursor="hand2")
        self.timer_label.pack(side="left", padx=10)
        self.timer_label.bind("<Button-1>", self.toggle_pause)
        
        # Status label (shows RECORDING or PAUSED)
        self.status_label = tk.Label(main_frame, text="RECORDING",
                                    font=("Arial", 10),
                                    bg="white", fg="red")
        self.status_label.place(x=10, y=35)
        
        # Cross (X) button to stop
        close_btn = tk.Label(main_frame, text="✕", 
                           font=("Arial", 16, "bold"),
                           bg="white", fg="black", cursor="hand2")
        close_btn.pack(side="right", padx=10)
        close_btn.bind("<Button-1>", self.stop_recording)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.stop_recording)
        
        # Start timer
        self.start_time = time.time()
        self.is_paused = False
        self.update_timer()
        
    def update_timer(self):
        """Update the timer display."""
        if not self.window or not self.window.winfo_exists():
            return
            
        if not self.is_paused:
            elapsed = time.time() - self.start_time - self.total_pause_duration
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_str)
        
        # Schedule next update
        self.window.after(100, self.update_timer)
    
    def toggle_pause(self, event=None):
        """Toggle between pause and resume."""
        if self.is_paused:
            # Resume
            self.total_pause_duration += time.time() - self.pause_time
            self.is_paused = False
            self.status_label.config(text="RECORDING", fg="red")
            self.timer_label.config(fg="red")
            if self.parent_app:
                self.parent_app.resume_recording()
        else:
            # Pause
            self.pause_time = time.time()
            self.is_paused = True
            self.status_label.config(text="PAUSED", fg="orange")
            self.timer_label.config(fg="orange")
            if self.parent_app:
                self.parent_app.pause_recording()
    
    def stop_recording(self, event=None):
        """Stop recording and close stopwatch."""
        if self.parent_app:
            self.parent_app.stop_recording_from_stopwatch()
        self.close()
    
    def close(self):
        """Close the stopwatch window."""
        if self.window:
            self.window.destroy()
            self.window = None


class RedBoundaryFrame:
    """Creates a red frame around the screen boundary during recording."""
    
    def __init__(self):
        self.frames = []
        
    def show(self):
        """Show the red boundary frame."""
        # Get screen dimensions
        root = tk.Tk()
        root.withdraw()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        
        # Frame thickness
        thickness = 5
        
        # Create four frames for each edge
        positions = [
            (0, 0, screen_width, thickness),  # Top
            (0, screen_height - thickness, screen_width, thickness),  # Bottom
            (0, 0, thickness, screen_height),  # Left
            (screen_width - thickness, 0, thickness, screen_height)  # Right
        ]
        
        for x, y, width, height in positions:
            frame = tk.Toplevel()
            frame.geometry(f"{width}x{height}+{x}+{y}")
            frame.configure(bg='red')
            frame.overrideredirect(True)
            frame.attributes('-topmost', True)
            frame.attributes('-alpha', 0.7)
            self.frames.append(frame)
    
    def hide(self):
        """Hide the red boundary frame."""
        for frame in self.frames:
            frame.destroy()
        self.frames = []


class ScreenshotCapture:
    """Handles screenshot capture during recording."""
    
    def __init__(self, save_dir):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.capturing = False
        self.capture_thread = None
        self.screenshot_count = 0
        self.capture_interval = 0.5  # 2 FPS
        
    def start(self):
        """Start capturing screenshots."""
        self.capturing = True
        self.screenshot_count = 0
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
    def stop(self):
        """Stop capturing screenshots."""
        self.capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=1)
        return self.screenshot_count
    
    def pause(self):
        """Pause screenshot capture."""
        self.capturing = False
        
    def resume(self):
        """Resume screenshot capture."""
        self.capturing = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
    
    def _capture_loop(self):
        """Capture screenshots in a loop."""
        while self.capturing:
            try:
                if HAS_PIL:
                    screenshot = ImageGrab.grab()
                    filename = f"frame_{self.screenshot_count:04d}.png"
                    filepath = self.save_dir / filename
                    screenshot.save(filepath, "PNG")
                    self.screenshot_count += 1
            except Exception as e:
                print(f"Screenshot error: {e}")
            
            time.sleep(self.capture_interval)


class ReplayController:
    """Controls replay of recorded sessions with screenshots."""
    
    def __init__(self, parent):
        self.parent = parent
        self.replay_window = None
        self.current_frame = 0
        self.frames = []
        self.is_playing = False
        self.playback_speed = 1.0
        
    def load_recording(self, recording_dir):
        """Load a recording for replay."""
        recording_path = Path(recording_dir)
        
        # Load PNG frames
        png_files = sorted(recording_path.glob("frame_*.png"))
        self.frames = []
        
        for png_file in png_files:
            try:
                img = Image.open(png_file)
                # Resize for display
                img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                self.frames.append(ImageTk.PhotoImage(img))
            except Exception as e:
                print(f"Error loading frame {png_file}: {e}")
        
        self.current_frame = 0
        return len(self.frames) > 0
    
    def show_replay_window(self):
        """Show the replay window."""
        if not self.frames:
            return
            
        self.replay_window = tk.Toplevel()
        self.replay_window.title("Replay Recording")
        self.replay_window.geometry("850x700")
        
        # Display canvas
        self.canvas = tk.Canvas(self.replay_window, width=800, height=600, bg="black")
        self.canvas.pack(pady=10)
        
        # Control frame
        controls = tk.Frame(self.replay_window)
        controls.pack()
        
        # Play/Pause button
        self.play_btn = tk.Button(controls, text="▶ Play", command=self.toggle_play)
        self.play_btn.pack(side="left", padx=5)
        
        # Frame slider
        self.frame_slider = tk.Scale(controls, from_=0, to=len(self.frames)-1,
                                    orient="horizontal", length=300,
                                    command=self.seek_frame)
        self.frame_slider.pack(side="left", padx=10)
        
        # Speed control
        tk.Label(controls, text="Speed:").pack(side="left", padx=5)
        self.speed_var = tk.StringVar(value="1.0x")
        speed_menu = ttk.Combobox(controls, textvariable=self.speed_var,
                                 values=["0.5x", "1.0x", "1.5x", "2.0x"],
                                 width=6, state="readonly")
        speed_menu.pack(side="left")
        speed_menu.bind("<<ComboboxSelected>>", self.change_speed)
        
        # Frame counter
        self.frame_label = tk.Label(controls, text=f"Frame 0/{len(self.frames)}")
        self.frame_label.pack(side="left", padx=10)
        
        # Show first frame
        self.show_frame(0)
        
        # Handle window close
        self.replay_window.protocol("WM_DELETE_WINDOW", self.close_replay)
    
    def show_frame(self, frame_num):
        """Display a specific frame."""
        if 0 <= frame_num < len(self.frames):
            self.current_frame = frame_num
            self.canvas.delete("all")
            self.canvas.create_image(400, 300, image=self.frames[frame_num])
            self.frame_slider.set(frame_num)
            self.frame_label.config(text=f"Frame {frame_num+1}/{len(self.frames)}")
    
    def toggle_play(self):
        """Toggle play/pause."""
        if self.is_playing:
            self.is_playing = False
            self.play_btn.config(text="▶ Play")
        else:
            self.is_playing = True
            self.play_btn.config(text="⏸ Pause")
            self.play_frames()
    
    def play_frames(self):
        """Play frames in sequence."""
        if not self.is_playing or not self.replay_window:
            return
            
        self.show_frame(self.current_frame)
        
        if self.current_frame < len(self.frames) - 1:
            self.current_frame += 1
            delay = int(500 / self.playback_speed)  # 2 FPS base rate
            self.replay_window.after(delay, self.play_frames)
        else:
            # Reached end
            self.is_playing = False
            self.play_btn.config(text="▶ Play")
    
    def seek_frame(self, value):
        """Seek to a specific frame."""
        self.show_frame(int(value))
    
    def change_speed(self, event=None):
        """Change playback speed."""
        speed_str = self.speed_var.get()
        self.playback_speed = float(speed_str[:-1])
    
    def close_replay(self):
        """Close the replay window."""
        self.is_playing = False
        if self.replay_window:
            self.replay_window.destroy()
            self.replay_window = None


class GUIRecorderApp:
    """Main GUI application."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MKD Automation - Recorder with Replay")
        self.root.geometry("600x750")
        
        # Components
        self.session_manager = SessionManager()
        self.config_manager = ConfigManager()
        self.script_storage = ScriptStorage()
        self.detector = PlatformDetector()
        
        # Recording state
        self.is_recording = False
        self.is_paused = False
        self.recording_session = None
        self.start_time = None
        self.actions_recorded = 0
        self.current_recording_dir = None
        
        # Visual components
        self.red_frame = RedBoundaryFrame()
        self.stopwatch = StopwatchWindow(self)
        self.screenshot_capture = None
        self.replay_controller = ReplayController(self)
        
        # Input listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Settings
        self.capture_mouse = tk.BooleanVar(value=True)
        self.capture_keyboard = tk.BooleanVar(value=True)
        self.show_red_boundary = tk.BooleanVar(value=True)
        
        # Event display
        self.events_text = None
        self.event_count = 0
        
        # Setup UI
        self.setup_styles()
        self.setup_ui()
        self.check_dependencies()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Setup UI styles with black fonts."""
        style = ttk.Style()
        
        # All buttons with black font
        style.configure("Record.TButton", 
                       background="#4CAF50", 
                       foreground="black",
                       font=("Arial", 12, "bold"))
        
        style.configure("Stop.TButton",
                       background="#f44336",
                       foreground="black", 
                       font=("Arial", 12, "bold"))
        
        style.configure("Replay.TButton",
                       background="#2196F3",
                       foreground="black",
                       font=("Arial", 12, "bold"))
        
        style.configure("Pause.TButton",
                       background="#FF9800",
                       foreground="black",
                       font=("Arial", 12, "bold"))
    
    def setup_ui(self):
        """Setup the user interface."""
        # Title header
        title_frame = tk.Frame(self.root, bg="#1976D2", height=60)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="MKD Automation", 
                              fg="white", bg="#1976D2",
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=15)
        
        version_label = tk.Label(title_frame, text="v2.0 - Recorder with Stopwatch",
                                fg="#E3F2FD", bg="#1976D2",
                                font=("Arial", 10))
        version_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5)
        
        # Status display
        self.status_var = tk.StringVar(value="● Ready")
        self.status_label = tk.Label(self.root, textvariable=self.status_var,
                                    font=("Arial", 14), fg="green")
        self.status_label.pack(pady=10)
        
        # Control buttons
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=20)
        
        self.start_btn = ttk.Button(controls_frame, text="▶ Start Recording",
                                  style="Record.TButton",
                                  command=self.start_recording)
        self.start_btn.pack(side="left", padx=10)
        
        self.pause_btn = ttk.Button(controls_frame, text="⏸ Pause",
                                  style="Pause.TButton",
                                  command=self.pause_recording,
                                  state="disabled")
        self.pause_btn.pack(side="left", padx=10)
        
        self.stop_btn = ttk.Button(controls_frame, text="⏹ Stop Recording",
                                 style="Stop.TButton", 
                                 command=self.stop_recording,
                                 state="disabled")
        self.stop_btn.pack(side="left", padx=10)
        
        # Replay controls
        replay_frame = tk.Frame(self.root)
        replay_frame.pack(pady=10)
        
        ttk.Button(replay_frame, text="▶ Replay Last Recording",
                  style="Replay.TButton",
                  command=self.replay_last_recording).pack(side="left", padx=5)
        
        ttk.Button(replay_frame, text="📁 Load Recording",
                  command=self.load_recording).pack(side="left", padx=5)
        
        # Settings frame
        settings_frame = tk.LabelFrame(self.root, text="Recording Settings", padx=20, pady=10)
        settings_frame.pack(pady=20, padx=20, fill="x")
        
        tk.Checkbutton(settings_frame, text="Capture Mouse", 
                      variable=self.capture_mouse).pack(anchor="w")
        tk.Checkbutton(settings_frame, text="Capture Keyboard",
                      variable=self.capture_keyboard).pack(anchor="w")
        tk.Checkbutton(settings_frame, text="Show Red Boundary",
                      variable=self.show_red_boundary).pack(anchor="w")
        
        # Recent Events
        events_frame = tk.LabelFrame(self.root, text="Recent Events", padx=10, pady=10)
        events_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.events_text = scrolledtext.ScrolledText(events_frame, height=10, width=60)
        self.events_text.pack(fill="both", expand=True)
        
        # Statistics
        self.stats_text = tk.Text(self.root, height=5, width=60)
        self.stats_text.pack(pady=10, padx=20)
        self.update_stats()
    
    def check_dependencies(self):
        """Check if required dependencies are available."""
        issues = []
        if not HAS_PYNPUT:
            issues.append("pynput library not found")
        if not HAS_PIL:
            issues.append("PIL/Pillow library not found")
            
        if issues:
            self.add_event(f"Warning: {', '.join(issues)}")
    
    def add_event(self, event_text):
        """Add an event to the display."""
        if self.events_text:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.events_text.insert("end", f"[{timestamp}] {event_text}\n")
            self.events_text.see("end")
            self.event_count += 1
    
    def update_stats(self):
        """Update statistics display."""
        self.stats_text.delete(1.0, "end")
        
        duration = 0
        if self.is_recording and self.start_time:
            duration = time.time() - self.start_time
        
        stats = [
            f"Recording Duration: {duration:.1f} seconds",
            f"Actions Recorded: {self.actions_recorded}",
            f"Status: {'Recording' if self.is_recording else 'Stopped'}",
            f"Paused: {'Yes' if self.is_paused else 'No'}",
            f"Platform: {self.detector.get_platform()}"
        ]
        
        self.stats_text.insert("end", "\n".join(stats))
        
        if self.is_recording:
            self.root.after(100, self.update_stats)
    
    def start_recording(self):
        """Start recording and minimize to stopwatch."""
        if self.is_recording:
            return
        
        if not HAS_PYNPUT:
            self.add_event("Error: pynput library not available")
            return
        
        # Start recording session
        self.is_recording = True
        self.is_paused = False
        self.actions_recorded = 0
        self.start_time = time.time()
        
        # Create recording directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_recording_dir = Path("recordings") / f"recording_{timestamp}"
        self.current_recording_dir.mkdir(parents=True, exist_ok=True)
        
        # Start session
        self.recording_session = self.session_manager.start_recording()
        
        # Show red boundary
        if self.show_red_boundary.get():
            self.red_frame.show()
        
        # Start screenshot capture
        if HAS_PIL:
            self.screenshot_capture = ScreenshotCapture(self.current_recording_dir)
            self.screenshot_capture.start()
        
        # Start input listeners
        if self.capture_mouse.get():
            self.mouse_listener = mouse.Listener(
                on_move=self.on_mouse_move,
                on_click=self.on_mouse_click
            )
            self.mouse_listener.start()
        
        if self.capture_keyboard.get():
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_key_press
            )
            self.keyboard_listener.start()
        
        # Update UI
        self.status_var.set("● Recording")
        self.status_label.config(fg="red")
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")
        
        self.add_event("Recording started")
        
        # Minimize main window and show stopwatch
        self.root.iconify()  # Minimize main window
        self.stopwatch.show()
        
        self.update_stats()
    
    def pause_recording(self):
        """Pause recording."""
        if not self.is_recording or self.is_paused:
            return
        
        self.is_paused = True
        
        # Pause listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # Pause screenshot capture
        if self.screenshot_capture:
            self.screenshot_capture.pause()
        
        self.status_var.set("⏸ Paused")
        self.status_label.config(fg="orange")
        self.pause_btn.config(text="▶ Resume")
        
        self.add_event("Recording paused")
    
    def resume_recording(self):
        """Resume recording."""
        if not self.is_recording or not self.is_paused:
            return
        
        self.is_paused = False
        
        # Resume listeners
        if self.capture_mouse.get():
            self.mouse_listener = mouse.Listener(
                on_move=self.on_mouse_move,
                on_click=self.on_mouse_click
            )
            self.mouse_listener.start()
        
        if self.capture_keyboard.get():
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_key_press
            )
            self.keyboard_listener.start()
        
        # Resume screenshot capture
        if self.screenshot_capture:
            self.screenshot_capture.resume()
        
        self.status_var.set("● Recording")
        self.status_label.config(fg="red")
        self.pause_btn.config(text="⏸ Pause")
        
        self.add_event("Recording resumed")
    
    def stop_recording(self):
        """Stop recording from main UI."""
        self.stop_recording_internal()
    
    def stop_recording_from_stopwatch(self):
        """Stop recording from stopwatch window."""
        # Restore main window
        self.root.deiconify()
        self.stop_recording_internal()
    
    def stop_recording_internal(self):
        """Internal method to stop recording."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.is_paused = False
        
        # Stop listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        # Hide red frame
        self.red_frame.hide()
        
        # Stop screenshot capture
        screenshot_count = 0
        if self.screenshot_capture:
            screenshot_count = self.screenshot_capture.stop()
            self.screenshot_capture = None
        
        # Close stopwatch
        self.stopwatch.close()
        
        # Stop recording session
        duration = time.time() - self.start_time if self.start_time else 0
        completed_session = self.session_manager.stop_recording()
        
        # Save recording
        if completed_session:
            try:
                script = completed_session.to_script(
                    name=f"Recording {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    description=f"GUI recorded session with {self.actions_recorded} actions"
                )
                
                mkd_file = self.current_recording_dir / "recording.mkd"
                self.script_storage.save(script, str(mkd_file))
                self.add_event(f"Recording saved to {mkd_file}")
            except Exception as e:
                self.add_event(f"Error saving recording: {e}")
        
        self.add_event(f"Recording stopped - Duration: {duration:.1f}s, Actions: {self.actions_recorded}, Screenshots: {screenshot_count}")
        
        # Update UI
        self.status_var.set("● Ready")
        self.status_label.config(fg="green")
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="⏸ Pause")
        self.stop_btn.config(state="disabled")
        
        self.update_stats()
    
    def on_mouse_move(self, x, y):
        """Handle mouse move event."""
        if self.is_recording and not self.is_paused:
            action = Action("mouse_move", {"x": x, "y": y}, 
                          time.time() - self.start_time)
            self.session_manager.add_action(action)
            self.actions_recorded += 1
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click event."""
        if self.is_recording and not self.is_paused:
            event_type = "mouse_press" if pressed else "mouse_release"
            action = Action(event_type, 
                          {"x": x, "y": y, "button": str(button)},
                          time.time() - self.start_time)
            self.session_manager.add_action(action)
            self.actions_recorded += 1
            
            event_text = f"Mouse {'Press' if pressed else 'Release'}: {button} at ({x}, {y})"
            self.add_event(event_text)
    
    def on_key_press(self, key):
        """Handle keyboard press event."""
        if self.is_recording and not self.is_paused:
            try:
                key_name = key.char if hasattr(key, 'char') else str(key)
            except:
                key_name = str(key)
            
            action = Action("key_press", {"key": key_name},
                          time.time() - self.start_time)
            self.session_manager.add_action(action)
            self.actions_recorded += 1
            
            self.add_event(f"Keyboard: {key_name}")
    
    def replay_last_recording(self):
        """Replay the last recording."""
        if not self.current_recording_dir or not self.current_recording_dir.exists():
            self.add_event("No recording to replay")
            return
        
        if self.replay_controller.load_recording(self.current_recording_dir):
            self.replay_controller.show_replay_window()
        else:
            self.add_event("No screenshots to replay")
    
    def load_recording(self):
        """Load a recording from file."""
        recordings_dir = Path("recordings")
        if not recordings_dir.exists():
            self.add_event("No recordings directory found")
            return
        
        # Get list of recordings
        recording_dirs = sorted([d for d in recordings_dir.iterdir() if d.is_dir()],
                              reverse=True)
        
        if not recording_dirs:
            self.add_event("No recordings found")
            return
        
        # For simplicity, load the most recent one
        # In a full implementation, show a selection dialog
        selected_dir = recording_dirs[0]
        
        if self.replay_controller.load_recording(selected_dir):
            self.replay_controller.show_replay_window()
            self.add_event(f"Loaded recording from {selected_dir.name}")
        else:
            self.add_event("No screenshots in selected recording")
    
    def on_closing(self):
        """Handle window close event."""
        if self.is_recording:
            response = tk.messagebox.askyesno("Recording Active", 
                                             "Stop recording and quit?")
            if response:
                self.stop_recording_internal()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = GUIRecorderApp()
    app.run()


if __name__ == "__main__":
    main()