"""
Unified Replay Manager for MKD Automation.

Manages both Visual and Action replay modes with a unified interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from enum import Enum
from typing import Optional
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from mkd.replay.visual_replay import launch_visual_replay
from mkd.replay.action_replay import launch_action_replay


class ReplayMode(Enum):
    """Available replay modes."""
    VISUAL = "visual"
    ACTION = "action"


class ReplayManager:
    """Manages replay functionality for recorded sessions."""
    
    def __init__(self):
        self.recording_dir: Optional[Path] = None
        self.metadata: dict = {}
        
    def load_recording(self, recording_dir: Path) -> bool:
        """Load a recording for replay."""
        if not recording_dir.exists():
            return False
            
        self.recording_dir = recording_dir
        
        # Load metadata if available
        metadata_file = recording_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)
        
        # Check for required files
        has_mkd = (recording_dir / "recording.mkd").exists()
        has_screenshots = len(list(recording_dir.glob("frame_*.png"))) > 0
        
        return has_mkd or has_screenshots
    
    def launch_replay(self, mode: ReplayMode):
        """Launch replay in specified mode."""
        if not self.recording_dir:
            raise ValueError("No recording loaded")
        
        if mode == ReplayMode.VISUAL:
            return launch_visual_replay(self.recording_dir)
        elif mode == ReplayMode.ACTION:
            return launch_action_replay(self.recording_dir)
        else:
            raise ValueError(f"Unknown replay mode: {mode}")
    
    def get_recording_info(self) -> dict:
        """Get information about loaded recording."""
        if not self.recording_dir:
            return {}
        
        info = {
            "path": str(self.recording_dir),
            "name": self.recording_dir.name,
            "has_screenshots": len(list(self.recording_dir.glob("frame_*.png"))) > 0,
            "screenshot_count": len(list(self.recording_dir.glob("frame_*.png"))),
            "has_mkd": (self.recording_dir / "recording.mkd").exists(),
            "has_metadata": (self.recording_dir / "metadata.json").exists()
        }
        
        if self.metadata:
            info.update({
                "duration": self.metadata.get("duration", 0),
                "action_count": len(self.metadata.get("actions", [])),
                "platform": self.metadata.get("platform", "unknown")
            })
        
        return info


class ReplayModeSelector:
    """GUI for selecting replay mode."""
    
    def __init__(self, recording_dir: Optional[Path] = None):
        self.manager = ReplayManager()
        self.window = tk.Tk()
        self.window.title("MKD Replay Mode Selector")
        self.window.geometry("600x500")
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"600x500+{x}+{y}")
        
        self.setup_ui()
        
        # Load recording if provided
        if recording_dir:
            self.load_recording(recording_dir)
    
    def setup_ui(self):
        """Setup the selector interface."""
        # Header
        header = tk.Frame(self.window, bg="#2196F3", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="MKD Replay Manager",
                font=("Arial", 18, "bold"),
                bg="#2196F3", fg="white").pack(pady=15)
        
        # Recording info
        info_frame = tk.LabelFrame(self.window, text="Recording Information", padx=15, pady=10)
        info_frame.pack(fill="x", padx=20, pady=20)
        
        self.info_text = tk.Text(info_frame, height=4, width=60, state="disabled")
        self.info_text.pack()
        
        # Load button
        load_btn = tk.Button(self.window, text="📁 Load Recording",
                           command=self.browse_recording,
                           font=("Arial", 11))
        load_btn.pack(pady=10)
        
        # Mode selection
        mode_frame = tk.Frame(self.window)
        mode_frame.pack(pady=20)
        
        # Visual Replay card
        visual_card = tk.Frame(mode_frame, relief="raised", bd=2, padx=20, pady=20)
        visual_card.pack(side="left", padx=20)
        
        tk.Label(visual_card, text="👁️ VISUAL REPLAY",
                font=("Arial", 14, "bold")).pack(pady=5)
        
        tk.Label(visual_card, text="Review Mode",
                font=("Arial", 10), fg="gray").pack()
        
        tk.Label(visual_card, text="\n• Watch replay with annotations\n" +
                                  "• See mouse clicks & keyboard\n" +
                                  "• Frame-by-frame control\n" +
                                  "• Export to video\n" +
                                  "• Safe to use\n",
                justify="left").pack(pady=10)
        
        self.visual_btn = tk.Button(visual_card, text="▶ Start Visual Replay",
                                   command=lambda: self.start_replay(ReplayMode.VISUAL),
                                   bg="#4CAF50", fg="white",
                                   font=("Arial", 11, "bold"),
                                   state="disabled")
        self.visual_btn.pack(pady=5)
        
        # Action Replay card
        action_card = tk.Frame(mode_frame, relief="raised", bd=2, padx=20, pady=20)
        action_card.pack(side="left", padx=20)
        
        tk.Label(action_card, text="🤖 ACTION REPLAY",
                font=("Arial", 14, "bold")).pack(pady=5)
        
        tk.Label(action_card, text="Automation Mode",
                font=("Arial", 10), fg="gray").pack()
        
        tk.Label(action_card, text="\n• Execute recorded actions\n" +
                                  "• Reproduce exact clicks\n" +
                                  "• Adjustable speed\n" +
                                  "• Run automation\n" +
                                  "⚠️ Controls mouse/keyboard\n",
                justify="left").pack(pady=10)
        
        self.action_btn = tk.Button(action_card, text="▶ Start Action Replay",
                                   command=lambda: self.start_replay(ReplayMode.ACTION),
                                   bg="#FF9800", fg="white",
                                   font=("Arial", 11, "bold"),
                                   state="disabled")
        self.action_btn.pack(pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="No recording loaded")
        status_bar = tk.Label(self.window, textvariable=self.status_var,
                            bd=1, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")
    
    def browse_recording(self):
        """Browse for a recording directory."""
        initial_dir = Path("recordings") if Path("recordings").exists() else Path.home()
        
        dir_path = filedialog.askdirectory(
            title="Select Recording Directory",
            initialdir=initial_dir
        )
        
        if dir_path:
            self.load_recording(Path(dir_path))
    
    def load_recording(self, recording_dir: Path):
        """Load a recording."""
        if self.manager.load_recording(recording_dir):
            info = self.manager.get_recording_info()
            
            # Update info display
            self.info_text.config(state="normal")
            self.info_text.delete(1.0, "end")
            
            info_lines = [
                f"Recording: {info['name']}",
                f"Duration: {info.get('duration', 0):.1f} seconds",
                f"Actions: {info.get('action_count', 'Unknown')}",
                f"Screenshots: {info['screenshot_count']} frames"
            ]
            
            self.info_text.insert("end", "\n".join(info_lines))
            self.info_text.config(state="disabled")
            
            # Enable buttons based on available data
            if info['has_screenshots']:
                self.visual_btn.config(state="normal")
            else:
                self.visual_btn.config(state="disabled")
            
            if info.get('action_count', 0) > 0 or info['has_mkd']:
                self.action_btn.config(state="normal")
            else:
                self.action_btn.config(state="disabled")
            
            self.status_var.set(f"Loaded: {info['name']}")
        else:
            messagebox.showerror("Error", "Failed to load recording")
            self.status_var.set("Failed to load recording")
    
    def start_replay(self, mode: ReplayMode):
        """Start replay in selected mode."""
        try:
            if mode == ReplayMode.ACTION:
                # Show warning for action replay
                result = messagebox.askyesno(
                    "Action Replay Warning",
                    "Action Replay will control your mouse and keyboard.\n\n" +
                    "Make sure you:\n" +
                    "• Save any open work\n" +
                    "• Understand the recording content\n" +
                    "• Know how to stop (ESC key)\n\n" +
                    "Continue?",
                    icon="warning"
                )
                
                if not result:
                    return
            
            self.manager.launch_replay(mode)
            self.status_var.set(f"Started {mode.value} replay")
            
        except Exception as e:
            messagebox.showerror("Replay Error", str(e))
            self.status_var.set(f"Error: {e}")
    
    def run(self):
        """Run the selector."""
        self.window.mainloop()


def main():
    """Main entry point for replay manager."""
    import sys
    
    # Check if recording directory provided
    recording_dir = None
    if len(sys.argv) > 1:
        recording_dir = Path(sys.argv[1])
    
    # Launch selector
    selector = ReplayModeSelector(recording_dir)
    selector.run()


if __name__ == "__main__":
    main()