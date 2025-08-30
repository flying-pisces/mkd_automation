"""
Recording engine for MKD Automation.
Manages the capture of user input events and coordinates recording operations.
"""
import time
import threading
from typing import Optional, Dict, Any, List, Callable
from queue import Queue, Empty
import datetime

from mkd.data.models import Action
from mkd.core.constants import (
    ACTION_TYPE_MOUSE_MOVE, ACTION_TYPE_MOUSE_CLICK, ACTION_TYPE_KEYBOARD,
    DEFAULT_SAMPLE_RATE
)


class RecordingEngine:
    """Main engine for recording user input events"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the recording engine.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.sample_rate = self.config.get('sample_rate', DEFAULT_SAMPLE_RATE)
        self.capture_mouse = self.config.get('capture_mouse', True)
        self.capture_keyboard = self.config.get('capture_keyboard', True)
        
        # Recording state
        self.is_recording = False
        self._recording_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._start_time: Optional[float] = None
        
        # Event handling
        self._event_queue: Queue = Queue()
        self._event_handlers: List[Callable[[Action], None]] = []
        self._recorded_actions: List[Action] = []
        
        # Statistics
        self._stats = {
            'actions_recorded': 0,
            'mouse_events': 0,
            'keyboard_events': 0,
            'recording_duration': 0.0
        }
    
    def add_event_handler(self, handler: Callable[[Action], None]) -> None:
        """
        Add an event handler to be called when actions are recorded.
        
        Args:
            handler: Function to call with each recorded action
        """
        self._event_handlers.append(handler)
    
    def remove_event_handler(self, handler: Callable[[Action], None]) -> bool:
        """
        Remove an event handler.
        
        Args:
            handler: Handler function to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        try:
            self._event_handlers.remove(handler)
            return True
        except ValueError:
            return False
    
    def start_recording(self) -> bool:
        """
        Start recording user input events.
        
        Returns:
            True if recording started successfully, False otherwise
        """
        if self.is_recording:
            return False
        
        # Reset state
        self._stop_event.clear()
        self._recorded_actions.clear()
        self._start_time = time.time()
        self._stats = {
            'actions_recorded': 0,
            'mouse_events': 0,
            'keyboard_events': 0,
            'recording_duration': 0.0
        }
        
        # Start recording thread
        self._recording_thread = threading.Thread(
            target=self._recording_worker,
            daemon=True
        )
        self._recording_thread.start()
        
        self.is_recording = True
        return True
    
    def stop_recording(self) -> List[Action]:
        """
        Stop recording and return all recorded actions.
        
        Returns:
            List of recorded actions
        """
        if not self.is_recording:
            return []
        
        # Signal stop and wait for thread
        self._stop_event.set()
        if self._recording_thread and self._recording_thread.is_alive():
            self._recording_thread.join(timeout=5.0)
        
        self.is_recording = False
        
        # Update stats
        if self._start_time:
            self._stats['recording_duration'] = time.time() - self._start_time
        
        return self._recorded_actions.copy()
    
    def pause_recording(self) -> bool:
        """
        Pause recording (placeholder for future implementation).
        
        Returns:
            True if paused successfully, False otherwise
        """
        # For now, just stop recording
        # Future implementations could implement true pause/resume
        return not self.is_recording
    
    def resume_recording(self) -> bool:
        """
        Resume recording (placeholder for future implementation).
        
        Returns:
            True if resumed successfully, False otherwise
        """
        # For now, just check if we can start recording
        return not self.is_recording
    
    def _recording_worker(self) -> None:
        """Worker thread that handles the recording loop"""
        sample_interval = 1.0 / self.sample_rate if self.sample_rate > 0 else 0.016
        
        try:
            # Simulate recording by generating some test events periodically
            # In a real implementation, this would hook into system input events
            while not self._stop_event.is_set():
                
                # Process any queued events
                self._process_event_queue()
                
                # Simulate mouse movement (for testing)
                if self.capture_mouse and self._should_record_mouse():
                    current_time = time.time() - (self._start_time or 0)
                    action = Action(
                        type=ACTION_TYPE_MOUSE_MOVE,
                        data={"x": 100, "y": 100},  # Mock position
                        timestamp=current_time
                    )
                    self._record_action(action)
                
                # Wait for next sample
                self._stop_event.wait(sample_interval)
                
        except Exception as e:
            print(f"Error in recording worker: {e}")
    
    def _should_record_mouse(self) -> bool:
        """Determine if mouse events should be recorded (placeholder logic)"""
        # In real implementation, this would check if mouse actually moved
        # For now, just record occasionally to avoid spam
        return len(self._recorded_actions) < 3
    
    def _process_event_queue(self) -> None:
        """Process any events in the queue"""
        try:
            while True:
                action = self._event_queue.get_nowait()
                self._record_action(action)
        except Empty:
            pass
    
    def _record_action(self, action: Action) -> None:
        """
        Record an action and notify handlers.
        
        Args:
            action: The action to record
        """
        # Add to recorded actions
        self._recorded_actions.append(action)
        
        # Update statistics
        self._stats['actions_recorded'] += 1
        if action.type.startswith('mouse'):
            self._stats['mouse_events'] += 1
        elif action.type.startswith('keyboard'):
            self._stats['keyboard_events'] += 1
        
        # Notify handlers
        for handler in self._event_handlers:
            try:
                handler(action)
            except Exception as e:
                print(f"Error in action handler: {e}")
    
    def inject_action(self, action: Action) -> None:
        """
        Manually inject an action into the recording.
        
        Args:
            action: Action to inject
        """
        if self.is_recording:
            self._event_queue.put(action)
        else:
            self._record_action(action)
    
    def get_recorded_actions(self) -> List[Action]:
        """Get all currently recorded actions"""
        return self._recorded_actions.copy()
    
    def get_action_count(self) -> int:
        """Get the number of recorded actions"""
        return len(self._recorded_actions)
    
    def get_recording_duration(self) -> float:
        """Get the current recording duration in seconds"""
        if self.is_recording and self._start_time:
            return time.time() - self._start_time
        return self._stats['recording_duration']
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get recording statistics"""
        current_stats = self._stats.copy()
        current_stats['is_recording'] = self.is_recording
        current_stats['current_duration'] = self.get_recording_duration()
        return current_stats
    
    def clear_recorded_actions(self) -> None:
        """Clear all recorded actions"""
        self._recorded_actions.clear()
        self._stats['actions_recorded'] = 0
        self._stats['mouse_events'] = 0
        self._stats['keyboard_events'] = 0
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Update recording configuration.
        
        Args:
            config: New configuration values
        """
        self.config.update(config)
        self.sample_rate = self.config.get('sample_rate', DEFAULT_SAMPLE_RATE)
        self.capture_mouse = self.config.get('capture_mouse', True)
        self.capture_keyboard = self.config.get('capture_keyboard', True)
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return {
            'sample_rate': self.sample_rate,
            'capture_mouse': self.capture_mouse,
            'capture_keyboard': self.capture_keyboard,
            **self.config
        }
    
    def is_healthy(self) -> bool:
        """Check if the recording engine is in a healthy state"""
        # Check if recording thread is alive when it should be
        if self.is_recording:
            return (self._recording_thread is not None and 
                   self._recording_thread.is_alive())
        return True
    
    def __del__(self):
        """Cleanup when engine is destroyed"""
        if self.is_recording:
            self.stop_recording()