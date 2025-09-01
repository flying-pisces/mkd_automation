#!/usr/bin/env python3
"""
Chrome Extension Connection Test

This script simulates Chrome extension messages to test the connection
between the Chrome extension and Python native messaging host.
"""

import json
import logging
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional
import queue
import tempfile

# Add src to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


class ChromeExtensionSimulator:
    """Simulates Chrome extension communication with native messaging host."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.message_id = 0
        self.host_process = None
        self.response_queue = queue.Queue()
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)-8s %(message)s'
        )
    
    def generate_message_id(self) -> str:
        """Generate unique message ID."""
        self.message_id += 1
        return f"chrome_test_{int(time.time())}_{self.message_id}"
    
    def start_native_host(self) -> bool:
        """Start the native messaging host process."""
        try:
            import os
            
            # Path to native host script
            host_script = project_root / "src" / "mkd_v2" / "native_host" / "host.py"
            
            if not host_script.exists():
                print(f"[FAIL] Native host script not found: {host_script}")
                return False
            
            # Set up environment
            env = os.environ.copy()
            env["PYTHONPATH"] = str(project_root / "src")
            
            # Start the host process
            self.host_process = subprocess.Popen(
                [sys.executable, "-m", "mkd_v2.native_host.host", "--debug"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=project_root,
                env=env
            )
            
            print("[OK] Native messaging host process started")
            
            # Give the process a moment to initialize
            time.sleep(1)
            
            # Check if process is still running
            if self.host_process.poll() is not None:
                # Process died, read stderr for error
                stderr_output = self.host_process.stderr.read().decode('utf-8', errors='ignore')
                print(f"[FAIL] Native host process died immediately")
                print(f"       Error output: {stderr_output}")
                return False
            
            print("[OK] Native messaging host is running")
            
            # Start response reader thread
            self.response_thread = threading.Thread(
                target=self._read_responses, 
                daemon=True
            )
            self.response_thread.start()
            
            return True
            
        except Exception as e:
            print(f"[FAIL] Failed to start native host: {e}")
            return False
    
    def stop_native_host(self):
        """Stop the native messaging host process."""
        if self.host_process:
            try:
                self.host_process.terminate()
                self.host_process.wait(timeout=5)
                print("[OK] Native messaging host stopped")
            except subprocess.TimeoutExpired:
                self.host_process.kill()
                print("[WARN] Native messaging host killed (timeout)")
            except Exception as e:
                print(f"[WARN] Error stopping native host: {e}")
    
    def send_message(self, command: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Send message to native host and wait for response.
        
        Args:
            command: Command to send
            params: Command parameters
            
        Returns:
            Response dictionary or None if failed
        """
        if not self.host_process or self.host_process.poll() is not None:
            print("[FAIL] Native host not running")
            return None
        
        message_id = self.generate_message_id()
        message = {
            'id': message_id,
            'command': command,
            'params': params or {},
            'timestamp': time.time()
        }
        
        try:
            # Serialize message
            message_json = json.dumps(message, default=str)
            message_bytes = message_json.encode('utf-8')
            
            # Send length header (4 bytes, little endian)
            length_bytes = struct.pack('=I', len(message_bytes))
            self.host_process.stdin.write(length_bytes)
            
            # Send message content
            self.host_process.stdin.write(message_bytes)
            self.host_process.stdin.flush()
            
            print(f"[SEND] {command} (id: {message_id})")
            
            # Wait for response
            try:
                response = self.response_queue.get(timeout=10)
                if response and response.get('id') == message_id:
                    print(f"[RECV] Response for {command}: {response.get('success', 'unknown')}")
                    return response
                else:
                    print(f"[FAIL] No matching response for {command}")
                    return None
            except queue.Empty:
                print(f"[FAIL] Timeout waiting for response to {command}")
                return None
                
        except Exception as e:
            print(f"[FAIL] Error sending {command}: {e}")
            return None
    
    def _read_responses(self):
        """Read responses from native host in background thread."""
        try:
            while self.host_process and self.host_process.poll() is None:
                try:
                    # Read message length (4 bytes)
                    length_data = self.host_process.stdout.read(4)
                    if not length_data or len(length_data) != 4:
                        break
                    
                    message_length = struct.unpack('=I', length_data)[0]
                    
                    if message_length == 0 or message_length > 1024 * 1024:
                        print(f"[WARN] Invalid message length: {message_length}")
                        continue
                    
                    # Read message content
                    message_data = self.host_process.stdout.read(message_length)
                    if len(message_data) != message_length:
                        print(f"[WARN] Incomplete message read")
                        continue
                    
                    # Parse response
                    response = json.loads(message_data.decode('utf-8'))
                    self.response_queue.put(response)
                    
                except json.JSONDecodeError as e:
                    print(f"[WARN] Invalid JSON response: {e}")
                except Exception as e:
                    print(f"[WARN] Error reading response: {e}")
                    break
                    
        except Exception as e:
            print(f"[WARN] Response reader error: {e}")
    
    def test_connection(self) -> bool:
        """Test basic connection with PING."""
        response = self.send_message('PING')
        if not response:
            return False
            
        if not response.get('success'):
            print(f"[FAIL] PING failed: {response.get('error', 'unknown')}")
            return False
        
        data = response.get('data', {})
        if data.get('status') != 'alive':
            print(f"[FAIL] PING response invalid: {data}")
            return False
        
        print(f"[OK] PING successful - host version {data.get('version', 'unknown')}")
        return True
    
    def test_get_status(self) -> bool:
        """Test GET_STATUS command."""
        response = self.send_message('GET_STATUS')
        if not response:
            return False
            
        if not response.get('success'):
            print(f"[FAIL] GET_STATUS failed: {response.get('error', 'unknown')}")
            return False
        
        data = response.get('data', {})
        required_sections = ['host', 'engine', 'broker']
        missing_sections = [s for s in required_sections if s not in data]
        
        if missing_sections:
            print(f"[FAIL] GET_STATUS missing sections: {missing_sections}")
            return False
        
        print(f"[OK] GET_STATUS successful - host running: {data['host'].get('running')}")
        return True
    
    def test_get_connection_status(self) -> bool:
        """Test GET_CONNECTION_STATUS command."""
        response = self.send_message('GET_CONNECTION_STATUS')
        if not response:
            return False
            
        if not response.get('success'):
            print(f"[FAIL] GET_CONNECTION_STATUS failed: {response.get('error', 'unknown')}")
            return False
        
        data = response.get('data', {})
        if not data.get('isConnected'):
            print(f"[FAIL] Connection status shows not connected: {data}")
            return False
        
        print(f"[OK] GET_CONNECTION_STATUS successful - connected: {data.get('isConnected')}")
        return True
    
    def test_recording_workflow(self) -> bool:
        """Test complete recording workflow."""
        print("\n--- Testing Recording Workflow ---")
        
        # Start recording
        print("1. Starting recording...")
        start_response = self.send_message('START_RECORDING', {
            'user_id': 1,
            'config': {
                'capture_video': True,
                'capture_audio': False,
                'show_border': True,
                'border_color': '#FF0000'
            }
        })
        
        if not start_response or not start_response.get('success'):
            print(f"[FAIL] START_RECORDING failed: {start_response.get('error') if start_response else 'no response'}")
            return False
        
        session_data = start_response.get('data', {})
        session_id = session_data.get('sessionId')
        
        if not session_id:
            print(f"[FAIL] No session ID in start response: {session_data}")
            return False
        
        print(f"[OK] Recording started - session: {session_id}")
        
        # Wait a bit for recording
        time.sleep(2)
        
        # Check status during recording
        print("2. Checking status during recording...")
        status_response = self.send_message('GET_STATUS')
        if status_response and status_response.get('success'):
            status_data = status_response.get('data', {})
            engine_status = status_data.get('engine', {})
            print(f"[OK] Recording status: {engine_status.get('state', 'unknown')}")
        
        # Stop recording
        print("3. Stopping recording...")
        stop_response = self.send_message('STOP_RECORDING')
        
        if not stop_response or not stop_response.get('success'):
            print(f"[FAIL] STOP_RECORDING failed: {stop_response.get('error') if stop_response else 'no response'}")
            return False
        
        stop_data = stop_response.get('data', {})
        file_path = stop_data.get('filePath')
        
        if not file_path:
            print(f"[FAIL] No file path in stop response: {stop_data}")
            return False
        
        print(f"[OK] Recording stopped - file: {Path(file_path).name}")
        print(f"[OK] Event count: {stop_data.get('eventCount', 0)}")
        print(f"[OK] Duration: {stop_data.get('duration', 0):.2f}s")
        
        return True
    
    def run_all_tests(self) -> bool:
        """Run all connection tests."""
        print("Chrome Extension Connection Test")
        print("=" * 50)
        
        self.setup_logging()
        
        # Start native host
        if not self.start_native_host():
            return False
        
        try:
            # Give host time to start
            time.sleep(1)
            
            # Test basic connection
            print("\n--- Testing Basic Connection ---")
            if not self.test_connection():
                return False
            
            # Test status commands
            print("\n--- Testing Status Commands ---")
            if not self.test_get_status():
                return False
            
            if not self.test_get_connection_status():
                return False
            
            # Test recording workflow
            if not self.test_recording_workflow():
                return False
            
            print("\n[OK] All connection tests passed!")
            print("The Chrome extension should be able to communicate with Python backend.")
            
            return True
            
        finally:
            # Clean up
            self.stop_native_host()


def main():
    """Main entry point."""
    simulator = ChromeExtensionSimulator()
    success = simulator.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()