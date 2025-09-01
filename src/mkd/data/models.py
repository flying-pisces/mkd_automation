"""
Data models for MKD Automation scripts and actions.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import datetime


@dataclass
class Action:
    """Represents a single automation action (mouse click, keyboard input, etc.)"""
    type: str
    data: Dict[str, Any]
    timestamp: float
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate action after initialization"""
        if not self.type:
            raise ValueError("Action type cannot be empty")
        if self.timestamp < 0:
            raise ValueError("Action timestamp cannot be negative")


@dataclass
class AutomationScript:
    """Represents a complete automation script containing a sequence of actions"""
    name: str
    description: str = ""
    created_at: Optional[datetime.datetime] = None
    actions: List[Action] = field(default_factory=list)
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Set defaults after initialization"""
        if self.created_at is None:
            self.created_at = datetime.datetime.now()
        if not self.name:
            raise ValueError("Script name cannot be empty")

    def add_action(self, action: Action) -> None:
        """Add an action to the script"""
        self.actions.append(action)

    def get_duration(self) -> float:
        """Calculate total duration of the script"""
        if not self.actions:
            return 0.0
        return max(action.timestamp for action in self.actions)

    def get_action_count(self) -> int:
        """Get total number of actions in the script"""
        return len(self.actions)


@dataclass
class RecordingSession:
    """Represents a recording session state"""
    session_id: str
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    actions: List[Action] = field(default_factory=list)
    is_active: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def start(self) -> None:
        """Start the recording session"""
        self.start_time = datetime.datetime.now()
        self.is_active = True
        self.actions.clear()

    def stop(self) -> None:
        """Stop the recording session"""
        self.end_time = datetime.datetime.now()
        self.is_active = False

    def add_action(self, action: Action) -> None:
        """Add an action to the current session"""
        if self.is_active:
            self.actions.append(action)

    def to_script(self, name: str, description: str = "") -> AutomationScript:
        """Convert session to an automation script"""
        return AutomationScript(
            name=name,
            description=description,
            created_at=self.start_time,
            actions=self.actions.copy(),
            metadata=self.metadata.copy()
        )