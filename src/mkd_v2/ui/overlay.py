"""
Screen Overlay - Cross-platform visual recording indicators.

Provides red border and timer display during recording to give
visual feedback to users that recording is active.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

from ..platform.base import PlatformInterface, OverlayConfig

logger = logging.getLogger(__name__)


class OverlayState(Enum):
    """Overlay display states."""
    HIDDEN = "hidden"
    VISIBLE = "visible"
    BLINKING = "blinking"
    ERROR = "error"


@dataclass
class TimerConfig:
    """Timer display configuration."""
    show_timer: bool = True
    position: str = "top-right"  # top-left, top-right, bottom-left, bottom-right
    font_size: int = 16
    font_color: str = "#FFFFFF"
    background_color: str = "#000000"
    background_opacity: float = 0.7
    format: str = "mm:ss"  # mm:ss or hh:mm:ss


@dataclass  
class BorderConfig:
    """Border overlay configuration."""
    show_border: bool = True
    color: str = "#FF0000"
    width: int = 5
    opacity: float = 0.8
    style: str = "solid"  # solid, dashed, dotted
    blink_interval: float = 1.0  # seconds
    monitors: List[int] = None  # None means all monitors


class OverlayInterface(ABC):
    """Abstract interface for overlay implementations."""
    
    @abstractmethod
    def create_border_overlay(self, config: BorderConfig) -> Any:
        """Create border overlay."""
        pass
    
    @abstractmethod
    def create_timer_overlay(self, config: TimerConfig) -> Any:
        """Create timer overlay."""
        pass
    
    @abstractmethod
    def update_timer_text(self, overlay: Any, text: str) -> bool:
        """Update timer text."""
        pass
    
    @abstractmethod
    def show_overlay(self, overlay: Any) -> bool:
        """Show overlay."""
        pass
    
    @abstractmethod
    def hide_overlay(self, overlay: Any) -> bool:
        """Hide overlay."""
        pass
    
    @abstractmethod
    def destroy_overlay(self, overlay: Any) -> bool:
        """Destroy overlay."""
        pass


class ScreenOverlay:
    """
    Main screen overlay controller.
    
    Features:
    - Red border around screen during recording
    - Timer display showing elapsed recording time
    - Blinking indicators for attention
    - Multi-monitor support
    - Cross-platform compatibility
    """
    
    def __init__(self, platform: PlatformInterface):
        self.platform = platform
        self.state = OverlayState.HIDDEN
        
        # Overlay components
        self.border_overlays: List[Any] = []
        self.timer_overlay: Optional[Any] = None
        
        # Configuration
        self.border_config = BorderConfig()
        self.timer_config = TimerConfig()
        
        # Recording timing
        self.recording_start_time: Optional[datetime] = None
        self.last_update_time: Optional[datetime] = None
        
        # Threading for updates
        self._lock = threading.RLock()
        self._update_thread: Optional[threading.Thread] = None
        self._stop_updates = threading.Event()
        
        # Statistics
        self.stats = {
            'overlays_created': 0,
            'overlays_destroyed': 0,
            'timer_updates': 0,
            'blinks_performed': 0,
            'errors_encountered': 0
        }
        
        logger.info("ScreenOverlay initialized")
    
    def show_recording_indicators(self, 
                                border_config: Optional[BorderConfig] = None,
                                timer_config: Optional[TimerConfig] = None) -> bool:
        """
        Show recording visual indicators.
        
        Args:
            border_config: Border overlay configuration
            timer_config: Timer display configuration
            
        Returns:
            True if indicators shown successfully
        """
        with self._lock:
            if self.state != OverlayState.HIDDEN:
                logger.warning("Overlay indicators already visible")
                return False
            
            try:
                # Update configurations
                if border_config:
                    self.border_config = border_config
                if timer_config:
                    self.timer_config = timer_config
                
                # Get monitor information
                monitors = self.platform.get_monitor_info()
                if not monitors:
                    logger.error("No monitors detected")
                    self.state = OverlayState.ERROR
                    self.stats['errors_encountered'] += 1
                    return False
                
                # Create border overlays for each monitor
                if self.border_config.show_border:
                    self._create_border_overlays(monitors)
                
                # Create timer overlay
                if self.timer_config.show_timer:
                    self._create_timer_overlay()
                
                # Start recording timing
                self.recording_start_time = datetime.now()
                self.last_update_time = self.recording_start_time
                
                # Start update thread
                self._start_update_thread()
                
                self.state = OverlayState.VISIBLE
                logger.info("Recording indicators shown")
                return True
                
            except Exception as e:
                logger.error(f"Failed to show recording indicators: {e}")
                self.stats['errors_encountered'] += 1
                self.state = OverlayState.ERROR
                return False
    
    def hide_recording_indicators(self) -> bool:
        """
        Hide recording visual indicators.
        
        Returns:
            True if indicators hidden successfully
        """
        with self._lock:
            if self.state == OverlayState.HIDDEN:
                return True
            
            try:
                # Stop update thread
                self._stop_update_thread()
                
                # Hide and destroy border overlays
                for overlay in self.border_overlays:
                    try:
                        self.platform.destroy_overlay(overlay)
                        self.stats['overlays_destroyed'] += 1
                    except Exception as e:
                        logger.error(f"Error destroying border overlay: {e}")
                
                self.border_overlays.clear()
                
                # Hide and destroy timer overlay
                if self.timer_overlay:
                    try:
                        self.platform.destroy_overlay(self.timer_overlay)
                        self.stats['overlays_destroyed'] += 1
                    except Exception as e:
                        logger.error(f"Error destroying timer overlay: {e}")
                    
                    self.timer_overlay = None
                
                # Reset timing
                self.recording_start_time = None
                self.last_update_time = None
                
                self.state = OverlayState.HIDDEN
                logger.info("Recording indicators hidden")
                return True
                
            except Exception as e:
                logger.error(f"Failed to hide recording indicators: {e}")
                self.stats['errors_encountered'] += 1
                return False
    
    def update_timer_display(self) -> bool:
        """
        Update timer display with current elapsed time.
        
        Returns:
            True if timer updated successfully
        """
        if not self.timer_overlay or not self.recording_start_time:
            return False
        
        try:
            # Calculate elapsed time
            current_time = datetime.now()
            elapsed = current_time - self.recording_start_time
            
            # Format time string
            if self.timer_config.format == "hh:mm:ss":
                hours = int(elapsed.total_seconds() // 3600)
                minutes = int((elapsed.total_seconds() % 3600) // 60)
                seconds = int(elapsed.total_seconds() % 60)
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:  # mm:ss format
                minutes = int(elapsed.total_seconds() // 60)
                seconds = int(elapsed.total_seconds() % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"
            
            # Update timer overlay
            # Note: This would call platform-specific update method
            # For now, we'll simulate the update
            self.last_update_time = current_time
            self.stats['timer_updates'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update timer display: {e}")
            return False
    
    def _create_border_overlays(self, monitors: List[Dict[str, Any]]):
        """Create border overlays for monitors."""
        target_monitors = monitors
        
        # Filter monitors if specified
        if self.border_config.monitors:
            target_monitors = [
                m for i, m in enumerate(monitors) 
                if i in self.border_config.monitors
            ]
        
        for monitor in target_monitors:
            try:
                # Create overlay config for this monitor
                overlay_config = OverlayConfig(
                    color=self.border_config.color,
                    width=self.border_config.width,
                    opacity=self.border_config.opacity,
                    style=self.border_config.style
                )
                
                # Create platform-specific overlay
                overlay = self.platform.create_screen_overlay(overlay_config)
                if overlay:
                    self.border_overlays.append(overlay)
                    self.stats['overlays_created'] += 1
                
            except Exception as e:
                logger.error(f"Failed to create border overlay for monitor: {e}")
    
    def _create_timer_overlay(self):
        """Create timer display overlay."""
        try:
            # Timer overlays require different handling than border overlays
            # This would typically create a small window or use platform-specific
            # overlay APIs to display text
            
            # For now, we'll create a placeholder that would be implemented
            # by the platform-specific overlay system
            self.timer_overlay = "timer_overlay_placeholder"
            self.stats['overlays_created'] += 1
            
        except Exception as e:
            logger.error(f"Failed to create timer overlay: {e}")
    
    def _start_update_thread(self):
        """Start thread for updating overlays."""
        if self._update_thread and self._update_thread.is_alive():
            return
        
        self._stop_updates.clear()
        self._update_thread = threading.Thread(
            target=self._update_loop,
            daemon=True,
            name="OverlayUpdater"
        )
        self._update_thread.start()
    
    def _stop_update_thread(self):
        """Stop overlay update thread."""
        if self._update_thread:
            self._stop_updates.set()
            self._update_thread.join(timeout=1.0)
            self._update_thread = None
    
    def _update_loop(self):
        """Main update loop for overlays."""
        while not self._stop_updates.is_set():
            try:
                # Update timer display every second
                if self.timer_config.show_timer:
                    self.update_timer_display()
                
                # Handle blinking border
                if (self.border_config.show_border and 
                    self.border_config.style in ['blinking', 'dashed']):
                    self._handle_border_blinking()
                
                # Sleep until next update
                self._stop_updates.wait(1.0)
                
            except Exception as e:
                logger.error(f"Error in overlay update loop: {e}")
                self.stats['errors_encountered'] += 1
    
    def _handle_border_blinking(self):
        """Handle blinking border animation."""
        try:
            # Simple blinking logic - hide/show borders
            current_time = time.time()
            blink_cycle = current_time % (self.border_config.blink_interval * 2)
            
            should_show = blink_cycle < self.border_config.blink_interval
            
            for overlay in self.border_overlays:
                if should_show:
                    self.platform.update_overlay(overlay, 
                        OverlayConfig(opacity=self.border_config.opacity))
                else:
                    self.platform.update_overlay(overlay,
                        OverlayConfig(opacity=0.1))
            
            self.stats['blinks_performed'] += 1
            
        except Exception as e:
            logger.error(f"Error handling border blinking: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get overlay status information."""
        with self._lock:
            status = {
                'state': self.state.value,
                'recording_active': self.recording_start_time is not None,
                'border_overlays_count': len(self.border_overlays),
                'timer_overlay_active': self.timer_overlay is not None,
                'stats': self.stats.copy()
            }
            
            if self.recording_start_time:
                elapsed = datetime.now() - self.recording_start_time
                status['recording_duration'] = elapsed.total_seconds()
                status['recording_start_time'] = self.recording_start_time.isoformat()
            
            return status
    
    def cleanup(self):
        """Clean up overlay resources."""
        logger.info("Cleaning up ScreenOverlay")
        
        try:
            self.hide_recording_indicators()
        except Exception as e:
            logger.error(f"Error hiding indicators during cleanup: {e}")
        
        logger.info("ScreenOverlay cleanup complete")