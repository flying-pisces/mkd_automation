"""
Configuration management for MKD Automation.
Handles loading, saving, and providing access to application settings.
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

from mkd.core.constants import (
    DEFAULT_SAMPLE_RATE, DEFAULT_MOTION_THRESHOLD, DEFAULT_CAPTURE_MOUSE,
    DEFAULT_CAPTURE_KEYBOARD, DEFAULT_CAPTURE_SCREEN, DEFAULT_SPEED_MULTIPLIER,
    DEFAULT_ERROR_HANDLING, DEFAULT_VERIFY_ACTIONS, DEFAULT_THEME,
    DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
)


class ConfigManager:
    """Manages application configuration settings"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self._config = self._load_default_config()
        
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values"""
        return {
            "recording": {
                "sample_rate": DEFAULT_SAMPLE_RATE,
                "motion_threshold": DEFAULT_MOTION_THRESHOLD,
                "capture_mouse": DEFAULT_CAPTURE_MOUSE,
                "capture_keyboard": DEFAULT_CAPTURE_KEYBOARD,
                "capture_screen": DEFAULT_CAPTURE_SCREEN
            },
            "playback": {
                "speed_multiplier": DEFAULT_SPEED_MULTIPLIER,
                "error_handling": DEFAULT_ERROR_HANDLING,
                "verify_actions": DEFAULT_VERIFY_ACTIONS
            },
            "ui": {
                "theme": DEFAULT_THEME,
                "window_width": DEFAULT_WINDOW_WIDTH,
                "window_height": DEFAULT_WINDOW_HEIGHT
            },
            "paths": {
                "scripts_dir": "scripts",
                "config_dir": "config",
                "logs_dir": "logs"
            }
        }
    
    def _load_config(self, config_path: str) -> None:
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                # Merge file config with defaults
                self._merge_config(self._config, file_config)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
    
    def _merge_config(self, default: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge configuration dictionaries"""
        for key, value in override.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    def get_recording_settings(self) -> Dict[str, Any]:
        """Get recording configuration settings"""
        return self._config.get("recording", {})
    
    def get_playback_settings(self) -> Dict[str, Any]:
        """Get playback configuration settings"""
        return self._config.get("playback", {})
    
    def get_ui_settings(self) -> Dict[str, Any]:
        """Get UI configuration settings"""
        return self._config.get("ui", {})
    
    def get_paths(self) -> Dict[str, str]:
        """Get path configuration settings"""
        return self._config.get("paths", {})
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific setting value using dot notation.
        
        Args:
            key: Setting key (e.g., 'recording.sample_rate')
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        keys = key.split('.')
        current = self._config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a specific setting value using dot notation.
        
        Args:
            key: Setting key (e.g., 'recording.sample_rate')
            value: New value
        """
        keys = key.split('.')
        current = self._config
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        # Set the value
        current[keys[-1]] = value
    
    def save_config(self, config_path: Optional[str] = None) -> None:
        """
        Save current configuration to file.
        
        Args:
            config_path: Optional path to save to, uses instance path if None
        """
        path = config_path or self.config_path
        if not path:
            raise ValueError("No config path specified")
        
        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(path, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to save config to {path}: {e}")
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self._config = self._load_default_config()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings"""
        return self._config.copy()