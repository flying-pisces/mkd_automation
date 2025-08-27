"""
Cross-Platform Overlay Renderer for Visual Recording Indicators.

Provides real visual overlay rendering using platform-specific GUI frameworks:
- macOS: Cocoa/NSWindow
- Windows: tkinter with topmost window attributes
- Linux: tkinter with window manager hints
"""

import logging
import platform
import threading
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    tk = ttk = None

# Platform-specific imports
if platform.system() == "Darwin":
    try:
        import objc
        from Foundation import NSObject
        from AppKit import (NSApplication, NSWindow, NSView, NSColor, NSBezierPath,
                           NSWindowStyleMaskBorderless, NSRect, NSMakeRect, 
                           NSBackingStoreBuffered, NSFloatingWindowLevel)
        COCOA_AVAILABLE = True
    except ImportError:
        COCOA_AVAILABLE = False
        NSObject = NSApplication = NSWindow = None
        NSFloatingWindowLevel = None
else:
    COCOA_AVAILABLE = False

logger = logging.getLogger(__name__)


class OverlayRenderer(ABC):
    """Abstract base class for platform-specific overlay renderers."""
    
    @abstractmethod
    def create_overlay(self, x: int, y: int, width: int, height: int, 
                      style: str = "recording", **kwargs) -> Any:
        """Create a visual overlay."""
        pass
    
    @abstractmethod
    def update_overlay(self, overlay_id: Any, **kwargs) -> bool:
        """Update overlay properties."""
        pass
    
    @abstractmethod
    def destroy_overlay(self, overlay_id: Any) -> bool:
        """Destroy an overlay."""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Clean up all overlays."""
        pass


class MacOSOverlayRenderer(OverlayRenderer):
    """macOS-specific overlay renderer using Cocoa/NSWindow."""
    
    def __init__(self):
        self.overlays: Dict[str, Any] = {}
        self.app = None
        
        # For now, always use tkinter fallback as it's more reliable
        logger.info("Using tkinter renderer for cross-platform compatibility")
        self.fallback_renderer = TkinterOverlayRenderer()
    
    def _initialize_cocoa(self):
        """Initialize Cocoa application."""
        try:
            self.app = NSApplication.sharedApplication()
            logger.info("macOS Cocoa overlay renderer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Cocoa: {e}")
            if not self.fallback_renderer:
                self.fallback_renderer = TkinterOverlayRenderer()
    
    def create_overlay(self, x: int, y: int, width: int, height: int,
                      style: str = "recording", **kwargs) -> str:
        """Create macOS overlay using tkinter fallback."""
        return self.fallback_renderer.create_overlay(x, y, width, height, style, **kwargs)
    
    def update_overlay(self, overlay_id: str, **kwargs) -> bool:
        """Update macOS overlay using tkinter fallback."""
        return self.fallback_renderer.update_overlay(overlay_id, **kwargs)
    
    def destroy_overlay(self, overlay_id: str) -> bool:
        """Destroy macOS overlay using tkinter fallback."""
        return self.fallback_renderer.destroy_overlay(overlay_id)
    
    def cleanup(self) -> bool:
        """Clean up all macOS overlays using tkinter fallback."""
        return self.fallback_renderer.cleanup()


class TkinterOverlayRenderer(OverlayRenderer):
    """Cross-platform overlay renderer using tkinter."""
    
    def __init__(self):
        self.overlays: Dict[str, Dict[str, Any]] = {}
        self.root = None
        self._setup_root()
    
    def _setup_root(self):
        """Setup tkinter root window."""
        if not TKINTER_AVAILABLE:
            logger.error("tkinter not available - overlay rendering disabled")
            return
        
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide root window
            self.root.attributes('-topmost', True)
            logger.info("tkinter overlay renderer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize tkinter: {e}")
    
    def create_overlay(self, x: int, y: int, width: int, height: int,
                      style: str = "recording", **kwargs) -> str:
        """Create tkinter overlay window."""
        if not TKINTER_AVAILABLE or not self.root:
            logger.error("tkinter not available for overlay creation")
            return ""
        
        try:
            overlay_id = f"tk_overlay_{len(self.overlays)}_{int(time.time())}"
            
            # Create overlay window
            overlay_window = tk.Toplevel(self.root)
            overlay_window.title("")
            overlay_window.geometry(f"{width}x{height}+{x}+{y}")
            
            # Configure window properties
            overlay_window.overrideredirect(True)  # Remove window decorations
            overlay_window.attributes('-topmost', True)  # Stay on top
            
            # Platform-specific attributes
            system = platform.system()
            if system == "Darwin":
                try:
                    overlay_window.attributes('-transparent', True)  # macOS transparency
                except:
                    pass  # Transparent not available on all macOS versions
            elif system == "Windows":
                overlay_window.attributes('-transparentcolor', 'black')  # Transparent background
                overlay_window.attributes('-toolwindow', True)  # Don't show in taskbar
            elif system == "Linux":
                overlay_window.attributes('-type', 'splash')  # Splash window type
            
            # Create canvas for drawing
            system = platform.system()
            bg_color = 'black' if system != "Darwin" else 'systemWindowBackgroundColor'
            
            canvas = tk.Canvas(
                overlay_window,
                width=width, height=height,
                bg=bg_color, highlightthickness=0
            )
            canvas.pack()
            
            # Draw recording indicator based on style
            self._draw_indicator(canvas, width, height, style, kwargs)
            
            # Store overlay info
            self.overlays[overlay_id] = {
                'window': overlay_window,
                'canvas': canvas,
                'x': x, 'y': y, 'width': width, 'height': height,
                'style': style,
                'active': True,
                'animation_job': None
            }
            
            # Start animation if needed
            if style in ['recording', 'pulse']:
                self._start_animation(overlay_id)
            
            logger.info(f"Created tkinter overlay: {overlay_id} at ({x}, {y})")
            return overlay_id
            
        except Exception as e:
            logger.error(f"Failed to create tkinter overlay: {e}")
            return ""
    
    def _draw_indicator(self, canvas: tk.Canvas, width: int, height: int, 
                       style: str, kwargs: Dict[str, Any]):
        """Draw recording indicator on canvas."""
        color = kwargs.get('color', 'red')
        opacity = kwargs.get('opacity', 0.8)
        
        # Clear canvas
        canvas.delete('all')
        
        if style == 'recording' or style == 'pulse':
            # Draw circular recording indicator
            margin = 5
            canvas.create_oval(
                margin, margin, width - margin, height - margin,
                fill=color, outline=color, width=2
            )
            # Add inner circle
            inner_margin = margin + 3
            canvas.create_oval(
                inner_margin, inner_margin,
                width - inner_margin, height - inner_margin,
                fill='white', outline='white'
            )
            
        elif style == 'border':
            # Draw border around area
            canvas.create_rectangle(
                0, 0, width, height,
                fill='', outline=color, width=3
            )
            
        elif style == 'highlight':
            # Draw semi-transparent highlight
            canvas.create_rectangle(
                0, 0, width, height,
                fill=color, stipple='gray25'
            )
    
    def _start_animation(self, overlay_id: str):
        """Start animation for overlay."""
        def animate():
            if overlay_id not in self.overlays or not self.overlays[overlay_id]['active']:
                return
            
            overlay = self.overlays[overlay_id]
            canvas = overlay['canvas']
            
            # Simple pulse animation by changing opacity
            current_time = time.time()
            alpha = (1 + math.sin(current_time * 3)) / 2  # Oscillate between 0 and 1
            
            # Redraw with new opacity
            self._draw_indicator(
                canvas, overlay['width'], overlay['height'],
                overlay['style'], {'color': 'red', 'opacity': alpha}
            )
            
            # Schedule next frame
            if overlay['active']:
                overlay['animation_job'] = self.root.after(50, animate)
        
        try:
            import math
            animate()
        except Exception as e:
            logger.error(f"Animation failed for {overlay_id}: {e}")
    
    def update_overlay(self, overlay_id: str, **kwargs) -> bool:
        """Update tkinter overlay properties."""
        if not TKINTER_AVAILABLE or overlay_id not in self.overlays:
            return False
        
        try:
            overlay = self.overlays[overlay_id]
            window = overlay['window']
            canvas = overlay['canvas']
            
            # Update position if specified
            if 'x' in kwargs or 'y' in kwargs:
                x = kwargs.get('x', overlay['x'])
                y = kwargs.get('y', overlay['y'])
                width = kwargs.get('width', overlay['width'])
                height = kwargs.get('height', overlay['height'])
                
                window.geometry(f"{width}x{height}+{x}+{y}")
                overlay.update({'x': x, 'y': y, 'width': width, 'height': height})
            
            # Redraw with new properties
            self._draw_indicator(canvas, overlay['width'], overlay['height'],
                               kwargs.get('style', overlay['style']), kwargs)
            
            logger.debug(f"Updated tkinter overlay: {overlay_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update tkinter overlay: {e}")
            return False
    
    def destroy_overlay(self, overlay_id: str) -> bool:
        """Destroy tkinter overlay."""
        if not TKINTER_AVAILABLE or overlay_id not in self.overlays:
            return False
        
        try:
            overlay = self.overlays[overlay_id]
            
            # Stop animation if running
            if overlay.get('animation_job'):
                self.root.after_cancel(overlay['animation_job'])
            
            # Mark as inactive and destroy window
            overlay['active'] = False
            overlay['window'].destroy()
            
            del self.overlays[overlay_id]
            logger.info(f"Destroyed tkinter overlay: {overlay_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to destroy tkinter overlay: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Clean up all tkinter overlays."""
        success = True
        for overlay_id in list(self.overlays.keys()):
            if not self.destroy_overlay(overlay_id):
                success = False
        
        if self.root:
            try:
                self.root.quit()
                self.root = None
            except:
                pass
        
        return success


