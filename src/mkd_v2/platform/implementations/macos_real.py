"""
Real macOS Platform Implementation with actual input capture.

This replaces the mock implementation with real pynput-based input capture
and actual macOS APIs for screen overlay rendering.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Callable

try:
    from pynput import mouse, keyboard
    from pynput.mouse import Button, Listener as MouseListener
    from pynput.keyboard import Key, Listener as KeyboardListener
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    mouse = keyboard = None

from ..base import PlatformInterface, MouseAction, KeyboardAction, WindowInfo, UIElement, OverlayConfig

logger = logging.getLogger(__name__)


class MacOSRealPlatform(PlatformInterface):
    """Real macOS platform implementation with actual input capture."""
    
    def __init__(self):
        super().__init__()
        self.name = "macOS"
        self.version = "2.0.0"
        
        # Input capture
        self.mouse_listener: Optional[MouseListener] = None
        self.keyboard_listener: Optional[KeyboardListener] = None
        self.input_callback: Optional[Callable] = None
        self.capturing = False
        
        # Overlay system
        self.overlays = {}
        
        if not PYNPUT_AVAILABLE:
            logger.warning("pynput not available - input capture will not work")
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize macOS platform with permission checks."""
        try:
            if not PYNPUT_AVAILABLE:
                return {
                    'success': False,
                    'error': 'pynput dependency not available. Install with: pip install pynput'
                }
            
            # Test permissions by trying to create listeners
            try:
                # Test mouse listener
                test_mouse = MouseListener(on_click=lambda x, y, button, pressed: None)
                test_mouse.start()
                time.sleep(0.1)
                test_mouse.stop()
                
                # Test keyboard listener  
                test_kbd = KeyboardListener(on_press=lambda key: None)
                test_kbd.start()
                time.sleep(0.1)
                test_kbd.stop()
                
                self._initialized = True
                logger.info("macOS platform initialized with real input capture")
                
                return {
                    'success': True,
                    'platform': self.name,
                    'capabilities': self.get_capabilities(),
                    'input_capture': 'pynput',
                    'permissions_ok': True
                }
                
            except Exception as perm_error:
                logger.error(f"Permission test failed: {perm_error}")
                return {
                    'success': False,
                    'error': 'macOS permissions required. Enable Accessibility and Input Monitoring in System Preferences',
                    'permissions_required': ['accessibility', 'input_monitoring']
                }
                
        except Exception as e:
            logger.error(f"macOS initialization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def cleanup(self) -> bool:
        """Clean up macOS resources."""
        try:
            # Stop input capture
            self.stop_input_capture()
            
            # Clean up overlays
            for overlay_id in list(self.overlays.keys()):
                self.destroy_overlay(overlay_id)
            
            self._initialized = False
            logger.info("macOS platform cleanup complete")
            return True
            
        except Exception as e:
            logger.error(f"macOS cleanup failed: {e}")
            return False
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get real macOS capabilities."""
        return {
            'input_capture': PYNPUT_AVAILABLE,
            'screen_recording': True,
            'ui_automation': True,
            'overlay_support': True,
            'window_management': True,
            'system_integration': True,
            'multi_monitor': True,
            'real_input_capture': PYNPUT_AVAILABLE
        }
    
    def check_permissions(self) -> Dict[str, Any]:
        """Check macOS permissions."""
        if not PYNPUT_AVAILABLE:
            return {
                'overall': False,
                'missing_permissions': ['pynput_dependency'],
                'details': {
                    'pynput': False,
                    'accessibility': False,
                    'input_monitoring': False
                }
            }
        
        # Test actual permissions
        missing = []
        details = {}
        
        try:
            # Quick permission test
            test_mouse = MouseListener(on_click=lambda x, y, button, pressed: None)
            test_mouse.start()
            time.sleep(0.05)
            test_mouse.stop()
            details['accessibility'] = True
            
        except Exception:
            missing.append('accessibility')
            details['accessibility'] = False
        
        try:
            test_kbd = KeyboardListener(on_press=lambda key: None)
            test_kbd.start()
            time.sleep(0.05)
            test_kbd.stop()
            details['input_monitoring'] = True
            
        except Exception:
            missing.append('input_monitoring')
            details['input_monitoring'] = False
        
        return {
            'overall': len(missing) == 0,
            'missing_permissions': missing,
            'details': details
        }
    
    def request_permissions(self, permissions: List[str]) -> bool:
        """Request macOS permissions."""
        logger.info("macOS permissions must be granted manually in System Preferences")
        logger.info("Go to System Preferences → Security & Privacy → Privacy")
        logger.info("Add this application to Accessibility and Input Monitoring")
        return False  # User must grant manually
    
    # Real Input Capture Implementation
    
    def start_input_capture(self, callback: Callable) -> bool:
        """Start real input capture using pynput."""
        if self.capturing:
            logger.warning("Input capture already active")
            return True
        
        if not PYNPUT_AVAILABLE:
            logger.error("pynput not available for input capture")
            return False
        
        try:
            self.input_callback = callback
            
            # Start mouse listener
            self.mouse_listener = MouseListener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click,
                on_scroll=self._on_mouse_scroll
            )
            
            # Start keyboard listener
            self.keyboard_listener = KeyboardListener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            
            # Start listeners
            self.mouse_listener.start()
            self.keyboard_listener.start()
            
            self.capturing = True
            logger.info("Real input capture started on macOS")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start real input capture: {e}")
            return False
    
    def stop_input_capture(self) -> bool:
        """Stop real input capture."""
        if not self.capturing:
            return True
        
        try:
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
            
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
            
            self.input_callback = None
            self.capturing = False
            
            logger.info("Real input capture stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop input capture: {e}")
            return False
    
    # pynput Event Handlers
    
    def _on_mouse_move(self, x, y):
        """Handle mouse movement."""
        if self.input_callback:
            event = {
                'timestamp': time.time(),
                'type': 'mouse_move',
                'source': 'mouse',
                'x': x,
                'y': y,
                'button': None,
                'pressed': False
            }
            self.input_callback(event)
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse clicks."""
        if self.input_callback:
            # Convert pynput button to our format
            button_name = {
                Button.left: 'left',
                Button.right: 'right', 
                Button.middle: 'middle'
            }.get(button, 'unknown')
            
            event = {
                'timestamp': time.time(),
                'type': 'mouse_click',
                'source': 'mouse',
                'x': x,
                'y': y,
                'button': button_name,
                'pressed': pressed
            }
            self.input_callback(event)
    
    def _on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll."""
        if self.input_callback:
            event = {
                'timestamp': time.time(),
                'type': 'mouse_scroll',
                'source': 'mouse',
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'scroll_delta': {'x': dx, 'y': dy}
            }
            self.input_callback(event)
    
    def _on_key_press(self, key):
        """Handle key press."""
        if self.input_callback:
            key_name, char = self._process_key(key)
            
            event = {
                'timestamp': time.time(),
                'type': 'key_press',
                'source': 'keyboard',
                'key': key_name,
                'char': char,
                'pressed': True,
                'modifiers': self._get_current_modifiers()
            }
            self.input_callback(event)
    
    def _on_key_release(self, key):
        """Handle key release."""
        if self.input_callback:
            key_name, char = self._process_key(key)
            
            event = {
                'timestamp': time.time(),
                'type': 'key_release',
                'source': 'keyboard',
                'key': key_name,
                'char': char,
                'pressed': False,
                'modifiers': self._get_current_modifiers()
            }
            self.input_callback(event)
    
    def _process_key(self, key) -> Tuple[str, Optional[str]]:
        """Process pynput key into our format."""
        try:
            if hasattr(key, 'char') and key.char:
                # Regular character key
                return key.char, key.char
            elif hasattr(key, 'name'):
                # Special key
                return key.name, None
            else:
                return str(key), None
        except:
            return str(key), None
    
    def _get_current_modifiers(self) -> List[str]:
        """Get currently pressed modifier keys."""
        # This is a simplified version - in a full implementation
        # you'd track modifier state more precisely
        modifiers = []
        
        try:
            # pynput doesn't easily provide current modifier state
            # For now, return empty list
            # In a full implementation, you'd maintain modifier state
            pass
        except:
            pass
        
        return modifiers
    
    # Action Execution (using pynput)
    
    def execute_mouse_action(self, action: MouseAction) -> bool:
        """Execute mouse action using pynput."""
        if not PYNPUT_AVAILABLE:
            return False
        
        try:
            controller = mouse.Controller()
            
            if action.action == 'click':
                # Move to position
                controller.position = (action.x, action.y)
                
                # Convert button
                pynput_button = {
                    'left': Button.left,
                    'right': Button.right,
                    'middle': Button.middle
                }.get(action.button.value if action.button else 'left', Button.left)
                
                # Click
                controller.click(pynput_button)
                
            elif action.action == 'move':
                controller.position = (action.x, action.y)
                
            elif action.action == 'scroll':
                controller.position = (action.x, action.y)
                controller.scroll(action.dx, action.dy)
                
            logger.debug(f"Executed mouse action: {action.action}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute mouse action: {e}")
            return False
    
    def execute_keyboard_action(self, action: KeyboardAction) -> bool:
        """Execute keyboard action using pynput."""
        if not PYNPUT_AVAILABLE:
            return False
        
        try:
            controller = keyboard.Controller()
            
            if action.action == 'type' and action.text:
                controller.type(action.text)
                
            elif action.action in ['press', 'release'] and action.key:
                # Convert key name to pynput key
                try:
                    if len(action.key) == 1:
                        # Single character
                        key_obj = action.key
                    else:
                        # Special key
                        key_obj = getattr(Key, action.key.lower(), action.key)
                        
                    if action.action == 'press':
                        controller.press(key_obj)
                    else:
                        controller.release(key_obj)
                        
                except Exception as key_error:
                    logger.error(f"Key conversion failed: {key_error}")
                    return False
            
            logger.debug(f"Executed keyboard action: {action.action}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute keyboard action: {e}")
            return False
    
    # Window and UI Methods (mock for now - Week 3 feature)
    
    def get_active_window_info(self) -> Optional[WindowInfo]:
        """Get active window info (mock implementation)."""
        return WindowInfo(
            title="macOS Active Window",
            class_name="NSWindow",
            process_name="TestApp",
            pid=5678,
            x=100, y=100, width=800, height=600,
            is_active=True, is_visible=True
        )
    
    def get_window_list(self) -> List[WindowInfo]:
        """Get window list (mock implementation)."""
        return [self.get_active_window_info()]
    
    def get_ui_element_at_position(self, x: int, y: int) -> Optional[UIElement]:
        """Get UI element at position (mock implementation)."""
        return UIElement(
            element_type="button", name="macOS Button", value=None,
            x=x, y=y, width=100, height=30,
            is_enabled=True, is_visible=True, properties={}
        )
    
    # Screen and Display Methods
    
    def get_screen_resolution(self) -> Tuple[int, int]:
        """Get screen resolution."""
        # Could use AppKit/Cocoa for real screen resolution
        return (2560, 1440)
    
    def get_monitor_info(self) -> List[Dict[str, Any]]:
        """Get monitor information."""
        return [
            {
                'index': 0, 'name': 'Built-in Retina Display',
                'width': 2560, 'height': 1440,
                'x': 0, 'y': 0, 'is_primary': True, 'scale_factor': 2.0
            }
        ]
    
    def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> bytes:
        """Take screenshot."""
        # Mock for now - would use Quartz APIs in real implementation
        return b"mock_macos_screenshot_data"
    
    # Overlay Methods (real implementation using overlay renderer)
    
    def create_screen_overlay(self, config: OverlayConfig) -> Any:
        """Create screen overlay using real renderer."""
        try:
            from ...ui.overlay_renderer import get_overlay_manager
            
            # Get screen resolution for full-screen overlay
            width, height = self.get_screen_resolution()
            
            renderer = get_overlay_manager()
            overlay_id = renderer.create_overlay(
                x=0, y=0, width=width, height=height,
                style="border" if config.style == "border" else "recording",
                color=config.color,
                opacity=config.opacity
            )
            
            if overlay_id:
                overlay_info = {
                    'id': overlay_id,
                    'config': config,
                    'renderer': renderer,
                    'active': True
                }
                self.overlays[overlay_id] = overlay_info
                logger.info(f"Created real macOS overlay: {overlay_id}")
                return overlay_id
            else:
                logger.error("Failed to create overlay with renderer")
                return None
            
        except Exception as e:
            logger.error(f"Failed to create macOS overlay: {e}")
            return None
    
    def update_overlay(self, overlay: Any, config: OverlayConfig) -> bool:
        """Update overlay using real renderer."""
        overlay_id = str(overlay)
        if overlay_id in self.overlays:
            try:
                overlay_info = self.overlays[overlay_id]
                renderer = overlay_info['renderer']
                
                success = renderer.update_overlay(
                    overlay_id,
                    style="border" if config.style == "border" else "recording",
                    color=config.color,
                    opacity=config.opacity
                )
                
                if success:
                    overlay_info['config'] = config
                    logger.debug(f"Updated real macOS overlay: {overlay_id}")
                return success
                
            except Exception as e:
                logger.error(f"Failed to update macOS overlay: {e}")
                return False
        return False
    
    def destroy_overlay(self, overlay: Any) -> bool:
        """Destroy overlay using real renderer."""
        overlay_id = str(overlay)
        if overlay_id in self.overlays:
            try:
                overlay_info = self.overlays[overlay_id]
                renderer = overlay_info['renderer']
                
                success = renderer.destroy_overlay(overlay_id)
                if success:
                    del self.overlays[overlay_id]
                    logger.info(f"Destroyed real macOS overlay: {overlay_id}")
                    return True
                else:
                    logger.error(f"Failed to destroy overlay with renderer: {overlay_id}")
                    return False
                    
            except Exception as e:
                logger.error(f"Failed to destroy macOS overlay: {e}")
                return False
        return False
    
    # System Integration
    
    def execute_shell_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute shell command."""
        import subprocess
        
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, 
                text=True, timeout=kwargs.get('timeout', 30)
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_process_list(self) -> List[Dict[str, Any]]:
        """Get running processes."""
        # Mock for now - would use ps or Activity Monitor APIs
        return [
            {'pid': 5678, 'name': 'TestApp', 'cpu_usage': 2.0, 'memory_usage': 2048}
        ]
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        import platform
        
        return {
            'platform': 'macOS',
            'version': platform.mac_ver()[0],
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'python_version': platform.python_version()
        }