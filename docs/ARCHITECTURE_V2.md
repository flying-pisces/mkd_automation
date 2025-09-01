# Architecture Design Document v2.0
## MKD Automation Platform

**Document Version:** 2.0  
**Date:** 2025-08-27  
**Supersedes:** Original architecture in README.md

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Browser Environment                                 │
│  ┌─────────────────────┐                                                    │
│  │   GUI Application   │                                                    │
│  │  ┌─────────────────┐│                                                    │
│  │  │   Popup UI      ││  ┌─────────────────┐                             │
│  │  │  - Start/Stop   ││  │  Content Script │                             │
│  │  │  - Status       ││  │  - Page Context │                             │
│  │  │  - Settings     ││  │  - DOM Access   │                             │
│  │  └─────────────────┘│  └─────────────────┘                             │
│  │          │           │           │                                       │
│  └──────────┼───────────┘───────────┼───────────────────────────────────────┘
│             │                       │                                       │
│             │    Native Messaging   │                                       │
│             │      Protocol         │                                       │
│             ▼                       ▼                                       │
└─────────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Native Host Application (Python)                      │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐           │
│  │  Message Broker │  │   UI Overlay    │  │  Session Mgr    │           │
│  │  - Cmd Routing  │  │  - Red Border   │  │  - State Track  │           │
│  │  - Response     │  │  - Timer        │  │  - User Auth    │           │
│  │  - Event Pub    │  │  - Controls     │  │  - Permissions  │           │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘           │
│           │                     │                     │                    │
│           ▼                     ▼                     ▼                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Core Engine Layer                                │   │
│  │                                                                     │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │   Recording  │  │   Context    │  │   Playback   │              │   │
│  │  │   Engine     │  │   Analyzer   │  │   Engine     │              │   │
│  │  │              │  │              │  │              │              │   │
│  │  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │              │   │
│  │  │ │Event     │ │  │ │App Track │ │  │ │Action    │ │              │   │
│  │  │ │Capture   │ │  │ │UI Detect │ │  │ │Executor  │ │              │   │
│  │  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │              │   │
│  │  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │              │   │
│  │  │ │Video Rec │ │  │ │Pattern   │ │  │ │Backup    │ │              │   │
│  │  │ │Audio Rec │ │  │ │Analysis  │ │  │ │Mechanism │ │              │   │
│  │  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│           │                     │                     │                    │
│           ▼                     ▼                     ▼                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Platform Abstraction Layer                      │   │
│  │                                                                     │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  Windows     │  │   macOS      │  │    Linux     │              │   │
│  │  │  Platform    │  │  Platform    │  │  Platform    │              │   │
│  │  │              │  │              │  │              │              │   │
│  │  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │              │   │
│  │  │ │Win32 API │ │  │ │Cocoa API │ │  │ │X11/Way   │ │              │   │
│  │  │ │DirectX   │ │  │ │Quartz    │ │  │ │GTK/Qt    │ │              │   │
│  │  │ │PowerShell│ │  │ │Apple     │ │  │ │Shell     │ │              │   │
│  │  │ └──────────┘ │  │ │Script    │ │  │ │Commands  │ │              │   │
│  │  └──────────────┘  │ └──────────┘ │  │ └──────────┘ │              │   │
│  │                    └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│           │                     │                     │                    │
│           ▼                     ▼                     ▼                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Storage & Security Layer                      │   │
│  │                                                                     │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  Database    │  │  File System │  │  Encryption  │              │   │
│  │  │  (SQLite)    │  │  Storage     │  │  Service     │              │   │
│  │  │              │  │              │  │              │              │   │
│  │  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │              │   │
│  │  │ │Users     │ │  │ │Recordings│ │  │ │AES-256   │ │              │   │
│  │  │ │Sessions  │ │  │ │Videos    │ │  │ │Key Mgmt  │ │              │   │
│  │  │ │Audit Log │ │  │ │Temp Files│ │  │ │JWT Token │ │              │   │
│  │  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Component Architecture

### 2.1 GUI Application Layer

#### 2.1.1 Manifest Structure

