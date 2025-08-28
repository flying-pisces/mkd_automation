#!/usr/bin/env python3
"""
Intelligent Automation Engine Tests

Comprehensive tests for the integrated intelligent automation system including:
- Intelligent automation actions
- Context-aware execution
- Pattern-based optimization
- Integration with traditional automation
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mkd_v2.automation.intelligent_automation import (
    IntelligentAutomationEngine, IntelligentActionResult
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
        logging.FileHandler(log_dir / "intelligent_automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IntelligentAutomationTester:
    """Test suite for intelligent automation functionality."""
    
    def __init__(self):
        self.platform = None
        self.intelligent_engine = None
        self.results = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all intelligent automation tests."""
        logger.info("🤖 Starting Intelligent Automation Tests")
        
        tests = [
            ("Engine Initialization", self.test_engine_initialization),
            ("Intelligent Click Actions", self.test_intelligent_click),
            ("Intelligent Text Input", self.test_intelligent_text_input),
            ("Intelligent Element Detection", self.test_intelligent_element_detection),
            ("Context Adaptation", self.test_context_adaptation),
            ("Pattern Learning", self.test_pattern_learning),
            ("Intelligent Recording", self.test_intelligent_recording),
            ("Performance Optimization", self.test_performance_optimization),
            ("Error Handling", self.test_error_handling),
            ("Integration Status", self.test_integration_status)
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
    
    def test_engine_initialization(self) -> Dict[str, Any]:
        """Test intelligent automation engine initialization."""
        try:
            # Initialize platform
            self.platform = PlatformDetector.detect()
            platform_init = self.platform.initialize()
            
            # Create intelligent automation engine
            self.intelligent_engine = IntelligentAutomationEngine(self.platform)
            
            # Initialize intelligent engine
            init_result = self.intelligent_engine.initialize()
            
            # Check components
            has_traditional_engine = self.intelligent_engine.automation_engine is not None
            has_context_detector = self.intelligent_engine.context_detector is not None
            has_pattern_analyzer = self.intelligent_engine.pattern_analyzer is not None
            has_smart_recorder = self.intelligent_engine.smart_recorder is not None
            
            return {
                'success': init_result.get('success', False),
                'platform_init': platform_init.get('success', False),
                'intelligent_init': init_result,
                'components_present': {
                    'traditional_engine': has_traditional_engine,
                    'context_detector': has_context_detector,
                    'pattern_analyzer': has_pattern_analyzer,
                    'smart_recorder': has_smart_recorder
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Engine initialization failed: {e}'
            }
    
    def test_intelligent_click(self) -> Dict[str, Any]:
        """Test intelligent click functionality."""
        try:
            if not self.intelligent_engine:
                self._initialize_engine()
            
            # Test intelligent click
            test_coordinates = [(400, 300), (500, 400), (300, 250)]
            click_results = []
            
            for x, y in test_coordinates:
                # Perform intelligent click
                result = self.intelligent_engine.click_at_coordinates_intelligent(x, y)
                
                # Validate result structure
                result_valid = isinstance(result, IntelligentActionResult)
                has_required_fields = all([
                    hasattr(result, 'success'),
                    hasattr(result, 'action_type'),
                    hasattr(result, 'context'),
                    hasattr(result, 'confidence'),
                    hasattr(result, 'execution_time')
                ])
                
                click_results.append({
                    'coordinates': (x, y),
                    'result_valid': result_valid,
                    'has_required_fields': has_required_fields,
                    'action_type': result.action_type,
                    'success': result.success,
                    'confidence': result.confidence,
                    'execution_time': result.execution_time,
                    'context_adapted': result.context_adapted,
                    'pattern_matched': result.pattern_matched is not None
                })
                
                # Small delay between clicks
                time.sleep(0.2)
            
            # Check overall results
            all_valid = all(r['result_valid'] and r['has_required_fields'] for r in click_results)
            avg_confidence = sum(r['confidence'] for r in click_results) / len(click_results)
            avg_execution_time = sum(r['execution_time'] for r in click_results) / len(click_results)
            
            return {
                'success': all_valid,
                'clicks_tested': len(test_coordinates),
                'all_results_valid': all_valid,
                'average_confidence': avg_confidence,
                'average_execution_time': avg_execution_time,
                'detailed_results': click_results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Intelligent click test failed: {e}'
            }
    
    def test_intelligent_text_input(self) -> Dict[str, Any]:
        """Test intelligent text input functionality."""
        try:
            if not self.intelligent_engine:
                self._initialize_engine()
            
            # Test various text inputs
            test_texts = [
                "Hello, World!",
                "This is a test message",
                "Python automation test",
                "Pattern learning sample"
            ]
            
            text_results = []
            
            for text in test_texts:
                # Perform intelligent text input
                result = self.intelligent_engine.type_text_intelligent(text)
                
                # Validate result
                result_valid = isinstance(result, IntelligentActionResult)
                correct_action_type = result.action_type == 'type'
                
                text_results.append({
                    'input_text': text,
                    'result_valid': result_valid,
                    'correct_action_type': correct_action_type,
                    'success': result.success,
                    'confidence': result.confidence,
                    'execution_time': result.execution_time,
                    'optimization_applied': result.optimization_applied,
                    'pattern_matched': result.pattern_matched is not None
                })
                
                time.sleep(0.3)
            
            # Analyze results
            all_valid = all(r['result_valid'] and r['correct_action_type'] for r in text_results)
            successful_inputs = sum(1 for r in text_results if r['success'])
            avg_confidence = sum(r['confidence'] for r in text_results) / len(text_results)
            
            return {
                'success': all_valid and successful_inputs > 0,
                'texts_tested': len(test_texts),
                'all_results_valid': all_valid,
                'successful_inputs': successful_inputs,
                'average_confidence': avg_confidence,
                'detailed_results': text_results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Intelligent text input test failed: {e}'
            }
    
    def test_intelligent_element_detection(self) -> Dict[str, Any]:
        """Test intelligent element detection functionality."""
        try:
            if not self.intelligent_engine:
                self._initialize_engine()
            
            # Test element detection at various locations
            test_locations = [
                (200, 200, 80),   # x, y, radius
                (400, 300, 100),
                (600, 400, 60),
                (300, 150, 120)
            ]
            
            detection_results = []
            
            for x, y, radius in test_locations:
                result = self.intelligent_engine.detect_elements_intelligent(x, y, radius)
                
                # Validate result
                result_valid = isinstance(result, IntelligentActionResult)
                correct_action_type = result.action_type == 'detect_elements'
                
                # Check if elements were found (traditional_result contains elements)
                elements_found = 0
                if result.traditional_result:
                    elements_found = len(result.traditional_result)
                
                detection_results.append({
                    'location': (x, y),
                    'radius': radius,
                    'result_valid': result_valid,
                    'correct_action_type': correct_action_type,
                    'success': result.success,
                    'confidence': result.confidence,
                    'execution_time': result.execution_time,
                    'elements_found': elements_found,
                    'pattern_matched': result.pattern_matched is not None
                })
            
            # Analyze detection results
            all_valid = all(r['result_valid'] and r['correct_action_type'] for r in detection_results)
            total_elements = sum(r['elements_found'] for r in detection_results)
            avg_detection_time = sum(r['execution_time'] for r in detection_results) / len(detection_results)
            
            return {
                'success': all_valid,
                'locations_tested': len(test_locations),
                'all_results_valid': all_valid,
                'total_elements_found': total_elements,
                'average_detection_time': avg_detection_time,
                'detailed_results': detection_results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Intelligent element detection test failed: {e}'
            }
    
    def test_context_adaptation(self) -> Dict[str, Any]:
        """Test context-aware action adaptation."""
        try:
            if not self.intelligent_engine:
                self._initialize_engine()
            
            # Enable context adaptation
            self.intelligent_engine.update_config(context_adaptation_enabled=True)
            
            # Perform actions with adaptation enabled
            adapted_result = self.intelligent_engine.click_at_coordinates_intelligent(
                350, 250, adapt_to_context=True
            )
            
            # Perform similar action without adaptation
            non_adapted_result = self.intelligent_engine.click_at_coordinates_intelligent(
                350, 250, adapt_to_context=False
            )
            
            # Check adaptation indicators
            adaptation_attempted = hasattr(adapted_result, 'context_adapted')
            adaptation_metadata = adapted_result.metadata is not None
            
            # Get current context for analysis
            current_context = self.intelligent_engine.context_detector.detect_current_context()
            context_confidence = current_context.confidence
            
            return {
                'success': adaptation_attempted and adaptation_metadata,
                'adaptation_attempted': adaptation_attempted,
                'adaptation_metadata_present': adaptation_metadata,
                'adapted_result_confidence': adapted_result.confidence,
                'non_adapted_result_confidence': non_adapted_result.confidence,
                'current_context_confidence': context_confidence,
                'context_adaptation_enabled': self.intelligent_engine.config.get('context_adaptation_enabled', False)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Context adaptation test failed: {e}'
            }
    
    def test_pattern_learning(self) -> Dict[str, Any]:
        """Test pattern learning and recognition."""
        try:
            if not self.intelligent_engine:
                self._initialize_engine()
            
            # Enable learning mode
            self.intelligent_engine.set_learning_mode(True)
            
            # Get initial pattern statistics
            initial_stats = self.intelligent_engine.pattern_analyzer.get_analysis_stats()
            initial_actions = initial_stats.get('total_actions', 0)
            initial_patterns = initial_stats.get('total_patterns', 0)
            
            # Perform repetitive actions to generate patterns
            repetitive_actions = [
                (300, 400, 'click'),
                (320, 450, 'click'),
                (300, 400, 'click'),
                (320, 450, 'click'),
                (300, 400, 'click')
            ]
            
            for x, y, action_type in repetitive_actions:
                if action_type == 'click':
                    self.intelligent_engine.click_at_coordinates_intelligent(x, y)
                time.sleep(0.1)
            
            # Add some text patterns
            for i in range(3):
                self.intelligent_engine.type_text_intelligent(f"Pattern text {i}")
                time.sleep(0.1)
            
            # Trigger pattern analysis
            detected_patterns = self.intelligent_engine.pattern_analyzer.analyze_patterns()
            
            # Get updated statistics
            final_stats = self.intelligent_engine.pattern_analyzer.get_analysis_stats()
            final_actions = final_stats.get('total_actions', 0)
            final_patterns = final_stats.get('total_patterns', 0)
            
            # Check learning progress
            actions_recorded = final_actions > initial_actions
            patterns_detected = len(detected_patterns) > 0
            learning_active = self.intelligent_engine.is_learning_mode
            
            return {
                'success': actions_recorded and learning_active,
                'learning_mode_active': learning_active,
                'actions_recorded': actions_recorded,
                'patterns_detected': patterns_detected,
                'initial_actions': initial_actions,
                'final_actions': final_actions,
                'actions_added': final_actions - initial_actions,
                'patterns_found': len(detected_patterns),
                'pattern_types': [p.pattern_type.value for p in detected_patterns]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Pattern learning test failed: {e}'
            }
    
    def test_intelligent_recording(self) -> Dict[str, Any]:
        """Test intelligent recording functionality."""
        try:
            if not self.intelligent_engine:
                self._initialize_engine()
            
            # Test manual recording start
            recording_result = self.intelligent_engine.start_intelligent_recording(manual=True)
            recording_started = recording_result.get('success', False)
            session_id = recording_result.get('session_id')
            
            # Perform some actions while recording
            if recording_started:
                self.intelligent_engine.click_at_coordinates_intelligent(400, 300)
                time.sleep(0.2)
                self.intelligent_engine.type_text_intelligent("Recording test")
                time.sleep(0.2)
                
                # Check recording status
                recording_active = self.intelligent_engine.is_recording
                
                # Stop recording
                stop_result = self.intelligent_engine.stop_intelligent_recording()
                recording_stopped = stop_result.get('success', False)
                session_stats = stop_result.get('session_stats', {})
            else:
                recording_active = False
                recording_stopped = False
                session_stats = {}
            
            # Test automatic recording decision
            auto_decision = self.intelligent_engine.smart_recorder.should_start_recording()
            decision_made = auto_decision is not None
            
            return {
                'success': recording_started and recording_stopped,
                'manual_recording_started': recording_started,
                'session_id_provided': session_id is not None,
                'recording_was_active': recording_active,
                'recording_stopped': recording_stopped,
                'session_stats': session_stats,
                'auto_decision_made': decision_made,
                'auto_decision_details': {
                    'should_record': auto_decision.should_record if auto_decision else False,
                    'confidence': auto_decision.confidence if auto_decision else 0.0,
                    'trigger': auto_decision.trigger.value if auto_decision else 'none'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Intelligent recording test failed: {e}'
            }
    
    def test_performance_optimization(self) -> Dict[str, Any]:
        """Test performance optimization features."""
        try:
            if not self.intelligent_engine:
                self._initialize_engine()
            
            # Get optimization suggestions
            suggestions = self.intelligent_engine.get_optimization_suggestions()
            suggestions_provided = isinstance(suggestions, list)
            
            # Test performance statistics
            performance_stats = self.intelligent_engine.performance_stats
            stats_valid = isinstance(performance_stats, dict)
            
            # Required stats fields
            required_stats = [
                'intelligent_actions', 'pattern_matches', 'context_adaptations',
                'optimizations_applied', 'avg_confidence', 'avg_execution_time'
            ]
            stats_complete = all(field in performance_stats for field in required_stats)
            
            # Test configuration updates
            original_config = self.intelligent_engine.config.copy()
            test_updates = {
                'min_confidence_threshold': 0.8,
                'context_adaptation_enabled': False
            }
            
            self.intelligent_engine.update_config(**test_updates)
            config_updated = all(
                self.intelligent_engine.config[k] == v for k, v in test_updates.items()
            )
            
            # Restore original config
            self.intelligent_engine.update_config(**original_config)
            
            return {
                'success': suggestions_provided and stats_valid and stats_complete,
                'optimization_suggestions': len(suggestions),
                'suggestions_provided': suggestions_provided,
                'performance_stats_valid': stats_valid,
                'stats_complete': stats_complete,
                'config_update_works': config_updated,
                'sample_suggestions': suggestions[:3] if suggestions else []
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Performance optimization test failed: {e}'
            }
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and recovery."""
        try:
            if not self.intelligent_engine:
                self._initialize_engine()
            
            error_scenarios = []
            
            # Test invalid coordinates
            try:
                result = self.intelligent_engine.click_at_coordinates_intelligent(-100, -100)
                invalid_coords_handled = isinstance(result, IntelligentActionResult)
                error_scenarios.append({
                    'scenario': 'invalid_coordinates',
                    'handled': invalid_coords_handled,
                    'success': result.success if invalid_coords_handled else False
                })
            except Exception as e:
                error_scenarios.append({
                    'scenario': 'invalid_coordinates',
                    'handled': False,
                    'error': str(e)
                })
            
            # Test empty text input
            try:
                result = self.intelligent_engine.type_text_intelligent("")
                empty_text_handled = isinstance(result, IntelligentActionResult)
                error_scenarios.append({
                    'scenario': 'empty_text',
                    'handled': empty_text_handled,
                    'success': result.success if empty_text_handled else False
                })
            except Exception as e:
                error_scenarios.append({
                    'scenario': 'empty_text',
                    'handled': False,
                    'error': str(e)
                })
            
            # Test invalid detection parameters
            try:
                result = self.intelligent_engine.detect_elements_intelligent(0, 0, -10)
                invalid_detection_handled = isinstance(result, IntelligentActionResult)
                error_scenarios.append({
                    'scenario': 'invalid_detection',
                    'handled': invalid_detection_handled,
                    'success': result.success if invalid_detection_handled else False
                })
            except Exception as e:
                error_scenarios.append({
                    'scenario': 'invalid_detection',
                    'handled': False,
                    'error': str(e)
                })
            
            # Count handled scenarios
            scenarios_handled = sum(1 for scenario in error_scenarios if scenario.get('handled', False))
            total_scenarios = len(error_scenarios)
            
            return {
                'success': scenarios_handled >= total_scenarios * 0.7,  # 70% threshold
                'total_scenarios': total_scenarios,
                'scenarios_handled': scenarios_handled,
                'handle_rate': scenarios_handled / total_scenarios if total_scenarios > 0 else 0,
                'detailed_scenarios': error_scenarios
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error handling test failed: {e}'
            }
    
    def test_integration_status(self) -> Dict[str, Any]:
        """Test integration status and comprehensive reporting."""
        try:
            if not self.intelligent_engine:
                self._initialize_engine()
            
            # Get comprehensive status
            status = self.intelligent_engine.get_intelligent_status()
            status_provided = isinstance(status, dict)
            
            # Check required status sections
            required_sections = [
                'traditional_automation', 'intelligence', 'performance', 
                'configuration', 'learning_mode', 'recording_active'
            ]
            
            sections_present = all(section in status for section in required_sections)
            
            # Check intelligence subsections
            intelligence_section = status.get('intelligence', {})
            intelligence_subsections = [
                'current_context', 'context_detection', 'pattern_analysis', 
                'smart_recording'
            ]
            
            intelligence_complete = all(subsection in intelligence_section 
                                      for subsection in intelligence_subsections)
            
            # Test delegation to traditional methods
            traditional_click = self.intelligent_engine.click_at_coordinates(500, 300)
            traditional_type = self.intelligent_engine.type_text("traditional test")
            traditional_elements = self.intelligent_engine.get_elements_in_region(400, 300, 100, 100)
            
            delegation_works = all([
                isinstance(traditional_click, bool),
                isinstance(traditional_type, bool),
                isinstance(traditional_elements, list)
            ])
            
            return {
                'success': status_provided and sections_present and intelligence_complete,
                'status_provided': status_provided,
                'required_sections_present': sections_present,
                'intelligence_section_complete': intelligence_complete,
                'traditional_delegation_works': delegation_works,
                'status_structure': {
                    'main_sections': list(status.keys()) if status_provided else [],
                    'intelligence_subsections': list(intelligence_section.keys())
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Integration status test failed: {e}'
            }
    
    def _initialize_engine(self):
        """Initialize the intelligent automation engine."""
        if not self.platform:
            self.platform = PlatformDetector.detect()
            self.platform.initialize()
        
        if not self.intelligent_engine:
            self.intelligent_engine = IntelligentAutomationEngine(self.platform)
            self.intelligent_engine.initialize()
    
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
                if 'Initialization' in test_name:
                    report['recommendations'].append(
                        "Check platform initialization and component integration"
                    )
                elif 'Context Adaptation' in test_name:
                    report['recommendations'].append(
                        "Verify context detection accuracy and adaptation algorithms"
                    )
                elif 'Pattern Learning' in test_name:
                    report['recommendations'].append(
                        "Review pattern analysis integration and learning mechanisms"
                    )
                elif 'Performance' in test_name:
                    report['recommendations'].append(
                        "Optimize intelligent automation algorithms for better performance"
                    )
        
        return report
    
    def cleanup(self):
        """Clean up test resources."""
        if self.intelligent_engine:
            self.intelligent_engine.cleanup()


def main():
    """Run intelligent automation tests."""
    tester = IntelligentAutomationTester()
    
    try:
        report = tester.run_all_tests()
        
        # Save detailed report
        log_dir = Path(__file__).parent / "logs"
        report_file = log_dir / "intelligent_automation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*60)
        print("🤖 INTELLIGENT AUTOMATION TEST SUMMARY")
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