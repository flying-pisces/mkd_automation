"""
Browser Controller and Multi-Tab Manager

Provides comprehensive browser automation and multi-tab coordination:
- Browser session management across multiple instances
- Advanced tab coordination and synchronization
- Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- Window and tab state management
- Browser process monitoring and control
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Set, Tuple
from enum import Enum
import time
import threading
import subprocess
import json
import logging
from collections import defaultdict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class BrowserType(Enum):
    """Supported browser types"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"
    CHROMIUM = "chromium"


class TabState(Enum):
    """Tab states"""
    LOADING = "loading"
    COMPLETE = "complete"
    INTERACTIVE = "interactive"
    CRASHED = "crashed"
    SUSPENDED = "suspended"
    ACTIVE = "active"
    BACKGROUND = "background"


class BrowserCommand(Enum):
    """Browser control commands"""
    NAVIGATE = "navigate"
    REFRESH = "refresh"
    BACK = "back"
    FORWARD = "forward"
    NEW_TAB = "new_tab"
    CLOSE_TAB = "close_tab"
    SWITCH_TAB = "switch_tab"
    EXECUTE_SCRIPT = "execute_script"
    INJECT_CSS = "inject_css"
    GET_COOKIES = "get_cookies"
    SET_COOKIES = "set_cookies"


@dataclass
class TabInfo:
    """Information about a browser tab"""
    tab_id: str
    window_id: str
    url: str
    title: str
    state: TabState
    is_active: bool
    is_pinned: bool
    favicon_url: Optional[str] = None
    load_time: float = 0.0
    last_activity: float = field(default_factory=time.time)
    dom_ready: bool = False
    resources_loaded: bool = False
    javascript_enabled: bool = True
    cookies: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class BrowserWindow:
    """Information about a browser window"""
    window_id: str
    browser_type: BrowserType
    tabs: List[TabInfo]
    active_tab_id: Optional[str]
    position: Dict[str, int]  # x, y, width, height
    is_focused: bool
    is_minimized: bool
    is_maximized: bool
    is_fullscreen: bool
    profile: Optional[str] = None


@dataclass
class BrowserSession:
    """Browser session with multiple windows and tabs"""
    session_id: str
    browser_type: BrowserType
    windows: List[BrowserWindow]
    active_window_id: Optional[str]
    profile_path: Optional[str] = None
    extensions_enabled: bool = True
    devtools_enabled: bool = False
    headless: bool = False
    process_id: Optional[int] = None
    startup_time: float = field(default_factory=time.time)


@dataclass
class CoordinationRule:
    """Rule for coordinating actions across tabs"""
    rule_id: str
    name: str
    trigger_condition: Callable[[TabInfo], bool]
    target_tabs: List[str]  # Tab IDs or patterns
    action: BrowserCommand
    action_params: Dict[str, Any]
    delay: float = 0.0
    enabled: bool = True


@dataclass
class CommandResult:
    """Result of browser command execution"""
    success: bool
    command: BrowserCommand
    target_tab_id: Optional[str]
    result_data: Any = None
    execution_time: float = 0.0
    error_message: Optional[str] = None


