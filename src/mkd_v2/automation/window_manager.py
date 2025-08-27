"""
Cross-Platform Window Management and Information Retrieval.

Provides window enumeration, focus management, and window property access
using platform-specific APIs.
"""

import logging
import platform
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import time

# Platform-specific imports
if platform.system() == "Darwin":
    try:
        from AppKit import NSWorkspace, NSRunningApplication
        APPKIT_AVAILABLE = True
    except ImportError:
        APPKIT_AVAILABLE = False
else:
    APPKIT_AVAILABLE = False

if platform.system() == "Windows":
    try:
        import win32gui
        import win32process
        import win32api
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
else:
    WIN32_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class WindowInfo:
    """Information about a window."""
    window_id: str
    title: str
    process_name: str
    process_id: int
    bounds: Tuple[int, int, int, int]  # x, y, width, height
    is_visible: bool = True
    is_minimized: bool = False
    is_active: bool = False
    z_order: int = 0
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
    
    @property
    def center_point(self) -> Tuple[int, int]:
        """Get center point of window."""
        x, y, w, h = self.bounds
        return (x + w // 2, y + h // 2)
    
    @property
    def area(self) -> int:
        """Get window area in pixels."""
        _, _, w, h = self.bounds
        return w * h


class WindowManager(ABC):
    """Abstract base class for platform-specific window managers."""
    
    @abstractmethod
    def get_active_window(self) -> Optional[WindowInfo]:
        """Get information about the currently active window."""
        pass
    
    @abstractmethod
    def get_window_list(self) -> List[WindowInfo]:
        """Get list of all visible windows."""
        pass
    
    @abstractmethod
    def get_window_at_point(self, x: int, y: int) -> Optional[WindowInfo]:
        """Get window at specific screen coordinates."""
        pass
    
    @abstractmethod
    def focus_window(self, window_id: str) -> bool:
        """Bring window to front and focus it."""
        pass
    
    @abstractmethod
    def get_window_screenshot(self, window_id: str) -> Optional[bytes]:
        """Take screenshot of specific window."""
        pass


class MacOSWindowManager(WindowManager):
    """macOS-specific window manager using AppKit."""
    
    def __init__(self):
        self.workspace = None
        if APPKIT_AVAILABLE:
            try:
                self.workspace = NSWorkspace.sharedWorkspace()
                logger.info("macOS WindowManager initialized with AppKit")
            except Exception as e:
                logger.error(f"Failed to initialize AppKit workspace: {e}")
        else:
            logger.warning("AppKit not available - using fallback methods")
    
    def get_active_window(self) -> Optional[WindowInfo]:
        """Get active window using AppKit."""
        try:
            if APPKIT_AVAILABLE and self.workspace:
                # Get active application
                active_app = self.workspace.activeApplication()
                if active_app:
                    return self._create_window_info_from_app(active_app, is_active=True)
            
            # Fallback to shell command
            return self._get_active_window_fallback()
            
        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            return None
    
    def get_window_list(self) -> List[WindowInfo]:
        """Get list of windows using AppKit."""
        windows = []
        
        try:
            if APPKIT_AVAILABLE and self.workspace:
                # Get running applications
                running_apps = self.workspace.runningApplications()
                
                for i, app in enumerate(running_apps):
                    if app.isActive() or not app.isHidden():
                        window_info = self._create_window_info_from_app(app, z_order=i)
                        if window_info:
                            windows.append(window_info)
            
            # If no windows found, use fallback
            if not windows:
                windows = self._get_window_list_fallback()
            
            return windows
            
        except Exception as e:
            logger.error(f"Failed to get window list: {e}")
            return self._get_window_list_fallback()
    
    def get_window_at_point(self, x: int, y: int) -> Optional[WindowInfo]:
        """Get window at point using screen coordinates."""
        try:
            # Use system command to find window at point
            result = subprocess.run([
                "python3", "-c",
                f"""
import Quartz
point = Quartz.CGPointMake({x}, {y})
window_list = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
for window in window_list:
    bounds = window.get('kCGWindowBounds', {{}})
    if bounds:
        wx, wy, ww, wh = bounds['X'], bounds['Y'], bounds['Width'], bounds['Height']
        if wx <= {x} <= wx + ww and wy <= {y} <= wy + wh:
            print(f"{{window.get('kCGWindowOwnerName', 'Unknown')}},{{window.get('kCGWindowNumber', 0)}}")
            break
                """
            ], capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(',')
                if len(parts) == 2:
                    app_name, window_id = parts
                    return WindowInfo(
                        window_id=window_id,
                        title=f"{app_name} Window",
                        process_name=app_name,
                        process_id=0,
                        bounds=(x-100, y-100, 200, 200),  # Approximate
                        is_visible=True
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get window at point ({x}, {y}): {e}")
            return None
    
    def focus_window(self, window_id: str) -> bool:
        """Focus window by ID."""
        try:
            if APPKIT_AVAILABLE and self.workspace:
                # Find application by window ID or process name
                running_apps = self.workspace.runningApplications()
                
                for app in running_apps:
                    if (str(app.processIdentifier()) == window_id or 
                        app.localizedName() == window_id):
                        return app.activateWithOptions_(0)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to focus window {window_id}: {e}")
            return False
    
    def get_window_screenshot(self, window_id: str) -> Optional[bytes]:
        """Take screenshot of window."""
        try:
            # Use screencapture utility for window screenshot
            result = subprocess.run([
                "screencapture", "-w", "-x", "-t", "png", "/dev/stdout"
            ], capture_output=True, timeout=5)
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"screencapture failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to screenshot window {window_id}: {e}")
            return None
    
    def _create_window_info_from_app(self, app, is_active: bool = False, z_order: int = 0) -> Optional[WindowInfo]:
        """Create WindowInfo from NSRunningApplication."""
        try:
            # Get basic app info
            app_name = app.localizedName() or "Unknown"
            process_id = app.processIdentifier()
            
            # Create window info
            return WindowInfo(
                window_id=str(process_id),
                title=f"{app_name} Window",
                process_name=app_name,
                process_id=process_id,
                bounds=(100, 100, 800, 600),  # Default bounds - real implementation would get actual bounds
                is_visible=not app.isHidden(),
                is_minimized=app.isHidden(),
                is_active=is_active,
                z_order=z_order
            )
            
        except Exception as e:
            logger.error(f"Failed to create window info from app: {e}")
            return None
    
    def _get_active_window_fallback(self) -> Optional[WindowInfo]:
        """Fallback method to get active window using shell commands."""
        try:
            # Use AppleScript to get frontmost application
            result = subprocess.run([
                "osascript", "-e", 
                'tell application "System Events" to get name of first process whose frontmost is true'
            ], capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                app_name = result.stdout.strip()
                return WindowInfo(
                    window_id="active",
                    title=f"{app_name} Window",
                    process_name=app_name,
                    process_id=0,
                    bounds=(100, 100, 800, 600),
                    is_active=True,
                    is_visible=True
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Fallback active window detection failed: {e}")
            return None
    
    def _get_window_list_fallback(self) -> List[WindowInfo]:
        """Fallback method to get window list."""
        try:
            # Use ps to get running processes
            result = subprocess.run([
                "ps", "-eo", "pid,comm", "-c"
            ], capture_output=True, text=True, timeout=5)
            
            windows = []
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for i, line in enumerate(lines[:10]):  # Limit to 10 processes
                    parts = line.strip().split(None, 1)
                    if len(parts) == 2:
                        pid, name = parts
                        windows.append(WindowInfo(
                            window_id=pid,
                            title=f"{name} Window",
                            process_name=name,
                            process_id=int(pid),
                            bounds=(50 + i*20, 50 + i*20, 600, 400),
                            is_visible=True,
                            z_order=i
                        ))
            
            return windows
            
        except Exception as e:
            logger.error(f"Fallback window list failed: {e}")
            return []


class WindowsWindowManager(WindowManager):
    """Windows-specific window manager using Win32 API."""
    
    def __init__(self):
        if not WIN32_AVAILABLE:
            logger.warning("Win32 API not available on this platform")
    
    def get_active_window(self) -> Optional[WindowInfo]:
        """Get active window using Win32 API."""
        if not WIN32_AVAILABLE:
            return None
        
        try:
            hwnd = win32gui.GetForegroundWindow()
            return self._create_window_info_from_hwnd(hwnd, is_active=True)
            
        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            return None
    
    def get_window_list(self) -> List[WindowInfo]:
        """Get window list using Win32 API."""
        if not WIN32_AVAILABLE:
            return []
        
        windows = []
        
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_info = self._create_window_info_from_hwnd(hwnd)
                if window_info and window_info.title:
                    windows.append(window_info)
            return True
        
        try:
            win32gui.EnumWindows(enum_windows_callback, windows)
            return windows
            
        except Exception as e:
            logger.error(f"Failed to get window list: {e}")
            return []
    
    def get_window_at_point(self, x: int, y: int) -> Optional[WindowInfo]:
        """Get window at point using Win32 API."""
        if not WIN32_AVAILABLE:
            return None
        
        try:
            hwnd = win32gui.WindowFromPoint((x, y))
            return self._create_window_info_from_hwnd(hwnd)
            
        except Exception as e:
            logger.error(f"Failed to get window at point ({x}, {y}): {e}")
            return None
    
    def focus_window(self, window_id: str) -> bool:
        """Focus window by HWND."""
        if not WIN32_AVAILABLE:
            return False
        
        try:
            hwnd = int(window_id)
            win32gui.SetForegroundWindow(hwnd)
            return True
            
        except Exception as e:
            logger.error(f"Failed to focus window {window_id}: {e}")
            return False
    
    def get_window_screenshot(self, window_id: str) -> Optional[bytes]:
        """Take screenshot of window using Win32 API."""
        # Implementation would use Win32 API to capture window
        # For now, return None as placeholder
        return None
    
    def _create_window_info_from_hwnd(self, hwnd: int, is_active: bool = False) -> Optional[WindowInfo]:
        """Create WindowInfo from window handle."""
        try:
            # Get window title
            title = win32gui.GetWindowText(hwnd)
            
            # Get window bounds
            rect = win32gui.GetWindowRect(hwnd)
            bounds = (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
            
            # Get process info
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            
            return WindowInfo(
                window_id=str(hwnd),
                title=title,
                process_name="Unknown",  # Would get from process ID
                process_id=process_id,
                bounds=bounds,
                is_visible=win32gui.IsWindowVisible(hwnd),
                is_minimized=win32gui.IsIconic(hwnd),
                is_active=is_active
            )
            
        except Exception as e:
            logger.error(f"Failed to create window info from HWND {hwnd}: {e}")
            return None


class LinuxWindowManager(WindowManager):
    """Linux window manager using X11/Wayland utilities."""
    
    def get_active_window(self) -> Optional[WindowInfo]:
        """Get active window using xprop."""
        try:
            result = subprocess.run([
                "xprop", "-root", "_NET_ACTIVE_WINDOW"
            ], capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                # Parse window ID from output
                output = result.stdout.strip()
                if "window id" in output:
                    window_id = output.split()[-1]
                    return self._get_window_info_by_id(window_id, is_active=True)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            return None
    
    def get_window_list(self) -> List[WindowInfo]:
        """Get window list using wmctrl."""
        windows = []
        
        try:
            result = subprocess.run([
                "wmctrl", "-l"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    parts = line.split(None, 3)
                    if len(parts) >= 4:
                        window_id, desktop, host, title = parts
                        windows.append(WindowInfo(
                            window_id=window_id,
                            title=title,
                            process_name="Unknown",
                            process_id=0,
                            bounds=(0, 0, 800, 600),  # Would get actual bounds
                            is_visible=True
                        ))
            
            return windows
            
        except Exception as e:
            logger.error(f"Failed to get window list: {e}")
            return []
    
    def get_window_at_point(self, x: int, y: int) -> Optional[WindowInfo]:
        """Get window at point using xwininfo."""
        try:
            result = subprocess.run([
                "xwininfo", "-int", "-root", "-tree"
            ], capture_output=True, text=True, timeout=5)
            
            # Parse output to find window at coordinates
            # This is a simplified implementation
            return None
            
        except Exception as e:
            logger.error(f"Failed to get window at point ({x}, {y}): {e}")
            return None
    
    def focus_window(self, window_id: str) -> bool:
        """Focus window using wmctrl."""
        try:
            result = subprocess.run([
                "wmctrl", "-i", "-a", window_id
            ], capture_output=True, timeout=3)
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Failed to focus window {window_id}: {e}")
            return False
    
    def get_window_screenshot(self, window_id: str) -> Optional[bytes]:
        """Take window screenshot using import command."""
        try:
            result = subprocess.run([
                "import", "-window", window_id, "png:-"
            ], capture_output=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to screenshot window {window_id}: {e}")
            return None
    
    def _get_window_info_by_id(self, window_id: str, is_active: bool = False) -> Optional[WindowInfo]:
        """Get window information by ID using xprop."""
        try:
            result = subprocess.run([
                "xprop", "-id", window_id
            ], capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                # Parse xprop output for window properties
                title = "Unknown Window"
                for line in result.stdout.split('\n'):
                    if "_NET_WM_NAME" in line or "WM_NAME" in line:
                        # Extract title from line
                        if '"' in line:
                            title = line.split('"')[1]
                        break
                
                return WindowInfo(
                    window_id=window_id,
                    title=title,
                    process_name="Unknown",
                    process_id=0,
                    bounds=(0, 0, 800, 600),
                    is_active=is_active,
                    is_visible=True
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get window info for {window_id}: {e}")
            return None


def create_window_manager() -> WindowManager:
    """Create platform-appropriate window manager."""
    system = platform.system()
    
    if system == "Darwin":
        return MacOSWindowManager()
    elif system == "Windows":
        return WindowsWindowManager()
    elif system == "Linux":
        return LinuxWindowManager()
    else:
        logger.error(f"Unsupported platform: {system}")
        return MacOSWindowManager()  # Fallback