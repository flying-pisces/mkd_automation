"""
Native Messaging Host Implementation.

Handles communication between Chrome extension and Python backend
using Chrome's native messaging protocol.
"""

import sys
import json
import logging
import threading
import struct
from typing import Dict, Any, Optional, Callable
from pathlib import Path

from ..core.message_broker import MessageBroker
from ..core.session_manager import SessionManager
from ..recording.recording_engine import RecordingEngine

logger = logging.getLogger(__name__)


class NativeHost:
    """
    Native messaging host for Chrome extension communication.
    
    Implements Chrome's native messaging protocol for bi-directional
    communication between the extension and Python backend.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".mkd"
        self.running = False
        
        # Initialize core components
        self.message_broker = MessageBroker()
        self.session_manager = SessionManager(storage_path=self.storage_path)
        self.recording_engine = RecordingEngine(self.session_manager)
        
        # Message processing
        self._lock = threading.RLock()
        self.message_handlers = {}
        
        # Setup message handlers
        self._setup_handlers()
        
        logger.info(f"NativeHost initialized with storage: {self.storage_path}")
    
    def _setup_handlers(self):
        """Setup message handlers for different command types."""
        self.message_handlers = {
            'START_RECORDING': self._handle_start_recording,
            'STOP_RECORDING': self._handle_stop_recording,
            'PAUSE_RECORDING': self._handle_pause_recording,
            'RESUME_RECORDING': self._handle_resume_recording,
            'GET_STATUS': self._handle_get_status,
            'GET_CAPABILITIES': self._handle_get_capabilities,
            'AUTHENTICATE': self._handle_authenticate,
            'PING': self._handle_ping
        }
    
    def start(self):
        """Start the native messaging host."""
        try:
            self.running = True
            
            # Start message broker
            self.message_broker.start()
            
            logger.info("Native messaging host started")
            
            # Main message processing loop
            self._message_loop()
            
        except Exception as e:
            logger.error(f"Native host startup failed: {e}")
            self._send_error_response(None, f"Startup failed: {e}")
            sys.exit(1)
    
    def stop(self):
        """Stop the native messaging host."""
        self.running = False
        
        try:
            # Clean up components
            if hasattr(self, 'recording_engine'):
                self.recording_engine.cleanup()
            
            if hasattr(self, 'message_broker'):
                self.message_broker.stop()
            
            logger.info("Native messaging host stopped")
            
        except Exception as e:
            logger.error(f"Error during host shutdown: {e}")
    
    def _message_loop(self):
        """Main message processing loop."""
        logger.info("Starting message loop")
        while self.running:
            try:
                # Read message from Chrome extension
                message = self._read_message()
                if message is None:
                    # EOF or invalid message - extension disconnected
                    logger.info("Received null message, exiting loop.")
                    break
                
                # Process message
                self._process_message(message)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except EOFError:
                logger.info("Extension disconnected")
                break
            except Exception as e:
                logger.error(f"Error in message loop: {e}")
                self._send_error_response(None, f"Message processing error: {e}")
        
        logger.info("Exited message loop")
        self.stop()
    
    def _read_message(self) -> Optional[Dict[str, Any]]:
        """
        Read message from Chrome extension using native messaging protocol.
        
        Returns:
            Parsed message dictionary or None if connection closed
        """
        try:
            # Read message length (4 bytes, little endian)
            logger.info("Waiting for message length...")
            raw_length = sys.stdin.buffer.read(4)
            logger.info(f"Read raw_length: {raw_length}")
            if not raw_length or len(raw_length) != 4:
                return None
            
            message_length = struct.unpack('=I', raw_length)[0]
            logger.info(f"Message length: {message_length}")
            
            # Validate message length
            if message_length == 0 or message_length > 1024 * 1024:  # Max 1MB
                logger.error(f"Invalid message length: {message_length}")
                return None
            
            # Read message content
            raw_message = sys.stdin.buffer.read(message_length)
            if len(raw_message) != message_length:
                logger.error(f"Incomplete message read: {len(raw_message)}/{message_length}")
                return None
            
            # Parse JSON
            message_text = raw_message.decode('utf-8')
            message = json.loads(message_text)
            
            logger.debug(f"Received message: {message.get('command', 'unknown')} (id: {message.get('id')})")
            return message
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading message: {e}")
            return None
    
    def _send_message(self, message: Dict[str, Any]):
        """
        Send message to Chrome extension using native messaging protocol.
        
        Args:
            message: Message dictionary to send
        """
        try:
            # Serialize message
            message_json = json.dumps(message, default=str)
            message_bytes = message_json.encode('utf-8')
            
            # Send message length (4 bytes, little endian)
            length_bytes = struct.pack('=I', len(message_bytes))
            sys.stdout.buffer.write(length_bytes)
            
            # Send message content
            sys.stdout.buffer.write(message_bytes)
            sys.stdout.buffer.flush()
            
            logger.debug(f"Sent message: {message.get('type', 'response')} (id: {message.get('id')})")
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    def _process_message(self, message: Dict[str, Any]):
        """
        Process incoming message from Chrome extension.
        
        Args:
            message: Message dictionary from extension
        """
        try:
            message_id = message.get('id')
            command = message.get('command')
            params = message.get('params', {})
            
            logger.info(f"Processing command: {command} (id: {message_id})")
            
            # Find handler for command
            handler = self.message_handlers.get(command)
            if not handler:
                self._send_error_response(message_id, f"Unknown command: {command}")
                return
            
            # Execute handler
            with self._lock:
                result = handler(params)
            
            # Send response
            self._send_success_response(message_id, result)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self._send_error_response(message.get('id'), str(e))
    
    def _send_success_response(self, message_id: str, data: Any):
        """Send success response to Chrome extension."""
        response = {
            'id': message_id,
            'type': 'response',
            'success': True,
            'data': data,
            'timestamp': self._get_timestamp()
        }
        self._send_message(response)
    
    def _send_error_response(self, message_id: str, error: str):
        """Send error response to Chrome extension."""
        response = {
            'id': message_id,
            'type': 'response',
            'success': False,
            'error': error,
            'timestamp': self._get_timestamp()
        }
        self._send_message(response)
    
    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        import time
        return time.time()
    
    # Message Handlers
    
    def _handle_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping command."""
        return {
            'status': 'alive',
            'timestamp': self._get_timestamp(),
            'version': '2.0.0'
        }
    
    def _handle_get_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get status command."""
        try:
            engine_status = self.recording_engine.get_status()
            broker_status = self.message_broker.get_status() if hasattr(self.message_broker, 'get_status') else {'running': True}
            
            return {
                'host': {
                    'running': self.running,
                    'storage_path': str(self.storage_path),
                    'version': '2.0.0'
                },
                'engine': engine_status,
                'broker': broker_status
            }
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {
                'host': {
                    'running': self.running,
                    'version': '2.0.0',
                    'error': str(e)
                }
            }
    
    def _handle_get_capabilities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get capabilities command."""
        try:
            platform_caps = self.recording_engine.platform.get_capabilities()
            
            return {
                'platform': platform_caps,
                'recording': {
                    'formats': ['mkd', 'json'],
                    'video_capture': False,  # Week 2 feature
                    'audio_capture': False,  # Week 2 feature
                    'visual_indicators': True,
                    'context_detection': True
                },
                'playback': {
                    'supported': False,  # Week 3 feature
                    'formats': []
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting capabilities: {e}")
            return {'error': str(e)}
    
    def _handle_authenticate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user authentication."""
        try:
            username = params.get('username')
            password = params.get('password')
            
            if not username or not password:
                return {'error': 'Username and password required'}
            
            user = self.session_manager.authenticate_user(username, password)
            if user:
                return {
                    'authenticated': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'role': user.role.value
                    }
                }
            else:
                return {
                    'authenticated': False,
                    'error': 'Invalid credentials'
                }
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {'error': str(e)}
    
    def _handle_start_recording(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle start recording command."""
        try:
            user_id = params.get('user_id', 1)  # Default to admin user
            config = params.get('config', {})
            
            result = self.recording_engine.start_recording(user_id, config)
            return result
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return {'error': str(e)}
    
    def _handle_stop_recording(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stop recording command."""
        try:
            result = self.recording_engine.stop_recording()
            return result
            
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return {'error': str(e)}
    
    def _handle_pause_recording(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pause recording command."""
        try:
            result = self.recording_engine.pause_recording()
            return result
            
        except Exception as e:
            logger.error(f"Failed to pause recording: {e}")
            return {'error': str(e)}
    
    def _handle_resume_recording(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resume recording command."""
        try:
            result = self.recording_engine.resume_recording()
            return result
            
        except Exception as e:
            logger.error(f"Failed to resume recording: {e}")
            return {'error': str(e)}


def main():
    """Main entry point for native messaging host."""
    import argparse
    
    # Setup logging
    log_file = Path.home() / '.mkd' / 'native_host.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stderr)
        ]
    )
    logger.info("--- Native Host Starting ---")

    parser = argparse.ArgumentParser(description='MKD Automation Native Messaging Host')
    parser.add_argument('--storage', type=str, help='Storage directory path')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create storage directory
    storage_path = Path(args.storage) if args.storage else Path.home() / '.mkd'
    storage_path.mkdir(parents=True, exist_ok=True)
    
    # Start native host
    try:
        host = NativeHost(storage_path=storage_path)
        host.start()
    except KeyboardInterrupt:
        logger.info("Native host interrupted")
    except Exception as e:
        logger.error(f"Native host failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()