"""
Input Action Data Structures

Defines data structures for representing user input actions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple, List, Dict, Any


class ActionType(Enum):
    """Types of user input actions"""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    MIDDLE_CLICK = "middle_click"
    MOUSE_DOWN = "mouse_down"
    MOUSE_UP = "mouse_up"
    MOUSE_MOVE = "mouse_move"
    SCROLL = "scroll"
    DRAG = "drag"
    DROP = "drop"
    
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    TYPE_TEXT = "type_text"
    
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    CUSTOM = "custom"


@dataclass
class InputAction:
    """Represents a single user input action"""
    action_type: ActionType
    timestamp: float
    coordinates: Optional[Tuple[int, int]] = None
    key: Optional[str] = None
    modifiers: List[str] = field(default_factory=list)
    text: Optional[str] = None
    button: str = "left"  # For mouse actions
    scroll_direction: str = "down"  # For scroll actions
    scroll_amount: int = 1  # For scroll actions
    duration: Optional[float] = None  # For wait actions
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate action after initialization"""
        if self.action_type in [ActionType.CLICK, ActionType.DOUBLE_CLICK, ActionType.RIGHT_CLICK]:
            if self.coordinates is None:
                raise ValueError(f"{self.action_type} requires coordinates")
        
        if self.action_type == ActionType.TYPE_TEXT:
            if not self.text:
                raise ValueError("TYPE_TEXT requires text")
        
        if self.action_type == ActionType.WAIT:
            if self.duration is None or self.duration <= 0:
                raise ValueError("WAIT requires positive duration")
    
    @property
    def x(self) -> Optional[int]:
        """X coordinate for mouse actions"""
        return self.coordinates[0] if self.coordinates else None
    
    @property
    def y(self) -> Optional[int]:
        """Y coordinate for mouse actions"""
        return self.coordinates[1] if self.coordinates else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary representation"""
        return {
            "action_type": self.action_type.value,
            "timestamp": self.timestamp,
            "coordinates": self.coordinates,
            "key": self.key,
            "modifiers": self.modifiers,
            "text": self.text,
            "button": self.button,
            "scroll_direction": self.scroll_direction,
            "scroll_amount": self.scroll_amount,
            "duration": self.duration,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InputAction':
        """Create action from dictionary representation"""
        data = data.copy()
        data["action_type"] = ActionType(data["action_type"])
        return cls(**data)