```json
{
  "manifest_version": 3,
  "name": "MKD Automation",
  "version": "2.0.0",
  "description": "Advanced automation recording and playback",
  
  "permissions": [
    "activeTab",
    "storage",
    "nativeMessaging"
  ],
  
  "host_permissions": [
    "<all_urls>"
  ],
  
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  
  "action": {
    "default_popup": "popup.html",
    "default_title": "MKD Automation"
  },
  
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content-script.js"],
      "run_at": "document_start"
    }
  ],
  
  "web_accessible_resources": [
    {
      "resources": ["injected-script.js"],
      "matches": ["<all_urls>"]
    }
  ]
}
```

#### 2.1.2 Extension Architecture

```typescript
// Extension Component Structure
interface ExtensionArchitecture {
  background: {
    nativeMessaging: NativeMessagingPort;
    commandRouter: CommandRouter;
    stateManager: ExtensionStateManager;
  };
  
  popup: {
    ui: PopupUI;
    controls: RecordingControls;
    statusDisplay: StatusDisplay;
  };
  
  contentScript: {
    pageContext: PageContextExtractor;
    domObserver: DOMChangeObserver;
    eventInjector: EventInjector;
  };
}

// Native Messaging Protocol
interface NativeMessage {
  id: string;
  command: 'START_RECORDING' | 'STOP_RECORDING' | 'GET_STATUS' | 'PAUSE_RECORDING';
  params?: Record<string, any>;
  timestamp: number;
}

interface NativeResponse {
  id: string;
  status: 'SUCCESS' | 'ERROR';
  data?: any;
  error?: string;
  timestamp: number;
}
```

### 2.2 Native Host Application Layer

#### 2.2.1 Core Services Architecture

```python
# Core Service Container
class ServiceContainer:
    """Dependency injection container for all services."""
    
    def __init__(self):
        self.chrome_bridge = ChromeBridge()
        self.session_manager = SessionManager()
        self.recording_engine = RecordingEngine()
        self.playback_engine = PlaybackEngine()
        self.context_analyzer = ContextAnalyzer()
        self.ui_overlay = UIOverlay()
        self.storage_service = StorageService()
        self.security_service = SecurityService()
        self.logger_service = LoggerService()

# Message Broker Pattern
class MessageBroker:
    """Central message routing and event management."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.command_handlers: Dict[str, Callable] = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to events."""
        
    def publish(self, event_type: str, data: Any):
        """Publish events to subscribers."""
        
    def register_command(self, command: str, handler: Callable):
        """Register command handlers."""
        
    def dispatch_command(self, message: NativeMessage) -> NativeResponse:
        """Route commands to appropriate handlers."""
```

#### 2.2.2 Recording Engine Architecture

```python
class RecordingEngine:
    """Orchestrates all recording components."""
    
    def __init__(self):
        self.event_capturer = EventCapturer()
        self.video_recorder = VideoRecorder()
        self.audio_recorder = AudioRecorder()  # Optional
        self.context_analyzer = ContextAnalyzer()
        self.event_processor = EventProcessor()
        self.storage_writer = StorageWriter()
    
    def start_recording(self, config: RecordingConfig):
        """Start comprehensive recording."""
        # Start all capture streams
        # Initialize context tracking
        # Begin data collection
        
    def stop_recording(self) -> RecordingResult:
        """Stop recording and process data."""
        # Stop all streams
        # Process collected data
        # Generate output files
        # Return summary

class EventCapturer:
    """Multi-source event capture."""
    
    def __init__(self):
        self.mouse_listener = None
        self.keyboard_listener = None
        self.screen_recorder = None
        self.window_tracker = None
    
    def start_capture(self):
        """Begin capturing from all sources."""
        
    def stop_capture(self):
        """Stop all capture streams."""

class ContextAnalyzer:
    """Intelligent context detection and analysis."""
    
    def __init__(self):
        self.app_detector = ApplicationDetector()
        self.ui_analyzer = UIElementAnalyzer()
        self.pattern_recognizer = PatternRecognizer()
        self.intent_classifier = IntentClassifier()
    
    def analyze_event(self, event: InputEvent) -> ContextualEvent:
        """Add context to raw events."""
        
    def detect_patterns(self, events: List[ContextualEvent]) -> List[Pattern]:
        """Identify workflow patterns."""
```

#### 2.2.3 Playback Engine Architecture