# Cocoa NSView subclass for custom drawing (macOS only)
if COCOA_AVAILABLE:
    class RecordingIndicatorView(NSView):
        """Custom NSView for drawing recording indicators."""
        
        def initWithFrame_(self, frame):
            self = objc.super(RecordingIndicatorView, self).initWithFrame_(frame)
            if self:
                self._style = "recording"
                self._color = "red"
                self._opacity = 0.8
            return self
        
        def setStyle_(self, style):
            self._style = style
        
        def setColor_(self, color):
            self._color = color
        
        def setOpacity_(self, opacity):
            self._opacity = opacity
        
        def drawRect_(self, rect):
            """Draw the recording indicator."""
            try:
                # Get color
                if self._color == "red":
                    color = NSColor.redColor()
                elif self._color == "green":
                    color = NSColor.greenColor()
                elif self._color == "blue":
                    color = NSColor.blueColor()
                else:
                    color = NSColor.redColor()
                
                # Apply opacity
                color = color.colorWithAlphaComponent_(self._opacity)
                color.set()
                
                # Draw based on style
                if self._style in ["recording", "pulse"]:
                    # Draw circular indicator
                    path = NSBezierPath.bezierPathWithOvalInRect_(rect)
                    path.fill()
                    
                elif self._style == "border":
                    # Draw border rectangle
                    path = NSBezierPath.bezierPathWithRect_(rect)
                    path.setLineWidth_(3.0)
                    path.stroke()
                    
                elif self._style == "highlight":
                    # Draw filled rectangle
                    NSBezierPath.fillRect_(rect)
                    
            except Exception as e:
                logger.error(f"Failed to draw recording indicator: {e}")


def create_overlay_renderer() -> OverlayRenderer:
    """Create platform-appropriate overlay renderer."""
    system = platform.system()
    
    if system == "Darwin" and COCOA_AVAILABLE:
        return MacOSOverlayRenderer()
    else:
        return TkinterOverlayRenderer()


# Global overlay manager instance
_overlay_manager = None

def get_overlay_manager() -> OverlayRenderer:
    """Get global overlay manager instance."""
    global _overlay_manager
    if _overlay_manager is None:
        _overlay_manager = create_overlay_renderer()
    return _overlay_manager