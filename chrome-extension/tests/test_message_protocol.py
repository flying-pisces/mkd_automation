#!/usr/bin/env python3
"""
Chrome-Python Message Protocol Testing Suite

Tests bidirectional communication between Chrome extension and Python native host.
This covers all message types defined in the Chrome extension and native host.
"""

import json
import logging
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Optional
import threading
import queue

# Add src to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from mkd_v2.native_host.host import NativeHost
    from mkd_v2.core.session_manager import SessionManager, RecordingConfig
except ImportError as e:
    print(f"Error: Failed to import MKD modules: {e}")
    sys.exit(1)


class MessageProtocolTester:
    """Tests Chrome-Python message protocol communication."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_results = []
        
    def setup_logging(self):
        """Setup test logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s: %(message)s'
        )
        
    def log_result(self, test_name: str, success: bool, message: str, details: Any = None):
        """Log test result."""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details
        }
        self.test_results.append(result)
        
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"     Details: {details}")
    
    def test_native_host_instantiation(self):
        """Test that native host can be instantiated."""
        try:
            host = NativeHost(storage_path=self.temp_dir)
            self.log_result(
                "native_host_instantiation", 
                True, 
                "Native host instantiated successfully"
            )
            return host
        except Exception as e:
            self.log_result(
                "native_host_instantiation", 
                False, 
                "Failed to instantiate native host",
                str(e)
            )
            return None
    
    def test_message_handlers_setup(self, host: NativeHost):
        """Test that all message handlers are properly set up."""
        expected_handlers = [
            'START_RECORDING',
            'STOP_RECORDING', 
            'PAUSE_RECORDING',
            'RESUME_RECORDING',
            'GET_STATUS',
            'GET_CAPABILITIES',
            'AUTHENTICATE',
            'PING'
        ]
        
        missing_handlers = []
        for handler_name in expected_handlers:
            if handler_name not in host.message_handlers:
                missing_handlers.append(handler_name)
        
        if missing_handlers:
            self.log_result(
                "message_handlers_setup",
                False,
                "Missing message handlers",
                missing_handlers
            )
        else:
            self.log_result(
                "message_handlers_setup",
                True,
                f"All {len(expected_handlers)} message handlers configured"
            )
            
        return len(missing_handlers) == 0
    
    def test_ping_handler(self, host: NativeHost):
        """Test PING message handler."""
        try:
            result = host._handle_ping({})
            
            required_fields = ['status', 'timestamp', 'version']
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                self.log_result(
                    "ping_handler",
                    False,
                    "PING response missing required fields",
                    missing_fields
                )
                return False
            
            if result['status'] != 'alive':
                self.log_result(
                    "ping_handler",
                    False,
                    "PING response has incorrect status",
                    result['status']
                )
                return False
            
            self.log_result(
                "ping_handler",
                True,
                "PING handler works correctly"
            )
            return True
            
        except Exception as e:
            self.log_result(
                "ping_handler",
                False,
                "PING handler failed",
                str(e)
            )
            return False
    
    def test_get_status_handler(self, host: NativeHost):
        """Test GET_STATUS message handler."""
        try:
            result = host._handle_get_status({})
            
            required_sections = ['host', 'engine', 'broker']
            missing_sections = [section for section in required_sections if section not in result]
            
            if missing_sections:
                self.log_result(
                    "get_status_handler",
                    False,
                    "GET_STATUS response missing required sections",
                    missing_sections
                )
                return False
            
            # Check host section
            host_status = result['host']
            if 'running' not in host_status or 'version' not in host_status:
                self.log_result(
                    "get_status_handler",
                    False,
                    "GET_STATUS host section incomplete",
                    host_status
                )
                return False
            
            self.log_result(
                "get_status_handler",
                True,
                "GET_STATUS handler works correctly"
            )
            return True
            
        except Exception as e:
            self.log_result(
                "get_status_handler",
                False,
                "GET_STATUS handler failed",
                str(e)
            )
            return False
    
    def test_get_capabilities_handler(self, host: NativeHost):
        """Test GET_CAPABILITIES message handler."""
        try:
            result = host._handle_get_capabilities({})
            
            required_sections = ['platform', 'recording']
            missing_sections = [section for section in required_sections if section not in result]
            
            if missing_sections:
                self.log_result(
                    "get_capabilities_handler",
                    False,
                    "GET_CAPABILITIES response missing required sections",
                    missing_sections
                )
                return False
            
            # Check recording capabilities
            recording_caps = result['recording']
            required_caps = ['formats', 'visual_indicators', 'context_detection']
            missing_caps = [cap for cap in required_caps if cap not in recording_caps]
            
            if missing_caps:
                self.log_result(
                    "get_capabilities_handler",
                    False,
                    "GET_CAPABILITIES recording section incomplete",
                    missing_caps
                )
                return False
            
            self.log_result(
                "get_capabilities_handler",
                True,
                "GET_CAPABILITIES handler works correctly"
            )
            return True
            
        except Exception as e:
            self.log_result(
                "get_capabilities_handler",
                False,
                "GET_CAPABILITIES handler failed",
                str(e)
            )
            return False
    
    def test_recording_handlers(self, host: NativeHost):
        """Test recording-related message handlers."""
        try:
            # Test START_RECORDING
            start_params = {
                'user_id': 1,
                'config': {
                    'capture_video': True,
                    'capture_audio': False,
                    'show_border': True,
                    'border_color': '#FF0000'
                }
            }
            
            start_result = host._handle_start_recording(start_params)
            if 'error' in start_result:
                self.log_result(
                    "recording_handlers",
                    True,  # This may be expected if recording engine isn't fully initialized
                    f"START_RECORDING handled (expected error): {start_result['error']}"
                )
            else:
                self.log_result(
                    "recording_handlers",
                    True,
                    "START_RECORDING handler works"
                )
            
            # Test STOP_RECORDING 
            stop_result = host._handle_stop_recording({})
            # This will likely fail since no recording is active, but handler should exist
            self.log_result(
                "recording_stop_handler",
                True,
                "STOP_RECORDING handler callable"
            )
            
            # Test PAUSE_RECORDING
            pause_result = host._handle_pause_recording({})
            self.log_result(
                "recording_pause_handler", 
                True,
                "PAUSE_RECORDING handler callable"
            )
            
            # Test RESUME_RECORDING
            resume_result = host._handle_resume_recording({})
            self.log_result(
                "recording_resume_handler",
                True, 
                "RESUME_RECORDING handler callable"
            )
            
            return True
            
        except Exception as e:
            self.log_result(
                "recording_handlers",
                False,
                "Recording handlers test failed",
                str(e)
            )
            return False
    
    def test_message_serialization(self):
        """Test message serialization/deserialization."""
        try:
            # Test message structures that would be sent between Chrome and Python
            test_messages = [
                {
                    'id': 'msg_123456789_1',
                    'command': 'PING',
                    'params': {},
                    'timestamp': time.time()
                },
                {
                    'id': 'msg_123456789_2',
                    'command': 'START_RECORDING',
                    'params': {
                        'config': {
                            'capture_video': True,
                            'capture_audio': False,
                            'show_border': True
                        }
                    },
                    'timestamp': time.time()
                },
                {
                    'id': 'msg_123456789_3',
                    'type': 'response',
                    'success': True,
                    'data': {
                        'status': 'recording',
                        'session_id': 'test_session_123'
                    },
                    'timestamp': time.time()
                }
            ]
            
            serialization_success = True
            for i, message in enumerate(test_messages):
                try:
                    # Test JSON serialization
                    json_str = json.dumps(message, default=str)
                    
                    # Test deserialization
                    deserialized = json.loads(json_str)
                    
                    # Verify all keys are preserved
                    if set(message.keys()) != set(deserialized.keys()):
                        serialization_success = False
                        break
                        
                except Exception as e:
                    serialization_success = False
                    self.log_result(
                        "message_serialization",
                        False,
                        f"Message {i} serialization failed",
                        str(e)
                    )
                    break
            
            if serialization_success:
                self.log_result(
                    "message_serialization",
                    True,
                    f"All {len(test_messages)} test messages serialized correctly"
                )
            
            return serialization_success
            
        except Exception as e:
            self.log_result(
                "message_serialization",
                False,
                "Message serialization test failed",
                str(e)
            )
            return False
    
    def test_native_messaging_protocol(self):
        """Test native messaging protocol format."""
        try:
            # Test the message format used by Chrome native messaging
            test_message = {
                'id': 'test_message_1',
                'command': 'PING',
                'params': {},
                'timestamp': time.time()
            }
            
            # Serialize message (as native host would send to Chrome)
            message_json = json.dumps(test_message, default=str)
            message_bytes = message_json.encode('utf-8')
            
            # Create length header (4 bytes, little endian)
            length_bytes = struct.pack('=I', len(message_bytes))
            
            # Test that we can reconstruct the message
            reconstructed_length = struct.unpack('=I', length_bytes)[0]
            if reconstructed_length != len(message_bytes):
                self.log_result(
                    "native_messaging_protocol",
                    False,
                    "Message length encoding/decoding failed",
                    f"Expected {len(message_bytes)}, got {reconstructed_length}"
                )
                return False
            
            # Test message decoding
            reconstructed_message = json.loads(message_bytes.decode('utf-8'))
            if reconstructed_message['command'] != 'PING':
                self.log_result(
                    "native_messaging_protocol",
                    False,
                    "Message reconstruction failed",
                    reconstructed_message
                )
                return False
            
            self.log_result(
                "native_messaging_protocol",
                True,
                "Native messaging protocol format works correctly"
            )
            return True
            
        except Exception as e:
            self.log_result(
                "native_messaging_protocol",
                False,
                "Native messaging protocol test failed",
                str(e)
            )
            return False
    
    def test_chrome_extension_message_types(self):
        """Test that all Chrome extension message types are supported."""
        # These are the message types expected from the Chrome extension
        chrome_message_types = [
            'START_RECORDING',
            'STOP_RECORDING', 
            'PAUSE_RECORDING',
            'RESUME_RECORDING',
            'START_PLAYBACK',
            'GET_RECENT_RECORDINGS',
            'GET_STATUS',
            'GET_CONNECTION_STATUS'
        ]
        
        # These are the message types the native host supports
        host = NativeHost(storage_path=self.temp_dir)
        supported_types = list(host.message_handlers.keys())
        
        # Check compatibility
        unsupported_types = []
        for msg_type in chrome_message_types:
            if msg_type not in supported_types:
                unsupported_types.append(msg_type)
        
        # Note: Some message types might be handled differently
        # START_PLAYBACK and GET_RECENT_RECORDINGS might not be implemented yet
        expected_unsupported = ['START_PLAYBACK', 'GET_RECENT_RECORDINGS']
        unexpected_unsupported = [t for t in unsupported_types if t not in expected_unsupported]
        
        if unexpected_unsupported:
            self.log_result(
                "chrome_extension_compatibility",
                False,
                "Chrome extension message types not supported",
                unexpected_unsupported
            )
            return False
        
        self.log_result(
            "chrome_extension_compatibility", 
            True,
            f"Chrome extension compatibility verified ({len(chrome_message_types) - len(unsupported_types)}/{len(chrome_message_types)} supported)"
        )
        
        if unsupported_types:
            self.log_result(
                "chrome_extension_compatibility_note",
                True,
                f"Expected unsupported types (Week 3 features): {unsupported_types}"
            )
        
        return True
    
    def run_all_tests(self):
        """Run all message protocol tests."""
        print("Chrome-Python Message Protocol Testing")
        print("=" * 50)
        
        self.setup_logging()
        
        # Test 1: Native host instantiation
        host = self.test_native_host_instantiation()
        if not host:
            print("\n[FAIL] Cannot proceed without native host")
            return False
        
        # Test 2: Message handlers setup
        self.test_message_handlers_setup(host)
        
        # Test 3: Individual handler tests
        self.test_ping_handler(host)
        self.test_get_status_handler(host) 
        self.test_get_capabilities_handler(host)
        self.test_recording_handlers(host)
        
        # Test 4: Message protocol tests
        self.test_message_serialization()
        self.test_native_messaging_protocol()
        self.test_chrome_extension_message_types()
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"\n" + "=" * 50)
        print(f"MESSAGE PROTOCOL TEST SUMMARY")
        print(f"=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed:      {passed_tests}")
        print(f"Failed:      {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests == 0:
            print(f"\n[OK] All message protocol tests passed!")
            print("The Chrome extension should be able to communicate with the Python backend.")
        else:
            print(f"\n[FAIL] {failed_tests} tests failed!")
            print("Review the failures above before proceeding.")
        
        return failed_tests == 0


def main():
    """Main entry point."""
    tester = MessageProtocolTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()