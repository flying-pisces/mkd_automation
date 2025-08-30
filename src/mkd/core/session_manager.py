"""
Session management for MKD Automation.
Handles recording sessions, state management, and session lifecycle.
"""
import uuid
import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from mkd.core.constants import (
    SESSION_STATE_IDLE, SESSION_STATE_RECORDING, 
    SESSION_STATE_PLAYING, SESSION_STATE_PAUSED
)
from mkd.data.models import RecordingSession, Action, AutomationScript


class SessionState(Enum):
    """Session state enumeration"""
    IDLE = SESSION_STATE_IDLE
    RECORDING = SESSION_STATE_RECORDING
    PLAYING = SESSION_STATE_PLAYING
    PAUSED = SESSION_STATE_PAUSED


class SessionManager:
    """Manages recording and playback sessions"""
    
    def __init__(self):
        """Initialize the session manager"""
        self.session_id = str(uuid.uuid4())
        self._state = SessionState.IDLE
        self._current_session: Optional[RecordingSession] = None
        self._sessions: Dict[str, RecordingSession] = {}
        self._event_handlers: Dict[str, List[callable]] = {}
        self._start_time: Optional[datetime.datetime] = None
        
    def get_state(self) -> str:
        """Get current session state"""
        return self._state.value
    
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self._state == SessionState.RECORDING
    
    def is_playing(self) -> bool:
        """Check if currently playing back"""
        return self._state == SessionState.PLAYING
    
    def is_paused(self) -> bool:
        """Check if currently paused"""
        return self._state == SessionState.PAUSED
    
    def is_idle(self) -> bool:
        """Check if currently idle"""
        return self._state == SessionState.IDLE
    
    def start_recording(self) -> str:
        """
        Start a new recording session.
        
        Returns:
            Session ID for the new recording session
        """
        if self._state != SessionState.IDLE:
            raise RuntimeError(f"Cannot start recording in state: {self._state.value}")
        
        # Create new recording session
        session_id = str(uuid.uuid4())
        self._current_session = RecordingSession(
            session_id=session_id,
            metadata={
                "created_by": "SessionManager",
                "created_at": datetime.datetime.now().isoformat()
            }
        )
        
        # Start the session
        self._current_session.start()
        self._sessions[session_id] = self._current_session
        self._state = SessionState.RECORDING
        self._start_time = datetime.datetime.now()
        
        # Notify handlers
        self._emit_event("recording_started", {
            "session_id": session_id,
            "timestamp": self._start_time
        })
        
        return session_id
    
    def stop_recording(self) -> Optional[RecordingSession]:
        """
        Stop the current recording session.
        
        Returns:
            The completed recording session, or None if not recording
        """
        if self._state != SessionState.RECORDING:
            return None
        
        if self._current_session:
            self._current_session.stop()
            session = self._current_session
            self._current_session = None
        else:
            session = None
        
        self._state = SessionState.IDLE
        end_time = datetime.datetime.now()
        
        # Notify handlers
        self._emit_event("recording_stopped", {
            "session_id": session.session_id if session else None,
            "timestamp": end_time,
            "duration": (end_time - self._start_time).total_seconds() if self._start_time else 0
        })
        
        return session
    
    def pause_recording(self) -> bool:
        """
        Pause the current recording session.
        
        Returns:
            True if paused successfully, False otherwise
        """
        if self._state != SessionState.RECORDING:
            return False
        
        self._state = SessionState.PAUSED
        
        # Notify handlers
        self._emit_event("recording_paused", {
            "session_id": self._current_session.session_id if self._current_session else None,
            "timestamp": datetime.datetime.now()
        })
        
        return True
    
    def resume_recording(self) -> bool:
        """
        Resume a paused recording session.
        
        Returns:
            True if resumed successfully, False otherwise
        """
        if self._state != SessionState.PAUSED:
            return False
        
        self._state = SessionState.RECORDING
        
        # Notify handlers
        self._emit_event("recording_resumed", {
            "session_id": self._current_session.session_id if self._current_session else None,
            "timestamp": datetime.datetime.now()
        })
        
        return True
    
    def add_action(self, action: Action) -> bool:
        """
        Add an action to the current recording session.
        
        Args:
            action: The action to add
            
        Returns:
            True if added successfully, False otherwise
        """
        if self._state != SessionState.RECORDING or not self._current_session:
            return False
        
        self._current_session.add_action(action)
        
        # Notify handlers
        self._emit_event("action_recorded", {
            "session_id": self._current_session.session_id,
            "action": action,
            "timestamp": datetime.datetime.now()
        })
        
        return True
    
    def get_current_session(self) -> Optional[RecordingSession]:
        """Get the current recording session"""
        return self._current_session
    
    def get_session(self, session_id: str) -> Optional[RecordingSession]:
        """Get a session by ID"""
        return self._sessions.get(session_id)
    
    def get_all_sessions(self) -> Dict[str, RecordingSession]:
        """Get all sessions"""
        return self._sessions.copy()
    
    def create_script_from_session(self, session_id: str, name: str, 
                                 description: str = "") -> Optional[AutomationScript]:
        """
        Create an automation script from a session.
        
        Args:
            session_id: ID of the session to convert
            name: Name for the new script
            description: Description for the new script
            
        Returns:
            The created AutomationScript, or None if session not found
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        return session.to_script(name, description)
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear a session from memory.
        
        Args:
            session_id: ID of the session to clear
            
        Returns:
            True if cleared successfully, False otherwise
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            
            # If this was the current session, reset state
            if (self._current_session and 
                self._current_session.session_id == session_id):
                self._current_session = None
                self._state = SessionState.IDLE
            
            return True
        
        return False
    
    def add_event_handler(self, event_type: str, handler: callable) -> None:
        """
        Add an event handler for session events.
        
        Args:
            event_type: Type of event to handle
            handler: Function to call when event occurs
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def remove_event_handler(self, event_type: str, handler: callable) -> bool:
        """
        Remove an event handler.
        
        Args:
            event_type: Type of event
            handler: Handler function to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type].remove(handler)
                return True
            except ValueError:
                pass
        return False
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to all registered handlers"""
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(event_type, data)
                except Exception as e:
                    print(f"Error in event handler for {event_type}: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about current sessions"""
        total_sessions = len(self._sessions)
        total_actions = sum(len(session.actions) for session in self._sessions.values())
        
        current_session_stats = {}
        if self._current_session:
            current_session_stats = {
                "session_id": self._current_session.session_id,
                "actions_count": len(self._current_session.actions),
                "is_active": self._current_session.is_active,
                "start_time": self._current_session.start_time.isoformat() if self._current_session.start_time else None
            }
        
        return {
            "state": self._state.value,
            "total_sessions": total_sessions,
            "total_actions": total_actions,
            "current_session": current_session_stats
        }