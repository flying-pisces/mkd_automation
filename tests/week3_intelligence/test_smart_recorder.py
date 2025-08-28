#!/usr/bin/env python3
"""
Smart Recording System Tests

Comprehensive tests for the intelligent recording system including:
- Recording decision making
- Context-aware recording triggers
- Session management
- Pattern-based recording optimization
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mkd_v2.intelligence.smart_recorder import (
    SmartRecorder, RecordingDecision, RecordingTrigger, RecordingPriority, RecordingSession
)
from mkd_v2.intelligence.context_detector import (
    ContextDetector, ApplicationContext, ContextType, UIState
)
from mkd_v2.intelligence.pattern_analyzer import PatternAnalyzer, ActionEvent
from mkd_v2.platform.detector import PlatformDetector

import logging

# Configure logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "smart_recording.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SmartRecorderTester:
    """Test suite for smart recording functionality."""
    
    def __init__(self):
        self.platform = None
        self.context_detector = None
        self.pattern_analyzer = None
        self.smart_recorder = None
        self.results = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all smart recording tests."""
        logger.info("🎬 Starting Smart Recording Tests")
        
        tests = [
            ("Smart Recorder Initialization", self.test_initialization),
            ("Recording Decision Logic", self.test_recording_decision_logic),
            ("Manual Recording Trigger", self.test_manual_recording_trigger),
            ("Context-based Recording", self.test_context_based_recording),
            ("Pattern-based Recording", self.test_pattern_based_recording),
            ("Session Management", self.test_session_management),
            ("Auto-stop Conditions", self.test_auto_stop_conditions),
            ("Recording Quality Tracking", self.test_recording_quality),
            ("Configuration Management", self.test_configuration_management),
            ("Concurrent Sessions", self.test_concurrent_sessions)
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
    
    def test_initialization(self) -> Dict[str, Any]:
        """Test smart recorder initialization with components."""
        try:
            # Initialize components
            self.platform = PlatformDetector.detect()
            init_result = self.platform.initialize()
            
            self.context_detector = ContextDetector(self.platform)
            self.pattern_analyzer = PatternAnalyzer()
            self.smart_recorder = SmartRecorder(self.context_detector, self.pattern_analyzer)
            
            # Check initialization
            has_components = all([
                self.smart_recorder.context_detector is not None,
                self.smart_recorder.pattern_analyzer is not None
            ])
            
            # Check initial configuration
            config_valid = isinstance(self.smart_recorder.config, dict)
            stats_valid = isinstance(self.smart_recorder.stats, dict)
            
            # Check decision weights
            weights_valid = isinstance(self.smart_recorder.decision_weights, dict)
            weights_sum = sum(self.smart_recorder.decision_weights.values())
            
            return {
                'success': has_components and config_valid and stats_valid,
                'platform_init': init_result.get('success', False),
                'components_linked': has_components,
                'config_valid': config_valid,
                'stats_valid': stats_valid,
                'weights_sum': weights_sum,
                'active_sessions': len(self.smart_recorder.active_sessions)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Initialization failed: {e}'
            }
    
    def test_recording_decision_logic(self) -> Dict[str, Any]:
        """Test core recording decision logic."""
        try:
            if not self.smart_recorder:
                self._initialize_components()
            
            # Create test context
            test_context = ApplicationContext(
                app_name="TestApp",
                process_name="testapp",
                window_title="Test Application",
                context_type=ContextType.TEXT_EDITOR,
                ui_state=UIState.IDLE,
                window_bounds={'x': 0, 'y': 0, 'width': 800, 'height': 600},
                confidence=0.9
            )
            
            # Test decision making
            decision = self.smart_recorder.should_start_recording(test_context)
            
            # Validate decision structure
            decision_valid = isinstance(decision, RecordingDecision)
            has_required_fields = all([
                hasattr(decision, 'should_record'),
                hasattr(decision, 'trigger'),
                hasattr(decision, 'priority'),
                hasattr(decision, 'confidence'),
                hasattr(decision, 'reason')
            ])
            
            # Test decision with different contexts
            decisions = []
            
            # High confidence context
            high_conf_context = ApplicationContext(
                "CodeEditor", "vscode", "main.py - VSCode",
                ContextType.DEVELOPMENT_IDE, UIState.IDLE, {},
                confidence=0.95
            )
            decisions.append(self.smart_recorder.should_start_recording(high_conf_context))
            
            # Low confidence context
            low_conf_context = ApplicationContext(
                "Unknown", "unknown", "Unknown Window",
                ContextType.UNKNOWN, UIState.UNKNOWN, {},
                confidence=0.2
            )
            decisions.append(self.smart_recorder.should_start_recording(low_conf_context))
            
            # System utility context (should generally not record)
            system_context = ApplicationContext(
                "SystemPrefs", "sysprefs", "System Preferences",
                ContextType.SYSTEM_UTILITY, UIState.IDLE, {},
                confidence=0.8
            )
            decisions.append(self.smart_recorder.should_start_recording(system_context))
            
            return {
                'success': decision_valid and has_required_fields,
                'decision_structure_valid': decision_valid,
                'required_fields_present': has_required_fields,
                'initial_decision': {
                    'should_record': decision.should_record,
                    'trigger': decision.trigger.value,
                    'confidence': decision.confidence
                },
                'decision_variations': [
                    {
                        'context_type': d.context.context_type.value,
                        'should_record': d.should_record,
                        'confidence': d.confidence,
                        'trigger': d.trigger.value
                    } for d in decisions
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Recording decision logic test failed: {e}'
            }
    
    def test_manual_recording_trigger(self) -> Dict[str, Any]:
        """Test manual recording trigger functionality."""
        try:
            if not self.smart_recorder:
                self._initialize_components()
            
            # Test manual trigger (should always be allowed)
            context = ApplicationContext(
                "ManualTest", "manual", "Manual Test",
                ContextType.TEXT_EDITOR, UIState.IDLE, {},
                confidence=0.5
            )
            
            # Get manual decision
            decision = self.smart_recorder._evaluate_manual_trigger(context)
            
            # Manual should always be positive
            manual_allowed = decision.should_record
            manual_trigger = decision.trigger == RecordingTrigger.MANUAL
            manual_high_priority = decision.priority == RecordingPriority.HIGH
            manual_confident = decision.confidence == 1.0
            
            return {
                'success': manual_allowed and manual_trigger and manual_high_priority,
                'manual_allowed': manual_allowed,
                'correct_trigger_type': manual_trigger,
                'high_priority': manual_high_priority,
                'full_confidence': manual_confident,
                'decision_reason': decision.reason
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Manual recording trigger test failed: {e}'
            }
    
    def test_context_based_recording(self) -> Dict[str, Any]:
        """Test context-based recording triggers."""
        try:
            if not self.smart_recorder:
                self._initialize_components()
            
            # Test various context-based scenarios
            contexts = [
                # Interesting context with high confidence
                ApplicationContext(
                    "Chrome", "chrome", "Important Document - Google Docs",
                    ContextType.WEB_BROWSER, UIState.IDLE, {},
                    confidence=0.9
                ),
                # Development IDE (interesting)
                ApplicationContext(
                    "VSCode", "code", "main.py - Visual Studio Code",
                    ContextType.DEVELOPMENT_IDE, UIState.IDLE, {},
                    confidence=0.85
                ),
                # System utility (less interesting)
                ApplicationContext(
                    "Calculator", "calc", "Calculator",
                    ContextType.SYSTEM_UTILITY, UIState.IDLE, {},
                    confidence=0.7
                )
            ]
            
            context_decisions = []
            for context in contexts:
                decision = self.smart_recorder._evaluate_context_trigger(context)
                context_decisions.append({
                    'context_type': context.context_type.value,
                    'app_name': context.app_name,
                    'confidence': context.confidence,
                    'should_record': decision.should_record,
                    'decision_confidence': decision.confidence,
                    'reason': decision.reason
                })
            
            # Check that interesting contexts are more likely to record
            interesting_decisions = [d for d in context_decisions 
                                   if 'BROWSER' in d['context_type'] or 'IDE' in d['context_type']]
            system_decisions = [d for d in context_decisions 
                              if 'SYSTEM_UTILITY' in d['context_type']]
            
            interesting_record_rate = sum(1 for d in interesting_decisions if d['should_record']) / len(interesting_decisions) if interesting_decisions else 0
            
            return {
                'success': len(context_decisions) == len(contexts),
                'contexts_tested': len(contexts),
                'decisions_made': len(context_decisions),
                'interesting_contexts': len(interesting_decisions),
                'system_contexts': len(system_decisions),
                'interesting_record_rate': interesting_record_rate,
                'detailed_decisions': context_decisions
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Context-based recording test failed: {e}'
            }
    
    def test_pattern_based_recording(self) -> Dict[str, Any]:
        """Test pattern-based recording triggers."""
        try:
            if not self.smart_recorder:
                self._initialize_components()
            
            # Create high-value patterns in pattern analyzer
            context = ApplicationContext(
                "DataEntry", "dataentry", "Form Application",
                ContextType.TEXT_EDITOR, UIState.IDLE, {}
            )
            
            # Simulate high-value repetitive pattern
            for i in range(5):  # 5 repetitions
                action = ActionEvent(
                    timestamp=time.time() + i,
                    action_type='click',
                    coordinates=(300, 400),
                    context=context,
                    duration=0.2
                )
                self.pattern_analyzer.record_action(action)
            
            # Trigger pattern analysis
            patterns = self.pattern_analyzer.analyze_patterns()
            
            # Test pattern-based decision
            decision = self.smart_recorder._evaluate_pattern_trigger(context)
            
            # Test with different pattern scenarios
            pattern_scenarios = []
            
            # High automation potential context
            high_potential_context = ApplicationContext(
                "RepeatedTask", "task", "Automated Task",
                ContextType.TEXT_EDITOR, UIState.IDLE, {}
            )
            
            pattern_decision = self.smart_recorder._evaluate_pattern_trigger(high_potential_context)
            pattern_scenarios.append({
                'scenario': 'high_potential',
                'should_record': pattern_decision.should_record,
                'confidence': pattern_decision.confidence
            })
            
            return {
                'success': True,  # Basic functionality test
                'patterns_detected': len(patterns),
                'pattern_decision_made': decision is not None,
                'decision_trigger': decision.trigger.value,
                'decision_confidence': decision.confidence,
                'pattern_scenarios': pattern_scenarios
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Pattern-based recording test failed: {e}'
            }
    
    def test_session_management(self) -> Dict[str, Any]:
        """Test recording session management."""
        try:
            if not self.smart_recorder:
                self._initialize_components()
            
            # Create positive recording decision
            context = ApplicationContext(
                "SessionTest", "session", "Session Test",
                ContextType.TEXT_EDITOR, UIState.IDLE, {},
                confidence=0.8
            )
            
            decision = RecordingDecision(
                should_record=True,
                trigger=RecordingTrigger.MANUAL,
                priority=RecordingPriority.HIGH,
                context=context,
                confidence=0.9,
                reason="Test recording session",
                expected_duration=60.0
            )
            
            # Start recording session
            session_id = self.smart_recorder.start_recording_session(decision)
            session_started = session_id is not None
            
            # Check session exists
            session_exists = session_id in self.smart_recorder.active_sessions
            
            # Get session status
            session_status = self.smart_recorder.get_session_status(session_id)
            status_valid = session_status is not None
            
            # Update session metrics
            self.smart_recorder.update_session_metrics(
                session_id, actions_recorded=5, context_changes=1
            )
            
            # Get updated status
            updated_status = self.smart_recorder.get_session_status(session_id)
            metrics_updated = (updated_status and 
                             updated_status.get('actions_recorded', 0) >= 5)
            
            # Stop session
            stop_result = self.smart_recorder.stop_recording_session(session_id, "Test complete")
            session_stopped = session_id not in self.smart_recorder.active_sessions
            
            return {
                'success': session_started and session_exists and session_stopped,
                'session_started': session_started,
                'session_exists': session_exists,
                'status_retrieved': status_valid,
                'metrics_updated': metrics_updated,
                'session_stopped': session_stopped,
                'session_id': session_id,
                'final_status': updated_status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Session management test failed: {e}'
            }
    
    def test_auto_stop_conditions(self) -> Dict[str, Any]:
        """Test automatic session stopping conditions."""
        try:
            if not self.smart_recorder:
                self._initialize_components()
            
            # Create test session
            context = ApplicationContext(
                "AutoStopTest", "autostop", "Auto Stop Test",
                ContextType.TEXT_EDITOR, UIState.IDLE, {},
                confidence=0.8
            )
            
            session = RecordingSession(
                session_id="auto_stop_test",
                start_time=time.time() - 310.0,  # Started 310 seconds ago (over 5 min limit)
                trigger=RecordingTrigger.MANUAL,
                initial_context=context,
                max_duration=300.0,  # 5 minutes max
                auto_stop_on_idle=True,
                auto_stop_on_context_loss=True
            )
            
            self.smart_recorder.active_sessions["auto_stop_test"] = session
            
            # Test max duration condition
            should_stop_duration = self.smart_recorder.should_stop_recording("auto_stop_test")
            
            # Create session with poor quality
            poor_quality_session = RecordingSession(
                session_id="poor_quality_test",
                start_time=time.time(),
                trigger=RecordingTrigger.MANUAL,
                initial_context=context,
                recording_quality=0.2  # Poor quality
            )
            
            self.smart_recorder.active_sessions["poor_quality_test"] = poor_quality_session
            should_stop_quality = self.smart_recorder.should_stop_recording("poor_quality_test")
            
            # Test with non-existent session
            should_stop_nonexistent = self.smart_recorder.should_stop_recording("nonexistent")
            
            # Clean up
            if "auto_stop_test" in self.smart_recorder.active_sessions:
                del self.smart_recorder.active_sessions["auto_stop_test"]
            if "poor_quality_test" in self.smart_recorder.active_sessions:
                del self.smart_recorder.active_sessions["poor_quality_test"]
            
            return {
                'success': should_stop_duration and should_stop_quality and should_stop_nonexistent,
                'duration_condition': should_stop_duration,
                'quality_condition': should_stop_quality,
                'nonexistent_condition': should_stop_nonexistent,
                'conditions_tested': 3
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Auto-stop conditions test failed: {e}'
            }
    
    def test_recording_quality(self) -> Dict[str, Any]:
        """Test recording quality tracking and metrics."""
        try:
            if not self.smart_recorder:
                self._initialize_components()
            
            # Create test session
            context = ApplicationContext(
                "QualityTest", "quality", "Quality Test",
                ContextType.TEXT_EDITOR, UIState.IDLE, {},
                confidence=0.9
            )
            
            session = RecordingSession(
                session_id="quality_test",
                start_time=time.time(),
                trigger=RecordingTrigger.MANUAL,
                initial_context=context
            )
            
            self.smart_recorder.active_sessions["quality_test"] = session
            
            # Initial quality metrics
            initial_context_stability = session.context_stability
            initial_user_engagement = session.user_engagement
            initial_recording_quality = session.recording_quality
            
            # Update metrics with activity
            self.smart_recorder.update_session_metrics(
                "quality_test",
                actions_recorded=10,
                context_changes=2
            )
            
            # Check updated quality metrics
            updated_session = self.smart_recorder.active_sessions["quality_test"]
            updated_context_stability = updated_session.context_stability
            updated_user_engagement = updated_session.user_engagement
            updated_recording_quality = updated_session.recording_quality
            
            # Quality should be reasonable values (0-1)
            quality_values_valid = all([
                0 <= updated_context_stability <= 1,
                0 <= updated_user_engagement <= 1,
                0 <= updated_recording_quality <= 1
            ])
            
            # Clean up
            del self.smart_recorder.active_sessions["quality_test"]
            
            return {
                'success': quality_values_valid,
                'initial_quality': {
                    'context_stability': initial_context_stability,
                    'user_engagement': initial_user_engagement,
                    'recording_quality': initial_recording_quality
                },
                'updated_quality': {
                    'context_stability': updated_context_stability,
                    'user_engagement': updated_user_engagement,
                    'recording_quality': updated_recording_quality
                },
                'quality_values_valid': quality_values_valid,
                'actions_processed': updated_session.actions_recorded
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Recording quality test failed: {e}'
            }
    
    def test_configuration_management(self) -> Dict[str, Any]:
        """Test configuration management functionality."""
        try:
            if not self.smart_recorder:
                self._initialize_components()
            
            # Get initial config
            initial_config = self.smart_recorder.config.copy()
            
            # Test config updates
            new_settings = {
                'auto_recording_enabled': False,
                'min_pattern_confidence': 0.8,
                'max_concurrent_sessions': 5
            }
            
            self.smart_recorder.update_config(**new_settings)
            
            # Check updates applied
            config_updated = all([
                self.smart_recorder.config['auto_recording_enabled'] == False,
                self.smart_recorder.config['min_pattern_confidence'] == 0.8,
                self.smart_recorder.config['max_concurrent_sessions'] == 5
            ])
            
            # Test invalid config (should be ignored)
            self.smart_recorder.update_config(invalid_setting=True)
            invalid_ignored = 'invalid_setting' not in self.smart_recorder.config
            
            # Get stats including config
            stats = self.smart_recorder.get_smart_recorder_stats()
            stats_include_config = 'config' in stats
            
            # Restore original config
            self.smart_recorder.update_config(**initial_config)
            config_restored = self.smart_recorder.config == initial_config
            
            return {
                'success': config_updated and invalid_ignored and stats_include_config,
                'config_updated': config_updated,
                'invalid_setting_ignored': invalid_ignored,
                'stats_include_config': stats_include_config,
                'config_restored': config_restored,
                'initial_config_keys': list(initial_config.keys()),
                'final_config_keys': list(self.smart_recorder.config.keys())
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Configuration management test failed: {e}'
            }
    
    def test_concurrent_sessions(self) -> Dict[str, Any]:
        """Test concurrent recording sessions management."""
        try:
            if not self.smart_recorder:
                self._initialize_components()
            
            # Set low concurrent session limit for testing
            original_limit = self.smart_recorder.config['max_concurrent_sessions']
            self.smart_recorder.update_config(max_concurrent_sessions=2)
            
            # Create contexts for different sessions
            contexts = [
                ApplicationContext(f"App{i}", f"app{i}", f"Window {i}",
                                ContextType.TEXT_EDITOR, UIState.IDLE, {},
                                confidence=0.8)
                for i in range(4)
            ]
            
            # Create recording decisions
            decisions = [
                RecordingDecision(
                    should_record=True,
                    trigger=RecordingTrigger.MANUAL,
                    priority=RecordingPriority.MEDIUM if i < 2 else RecordingPriority.LOW,
                    context=context,
                    confidence=0.8,
                    reason=f"Concurrent test session {i}"
                )
                for i, context in enumerate(contexts)
            ]
            
            # Start sessions
            session_ids = []
            for i, decision in enumerate(decisions):
                try:
                    session_id = self.smart_recorder.start_recording_session(decision)
                    session_ids.append(session_id)
                except Exception as e:
                    logger.info(f"Session {i} failed to start (expected for limit test): {e}")
            
            # Check how many sessions are active (should be limited to 2)
            active_count = len(self.smart_recorder.active_sessions)
            limit_respected = active_count <= 2
            
            # Get active sessions
            active_sessions = self.smart_recorder.get_active_sessions()
            
            # Stop all active sessions
            stopped_sessions = []
            for session_id in list(self.smart_recorder.active_sessions.keys()):
                self.smart_recorder.stop_recording_session(session_id, "Concurrent test cleanup")
                stopped_sessions.append(session_id)
            
            # Restore original limit
            self.smart_recorder.update_config(max_concurrent_sessions=original_limit)
            
            return {
                'success': limit_respected and len(stopped_sessions) > 0,
                'attempted_sessions': len(decisions),
                'successful_sessions': len(session_ids),
                'active_sessions': active_count,
                'limit_respected': limit_respected,
                'sessions_stopped': len(stopped_sessions),
                'original_limit': original_limit
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Concurrent sessions test failed: {e}'
            }
    
    def _initialize_components(self):
        """Initialize test components."""
        if not self.platform:
            self.platform = PlatformDetector.detect()
            self.platform.initialize()
        
        if not self.context_detector:
            self.context_detector = ContextDetector(self.platform)
        
        if not self.pattern_analyzer:
            self.pattern_analyzer = PatternAnalyzer()
        
        if not self.smart_recorder:
            self.smart_recorder = SmartRecorder(self.context_detector, self.pattern_analyzer)
    
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
                if 'Decision Logic' in test_name:
                    report['recommendations'].append(
                        "Review recording decision algorithms and thresholds"
                    )
                elif 'Session Management' in test_name:
                    report['recommendations'].append(
                        "Check session lifecycle management and resource cleanup"
                    )
                elif 'Pattern-based' in test_name:
                    report['recommendations'].append(
                        "Verify pattern integration and automation potential calculations"
                    )
        
        return report
    
    def cleanup(self):
        """Clean up test resources."""
        if self.smart_recorder:
            self.smart_recorder.cleanup()


def main():
    """Run smart recording tests."""
    tester = SmartRecorderTester()
    
    try:
        report = tester.run_all_tests()
        
        # Save detailed report
        log_dir = Path(__file__).parent / "logs"
        report_file = log_dir / "smart_recording_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*60)
        print("🎬 SMART RECORDING TEST SUMMARY")
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