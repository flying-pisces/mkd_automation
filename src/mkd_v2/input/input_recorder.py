"""
Input Recorder

Records user input actions for automation playback.
"""

import asyncio
import logging
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from .input_action import InputAction, ActionType

logger = logging.getLogger(__name__)


@dataclass
class RecordingConfig:
    """Configuration for input recording"""
    record_mouse: bool = True
    record_keyboard: bool = True
    record_timing: bool = True
    min_action_interval: float = 0.05  # Minimum time between actions
    max_recording_duration: float = 300.0  # 5 minutes max
    ignore_modifiers: List[str] = None
    
    def __post_init__(self):
        if self.ignore_modifiers is None:
            self.ignore_modifiers = []


class InputRecorder:
    """Records user input actions"""
    
    def __init__(self, config: Optional[RecordingConfig] = None):
        self.config = config or RecordingConfig()
        self.is_recording = False
        self.recorded_actions: List[InputAction] = []
        self.start_time: Optional[float] = None
        self.last_action_time: Optional[float] = None
        
        logger.info("InputRecorder initialized")
    
    async def start_recording(self) -> None:
        """Start recording user input"""
        if self.is_recording:
            logger.warning("Recording already in progress")
            return
        
        self.is_recording = True
        self.recorded_actions.clear()
        self.start_time = time.time()
        self.last_action_time = self.start_time
        
        logger.info("Started input recording")
        
        # In a real implementation, this would set up platform-specific
        # input capturing (e.g., Windows hooks, macOS event taps, Linux X11)
        # For testing, we simulate minimal recording
    
    async def stop_recording(self) -> List[InputAction]:
        """Stop recording and return captured actions"""
        if not self.is_recording:
            logger.warning("No recording in progress")
            return []
        
        self.is_recording = False
        duration = time.time() - self.start_time if self.start_time else 0
        
        logger.info(f"Stopped input recording - captured {len(self.recorded_actions)} actions in {duration:.2f}s")
        
        return self.recorded_actions.copy()
    
    async def pause_recording(self) -> None:
        """Pause recording temporarily"""
        if self.is_recording:
            self.is_recording = False
            logger.info("Recording paused")
    
    async def resume_recording(self) -> None:
        """Resume recording"""
        if not self.is_recording:
            self.is_recording = True
            logger.info("Recording resumed")
    
    def get_recorded_actions(self) -> List[InputAction]:
        """Get currently recorded actions without stopping recording"""
        return self.recorded_actions.copy()
    
    def add_action(self, action: InputAction) -> None:
        """Add an action to the recording (for testing/simulation)"""
        if not self.is_recording:
            return
        
        current_time = time.time()
        
        # Check minimum interval
        if self.last_action_time:
            interval = current_time - self.last_action_time
            if interval < self.config.min_action_interval:
                return
        
        self.recorded_actions.append(action)
        self.last_action_time = current_time
        
        logger.debug(f"Recorded action: {action.action_type.value}")
    
    def clear_recording(self) -> None:
        """Clear all recorded actions"""
        self.recorded_actions.clear()
        logger.info("Recording cleared")
    
    def get_recording_stats(self) -> Dict[str, Any]:
        """Get recording statistics"""
        if not self.start_time:
            return {}
        
        current_time = time.time()
        duration = current_time - self.start_time if self.is_recording else 0
        
        action_types = {}
        for action in self.recorded_actions:
            action_type = action.action_type.value
            action_types[action_type] = action_types.get(action_type, 0) + 1
        
        return {
            "is_recording": self.is_recording,
            "duration": duration,
            "total_actions": len(self.recorded_actions),
            "actions_per_second": len(self.recorded_actions) / duration if duration > 0 else 0,
            "action_types": action_types,
            "start_time": self.start_time
        }