```python
class PlaybackEngine:
    """Intelligent action playback with fallback mechanisms."""
    
    def __init__(self):
        self.action_executor = ActionExecutor()
        self.backup_mechanism = BackupMechanism()
        self.timing_engine = TimingEngine()
        self.validator = ActionValidator()
    
    def execute_recording(self, recording: Recording) -> PlaybackResult:
        """Execute recorded actions with intelligent fallback."""
        
class ActionExecutor:
    """Primary action execution engine."""
    
    def __init__(self):
        self.platform_executor = self._get_platform_executor()
    
    def execute_action(self, action: ContextualEvent) -> ExecutionResult:
        """Execute single action with validation."""
        # Try UI automation first
        # Fall back to coordinates if needed
        # Validate result
        
class BackupMechanism:
    """Fallback strategies for failed actions."""
    
    def __init__(self):
        self.shell_executor = ShellCommandExecutor()
        self.process_manager = ProcessManager()
        self.hotkey_executor = HotkeyExecutor()
    
    def execute_fallback(self, failed_action: ContextualEvent) -> ExecutionResult:
        """Execute fallback strategy for failed action."""
        # Strategy 1: Keyboard shortcuts
        # Strategy 2: Shell commands
        # Strategy 3: Process manipulation
        # Strategy 4: User notification
```

### 2.3 Platform Abstraction Layer

#### 2.3.1 Platform Interface

```python
from abc import ABC, abstractmethod

class PlatformInterface(ABC):
    """Abstract interface for platform-specific implementations."""
    
    @abstractmethod
    def start_input_capture(self, callback: Callable) -> bool:
        """Start capturing input events."""
        
    @abstractmethod
    def stop_input_capture(self) -> bool:
        """Stop input capture."""
        
    @abstractmethod
    def execute_mouse_action(self, action: MouseAction) -> bool:
        """Execute mouse action."""
        
    @abstractmethod
    def execute_keyboard_action(self, action: KeyboardAction) -> bool:
        """Execute keyboard action."""
        
    @abstractmethod
    def get_active_window_info(self) -> WindowInfo:
        """Get information about active window."""
        
    @abstractmethod
    def get_ui_element_at_position(self, x: int, y: int) -> Optional[UIElement]:
        """Get UI element at screen coordinates."""
        
    @abstractmethod
    def execute_shell_command(self, command: str) -> CommandResult:
        """Execute platform-specific shell command."""
        
    @abstractmethod
    def create_screen_overlay(self, config: OverlayConfig) -> Overlay:
        """Create screen overlay for visual feedback."""
```

#### 2.3.2 Windows Implementation

```python
class WindowsPlatform(PlatformInterface):
    """Windows-specific implementation."""
    
    def __init__(self):
        import win32gui
        import win32api
        import win32con
        from pycaw.pycaw import AudioUtilities
        
        self.win32gui = win32gui
        self.win32api = win32api
        self.win32con = win32con
        self.audio = AudioUtilities
    
    def start_input_capture(self, callback: Callable) -> bool:
        """Use Windows hooks for input capture."""
        # Set up low-level mouse and keyboard hooks
        # Register window change notifications
        
    def get_ui_element_at_position(self, x: int, y: int) -> Optional[UIElement]:
        """Use UI Automation API."""
        # Use Windows UI Automation
        # Fall back to Win32 API
        
    def execute_shell_command(self, command: str) -> CommandResult:
        """Execute PowerShell or CMD command."""
        # Use PowerShell for advanced operations
        # Fall back to CMD for simple commands
```

#### 2.3.3 macOS Implementation

```python
class macOSPlatform(PlatformInterface):
    """macOS-specific implementation."""
    
    def __init__(self):
        from Cocoa import NSApplication, NSWorkspace
        from Quartz import CGWindowListCopyWindowInfo
        from ApplicationServices import AXUIElementCreateApplication
        
        self.cocoa = NSApplication
        self.workspace = NSWorkspace
        self.quartz = CGWindowListCopyWindowInfo
        self.accessibility = AXUIElementCreateApplication
    
    def get_ui_element_at_position(self, x: int, y: int) -> Optional[UIElement]:
        """Use Accessibility API."""
        # Use macOS Accessibility API
        # Fall back to Quartz services
        
    def execute_shell_command(self, command: str) -> CommandResult:
        """Execute AppleScript or shell command."""
        # Use AppleScript for GUI automation
        # Use bash for system commands
```

### 2.4 UI Overlay System

#### 2.4.1 Overlay Architecture

