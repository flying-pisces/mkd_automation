#!/usr/bin/env python
"""
GUI Recorder with Replay Functionality

A standalone Python GUI for testing recording and replay functionality.

Features:
- Chrome extension-like interface
- Red frame boundary when recording
- Screenshot capture during recording
- Replay function with PNG sequence playback
- Integration with existing recording system
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

class RedBoundaryFrame:
    """Creates a red frame around the screen boundary during recording."""
    
    def __init__(self):
        self.windows = []
        self.is_showing = False
    
    def show(self):
        """Show red boundary frame."""
        if self.is_showing:
            return
        
        self.is_showing = True
        
        # Get screen dimensions
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        
        # Create 4 red frames for screen edges
        frame_thickness = 5
        
        # Top frame
        top = tk.Toplevel()
        top.title("Recording Active")
        top.geometry(f"{screen_width}x{frame_thickness}+0+0")
        top.configure(bg='red')
        top.attributes('-topmost', True)
        top.attributes('-alpha', 0.7)
        top.overrideredirect(True)
        self.windows.append(top)
        
        # Bottom frame
        bottom = tk.Toplevel()
        bottom.geometry(f"{screen_width}x{frame_thickness}+0+{screen_height-frame_thickness}")
        bottom.configure(bg='red')
        bottom.attributes('-topmost', True)
        bottom.attributes('-alpha', 0.7)
        bottom.overrideredirect(True)
        self.windows.append(bottom)
        
        # Left frame
        left = tk.Toplevel()
        left.geometry(f"{frame_thickness}x{screen_height}+0+0")
        left.configure(bg='red')
        left.attributes('-topmost', True)
        left.attributes('-alpha', 0.7)
        left.overrideredirect(True)
        self.windows.append(left)
        
        # Right frame
        right = tk.Toplevel()
        right.geometry(f"{frame_thickness}x{screen_height}+{screen_width-frame_thickness}+0")
        right.configure(bg='red')
        right.attributes('-topmost', True)
        right.attributes('-alpha', 0.7)
        right.overrideredirect(True)
        self.windows.append(right)
    
    def hide(self):
        """Hide red boundary frame."""
        self.is_showing = False
        for window in self.windows:
            try:
                window.destroy()
            except:
                pass
        self.windows.clear()

class ScreenshotCapture:
    """Handles screenshot capture during recording."""
    
    def __init__(self):
        self.capturing = False
        self.capture_thread = None
        self.screenshots_dir = None
        self.screenshot_count = 0
        self.capture_interval = 0.5  # 2 FPS
        
    def start_capture(self, output_dir):
        """Start screenshot capture."""
        if not HAS_PIL:
            print("PIL not available for screenshots")
            return False
        
        self.screenshots_dir = Path(output_dir)
        self.screenshots_dir.mkdir(exist_ok=True)
        self.screenshot_count = 0
        self.capturing = True
        
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        return True
    
    def stop_capture(self):
        """Stop screenshot capture."""
        self.capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        return self.screenshot_count
    
    def _capture_loop(self):
        """Screenshot capture loop."""
        while self.capturing:
            try:
                # Capture screenshot
                screenshot = ImageGrab.grab()
                
                # Save with sequential filename
                filename = f"frame_{self.screenshot_count:04d}.png"
                filepath = self.screenshots_dir / filename
                screenshot.save(filepath, "PNG")
                
                self.screenshot_count += 1
                
                # Wait for next capture
                time.sleep(self.capture_interval)
                
            except Exception as e:
                print(f"Screenshot capture error: {e}")
                break

class ReplayWindow:
    """Window for replaying recorded screenshots."""
    
    def __init__(self, parent, screenshots_dir):
        self.parent = parent
        self.screenshots_dir = Path(screenshots_dir)
        self.window = None
        self.canvas = None
        self.image_files = []
        self.current_frame = 0
        self.playing = False
        self.replay_thread = None
        self.playback_speed = 1.0
        
        self.load_screenshots()
        self.create_window()
    
    def load_screenshots(self):
        """Load screenshot files."""
        pattern = self.screenshots_dir / "frame_*.png"
        self.image_files = sorted(glob.glob(str(pattern)))
        print(f"Loaded {len(self.image_files)} screenshot frames")
    
    def create_window(self):
        """Create replay window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Replay - MKD Automation")
        self.window.geometry("900x700")
        
        # Control panel
        control_frame = tk.Frame(self.window)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Playback controls
        self.play_btn = tk.Button(control_frame, text="▶ Play", command=self.play_pause)
        self.play_btn.pack(side="left", padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹ Stop", command=self.stop_playback)
        self.stop_btn.pack(side="left", padx=5)
        
        tk.Label(control_frame, text="Speed:").pack(side="left", padx=(20,5))
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = tk.Scale(control_frame, from_=0.1, to=3.0, resolution=0.1, 
                              orient="horizontal", variable=self.speed_var, length=100)
        speed_scale.pack(side="left", padx=5)
        
        # Frame info
        self.frame_info = tk.Label(control_frame, text=f"Frame: 0 / {len(self.image_files)}")
        self.frame_info.pack(side="right", padx=10)
        
        # Progress bar
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self.window, variable=self.progress_var, 
                                          maximum=len(self.image_files)-1 if self.image_files else 1)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        
        # Canvas for image display
        canvas_frame = tk.Frame(self.window, bg="black")
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg="black")
        self.canvas.pack(fill="both", expand=True)
        
        # Load first frame if available
        if self.image_files:
            self.show_frame(0)
        else:
            self.canvas.create_text(450, 350, text="No screenshots found", 
                                   fill="white", font=("Arial", 16))
        
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
    
    def show_frame(self, frame_index):
        """Display a specific frame."""
        if not self.image_files or frame_index >= len(self.image_files):
            return
        
        try:
            # Load and resize image to fit canvas
            img = Image.open(self.image_files[frame_index])
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Calculate scaling to fit canvas while maintaining aspect ratio
            if canvas_width > 1 and canvas_height > 1:
                img_ratio = img.width / img.height
                canvas_ratio = canvas_width / canvas_height
                
                if img_ratio > canvas_ratio:
                    # Image is wider, scale by width
                    new_width = canvas_width
                    new_height = int(canvas_width / img_ratio)
                else:
                    # Image is taller, scale by height
                    new_height = canvas_height
                    new_width = int(canvas_height * img_ratio)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage and display
            self.photo = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width//2, canvas_height//2, 
                                   image=self.photo, anchor="center")
            
            # Update frame info
            self.current_frame = frame_index
            self.frame_info.config(text=f"Frame: {frame_index + 1} / {len(self.image_files)}")
            self.progress_var.set(frame_index)
            
        except Exception as e:
            print(f"Error showing frame {frame_index}: {e}")
    
    def play_pause(self):
        """Toggle play/pause."""
        if self.playing:
            self.playing = False
            self.play_btn.config(text="▶ Play")
        else:
            if not self.image_files:
                messagebox.showwarning("No Frames", "No screenshots to replay")
                return
            
            self.playing = True
            self.play_btn.config(text="⏸ Pause")
            self.playback_speed = self.speed_var.get()
            
            if not self.replay_thread or not self.replay_thread.is_alive():
                self.replay_thread = threading.Thread(target=self._playback_loop, daemon=True)
                self.replay_thread.start()
    
    def stop_playback(self):
        """Stop playback and return to first frame."""
        self.playing = False
        self.play_btn.config(text="▶ Play")
        self.current_frame = 0
        if self.image_files:
            self.show_frame(0)
    
    def _playback_loop(self):
        """Playback loop for replay."""
        while self.playing and self.current_frame < len(self.image_files):
            self.window.after(0, self.show_frame, self.current_frame)
            self.current_frame += 1
            
            # Calculate delay based on speed
            delay = (0.5 / self.playback_speed)  # Base 0.5s interval
            time.sleep(delay)
        
        # End of playback
        self.playing = False
        self.window.after(0, lambda: self.play_btn.config(text="▶ Play"))
    
    def close_window(self):
        """Close replay window."""
        self.playing = False
        if self.replay_thread:
            self.replay_thread.join(timeout=1)
        self.window.destroy()

