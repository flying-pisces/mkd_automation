"""
Windows-specific desktop automation using native Windows APIs.
"""
import os
import sys
import time
import subprocess
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import Windows-specific modules
try:
    import win32api
    import win32con
    import win32gui
    import win32process
    import win32clipboard
    import psutil
    WINDOWS_APIS_AVAILABLE = True
except ImportError:
    WINDOWS_APIS_AVAILABLE = False
    logger.warning("Windows APIs not available. Install pywin32 for full functionality.")


class WindowsDesktopAutomation:
    """
    Windows-specific desktop automation using native APIs.
    
    Provides advanced Windows functionality including:
    - Window management with Win32 APIs
    - Process control
    - Registry operations  
    - System integration
    - Advanced file operations
    """
    
    def __init__(self):
        """Initialize Windows automation."""
        self.is_available = WINDOWS_APIS_AVAILABLE and sys.platform == "win32"
        
    def open_command_prompt(self, admin: bool = False, path: str = None) -> int:
        """
        Open Command Prompt.
        
        Args:
            admin: Open as administrator
            path: Starting directory
            
        Returns:
            Process ID
        """
        if admin:
            # Open as administrator
            cmd = f'powershell -Command "Start-Process cmd -Verb runAs'
            if path:
                cmd += f' -ArgumentList \'/k cd /d {path}\''
            cmd += '"'
            
            process = subprocess.Popen(cmd, shell=True)
            return process.pid
        else:
            # Regular command prompt
            cmd = ['cmd']
            if path:
                cmd.extend(['/k', f'cd /d {path}'])
                
            process = subprocess.Popen(cmd, cwd=path)
            return process.pid
            
    def open_powershell(self, admin: bool = False, path: str = None) -> int:
        """
        Open PowerShell.
        
        Args:
            admin: Open as administrator
            path: Starting directory
            
        Returns:
            Process ID
        """
        if admin:
            cmd = 'powershell -Command "Start-Process powershell -Verb runAs'
            if path:
                cmd += f' -ArgumentList \'-NoExit -Command "Set-Location \'{path}\'"\''
            cmd += '"'
            
            process = subprocess.Popen(cmd, shell=True)
            return process.pid
        else:
            cmd = ['powershell', '-NoExit']
            if path:
                cmd.extend(['-Command', f'Set-Location "{path}"'])
                
            process = subprocess.Popen(cmd, cwd=path)
            return process.pid
            
    def run_as_admin(self, command: str, args: str = "") -> bool:
        """
        Run command as administrator.
        
        Args:
            command: Command to run
            args: Command arguments
            
        Returns:
            Success status
        """
        try:
            if WINDOWS_APIS_AVAILABLE:
                win32api.ShellExecute(
                    None, 
                    "runas", 
                    command, 
                    args, 
                    None, 
                    win32con.SW_SHOWNORMAL
                )
                return True
            else:
                # Fallback using PowerShell
                cmd = f'powershell -Command "Start-Process {command} -ArgumentList \'{args}\' -Verb runAs"'
                subprocess.run(cmd, shell=True)
                return True
                
        except Exception as e:
            logger.error(f"Failed to run as admin: {e}")
            return False
            
    def get_window_list(self) -> List[Dict[str, Any]]:
        """Get list of all visible windows."""
        windows = []
        
        if not WINDOWS_APIS_AVAILABLE:
            return windows
            
        def enum_window_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:  # Only include windows with titles
                    try:
                        rect = win32gui.GetWindowRect(hwnd)
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        
                        windows.append({
                            'hwnd': hwnd,
                            'title': window_text,
                            'pid': pid,
                            'position': (rect[0], rect[1]),
                            'size': (rect[2] - rect[0], rect[3] - rect[1]),
                            'rect': rect
                        })
                    except:
                        pass
                        
        win32gui.EnumWindows(enum_window_callback, windows)
        return windows
        
    def get_active_window(self) -> Optional[Dict[str, Any]]:
        """Get information about the active window."""
        if not WINDOWS_APIS_AVAILABLE:
            return None
            
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                window_text = win32gui.GetWindowText(hwnd)
                rect = win32gui.GetWindowRect(hwnd)
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                
                return {
                    'hwnd': hwnd,
                    'title': window_text,
                    'pid': pid,
                    'position': (rect[0], rect[1]),
                    'size': (rect[2] - rect[0], rect[3] - rect[1]),
                    'rect': rect
                }
        except Exception as e:
            logger.error(f"Error getting active window: {e}")
            
        return None
        
    def find_window(self, title: str = None, class_name: str = None) -> Optional[int]:
        """Find window by title or class name."""
        if not WINDOWS_APIS_AVAILABLE:
            return None
            
        try:
            hwnd = win32gui.FindWindow(class_name, title)
            return hwnd if hwnd != 0 else None
        except:
            return None
            
    def activate_window(self, hwnd: int) -> bool:
        """Bring window to foreground."""
        if not WINDOWS_APIS_AVAILABLE:
            return False
            
        try:
            win32gui.SetForegroundWindow(hwnd)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            return True
        except Exception as e:
            logger.error(f"Error activating window: {e}")
            return False
            
    def resize_window(self, hwnd: int, width: int, height: int) -> bool:
        """Resize window."""
        if not WINDOWS_APIS_AVAILABLE:
            return False
            
        try:
            win32gui.SetWindowPos(
                hwnd, 0, 0, 0, width, height, 
                win32con.SWP_NOMOVE | win32con.SWP_NOZORDER
            )
            return True
        except Exception as e:
            logger.error(f"Error resizing window: {e}")
            return False
            
    def move_window(self, hwnd: int, x: int, y: int) -> bool:
        """Move window to position."""
        if not WINDOWS_APIS_AVAILABLE:
            return False
            
        try:
            win32gui.SetWindowPos(
                hwnd, 0, x, y, 0, 0,
                win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
            )
            return True
        except Exception as e:
            logger.error(f"Error moving window: {e}")
            return False
            
    def minimize_window(self, hwnd: int) -> bool:
        """Minimize window."""
        if not WINDOWS_APIS_AVAILABLE:
            return False
            
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True
        except Exception as e:
            logger.error(f"Error minimizing window: {e}")
            return False
            
    def maximize_window(self, hwnd: int) -> bool:
        """Maximize window."""
        if not WINDOWS_APIS_AVAILABLE:
            return False
            
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        except Exception as e:
            logger.error(f"Error maximizing window: {e}")
            return False
            
    def close_window(self, hwnd: int) -> bool:
        """Close window."""
        if not WINDOWS_APIS_AVAILABLE:
            return False
            
        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return True
        except Exception as e:
            logger.error(f"Error closing window: {e}")
            return False
            
    def get_process_list(self) -> List[Dict[str, Any]]:
        """Get list of running processes."""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'memory_info', 'cpu_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'exe': proc.info['exe'],
                    'memory': proc.info['memory_info'].rss if proc.info['memory_info'] else 0,
                    'cpu_percent': proc.info['cpu_percent'] or 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        return processes
        
    def kill_process(self, pid: int) -> bool:
        """Kill process by PID."""
        try:
            process = psutil.Process(pid)
            process.terminate()
            process.wait(timeout=5)
            return True
        except (psutil.NoSuchProcess, psutil.TimeoutExpired) as e:
            logger.error(f"Error killing process {pid}: {e}")
            return False
            
    def set_clipboard_text(self, text: str) -> bool:
        """Set clipboard text."""
        if not WINDOWS_APIS_AVAILABLE:
            return False
            
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()
            return True
        except Exception as e:
            logger.error(f"Error setting clipboard: {e}")
            return False
            
    def get_clipboard_text(self) -> Optional[str]:
        """Get clipboard text."""
        if not WINDOWS_APIS_AVAILABLE:
            return None
            
        try:
            win32clipboard.OpenClipboard()
            text = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            return text
        except Exception as e:
            logger.error(f"Error getting clipboard: {e}")
            return None
            
    def open_control_panel(self, applet: str = None) -> bool:
        """Open Control Panel."""
        try:
            if applet:
                subprocess.run(['control', applet], shell=True)
            else:
                subprocess.run(['control'], shell=True)
            return True
        except Exception as e:
            logger.error(f"Error opening control panel: {e}")
            return False
            
    def open_task_manager(self) -> bool:
        """Open Task Manager."""
        try:
            subprocess.run(['taskmgr'], shell=True)
            return True
        except Exception as e:
            logger.error(f"Error opening task manager: {e}")
            return False
            
    def open_device_manager(self) -> bool:
        """Open Device Manager."""
        try:
            subprocess.run(['devmgmt.msc'], shell=True)
            return True
        except Exception as e:
            logger.error(f"Error opening device manager: {e}")
            return False
            
    def open_services(self) -> bool:
        """Open Services."""
        try:
            subprocess.run(['services.msc'], shell=True)
            return True
        except Exception as e:
            logger.error(f"Error opening services: {e}")
            return False
            
    def open_registry_editor(self) -> bool:
        """Open Registry Editor."""
        try:
            subprocess.run(['regedit'], shell=True)
            return True
        except Exception as e:
            logger.error(f"Error opening registry editor: {e}")
            return False
            
    def lock_workstation(self) -> bool:
        """Lock the workstation."""
        try:
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], shell=True)
            return True
        except Exception as e:
            logger.error(f"Error locking workstation: {e}")
            return False
            
    def shutdown_system(self, force: bool = False, timeout: int = 0) -> bool:
        """Shutdown the system."""
        try:
            cmd = ['shutdown', '/s']
            if force:
                cmd.append('/f')
            if timeout > 0:
                cmd.extend(['/t', str(timeout)])
            else:
                cmd.extend(['/t', '0'])
                
            subprocess.run(cmd, shell=True)
            return True
        except Exception as e:
            logger.error(f"Error shutting down system: {e}")
            return False
            
    def restart_system(self, force: bool = False, timeout: int = 0) -> bool:
        """Restart the system."""
        try:
            cmd = ['shutdown', '/r']
            if force:
                cmd.append('/f')
            if timeout > 0:
                cmd.extend(['/t', str(timeout)])
            else:
                cmd.extend(['/t', '0'])
                
            subprocess.run(cmd, shell=True)
            return True
        except Exception as e:
            logger.error(f"Error restarting system: {e}")
            return False