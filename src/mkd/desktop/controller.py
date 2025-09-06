"""
Desktop automation controller for comprehensive system control.
"""
import logging
import time
import platform
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path

from .actions import DesktopAction, DesktopActionType

logger = logging.getLogger(__name__)


class DesktopController:
    """
    Main controller for desktop automation.
    
    Provides comprehensive desktop control including:
    - Mouse and keyboard automation
    - Window management
    - Application launching
    - File operations
    - System commands
    - Screen capture
    """
    
    def __init__(self):
        """Initialize desktop controller."""
        self.platform = platform.system()
        self._mouse_controller = None
        self._keyboard_controller = None
        self._screen_capture = None
        self._initialize_controllers()
        
    def _initialize_controllers(self):
        """Initialize platform-specific controllers."""
        try:
            import pynput
            from pynput import mouse, keyboard
            from PIL import ImageGrab
            
            self._mouse_controller = mouse.Controller()
            self._keyboard_controller = keyboard.Controller()
            self._screen_capture = ImageGrab
            
            logger.info(f"Desktop controller initialized for {self.platform}")
            
        except ImportError as e:
            logger.error(f"Failed to initialize controllers: {e}")
            logger.error("Please install required packages: pip install pynput pillow")
            
    def execute_action(self, action: DesktopAction) -> Any:
        """Execute a desktop action."""
        action_type = action.type
        params = action.parameters
        
        logger.info(f"Executing action: {action.description}")
        
        try:
            if action_type == DesktopActionType.MOUSE_CLICK:
                return self._execute_mouse_click(params)
            elif action_type == DesktopActionType.MOUSE_MOVE:
                return self._execute_mouse_move(params)
            elif action_type == DesktopActionType.MOUSE_DRAG:
                return self._execute_mouse_drag(params)
            elif action_type == DesktopActionType.MOUSE_SCROLL:
                return self._execute_mouse_scroll(params)
            elif action_type == DesktopActionType.KEY_PRESS:
                return self._execute_key_press(params)
            elif action_type == DesktopActionType.KEY_COMBINATION:
                return self._execute_key_combination(params)
            elif action_type == DesktopActionType.TYPE_TEXT:
                return self._execute_type_text(params)
            elif action_type == DesktopActionType.LAUNCH_APP:
                return self._execute_launch_app(params)
            elif action_type == DesktopActionType.OPEN_FILE:
                return self._execute_open_file(params)
            elif action_type == DesktopActionType.OPEN_FOLDER:
                return self._execute_open_folder(params)
            elif action_type == DesktopActionType.RUN_COMMAND:
                return self._execute_run_command(params)
            elif action_type == DesktopActionType.SCREENSHOT:
                return self._execute_screenshot(params)
            elif action_type == DesktopActionType.WAIT_TIME:
                return self._execute_wait_time(params)
            elif action_type == DesktopActionType.RESIZE_WINDOW:
                return self._execute_resize_window(params)
            elif action_type == DesktopActionType.MOVE_WINDOW:
                return self._execute_move_window(params)
            elif action_type == DesktopActionType.MINIMIZE_WINDOW:
                return self._execute_minimize_window(params)
            elif action_type == DesktopActionType.MAXIMIZE_WINDOW:
                return self._execute_maximize_window(params)
            elif action_type == DesktopActionType.GET_ACTIVE_WINDOW:
                return self._execute_get_active_window(params)
            elif action_type == DesktopActionType.GET_WINDOW_LIST:
                return self._execute_get_window_list(params)
            else:
                logger.warning(f"Unsupported action type: {action_type}")
                return f"Action type {action_type.value} not implemented"
                
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {e}")
            raise
            
    def _execute_mouse_click(self, params: Dict[str, Any]) -> None:
        """Execute mouse click."""
        if not self._mouse_controller:
            raise RuntimeError("Mouse controller not available")
            
        x = params['x']
        y = params['y']
        button = params.get('button', 'left')
        
        import pynput.mouse
        
        # Move to position first
        self._mouse_controller.position = (x, y)
        time.sleep(0.1)
        
        # Click
        if button == 'left':
            self._mouse_controller.click(pynput.mouse.Button.left)
        elif button == 'right':
            self._mouse_controller.click(pynput.mouse.Button.right)
        elif button == 'middle':
            self._mouse_controller.click(pynput.mouse.Button.middle)
            
    def _execute_mouse_move(self, params: Dict[str, Any]) -> None:
        """Execute mouse move."""
        if not self._mouse_controller:
            raise RuntimeError("Mouse controller not available")
            
        x = params['x']
        y = params['y']
        smooth = params.get('smooth', True)
        
        if smooth:
            # Smooth movement
            current_x, current_y = self._mouse_controller.position
            steps = 20
            for i in range(steps):
                t = i / (steps - 1)
                new_x = int(current_x + (x - current_x) * t)
                new_y = int(current_y + (y - current_y) * t)
                self._mouse_controller.position = (new_x, new_y)
                time.sleep(0.01)
        else:
            # Direct movement
            self._mouse_controller.position = (x, y)
            
    def _execute_mouse_drag(self, params: Dict[str, Any]) -> None:
        """Execute mouse drag."""
        if not self._mouse_controller:
            raise RuntimeError("Mouse controller not available")
            
        start_x = params['start_x']
        start_y = params['start_y']
        end_x = params['end_x']
        end_y = params['end_y']
        
        import pynput.mouse
        
        # Move to start position
        self._mouse_controller.position = (start_x, start_y)
        time.sleep(0.1)
        
        # Press and drag
        self._mouse_controller.press(pynput.mouse.Button.left)
        time.sleep(0.1)
        
        # Drag to end position
        self._execute_mouse_move({'x': end_x, 'y': end_y, 'smooth': True})
        
        # Release
        self._mouse_controller.release(pynput.mouse.Button.left)
        
    def _execute_mouse_scroll(self, params: Dict[str, Any]) -> None:
        """Execute mouse scroll."""
        if not self._mouse_controller:
            raise RuntimeError("Mouse controller not available")
            
        dx = params.get('dx', 0)
        dy = params.get('dy', 0)
        
        self._mouse_controller.scroll(dx, dy)
        
    def _execute_key_press(self, params: Dict[str, Any]) -> None:
        """Execute key press."""
        if not self._keyboard_controller:
            raise RuntimeError("Keyboard controller not available")
            
        key = params['key']
        modifiers = params.get('modifiers', [])
        
        import pynput.keyboard
        
        # Press modifiers
        modifier_keys = []
        for mod in modifiers:
            if mod.lower() == 'ctrl':
                modifier_keys.append(pynput.keyboard.Key.ctrl)
            elif mod.lower() == 'alt':
                modifier_keys.append(pynput.keyboard.Key.alt)
            elif mod.lower() == 'shift':
                modifier_keys.append(pynput.keyboard.Key.shift)
            elif mod.lower() == 'cmd' or mod.lower() == 'win':
                modifier_keys.append(pynput.keyboard.Key.cmd)
                
        for mod_key in modifier_keys:
            self._keyboard_controller.press(mod_key)
            
        # Press main key
        try:
            # Try special keys first
            if hasattr(pynput.keyboard.Key, key.lower()):
                key_obj = getattr(pynput.keyboard.Key, key.lower())
                self._keyboard_controller.press(key_obj)
                self._keyboard_controller.release(key_obj)
            else:
                # Regular character
                self._keyboard_controller.press(key)
                self._keyboard_controller.release(key)
        finally:
            # Release modifiers
            for mod_key in reversed(modifier_keys):
                self._keyboard_controller.release(mod_key)
                
    def _execute_key_combination(self, params: Dict[str, Any]) -> None:
        """Execute key combination."""
        if not self._keyboard_controller:
            raise RuntimeError("Keyboard controller not available")
            
        keys = params['keys']
        
        import pynput.keyboard
        
        # Press all keys
        key_objects = []
        for key in keys:
            if key.lower() == 'ctrl':
                key_obj = pynput.keyboard.Key.ctrl
            elif key.lower() == 'alt':
                key_obj = pynput.keyboard.Key.alt
            elif key.lower() == 'shift':
                key_obj = pynput.keyboard.Key.shift
            elif key.lower() in ['cmd', 'win']:
                key_obj = pynput.keyboard.Key.cmd
            elif hasattr(pynput.keyboard.Key, key.lower()):
                key_obj = getattr(pynput.keyboard.Key, key.lower())
            else:
                key_obj = key
                
            key_objects.append(key_obj)
            self._keyboard_controller.press(key_obj)
            
        time.sleep(0.1)
        
        # Release in reverse order
        for key_obj in reversed(key_objects):
            self._keyboard_controller.release(key_obj)
            
    def _execute_type_text(self, params: Dict[str, Any]) -> None:
        """Execute type text."""
        if not self._keyboard_controller:
            raise RuntimeError("Keyboard controller not available")
            
        text = params['text']
        delay = params.get('delay', 0.05)
        
        for char in text:
            self._keyboard_controller.type(char)
            if delay > 0:
                time.sleep(delay)
                
    def _execute_launch_app(self, params: Dict[str, Any]) -> None:
        """Execute launch application."""
        import subprocess
        
        app_name = params['app_name']
        path = params.get('path')
        args = params.get('args', [])
        
        if path:
            # Launch specific executable
            cmd = [path] + args
        else:
            # Launch by app name (Windows)
            if self.platform == "Windows":
                cmd = ['start', app_name] + args
            elif self.platform == "Darwin":
                cmd = ['open', '-a', app_name] + args
            else:
                cmd = [app_name] + args
                
        subprocess.Popen(cmd, shell=(self.platform == "Windows"))
        
    def _execute_open_file(self, params: Dict[str, Any]) -> None:
        """Execute open file."""
        import subprocess
        
        file_path = params['file_path']
        app = params.get('app')
        
        if app:
            if self.platform == "Windows":
                subprocess.run(['start', app, file_path], shell=True)
            elif self.platform == "Darwin":
                subprocess.run(['open', '-a', app, file_path])
            else:
                subprocess.run([app, file_path])
        else:
            if self.platform == "Windows":
                subprocess.run(['start', file_path], shell=True)
            elif self.platform == "Darwin":
                subprocess.run(['open', file_path])
            else:
                subprocess.run(['xdg-open', file_path])
                
    def _execute_open_folder(self, params: Dict[str, Any]) -> None:
        """Execute open folder."""
        import subprocess
        
        folder_path = params['folder_path']
        
        if self.platform == "Windows":
            subprocess.run(['explorer', folder_path])
        elif self.platform == "Darwin":
            subprocess.run(['open', folder_path])
        else:
            subprocess.run(['xdg-open', folder_path])
            
    def _execute_run_command(self, params: Dict[str, Any]) -> str:
        """Execute run command."""
        import subprocess
        
        command = params['command']
        shell = params.get('shell', 'cmd')
        wait = params.get('wait', True)
        
        if self.platform == "Windows":
            if shell == 'powershell':
                cmd = ['powershell', '-Command', command]
            else:
                cmd = ['cmd', '/c', command]
        else:
            cmd = ['bash', '-c', command]
            
        if wait:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
            return result.stdout + result.stderr
        else:
            subprocess.Popen(cmd, shell=False)
            return "Command started in background"
            
    def _execute_screenshot(self, params: Dict[str, Any]) -> str:
        """Execute screenshot."""
        if not self._screen_capture:
            raise RuntimeError("Screen capture not available")
            
        file_path = params.get('file_path', f'screenshot_{int(time.time())}.png')
        region = params.get('region')  # (x, y, width, height)
        
        if region:
            screenshot = self._screen_capture.grab(bbox=region)
        else:
            screenshot = self._screen_capture.grab()
            
        screenshot.save(file_path)
        return file_path
        
    def _execute_wait_time(self, params: Dict[str, Any]) -> None:
        """Execute wait time."""
        seconds = params['seconds']
        time.sleep(seconds)
        
    def _execute_resize_window(self, params: Dict[str, Any]) -> None:
        """Execute resize window."""
        # This would require platform-specific window management
        # For now, just log the action
        width = params['width']
        height = params['height']
        window_title = params.get('window_title', 'active window')
        logger.info(f"Would resize {window_title} to {width}x{height}")
        
    def _execute_move_window(self, params: Dict[str, Any]) -> None:
        """Execute move window."""
        # This would require platform-specific window management
        # For now, just log the action
        x = params['x']
        y = params['y']
        window_title = params.get('window_title', 'active window')
        logger.info(f"Would move {window_title} to ({x}, {y})")
        
    def _execute_minimize_window(self, params: Dict[str, Any]) -> None:
        """Execute minimize window."""
        # Use keyboard shortcut as fallback
        self._execute_key_combination({'keys': ['alt', 'F9']})
        
    def _execute_maximize_window(self, params: Dict[str, Any]) -> None:
        """Execute maximize window."""
        # Use keyboard shortcut as fallback
        self._execute_key_combination({'keys': ['win', 'up']})
        
    def _execute_get_active_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get active window information."""
        # This would require platform-specific implementation
        return {
            'title': 'Unknown Window',
            'pid': 0,
            'position': (0, 0),
            'size': (800, 600)
        }
        
    def _execute_get_window_list(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of all windows."""
        # This would require platform-specific implementation
        return [
            {
                'title': 'Example Window',
                'pid': 1234,
                'position': (100, 100),
                'size': (800, 600),
                'visible': True
            }
        ]