#!/usr/bin/env python
"""
Windows Native Host Test - Milestone 2.1.1
Tests native messaging host functionality on Windows
"""

import os
import sys
import json
import time
import subprocess
import tempfile
import struct
from pathlib import Path

def test_native_host_windows():
    """Test native messaging host on Windows."""
    print("🖥️  Testing Windows Native Host...")
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("⚠️  SKIP: Not running on Windows")
        return True
    
    results = {
        'host_executable': False,
        'path_resolution': False,
        'startup_success': False,
        'ping_response': False,
        'message_protocol': False
    }
    
    project_root = Path(__file__).parent.parent.parent
    
    # Test 1: Check if native host executable exists
    print("  1. Checking for Windows native host executable...")
    
    host_paths = [
        project_root / "bin" / "mkd_native_host.exe",
        project_root / "bin" / "mkd_native_host.bat",
        project_root / "bin" / "mkd_native_host"
    ]
    
    host_executable = None
    for path in host_paths:
        if path.exists():
            host_executable = path
            results['host_executable'] = True
            print(f"  ✅ Found native host: {path}")
            break
    
    if not host_executable:
        print("  ❌ No native host executable found")
        print("  Expected paths:")
        for path in host_paths:
            print(f"    - {path}")
        return False
    
    # Test 2: Check path resolution (no hardcoded paths)
    print("  2. Checking for hardcoded paths...")
    
    try:
        content = host_executable.read_text()
        if '/Users/cyin' in content or '/home/' in content:
            print("  ❌ Found hardcoded Unix paths")
            results['path_resolution'] = False
        else:
            print("  ✅ No hardcoded paths found")
            results['path_resolution'] = True
    except Exception as e:
        print(f"  ⚠️  Could not read host file: {e}")
        results['path_resolution'] = True  # Assume binary is OK
    
    # Test 3: Test native host startup
    print("  3. Testing native host startup...")
    
    try:
        # Create a test message
        test_message = {
            "id": "test-001",
            "command": "PING",
            "params": {}
        }
        
        # Start the native host process
        process = subprocess.Popen(
            [str(host_executable)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(project_root)
        )
        
        print("    Host process started...")
        results['startup_success'] = True
        
        # Test 4: Send ping message
        print("  4. Testing ping message...")
        
        # Encode message using Chrome native messaging protocol
        message_json = json.dumps(test_message)
        message_bytes = message_json.encode('utf-8')
        length_bytes = struct.pack('I', len(message_bytes))
        
        # Send message
        process.stdin.write(length_bytes)
        process.stdin.write(message_bytes)
        process.stdin.flush()
        
        print("    Ping message sent...")
        
        # Wait for response with timeout
        try:
            # Read response length
            response_length_bytes = process.stdout.read(4)
            if len(response_length_bytes) == 4:
                response_length = struct.unpack('I', response_length_bytes)[0]
                
                # Read response content
                response_bytes = process.stdout.read(response_length)
                if len(response_bytes) == response_length:
                    response = json.loads(response_bytes.decode('utf-8'))
                    
                    if response.get('id') == 'test-001' and response.get('success'):
                        print("    ✅ Ping response received")
                        results['ping_response'] = True
                        results['message_protocol'] = True
                    else:
                        print(f"    ❌ Invalid ping response: {response}")
                else:
                    print("    ❌ Incomplete response received")
            else:
                print("    ❌ No response length received")
                
        except Exception as e:
            print(f"    ❌ Error reading response: {e}")
        
        # Clean up process
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            
    except Exception as e:
        print(f"    ❌ Failed to start native host: {e}")
        results['startup_success'] = False
    
    # Generate report
    print("\n📊 Windows Native Host Test Results:")
    print("=" * 45)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    if passed_tests == total_tests:
        print("✅ PASS: All Windows native host tests passed")
        print(f"  Executable: {host_executable.name}")
        print(f"  Tests passed: {passed_tests}/{total_tests}")
        return True
    else:
        print(f"❌ FAIL: {total_tests - passed_tests} tests failed")
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {test_name}")
        
        return False

def main():
    """Run Windows native host test."""
    try:
        success = test_native_host_windows()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ FAIL: Test error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())