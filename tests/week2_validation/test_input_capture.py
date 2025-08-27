#!/usr/bin/env python3
"""
Real Input Capture System Tests

Tests the pynput-based input capture implementation including:
- Platform detection and initialization
- Mouse event capture and processing
- Keyboard event capture and processing  
- Event format standardization
- Permission handling
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mkd_v2.platform.detector import PlatformDetector
from mkd_v2.platform.implementations.macos_real import MacOSRealPlatform

import logging

# Configure logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "input_capture.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class InputCaptureTester:
    """Test real input capture functionality."""
    
    def __init__(self):
        self.platform = None
        self.captured_events = []
        self.results = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all input capture tests."""
        logger.info("🚀 Starting Input Capture Tests")
        
        tests = [
            ("Platform Detection", self.test_platform_detection),
            ("Platform Initialization", self.test_platform_initialization),
            ("Capabilities Check", self.test_capabilities_check),
            ("Permission Check", self.test_permission_check),
            ("Input Capture Setup", self.test_input_capture_setup),
            ("Mouse Action Execution", self.test_mouse_action_execution),
            ("Keyboard Action Execution", self.test_keyboard_action_execution),
            ("Event Processing", self.test_event_processing),
        ]
        
        for test_name, test_func in tests:
            logger.info(f"📝 Running: {test_name}")
            try:
                result = test_func()
                self.results.append({
                    'test': test_name,
                    'status': 'PASS' if result.get('success', False) else 'FAIL',
                    'details': result
                })
                logger.info(f"✅ {test_name}: {'PASS' if result.get('success', False) else 'FAIL'}")
            except Exception as e:
                self.results.append({
                    'test': test_name,
                    'status': 'ERROR',
                    'error': str(e)
                })
                logger.error(f"❌ {test_name}: ERROR - {e}")
        
        return self._generate_report()
    
    def test_platform_detection(self) -> Dict[str, Any]:
        """Test platform detection and selection."""
        try:
            # Test platform detector
            platform = PlatformDetector.detect()
            
            # Check if we got a real platform implementation
            platform_type = type(platform).__name__
            is_real_implementation = 'Real' in platform_type
            
            return {
                'success': platform is not None,
                'platform_name': platform.name if platform else None,
                'platform_type': platform_type,
                'platform_version': getattr(platform, 'version', 'unknown'),
                'is_real_implementation': is_real_implementation
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Platform detection failed: {e}'
            }
    
    def test_platform_initialization(self) -> Dict[str, Any]:
        """Test platform initialization."""
        try:
            self.platform = PlatformDetector.detect()
            
            # Initialize platform
            init_result = self.platform.initialize()
            
            return {
                'success': init_result.get('success', False),
                'init_result': init_result,
                'platform_initialized': getattr(self.platform, '_initialized', False)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Platform initialization failed: {e}'
            }
    
    def test_capabilities_check(self) -> Dict[str, Any]:
        """Test platform capabilities."""
        try:
            if not self.platform:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
            
            capabilities = self.platform.get_capabilities()
            
            # Check for real input capture capability
            real_input_capture = capabilities.get('real_input_capture', False)
            input_capture = capabilities.get('input_capture', False)
            
            return {
                'success': input_capture and real_input_capture,
                'capabilities': capabilities,
                'has_real_input_capture': real_input_capture,
                'has_input_capture': input_capture
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Capabilities check failed: {e}'
            }
    
    def test_permission_check(self) -> Dict[str, Any]:
        """Test system permissions for input capture."""
        try:
            if not self.platform:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
            
            # Check permissions
            permissions = self.platform.check_permissions()
            
            return {
                'success': permissions.get('overall', False),
                'permissions': permissions,
                'missing_permissions': permissions.get('missing_permissions', [])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Permission check failed: {e}'
            }
    
    def test_input_capture_setup(self) -> Dict[str, Any]:
        """Test input capture setup and teardown."""
        try:
            if not self.platform:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
            
            # Set up event callback
            def event_callback(event):
                self.captured_events.append(event)
                logger.debug(f"Captured event: {event['type']}")
            
            # Start input capture
            start_result = self.platform.start_input_capture(event_callback)
            
            if start_result:
                # Let it run briefly
                time.sleep(0.5)
                
                # Stop input capture
                stop_result = self.platform.stop_input_capture()
            else:
                stop_result = False
            
            return {
                'success': start_result and stop_result,
                'start_result': start_result,
                'stop_result': stop_result,
                'events_captured': len(self.captured_events)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Input capture setup failed: {e}'
            }
    
    def test_mouse_action_execution(self) -> Dict[str, Any]:
        """Test mouse action execution."""
        try:
            if not self.platform:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
            
            from mkd_v2.platform.base import MouseAction
            
            # Test mouse move
            move_action = MouseAction(action="move", x=500, y=400)
            move_result = self.platform.execute_mouse_action(move_action)
            
            # Brief delay
            time.sleep(0.1)
            
            # Test mouse click (safe coordinates)
            click_action = MouseAction(action="click", x=500, y=400, button="left")
            click_result = self.platform.execute_mouse_action(click_action)
            
            return {
                'success': move_result and click_result,
                'move_result': move_result,
                'click_result': click_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Mouse action execution failed: {e}'
            }
    
    def test_keyboard_action_execution(self) -> Dict[str, Any]:
        """Test keyboard action execution."""
        try:
            if not self.platform:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
            
            from mkd_v2.platform.base import KeyboardAction
            
            # Test key press/release
            key_action = KeyboardAction(action="press", key="space")
            key_result = self.platform.execute_keyboard_action(key_action)
            
            time.sleep(0.1)
            
            release_action = KeyboardAction(action="release", key="space")
            release_result = self.platform.execute_keyboard_action(release_action)
            
            time.sleep(0.1)
            
            # Test text typing (safe text)
            type_action = KeyboardAction(action="type", text="test")
            type_result = self.platform.execute_keyboard_action(type_action)
            
            return {
                'success': key_result and release_result and type_result,
                'key_result': key_result,
                'release_result': release_result,
                'type_result': type_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Keyboard action execution failed: {e}'
            }
    
    def test_event_processing(self) -> Dict[str, Any]:
        """Test event processing and format."""
        try:
            if not self.platform:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
            
            # Clear previous events
            self.captured_events = []
            
            # Set up event callback
            def event_callback(event):
                self.captured_events.append(event)
            
            # Start capture
            self.platform.start_input_capture(event_callback)
            
            # Generate some events programmatically
            from mkd_v2.platform.base import MouseAction, KeyboardAction
            
            # Move mouse
            move_action = MouseAction(action="move", x=600, y=500)
            self.platform.execute_mouse_action(move_action)
            time.sleep(0.2)
            
            # Click
            click_action = MouseAction(action="click", x=600, y=500)
            self.platform.execute_mouse_action(click_action)
            time.sleep(0.2)
            
            # Type text
            type_action = KeyboardAction(action="type", text="hi")
            self.platform.execute_keyboard_action(type_action)
            time.sleep(0.2)
            
            # Stop capture
            self.platform.stop_input_capture()
            
            # Analyze captured events
            event_types = [event.get('type') for event in self.captured_events]
            unique_types = set(event_types)
            
            # Check event structure
            valid_events = []
            invalid_events = []
            
            for event in self.captured_events:
                required_fields = ['timestamp', 'type', 'source']
                if all(field in event for field in required_fields):
                    valid_events.append(event)
                else:
                    invalid_events.append(event)
            
            return {
                'success': len(valid_events) > 0 and len(invalid_events) == 0,
                'total_events': len(self.captured_events),
                'valid_events': len(valid_events),
                'invalid_events': len(invalid_events),
                'event_types': list(unique_types),
                'sample_events': self.captured_events[:5]  # First 5 events as samples
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Event processing test failed: {e}'
            }
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.results if r['status'] == 'ERROR'])
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'errors': error_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'results': self.results,
            'recommendations': []
        }
        
        # Add recommendations based on failures
        for result in self.results:
            if result['status'] != 'PASS':
                test_name = result['test']
                if 'Permission' in test_name:
                    report['recommendations'].append(
                        "Grant Accessibility and Input Monitoring permissions in System Preferences (macOS)"
                    )
                elif 'Platform Initialization' in test_name:
                    report['recommendations'].append(
                        "Install pynput dependency: pip install pynput"
                    )
                elif 'Input Capture' in test_name:
                    report['recommendations'].append(
                        "Check system permissions and pynput installation"
                    )
        
        return report


def main():
    """Run input capture tests."""
    tester = InputCaptureTester()
    report = tester.run_all_tests()
    
    # Save detailed report
    log_dir = Path(__file__).parent / "logs"
    report_file = log_dir / "input_capture_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "="*60)
    print("🖱️  INPUT CAPTURE TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']} ✅")
    print(f"Failed: {report['summary']['failed']} ❌")
    print(f"Errors: {report['summary']['errors']} 🚨")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    
    if report['recommendations']:
        print("\n🔧 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    return report['summary']['success_rate'] >= 70  # 70% pass rate threshold (permissions may fail)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)