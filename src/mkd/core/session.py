"""
Core session management for MKD Automation.

This module provides the main Session class that manages automation
sessions, recordings, and integrates with the GUI conversation interface.
"""

import uuid
import time
import logging
from typing import Optional, Dict, Any, List, Callable
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Session state enumeration."""
    IDLE = "idle"
    RECORDING = "recording"
    PLAYING = "playing"
    PAUSED = "paused"
    ERROR = "error"


class Action:
    """Represents a single automation action."""
    
    def __init__(self, action_type: str, timestamp: float = None, data: Dict[str, Any] = None):
        self.type = action_type
        self.timestamp = timestamp or time.time()
        self.data = data or {}
        self.id = str(uuid.uuid4())
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary."""
        return {
            'id': self.id,
            'type': self.type,
            'timestamp': self.timestamp,
            'data': self.data
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        """Create action from dictionary."""
        action = cls(
            action_type=data['type'],
            timestamp=data.get('timestamp'),
            data=data.get('data', {})
        )
        action.id = data.get('id', str(uuid.uuid4()))
        return action


class Session:
    """
    Main session class for MKD Automation.
    
    Manages automation sessions, recordings, and provides integration
    points for the GUI and browser automation.
    """
    
    def __init__(self, session_id: str = None):
        """Initialize a new session."""
        self.id = session_id or str(uuid.uuid4())
        self.state = SessionState.IDLE
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Session data
        self.actions: List[Action] = []
        self.metadata: Dict[str, Any] = {}
        self.current_recording = None
        
        # Callbacks for integration
        self.on_action_executed: Optional[Callable] = None
        self.on_state_changed: Optional[Callable] = None
        self.on_recording_started: Optional[Callable] = None
        self.on_recording_stopped: Optional[Callable] = None
        
        # Execution components (set by integrations)
        self.executor = None
        self.browser_integration = None
        
        logger.info(f"Session created: {self.id}")
        
    def start_recording(self) -> None:
        """Start recording actions."""
        if self.state == SessionState.RECORDING:
            logger.warning("Session already recording")
            return
            
        self.state = SessionState.RECORDING
        self.updated_at = datetime.now()
        self.current_recording = {
            'started_at': time.time(),
            'actions': []
        }
        
        if self.on_recording_started:
            self.on_recording_started()
            
        if self.on_state_changed:
            self.on_state_changed(self.state)
            
        logger.info("Recording started")
        
    def stop_recording(self) -> List[Action]:
        """Stop recording and return recorded actions."""
        if self.state != SessionState.RECORDING:
            logger.warning("Session not recording")
            return []
            
        recorded_actions = []
        if self.current_recording:
            recorded_actions = self.current_recording.get('actions', [])
            self.current_recording['stopped_at'] = time.time()
            
        self.state = SessionState.IDLE
        self.updated_at = datetime.now()
        
        if self.on_recording_stopped:
            self.on_recording_stopped(recorded_actions)
            
        if self.on_state_changed:
            self.on_state_changed(self.state)
            
        logger.info(f"Recording stopped. Captured {len(recorded_actions)} actions")
        return recorded_actions
        
    def add_action(self, action: Action) -> None:
        """Add an action to the session."""
        self.actions.append(action)
        
        # Add to current recording if active
        if self.state == SessionState.RECORDING and self.current_recording:
            self.current_recording['actions'].append(action)
            
        self.updated_at = datetime.now()
        
        # Notify callbacks
        if self.on_action_executed:
            self.on_action_executed(action, None)
            
        logger.debug(f"Action added: {action.type}")
        
    def execute_action(self, action: Action) -> Any:
        """Execute an action using the configured executor."""
        if not self.executor:
            logger.warning("No executor configured for session")
            return None
            
        try:
            self.state = SessionState.PLAYING
            self.updated_at = datetime.now()
            
            if self.on_state_changed:
                self.on_state_changed(self.state)
                
            result = self.executor.execute_action(action)
            
            # Add to session history
            self.add_action(action)
            
            self.state = SessionState.IDLE
            if self.on_state_changed:
                self.on_state_changed(self.state)
                
            return result
            
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            self.state = SessionState.ERROR
            if self.on_state_changed:
                self.on_state_changed(self.state)
            raise
            
    def get_status(self) -> Dict[str, Any]:
        """Get current session status."""
        return {
            'id': self.id,
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'action_count': len(self.actions),
            'is_recording': self.state == SessionState.RECORDING,
            'recording_actions': len(self.current_recording['actions']) if self.current_recording else 0,
            'metadata': self.metadata
        }
        
    def clear_actions(self) -> None:
        """Clear all actions from the session."""
        self.actions.clear()
        self.updated_at = datetime.now()
        logger.info("Session actions cleared")
        
    def save_to_file(self, filename: str) -> None:
        """Save session to file."""
        import json
        
        session_data = {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'state': self.state.value,
            'actions': [action.to_dict() for action in self.actions],
            'metadata': self.metadata
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Session saved to {filename}")
        
    @classmethod
    def load_from_file(cls, filename: str) -> 'Session':
        """Load session from file."""
        import json
        
        with open(filename, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
            
        session = cls(session_id=session_data['id'])
        session.created_at = datetime.fromisoformat(session_data['created_at'])
        session.updated_at = datetime.fromisoformat(session_data['updated_at'])
        session.state = SessionState(session_data['state'])
        session.metadata = session_data.get('metadata', {})
        
        # Load actions
        for action_data in session_data.get('actions', []):
            action = Action.from_dict(action_data)
            session.actions.append(action)
            
        logger.info(f"Session loaded from {filename}")
        return session
        
    def __str__(self) -> str:
        """String representation of session."""
        return f"Session({self.id}, state={self.state.value}, actions={len(self.actions)})"
        
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"Session(id='{self.id}', state={self.state.value}, "
                f"created_at='{self.created_at}', actions={len(self.actions)})")