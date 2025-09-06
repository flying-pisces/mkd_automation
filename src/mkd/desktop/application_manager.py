"""
Application management for desktop automation.
"""
import os
import subprocess
import psutil
import logging
import platform
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class ApplicationManager:
    """
    Manages applications and processes for desktop automation.
    
    Provides functionality for:
    - Launching applications
    - Managing running processes
    - Finding and interacting with applications
    - System service management
    """
    
    def __init__(self):
        """Initialize application manager."""
        self.platform = platform.system()
        self._common_apps = self._get_common_applications()
        
    def _get_common_applications(self) -> Dict[str, Dict[str, Any]]:
        """Get dictionary of common applications and their launch info."""
        if self.platform == "Windows":
            return {
                'notepad': {'command': 'notepad.exe', 'name': 'Notepad'},
                'calculator': {'command': 'calc.exe', 'name': 'Calculator'},
                'paint': {'command': 'mspaint.exe', 'name': 'Paint'},
                'wordpad': {'command': 'wordpad.exe', 'name': 'WordPad'},
                'cmd': {'command': 'cmd.exe', 'name': 'Command Prompt'},
                'powershell': {'command': 'powershell.exe', 'name': 'PowerShell'},
                'explorer': {'command': 'explorer.exe', 'name': 'File Explorer'},
                'chrome': {'command': 'chrome.exe', 'name': 'Google Chrome', 'paths': [
                    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
                ]},
                'firefox': {'command': 'firefox.exe', 'name': 'Firefox', 'paths': [
                    r'C:\Program Files\Mozilla Firefox\firefox.exe',
                    r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'
                ]},
                'edge': {'command': 'msedge.exe', 'name': 'Microsoft Edge'},
                'vscode': {'command': 'code.exe', 'name': 'Visual Studio Code', 'paths': [
                    r'C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe',
                    r'C:\Program Files\Microsoft VS Code\Code.exe'
                ]},
                'discord': {'command': 'Discord.exe', 'name': 'Discord'},
                'spotify': {'command': 'Spotify.exe', 'name': 'Spotify'},
                'teams': {'command': 'Teams.exe', 'name': 'Microsoft Teams'},
                'outlook': {'command': 'OUTLOOK.EXE', 'name': 'Microsoft Outlook'},
                'excel': {'command': 'EXCEL.EXE', 'name': 'Microsoft Excel'},
                'word': {'command': 'WINWORD.EXE', 'name': 'Microsoft Word'},
                'powerpoint': {'command': 'POWERPNT.EXE', 'name': 'Microsoft PowerPoint'},
            }
        elif self.platform == "Darwin":
            return {
                'safari': {'command': 'Safari', 'name': 'Safari'},
                'chrome': {'command': 'Google Chrome', 'name': 'Google Chrome'},
                'firefox': {'command': 'Firefox', 'name': 'Firefox'},
                'finder': {'command': 'Finder', 'name': 'Finder'},
                'terminal': {'command': 'Terminal', 'name': 'Terminal'},
                'textedit': {'command': 'TextEdit', 'name': 'TextEdit'},
                'calculator': {'command': 'Calculator', 'name': 'Calculator'},
                'vscode': {'command': 'Visual Studio Code', 'name': 'Visual Studio Code'},
            }
        else:  # Linux
            return {
                'firefox': {'command': 'firefox', 'name': 'Firefox'},
                'chrome': {'command': 'google-chrome', 'name': 'Google Chrome'},
                'nautilus': {'command': 'nautilus', 'name': 'Files'},
                'terminal': {'command': 'gnome-terminal', 'name': 'Terminal'},
                'gedit': {'command': 'gedit', 'name': 'Text Editor'},
                'calculator': {'command': 'gnome-calculator', 'name': 'Calculator'},
                'vscode': {'command': 'code', 'name': 'Visual Studio Code'},
            }
            
    def launch_application(self, app_identifier: str, args: List[str] = None, 
                          wait_for_window: bool = True) -> Optional[Dict[str, Any]]:
        """
        Launch an application.
        
        Args:
            app_identifier: App name, command, or path
            args: Command line arguments
            wait_for_window: Whether to wait for the app window to appear
            
        Returns:
            Dictionary with process information
        """
        try:
            args = args or []
            
            # Check if it's a known app
            app_info = self._common_apps.get(app_identifier.lower())
            
            if app_info:
                command = self._find_application_path(app_info)
                if not command:
                    logger.error(f"Could not find application: {app_identifier}")
                    return None
            else:
                command = app_identifier
                
            # Launch the application
            if self.platform == "Windows":
                if Path(command).exists():
                    # Full path provided
                    process = subprocess.Popen([command] + args)
                else:
                    # Command name - let Windows find it
                    process = subprocess.Popen([command] + args, shell=True)
            elif self.platform == "Darwin":
                if app_info and 'command' in app_info:
                    # macOS app name
                    cmd = ['open', '-a', command]
                    if args:
                        cmd.extend(['--args'] + args)
                    process = subprocess.Popen(cmd)
                else:
                    process = subprocess.Popen([command] + args)
            else:  # Linux
                process = subprocess.Popen([command] + args)
                
            # Wait a moment for the process to start
            time.sleep(1)
            
            result = {
                'pid': process.pid,
                'command': command,
                'args': args,
                'process': process
            }
            
            if wait_for_window:
                # Wait for window to appear (simple implementation)
                time.sleep(2)
                
            logger.info(f"Launched application: {app_identifier} (PID: {process.pid})")
            return result
            
        except Exception as e:
            logger.error(f"Error launching application {app_identifier}: {e}")
            return None
            
    def _find_application_path(self, app_info: Dict[str, Any]) -> Optional[str]:
        """Find the actual path to an application."""
        command = app_info['command']
        
        # Try common paths if provided
        if 'paths' in app_info:
            for path in app_info['paths']:
                # Replace {username} placeholder
                if '{username}' in path:
                    import getpass
                    path = path.format(username=getpass.getuser())
                    
                if Path(path).exists():
                    return path
                    
        # Try the command as-is
        return command
        
    def find_application_windows(self, app_name: str = None, pid: int = None) -> List[Dict[str, Any]]:
        """
        Find windows belonging to an application.
        
        Args:
            app_name: Application name to search for
            pid: Process ID to search for
            
        Returns:
            List of window information dictionaries
        """
        # This would integrate with the Windows automation module
        from .windows_automation import WindowsDesktopAutomation
        
        if self.platform == "Windows":
            win_automation = WindowsDesktopAutomation()
            windows = win_automation.get_window_list()
            
            if app_name:
                # Filter by application name in title
                windows = [w for w in windows if app_name.lower() in w['title'].lower()]
                
            if pid:
                # Filter by process ID
                windows = [w for w in windows if w['pid'] == pid]
                
            return windows
        else:
            # For other platforms, return empty list for now
            return []
            
    def get_running_applications(self) -> List[Dict[str, Any]]:
        """Get list of running applications."""
        applications = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'create_time', 'memory_info']):
            try:
                proc_info = proc.info
                
                # Skip system processes
                if not proc_info['name'] or proc_info['name'].startswith('System'):
                    continue
                    
                app_info = {
                    'pid': proc_info['pid'],
                    'name': proc_info['name'],
                    'exe': proc_info['exe'],
                    'cmdline': ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else '',
                    'create_time': proc_info['create_time'],
                    'memory_mb': round(proc_info['memory_info'].rss / 1024 / 1024, 1) if proc_info['memory_info'] else 0
                }
                
                applications.append(app_info)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        return sorted(applications, key=lambda x: x['memory_mb'], reverse=True)
        
    def close_application(self, identifier: str = None, pid: int = None, force: bool = False) -> bool:
        """
        Close an application.
        
        Args:
            identifier: Application name or window title
            pid: Process ID
            force: Whether to force kill the process
            
        Returns:
            Success status
        """
        try:
            processes_to_close = []
            
            if pid:
                # Close by PID
                processes_to_close.append(pid)
            elif identifier:
                # Find processes by name
                for proc in psutil.process_iter(['pid', 'name', 'exe']):
                    try:
                        if (identifier.lower() in proc.info['name'].lower() or 
                            (proc.info['exe'] and identifier.lower() in Path(proc.info['exe']).name.lower())):
                            processes_to_close.append(proc.info['pid'])
                    except:
                        pass
                        
            if not processes_to_close:
                logger.error(f"No processes found matching: {identifier or pid}")
                return False
                
            # Close the processes
            for pid in processes_to_close:
                try:
                    process = psutil.Process(pid)
                    
                    if force:
                        process.kill()
                    else:
                        process.terminate()
                        
                    # Wait for process to close
                    process.wait(timeout=5)
                    logger.info(f"Closed process: {pid}")
                    
                except psutil.TimeoutExpired:
                    if not force:
                        # Try to force kill if terminate didn't work
                        try:
                            process.kill()
                            process.wait(timeout=5)
                            logger.info(f"Force killed process: {pid}")
                        except:
                            logger.error(f"Failed to kill process: {pid}")
                            return False
                except psutil.NoSuchProcess:
                    # Process already closed
                    pass
                    
            return True
            
        except Exception as e:
            logger.error(f"Error closing application: {e}")
            return False
            
    def is_application_running(self, app_name: str) -> bool:
        """Check if an application is running."""
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                if (app_name.lower() in proc.info['name'].lower() or 
                    (proc.info['exe'] and app_name.lower() in Path(proc.info['exe']).name.lower())):
                    return True
            except:
                pass
                
        return False
        
    def get_application_info(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific application."""
        app_info = self._common_apps.get(app_name.lower())
        
        if app_info:
            # Add runtime information
            is_running = self.is_application_running(app_name)
            path = self._find_application_path(app_info)
            
            return {
                'name': app_info['name'],
                'command': app_info['command'],
                'path': path,
                'is_running': is_running,
                'is_available': path is not None or app_info['command'] in os.environ.get('PATH', '')
            }
            
        return None
        
    def restart_application(self, app_name: str, args: List[str] = None) -> Optional[Dict[str, Any]]:
        """Restart an application."""
        # Close if running
        if self.is_application_running(app_name):
            self.close_application(app_name)
            time.sleep(2)  # Wait for cleanup
            
        # Relaunch
        return self.launch_application(app_name, args)
        
    def get_system_services(self) -> List[Dict[str, Any]]:
        """Get list of system services (Windows only for now)."""
        if self.platform != "Windows":
            return []
            
        try:
            import win32service
            import win32serviceutil
            
            services = []
            service_list = win32service.EnumServicesStatus(
                win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE),
                win32service.SERVICE_WIN32,
                win32service.SERVICE_STATE_ALL
            )
            
            for service in service_list:
                service_name = service[0]
                display_name = service[1]
                status = service[2]
                
                services.append({
                    'name': service_name,
                    'display_name': display_name,
                    'status': status[1],  # Current state
                    'can_stop': bool(status[2] & win32service.SERVICE_ACCEPT_STOP),
                    'can_pause': bool(status[2] & win32service.SERVICE_ACCEPT_PAUSE_CONTINUE)
                })
                
            return services
            
        except ImportError:
            logger.error("Windows service management requires pywin32")
            return []
        except Exception as e:
            logger.error(f"Error getting system services: {e}")
            return []