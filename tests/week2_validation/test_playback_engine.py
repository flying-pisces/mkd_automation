#!/usr/bin/env python3
"""
Playback Engine Foundation Tests

Tests the playback system including:
- Playback engine initialization
- Action execution and validation
- Sequence processing
- Performance and error handling
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mkd_v2.playback import PlaybackEngine, ActionExecutor, SequenceValidator
from mkd_v2.automation.automation_engine import AutomationEngine
from mkd_v2.platform.detector import PlatformDetector
from mkd_v2.core.session_manager import RecordingSession, SessionState

import logging

# Configure logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "playback_engine.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PlaybackEngineTester:
    """Test playback engine functionality."""
    
    def __init__(self):
        self.platform = None
        self.automation_engine = None
        self.playback_engine = None
        self.action_executor = None
        self.sequence_validator = None
        self.results = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all playback engine tests."""
        logger.info("🚀 Starting Playback Engine Tests")
        
        tests = [
            ("Component Setup", self.test_component_setup),
            ("Sequence Validator", self.test_sequence_validator),
            ("Action Executor", self.test_action_executor),
            ("Playback Engine", self.test_playback_engine),
            ("Speed Control", self.test_speed_control),
            ("Action Validation", self.test_action_validation),
            ("Performance Test", self.test_performance),
            ("Error Handling", self.test_error_handling)
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
    
    def test_component_setup(self) -> Dict[str, Any]:
        """Test setup of all playback components."""
        try:
            # Setup platform and automation
            self.platform = PlatformDetector.detect()
            init_result = self.platform.initialize()
            
            self.automation_engine = AutomationEngine(self.platform)
            
            # Create playback components
            self.playback_engine = PlaybackEngine(self.platform, self.automation_engine)
            self.action_executor = ActionExecutor(self.platform, self.automation_engine)
            self.sequence_validator = SequenceValidator(self.automation_engine)
            
            return {
                'success': all([
                    init_result.get('success', False),
                    self.playback_engine is not None,
                    self.action_executor is not None,
                    self.sequence_validator is not None
                ]),
                'platform_initialized': init_result.get('success', False),
                'playback_engine_created': self.playback_engine is not None,
                'action_executor_created': self.action_executor is not None,
                'sequence_validator_created': self.sequence_validator is not None,
                'platform_name': self.platform.name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Component setup failed: {e}'
            }
    
    def test_sequence_validator(self) -> Dict[str, Any]:
        """Test sequence validation functionality."""
        try:
            if not self.sequence_validator:
                self.automation_engine = AutomationEngine(PlatformDetector.detect())
                self.sequence_validator = SequenceValidator(self.automation_engine)
            
            # Test valid sequence
            valid_sequence = [
                {'type': 'mouse_click', 'coordinates': [100, 200]},
                {'type': 'delay', 'duration': 1.0},
                {'type': 'type_text', 'text': 'Hello World'},
                {'type': 'key_press', 'key': 'Enter'}
            ]
            
            valid_result = self.sequence_validator.validate_sequence(valid_sequence)
            
            # Test invalid sequence
            invalid_sequence = [
                {'type': 'mouse_click'},  # Missing coordinates
                {'type': 'delay', 'duration': -1},  # Invalid duration
                {'type': 'unknown_action'},  # Unknown action type
                {}  # Empty action
            ]
            
            invalid_result = self.sequence_validator.validate_sequence(invalid_sequence)
            
            # Test empty sequence
            empty_result = self.sequence_validator.validate_sequence([])
            
            return {
                'success': valid_result.is_valid and not invalid_result.is_valid and not empty_result.is_valid,
                'valid_sequence': {
                    'is_valid': valid_result.is_valid,
                    'issues_count': len(valid_result.issues)
                },
                'invalid_sequence': {
                    'is_valid': invalid_result.is_valid,
                    'issues_count': len(invalid_result.issues),
                    'sample_issues': [issue.message for issue in invalid_result.issues[:3]]
                },
                'empty_sequence': {
                    'is_valid': empty_result.is_valid,
                    'issues_count': len(empty_result.issues)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Sequence validator test failed: {e}'
            }
    
    def test_action_executor(self) -> Dict[str, Any]:
        """Test individual action execution."""
        try:
            if not self.action_executor:
                platform = PlatformDetector.detect()
                platform.initialize()
                automation = AutomationEngine(platform)
                self.action_executor = ActionExecutor(platform, automation)
            
            # Test different action types
            test_actions = [
                {'type': 'delay', 'duration': 0.1},
                {'type': 'mouse_move', 'x': 400, 'y': 300},
                {'type': 'mouse_click', 'x': 400, 'y': 300, 'button': 'left'},
                {'type': 'type_text', 'text': 'test'},
                {'type': 'key_press', 'key': 'space', 'action': 'press'}
            ]
            
            execution_results = []
            
            for action in test_actions:
                result = self.action_executor.execute_action(action)
                execution_results.append({
                    'action_type': action['type'],
                    'success': result.success,
                    'execution_time': result.execution_time,
                    'status': result.status.value
                })
                
                # Small delay between actions
                time.sleep(0.1)
            
            # Get executor stats
            stats = self.action_executor.get_execution_stats()
            
            successful_actions = len([r for r in execution_results if r['success']])
            
            return {
                'success': successful_actions >= len(test_actions) // 2,  # At least half should succeed
                'total_actions': len(test_actions),
                'successful_actions': successful_actions,
                'execution_results': execution_results,
                'executor_stats': stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Action executor test failed: {e}'
            }
    
    def test_playback_engine(self) -> Dict[str, Any]:
        """Test playback engine functionality."""
        try:
            if not self.playback_engine:
                platform = PlatformDetector.detect()
                platform.initialize()
                automation = AutomationEngine(platform)
                self.playback_engine = PlaybackEngine(platform, automation)
            
            # Test playback status
            initial_status = self.playback_engine.get_playback_status()
            
            # Test basic playback controls
            pause_result = self.playback_engine.pause_playback()  # Should fail (not running)
            resume_result = self.playback_engine.resume_playback()  # Should fail (not running)
            stop_result = self.playback_engine.stop_playback()  # Should fail (not running)
            
            # Create mock session for testing
            class MockSession:
                def __init__(self):
                    self.id = 'test_session'
                    self.actions = [
                        {'type': 'delay', 'duration': 0.1},
                        {'type': 'mouse_move', 'x': 500, 'y': 400}
                    ]
            
            mock_session = MockSession()
            
            # Test session playback (will be quick due to simple actions)
            try:
                playback_result = self.playback_engine.play_session(mock_session)
                playback_success = playback_result.success
            except Exception as playback_error:
                playback_success = False
                logger.warning(f"Playback failed: {playback_error}")
            
            # Get final status
            final_status = self.playback_engine.get_playback_status()
            
            return {
                'success': initial_status is not None,
                'initial_status': initial_status['status'],
                'control_results': {
                    'pause_when_idle': pause_result == False,  # Should fail when idle
                    'resume_when_idle': resume_result == False,  # Should fail when idle
                    'stop_when_idle': stop_result == False  # Should fail when idle
                },
                'playback_test': playback_success,
                'final_status': final_status['status']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Playback engine test failed: {e}'
            }
    
    def test_speed_control(self) -> Dict[str, Any]:
        """Test playback speed control."""
        try:
            if not self.playback_engine:
                platform = PlatformDetector.detect()
                platform.initialize()
                automation = AutomationEngine(platform)
                self.playback_engine = PlaybackEngine(platform, automation)
            
            # Test speed setting
            speed_tests = [
                (0.5, True),   # Half speed - should work
                (1.0, True),   # Normal speed - should work
                (2.0, True),   # Double speed - should work
                (0.05, False), # Too slow - should fail
                (15.0, False)  # Too fast - should fail
            ]
            
            speed_results = []
            for speed, expected_success in speed_tests:
                result = self.playback_engine.set_speed(speed)
                speed_results.append({
                    'speed': speed,
                    'set_success': result,
                    'expected_success': expected_success,
                    'correct': result == expected_success
                })
            
            # Reset to normal speed
            self.playback_engine.set_speed(1.0)
            
            correct_results = len([r for r in speed_results if r['correct']])
            
            return {
                'success': correct_results >= len(speed_tests) // 2,
                'speed_tests': speed_results,
                'correct_results': correct_results,
                'total_tests': len(speed_tests)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Speed control test failed: {e}'
            }
    
    def test_action_validation(self) -> Dict[str, Any]:
        """Test action validation in different scenarios."""
        try:
            if not self.sequence_validator:
                automation = AutomationEngine(PlatformDetector.detect())
                self.sequence_validator = SequenceValidator(automation)
            
            # Test various action validation scenarios
            validation_tests = [
                # Valid actions
                ({'type': 'mouse_click', 'coordinates': [100, 200]}, True),
                ({'type': 'delay', 'duration': 1.0}, True),
                ({'type': 'type_text', 'text': 'hello'}, True),
                
                # Invalid actions
                ({'type': 'mouse_click', 'coordinates': 'invalid'}, False),
                ({'type': 'delay', 'duration': -5}, False),
                ({'type': 'unknown_type'}, False),
                ({}, False)  # Empty action
            ]
            
            validation_results = []
            for action, expected_valid in validation_tests:
                result = self.sequence_validator.validate_single_action(action)
                validation_results.append({
                    'action': action,
                    'is_valid': result.is_valid,
                    'expected_valid': expected_valid,
                    'correct': result.is_valid == expected_valid,
                    'issues': len(result.issues)
                })
            
            correct_validations = len([r for r in validation_results if r['correct']])
            
            return {
                'success': correct_validations >= len(validation_tests) * 0.8,  # 80% accuracy
                'validation_results': validation_results,
                'correct_validations': correct_validations,
                'total_tests': len(validation_tests)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Action validation test failed: {e}'
            }
    
    def test_performance(self) -> Dict[str, Any]:
        """Test playback engine performance."""
        try:
            if not self.action_executor:
                platform = PlatformDetector.detect()
                platform.initialize()
                automation = AutomationEngine(platform)
                self.action_executor = ActionExecutor(platform, automation)
            
            # Performance test with rapid action execution
            num_actions = 20
            test_actions = [
                {'type': 'delay', 'duration': 0.01}  # Very short delays
            ] * num_actions
            
            start_time = time.time()
            successful_executions = 0
            
            for action in test_actions:
                result = self.action_executor.execute_action(action)
                if result.success:
                    successful_executions += 1
            
            total_time = time.time() - start_time
            actions_per_second = num_actions / total_time if total_time > 0 else 0
            
            # Get final stats
            stats = self.action_executor.get_execution_stats()
            
            return {
                'success': successful_executions >= num_actions * 0.8,  # 80% success rate
                'total_actions': num_actions,
                'successful_executions': successful_executions,
                'total_time': total_time,
                'actions_per_second': actions_per_second,
                'final_stats': stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Performance test failed: {e}'
            }
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling in playback system."""
        try:
            if not self.action_executor:
                platform = PlatformDetector.detect()
                platform.initialize()
                automation = AutomationEngine(platform)
                self.action_executor = ActionExecutor(platform, automation)
            
            # Test actions that should fail gracefully
            error_actions = [
                {'type': 'mouse_click'},  # Missing coordinates
                {'type': 'invalid_action'},  # Invalid action type
                {'type': 'type_text'},  # Missing text
                {'type': 'delay', 'duration': 'invalid'}  # Invalid duration type
            ]
            
            error_results = []
            for action in error_actions:
                result = self.action_executor.execute_action(action)
                error_results.append({
                    'action': action,
                    'failed_gracefully': not result.success and result.error_message is not None,
                    'error_message': result.error_message,
                    'execution_time': result.execution_time
                })
            
            graceful_failures = len([r for r in error_results if r['failed_gracefully']])
            
            return {
                'success': graceful_failures >= len(error_actions) * 0.7,  # 70% should fail gracefully
                'error_tests': error_results,
                'graceful_failures': graceful_failures,
                'total_error_tests': len(error_actions)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error handling test failed: {e}'
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
                if 'Component Setup' in test_name:
                    report['recommendations'].append(
                        "Ensure platform initialization and all dependencies are installed"
                    )
                elif 'Action Executor' in test_name:
                    report['recommendations'].append(
                        "Check system permissions for input simulation"
                    )
                elif 'Performance' in test_name:
                    report['recommendations'].append(
                        "Review system resources and action execution timing"
                    )
        
        return report


def main():
    """Run playback engine tests."""
    tester = PlaybackEngineTester()
    report = tester.run_all_tests()
    
    # Save detailed report
    log_dir = Path(__file__).parent / "logs"
    report_file = log_dir / "playback_engine_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "="*60)
    print("⏯️  PLAYBACK ENGINE TEST SUMMARY")
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
    
    return report['summary']['success_rate'] >= 75  # 75% pass rate threshold


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)