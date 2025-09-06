#!/usr/bin/env python3
"""
MKD Automation Web GUI Backend Server

WebSocket server that bridges the web frontend with the existing MKD automation system.
Provides real-time communication for recording, playback, and system integration.
"""

import asyncio
import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Optional, Any

import websockets
# from websockets import WebSocketServerProtocol  # Deprecated in newer versions

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

try:
    from mkd.core.session_manager import SessionManager
    from mkd.core.config_manager import ConfigManager
    from mkd.data.models import Action, AutomationScript
    from mkd.data.script_storage import ScriptStorage
    from mkd.platform.detector import PlatformDetector
    from mkd.recording.input_capture import InputCapture
    from mkd.playback.action_executor import ActionExecutor
    HAS_MKD = True
except ImportError as e:
    print(f"Warning: MKD modules not available: {e}")
    HAS_MKD = False

# Import system monitor
try:
    from system_monitor import SystemMonitor, TaskManagerController
    HAS_SYSTEM_MONITOR = True
except ImportError as e:
    print(f"Warning: System monitor not available: {e}")
    HAS_SYSTEM_MONITOR = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebGUIBackend:
    """WebSocket server backend for MKD Web GUI."""
    
    def __init__(self, host: str = 'localhost', port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set = set()  # Set of websocket connections
        
        # MKD components
        if HAS_MKD:
            self.session_manager = SessionManager()
            self.config_manager = ConfigManager()
            self.script_storage = ScriptStorage()
            self.platform_detector = PlatformDetector()
            self.input_capture = None
            self.action_executor = ActionExecutor()
        else:
            # Mock components for development
            self.session_manager = None
            self.config_manager = None
            self.script_storage = None
            self.platform_detector = None
            self.input_capture = None
            self.action_executor = None
        
        # Recording state
        self.recording_session = None
        self.recording_start_time = None
        self.recordings_dir = Path("web_recordings")
        self.recordings_dir.mkdir(exist_ok=True)
        
        # Screenshot capture
        self.screenshot_thread = None
        self.screenshot_count = 0
        
        # System monitoring
        if HAS_SYSTEM_MONITOR:
            self.system_monitor = SystemMonitor()
            self.task_manager = TaskManagerController()
        else:
            self.system_monitor = None
            self.task_manager = None
        
        logger.info(f"WebGUI Backend initialized (MKD available: {HAS_MKD}, System Monitor: {HAS_SYSTEM_MONITOR})")
    
    async def register_client(self, websocket):
        """Register a new client connection."""
        self.clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        
        # Send welcome message
        await self.send_to_client(websocket, {
            "type": "connection_established",
            "server_info": {
                "mkd_available": HAS_MKD,
                "system_monitor_available": HAS_SYSTEM_MONITOR,
                "platform": self.platform_detector.get_platform() if HAS_MKD else "unknown",
                "version": "2.1",
                "features": {
                    "process_monitoring": HAS_SYSTEM_MONITOR,
                    "task_manager_integration": HAS_SYSTEM_MONITOR,
                    "semantic_analysis": HAS_SYSTEM_MONITOR,
                    "intelligent_replay": HAS_SYSTEM_MONITOR
                }
            }
        })
    
    async def unregister_client(self, websocket):
        """Unregister a client connection."""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected: {websocket.remote_address}")
    
    async def send_to_client(self, websocket, message: Dict[str, Any]):
        """Send message to a specific client."""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Failed to send message - client disconnected")
        except Exception as e:
            logger.error(f"Error sending message to client: {e}")
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        if not self.clients:
            return
        
        disconnected = []
        for client in self.clients:
            try:
                await self.send_to_client(client, message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(client)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(client)
        
        # Remove disconnected clients
        for client in disconnected:
            self.clients.discard(client)
    
    async def handle_message(self, websocket, message: str):
        """Handle incoming message from client."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            logger.debug(f"Received message: {message_type}")
            
            if message_type == 'start_recording':
                await self.start_recording(websocket, data.get('settings', {}))
            elif message_type == 'stop_recording':
                await self.stop_recording(websocket)
            elif message_type == 'action':
                await self.handle_action(data.get('action'))
            elif message_type == 'get_recordings':
                await self.send_recordings_list(websocket)
            elif message_type == 'load_recording':
                await self.load_recording(websocket, data.get('recording_id'))
            elif message_type == 'replay_actions':
                await self.replay_actions(websocket, data.get('actions', []))
            elif message_type == 'save_video':
                await self.save_video_data(websocket, data.get('video_data'), data.get('recording_id'))
            elif message_type == 'save_screenshots':
                await self.save_screenshot_data(websocket, data.get('screenshots'), data.get('recording_id'))
            elif message_type == 'get_system_status':
                await self.get_system_status(websocket)
            elif message_type == 'launch_task_manager':
                await self.launch_task_manager(websocket)
            elif message_type == 'get_process_list':
                await self.get_process_list(websocket)
            elif message_type == 'analyze_user_action':
                await self.analyze_user_action(websocket, data.get('action'))
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from client")
            await self.send_to_client(websocket, {
                "type": "error",
                "message": "Invalid JSON format"
            })
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            traceback.print_exc()
            await self.send_to_client(websocket, {
                "type": "error",
                "message": f"Server error: {str(e)}"
            })
    
    async def start_recording(self, websocket, settings: Dict[str, Any]):
        """Start recording session."""
        try:
            if self.recording_session:
                await self.send_to_client(websocket, {
                    "type": "error",
                    "message": "Recording already in progress"
                })
                return
            
            logger.info("Starting recording session")
            
            if HAS_MKD:
                # Start MKD recording session
                self.recording_session = self.session_manager.start_recording()
                self.recording_start_time = time.time()
                
                # Setup input capture if available
                # Note: Web-based input capture will be handled by the frontend
                # Backend will receive actions via WebSocket
            else:
                # Mock recording session
                self.recording_session = {
                    "actions": [],
                    "start_time": time.time()
                }
                self.recording_start_time = time.time()
            
            # Create recording directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_recording_dir = self.recordings_dir / f"web_recording_{timestamp}"
            self.current_recording_dir.mkdir(exist_ok=True)
            
            # Reset counters
            self.screenshot_count = 0
            
            # Start screenshot capture simulation (if enabled)
            if settings.get('capture_screenshots', False):
                await self.start_screenshot_capture()
            
            # Start system monitoring (if available and enabled)
            if HAS_SYSTEM_MONITOR and self.system_monitor and settings.get('system_monitoring', True):
                asyncio.create_task(self.system_monitor.start_monitoring())
                logger.info("System monitoring started")
                
                # Launch Task Manager if requested
                if settings.get('auto_launch_task_manager', True):
                    await self.task_manager.launch_task_manager()
                    logger.info("Task Manager launched automatically")
            
            await self.send_to_client(websocket, {
                "type": "recording_started",
                "session_id": str(id(self.recording_session)),
                "settings": settings
            })
            
            await self.broadcast_to_all({
                "type": "status_update",
                "status": "recording",
                "session_id": str(id(self.recording_session))
            })
            
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            traceback.print_exc()
            await self.send_to_client(websocket, {
                "type": "error",
                "message": f"Failed to start recording: {str(e)}"
            })
    
    async def stop_recording(self, websocket):
        """Stop recording session and save data."""
        try:
            if not self.recording_session:
                await self.send_to_client(websocket, {
                    "type": "error",
                    "message": "No recording session active"
                })
                return
            
            logger.info("Stopping recording session")
            
            if HAS_MKD:
                # Stop MKD recording session
                completed_session = self.session_manager.stop_recording()
                actions_count = len(completed_session.actions) if completed_session else 0
                
                # Save recording
                if completed_session and completed_session.actions:
                    script = AutomationScript(
                        name="Web Recording",
                        description=f"Recorded via web interface at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        created_at=datetime.now(),
                        actions=list(completed_session.actions)
                    )
                    
                    # Save to .mkd file
                    mkd_file = self.current_recording_dir / "recording.mkd"
                    self.script_storage.save(script, str(mkd_file))
                    
            else:
                # Mock session handling
                actions_count = len(self.recording_session.get("actions", []))
            
            # Stop screenshot capture
            await self.stop_screenshot_capture()
            
            # Stop system monitoring and get results
            system_events = []
            semantic_summary = {}
            if HAS_SYSTEM_MONITOR and self.system_monitor:
                await self.system_monitor.stop_monitoring()
                system_events = self.system_monitor.events.copy()
                semantic_summary = self.system_monitor.get_semantic_summary()
                logger.info(f"System monitoring stopped. Captured {len(system_events)} system events")
                
                # Close Task Manager if we opened it
                if self.task_manager:
                    await self.task_manager.close_task_manager()
            
            duration = time.time() - self.recording_start_time if self.recording_start_time else 0
            
            await self.send_to_client(websocket, {
                "type": "recording_stopped",
                "duration": duration,
                "actions": actions_count,
                "screenshots": self.screenshot_count,
                "recording_dir": str(self.current_recording_dir),
                "system_events": len(system_events),
                "semantic_summary": semantic_summary
            })
            
            await self.broadcast_to_all({
                "type": "status_update",
                "status": "stopped",
                "duration": duration,
                "actions": actions_count
            })
            
            # Reset recording state
            self.recording_session = None
            self.recording_start_time = None
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            traceback.print_exc()
            await self.send_to_client(websocket, {
                "type": "error",
                "message": f"Failed to stop recording: {str(e)}"
            })
    
    async def handle_action(self, action_data: Dict[str, Any]):
        """Handle action received from web client."""
        try:
            if not self.recording_session:
                return
            
            if HAS_MKD:
                # Create MKD Action object
                action = Action(
                    type=action_data['type'],
                    data=action_data['data'],
                    timestamp=action_data['timestamp']
                )
                
                # Add to current session
                self.session_manager.add_action(action)
            else:
                # Store in mock session
                self.recording_session["actions"].append(action_data)
            
        except Exception as e:
            logger.error(f"Error handling action: {e}")
            # Don't send error to client for actions to avoid spam
    
    async def start_screenshot_capture(self):
        """Start screenshot capture notification loop."""
        # Note: Actual screenshot capture happens on the client side
        # This just tracks the count for statistics
        async def capture_loop():
            while self.recording_session:
                await asyncio.sleep(0.5)  # 2 FPS notification rate
                self.screenshot_count += 1
                
                # Notify clients about screenshot count
                await self.broadcast_to_all({
                    "type": "screenshot_captured",
                    "count": self.screenshot_count
                })
        
        self.screenshot_task = asyncio.create_task(capture_loop())
    
    async def stop_screenshot_capture(self):
        """Stop screenshot capture."""
        if hasattr(self, 'screenshot_task'):
            self.screenshot_task.cancel()
            try:
                await self.screenshot_task
            except asyncio.CancelledError:
                pass
    
    async def send_recordings_list(self, websocket):
        """Send list of available recordings to client."""
        try:
            recordings = []
            
            # Scan recordings directory
            if self.recordings_dir.exists():
                for recording_dir in self.recordings_dir.iterdir():
                    if recording_dir.is_dir():
                        mkd_file = recording_dir / "recording.mkd"
                        if mkd_file.exists():
                            stat_info = mkd_file.stat()
                            recordings.append({
                                "id": recording_dir.name,
                                "name": recording_dir.name,
                                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                                "size": stat_info.st_size,
                                "path": str(mkd_file)
                            })
            
            # Sort by creation time (newest first)
            recordings.sort(key=lambda x: x['created'], reverse=True)
            
            await self.send_to_client(websocket, {
                "type": "recordings_list",
                "recordings": recordings
            })
            
        except Exception as e:
            logger.error(f"Error getting recordings list: {e}")
            await self.send_to_client(websocket, {
                "type": "error",
                "message": f"Failed to get recordings: {str(e)}"
            })
    
    async def load_recording(self, websocket, recording_id: str):
        """Load a specific recording for replay."""
        try:
            recording_dir = self.recordings_dir / recording_id
            mkd_file = recording_dir / "recording.mkd"
            
            if not mkd_file.exists():
                await self.send_to_client(websocket, {
                    "type": "error",
                    "message": f"Recording not found: {recording_id}"
                })
                return
            
            if HAS_MKD:
                # Load using MKD script storage
                script = self.script_storage.load(str(mkd_file))
                actions = [
                    {
                        "type": action.type,
                        "data": action.data,
                        "timestamp": action.timestamp
                    }
                    for action in script.actions
                ]
            else:
                # Mock data
                actions = [
                    {"type": "mock_action", "data": {"x": 100, "y": 100}, "timestamp": 0.0}
                ]
            
            await self.send_to_client(websocket, {
                "type": "recording_loaded",
                "recording_id": recording_id,
                "actions": actions,
                "frame_count": len(actions)  # Simplified
            })
            
        except Exception as e:
            logger.error(f"Error loading recording: {e}")
            await self.send_to_client(websocket, {
                "type": "error",
                "message": f"Failed to load recording: {str(e)}"
            })
    
    async def replay_actions(self, websocket, actions: list):
        """Execute replay of actions."""
        try:
            if not HAS_MKD or not self.action_executor:
                await self.send_to_client(websocket, {
                    "type": "error",
                    "message": "Action execution not available"
                })
                return
            
            logger.info(f"Starting replay of {len(actions)} actions")
            
            await self.send_to_client(websocket, {
                "type": "replay_started",
                "action_count": len(actions)
            })
            
            # Execute actions sequentially
            for i, action_data in enumerate(actions):
                try:
                    action = Action(
                        type=action_data['type'],
                        data=action_data['data'],
                        timestamp=action_data['timestamp']
                    )
                    
                    # Execute action
                    await self.action_executor.execute_action(action)
                    
                    # Send progress update
                    await self.send_to_client(websocket, {
                        "type": "replay_progress",
                        "current": i + 1,
                        "total": len(actions)
                    })
                    
                    # Wait for timing
                    if i < len(actions) - 1:
                        next_timestamp = actions[i + 1]['timestamp']
                        current_timestamp = action_data['timestamp']
                        delay = next_timestamp - current_timestamp
                        if delay > 0:
                            await asyncio.sleep(delay)
                
                except Exception as e:
                    logger.warning(f"Error executing action {i}: {e}")
            
            await self.send_to_client(websocket, {
                "type": "replay_completed",
                "actions_executed": len(actions)
            })
            
        except Exception as e:
            logger.error(f"Error during replay: {e}")
            await self.send_to_client(websocket, {
                "type": "error",
                "message": f"Replay failed: {str(e)}"
            })
    
    async def save_video_data(self, websocket, video_data: str, recording_id: str = None):
        """Save video data received from client."""
        try:
            if not recording_id:
                recording_id = datetime.now().strftime("web_recording_%Y%m%d_%H%M%S")
            
            recording_dir = self.recordings_dir / recording_id
            recording_dir.mkdir(exist_ok=True)
            
            # Save video data (base64 encoded)
            video_file = recording_dir / "recording.webm"
            
            # Decode base64 and save
            import base64
            video_bytes = base64.b64decode(video_data.split(',')[1] if ',' in video_data else video_data)
            
            with open(video_file, 'wb') as f:
                f.write(video_bytes)
            
            logger.info(f"Saved video to {video_file}")
            
            await self.send_to_client(websocket, {
                "type": "video_saved",
                "recording_id": recording_id,
                "path": str(video_file),
                "size": len(video_bytes)
            })
            
        except Exception as e:
            logger.error(f"Error saving video data: {e}")
            await self.send_to_client(websocket, {
                "type": "error",
                "message": f"Failed to save video: {str(e)}"
            })
    
    async def save_screenshot_data(self, websocket, screenshots: list, recording_id: str = None):
        """Save screenshot data received from client."""
        try:
            if not recording_id:
                recording_id = datetime.now().strftime("web_recording_%Y%m%d_%H%M%S")
            
            recording_dir = self.recordings_dir / recording_id
            recording_dir.mkdir(exist_ok=True)
            screenshots_dir = recording_dir / "screenshots"
            screenshots_dir.mkdir(exist_ok=True)
            
            import base64
            
            for i, screenshot in enumerate(screenshots):
                # Save each screenshot
                screenshot_file = screenshots_dir / f"screenshot_{i:04d}.jpg"
                
                # Decode base64 and save
                img_data = screenshot.get('data', '')
                if img_data:
                    img_bytes = base64.b64decode(img_data.split(',')[1] if ',' in img_data else img_data)
                    
                    with open(screenshot_file, 'wb') as f:
                        f.write(img_bytes)
            
            logger.info(f"Saved {len(screenshots)} screenshots to {screenshots_dir}")
            
            await self.send_to_client(websocket, {
                "type": "screenshots_saved",
                "recording_id": recording_id,
                "path": str(screenshots_dir),
                "count": len(screenshots)
            })
            
        except Exception as e:
            logger.error(f"Error saving screenshots: {e}")
            await self.send_to_client(websocket, {
                "type": "error",
                "message": f"Failed to save screenshots: {str(e)}"
            })
    
    async def get_system_status(self, websocket):
        """Get current system status"""
        try:
            if not HAS_SYSTEM_MONITOR:
                await self.send_to_client(websocket, {
                    "type": "error",
                    "message": "System monitoring not available"
                })
                return
            
            # Get current system info
            import psutil
            status = {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent if sys.platform != 'win32' else psutil.disk_usage('C:').percent,
                "process_count": len(psutil.pids()),
                "system_monitor_active": self.system_monitor.is_monitoring if self.system_monitor else False
            }
            
            await self.send_to_client(websocket, {
                "type": "system_status",
                "status": status
            })
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            await self.send_to_client(websocket, {
                "type": "error",
                "message": f"Failed to get system status: {str(e)}"
            })
    
    async def launch_task_manager(self, websocket):
        """Launch Task Manager"""
        try:
            if not HAS_SYSTEM_MONITOR or not self.task_manager:
                await self.send_to_client(websocket, {
                    "type": "error", 
                    "message": "Task Manager integration not available"
                })
                return
            
            success = await self.task_manager.launch_task_manager()
            
            await self.send_to_client(websocket, {
                "type": "task_manager_launched",
                "success": success,
                "pid": self.task_manager.task_manager_pid
            })
            
        except Exception as e:
            logger.error(f"Error launching Task Manager: {e}")
            await self.send_to_client(websocket, {
                "type": "error",
                "message": f"Failed to launch Task Manager: {str(e)}"
            })
    
    async def get_process_list(self, websocket):
        """Get current process list"""
        try:
            if not HAS_SYSTEM_MONITOR or not self.task_manager:
                await self.send_to_client(websocket, {
                    "type": "error",
                    "message": "Process monitoring not available"
                })
                return
            
            processes = self.task_manager.get_process_list()
            
            await self.send_to_client(websocket, {
                "type": "process_list",
                "processes": processes[:50]  # Send top 50 processes
            })
            
        except Exception as e:
            logger.error(f"Error getting process list: {e}")
            await self.send_to_client(websocket, {
                "type": "error", 
                "message": f"Failed to get process list: {str(e)}"
            })
    
    async def analyze_user_action(self, websocket, action):
        """Analyze user action for semantic meaning"""
        try:
            if not HAS_SYSTEM_MONITOR or not self.system_monitor:
                await self.send_to_client(websocket, {
                    "type": "error",
                    "message": "System monitoring not available for action analysis"
                })
                return
            
            # Correlate action with system events
            correlated_event = self.system_monitor.correlate_with_user_action(action)
            
            analysis = {
                "user_action": action,
                "timestamp": action.get('timestamp', time.time()),
                "correlated_system_event": correlated_event.__dict__ if correlated_event else None,
                "semantic_meaning": correlated_event.semantic_action if correlated_event else "Low-level input action"
            }
            
            # Check for hotkey patterns
            if action.get('type') == 'key_down':
                # This would need to be enhanced to detect key combinations
                key = action.get('data', {}).get('key', '')
                if key:
                    analysis['hotkey_analysis'] = f"Key press: {key}"
            
            await self.send_to_client(websocket, {
                "type": "action_analysis",
                "analysis": analysis
            })
            
        except Exception as e:
            logger.error(f"Error analyzing user action: {e}")
            await self.send_to_client(websocket, {
                "type": "error",
                "message": f"Failed to analyze action: {str(e)}"
            })

    async def handle_client(self, websocket, path=None):
        """Handle individual client connection."""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed normally")
        except Exception as e:
            logger.error(f"Error in client handler: {e}")
        finally:
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """Start the WebSocket server."""
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=10
        )
        
        logger.info("WebSocket server started successfully")
        return server


async def main():
    """Main entry point."""
    backend = WebGUIBackend()
    
    try:
        server = await backend.start_server()
        
        logger.info("Server running. Press Ctrl+C to stop.")
        
        # Keep server running
        await server.wait_closed()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    # Check for websockets dependency
    try:
        import websockets
    except ImportError:
        print("Error: websockets library not found")
        print("Install with: pip install websockets")
        sys.exit(1)
    
    asyncio.run(main())