```python
class UIOverlay:
    """Cross-platform overlay system for visual feedback."""
    
    def __init__(self):
        self.overlay_windows = []
        self.timer_widget = None
        self.control_panel = None
        self.border_renderer = None
    
    def create_recording_border(self, config: BorderConfig):
        """Create red border around screens."""
        for monitor in self._get_monitors():
            border_window = self._create_border_window(monitor, config)
            self.overlay_windows.append(border_window)
    
    def create_timer_display(self, position: Position):
        """Create recording timer display."""
        self.timer_widget = TimerWidget(position)
        self.timer_widget.show()
    
    def create_control_panel(self, position: Position):
        """Create floating control panel."""
        self.control_panel = ControlPanel(position)
        self.control_panel.add_stop_button()
        self.control_panel.show()

class TimerWidget:
    """Recording timer with optional stop button."""
    
    def __init__(self, position: Position):
        self.position = position
        self.start_time = None
        self.is_running = False
        self.widget = self._create_widget()
    
    def start_timer(self):
        """Start timer display."""
        self.start_time = time.time()
        self.is_running = True
        self._update_display()
    
    def _update_display(self):
        """Update timer display every second."""
        if self.is_running:
            elapsed = time.time() - self.start_time
            display_time = self._format_time(elapsed)
            self.widget.update_text(display_time)
            # Schedule next update
```

### 2.5 Security Architecture

#### 2.5.1 Authentication System

```python
class SecurityService:
    """Comprehensive security and authentication service."""
    
    def __init__(self):
        self.user_manager = UserManager()
        self.session_manager = SessionManager()
        self.encryption_service = EncryptionService()
        self.audit_logger = AuditLogger()
    
    def authenticate_user(self, username: str, password: str) -> AuthResult:
        """Authenticate user credentials."""
        # Verify password hash
        # Check account status
        # Generate JWT token
        # Log authentication attempt
        
    def authorize_action(self, user_id: int, action: str, resource: str) -> bool:
        """Check user permissions for action."""
        # Get user role
        # Check permission matrix
        # Log authorization attempt
        
    def encrypt_recording(self, recording_data: bytes, user_id: int) -> bytes:
        """Encrypt recording with user-specific key."""
        # Generate or retrieve user encryption key
        # Encrypt data with AES-256
        # Add integrity verification
        
class UserManager:
    """User account and role management."""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_user(self, username: str, password: str, role: UserRole) -> User:
        """Create new user account."""
        # Hash password with salt
        # Store user record
        # Initialize user settings
        
    def get_user_permissions(self, user_id: int) -> Set[Permission]:
        """Get all permissions for user."""
        # Get user role
        # Return role permissions
```

### 2.6 Storage Architecture

#### 2.6.1 Data Storage Strategy

```python
class StorageService:
    """Multi-tier storage management."""
    
    def __init__(self):
        self.metadata_db = SQLiteDatabase()
        self.file_storage = FileSystemStorage()
        self.encryption = EncryptionService()
        self.compression = CompressionService()
    
    def store_recording(self, recording: Recording, user_id: int) -> str:
        """Store recording with metadata."""
        # Compress recording data
        # Encrypt if required
        # Store file to disk
        # Store metadata to database
        # Return recording ID
        
    def retrieve_recording(self, recording_id: str, user_id: int) -> Recording:
        """Retrieve and decrypt recording."""
        # Check user permissions
        # Load metadata from database
        # Load file from disk
        # Decrypt if required
        # Decompress data
        # Return recording object

class RecordingFormat:
    """MKD file format specification."""
    
    header: RecordingHeader
    events: List[ContextualEvent]
    video_data: Optional[bytes]
    audio_data: Optional[bytes]
    metadata: RecordingMetadata
    checksum: str
```

## 3. Data Flow Architecture

### 3.1 Recording Data Flow

```
[User Input] 
    ↓
[Platform Input Hooks] 
    ↓
[Event Capturer] 
    ↓
[Context Analyzer] → [Application Detector]
    ↓                 [UI Element Analyzer]
[Event Processor]     [Pattern Recognizer]
    ↓
[Parallel Streams]
    ├─ [Video Recorder] → [FFmpeg Encoder]
    ├─ [Screenshot Capture] → [Image Processor]
    └─ [Audio Recorder] → [Audio Encoder]
    ↓
[Data Synchronizer] → [Timestamp Alignment]
    ↓
[Storage Writer] → [Compression] → [Encryption] → [File System]
    ↓
[Database Writer] → [Metadata Storage]
```