class GUIRecorderWithReplay:
    """Main GUI application with recording and replay functionality."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MKD Automation - Recorder with Replay")
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        
        # Initialize components
        self.session_manager = SessionManager()
        self.config_manager = ConfigManager()
        self.script_storage = ScriptStorage()
        self.platform_detector = PlatformDetector()
        
        # UI components
        self.red_frame = RedBoundaryFrame()
        self.screenshot_capture = ScreenshotCapture()
        
        # Recording state
        self.recording = False
        self.paused = False
        self.start_time = None
        self.actions_recorded = 0
        self.current_recording_dir = None
        
        # Input listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Setup UI
        self.setup_ui()
        self.setup_styles()
        
        # Check dependencies
        self.check_dependencies()
    
    def check_dependencies(self):
        """Check for required dependencies."""
        issues = []
        
        if not HAS_PYNPUT:
            issues.append("pynput library not found (needed for input capture)")
        
        if not HAS_PIL:
            issues.append("Pillow library not found (needed for screenshots)")
        
        if issues:
            messagebox.showwarning(
                "Missing Dependencies",
                "Some features may not work:\n\n" + "\n".join(f"• {issue}" for issue in issues) +
                "\n\nInstall with:\npip install pynput pillow"
            )
    
    def setup_styles(self):
        """Setup UI styles."""
        style = ttk.Style()
        
        style.configure("Record.TButton", 
                       background="#4CAF50", 
                       foreground="red",
                       font=("Arial", 12, "bold"))
        
        style.configure("Stop.TButton",
                       background="#f44336",
                       foreground="white", 
                       font=("Arial", 12, "bold"))
        
        style.configure("Replay.TButton",
                       background="#2196F3",
                       foreground="white",
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
        
        version_label = tk.Label(title_frame, text="v2.0 - Recorder with Replay",
                                fg="#E3F2FD", bg="#1976D2",
                                font=("Arial", 10))
        version_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5)
        
        # Status section
        status_frame = tk.LabelFrame(self.root, text="Recording Status", 
                                   font=("Arial", 12, "bold"))
        status_frame.pack(fill="x", padx=20, pady=10)
        
        self.status_label = tk.Label(status_frame, text="● Ready", 
                                   fg="green", font=("Arial", 14, "bold"))
        self.status_label.pack(pady=10)
        
        # Main control buttons
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=20)
        
        self.start_btn = ttk.Button(controls_frame, text="▶ Start Recording",
                                  style="Record.TButton",
                                  command=self.start_recording)
        self.start_btn.pack(side="left", padx=10)
        
        self.stop_btn = ttk.Button(controls_frame, text="⏹ Stop Recording",
                                 style="Stop.TButton", 
                                 command=self.stop_recording,
                                 state="disabled")
        self.stop_btn.pack(side="left", padx=10)
        
        # Replay controls
        replay_frame = tk.Frame(self.root)
        replay_frame.pack(pady=10)
        
        self.replay_btn = ttk.Button(replay_frame, text="🎬 Replay Last Recording",
                                   style="Replay.TButton",
                                   command=self.replay_last_recording)
        self.replay_btn.pack(side="left", padx=10)
        
        self.open_replay_btn = ttk.Button(replay_frame, text="📂 Open Recording",
                                        style="Replay.TButton",
                                        command=self.open_recording_for_replay)
        self.open_replay_btn.pack(side="left", padx=10)
        
        # Settings section
        settings_frame = tk.LabelFrame(self.root, text="Recording Settings",
                                     font=("Arial", 12, "bold"))
        settings_frame.pack(fill="x", padx=20, pady=10)
        
        # Capture options
        self.capture_mouse = tk.BooleanVar(value=True)
        self.capture_keyboard = tk.BooleanVar(value=True)
        self.capture_screenshots = tk.BooleanVar(value=True)
        self.show_boundary = tk.BooleanVar(value=True)
        
        tk.Checkbutton(settings_frame, text="Capture Mouse", 
                      variable=self.capture_mouse).pack(anchor="w", padx=10)
        tk.Checkbutton(settings_frame, text="Capture Keyboard",
                      variable=self.capture_keyboard).pack(anchor="w", padx=10)
        tk.Checkbutton(settings_frame, text="Capture Screenshots (for Replay)",
                      variable=self.capture_screenshots).pack(anchor="w", padx=10)
        tk.Checkbutton(settings_frame, text="Show Red Boundary",
                      variable=self.show_boundary).pack(anchor="w", padx=10)
        
        # Statistics section
        stats_frame = tk.LabelFrame(self.root, text="Statistics",
                                  font=("Arial", 12, "bold"))
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=8, font=("Consolas", 10))
        self.stats_text.pack(fill="both", padx=10, pady=10)
        
        # Recent event display (integrated)
        events_frame = tk.LabelFrame(self.root, text="Recent Events",
                                   font=("Arial", 12, "bold"))
        events_frame.pack(fill="x", padx=20, pady=10)
        
        self.events_text = tk.Text(events_frame, height=6, font=("Consolas", 9))
        self.events_text.pack(fill="both", padx=10, pady=10)
        
        # Platform info
        info_frame = tk.LabelFrame(self.root, text="System Information",
                                 font=("Arial", 12, "bold"))
        info_frame.pack(fill="x", padx=20, pady=10)
        
        platform_info = f"Platform: {self.platform_detector.get_platform()}"
        pynput_status = "Available" if HAS_PYNPUT else "Not Installed"
        pil_status = "Available" if HAS_PIL else "Not Installed"
        
        tk.Label(info_frame, text=platform_info).pack(anchor="w", padx=10, pady=2)
        tk.Label(info_frame, text=f"pynput Library: {pynput_status}").pack(anchor="w", padx=10, pady=2)
        tk.Label(info_frame, text=f"Pillow Library: {pil_status}").pack(anchor="w", padx=10, pady=2)
        
        self.update_stats()
    
    def add_event(self, event_text):
        """Add event to recent events display."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Add to events text widget
        self.events_text.insert(tk.END, f"[{timestamp}] {event_text}\n")
        self.events_text.see(tk.END)
        
        # Keep only last 20 lines
        lines = self.events_text.get("1.0", tk.END).split('\n')
        if len(lines) > 20:
            self.events_text.delete("1.0", f"{len(lines)-20}.0")
    
    def get_current_timestamp(self):
        """Get timestamp relative to recording start."""
        if not self.start_time:
            return 0.0
        return time.time() - self.start_time
    
    def on_mouse_move(self, x, y):
        """Handle mouse move events."""
        if not self.recording or self.paused or not self.capture_mouse.get():
            return
        
        timestamp = self.get_current_timestamp()
        action = Action(
            type="mouse_move",
            data={"x": x, "y": y},
            timestamp=timestamp
        )
        self.session_manager.add_action(action)
        self.actions_recorded += 1
        
        # Show in events (throttled)
        if self.actions_recorded % 10 == 0:
            self.add_event(f"Mouse Move: ({x}, {y})")
        
        self.update_stats()
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        if not self.recording or self.paused or not self.capture_mouse.get():
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
        
        status = "Press" if pressed else "Release"
        self.add_event(f"Mouse {status}: {button_name} at ({x}, {y})")
        
        self.update_stats()
    
    def on_key_press(self, key):
        """Handle key press events."""
        if not self.recording or self.paused or not self.capture_keyboard.get():
            return
        
        timestamp = self.get_current_timestamp()
        
        try:
            # Get key name
            if hasattr(key, 'char') and key.char:
                key_name = key.char.upper()
            elif hasattr(key, 'name'):
                key_name = key.name.upper()
            else:
                key_name = str(key)
            
            action = Action(
                type="key_down",
                data={"key": key_name},
                timestamp=timestamp
            )
            self.session_manager.add_action(action)
            self.actions_recorded += 1
            
            self.add_event(f"Keyboard: {key_name}")
            self.update_stats()
            
        except Exception:
            pass  # Ignore key handling errors
    
    def start_recording(self):
        """Start recording with visual feedback."""
        if not HAS_PYNPUT:
            messagebox.showerror("Error", "pynput library not available")
            return
        
        if self.recording:
            return
        
        self.recording = True
        self.paused = False
        self.start_time = time.time()
        self.actions_recorded = 0
        
        # Create recording directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_recording_dir = Path("recordings") / f"recording_{timestamp}"
        self.current_recording_dir.mkdir(parents=True, exist_ok=True)
        
        # Clear events display
        self.events_text.delete("1.0", tk.END)
        
        # Update UI
        self.status_label.config(text="● Recording", fg="red")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        # Start session
        self.session_manager.start_recording()
        
        # Show visual feedback
        if self.show_boundary.get():
            self.red_frame.show()
        
        # Start screenshot capture if enabled
        if self.capture_screenshots.get():
            screenshots_dir = self.current_recording_dir / "screenshots"
            self.screenshot_capture.start_capture(screenshots_dir)
        
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
        
        self.add_event("Recording started")
    
    def stop_recording(self):
        """Stop recording and save data."""
        if not self.recording:
            return
        
        self.recording = False
        self.paused = False
        
        # Stop input listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # Stop screenshot capture
        screenshot_count = 0
        if self.capture_screenshots.get():
            screenshot_count = self.screenshot_capture.stop_capture()
        
        # Stop session
        completed_session = self.session_manager.stop_recording()
        
        # Hide visual feedback
        self.red_frame.hide()
        
        # Update UI
        self.status_label.config(text="● Stopped", fg="orange")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        duration = time.time() - self.start_time if self.start_time else 0
        
        # Save recording data
        if completed_session and len(completed_session.actions) > 0:
            # Create script from session
            script = AutomationScript(
                name="GUI Recording",
                description=f"Recorded at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                created_at=datetime.now(),
                actions=list(completed_session.actions)
            )
            
            # Save to .mkd file
            mkd_file = self.current_recording_dir / "recording.mkd"
            try:
                self.script_storage.save(script, str(mkd_file))
                self.add_event(f"Recording saved to {mkd_file}")
            except Exception as e:
                self.add_event(f"Error saving recording: {e}")
        
        self.add_event(f"Recording stopped - Duration: {duration:.1f}s, Actions: {self.actions_recorded}, Screenshots: {screenshot_count}")
        
        self.update_stats()
    
    def replay_last_recording(self):
        """Replay the most recent recording."""
        recordings_dir = Path("recordings")
        if not recordings_dir.exists():
            messagebox.showwarning("No Recordings", "No recordings directory found")
            return
        
        # Find most recent recording directory
        recording_dirs = [d for d in recordings_dir.iterdir() if d.is_dir()]
        if not recording_dirs:
            messagebox.showwarning("No Recordings", "No recordings found")
            return
        
        latest_dir = max(recording_dirs, key=lambda d: d.stat().st_ctime)
        screenshots_dir = latest_dir / "screenshots"
        
        if not screenshots_dir.exists():
            messagebox.showwarning("No Screenshots", 
                                 f"No screenshots found in {latest_dir.name}\n" +
                                 "Enable 'Capture Screenshots' during recording")
            return
        
        # Open replay window
        ReplayWindow(self.root, screenshots_dir)
    
    def open_recording_for_replay(self):
        """Open file dialog to select recording for replay."""
        recordings_dir = Path("recordings")
        if recordings_dir.exists():
            initial_dir = str(recordings_dir)
        else:
            initial_dir = "."
        
        selected_dir = filedialog.askdirectory(
            title="Select Recording Directory",
            initialdir=initial_dir
        )
        
        if not selected_dir:
            return
        
        screenshots_dir = Path(selected_dir) / "screenshots"
        if not screenshots_dir.exists():
            messagebox.showwarning("No Screenshots", 
                                 f"No screenshots found in selected directory\n" +
                                 "Make sure 'Capture Screenshots' was enabled during recording")
            return
        
        # Open replay window
        ReplayWindow(self.root, screenshots_dir)
    
    def update_stats(self):
        """Update statistics display."""
        if self.recording and self.start_time:
            duration = time.time() - self.start_time
            rate = self.actions_recorded / duration if duration > 0 else 0
        else:
            duration = 0
            rate = 0
        
        screenshot_info = ""
        if self.capture_screenshots.get() and hasattr(self.screenshot_capture, 'screenshot_count'):
            screenshot_info = f"Screenshots: {self.screenshot_capture.screenshot_count}\n"
        
        stats_text = f"""Recording Duration: {duration:.1f} seconds
Actions Recorded: {self.actions_recorded}
Capture Rate: {rate:.1f} actions/sec
{screenshot_info}Status: {'Recording' if self.recording else 'Stopped'}

Settings:
  Mouse Capture: {'On' if self.capture_mouse.get() else 'Off'}
  Keyboard Capture: {'On' if self.capture_keyboard.get() else 'Off'}
  Screenshot Capture: {'On' if self.capture_screenshots.get() else 'Off'}
  Red Boundary: {'On' if self.show_boundary.get() else 'Off'}

Current Recording Directory:
{str(self.current_recording_dir) if self.current_recording_dir else 'None'}"""
        
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert("1.0", stats_text)
        
        # Schedule next update if recording
        if self.recording:
            self.root.after(1000, self.update_stats)
    
    def run(self):
        """Start the GUI application."""
        def on_closing():
            if self.recording:
                if messagebox.askokcancel("Recording Active", "Stop recording and quit?"):
                    self.stop_recording()
                    self.root.destroy()
            else:
                self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Start main loop
        self.root.mainloop()

def main():
    """Main entry point."""
    try:
        app = GUIRecorderWithReplay()
        app.run()
    except KeyboardInterrupt:
        print("Application interrupted")
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()