class TabManager:
    """Advanced tab management and coordination"""
    
    def __init__(self):
        self.tabs: Dict[str, TabInfo] = {}
        self.coordination_rules: List[CoordinationRule] = []
        self.tab_groups: Dict[str, List[str]] = {}  # group_name -> tab_ids
        self.sync_lock = threading.Lock()
        self.monitoring_active = False
        self.activity_callbacks: List[Callable] = []
    
    def register_tab(self, tab_info: TabInfo) -> None:
        """Register a new tab for management"""
        with self.sync_lock:
            self.tabs[tab_info.tab_id] = tab_info
            logger.debug(f"Registered tab {tab_info.tab_id}: {tab_info.title[:50]}")
    
    def unregister_tab(self, tab_id: str) -> None:
        """Unregister a tab"""
        with self.sync_lock:
            if tab_id in self.tabs:
                del self.tabs[tab_id]
                # Remove from all groups
                for group_tabs in self.tab_groups.values():
                    if tab_id in group_tabs:
                        group_tabs.remove(tab_id)
                logger.debug(f"Unregistered tab {tab_id}")
    
    def update_tab_state(self, tab_id: str, new_state: TabState) -> None:
        """Update tab state"""
        with self.sync_lock:
            if tab_id in self.tabs:
                old_state = self.tabs[tab_id].state
                self.tabs[tab_id].state = new_state
                self.tabs[tab_id].last_activity = time.time()
                
                logger.debug(f"Tab {tab_id} state changed: {old_state.value} -> {new_state.value}")
                
                # Check coordination rules
                self._check_coordination_rules(self.tabs[tab_id])
    
    def create_tab_group(self, group_name: str, tab_ids: List[str]) -> None:
        """Create a group of related tabs"""
        with self.sync_lock:
            self.tab_groups[group_name] = tab_ids.copy()
            logger.info(f"Created tab group '{group_name}' with {len(tab_ids)} tabs")
    
    def coordinate_group_action(self, group_name: str, action: BrowserCommand, 
                               params: Dict[str, Any] = None) -> List[CommandResult]:
        """Execute coordinated action across tab group"""
        params = params or {}
        results = []
        
        if group_name not in self.tab_groups:
            return [CommandResult(False, action, None, error_message=f"Group '{group_name}' not found")]
        
        tab_ids = self.tab_groups[group_name]
        
        for tab_id in tab_ids:
            if tab_id in self.tabs:
                # Execute action on tab (would integrate with browser controller)
                result = self._execute_tab_command(tab_id, action, params)
                results.append(result)
        
        return results
    
    def _check_coordination_rules(self, tab_info: TabInfo) -> None:
        """Check and execute coordination rules for a tab"""
        for rule in self.coordination_rules:
            if rule.enabled and rule.trigger_condition(tab_info):
                logger.info(f"Executing coordination rule: {rule.name}")
                
                # Apply rule to target tabs
                target_tabs = self._resolve_target_tabs(rule.target_tabs, tab_info)
                
                for target_tab_id in target_tabs:
                    if target_tab_id in self.tabs:
                        # Add delay if specified
                        if rule.delay > 0:
                            threading.Timer(rule.delay, 
                                          lambda: self._execute_tab_command(target_tab_id, rule.action, rule.action_params)
                                          ).start()
                        else:
                            self._execute_tab_command(target_tab_id, rule.action, rule.action_params)
    
    def _resolve_target_tabs(self, target_patterns: List[str], source_tab: TabInfo) -> List[str]:
        """Resolve target tab patterns to actual tab IDs"""
        resolved_tabs = []
        
        for pattern in target_patterns:
            if pattern == "*":  # All tabs
                resolved_tabs.extend(self.tabs.keys())
            elif pattern == "same_window":  # Same window tabs
                resolved_tabs.extend([tid for tid, tab in self.tabs.items() 
                                    if tab.window_id == source_tab.window_id])
            elif pattern == "same_domain":  # Same domain tabs
                source_domain = urlparse(source_tab.url).netloc
                resolved_tabs.extend([tid for tid, tab in self.tabs.items() 
                                    if urlparse(tab.url).netloc == source_domain])
            elif pattern in self.tabs:  # Direct tab ID
                resolved_tabs.append(pattern)
            elif pattern in self.tab_groups:  # Tab group
                resolved_tabs.extend(self.tab_groups[pattern])
        
        return list(set(resolved_tabs))  # Remove duplicates
    
    def _execute_tab_command(self, tab_id: str, command: BrowserCommand, params: Dict[str, Any]) -> CommandResult:
        """Execute command on specific tab"""
        start_time = time.time()
        
        # Mock implementation - would integrate with actual browser controller
        try:
            if command == BrowserCommand.NAVIGATE:
                url = params.get('url', '')
                logger.debug(f"Navigating tab {tab_id} to {url}")
                result_data = {"navigated_to": url}
            
            elif command == BrowserCommand.EXECUTE_SCRIPT:
                script = params.get('script', '')
                logger.debug(f"Executing script in tab {tab_id}")
                result_data = {"script_executed": True, "result": "mock_result"}
            
            elif command == BrowserCommand.REFRESH:
                logger.debug(f"Refreshing tab {tab_id}")
                result_data = {"refreshed": True}
            
            else:
                result_data = {"command_executed": command.value}
            
            return CommandResult(
                success=True,
                command=command,
                target_tab_id=tab_id,
                result_data=result_data,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                command=command,
                target_tab_id=tab_id,
                execution_time=time.time() - start_time,
                error_message=str(e)
            )


