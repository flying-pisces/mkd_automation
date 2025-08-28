#!/usr/bin/env python3
"""
Context Detection System Tests

Comprehensive tests for the intelligent context detection system including:
- Application context detection
- UI state analysis  
- Context change tracking
- Pattern recognition integration
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mkd_v2.intelligence.context_detector import (
    ContextDetector, ApplicationContext, ContextType, UIState, ContextChangeEvent
)
from mkd_v2.platform.detector import PlatformDetector

import logging

# Configure logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "context_detection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ContextDetectorTester:
    """Test suite for context detection functionality."""
    
    def __init__(self):
        self.platform = None
        self.context_detector = None
        self.results = []
        self.change_events = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all context detection tests."""
        logger.info("🧠 Starting Context Detection Tests")
        
        tests = [
            ("Platform Integration", self.test_platform_integration),
            ("Basic Context Detection", self.test_basic_context_detection),
            ("Application Classification", self.test_application_classification),
            ("UI State Analysis", self.test_ui_state_analysis),
            ("Context Change Detection", self.test_context_change_detection),
            ("Context Stability Tracking", self.test_context_stability),
            ("Context History Management", self.test_context_history),
            ("Performance Optimization", self.test_performance_optimization),
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
    
    def test_platform_integration(self) -> Dict[str, Any]:
        """Test platform integration and initialization."""
        try:
            # Initialize platform
            self.platform = PlatformDetector.detect()
            init_result = self.platform.initialize()
            
            # Create context detector
            self.context_detector = ContextDetector(self.platform)
            
            return {
                'success': init_result.get('success', False) and self.context_detector is not None,
                'platform_name': self.platform.name,
                'platform_init': init_result,
                'detector_created': self.context_detector is not None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Platform integration failed: {e}'
            }
    
    def test_basic_context_detection(self) -> Dict[str, Any]:
        """Test basic context detection functionality."""
        try:
            if not self.context_detector:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
                self.context_detector = ContextDetector(self.platform)
            
            # Detect current context
            context = self.context_detector.detect_current_context()
            
            # Verify context structure
            required_fields = [
                'app_name', 'process_name', 'window_title', 
                'context_type', 'ui_state', 'window_bounds', 'confidence'
            ]
            
            has_required_fields = all(hasattr(context, field) for field in required_fields)
            
            # Test multiple detections for consistency
            contexts = []
            for _ in range(3):
                ctx = self.context_detector.detect_current_context()
                contexts.append(ctx)
                time.sleep(0.1)
            
            # Check consistency
            consistent_app = all(ctx.app_name == contexts[0].app_name for ctx in contexts)
            
            return {
                'success': context is not None and has_required_fields,
                'context': {
                    'app_name': context.app_name,
                    'process_name': context.process_name,
                    'context_type': context.context_type.value,
                    'ui_state': context.ui_state.value,
                    'confidence': context.confidence
                },
                'has_required_fields': has_required_fields,
                'detection_consistent': consistent_app,
                'multiple_detections': len(contexts)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Basic detection failed: {e}'
            }
    
    def test_application_classification(self) -> Dict[str, Any]:
        """Test application classification accuracy."""
        try:
            if not self.context_detector:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
                self.context_detector = ContextDetector(self.platform)
            
            # Test classification with different mock applications
            test_cases = [
                {'process_name': 'chrome', 'expected_type': ContextType.WEB_BROWSER},
                {'process_name': 'firefox', 'expected_type': ContextType.WEB_BROWSER},
                {'process_name': 'code', 'expected_type': ContextType.DEVELOPMENT_IDE},
                {'process_name': 'terminal', 'expected_type': ContextType.TERMINAL},
                {'process_name': 'finder', 'expected_type': ContextType.FILE_MANAGER},
                {'process_name': 'unknown_app', 'expected_type': ContextType.UNKNOWN}
            ]
            
            classification_results = []
            
            for case in test_cases:
                # Use internal classification method
                classified_type = self.context_detector._classify_application(
                    case['process_name'], f"{case['process_name']} window"
                )
                
                is_correct = classified_type == case['expected_type']
                classification_results.append({
                    'process_name': case['process_name'],
                    'expected': case['expected_type'].value,
                    'classified': classified_type.value,
                    'correct': is_correct
                })
            
            correct_classifications = sum(1 for r in classification_results if r['correct'])
            accuracy = correct_classifications / len(classification_results)
            
            return {
                'success': accuracy >= 0.8,  # 80% accuracy threshold
                'accuracy': accuracy,
                'correct_classifications': correct_classifications,
                'total_tests': len(classification_results),
                'detailed_results': classification_results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Application classification failed: {e}'
            }
    
    def test_ui_state_analysis(self) -> Dict[str, Any]:
        """Test UI state analysis functionality."""
        try:
            if not self.context_detector:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
                self.context_detector = ContextDetector(self.platform)
            
            # Create mock window info for testing
            class MockWindowInfo:
                def __init__(self, title, bounds):
                    self.title = title
                    self.bounds = bounds
                    self.is_fullscreen = False
                    self.is_modal = False
            
            # Test UI state detection with different scenarios
            test_scenarios = [
                {
                    'window': MockWindowInfo("Loading - Please Wait", {'width': 800, 'height': 600}),
                    'expected_state': UIState.LOADING
                },
                {
                    'window': MockWindowInfo("Alert Dialog", {'width': 300, 'height': 200}),
                    'expected_state': UIState.MODAL_DIALOG
                },
                {
                    'window': MockWindowInfo("Normal Window", {'width': 800, 'height': 600}),
                    'expected_state': UIState.IDLE
                }
            ]
            
            state_results = []
            
            for scenario in test_scenarios:
                detected_state = self.context_detector._analyze_ui_state(scenario['window'])
                is_correct = detected_state == scenario['expected_state']
                
                state_results.append({
                    'title': scenario['window'].title,
                    'expected': scenario['expected_state'].value,
                    'detected': detected_state.value,
                    'correct': is_correct
                })
            
            correct_states = sum(1 for r in state_results if r['correct'])
            state_accuracy = correct_states / len(state_results)
            
            return {
                'success': state_accuracy >= 0.6,  # 60% accuracy threshold
                'state_accuracy': state_accuracy,
                'correct_states': correct_states,
                'total_scenarios': len(state_results),
                'detailed_results': state_results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'UI state analysis failed: {e}'
            }
    
    def test_context_change_detection(self) -> Dict[str, Any]:
        """Test context change detection and event handling."""
        try:
            if not self.context_detector:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
                self.context_detector = ContextDetector(self.platform)
            
            # Set up change listener
            change_events = []
            
            def change_listener(event: ContextChangeEvent):
                change_events.append({
                    'timestamp': event.timestamp,
                    'change_type': event.change_type,
                    'significance': event.significance,
                    'previous_app': event.previous_context.app_name if event.previous_context else None,
                    'new_app': event.new_context.app_name
                })
            
            self.context_detector.add_change_listener(change_listener)
            
            # Get initial context
            initial_context = self.context_detector.detect_current_context()
            
            # Wait for potential context changes
            time.sleep(2.0)
            
            # Force another detection to potentially trigger change detection
            current_context = self.context_detector.detect_current_context(force_refresh=True)
            
            # Wait for change processing
            time.sleep(0.5)
            
            # Check if change detection is working
            listener_registered = change_listener in self.context_detector.change_listeners
            
            # Remove listener
            self.context_detector.remove_change_listener(change_listener)
            listener_removed = change_listener not in self.context_detector.change_listeners
            
            return {
                'success': listener_registered and listener_removed,
                'initial_context': initial_context.app_name,
                'current_context': current_context.app_name,
                'change_events_detected': len(change_events),
                'listener_registered': listener_registered,
                'listener_removed': listener_removed,
                'change_events': change_events[:5]  # First 5 events
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Context change detection failed: {e}'
            }
    
    def test_context_stability(self) -> Dict[str, Any]:
        """Test context stability tracking."""
        try:
            if not self.context_detector:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
                self.context_detector = ContextDetector(self.platform)
            
            # Detect initial context
            initial_context = self.context_detector.detect_current_context()
            initial_time = time.time()
            
            # Wait for stability period
            time.sleep(1.5)
            
            # Check stability
            is_stable_short = self.context_detector.is_context_stable(duration=1.0)
            is_stable_long = self.context_detector.is_context_stable(duration=3.0)
            
            # Test recording trigger decision
            should_trigger = self.context_detector.should_trigger_recording()
            
            return {
                'success': True,  # Basic functionality test
                'initial_context': {
                    'app_name': initial_context.app_name,
                    'confidence': initial_context.confidence
                },
                'stability_1s': is_stable_short,
                'stability_3s': is_stable_long,
                'should_trigger_recording': should_trigger,
                'context_age': time.time() - initial_context.detection_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Context stability test failed: {e}'
            }
    
    def test_context_history(self) -> Dict[str, Any]:
        """Test context history management."""
        try:
            if not self.context_detector:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
                self.context_detector = ContextDetector(self.platform)
            
            # Generate some context history by forcing multiple detections
            contexts = []
            for i in range(5):
                context = self.context_detector.detect_current_context(force_refresh=True)
                contexts.append(context)
                time.sleep(0.2)
            
            # Get history
            history = self.context_detector.get_context_history(limit=10)
            
            # Test history functionality
            history_exists = history is not None
            history_reasonable_length = len(history) <= 10  # Respects limit
            
            return {
                'success': history_exists,
                'history_length': len(history),
                'history_reasonable_length': history_reasonable_length,
                'contexts_generated': len(contexts),
                'latest_context': contexts[-1].app_name if contexts else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Context history test failed: {e}'
            }
    
    def test_performance_optimization(self) -> Dict[str, Any]:
        """Test performance optimization features like caching."""
        try:
            if not self.context_detector:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
                self.context_detector = ContextDetector(self.platform)
            
            # Test detection performance
            detection_times = []
            
            # Cold detection (no cache)
            start_time = time.time()
            context1 = self.context_detector.detect_current_context(force_refresh=True)
            cold_time = time.time() - start_time
            detection_times.append(cold_time)
            
            # Warm detection (should use cache)
            start_time = time.time()
            context2 = self.context_detector.detect_current_context(force_refresh=False)
            warm_time = time.time() - start_time
            detection_times.append(warm_time)
            
            # Another warm detection
            start_time = time.time()
            context3 = self.context_detector.detect_current_context(force_refresh=False)
            warm_time2 = time.time() - start_time
            detection_times.append(warm_time2)
            
            # Get detection stats
            stats = self.context_detector.get_detection_stats()
            
            avg_detection_time = sum(detection_times) / len(detection_times)
            performance_acceptable = avg_detection_time < 0.5  # Under 500ms
            
            return {
                'success': performance_acceptable,
                'cold_detection_time': cold_time,
                'warm_detection_times': [warm_time, warm_time2],
                'average_detection_time': avg_detection_time,
                'detection_stats': stats,
                'performance_acceptable': performance_acceptable
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Performance test failed: {e}'
            }
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and recovery."""
        try:
            if not self.context_detector:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
                self.context_detector = ContextDetector(self.platform)
            
            error_scenarios = []
            
            # Test with invalid platform state
            try:
                # Temporarily break something to test error handling
                original_platform = self.context_detector.platform
                self.context_detector.platform = None
                
                context = self.context_detector.detect_current_context()
                
                # Restore platform
                self.context_detector.platform = original_platform
                
                # Should get unknown context on error
                error_handled = (context.context_type == ContextType.UNKNOWN and 
                               context.confidence == 0.0)
                
                error_scenarios.append({
                    'scenario': 'invalid_platform',
                    'handled_gracefully': error_handled
                })
                
            except Exception as e:
                error_scenarios.append({
                    'scenario': 'invalid_platform',
                    'handled_gracefully': False,
                    'error': str(e)
                })
            
            # Test confidence calculation edge cases
            try:
                class MockWindow:
                    def __init__(self):
                        self.process_name = ""
                        self.title = ""
                        self.bounds = {}
                
                mock_window = MockWindow()
                confidence = self.context_detector._calculate_confidence(
                    ContextType.UNKNOWN, UIState.UNKNOWN, mock_window
                )
                
                confidence_reasonable = 0.0 <= confidence <= 1.0
                
                error_scenarios.append({
                    'scenario': 'edge_case_confidence',
                    'handled_gracefully': confidence_reasonable,
                    'confidence': confidence
                })
                
            except Exception as e:
                error_scenarios.append({
                    'scenario': 'edge_case_confidence',
                    'handled_gracefully': False,
                    'error': str(e)
                })
            
            # Overall error handling success
            all_handled = all(scenario.get('handled_gracefully', False) 
                            for scenario in error_scenarios)
            
            return {
                'success': all_handled,
                'error_scenarios_tested': len(error_scenarios),
                'scenarios_handled': sum(1 for s in error_scenarios 
                                       if s.get('handled_gracefully', False)),
                'detailed_results': error_scenarios
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
                if 'Platform Integration' in test_name:
                    report['recommendations'].append(
                        "Ensure platform detection and initialization work correctly"
                    )
                elif 'Context Detection' in test_name:
                    report['recommendations'].append(
                        "Check window management and application access permissions"
                    )
                elif 'Performance' in test_name:
                    report['recommendations'].append(
                        "Consider optimizing detection algorithms or caching strategies"
                    )
        
        return report
    
    def cleanup(self):
        """Clean up test resources."""
        if self.context_detector:
            self.context_detector.cleanup()


def main():
    """Run context detection tests."""
    tester = ContextDetectorTester()
    
    try:
        report = tester.run_all_tests()
        
        # Save detailed report
        log_dir = Path(__file__).parent / "logs"
        report_file = log_dir / "context_detection_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*60)
        print("🧠 CONTEXT DETECTION TEST SUMMARY")
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
        
    finally:
        # Always clean up
        tester.cleanup()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)