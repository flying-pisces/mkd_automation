#!/usr/bin/env python
"""
GUI Recorder Test Application

A standalone Python GUI that mimics Chrome extension interface for testing
recording functionality with visual feedback.

Features:
- Chrome extension-like interface
- Red frame boundary when recording
- Real-time event display dialog
- Full keyboard and mouse capture
- Integration with existing recording system
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from pynput import mouse, keyboard
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False

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

class EventDisplayDialog:
    """Real-time event display dialog for testing."""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.text_widget = None
        self.event_count = 0
        
    def show(self):
        """Show event display dialog."""
        if self.window:
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Live Event Monitor")
        self.window.geometry("400x300+50+50")
        self.window.attributes('-topmost', True)
        
        # Event counter label
        self.counter_label = tk.Label(self.window, text="Events Captured: 0", 
                                     font=("Arial", 12, "bold"))
        self.counter_label.pack(pady=5)
        
        # Text area for events
        self.text_widget = scrolledtext.ScrolledText(
            self.window, 
            width=50, 
            height=15,
            font=("Consolas", 9)
        )
        self.text_widget.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Clear button
        clear_btn = tk.Button(self.window, text="Clear Events", 
                             command=self.clear_events)
        clear_btn.pack(pady=5)
        
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
    
    def hide(self):
        """Hide event display dialog."""
        if self.window:
            self.window.destroy()
            self.window = None
            self.text_widget = None
            self.event_count = 0
    
    def add_event(self, event_text):
        """Add event to display."""
        if not self.text_widget:
            return
        
        self.event_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Update counter
        self.counter_label.config(text=f"Events Captured: {self.event_count}")
        
        # Add event to text widget
        self.text_widget.insert(tk.END, f"[{timestamp}] {event_text}\n")
        self.text_widget.see(tk.END)
        
        # Limit text length (keep last 100 lines)
        lines = self.text_widget.get("1.0", tk.END).split('\n')
        if len(lines) > 100:
            self.text_widget.delete("1.0", f"{len(lines)-100}.0")
    
    def clear_events(self):
        """Clear all events."""
        if self.text_widget:
            self.text_widget.delete("1.0", tk.END)
            self.event_count = 0
            self.counter_label.config(text="Events Captured: 0")

class GUIRecorderTest:
    """Main GUI application for testing recording functionality."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MKD Automation - GUI Recorder Test")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # Initialize components
        self.session_manager = SessionManager()
        self.config_manager = ConfigManager()
        self.script_storage = ScriptStorage()
        self.platform_detector = PlatformDetector()
        
        # UI components
        self.red_frame = RedBoundaryFrame()
        self.event_dialog = EventDisplayDialog(self.root)
        
        # Recording state
        self.recording = False
        self.paused = False
        self.start_time = None
        self.actions_recorded = 0
        
        # Input listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Setup UI
        self.setup_ui()
        self.setup_styles()
        
        # Check pynput availability
        if not HAS_PYNPUT:
            messagebox.showwarning(
                "Missing Dependency",
                "pynput library not found. Please install with:\npip install pynput"
            )
    
    def setup_styles(self):
        """Setup UI styles similar to Chrome extension."""
        style = ttk.Style()
        
        # Configure button styles
        style.configure("Record.TButton", 
                       background="#4CAF50", 
                       foreground="white",
                       font=("Arial", 12, "bold"))
        
        style.configure("Stop.TButton",
                       background="#f44336",
                       foreground="white", 
                       font=("Arial", 12, "bold"))
        
        style.configure("Pause.TButton",
                       background="#FF9800",
                       foreground="white",
                       font=("Arial", 10))
    
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
        
        version_label = tk.Label(title_frame, text="v2.0 - GUI Test Mode",
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
        
        self.pause_btn = ttk.Button(controls_frame, text="⏸ Pause",
                                  style="Pause.TButton",
                                  command=self.toggle_pause,
                                  state="disabled")
        self.pause_btn.pack(side="left", padx=10)
        
        # Settings section
        settings_frame = tk.LabelFrame(self.root, text="Recording Settings",
                                     font=("Arial", 12, "bold"))
        settings_frame.pack(fill="x", padx=20, pady=10)
        
        # Capture options
        self.capture_mouse = tk.BooleanVar(value=True)
        self.capture_keyboard = tk.BooleanVar(value=True)
        self.show_boundary = tk.BooleanVar(value=True)
        self.show_events = tk.BooleanVar(value=True)
        
        tk.Checkbutton(settings_frame, text="Capture Mouse", 
                      variable=self.capture_mouse).pack(anchor="w", padx=10)
        tk.Checkbutton(settings_frame, text="Capture Keyboard",
                      variable=self.capture_keyboard).pack(anchor="w", padx=10)
        tk.Checkbutton(settings_frame, text="Show Red Boundary",
                      variable=self.show_boundary).pack(anchor="w", padx=10)
        tk.Checkbutton(settings_frame, text="Show Live Events",
                      variable=self.show_events).pack(anchor="w", padx=10)
        
        # Statistics section
        stats_frame = tk.LabelFrame(self.root, text="Statistics",
                                  font=("Arial", 12, "bold"))
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=6, font=("Consolas", 10))
        self.stats_text.pack(fill="both", padx=10, pady=10)
        
        # Platform info
        info_frame = tk.LabelFrame(self.root, text="System Information",
                                 font=("Arial", 12, "bold"))
        info_frame.pack(fill="x", padx=20, pady=10)
        
        platform_info = f"Platform: {self.platform_detector.get_platform()}"
        pynput_status = "Available" if HAS_PYNPUT else "Not Installed"
        
        tk.Label(info_frame, text=platform_info).pack(anchor="w", padx=10, pady=2)
        tk.Label(info_frame, text=f"pynput Library: {pynput_status}").pack(anchor="w", padx=10, pady=2)
        
        # Test controls
        test_frame = tk.LabelFrame(self.root, text="Testing Controls",
                                 font=("Arial", 12, "bold"))
        test_frame.pack(fill="x", padx=20, pady=10)
        
        test_controls = tk.Frame(test_frame)
        test_controls.pack(pady=10)
        
        tk.Button(test_controls, text="Show Event Monitor",
                 command=self.show_event_monitor).pack(side="left", padx=5)
        
        tk.Button(test_controls, text="Save Test Recording",
                 command=self.save_recording).pack(side="left", padx=5)
        
        tk.Button(test_controls, text="View Recordings",
                 command=self.view_recordings).pack(side="left", padx=5)
        
        self.update_stats()
    
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
        
        # Show in event monitor (throttled)
        if self.actions_recorded % 5 == 0 and self.show_events.get():
            self.event_dialog.add_event(f"Mouse Move: ({x}, {y})")
        
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
        
        # Show in event monitor
        if self.show_events.get():
            status = "Press" if pressed else "Release"
            self.event_dialog.add_event(f"Mouse {status}: {button_name} at ({x}, {y})")
        
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
            
            # Show in event monitor
            if self.show_events.get():
                self.event_dialog.add_event(f"Keyboard: {key_name}")
            
            self.update_stats()
            
        except Exception:
            pass  # Ignore key handling errors
    
    def on_key_release(self, key):
        """Handle key release events."""
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
                type="key_up", 
                data={"key": key_name},
                timestamp=timestamp
            )
            self.session_manager.add_action(action)
            self.actions_recorded += 1
            
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
        
        # Update UI
        self.status_label.config(text="● Recording", fg="red")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.pause_btn.config(state="normal")
        
        # Start session
        self.session_manager.start_recording()
        
        # Show visual feedback
        if self.show_boundary.get():
            self.red_frame.show()
        
        if self.show_events.get():
            self.event_dialog.show()
        
        # Start input listeners
        if self.capture_mouse.get():
            self.mouse_listener = mouse.Listener(
                on_move=self.on_mouse_move,
                on_click=self.on_mouse_click
            )
            self.mouse_listener.start()
        
        if self.capture_keyboard.get():
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            )
            self.keyboard_listener.start()
        
        messagebox.showinfo("Recording Started", 
                           "Recording is now active!\n\n" +
                           "• Red frame shows recording boundary\n" +
                           "• Event monitor shows live captures\n" +
                           "• Click Stop when finished")
    
    def stop_recording(self):
        """Stop recording and hide visual feedback."""
        if not self.recording:
            return
        
        self.recording = False
        self.paused = False
        
        # Stop input listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # Stop session
        self.session_manager.stop_recording()
        
        # Hide visual feedback
        self.red_frame.hide()
        
        # Update UI
        self.status_label.config(text="● Stopped", fg="orange")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.pause_btn.config(state="disabled")
        
        duration = time.time() - self.start_time if self.start_time else 0
        
        messagebox.showinfo("Recording Stopped", 
                           f"Recording completed!\n\n" +
                           f"Duration: {duration:.1f} seconds\n" +
                           f"Actions captured: {self.actions_recorded}\n\n" +
                           "Use 'Save Test Recording' to save the data.")
        
        self.update_stats()
    
    def toggle_pause(self):
        """Toggle pause/resume recording."""
        if not self.recording:
            return
        
        self.paused = not self.paused
        
        if self.paused:
            self.status_label.config(text="⏸ Paused", fg="orange")
            self.pause_btn.config(text="▶ Resume")
        else:
            self.status_label.config(text="● Recording", fg="red") 
            self.pause_btn.config(text="⏸ Pause")
    
    def show_event_monitor(self):
        """Show/hide event monitor dialog."""
        if self.event_dialog.window:
            self.event_dialog.hide()
        else:
            self.event_dialog.show()
    
    def save_recording(self):
        """Save the current recording session."""
        current_session = self.session_manager.get_current_session()
        if not current_session or len(current_session.actions) == 0:
            messagebox.showwarning("No Data", "No recorded actions to save")
            return
        
        # Create script from session
        script = AutomationScript(
            name="GUI Test Recording",
            description=f"Recorded via GUI at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            created_at=datetime.now(),
            actions=list(current_session.actions)
        )
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gui_test_recording_{timestamp}.mkd"
        os.makedirs("recordings", exist_ok=True)
        filepath = os.path.join("recordings", filename)
        
        try:
            self.script_storage.save(script, filepath)
            messagebox.showinfo("Saved", f"Recording saved to:\n{filepath}\n\n" +
                               f"Actions: {len(script.actions)}\n" +
                               f"Duration: {script.actions[-1].timestamp:.1f}s")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save recording:\n{str(e)}")
    
    def view_recordings(self):
        """Show list of saved recordings."""
        recordings_dir = Path("recordings")
        if not recordings_dir.exists():
            messagebox.showinfo("No Recordings", "No recordings directory found")
            return
        
        mkd_files = list(recordings_dir.glob("*.mkd"))
        if not mkd_files:
            messagebox.showinfo("No Recordings", "No .mkd files found in recordings directory")
            return
        
        # Create dialog to show recordings
        dialog = tk.Toplevel(self.root)
        dialog.title("Saved Recordings")
        dialog.geometry("500x300")
        
        listbox = tk.Listbox(dialog, font=("Consolas", 10))
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        for mkd_file in sorted(mkd_files, key=os.path.getctime, reverse=True):
            size = mkd_file.stat().st_size
            modified = datetime.fromtimestamp(mkd_file.stat().st_mtime)
            listbox.insert(tk.END, f"{mkd_file.name} ({size} bytes) - {modified.strftime('%Y-%m-%d %H:%M')}")
    
    def update_stats(self):
        """Update statistics display."""
        if self.recording and self.start_time:
            duration = time.time() - self.start_time
            rate = self.actions_recorded / duration if duration > 0 else 0
        else:
            duration = 0
            rate = 0
        
        stats_text = f"""Recording Duration: {duration:.1f} seconds
Actions Recorded: {self.actions_recorded}
Capture Rate: {rate:.1f} actions/sec
Status: {'Recording' if self.recording else 'Stopped'}
Paused: {'Yes' if self.paused else 'No'}

Settings:
  Mouse Capture: {'On' if self.capture_mouse.get() else 'Off'}
  Keyboard Capture: {'On' if self.capture_keyboard.get() else 'Off'}
  Red Boundary: {'On' if self.show_boundary.get() else 'Off'}
  Event Monitor: {'On' if self.show_events.get() else 'Off'}"""
        
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert("1.0", stats_text)
        
        # Schedule next update if recording
        if self.recording:
            self.root.after(1000, self.update_stats)
    
    def run(self):
        """Start the GUI application."""
        # Handle window close
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
        app = GUIRecorderTest()
        app.run()
    except KeyboardInterrupt:
        print("Application interrupted")
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()