### 3.2 Playback Data Flow

```
[Recording Selection]
    ↓
[Security Check] → [User Authorization]
    ↓
[File Loader] → [Decryption] → [Decompression]
    ↓
[Action Validator] → [Compatibility Check]
    ↓
[Timing Engine] → [Speed Control] → [Pause/Resume]
    ↓
[Action Executor]
    ├─ [Primary Method] → [UI Automation]
    │   ↓ (if fails)
    ├─ [Backup Method] → [Keyboard Shortcuts]
    │   ↓ (if fails)
    ├─ [Shell Commands] → [Process Management]
    │   ↓ (if fails)
    └─ [User Notification] → [Manual Intervention]
    ↓
[Result Validator] → [Success Verification]
    ↓
[Logger Service] → [Audit Trail]
```

### 3.3 Application Communication Flow

```
[GUI Application]
    ↓ (user click)
[Background Script] → [Command Validation]
    ↓
[Native Messaging Port] → [JSON Message]
    ↓
[Native Host Receiver] → [Message Deserializer]
    ↓
[Command Router] → [Security Check] → [User Session]
    ↓
[Service Dispatcher]
    ├─ [Recording Service]
    ├─ [Playback Service]
    ├─ [Status Service]
    └─ [Configuration Service]
    ↓
[Response Builder] → [JSON Response]
    ↓
[Native Messaging Port] ← [Response Serializer]
    ↓
[Background Script] ← [Message Handler]
    ↓
[Extension UI Update] ← [State Manager]
```

## 4. Performance Considerations

### 4.1 Recording Performance Optimization

```python
class PerformanceOptimizer:
    """Optimize recording performance across all streams."""
    
    def __init__(self):
        self.event_buffer = RingBuffer(size=10000)
        self.video_encoder = HardwareEncoder()  # Use GPU if available
        self.compression_pool = ThreadPool(workers=4)
        self.io_scheduler = AsyncIOScheduler()
    
    def optimize_event_capture(self):
        """Optimize input event capture."""
        # Use ring buffer for events
        # Batch write operations
        # Async I/O for disk writes
        
    def optimize_video_recording(self):
        """Optimize video recording performance."""
        # Use hardware encoding
        # Adjust quality based on CPU load
        # Stream compression
```

### 4.2 Memory Management

```python
class MemoryManager:
    """Intelligent memory management for large recordings."""
    
    def __init__(self):
        self.memory_threshold = 100 * 1024 * 1024  # 100MB
        self.swap_storage = SwapFileManager()
        self.gc_scheduler = GarbageCollectionScheduler()
    
    def monitor_memory_usage(self):
        """Monitor and manage memory consumption."""
        # Track memory usage
        # Trigger garbage collection
        # Swap to disk if needed
```

## 5. Deployment Architecture

### 5.1 Installation Strategy

```yaml
Installation_Components:
  Chrome_Extension:
    distribution: "Chrome Web Store"
    permissions: "minimal required"
    auto_update: true
    
  Native_Host:
    windows: "MSI installer"
    macos: "PKG installer"  
    linux: "AppImage / DEB / RPM"
    
  Dependencies:
    python_runtime: "embedded with installer"
    native_libraries: "platform-specific bundles"
    
  Registry_Setup:
    chrome_native_messaging: "automatic registration"
    file_associations: "optional .mkd files"
    system_permissions: "prompt for accessibility"
```

### 5.2 Update Mechanism

```python
class UpdateService:
    """Automatic update management."""
    
    def __init__(self):
        self.version_checker = VersionChecker()
        self.update_downloader = SecureDownloader()
        self.installer = UpdateInstaller()
    
    def check_for_updates(self) -> UpdateInfo:
        """Check for available updates."""
        # Check current version
        # Query update server
        # Verify digital signatures
        
    def apply_update(self, update_info: UpdateInfo):
        """Apply update safely."""
        # Backup current installation
        # Download update package
        # Verify integrity
        # Install update
        # Rollback if needed
```

This architecture provides a robust, scalable, and secure foundation for the MKD Automation Platform v2.0, addressing all requirements outlined in the ERS while maintaining performance and cross-platform compatibility.