class BrowserController:
    """Advanced browser controller with multi-instance support"""
    
    def __init__(self):
        self.sessions: Dict[str, BrowserSession] = {}
        self.tab_manager = TabManager()
        self.active_session_id: Optional[str] = None
        self.browser_processes: Dict[str, subprocess.Popen] = {}
        self.command_queue = defaultdict(list)
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Browser-specific configurations
        self.browser_configs = {
            BrowserType.CHROME: {
                "executable": "google-chrome",
                "args": ["--remote-debugging-port=9222", "--no-first-run", "--no-default-browser-check"],
                "profile_dir": "~/.config/google-chrome",
                "extension_support": True
            },
            BrowserType.FIREFOX: {
                "executable": "firefox",
                "args": ["--marionette", "--no-remote"],
                "profile_dir": "~/.mozilla/firefox",
                "extension_support": True
            },
            BrowserType.SAFARI: {
                "executable": "safari",
                "args": [],
                "profile_dir": "~/Library/Safari",
                "extension_support": False
            }
        }
    
    def create_session(self, browser_type: BrowserType, 
                      profile: str = None,
                      headless: bool = False,
                      extensions: List[str] = None) -> str:
        """Create a new browser session"""
        
        session_id = f"{browser_type.value}_{int(time.time())}"
        
        # Prepare browser launch configuration
        config = self.browser_configs.get(browser_type, {})
        launch_args = config.get("args", []).copy()
        
        if headless:
            if browser_type == BrowserType.CHROME:
                launch_args.append("--headless")
            elif browser_type == BrowserType.FIREFOX:
                launch_args.append("--headless")
        
        if profile:
            if browser_type == BrowserType.CHROME:
                launch_args.append(f"--user-data-dir={profile}")
            elif browser_type == BrowserType.FIREFOX:
                launch_args.append(f"--profile={profile}")
        
        # Load extensions if specified
        if extensions and config.get("extension_support"):
            for extension_path in extensions:
                if browser_type == BrowserType.CHROME:
                    launch_args.append(f"--load-extension={extension_path}")
        
        try:
            # Launch browser process
            process = self._launch_browser(browser_type, launch_args)
            
            session = BrowserSession(
                session_id=session_id,
                browser_type=browser_type,
                windows=[],
                active_window_id=None,
                profile_path=profile,
                extensions_enabled=bool(extensions),
                headless=headless,
                process_id=process.pid if process else None
            )
            
            self.sessions[session_id] = session
            self.browser_processes[session_id] = process
            
            if not self.active_session_id:
                self.active_session_id = session_id
            
            logger.info(f"Created browser session {session_id} for {browser_type.value}")
            
            # Start monitoring if not already running
            if not self.monitoring_thread or not self.monitoring_thread.is_alive():
                self._start_monitoring()
            
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create browser session: {e}")
            raise
    
    def _launch_browser(self, browser_type: BrowserType, args: List[str]) -> subprocess.Popen:
        """Launch browser process with specified arguments"""
        config = self.browser_configs[browser_type]
        executable = config["executable"]
        
        try:
            # Mock process for demonstration - in real implementation would launch actual browser
            logger.info(f"Launching {executable} with args: {args}")
            return None  # Would return subprocess.Popen([executable] + args)
            
        except Exception as e:
            logger.error(f"Failed to launch browser {browser_type.value}: {e}")
            raise
    
    def close_session(self, session_id: str) -> bool:
        """Close browser session and cleanup"""
        try:
            if session_id in self.sessions:
                # Close all tabs in session
                session = self.sessions[session_id]
                for window in session.windows:
                    for tab in window.tabs:
                        self.tab_manager.unregister_tab(tab.tab_id)
                
                # Terminate browser process
                if session_id in self.browser_processes:
                    process = self.browser_processes[session_id]
                    if process and process.poll() is None:
                        process.terminate()
                        process.wait(timeout=5)
                    del self.browser_processes[session_id]
                
                del self.sessions[session_id]
                
                # Update active session
                if self.active_session_id == session_id:
                    self.active_session_id = next(iter(self.sessions), None)
                
                logger.info(f"Closed browser session {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to close session {session_id}: {e}")
            
        return False
    
    def execute_command(self, command: BrowserCommand, 
                       target: str = None,  # tab_id, window_id, or session_id
                       params: Dict[str, Any] = None) -> CommandResult:
        """Execute browser command on specified target"""
        params = params or {}
        start_time = time.time()
        
        try:
            if not target and self.active_session_id:
                # Use active session if no target specified
                session = self.sessions[self.active_session_id]
                if session.windows and session.active_window_id:
                    window = next(w for w in session.windows if w.window_id == session.active_window_id)
                    if window.active_tab_id:
                        target = window.active_tab_id
            
            if not target:
                return CommandResult(False, command, None, error_message="No target specified or available")
            
            # Route command based on type
            if command in [BrowserCommand.NEW_TAB, BrowserCommand.CLOSE_TAB, BrowserCommand.SWITCH_TAB]:
                return self._handle_tab_command(command, target, params)
            elif command in [BrowserCommand.NAVIGATE, BrowserCommand.REFRESH, BrowserCommand.BACK, BrowserCommand.FORWARD]:
                return self._handle_navigation_command(command, target, params)
            elif command in [BrowserCommand.EXECUTE_SCRIPT, BrowserCommand.INJECT_CSS]:
                return self._handle_script_command(command, target, params)
            elif command in [BrowserCommand.GET_COOKIES, BrowserCommand.SET_COOKIES]:
                return self._handle_cookie_command(command, target, params)
            else:
                return CommandResult(False, command, target, error_message=f"Unsupported command: {command.value}")
                
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return CommandResult(False, command, target, execution_time=time.time() - start_time, error_message=str(e))
    
    def _handle_tab_command(self, command: BrowserCommand, target: str, params: Dict[str, Any]) -> CommandResult:
        """Handle tab-related commands"""
        if command == BrowserCommand.NEW_TAB:
            # Create new tab
            url = params.get('url', 'about:blank')
            new_tab_id = f"tab_{int(time.time() * 1000)}"
            
            # Create tab info
            tab_info = TabInfo(
                tab_id=new_tab_id,
                window_id=target,  # target is window_id for new tab
                url=url,
                title="New Tab",
                state=TabState.LOADING,
                is_active=True,
                is_pinned=False
            )
            
            self.tab_manager.register_tab(tab_info)
            
            return CommandResult(True, command, new_tab_id, {"tab_id": new_tab_id})
        
        elif command == BrowserCommand.CLOSE_TAB:
            self.tab_manager.unregister_tab(target)
            return CommandResult(True, command, target, {"closed": True})
        
        elif command == BrowserCommand.SWITCH_TAB:
            # Update tab states
            for tab_id, tab in self.tab_manager.tabs.items():
                tab.is_active = (tab_id == target)
            
            return CommandResult(True, command, target, {"switched": True})
        
        return CommandResult(False, command, target, error_message="Tab command not implemented")
    
    def _handle_navigation_command(self, command: BrowserCommand, target: str, params: Dict[str, Any]) -> CommandResult:
        """Handle navigation commands"""
        tab_info = self.tab_manager.tabs.get(target)
        if not tab_info:
            return CommandResult(False, command, target, error_message="Tab not found")
        
        if command == BrowserCommand.NAVIGATE:
            url = params.get('url', '')
            if url:
                tab_info.url = url
                tab_info.state = TabState.LOADING
                tab_info.last_activity = time.time()
                
                # Simulate navigation completion
                threading.Timer(1.0, lambda: self.tab_manager.update_tab_state(target, TabState.COMPLETE)).start()
                
                return CommandResult(True, command, target, {"navigated_to": url})
        
        elif command == BrowserCommand.REFRESH:
            tab_info.state = TabState.LOADING
            tab_info.last_activity = time.time()
            
            # Simulate refresh completion
            threading.Timer(0.5, lambda: self.tab_manager.update_tab_state(target, TabState.COMPLETE)).start()
            
            return CommandResult(True, command, target, {"refreshed": True})
        
        elif command in [BrowserCommand.BACK, BrowserCommand.FORWARD]:
            # Would implement actual navigation history
            return CommandResult(True, command, target, {"navigated": command.value})
        
        return CommandResult(False, command, target, error_message="Navigation command not implemented")
    
    def _handle_script_command(self, command: BrowserCommand, target: str, params: Dict[str, Any]) -> CommandResult:
        """Handle script execution commands"""
        tab_info = self.tab_manager.tabs.get(target)
        if not tab_info:
            return CommandResult(False, command, target, error_message="Tab not found")
        
        if command == BrowserCommand.EXECUTE_SCRIPT:
            script = params.get('script', '')
            if script:
                # Would execute actual JavaScript
                logger.debug(f"Executing script in tab {target}: {script[:100]}")
                return CommandResult(True, command, target, {"result": "script_executed", "script_length": len(script)})
        
        elif command == BrowserCommand.INJECT_CSS:
            css = params.get('css', '')
            if css:
                # Would inject actual CSS
                logger.debug(f"Injecting CSS in tab {target}: {css[:100]}")
                return CommandResult(True, command, target, {"result": "css_injected", "css_length": len(css)})
        
        return CommandResult(False, command, target, error_message="Script command not implemented")
    
    def _handle_cookie_command(self, command: BrowserCommand, target: str, params: Dict[str, Any]) -> CommandResult:
        """Handle cookie-related commands"""
        tab_info = self.tab_manager.tabs.get(target)
        if not tab_info:
            return CommandResult(False, command, target, error_message="Tab not found")
        
        if command == BrowserCommand.GET_COOKIES:
            # Return current cookies for tab
            return CommandResult(True, command, target, {"cookies": tab_info.cookies})
        
        elif command == BrowserCommand.SET_COOKIES:
            cookies = params.get('cookies', [])
            tab_info.cookies = cookies
            return CommandResult(True, command, target, {"cookies_set": len(cookies)})
        
        return CommandResult(False, command, target, error_message="Cookie command not implemented")
    
    def _start_monitoring(self) -> None:
        """Start background monitoring of browser sessions"""
        def monitor_loop():
            while self.sessions:
                try:
                    for session_id, session in list(self.sessions.items()):
                        # Check if browser process is still alive
                        process = self.browser_processes.get(session_id)
                        if process and process.poll() is not None:
                            logger.warning(f"Browser process for session {session_id} has terminated")
                            # Could implement automatic restart or cleanup
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    logger.error(f"Monitor loop error: {e}")
                    time.sleep(10)
        
        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()
    
    def coordinate_cross_tab_action(self, action_name: str, 
                                   source_tab: str, 
                                   target_pattern: str,
                                   action_params: Dict[str, Any]) -> List[CommandResult]:
        """Coordinate action across multiple tabs"""
        
        # Create coordination rule
        rule = CoordinationRule(
            rule_id=f"coord_{int(time.time())}",
            name=action_name,
            trigger_condition=lambda tab: tab.tab_id == source_tab,
            target_tabs=[target_pattern],
            action=BrowserCommand.EXECUTE_SCRIPT,  # Default action
            action_params=action_params
        )
        
        # Execute coordination
        source_tab_info = self.tab_manager.tabs.get(source_tab)
        if source_tab_info:
            self.tab_manager._check_coordination_rules(source_tab_info)
        
        return []  # Would return actual results
    
    def get_session_status(self, session_id: str = None) -> Dict[str, Any]:
        """Get comprehensive session status"""
        if session_id:
            sessions_to_check = {session_id: self.sessions[session_id]} if session_id in self.sessions else {}
        else:
            sessions_to_check = self.sessions
        
        status = {
            "active_sessions": len(self.sessions),
            "active_session_id": self.active_session_id,
            "total_tabs": len(self.tab_manager.tabs),
            "sessions": {}
        }
        
        for sid, session in sessions_to_check.items():
            session_info = {
                "browser_type": session.browser_type.value,
                "windows": len(session.windows),
                "total_tabs": sum(len(w.tabs) for w in session.windows),
                "headless": session.headless,
                "extensions_enabled": session.extensions_enabled,
                "uptime": time.time() - session.startup_time,
                "process_alive": self.browser_processes.get(sid, {}).get('poll', lambda: None)() is None
            }
            
            status["sessions"][sid] = session_info
        
        return status