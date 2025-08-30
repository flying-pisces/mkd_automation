"""
Script storage and serialization for MKD Automation.
Handles saving and loading automation scripts to/from files.
"""
import json
import os
import pickle
from pathlib import Path
from typing import Optional, Dict, Any, List
import datetime

from mkd.data.models import AutomationScript, Action
from mkd.core.constants import SCRIPT_EXTENSION


class ScriptStorage:
    """Handles storage and retrieval of automation scripts"""
    
    def __init__(self, storage_format: str = "json"):
        """
        Initialize script storage.
        
        Args:
            storage_format: Format to use for storage ("json" or "pickle")
        """
        self.storage_format = storage_format.lower()
        if self.storage_format not in ["json", "pickle"]:
            raise ValueError(f"Unsupported storage format: {storage_format}")
    
    def save(self, script: AutomationScript, file_path: str) -> None:
        """
        Save an automation script to file.
        
        Args:
            script: The automation script to save
            file_path: Path where to save the script
        """
        if not isinstance(script, AutomationScript):
            raise TypeError("script must be an AutomationScript instance")
        
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if self.storage_format == "json":
                self._save_json(script, file_path)
            elif self.storage_format == "pickle":
                self._save_pickle(script, file_path)
        except Exception as e:
            raise RuntimeError(f"Failed to save script to {file_path}: {e}")
    
    def load(self, file_path: str) -> AutomationScript:
        """
        Load an automation script from file.
        
        Args:
            file_path: Path to the script file
            
        Returns:
            The loaded automation script
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Script file not found: {file_path}")
        
        try:
            # Try to detect format from file content
            if self._is_json_file(file_path):
                return self._load_json(file_path)
            else:
                return self._load_pickle(file_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load script from {file_path}: {e}")
    
    def _save_json(self, script: AutomationScript, file_path: str) -> None:
        """Save script as JSON"""
        data = self._script_to_dict(script)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=self._json_serializer)
    
    def _load_json(self, file_path: str) -> AutomationScript:
        """Load script from JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return self._dict_to_script(data)
    
    def _save_pickle(self, script: AutomationScript, file_path: str) -> None:
        """Save script as pickle"""
        with open(file_path, 'wb') as f:
            pickle.dump(script, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    def _load_pickle(self, file_path: str) -> AutomationScript:
        """Load script from pickle"""
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    
    def _is_json_file(self, file_path: str) -> bool:
        """Check if file appears to be JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_char = f.read(1)
                return first_char in ['{', '[']
        except:
            return False
    
    def _script_to_dict(self, script: AutomationScript) -> Dict[str, Any]:
        """Convert AutomationScript to dictionary"""
        return {
            "name": script.name,
            "description": script.description,
            "created_at": script.created_at.isoformat() if script.created_at else None,
            "version": script.version,
            "metadata": script.metadata,
            "actions": [self._action_to_dict(action) for action in script.actions]
        }
    
    def _action_to_dict(self, action: Action) -> Dict[str, Any]:
        """Convert Action to dictionary"""
        return {
            "type": action.type,
            "data": action.data,
            "timestamp": action.timestamp,
            "duration": action.duration,
            "metadata": action.metadata
        }
    
    def _dict_to_script(self, data: Dict[str, Any]) -> AutomationScript:
        """Convert dictionary to AutomationScript"""
        created_at = None
        if data.get("created_at"):
            try:
                created_at = datetime.datetime.fromisoformat(data["created_at"])
            except ValueError:
                # Fallback to current time if parsing fails
                created_at = datetime.datetime.now()
        
        actions = [self._dict_to_action(action_data) for action_data in data.get("actions", [])]
        
        return AutomationScript(
            name=data.get("name", "Unnamed Script"),
            description=data.get("description", ""),
            created_at=created_at,
            version=data.get("version", "1.0"),
            metadata=data.get("metadata", {}),
            actions=actions
        )
    
    def _dict_to_action(self, data: Dict[str, Any]) -> Action:
        """Convert dictionary to Action"""
        return Action(
            type=data.get("type", "unknown"),
            data=data.get("data", {}),
            timestamp=data.get("timestamp", 0.0),
            duration=data.get("duration"),
            metadata=data.get("metadata", {})
        )
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for non-standard types"""
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def list_scripts(self, directory: str) -> List[Dict[str, Any]]:
        """
        List all script files in a directory.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of script file information
        """
        if not os.path.exists(directory):
            return []
        
        scripts = []
        for filename in os.listdir(directory):
            if filename.endswith(SCRIPT_EXTENSION) or filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                try:
                    stat = os.stat(file_path)
                    scripts.append({
                        "filename": filename,
                        "path": file_path,
                        "size": stat.st_size,
                        "modified": datetime.datetime.fromtimestamp(stat.st_mtime),
                        "created": datetime.datetime.fromtimestamp(stat.st_ctime)
                    })
                except Exception as e:
                    print(f"Warning: Could not get info for {filename}: {e}")
        
        # Sort by modification time, newest first
        scripts.sort(key=lambda x: x["modified"], reverse=True)
        return scripts
    
    def delete_script(self, file_path: str) -> bool:
        """
        Delete a script file.
        
        Args:
            file_path: Path to the script file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting script {file_path}: {e}")
            return False
    
    def validate_script(self, script: AutomationScript) -> List[str]:
        """
        Validate a script for potential issues.
        
        Args:
            script: Script to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not script.name or not script.name.strip():
            errors.append("Script name cannot be empty")
        
        if not script.actions:
            errors.append("Script has no actions")
        
        # Check for negative timestamps
        for i, action in enumerate(script.actions):
            if action.timestamp < 0:
                errors.append(f"Action {i} has negative timestamp: {action.timestamp}")
            
            if not action.type or not action.type.strip():
                errors.append(f"Action {i} has empty type")
        
        # Check timestamp ordering
        timestamps = [action.timestamp for action in script.actions]
        if timestamps != sorted(timestamps):
            errors.append("Actions are not in chronological order")
        
        return errors
    
    def get_script_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get basic information about a script file without fully loading it.
        
        Args:
            file_path: Path to the script file
            
        Returns:
            Script information dictionary, or None if file cannot be read
        """
        try:
            if self._is_json_file(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {
                        "name": data.get("name", "Unknown"),
                        "description": data.get("description", ""),
                        "created_at": data.get("created_at"),
                        "version": data.get("version", "1.0"),
                        "action_count": len(data.get("actions", [])),
                        "format": "json"
                    }
            else:
                # For pickle files, we need to load them fully
                script = self._load_pickle(file_path)
                return {
                    "name": script.name,
                    "description": script.description,
                    "created_at": script.created_at.isoformat() if script.created_at else None,
                    "version": script.version,
                    "action_count": len(script.actions),
                    "format": "pickle"
                }
        except Exception:
            return None