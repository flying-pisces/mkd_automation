"""
Session Manager - Manages recording sessions and user state.

Handles recording session lifecycle, state persistence, and user authentication
for MKD Automation Platform v2.0.
"""

import json
import logging
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib


logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Recording session states."""
    INACTIVE = "inactive"
    STARTING = "starting"
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPING = "stopping"
    COMPLETED = "completed"
    ERROR = "error"


class UserRole(Enum):
    """User roles for permission management."""
    ADMIN = "admin"
    EDITOR = "editor"
    EXECUTOR = "executor"
    VIEWER = "viewer"


@dataclass
class RecordingConfig:
    """Configuration for a recording session."""
    capture_video: bool = True
    capture_audio: bool = False
    show_border: bool = True
    border_color: str = "#FF0000"
    mouse_sample_rate: int = 60
    keyboard_capture: bool = True
    screenshot_on_events: bool = True
    compress_events: bool = True
    encrypt_data: bool = False


@dataclass
class User:
    """User information."""
    id: int
    username: str
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None


@dataclass
class RecordingSession:
    """Recording session information."""
    id: str
    user_id: int
    state: SessionState
    config: RecordingConfig
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration: Optional[float] = None
    event_count: int = 0
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionManager:
    """
    Manages recording sessions and user authentication.
    
    Features:
    - Session lifecycle management
    - User authentication and authorization
    - Session state persistence
    - Configuration management
    - Multi-user support
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".mkd" / "sessions"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.storage_path / "sessions.db"
        self._lock = threading.RLock()
        
        # In-memory session cache
        self.active_sessions: Dict[str, RecordingSession] = {}
        self.user_sessions: Dict[int, str] = {}  # user_id -> session_id mapping
        
        # Initialize database
        self._init_database()
        
        logger.info(f"SessionManager initialized with storage: {self.storage_path}")
    
    def _init_database(self):
        """Initialize SQLite database for session persistence."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        settings TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        user_id INTEGER,
                        state TEXT NOT NULL,
                        config TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        started_at TIMESTAMP,
                        ended_at TIMESTAMP,
                        duration REAL,
                        event_count INTEGER DEFAULT 0,
                        file_path TEXT,
                        error_message TEXT,
                        metadata TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # Create default admin user if none exists
                cursor = conn.execute("SELECT COUNT(*) FROM users")
                if cursor.fetchone()[0] == 0:
                    self._create_default_admin(conn)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def _create_default_admin(self, conn: sqlite3.Connection):
        """Create default admin user."""
        password_hash = self._hash_password("admin123")
        
        conn.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
        """, ("admin", password_hash, UserRole.ADMIN.value))
        
        logger.info("Created default admin user (username: admin, password: admin123)")
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt."""
        salt = "mkd_automation_v2"  # In production, use random salt per user
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user credentials.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        try:
            password_hash = self._hash_password(password)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM users 
                    WHERE username = ? AND password_hash = ?
                """, (username, password_hash))
                
                row = cursor.fetchone()
                if not row:
                    logger.warning(f"Authentication failed for user: {username}")
                    return None
                
                # Update last login
                conn.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (row['id'],))
                conn.commit()
                
                # Parse settings
                settings = None
                if row['settings']:
                    try:
                        settings = json.loads(row['settings'])
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid settings JSON for user {username}")
                
                user = User(
                    id=row['id'],
                    username=row['username'],
                    role=UserRole(row['role']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_login=datetime.fromisoformat(row['last_login']) if row['last_login'] else None,
                    settings=settings
                )
                
                logger.info(f"User authenticated: {username} (role: {user.role.value})")
                return user
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def create_session(self, user_id: int, config: Optional[RecordingConfig] = None) -> RecordingSession:
        """
        Create a new recording session.
        
        Args:
            user_id: User ID creating the session
            config: Recording configuration
            
        Returns:
            Created RecordingSession
            
        Raises:
            ValueError: If user already has an active session
        """
        with self._lock:
            # Check if user already has active session
            if user_id in self.user_sessions:
                existing_session_id = self.user_sessions[user_id]
                existing_session = self.active_sessions.get(existing_session_id)
                if existing_session and existing_session.state not in [SessionState.COMPLETED, SessionState.ERROR]:
                    raise ValueError(f"User {user_id} already has an active session")
            
            # Create new session
            session_id = str(uuid.uuid4())
            session_config = config or RecordingConfig()
            
            session = RecordingSession(
                id=session_id,
                user_id=user_id,
                state=SessionState.INACTIVE,
                config=session_config,
                created_at=datetime.now(),
                metadata={}
            )
            
            # Store in memory and database
            self.active_sessions[session_id] = session
            self.user_sessions[user_id] = session_id
            self._persist_session(session)
            
            logger.info(f"Created session {session_id} for user {user_id}")
            return session
    
    def get_session(self, session_id: str) -> Optional[RecordingSession]:
        """
        Get session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            RecordingSession if found, None otherwise
        """
        with self._lock:
            if session_id in self.active_sessions:
                return self.active_sessions[session_id]
            
            # Try loading from database
            return self._load_session(session_id)
    
    def get_user_session(self, user_id: int) -> Optional[RecordingSession]:
        """
        Get active session for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Active RecordingSession if found, None otherwise
        """
        with self._lock:
            if user_id in self.user_sessions:
                session_id = self.user_sessions[user_id]
                return self.active_sessions.get(session_id)
            return None
    
    def start_recording(self, session_id: str) -> bool:
        """
        Start recording for a session.
        
        Args:
            session_id: Session ID to start recording
            
        Returns:
            True if recording started successfully
        """
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                logger.error(f"Session not found: {session_id}")
                return False
            
            if session.state != SessionState.INACTIVE:
                logger.error(f"Cannot start recording: session {session_id} is in state {session.state}")
                return False
            
            # Update session state
            session.state = SessionState.STARTING
            session.started_at = datetime.now()
            self._persist_session(session)
            
            logger.info(f"Recording started for session {session_id}")
            return True
    
    def set_recording_active(self, session_id: str) -> bool:
        """
        Set session state to actively recording.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if state updated successfully
        """
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                return False
            
            session.state = SessionState.RECORDING
            self._persist_session(session)
            
            logger.info(f"Session {session_id} is now actively recording")
            return True
    
    def pause_recording(self, session_id: str) -> bool:
        """
        Pause recording for a session.
        
        Args:
            session_id: Session ID to pause
            
        Returns:
            True if paused successfully
        """
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                return False
            
            if session.state != SessionState.RECORDING:
                logger.error(f"Cannot pause: session {session_id} is not recording")
                return False
            
            session.state = SessionState.PAUSED
            self._persist_session(session)
            
            logger.info(f"Recording paused for session {session_id}")
            return True
    
    def resume_recording(self, session_id: str) -> bool:
        """
        Resume recording for a paused session.
        
        Args:
            session_id: Session ID to resume
            
        Returns:
            True if resumed successfully
        """
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                return False
            
            if session.state != SessionState.PAUSED:
                logger.error(f"Cannot resume: session {session_id} is not paused")
                return False
            
            session.state = SessionState.RECORDING
            self._persist_session(session)
            
            logger.info(f"Recording resumed for session {session_id}")
            return True
    
    def stop_recording(self, session_id: str) -> bool:
        """
        Stop recording for a session.
        
        Args:
            session_id: Session ID to stop
            
        Returns:
            True if stopped successfully
        """
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                return False
            
            if session.state not in [SessionState.RECORDING, SessionState.PAUSED]:
                logger.error(f"Cannot stop: session {session_id} is not recording")
                return False
            
            # Calculate duration
            if session.started_at:
                session.duration = (datetime.now() - session.started_at).total_seconds()
            
            session.state = SessionState.STOPPING
            session.ended_at = datetime.now()
            self._persist_session(session)
            
            logger.info(f"Recording stopped for session {session_id}")
            return True
    
    def complete_session(self, session_id: str, event_count: int = 0, file_path: Optional[str] = None) -> bool:
        """
        Mark session as completed.
        
        Args:
            session_id: Session ID to complete
            event_count: Number of events recorded
            file_path: Path to saved recording file
            
        Returns:
            True if completed successfully
        """
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                return False
            
            session.state = SessionState.COMPLETED
            session.event_count = event_count
            session.file_path = file_path
            self._persist_session(session)
            
            # Remove from active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            if session.user_id in self.user_sessions and self.user_sessions[session.user_id] == session_id:
                del self.user_sessions[session.user_id]
            
            logger.info(f"Session {session_id} completed with {event_count} events")
            return True
    
    def set_session_error(self, session_id: str, error_message: str) -> bool:
        """
        Mark session as having an error.
        
        Args:
            session_id: Session ID
            error_message: Error description
            
        Returns:
            True if error state set successfully
        """
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                return False
            
            session.state = SessionState.ERROR
            session.error_message = error_message
            session.ended_at = datetime.now()
            self._persist_session(session)
            
            logger.error(f"Session {session_id} error: {error_message}")
            return True
    
    def update_session_metadata(self, session_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update session metadata.
        
        Args:
            session_id: Session ID
            metadata: Metadata to update
            
        Returns:
            True if updated successfully
        """
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                return False
            
            if session.metadata is None:
                session.metadata = {}
            session.metadata.update(metadata)
            self._persist_session(session)
            
            return True
    
    def _persist_session(self, session: RecordingSession):
        """Persist session to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO sessions 
                    (id, user_id, state, config, created_at, started_at, ended_at, 
                     duration, event_count, file_path, error_message, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.id,
                    session.user_id,
                    session.state.value,
                    json.dumps(asdict(session.config)),
                    session.created_at.isoformat(),
                    session.started_at.isoformat() if session.started_at else None,
                    session.ended_at.isoformat() if session.ended_at else None,
                    session.duration,
                    session.event_count,
                    session.file_path,
                    session.error_message,
                    json.dumps(session.metadata) if session.metadata else None
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error persisting session {session.id}: {e}")
    
    def _load_session(self, session_id: str) -> Optional[RecordingSession]:
        """Load session from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM sessions WHERE id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Parse config and metadata
                config = RecordingConfig(**json.loads(row['config']))
                metadata = json.loads(row['metadata']) if row['metadata'] else None
                
                session = RecordingSession(
                    id=row['id'],
                    user_id=row['user_id'],
                    state=SessionState(row['state']),
                    config=config,
                    created_at=datetime.fromisoformat(row['created_at']),
                    started_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
                    ended_at=datetime.fromisoformat(row['ended_at']) if row['ended_at'] else None,
                    duration=row['duration'],
                    event_count=row['event_count'],
                    file_path=row['file_path'],
                    error_message=row['error_message'],
                    metadata=metadata
                )
                
                # Add to active sessions if not completed
                if session.state not in [SessionState.COMPLETED, SessionState.ERROR]:
                    self.active_sessions[session_id] = session
                    self.user_sessions[session.user_id] = session_id
                
                return session
                
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None
    
    def get_user_sessions(self, user_id: int, limit: int = 50) -> List[RecordingSession]:
        """
        Get recent sessions for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of sessions to return
            
        Returns:
            List of RecordingSessions
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM sessions 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (user_id, limit))
                
                sessions = []
                for row in cursor.fetchall():
                    config = RecordingConfig(**json.loads(row['config']))
                    metadata = json.loads(row['metadata']) if row['metadata'] else None
                    
                    session = RecordingSession(
                        id=row['id'],
                        user_id=row['user_id'],
                        state=SessionState(row['state']),
                        config=config,
                        created_at=datetime.fromisoformat(row['created_at']),
                        started_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
                        ended_at=datetime.fromisoformat(row['ended_at']) if row['ended_at'] else None,
                        duration=row['duration'],
                        event_count=row['event_count'],
                        file_path=row['file_path'],
                        error_message=row['error_message'],
                        metadata=metadata
                    )
                    sessions.append(session)
                
                return sessions
                
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []
    
    def cleanup_old_sessions(self, days_old: int = 30):
        """
        Clean up old completed sessions.
        
        Args:
            days_old: Age threshold in days
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM sessions 
                    WHERE state IN ('completed', 'error') 
                    AND created_at < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old sessions")
                
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get session manager status."""
        with self._lock:
            return {
                'active_sessions': len(self.active_sessions),
                'user_sessions': len(self.user_sessions),
                'storage_path': str(self.storage_path),
                'database_path': str(self.db_path),
                'sessions_by_state': self._get_session_stats()
            }
    
    def _get_session_stats(self) -> Dict[str, int]:
        """Get session statistics by state."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT state, COUNT(*) as count 
                    FROM sessions 
                    GROUP BY state
                """)
                
                return {row[0]: row[1] for row in cursor.fetchall()}
                
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return {}