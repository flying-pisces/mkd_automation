#!/usr/bin/env python3
"""
End-to-End Testing for MKD Chrome Extension Recording and Playback

This script tests the complete workflow from Chrome extension recording
to Python playback engine execution.
"""

import json
import time
import tempfile
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import struct
import threading
import queue

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mkd.core.session import Session
from mkd.playback.action_executor import ActionExecutor
from mkd.data.serializer import ScriptSerializer


class E2ETestRunner:
    """End-to-end test runner for Chrome extension integration."""
    
    def __init__(self):
        self.test_results = []
        self.native_host_process = None
        self.response_queue = queue.Queue()
        
    def setup(self) -> bool:
        """Setup test environment."""
        print("[SETUP] Initializing E2E test environment...")
        
        # Check Chrome extension files
        extension_path = project_root / "chrome-extension"
        required_files = [
            "manifest.json",
            "src/background.js",
            "src/content.js",
            "src/popup/popup.js"
        ]
        
        for file in required_files:
            if not (extension_path / file).exists():
                print(f"[FAIL] Missing required file: {file}")
                return False
        
        print("[OK] Chrome extension files verified")
        
        # Start native host
        if not self.start_native_host():
            return False
            
        print("[OK] Test environment ready")
        return True
    
    def start_native_host(self) -> bool:
        """Start the native messaging host."""
        try:
            host_script = project_root / "src" / "mkd_v2" / "native_host" / "host.py"
            
            self.native_host_process = subprocess.Popen(
                [sys.executable, str(host_script), "--debug"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=project_root
            )
            
            # Start response reader
            self.reader_thread = threading.Thread(
                target=self._read_responses,
                daemon=True
            )
            self.reader_thread.start()
            
            # Test connection
            response = self.send_message("PING", {})
            if not response or not response.get("success"):
                print("[FAIL] Native host ping failed")
                return False
                
            print("[OK] Native host started")
            return True
            
        except Exception as e:
            print(f"[FAIL] Failed to start native host: {e}")
            return False
    
    def stop_native_host(self):
        """Stop the native messaging host."""
        if self.native_host_process:
            try:
                self.native_host_process.terminate()
                self.native_host_process.wait(timeout=5)
                print("[OK] Native host stopped")
            except Exception as e:
                print(f"[WARN] Error stopping native host: {e}")
                self.native_host_process.kill()
    
    def send_message(self, command: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send message to native host."""
        if not self.native_host_process:
            return None
            
        message = {
            "id": f"e2e_test_{int(time.time() * 1000)}",
            "command": command,
            "params": params,
            "timestamp": time.time()
        }
        
        try:
            # Send message
            message_json = json.dumps(message)
            message_bytes = message_json.encode("utf-8")
            
            length_bytes = struct.pack("=I", len(message_bytes))
            self.native_host_process.stdin.write(length_bytes)
            self.native_host_process.stdin.write(message_bytes)
            self.native_host_process.stdin.flush()
            
            # Wait for response
            try:
                response = self.response_queue.get(timeout=10)
                return response
            except queue.Empty:
                print(f"[FAIL] Timeout waiting for response to {command}")
                return None
                
        except Exception as e:
            print(f"[FAIL] Error sending message: {e}")
            return None
    
    def _read_responses(self):
        """Read responses from native host."""
        try:
            while self.native_host_process and self.native_host_process.poll() is None:
                # Read message length
                length_data = self.native_host_process.stdout.read(4)
                if not length_data:
                    break
                    
                message_length = struct.unpack("=I", length_data)[0]
                
                # Read message
                message_data = self.native_host_process.stdout.read(message_length)
                response = json.loads(message_data.decode("utf-8"))
                
                self.response_queue.put(response)
                
        except Exception as e:
            print(f"[WARN] Response reader error: {e}")
    
    def test_recording_workflow(self) -> bool:
        """Test complete recording workflow."""
        print("\n[TEST] Recording Workflow")
        print("-" * 40)
        
        # Start recording
        print("1. Starting recording session...")
        start_response = self.send_message("START_RECORDING", {
            "user_id": 1,
            "config": {
                "capture_video": False,
                "capture_audio": False,
                "show_border": True
            }
        })
        
        if not start_response or not start_response.get("success"):
            print("[FAIL] Failed to start recording")
            return False
            
        session_id = start_response["data"]["sessionId"]
        print(f"[OK] Recording started - Session: {session_id}")
        
        # Simulate Chrome extension sending events
        print("2. Simulating user interactions...")
        test_events = [
            {
                "type": "click",
                "data": {
                    "x": 100,
                    "y": 200,
                    "selector": "#submit-button",
                    "element": {
                        "tag": "button",
                        "id": "submit-button",
                        "innerText": "Submit"
                    }
                },
                "timestamp": time.time() * 1000
            },
            {
                "type": "input",
                "data": {
                    "selector": "#username",
                    "value": "testuser",
                    "element": {
                        "tag": "input",
                        "id": "username",
                        "type": "text"
                    }
                },
                "timestamp": time.time() * 1000 + 1000
            },
            {
                "type": "keydown",
                "data": {
                    "key": "Enter",
                    "code": "Enter",
                    "ctrlKey": False,
                    "shiftKey": False
                },
                "timestamp": time.time() * 1000 + 2000
            }
        ]
        
        for event in test_events:
            add_response = self.send_message("ADD_EVENT", {
                "sessionId": session_id,
                "event": event
            })
            
            if not add_response or not add_response.get("success"):
                print(f"[FAIL] Failed to add event: {event['type']}")
                return False
        
        print(f"[OK] Added {len(test_events)} test events")
        
        # Stop recording
        print("3. Stopping recording...")
        stop_response = self.send_message("STOP_RECORDING", {})
        
        if not stop_response or not stop_response.get("success"):
            print("[FAIL] Failed to stop recording")
            return False
            
        recording_data = stop_response["data"]
        print(f"[OK] Recording stopped")
        print(f"     Events: {recording_data.get('eventCount', 0)}")
        print(f"     Duration: {recording_data.get('duration', 0):.2f}s")
        print(f"     File: {recording_data.get('filePath', 'N/A')}")
        
        return True
    
    def test_playback_workflow(self) -> bool:
        """Test playback of recorded script."""
        print("\n[TEST] Playback Workflow")
        print("-" * 40)
        
        # Create a test script
        print("1. Creating test script...")
        test_script = {
            "version": "2.0",
            "metadata": {
                "created_at": time.time(),
                "user_id": 1,
                "description": "E2E test script"
            },
            "actions": [
                {
                    "type": "mouse_click",
                    "timestamp": 0,
                    "data": {
                        "x": 100,
                        "y": 200,
                        "button": "left"
                    }
                },
                {
                    "type": "keyboard_type",
                    "timestamp": 1000,
                    "data": {
                        "text": "Hello World"
                    }
                },
                {
                    "type": "keyboard_key",
                    "timestamp": 2000,
                    "data": {
                        "key": "enter"
                    }
                }
            ]
        }
        
        # Save script
        with tempfile.NamedTemporaryFile(suffix=".mkd", delete=False) as f:
            script_path = Path(f.name)
            serializer = ScriptSerializer()
            serializer.save(test_script, script_path)
        
        print(f"[OK] Test script created: {script_path.name}")
        
        # Test playback via native host
        print("2. Starting playback...")
        playback_response = self.send_message("START_PLAYBACK", {
            "scriptPath": str(script_path),
            "config": {
                "speed": 1.0,
                "loop": False
            }
        })
        
        if not playback_response or not playback_response.get("success"):
            print("[FAIL] Failed to start playback")
            return False
        
        print("[OK] Playback started")
        
        # Monitor playback status
        print("3. Monitoring playback progress...")
        time.sleep(3)  # Wait for playback to complete
        
        status_response = self.send_message("GET_PLAYBACK_STATUS", {})
        if status_response and status_response.get("success"):
            status = status_response["data"]
            print(f"[OK] Playback status: {status.get('state', 'unknown')}")
            print(f"     Actions executed: {status.get('actionsExecuted', 0)}")
        
        # Clean up
        script_path.unlink()
        
        return True
    
    def test_error_handling(self) -> bool:
        """Test error handling and recovery."""
        print("\n[TEST] Error Handling")
        print("-" * 40)
        
        # Test invalid command
        print("1. Testing invalid command...")
        response = self.send_message("INVALID_COMMAND", {})
        if response and not response.get("success"):
            print("[OK] Invalid command rejected properly")
        else:
            print("[FAIL] Invalid command not handled")
            return False
        
        # Test missing parameters
        print("2. Testing missing parameters...")
        response = self.send_message("START_RECORDING", {})  # Missing user_id
        if response and response.get("success"):
            print("[OK] Missing parameters handled with defaults")
        else:
            print("[WARN] Missing parameters rejected")
        
        # Test connection recovery
        print("3. Testing connection recovery...")
        
        # Simulate disconnect
        self.stop_native_host()
        time.sleep(1)
        
        # Restart
        if self.start_native_host():
            print("[OK] Connection recovered successfully")
        else:
            print("[FAIL] Failed to recover connection")
            return False
        
        return True
    
    def test_performance(self) -> bool:
        """Test performance and scalability."""
        print("\n[TEST] Performance")
        print("-" * 40)
        
        # Test rapid message sending
        print("1. Testing rapid message handling...")
        start_time = time.time()
        message_count = 100
        
        for i in range(message_count):
            response = self.send_message("PING", {})
            if not response or not response.get("success"):
                print(f"[FAIL] Message {i} failed")
                return False
        
        elapsed = time.time() - start_time
        rate = message_count / elapsed
        print(f"[OK] Processed {message_count} messages in {elapsed:.2f}s")
        print(f"     Rate: {rate:.1f} messages/second")
        
        # Test large event recording
        print("2. Testing large event recording...")
        start_response = self.send_message("START_RECORDING", {"user_id": 1})
        if not start_response:
            return False
            
        session_id = start_response["data"]["sessionId"]
        
        # Add many events
        event_count = 1000
        start_time = time.time()
        
        for i in range(event_count):
            event = {
                "type": "mouse_move",
                "data": {"x": i, "y": i},
                "timestamp": time.time() * 1000
            }
            
            self.send_message("ADD_EVENT", {
                "sessionId": session_id,
                "event": event
            })
        
        elapsed = time.time() - start_time
        print(f"[OK] Added {event_count} events in {elapsed:.2f}s")
        
        # Stop and check
        stop_response = self.send_message("STOP_RECORDING", {})
        if stop_response and stop_response.get("success"):
            actual_count = stop_response["data"].get("eventCount", 0)
            if actual_count == event_count:
                print(f"[OK] All {event_count} events recorded successfully")
            else:
                print(f"[WARN] Expected {event_count} events, got {actual_count}")
        
        return True
    
    def generate_report(self) -> str:
        """Generate test report."""
        report = []
        report.append("\n" + "=" * 50)
        report.append("E2E TEST REPORT")
        report.append("=" * 50)
        
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = total_tests - passed
        
        report.append(f"\nTotal Tests: {total_tests}")
        report.append(f"Passed: {passed}")
        report.append(f"Failed: {failed}")
        report.append(f"Success Rate: {(passed/total_tests*100):.1f}%")
        
        report.append("\nTest Results:")
        report.append("-" * 30)
        
        for result in self.test_results:
            status = "[OK]" if result["passed"] else "[FAIL]"
            report.append(f"{status} {result['name']}")
            if result.get("message"):
                report.append(f"      {result['message']}")
        
        report.append("\n" + "=" * 50)
        
        return "\n".join(report)
    
    def run_all_tests(self) -> bool:
        """Run all E2E tests."""
        print("\nMKD Chrome Extension - End-to-End Testing")
        print("=" * 50)
        
        # Setup
        if not self.setup():
            print("[FAIL] Setup failed, cannot run tests")
            return False
        
        # Run tests
        tests = [
            ("Recording Workflow", self.test_recording_workflow),
            ("Playback Workflow", self.test_playback_workflow),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance)
        ]
        
        for test_name, test_func in tests:
            try:
                passed = test_func()
                self.test_results.append({
                    "name": test_name,
                    "passed": passed,
                    "message": None
                })
            except Exception as e:
                self.test_results.append({
                    "name": test_name,
                    "passed": False,
                    "message": str(e)
                })
                print(f"[FAIL] Test '{test_name}' raised exception: {e}")
        
        # Cleanup
        self.stop_native_host()
        
        # Generate report
        report = self.generate_report()
        print(report)
        
        # Save report
        report_path = project_root / "chrome-extension" / "tests" / "e2e_test_report.txt"
        report_path.write_text(report)
        print(f"\nReport saved to: {report_path}")
        
        # Return overall success
        return all(r["passed"] for r in self.test_results)


def main():
    """Main entry point."""
    runner = E2ETestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()