"""
Desktop action definitions for comprehensive system automation.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any, Dict, Tuple, List
import time


class DesktopActionType(Enum):
    """Types of desktop actions for full system control."""
    
    # Mouse actions
    MOUSE_CLICK = "mouse_click"
    MOUSE_DOUBLE_CLICK = "mouse_double_click"
    MOUSE_RIGHT_CLICK = "mouse_right_click"
    MOUSE_MOVE = "mouse_move"
    MOUSE_DRAG = "mouse_drag"
    MOUSE_SCROLL = "mouse_scroll"
    
    # Keyboard actions
    KEY_PRESS = "key_press"
    KEY_COMBINATION = "key_combination"
    TYPE_TEXT = "type_text"
    
    # Application management
    LAUNCH_APP = "launch_app"
    CLOSE_APP = "close_app"
    SWITCH_APP = "switch_app"
    MINIMIZE_WINDOW = "minimize_window"
    MAXIMIZE_WINDOW = "maximize_window"
    RESTORE_WINDOW = "restore_window"
    RESIZE_WINDOW = "resize_window"
    MOVE_WINDOW = "move_window"
    
    # File operations
    OPEN_FILE = "open_file"
    OPEN_FOLDER = "open_folder"
    CREATE_FILE = "create_file"
    CREATE_FOLDER = "create_folder"
    DELETE_FILE = "delete_file"
    DELETE_FOLDER = "delete_folder"
    COPY_FILE = "copy_file"
    MOVE_FILE = "move_file"
    RENAME_FILE = "rename_file"
    
    # System operations
    RUN_COMMAND = "run_command"
    OPEN_CMD = "open_cmd"
    OPEN_POWERSHELL = "open_powershell"
    OPEN_TASK_MANAGER = "open_task_manager"
    OPEN_CONTROL_PANEL = "open_control_panel"
    OPEN_SETTINGS = "open_settings"
    SHUTDOWN_SYSTEM = "shutdown_system"
    RESTART_SYSTEM = "restart_system"
    LOCK_SYSTEM = "lock_system"
    
    # Screen operations
    SCREENSHOT = "screenshot"
    SCREEN_RECORD_START = "screen_record_start"
    SCREEN_RECORD_STOP = "screen_record_stop"
    
    # Wait operations
    WAIT_TIME = "wait_time"
    WAIT_FOR_WINDOW = "wait_for_window"
    WAIT_FOR_IMAGE = "wait_for_image"
    WAIT_FOR_TEXT = "wait_for_text"
    
    # Advanced operations
    OCR_READ_TEXT = "ocr_read_text"
    FIND_IMAGE = "find_image"
    COMPARE_IMAGES = "compare_images"
    
    # System state
    GET_ACTIVE_WINDOW = "get_active_window"
    GET_WINDOW_LIST = "get_window_list"
    GET_PROCESS_LIST = "get_process_list"
    GET_SYSTEM_INFO = "get_system_info"


@dataclass
class DesktopAction:
    """Represents a desktop automation action."""
    type: DesktopActionType
    parameters: Dict[str, Any]
    timestamp: float = None
    description: str = ""
    
    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = time.time()
    
    @staticmethod
    def mouse_click(x: int, y: int, button: str = "left") -> 'DesktopAction':
        """Create a mouse click action."""
        return DesktopAction(
            type=DesktopActionType.MOUSE_CLICK,
            parameters={"x": x, "y": y, "button": button},
            description=f"Click {button} mouse button at ({x}, {y})"
        )
    
    @staticmethod
    def mouse_move(x: int, y: int, smooth: bool = True) -> 'DesktopAction':
        """Create a mouse move action."""
        return DesktopAction(
            type=DesktopActionType.MOUSE_MOVE,
            parameters={"x": x, "y": y, "smooth": smooth},
            description=f"Move mouse to ({x}, {y})"
        )
    
    @staticmethod
    def key_press(key: str, modifiers: List[str] = None) -> 'DesktopAction':
        """Create a key press action."""
        return DesktopAction(
            type=DesktopActionType.KEY_PRESS,
            parameters={"key": key, "modifiers": modifiers or []},
            description=f"Press key: {'+'.join((modifiers or []) + [key])}"
        )
    
    @staticmethod
    def key_combination(keys: List[str]) -> 'DesktopAction':
        """Create a key combination action (e.g., Ctrl+C)."""
        return DesktopAction(
            type=DesktopActionType.KEY_COMBINATION,
            parameters={"keys": keys},
            description=f"Key combination: {'+'.join(keys)}"
        )
    
    @staticmethod
    def type_text(text: str, delay: float = 0.05) -> 'DesktopAction':
        """Create a type text action."""
        return DesktopAction(
            type=DesktopActionType.TYPE_TEXT,
            parameters={"text": text, "delay": delay},
            description=f"Type text: '{text[:50]}...'" if len(text) > 50 else f"Type text: '{text}'"
        )
    
    @staticmethod
    def launch_app(app_name: str, path: str = None, args: List[str] = None) -> 'DesktopAction':
        """Create a launch application action."""
        return DesktopAction(
            type=DesktopActionType.LAUNCH_APP,
            parameters={"app_name": app_name, "path": path, "args": args or []},
            description=f"Launch application: {app_name}"
        )
    
    @staticmethod
    def open_file(file_path: str, app: str = None) -> 'DesktopAction':
        """Create an open file action."""
        return DesktopAction(
            type=DesktopActionType.OPEN_FILE,
            parameters={"file_path": file_path, "app": app},
            description=f"Open file: {file_path}"
        )
    
    @staticmethod
    def open_folder(folder_path: str) -> 'DesktopAction':
        """Create an open folder action."""
        return DesktopAction(
            type=DesktopActionType.OPEN_FOLDER,
            parameters={"folder_path": folder_path},
            description=f"Open folder: {folder_path}"
        )
    
    @staticmethod
    def run_command(command: str, shell: str = "cmd", wait: bool = True) -> 'DesktopAction':
        """Create a run command action."""
        return DesktopAction(
            type=DesktopActionType.RUN_COMMAND,
            parameters={"command": command, "shell": shell, "wait": wait},
            description=f"Run command: {command}"
        )
    
    @staticmethod
    def screenshot(file_path: str = None, region: Tuple[int, int, int, int] = None) -> 'DesktopAction':
        """Create a screenshot action."""
        return DesktopAction(
            type=DesktopActionType.SCREENSHOT,
            parameters={"file_path": file_path, "region": region},
            description=f"Take screenshot{f' to {file_path}' if file_path else ''}"
        )
    
    @staticmethod
    def wait_time(seconds: float) -> 'DesktopAction':
        """Create a wait time action."""
        return DesktopAction(
            type=DesktopActionType.WAIT_TIME,
            parameters={"seconds": seconds},
            description=f"Wait {seconds} seconds"
        )
    
    @staticmethod
    def resize_window(width: int, height: int, window_title: str = None) -> 'DesktopAction':
        """Create a resize window action."""
        return DesktopAction(
            type=DesktopActionType.RESIZE_WINDOW,
            parameters={"width": width, "height": height, "window_title": window_title},
            description=f"Resize window to {width}x{height}"
        )
    
    @staticmethod
    def move_window(x: int, y: int, window_title: str = None) -> 'DesktopAction':
        """Create a move window action."""
        return DesktopAction(
            type=DesktopActionType.MOVE_WINDOW,
            parameters={"x": x, "y": y, "window_title": window_title},
            description=f"Move window to ({x}, {y})"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary."""
        return {
            'type': self.type.value,
            'parameters': self.parameters,
            'timestamp': self.timestamp,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DesktopAction':
        """Create action from dictionary."""
        return cls(
            type=DesktopActionType(data['type']),
            parameters=data['parameters'],
            timestamp=data.get('timestamp'),
            description=data.get('description', '')
        )