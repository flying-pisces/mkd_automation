"""
Recording Engine - Main controller for recording user interactions.

Orchestrates input capture, context analysis, and data storage for
comprehensive automation recording.
"""

import asyncio
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import uuid

from ..core.session_manager import SessionManager, RecordingSession, SessionState
from ..platform.detector import PlatformDetector
from ..ui.overlay import ScreenOverlay, BorderConfig, TimerConfig
from .input_capturer import InputCapturer
from .event_processor import EventProcessor


logger = logging.getLogger(__name__)


class RecordingState(Enum):
    """Recording engine states."""
    IDLE = "idle"
    STARTING = "starting"
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class RecordingEvent:
    """Standardized recording event."""
    id: str
    timestamp: float
    event_type: str
    source: str  # mouse, keyboard, system
    data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    screenshot_path: Optional[str] = None


class RecordingEngine:
    """
    Main recording engine that orchestrates all recording components.
    
    Features:
    - Cross-platform input capture
    - Context-aware event processing
    - Real-time event filtering
    - Parallel data streams (video, audio, events)
    - Session state management
    """
    
    def __init__(self, session_manager: Optional[SessionManager] = None):
        self.session_manager = session_manager or SessionManager()
        self.platform = PlatformDetector.detect()
        
        self.input_capturer = InputCapturer(self.platform)
        self.event_processor = EventProcessor()
        self.overlay = ScreenOverlay(self.platform)
        
        self.state = RecordingState.IDLE
        self.current_session: Optional[RecordingSession] = None
        self.current_user_id: Optional[int] = None
        
        # Event storage
        self.recorded_events: List[RecordingEvent] = []
        self.event_count = 0
        
        # Threading and synchronization
        self._lock = threading.RLock()
        self._event_loop = None
        self._recording_task = None
        
        # Performance tracking
        self.stats = {
            'events_captured': 0,
            'events_filtered': 0,
            'events_processed': 0,
            'recording_start_time': None,
            'recording_duration': 0,
            'average_event_rate': 0
        }
        
        logger.info("RecordingEngine initialized")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current recording status.
        
        Returns:
            Dictionary with recording status and statistics
        """
        with self._lock:
            return {
                'state': self.state.value,
                'session_id': self.current_session.id if self.current_session else None,
                'user_id': self.current_user_id,
                'event_count': self.event_count,
                'is_recording': self.state == RecordingState.RECORDING,
                'is_paused': self.state == RecordingState.PAUSED,
                'platform': self.platform.name,
                'stats': self.stats.copy(),
                'capabilities': self.platform.get_capabilities()
            }
    
    def start_recording(self, user_id: int, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Start recording session.
        
        Args:
            user_id: User ID starting the recording
            config: Recording configuration
            
        Returns:
            Dictionary with session information
            
        Raises:
            RuntimeError: If recording cannot be started
        """
        with self._lock:
            if self.state != RecordingState.IDLE:
                raise RuntimeError(f"Cannot start recording: engine is in state {self.state}")
            
            try:
                # Create recording session
                from ..core.session_manager import RecordingConfig
                session_config = RecordingConfig(**(config or {}))
                session = self.session_manager.create_session(user_id, session_config)
                
                self.current_session = session
                self.current_user_id = user_id
                self.state = RecordingState.STARTING
                
                # Initialize recording components
                self._initialize_recording()
                
                # Start session
                success = self.session_manager.start_recording(session.id)
                if not success:
                    raise RuntimeError("Failed to start session")
                
                # Start actual recording
                self._start_recording_async()
                
                # Show visual indicators
                self._show_recording_indicators(session_config)
                
                self.state = RecordingState.RECORDING
                self.session_manager.set_recording_active(session.id)
                
                self.stats['recording_start_time'] = time.time()
                
                logger.info(f"Recording started for user {user_id}, session {session.id}")
                
                return {
                    'sessionId': session.id,
                    'userId': user_id,
                    'startTime': session.started_at.isoformat() if session.started_at else None,
                    'config': session.config.__dict__
                }
                
            except Exception as e:
                self.state = RecordingState.ERROR
                if self.current_session:
                    self.session_manager.set_session_error(
                        self.current_session.id, 
                        str(e)
                    )
                logger.error(f"Failed to start recording: {e}")
                raise RuntimeError(f"Failed to start recording: {e}")
    
    def stop_recording(self) -> Dict[str, Any]:
        """
        Stop current recording session.
        
        Returns:
            Dictionary with recording results
            
        Raises:
            RuntimeError: If no recording is active
        """
        with self._lock:
            if self.state not in [RecordingState.RECORDING, RecordingState.PAUSED]:
                raise RuntimeError("No active recording to stop")
            
            try:
                session = self.current_session
                if not session:
                    raise RuntimeError("No active session")
                
                self.state = RecordingState.STOPPING
                
                # Stop recording components
                self._stop_recording_async()
                
                # Hide visual indicators
                self.overlay.hide_recording_indicators()
                
                # Process and save recorded data
                file_path = self._save_recording_data(session)
                
                # Complete session
                self.session_manager.complete_session(
                    session.id,
                    event_count=self.event_count,
                    file_path=file_path
                )
                
                # Update statistics
                end_time = time.time()
                if self.stats['recording_start_time']:
                    duration = end_time - self.stats['recording_start_time']
                    self.stats['recording_duration'] = duration
                    if duration > 0:
                        self.stats['average_event_rate'] = self.event_count / duration
                
                result = {
                    'sessionId': session.id,
                    'filePath': file_path,
                    'eventCount': self.event_count,
                    'duration': self.stats['recording_duration'],
                    'averageEventRate': self.stats['average_event_rate'],
                    'endTime': datetime.now().isoformat()
                }
                
                # Reset state
                self._reset_recording_state()
                
                logger.info(f"Recording stopped: {result}")
                return result
                
            except Exception as e:
                self.state = RecordingState.ERROR
                if self.current_session:
                    self.session_manager.set_session_error(
                        self.current_session.id,
                        str(e)
                    )
                logger.error(f"Failed to stop recording: {e}")
                raise RuntimeError(f"Failed to stop recording: {e}")
    
    def pause_recording(self) -> Dict[str, Any]:
        """
        Pause current recording session.
        
        Returns:
            Dictionary with pause confirmation
        """
        with self._lock:
            if self.state != RecordingState.RECORDING:
                raise RuntimeError("No active recording to pause")
            
            try:
                # Pause input capture
                self.input_capturer.pause()
                
                # Update session state
                session_id = self.current_session.id
                self.session_manager.pause_recording(session_id)
                
                self.state = RecordingState.PAUSED
                
                logger.info(f"Recording paused: {session_id}")
                
                return {
                    'sessionId': session_id,
                    'state': 'paused',
                    'pausedAt': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Failed to pause recording: {e}")
                raise RuntimeError(f"Failed to pause recording: {e}")
    
    def resume_recording(self) -> Dict[str, Any]:
        """
        Resume paused recording session.
        
        Returns:
            Dictionary with resume confirmation
        """
        with self._lock:
            if self.state != RecordingState.PAUSED:
                raise RuntimeError("No paused recording to resume")
            
            try:
                # Resume input capture
                self.input_capturer.resume()
                
                # Update session state
                session_id = self.current_session.id
                self.session_manager.resume_recording(session_id)
                
                self.state = RecordingState.RECORDING
                
                logger.info(f"Recording resumed: {session_id}")
                
                return {
                    'sessionId': session_id,
                    'state': 'recording',
                    'resumedAt': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Failed to resume recording: {e}")
                raise RuntimeError(f"Failed to resume recording: {e}")
    
    def _initialize_recording(self):
        """Initialize recording components."""
        try:
            # Initialize platform
            platform_init = self.platform.initialize()
            if not platform_init.get('success', False):
                raise RuntimeError("Platform initialization failed")
            
            # Check permissions
            permissions = self.platform.check_permissions()
            if not permissions.get('overall', False):
                missing = permissions.get('missing_permissions', [])
                raise RuntimeError(f"Missing permissions: {missing}")
            
            # Initialize input capturer
            self.input_capturer.initialize()
            
            # Initialize event processor
            self.event_processor.initialize()
            
            # Reset event storage
            self.recorded_events.clear()
            self.event_count = 0
            self.stats['events_captured'] = 0
            self.stats['events_filtered'] = 0
            self.stats['events_processed'] = 0
            
        except Exception as e:
            logger.error(f"Recording initialization failed: {e}")
            raise
    
    def _show_recording_indicators(self, config):
        """Show visual recording indicators."""
        try:
            # Configure red border
            border_config = BorderConfig(
                show_border=config.show_border if hasattr(config, 'show_border') else True,
                color="#FF0000",
                width=5,
                opacity=0.8,
                style="solid"
            )
            
            # Configure timer display
            timer_config = TimerConfig(
                show_timer=True,
                position="top-right",
                font_size=16,
                font_color="#FFFFFF",
                background_color="#000000",
                background_opacity=0.7,
                format="mm:ss"
            )
            
            # Show indicators
            success = self.overlay.show_recording_indicators(border_config, timer_config)
            if not success:
                logger.warning("Failed to show recording indicators")
                
        except Exception as e:
            logger.error(f"Error showing recording indicators: {e}")
    
    def _start_recording_async(self):
        """Start asynchronous recording process."""
        # Start input capture with event callback
        self.input_capturer.start_capture(self._handle_input_event)
        
        # Start event processing loop
        self._event_loop = asyncio.new_event_loop()
        recording_thread = threading.Thread(
            target=self._run_recording_loop,
            daemon=True,
            name="RecordingLoop"
        )
        recording_thread.start()
    
    def _stop_recording_async(self):
        """Stop asynchronous recording process."""
        # Stop input capture
        self.input_capturer.stop_capture()
        
        # Stop event processing loop
        if self._event_loop:
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
    
    def _run_recording_loop(self):
        """Run the main recording event loop."""
        asyncio.set_event_loop(self._event_loop)
        try:
            self._event_loop.run_forever()
        except Exception as e:
            logger.error(f"Recording loop error: {e}")
        finally:
            self._event_loop.close()
    
    def _handle_input_event(self, raw_event: Dict[str, Any]):
        """
        Handle input event from input capturer.
        
        Args:
            raw_event: Raw event data from input capture
        """
        try:
            # Update statistics
            self.stats['events_captured'] += 1
            
            # Process event
            processed_event = self.event_processor.process_event(raw_event)
            
            if processed_event:
                # Convert to RecordingEvent
                recording_event = RecordingEvent(
                    id=str(uuid.uuid4()),
                    timestamp=processed_event.get('timestamp', time.time()),
                    event_type=processed_event.get('type', 'unknown'),
                    source=processed_event.get('source', 'unknown'),
                    data=processed_event.get('data', {}),
                    context=processed_event.get('context')
                )
                
                # Store event
                with self._lock:
                    self.recorded_events.append(recording_event)
                    self.event_count += 1
                    self.stats['events_processed'] += 1
                
            else:
                self.stats['events_filtered'] += 1
                
        except Exception as e:
            logger.error(f"Error handling input event: {e}")
    
    def _save_recording_data(self, session: RecordingSession) -> str:
        """
        Save recording data to file.
        
        Args:
            session: Recording session
            
        Returns:
            Path to saved recording file
        """
        try:
            import json
            from pathlib import Path
            
            # Create output directory
            output_dir = Path.home() / ".mkd" / "recordings"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}_{session.id[:8]}.mkd"
            file_path = output_dir / filename
            
            # Prepare recording data
            recording_data = {
                'version': '2.0.0',
                'session': {
                    'id': session.id,
                    'user_id': session.user_id,
                    'created_at': session.created_at.isoformat(),
                    'started_at': session.started_at.isoformat() if session.started_at else None,
                    'config': session.config.__dict__
                },
                'events': [
                    {
                        'id': event.id,
                        'timestamp': event.timestamp,
                        'event_type': event.event_type,
                        'source': event.source,
                        'data': event.data,
                        'context': event.context
                    }
                    for event in self.recorded_events
                ],
                'stats': self.stats,
                'platform': {
                    'name': self.platform.name,
                    'capabilities': self.platform.get_capabilities()
                }
            }
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(recording_data, f, indent=2, default=str)
            
            logger.info(f"Recording saved to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to save recording data: {e}")
            raise
    
    def _reset_recording_state(self):
        """Reset recording state after completion."""
        self.state = RecordingState.IDLE
        self.current_session = None
        self.current_user_id = None
        self.recorded_events.clear()
        self.event_count = 0
        
        # Clean up resources
        self.input_capturer.cleanup()
        self.event_processor.cleanup()
        self.overlay.cleanup()
    
    def get_recorded_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recorded events.
        
        Args:
            limit: Optional limit on number of events
            
        Returns:
            List of recorded events
        """
        with self._lock:
            events = self.recorded_events
            if limit:
                events = events[-limit:]
            
            return [
                {
                    'id': event.id,
                    'timestamp': event.timestamp,
                    'event_type': event.event_type,
                    'source': event.source,
                    'data': event.data,
                    'context': event.context
                }
                for event in events
            ]
    
    def cleanup(self):
        """Clean up recording engine resources."""
        logger.info("Cleaning up RecordingEngine")
        
        # Stop any active recording
        if self.state in [RecordingState.RECORDING, RecordingState.PAUSED]:
            try:
                self.stop_recording()
            except Exception as e:
                logger.error(f"Error stopping recording during cleanup: {e}")
        
        # Clean up components
        self.input_capturer.cleanup()
        self.event_processor.cleanup()
        self.overlay.cleanup()
        self.platform.cleanup()
        
        # Clean up async resources
        if self._event_loop:
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        
        logger.info("RecordingEngine cleanup complete")