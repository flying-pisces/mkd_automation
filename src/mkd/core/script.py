"""
Script management for MKD Automation.

This module provides classes for managing automation scripts,
including browser and desktop actions.
"""

import json
import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .session import Action


class Script:
    """
    Represents an automation script containing a sequence of actions.
    
    Scripts can contain mixed browser and desktop actions and can be
    saved, loaded, and executed.
    """
    
    def __init__(self, name: str = "Untitled Script", description: str = ""):
        """Initialize a new script."""
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.actions: List[Action] = []
        self.metadata: Dict[str, Any] = {}
        self.version = "1.0"
        
    def add_action(self, action: Action) -> None:
        """Add an action to the script."""
        self.actions.append(action)
        self.updated_at = datetime.now()
        
    def remove_action(self, action_id: str) -> bool:
        """Remove an action by ID."""
        for i, action in enumerate(self.actions):
            if action.id == action_id:
                del self.actions[i]
                self.updated_at = datetime.now()
                return True
        return False
        
    def insert_action(self, index: int, action: Action) -> None:
        """Insert an action at a specific index."""
        self.actions.insert(index, action)
        self.updated_at = datetime.now()
        
    def get_action_by_id(self, action_id: str) -> Optional[Action]:
        """Get an action by its ID."""
        for action in self.actions:
            if action.id == action_id:
                return action
        return None
        
    def get_actions_by_type(self, action_type: str) -> List[Action]:
        """Get all actions of a specific type."""
        return [action for action in self.actions if action.type == action_type]
        
    def get_browser_actions(self) -> List[Action]:
        """Get all browser-related actions."""
        return self.get_actions_by_type("browser")
        
    def get_desktop_actions(self) -> List[Action]:
        """Get all desktop-related actions."""
        return [action for action in self.actions if action.type != "browser"]
        
    def get_duration(self) -> float:
        """Get the total duration of the script in seconds."""
        if len(self.actions) < 2:
            return 0.0
            
        start_time = min(action.timestamp for action in self.actions if action.timestamp)
        end_time = max(action.timestamp for action in self.actions if action.timestamp)
        
        return end_time - start_time
        
    def sort_actions_by_time(self) -> None:
        """Sort actions by timestamp."""
        self.actions.sort(key=lambda a: a.timestamp or 0)
        self.updated_at = datetime.now()
        
    def clear_actions(self) -> None:
        """Remove all actions from the script."""
        self.actions.clear()
        self.updated_at = datetime.now()
        
    def clone(self, new_name: str = None) -> 'Script':
        """Create a copy of this script."""
        clone_name = new_name or f"{self.name} (Copy)"
        cloned_script = Script(clone_name, self.description)
        
        # Copy actions
        for action in self.actions:
            cloned_action = Action(
                action_type=action.type,
                timestamp=action.timestamp,
                data=action.data.copy()
            )
            cloned_script.add_action(cloned_action)
            
        # Copy metadata
        cloned_script.metadata = self.metadata.copy()
        
        return cloned_script
        
    def merge_script(self, other_script: 'Script') -> None:
        """Merge another script's actions into this script."""
        for action in other_script.actions:
            cloned_action = Action(
                action_type=action.type,
                timestamp=action.timestamp,
                data=action.data.copy()
            )
            self.add_action(cloned_action)
            
        # Sort by timestamp after merging
        self.sort_actions_by_time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert script to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'version': self.version,
            'actions': [action.to_dict() for action in self.actions],
            'metadata': self.metadata,
            'stats': {
                'action_count': len(self.actions),
                'browser_actions': len(self.get_browser_actions()),
                'desktop_actions': len(self.get_desktop_actions()),
                'duration': self.get_duration()
            }
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Script':
        """Create script from dictionary."""
        script = cls(
            name=data.get('name', 'Untitled Script'),
            description=data.get('description', '')
        )
        
        script.id = data.get('id', str(uuid.uuid4()))
        script.version = data.get('version', '1.0')
        script.metadata = data.get('metadata', {})
        
        # Parse timestamps
        if 'created_at' in data:
            script.created_at = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            script.updated_at = datetime.fromisoformat(data['updated_at'])
            
        # Load actions
        for action_data in data.get('actions', []):
            action = Action.from_dict(action_data)
            script.actions.append(action)
            
        return script
        
    def save(self, filename: str, format: str = "json") -> None:
        """Save script to file."""
        filepath = Path(filename)
        
        if format.lower() == "json":
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        elif format.lower() == "mkd":
            # Custom MKD format (compressed JSON)
            import lz4.frame
            data = json.dumps(self.to_dict()).encode('utf-8')
            compressed = lz4.frame.compress(data)
            with open(filepath, 'wb') as f:
                f.write(compressed)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    @classmethod
    def load(cls, filename: str, format: str = None) -> 'Script':
        """Load script from file."""
        filepath = Path(filename)
        
        # Auto-detect format if not specified
        if format is None:
            format = "mkd" if filepath.suffix.lower() == ".mkd" else "json"
            
        if format.lower() == "json":
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif format.lower() == "mkd":
            # Custom MKD format (compressed JSON)
            import lz4.frame
            with open(filepath, 'rb') as f:
                compressed = f.read()
            data_bytes = lz4.frame.decompress(compressed)
            data = json.loads(data_bytes.decode('utf-8'))
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        return cls.from_dict(data)
        
    def validate(self) -> List[str]:
        """Validate the script and return any issues found."""
        issues = []
        
        if not self.name.strip():
            issues.append("Script name is empty")
            
        if not self.actions:
            issues.append("Script has no actions")
            
        # Check for valid timestamps
        for i, action in enumerate(self.actions):
            if not action.timestamp:
                issues.append(f"Action {i+1} has no timestamp")
            if not action.type:
                issues.append(f"Action {i+1} has no type")
                
        # Check for reasonable time ordering
        timestamps = [a.timestamp for a in self.actions if a.timestamp]
        if len(timestamps) > 1:
            sorted_timestamps = sorted(timestamps)
            if timestamps != sorted_timestamps:
                issues.append("Actions are not in chronological order")
                
        return issues
        
    def get_summary(self) -> str:
        """Get a human-readable summary of the script."""
        duration = self.get_duration()
        browser_count = len(self.get_browser_actions())
        desktop_count = len(self.get_desktop_actions())
        
        summary = f"Script '{self.name}'\n"
        summary += f"Actions: {len(self.actions)} total"
        
        if browser_count > 0:
            summary += f", {browser_count} browser"
        if desktop_count > 0:
            summary += f", {desktop_count} desktop"
            
        if duration > 0:
            summary += f"\nDuration: {duration:.1f} seconds"
            
        if self.description:
            summary += f"\nDescription: {self.description}"
            
        return summary
        
    def __str__(self) -> str:
        """String representation."""
        return f"Script('{self.name}', {len(self.actions)} actions)"
        
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"Script(id='{self.id}', name='{self.name}', "
                f"actions={len(self.actions)}, created='{self.created_at}')")