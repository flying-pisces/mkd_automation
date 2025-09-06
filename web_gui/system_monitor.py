#!/usr/bin/env python3
"""
System-Level Task Monitor for MKD Automation

This module monitors system-level activities including:
- Process creation/termination
- Window focus changes 
- Application launches
- Task Manager interactions
- System commands (Ctrl+Alt combinations)
- File system operations

Correlates low-level mouse/keyboard actions with high-level system operations.
"""

import asyncio
import json
import logging
import os
import sys
import time
import threading
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

# Windows-specific imports
if sys.platform == 'win32':
    import win32gui
    import win32process
    import win32con
    import win32api
    import win32event
    import wmi
    import psutil
    from win32com.client import GetObject

logger = logging.getLogger(__name__)

@dataclass
class SystemEvent:
    """Represents a system-level event"""
    timestamp: float
    event_type: str  # 'process_start', 'process_end', 'window_focus', 'hotkey', etc.
    process_name: str
    process_id: int
    window_title: str = ""
    executable_path: str = ""
    command_line: str = ""
    parent_process: str = ""
    semantic_action: str = ""  # High-level meaning
    related_files: List[str] = None
    system_impact: str = ""  # What this action accomplished
    
    def __post_init__(self):
        if self.related_files is None:
            self.related_files = []

@dataclass
class ApplicationContext:
    """Context about currently active applications"""
    active_window: str
    active_process: str
    process_id: int
    window_handle: int
    executable_path: str
    working_directory: str = ""
    open_files: List[str] = None
    
    def __post_init__(self):
        if self.open_files is None:
            self.open_files = []

