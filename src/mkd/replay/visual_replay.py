"""
Visual Replay Engine - Review Mode Implementation

Provides playback of recorded sessions with visual annotations
for review, training, and debugging purposes.
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
import time
from dataclasses import dataclass
from enum import Enum

try:
    from PIL import Image, ImageDraw, ImageTk, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class AnnotationType(Enum):
    """Types of visual annotations."""
    MOUSE_CLICK = "mouse_click"
    MOUSE_MOVE = "mouse_move" 
    KEYBOARD_INPUT = "keyboard_input"
    WINDOW_FOCUS = "window_focus"
    SCROLL = "scroll"
    DRAG = "drag"


@dataclass
class Annotation:
    """Visual annotation for an action."""
    type: AnnotationType
    timestamp: float
    position: Tuple[int, int]
    data: Dict
    duration: float = 0.5  # How long to show annotation


class VisualReplayEngine:
    """Core engine for visual replay functionality."""
    
    def __init__(self):
        self.screenshots: List[Image.Image] = []
        self.actions: List[Dict] = []
        self.annotations: List[Annotation] = []
        self.current_frame = 0
        self.fps = 2  # Screenshots captured at 2 FPS
        self.playback_speed = 1.0
        self.is_playing = False
        
        # Visual settings
        self.show_mouse_trail = True
        self.show_click_ripples = True
        self.show_keyboard_overlay = True
        self.annotation_opacity = 180  # 0-255
        
    def load_recording(self, recording_dir: Path) -> bool:
        """Load a recording for visual replay."""
        # Load screenshots
        self.screenshots = []
        png_files = sorted(recording_dir.glob("frame_*.png"))
        
        for png_file in png_files:
            if HAS_PIL:
                img = Image.open(png_file)
                self.screenshots.append(img)
        
        # Load actions from .mkd file
        mkd_file = recording_dir / "recording.mkd"
        if mkd_file.exists():
            # In real implementation, would use msgpack
            # For now, using JSON for simplicity
            metadata_file = recording_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    self.actions = data.get('actions', [])
                    self._generate_annotations()
        
        return len(self.screenshots) > 0
    
    def _generate_annotations(self):
        """Generate visual annotations from actions."""
        self.annotations = []
        
        for action in self.actions:
            ann_type = None
            position = (0, 0)
            
            if action['type'] == 'mouse_click':
                ann_type = AnnotationType.MOUSE_CLICK
                position = (action['data']['x'], action['data']['y'])
            elif action['type'] == 'mouse_move':
                ann_type = AnnotationType.MOUSE_MOVE
                position = (action['data']['x'], action['data']['y'])
            elif action['type'] == 'key_press':
                ann_type = AnnotationType.KEYBOARD_INPUT
                # Position keyboard overlay at bottom center
                position = (960, 900)  # Assuming 1920x1080
            
            if ann_type:
                self.annotations.append(Annotation(
                    type=ann_type,
                    timestamp=action['timestamp'],
                    position=position,
                    data=action['data']
                ))
    
    def render_frame(self, frame_num: int) -> Image.Image:
        """Render a frame with annotations."""
        if not HAS_PIL or frame_num >= len(self.screenshots):
            return None
        
        # Get base screenshot
        frame = self.screenshots[frame_num].copy()
        
        # Calculate time for this frame
        frame_time = frame_num / self.fps
        
        # Draw annotations for this time
        draw = ImageDraw.Draw(frame, 'RGBA')
        
        for annotation in self.annotations:
            # Check if annotation should be visible at this time
            if (annotation.timestamp <= frame_time <= 
                annotation.timestamp + annotation.duration):
                self._draw_annotation(draw, annotation, frame)
        
        return frame
    
    def _draw_annotation(self, draw: ImageDraw.Draw, 
                         annotation: Annotation, frame: Image.Image):
        """Draw a specific annotation on the frame."""
        x, y = annotation.position
        
        if annotation.type == AnnotationType.MOUSE_CLICK:
            if self.show_click_ripples:
                # Draw ripple effect
                for radius in [10, 20, 30]:
                    alpha = int(self.annotation_opacity * (1 - radius/30))
                    color = (255, 0, 0, alpha)  # Red with transparency
                    draw.ellipse(
                        [x-radius, y-radius, x+radius, y+radius],
                        outline=color, width=3
                    )
                # Draw center dot
                draw.ellipse([x-5, y-5, x+5, y+5], 
                           fill=(255, 0, 0, self.annotation_opacity))
                
                # Draw click type label
                button = annotation.data.get('button', 'left')
                label = f"{button.upper()} CLICK"
                draw.text((x+15, y-25), label, 
                         fill=(255, 255, 255, 255),
                         stroke_width=2, stroke_fill=(0, 0, 0, 255))
        
        elif annotation.type == AnnotationType.MOUSE_MOVE:
            if self.show_mouse_trail:
                # Draw small dot for mouse position
                draw.ellipse([x-2, y-2, x+2, y+2],
                           fill=(0, 255, 0, self.annotation_opacity))
        
        elif annotation.type == AnnotationType.KEYBOARD_INPUT:
            if self.show_keyboard_overlay:
                # Draw keyboard input overlay
                key = annotation.data.get('key', '')
                text = f"Typed: {key}"
                
                # Draw background box
                text_bbox = draw.textbbox((x, y), text)
                padding = 10
                box_coords = [
                    text_bbox[0] - padding,
                    text_bbox[1] - padding,
                    text_bbox[2] + padding,
                    text_bbox[3] + padding
                ]
                draw.rectangle(box_coords, 
                             fill=(0, 0, 0, self.annotation_opacity))
                
                # Draw text
                draw.text((x, y), text,
                         fill=(255, 255, 255, 255))
    
    def get_frame_at_time(self, timestamp: float) -> int:
        """Get frame number for a given timestamp."""
        return int(timestamp * self.fps)
    
    def get_time_at_frame(self, frame_num: int) -> float:
        """Get timestamp for a given frame number."""
        return frame_num / self.fps


class VisualReplayWindow:
    """GUI window for visual replay."""
    
    def __init__(self, recording_dir: Path):
        self.engine = VisualReplayEngine()
        self.recording_dir = recording_dir
        
        # Create window
        self.window = tk.Toplevel()
        self.window.title("Visual Replay - Review Mode")
        self.window.geometry("1200x800")
        
        # Load recording
        if not self.engine.load_recording(recording_dir):
            tk.messagebox.showerror("Error", "Failed to load recording")
            self.window.destroy()
            return
        
        self.setup_ui()
        self.show_frame(0)
    
    def setup_ui(self):
        """Setup the replay interface."""
        # Main display area
        display_frame = tk.Frame(self.window, bg="black")
        display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Canvas for showing frames
        self.canvas = tk.Canvas(display_frame, bg="black")
        self.canvas.pack(fill="both", expand=True)
        
        # Control panel
        controls = tk.Frame(self.window)
        controls.pack(fill="x", padx=10, pady=5)
        
        # Playback controls
        self.play_btn = tk.Button(controls, text="▶ Play",
                                 command=self.toggle_play)
        self.play_btn.pack(side="left", padx=5)
        
        tk.Button(controls, text="⏹ Stop",
                 command=self.stop).pack(side="left", padx=5)
        
        tk.Button(controls, text="⏮ Previous",
                 command=self.previous_frame).pack(side="left", padx=5)
        
        tk.Button(controls, text="⏭ Next",
                 command=self.next_frame).pack(side="left", padx=5)
        
        # Timeline slider
        self.timeline = tk.Scale(controls, from_=0, 
                                to=len(self.engine.screenshots)-1,
                                orient="horizontal", length=400,
                                command=self.seek)
        self.timeline.pack(side="left", padx=20)
        
        # Speed control
        tk.Label(controls, text="Speed:").pack(side="left", padx=5)
        self.speed_var = tk.StringVar(value="1.0x")
        speed_menu = ttk.Combobox(controls, textvariable=self.speed_var,
                                 values=["0.5x", "1.0x", "2.0x", "5.0x"],
                                 width=8, state="readonly")
        speed_menu.pack(side="left")
        speed_menu.bind("<<ComboboxSelected>>", self.change_speed)
        
        # Frame info
        self.info_label = tk.Label(controls, text="Frame 0/0")
        self.info_label.pack(side="left", padx=20)
        
        # Annotation settings
        settings_frame = tk.LabelFrame(self.window, text="Display Settings")
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        self.show_clicks = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_frame, text="Show Click Indicators",
                      variable=self.show_clicks,
                      command=self.update_settings).pack(side="left", padx=10)
        
        self.show_mouse = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_frame, text="Show Mouse Trail",
                      variable=self.show_mouse,
                      command=self.update_settings).pack(side="left", padx=10)
        
        self.show_keyboard = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_frame, text="Show Keyboard Input",
                      variable=self.show_keyboard,
                      command=self.update_settings).pack(side="left", padx=10)
        
        # Action list
        action_frame = tk.LabelFrame(self.window, text="Action Timeline")
        action_frame.pack(fill="x", padx=10, pady=5)
        
        self.action_list = tk.Listbox(action_frame, height=5)
        self.action_list.pack(fill="x", padx=5, pady=5)
        self.populate_action_list()
    
    def populate_action_list(self):
        """Populate the action timeline list."""
        for i, action in enumerate(self.engine.actions):
            time_str = f"{action['timestamp']:.2f}s"
            action_str = f"{time_str}: {action['type']} - {action.get('data', {})}"
            self.action_list.insert("end", action_str)
    
    def show_frame(self, frame_num: int):
        """Display a specific frame with annotations."""
        if not HAS_PIL:
            return
        
        # Render frame with annotations
        frame = self.engine.render_frame(frame_num)
        if not frame:
            return
        
        # Resize to fit canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width > 1 and canvas_height > 1:
            frame.thumbnail((canvas_width, canvas_height), 
                          Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage and display
        self.current_image = ImageTk.PhotoImage(frame)
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width//2, canvas_height//2,
            image=self.current_image
        )
        
        # Update controls
        self.timeline.set(frame_num)
        self.info_label.config(
            text=f"Frame {frame_num+1}/{len(self.engine.screenshots)} | "
                 f"Time: {self.engine.get_time_at_frame(frame_num):.1f}s"
        )
        
        # Highlight current action in list
        current_time = self.engine.get_time_at_frame(frame_num)
        for i, action in enumerate(self.engine.actions):
            if action['timestamp'] <= current_time:
                self.action_list.selection_clear(0, "end")
                self.action_list.selection_set(i)
                self.action_list.see(i)
    
    def toggle_play(self):
        """Toggle play/pause."""
        if self.engine.is_playing:
            self.engine.is_playing = False
            self.play_btn.config(text="▶ Play")
        else:
            self.engine.is_playing = True
            self.play_btn.config(text="⏸ Pause")
            self.play()
    
    def play(self):
        """Play the replay."""
        if not self.engine.is_playing:
            return
        
        # Show current frame
        self.show_frame(self.engine.current_frame)
        
        # Advance to next frame
        if self.engine.current_frame < len(self.engine.screenshots) - 1:
            self.engine.current_frame += 1
            delay = int(500 / self.engine.playback_speed)  # 2 FPS base
            self.window.after(delay, self.play)
        else:
            self.stop()
    
    def stop(self):
        """Stop playback."""
        self.engine.is_playing = False
        self.engine.current_frame = 0
        self.play_btn.config(text="▶ Play")
        self.show_frame(0)
    
    def previous_frame(self):
        """Go to previous frame."""
        if self.engine.current_frame > 0:
            self.engine.current_frame -= 1
            self.show_frame(self.engine.current_frame)
    
    def next_frame(self):
        """Go to next frame."""
        if self.engine.current_frame < len(self.engine.screenshots) - 1:
            self.engine.current_frame += 1
            self.show_frame(self.engine.current_frame)
    
    def seek(self, frame_num):
        """Seek to specific frame."""
        self.engine.current_frame = int(frame_num)
        self.show_frame(self.engine.current_frame)
    
    def change_speed(self, event=None):
        """Change playback speed."""
        speed_str = self.speed_var.get()
        self.engine.playback_speed = float(speed_str[:-1])
    
    def update_settings(self):
        """Update display settings."""
        self.engine.show_click_ripples = self.show_clicks.get()
        self.engine.show_mouse_trail = self.show_mouse.get()
        self.engine.show_keyboard_overlay = self.show_keyboard.get()
        self.show_frame(self.engine.current_frame)


def launch_visual_replay(recording_dir: Path):
    """Launch visual replay for a recording."""
    window = VisualReplayWindow(recording_dir)
    return window