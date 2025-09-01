"""
Constants and configuration values for MKD Automation.
"""

# Application metadata
APP_NAME = "MKD Automation"
APP_VERSION = "2.0.0"

# File extensions
SCRIPT_EXTENSION = ".mkd"
CONFIG_EXTENSION = ".json"

# Recording settings defaults
DEFAULT_SAMPLE_RATE = 60  # Hz
DEFAULT_MOTION_THRESHOLD = 5  # pixels
DEFAULT_CAPTURE_MOUSE = True
DEFAULT_CAPTURE_KEYBOARD = True
DEFAULT_CAPTURE_SCREEN = False

# Playback settings defaults
DEFAULT_SPEED_MULTIPLIER = 1.0
DEFAULT_ERROR_HANDLING = "pause"  # pause, skip, stop
DEFAULT_VERIFY_ACTIONS = True

# Session states
SESSION_STATE_IDLE = "idle"
SESSION_STATE_RECORDING = "recording"
SESSION_STATE_PLAYING = "playing"
SESSION_STATE_PAUSED = "paused"

# Action types
ACTION_TYPE_MOUSE_MOVE = "mouse_move"
ACTION_TYPE_MOUSE_CLICK = "mouse_click"
ACTION_TYPE_MOUSE_DRAG = "mouse_drag"
ACTION_TYPE_KEYBOARD = "keyboard"
ACTION_TYPE_WAIT = "wait"
ACTION_TYPE_SCREENSHOT = "screenshot"

# Mouse buttons
MOUSE_BUTTON_LEFT = "left"
MOUSE_BUTTON_RIGHT = "right"
MOUSE_BUTTON_MIDDLE = "middle"

# Keyboard actions
KEYBOARD_ACTION_PRESS = "press"
KEYBOARD_ACTION_RELEASE = "release"
KEYBOARD_ACTION_TYPE = "type"

# Error handling modes
ERROR_HANDLING_PAUSE = "pause"
ERROR_HANDLING_SKIP = "skip"
ERROR_HANDLING_STOP = "stop"
ERROR_HANDLING_RETRY = "retry"

# File paths
DEFAULT_CONFIG_DIR = "config"
DEFAULT_SCRIPTS_DIR = "scripts"
DEFAULT_LOGS_DIR = "logs"

# Logging levels
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"

# Performance settings
MAX_ACTION_QUEUE_SIZE = 1000
DEFAULT_PROCESSING_THREADS = 2
MEMORY_USAGE_WARNING_THRESHOLD = 100  # MB

# UI settings
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600
DEFAULT_THEME = "default"

# Platform detection
PLATFORM_WINDOWS = "Windows"
PLATFORM_MACOS = "Darwin"
PLATFORM_LINUX = "Linux"