class SystemMonitor:
    """Monitors system-level activities and correlates with user actions"""
    
    def __init__(self):
        self.is_monitoring = False
        self.events: List[SystemEvent] = []
        self.current_context = None
        self.process_watcher = None
        self.window_watcher = None
        self.hotkey_watcher = None
        
        # System monitoring components
        if sys.platform == 'win32':
            self.wmi = wmi.WMI()
            self.setup_windows_monitoring()
        
        # Known application signatures
        self.app_signatures = {
            'chrome.exe': 'Web Browser',
            'firefox.exe': 'Web Browser', 
            'msedge.exe': 'Web Browser',
            'notepad.exe': 'Text Editor',
            'calc.exe': 'Calculator',
            'taskmgr.exe': 'Task Manager',
            'explorer.exe': 'File Explorer',
            'cmd.exe': 'Command Prompt',
            'powershell.exe': 'PowerShell',
            'code.exe': 'Visual Studio Code',
            'winword.exe': 'Microsoft Word',
            'excel.exe': 'Microsoft Excel',
            'outlook.exe': 'Microsoft Outlook'
        }
        
        # Hotkey combinations and their meanings
        self.hotkey_meanings = {
            ('ctrl', 'alt', 'd'): 'Show Desktop',
            ('ctrl', 'alt', 'del'): 'Security Screen',
            ('ctrl', 'shift', 'esc'): 'Task Manager',
            ('win', 'r'): 'Run Dialog',
            ('win', 'e'): 'File Explorer',
            ('win', 'l'): 'Lock Screen',
            ('alt', 'tab'): 'Application Switcher',
            ('alt', 'f4'): 'Close Application',
            ('ctrl', 'c'): 'Copy',
            ('ctrl', 'v'): 'Paste',
            ('ctrl', 'x'): 'Cut',
            ('ctrl', 'z'): 'Undo',
            ('ctrl', 'y'): 'Redo',
            ('ctrl', 's'): 'Save',
            ('ctrl', 'o'): 'Open File',
            ('ctrl', 'n'): 'New Document/Window'
        }
        
        logger.info("System Monitor initialized")
    
    def setup_windows_monitoring(self):
        """Setup Windows-specific monitoring"""
        try:
            # Setup WMI event watchers
            self.setup_process_watcher()
            self.setup_window_watcher()
            logger.info("Windows monitoring setup complete")
        except Exception as e:
            logger.error(f"Failed to setup Windows monitoring: {e}")
    
    def setup_process_watcher(self):
        """Setup process creation/termination monitoring"""
        try:
            # Monitor process creation
            self.process_start_watcher = self.wmi.Win32_Process.watch_for("creation")
            self.process_end_watcher = self.wmi.Win32_Process.watch_for("deletion")
            logger.info("Process watchers configured")
        except Exception as e:
            logger.error(f"Failed to setup process watchers: {e}")
    
    def setup_window_watcher(self):
        """Setup window focus change monitoring"""
        try:
            # We'll poll for active window changes instead of hooking
            # This is more reliable across different Windows versions
            self.current_window = self.get_active_window_info()
            logger.info("Window monitoring configured")
        except Exception as e:
            logger.error(f"Failed to setup window monitoring: {e}")
    
    def get_active_window_info(self) -> Optional[ApplicationContext]:
        """Get information about the currently active window"""
        try:
            if sys.platform != 'win32':
                return None
            
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None
            
            window_title = win32gui.GetWindowText(hwnd)
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            
            try:
                process = psutil.Process(process_id)
                process_name = process.name()
                executable_path = process.exe()
                working_dir = process.cwd() if process.is_running() else ""
                
                return ApplicationContext(
                    active_window=window_title,
                    active_process=process_name,
                    process_id=process_id,
                    window_handle=hwnd,
                    executable_path=executable_path,
                    working_directory=working_dir
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return None
                
        except Exception as e:
            logger.error(f"Error getting active window info: {e}")
            return None
    
    async def start_monitoring(self):
        """Start system monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.events = []
        
        logger.info("Starting system monitoring")
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self.monitor_processes()),
            asyncio.create_task(self.monitor_windows()),
            asyncio.create_task(self.monitor_system_state())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("System monitoring cancelled")
        except Exception as e:
            logger.error(f"Error in system monitoring: {e}")
    
    async def stop_monitoring(self):
        """Stop system monitoring"""
        self.is_monitoring = False
        logger.info("Stopping system monitoring")
    
    async def monitor_processes(self):
        """Monitor process creation and termination"""
        while self.is_monitoring:
            try:
                if sys.platform == 'win32' and hasattr(self, 'process_start_watcher'):
                    # Check for new processes
                    try:
                        new_process = self.process_start_watcher(timeout_ms=100)
                        if new_process:
                            await self.handle_process_start(new_process)
                    except Exception:
                        pass  # Timeout is expected
                    
                    # Check for ended processes  
                    try:
                        ended_process = self.process_end_watcher(timeout_ms=100)
                        if ended_process:
                            await self.handle_process_end(ended_process)
                    except Exception:
                        pass  # Timeout is expected
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in process monitoring: {e}")
                await asyncio.sleep(1)
    
    async def monitor_windows(self):
        """Monitor active window changes"""
        while self.is_monitoring:
            try:
                current_window = self.get_active_window_info()
                
                if current_window and (
                    not self.current_context or 
                    current_window.window_handle != self.current_context.window_handle
                ):
                    await self.handle_window_change(current_window)
                    self.current_context = current_window
                
                await asyncio.sleep(0.2)  # Check every 200ms
                
            except Exception as e:
                logger.error(f"Error in window monitoring: {e}")
                await asyncio.sleep(1)
    
    async def monitor_system_state(self):
        """Monitor overall system state and performance"""
        while self.is_monitoring:
            try:
                # Log periodic system state
                cpu_usage = psutil.cpu_percent()
                memory_usage = psutil.virtual_memory().percent
                
                # Log high CPU/memory events
                if cpu_usage > 80 or memory_usage > 85:
                    event = SystemEvent(
                        timestamp=time.time(),
                        event_type='system_stress',
                        process_name='system',
                        process_id=0,
                        semantic_action=f'High resource usage: CPU {cpu_usage}%, Memory {memory_usage}%',
                        system_impact='System performance impact detected'
                    )
                    self.events.append(event)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in system state monitoring: {e}")
                await asyncio.sleep(5)
    
    async def handle_process_start(self, process_info):
        """Handle new process creation"""
        try:
            process_name = process_info.Name
            process_id = process_info.ProcessId
            command_line = getattr(process_info, 'CommandLine', '') or ''
            
            # Get parent process info
            parent_id = getattr(process_info, 'ParentProcessId', 0)
            parent_name = ""
            try:
                if parent_id:
                    parent_process = psutil.Process(parent_id)
                    parent_name = parent_process.name()
            except:
                pass
            
            # Determine semantic action
            semantic_action = self.analyze_process_launch(process_name, command_line, parent_name)
            
            event = SystemEvent(
                timestamp=time.time(),
                event_type='process_start',
                process_name=process_name,
                process_id=process_id,
                command_line=command_line,
                parent_process=parent_name,
                semantic_action=semantic_action,
                system_impact=f'Launched {self.app_signatures.get(process_name.lower(), process_name)}'
            )
            
            self.events.append(event)
            logger.info(f"Process started: {process_name} (PID: {process_id}) - {semantic_action}")
            
        except Exception as e:
            logger.error(f"Error handling process start: {e}")
    
    async def handle_process_end(self, process_info):
        """Handle process termination"""
        try:
            process_name = process_info.Name
            process_id = process_info.ProcessId
            
            event = SystemEvent(
                timestamp=time.time(),
                event_type='process_end',
                process_name=process_name,
                process_id=process_id,
                semantic_action=f'Closed {self.app_signatures.get(process_name.lower(), process_name)}',
                system_impact=f'Application {process_name} terminated'
            )
            
            self.events.append(event)
            logger.info(f"Process ended: {process_name} (PID: {process_id})")
            
        except Exception as e:
            logger.error(f"Error handling process end: {e}")
    
    async def handle_window_change(self, window_context: ApplicationContext):
        """Handle active window change"""
        try:
            semantic_action = f"Switched to {self.app_signatures.get(window_context.active_process.lower(), window_context.active_process)}"
            if window_context.active_window:
                semantic_action += f": {window_context.active_window}"
            
            event = SystemEvent(
                timestamp=time.time(),
                event_type='window_focus',
                process_name=window_context.active_process,
                process_id=window_context.process_id,
                window_title=window_context.active_window,
                executable_path=window_context.executable_path,
                semantic_action=semantic_action,
                system_impact=f'User focused on {window_context.active_process}'
            )
            
            self.events.append(event)
            logger.info(f"Window focus: {window_context.active_process} - {window_context.active_window}")
            
        except Exception as e:
            logger.error(f"Error handling window change: {e}")
    
    def analyze_process_launch(self, process_name: str, command_line: str, parent_name: str) -> str:
        """Analyze the semantic meaning of a process launch"""
        process_lower = process_name.lower()
        
        # Browser launches
        if process_lower in ['chrome.exe', 'firefox.exe', 'msedge.exe']:
            if 'incognito' in command_line.lower() or 'private' in command_line.lower():
                return 'Opened web browser in private mode'
            return 'Opened web browser'
        
        # System tools
        if process_lower == 'taskmgr.exe':
            return 'Opened Task Manager to monitor system processes'
        elif process_lower == 'calc.exe':
            return 'Opened Calculator for calculations'
        elif process_lower == 'notepad.exe':
            return 'Opened Notepad for text editing'
        elif process_lower == 'cmd.exe':
            return 'Opened Command Prompt for system commands'
        elif process_lower == 'powershell.exe':
            return 'Opened PowerShell for advanced system operations'
        
        # Office applications
        elif process_lower == 'winword.exe':
            return 'Opened Microsoft Word for document editing'
        elif process_lower == 'excel.exe':
            return 'Opened Microsoft Excel for spreadsheet work'
        elif process_lower == 'outlook.exe':
            return 'Opened Microsoft Outlook for email management'
        
        # Development tools
        elif process_lower == 'code.exe':
            return 'Opened Visual Studio Code for programming'
        elif process_lower == 'devenv.exe':
            return 'Opened Visual Studio for development'
        
        # File operations
        elif process_lower == 'explorer.exe' and parent_name != 'explorer.exe':
            return 'Opened File Explorer for file management'
        
        # Default analysis
        app_type = self.app_signatures.get(process_lower, 'Application')
        return f'Launched {app_type}'
    
    def analyze_hotkey_combination(self, keys: List[str]) -> Optional[str]:
        """Analyze hotkey combination meaning"""
        # Normalize keys
        normalized = tuple(sorted([key.lower().strip() for key in keys]))
        
        # Check against known combinations
        for combo, meaning in self.hotkey_meanings.items():
            if set(normalized) == set(combo):
                return meaning
        
        return None
    
    def correlate_with_user_action(self, user_action: Dict[str, Any]) -> Optional[SystemEvent]:
        """Correlate user action with system events"""
        action_timestamp = user_action.get('timestamp', 0)
        action_type = user_action.get('type', '')
        
        # Look for system events within 2 seconds of user action
        time_window = 2.0
        related_events = [
            event for event in self.events
            if abs(event.timestamp - action_timestamp) <= time_window
        ]
        
        if not related_events:
            return None
        
        # Find most relevant event
        if action_type == 'key_down' and len(related_events) > 0:
            # Check if this was part of a hotkey that triggered something
            return related_events[-1]  # Most recent event
        elif action_type == 'mouse_down':
            # Check if click resulted in process launch or window change
            for event in related_events:
                if event.event_type in ['process_start', 'window_focus']:
                    return event
        
        return None
    
    def get_semantic_summary(self) -> Dict[str, Any]:
        """Get semantic summary of recorded session"""
        if not self.events:
            return {}
        
        # Categorize events
        processes_launched = [e for e in self.events if e.event_type == 'process_start']
        windows_used = [e for e in self.events if e.event_type == 'window_focus']
        applications = set(e.process_name for e in self.events)
        
        # Generate narrative
        narrative = []
        if processes_launched:
            apps = [self.app_signatures.get(p.process_name.lower(), p.process_name) 
                   for p in processes_launched]
            narrative.append(f"Launched applications: {', '.join(set(apps))}")
        
        if windows_used:
            unique_windows = set((e.process_name, e.window_title) for e in windows_used)
            narrative.append(f"Worked with {len(unique_windows)} different windows")
        
        return {
            'total_events': len(self.events),
            'processes_launched': len(processes_launched),
            'applications_used': list(applications),
            'session_narrative': '. '.join(narrative),
            'timeline': [asdict(event) for event in self.events],
            'start_time': min(e.timestamp for e in self.events) if self.events else 0,
            'end_time': max(e.timestamp for e in self.events) if self.events else 0
        }
    
    def get_events_json(self) -> str:
        """Get all events as JSON"""
        return json.dumps([asdict(event) for event in self.events], indent=2, default=str)
    
    def clear_events(self):
        """Clear all recorded events"""
        self.events = []
        logger.info("System events cleared")

# Task Manager Integration
class TaskManagerController:
    """Controls Task Manager for system analysis"""
    
    def __init__(self):
        self.task_manager_pid = None
    
    async def launch_task_manager(self) -> bool:
        """Launch Task Manager"""
        try:
            if sys.platform == 'win32':
                process = subprocess.Popen(['taskmgr.exe'])
                self.task_manager_pid = process.pid
                logger.info(f"Task Manager launched (PID: {self.task_manager_pid})")
                return True
        except Exception as e:
            logger.error(f"Failed to launch Task Manager: {e}")
        return False
    
    async def close_task_manager(self):
        """Close Task Manager"""
        try:
            if self.task_manager_pid:
                os.kill(self.task_manager_pid, 9)
                logger.info("Task Manager closed")
        except Exception as e:
            logger.error(f"Failed to close Task Manager: {e}")
    
    def get_process_list(self) -> List[Dict[str, Any]]:
        """Get current process list"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'] or 0,
                    'memory_mb': proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)

if __name__ == "__main__":
    # Test the system monitor
    import asyncio
    
    async def test_monitor():
        monitor = SystemMonitor()
        
        print("Starting system monitoring for 30 seconds...")
        
        # Start monitoring
        monitoring_task = asyncio.create_task(monitor.start_monitoring())
        
        # Let it run for 30 seconds
        await asyncio.sleep(30)
        
        # Stop monitoring
        await monitor.stop_monitoring()
        
        # Print summary
        summary = monitor.get_semantic_summary()
        print(f"\nMonitoring Summary:")
        print(f"Total events: {summary.get('total_events', 0)}")
        print(f"Processes launched: {summary.get('processes_launched', 0)}")
        print(f"Applications used: {summary.get('applications_used', [])}")
        print(f"Session narrative: {summary.get('session_narrative', 'No activity')}")
        
        # Print detailed events
        print(f"\nDetailed events:")
        for event in monitor.events[:10]:  # Show first 10 events
            print(f"  {event.event_type}: {event.semantic_action}")
    
    asyncio.run(test_monitor())