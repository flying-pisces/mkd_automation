#!/usr/bin/env python3
"""
Pattern Analysis System Tests

Comprehensive tests for the intelligent pattern analysis system including:
- Action pattern detection
- Workflow sequence recognition  
- User behavior analysis
- Automation opportunity identification
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mkd_v2.intelligence.pattern_analyzer import (
    PatternAnalyzer, UserPattern, PatternType, ActionEvent
)
from mkd_v2.intelligence.context_detector import (
    ApplicationContext, ContextType, UIState
)

import logging

# Configure logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "pattern_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PatternAnalyzerTester:
    """Test suite for pattern analysis functionality."""
    
    def __init__(self):
        self.pattern_analyzer = PatternAnalyzer()
        self.results = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all pattern analysis tests."""
        logger.info("🔍 Starting Pattern Analysis Tests")
        
        tests = [
            ("Pattern Analyzer Initialization", self.test_initialization),
            ("Action Recording", self.test_action_recording),
            ("Repetitive Pattern Detection", self.test_repetitive_pattern_detection),
            ("Workflow Pattern Detection", self.test_workflow_pattern_detection),
            ("Context Switching Patterns", self.test_context_switching_patterns),
            ("Time-based Patterns", self.test_time_based_patterns),
            ("Pattern Similarity Calculation", self.test_pattern_similarity),
            ("Automation Potential Analysis", self.test_automation_potential),
            ("Pattern Export/Import", self.test_pattern_export),
            ("Performance Under Load", self.test_performance_load)
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
        """Test pattern analyzer initialization."""
        try:
            analyzer = PatternAnalyzer(max_history=500)
            
            # Check initialization
            has_action_history = hasattr(analyzer, 'action_history')
            has_context_history = hasattr(analyzer, 'context_history')
            has_pattern_templates = hasattr(analyzer, 'pattern_templates')
            has_detected_patterns = hasattr(analyzer, 'detected_patterns')
            
            # Check template initialization
            template_count = len(analyzer.pattern_templates)
            
            # Check stats initialization
            stats = analyzer.get_analysis_stats()
            stats_valid = isinstance(stats, dict) and 'total_actions' in stats
            
            return {
                'success': all([has_action_history, has_context_history, 
                              has_pattern_templates, has_detected_patterns, stats_valid]),
                'has_action_history': has_action_history,
                'has_context_history': has_context_history,
                'template_count': template_count,
                'initial_stats': stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Initialization failed: {e}'
            }
    
    def test_action_recording(self) -> Dict[str, Any]:
        """Test action recording functionality."""
        try:
            analyzer = PatternAnalyzer(max_history=100)
            
            # Create test context
            context = ApplicationContext(
                app_name="TestApp",
                process_name="testapp",
                window_title="Test Window",
                context_type=ContextType.TEXT_EDITOR,
                ui_state=UIState.IDLE,
                window_bounds={'x': 0, 'y': 0, 'width': 800, 'height': 600}
            )
            
            # Record various actions
            test_actions = [
                ActionEvent(
                    timestamp=time.time(),
                    action_type='click',
                    coordinates=(100, 200),
                    context=context
                ),
                ActionEvent(
                    timestamp=time.time() + 1,
                    action_type='type',
                    text_input='Hello World',
                    context=context
                ),
                ActionEvent(
                    timestamp=time.time() + 2,
                    action_type='key',
                    key_combination='Ctrl+S',
                    context=context
                )
            ]
            
            # Record actions
            for action in test_actions:
                analyzer.record_action(action)
            
            # Check recording
            recorded_count = len(analyzer.action_history)
            stats = analyzer.get_analysis_stats()
            total_actions = stats.get('total_actions', 0)
            
            return {
                'success': recorded_count == len(test_actions),
                'actions_recorded': recorded_count,
                'expected_actions': len(test_actions),
                'stats_updated': total_actions == len(test_actions)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Action recording failed: {e}'
            }
    
    def test_repetitive_pattern_detection(self) -> Dict[str, Any]:
        """Test detection of repetitive task patterns."""
        try:
            analyzer = PatternAnalyzer(max_history=200)
            
            # Create context
            context = ApplicationContext(
                app_name="TextEditor",
                process_name="editor",
                window_title="Document.txt",
                context_type=ContextType.TEXT_EDITOR,
                ui_state=UIState.IDLE,
                window_bounds={'x': 0, 'y': 0, 'width': 800, 'height': 600}
            )
            
            # Create repetitive pattern: Click -> Type -> Save
            base_time = time.time()
            repetitions = 5
            
            for i in range(repetitions):
                # Click action
                analyzer.record_action(ActionEvent(
                    timestamp=base_time + i * 10,
                    action_type='click',
                    coordinates=(300, 400),
                    context=context,
                    duration=0.1
                ))
                
                # Type action
                analyzer.record_action(ActionEvent(
                    timestamp=base_time + i * 10 + 1,
                    action_type='type',
                    text_input=f'Line {i+1}',
                    context=context,
                    duration=2.0
                ))
                
                # Save action
                analyzer.record_action(ActionEvent(
                    timestamp=base_time + i * 10 + 3,
                    action_type='key',
                    key_combination='Ctrl+S',
                    context=context,
                    duration=0.2
                ))
            
            # Run pattern analysis
            detected_patterns = analyzer.analyze_patterns()
            
            # Check for repetitive patterns
            repetitive_patterns = [p for p in detected_patterns 
                                 if p.pattern_type == PatternType.REPETITIVE_TASK]
            
            return {
                'success': len(repetitive_patterns) > 0,
                'total_patterns': len(detected_patterns),
                'repetitive_patterns': len(repetitive_patterns),
                'actions_generated': repetitions * 3,
                'patterns_details': [
                    {
                        'type': p.pattern_type.value,
                        'frequency': p.frequency,
                        'confidence': p.confidence,
                        'automation_potential': p.automation_potential
                    } for p in repetitive_patterns[:3]
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Repetitive pattern detection failed: {e}'
            }
    
    def test_workflow_pattern_detection(self) -> Dict[str, Any]:
        """Test workflow sequence pattern detection."""
        try:
            analyzer = PatternAnalyzer(max_history=300)
            
            # Create different contexts for workflow
            editor_context = ApplicationContext(
                app_name="VSCode", process_name="code", window_title="main.py",
                context_type=ContextType.DEVELOPMENT_IDE, ui_state=UIState.IDLE,
                window_bounds={'x': 0, 'y': 0, 'width': 1000, 'height': 800}
            )
            
            browser_context = ApplicationContext(
                app_name="Chrome", process_name="chrome", window_title="Documentation",
                context_type=ContextType.WEB_BROWSER, ui_state=UIState.IDLE,
                window_bounds={'x': 0, 'y': 0, 'width': 800, 'height': 600}
            )
            
            terminal_context = ApplicationContext(
                app_name="Terminal", process_name="terminal", window_title="bash",
                context_type=ContextType.TERMINAL, ui_state=UIState.IDLE,
                window_bounds={'x': 0, 'y': 0, 'width': 600, 'height': 400}
            )
            
            # Simulate workflow: Code -> Research -> Test (repeated twice)
            base_time = time.time()
            
            for iteration in range(2):
                offset = iteration * 60  # 1 minute apart
                
                # Coding phase
                for i in range(5):
                    analyzer.record_action(ActionEvent(
                        timestamp=base_time + offset + i * 2,
                        action_type='type',
                        text_input=f'code line {i}',
                        context=editor_context,
                        duration=1.5
                    ))
                
                # Research phase  
                for i in range(3):
                    analyzer.record_action(ActionEvent(
                        timestamp=base_time + offset + 15 + i * 3,
                        action_type='click',
                        coordinates=(400, 300 + i * 50),
                        context=browser_context,
                        duration=0.2
                    ))
                
                # Testing phase
                for i in range(2):
                    analyzer.record_action(ActionEvent(
                        timestamp=base_time + offset + 30 + i * 5,
                        action_type='type',
                        text_input=f'python test{i}.py',
                        context=terminal_context,
                        duration=3.0
                    ))
            
            # Analyze patterns
            detected_patterns = analyzer.analyze_patterns()
            workflow_patterns = [p for p in detected_patterns 
                               if p.pattern_type == PatternType.WORKFLOW_SEQUENCE]
            
            return {
                'success': len(workflow_patterns) > 0,
                'workflow_patterns': len(workflow_patterns),
                'total_patterns': len(detected_patterns),
                'contexts_involved': 3,
                'workflow_details': [
                    {
                        'frequency': p.frequency,
                        'duration_avg': p.duration_avg,
                        'contexts': len(p.contexts),
                        'involves_context_switch': p.involves_context_switch
                    } for p in workflow_patterns[:2]
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Workflow pattern detection failed: {e}'
            }
    
    def test_context_switching_patterns(self) -> Dict[str, Any]:
        """Test context switching pattern detection."""
        try:
            analyzer = PatternAnalyzer(max_history=150)
            
            # Create contexts
            contexts = [
                ApplicationContext("App1", "app1", "Window 1", ContextType.TEXT_EDITOR, UIState.IDLE, {}),
                ApplicationContext("App2", "app2", "Window 2", ContextType.WEB_BROWSER, UIState.IDLE, {}),
                ApplicationContext("App3", "app3", "Window 3", ContextType.TERMINAL, UIState.IDLE, {})
            ]
            
            # Simulate context switching pattern: App1 -> App2 -> App3 -> repeat
            base_time = time.time()
            
            # Repeat the switching pattern 4 times
            for cycle in range(4):
                for i, context in enumerate(contexts):
                    # Create context change event
                    from mkd_v2.intelligence.context_detector import ContextChangeEvent
                    
                    prev_context = contexts[(i-1) % len(contexts)] if i > 0 or cycle > 0 else None
                    
                    event = ContextChangeEvent(
                        timestamp=base_time + cycle * 15 + i * 5,
                        previous_context=prev_context,
                        new_context=context,
                        change_type="app_switch",
                        significance=0.8
                    )
                    
                    analyzer.record_context_change(event)
                    
                    # Add some actions in this context
                    analyzer.record_action(ActionEvent(
                        timestamp=base_time + cycle * 15 + i * 5 + 1,
                        action_type='click',
                        coordinates=(200, 300),
                        context=context
                    ))
            
            # Analyze patterns
            detected_patterns = analyzer.analyze_patterns()
            context_patterns = [p for p in detected_patterns 
                              if p.pattern_type == PatternType.CONTEXT_SWITCHING]
            
            return {
                'success': len(context_patterns) > 0,
                'context_switching_patterns': len(context_patterns),
                'total_context_changes': 4 * 3,  # 4 cycles * 3 switches
                'pattern_details': [
                    {
                        'frequency': p.frequency,
                        'involves_context_switch': p.involves_context_switch,
                        'efficiency_score': p.efficiency_score
                    } for p in context_patterns[:2]
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Context switching pattern test failed: {e}'
            }
    
    def test_time_based_patterns(self) -> Dict[str, Any]:
        """Test time-based pattern detection."""
        try:
            analyzer = PatternAnalyzer(max_history=200)
            
            # Create context
            context = ApplicationContext(
                "EmailApp", "email", "Inbox", ContextType.COMMUNICATION, UIState.IDLE, {}
            )
            
            # Simulate time-based pattern: Email checking at specific hour
            import datetime
            current_hour = datetime.datetime.now().hour
            base_time = time.time()
            
            # Generate actions at the same hour over multiple days (simulated)
            for day in range(7):  # 7 days
                for action_num in range(5):  # 5 actions per day at this hour
                    # Simulate different days by using different base times
                    action_time = base_time + day * 3600 * 24 + action_num * 60
                    
                    analyzer.record_action(ActionEvent(
                        timestamp=action_time,
                        action_type='click',
                        coordinates=(150, 100 + action_num * 30),
                        context=context,
                        duration=0.5
                    ))
            
            # Analyze patterns
            detected_patterns = analyzer.analyze_patterns()
            time_patterns = [p for p in detected_patterns 
                           if p.pattern_type == PatternType.TIME_BASED]
            
            return {
                'success': len(time_patterns) > 0,
                'time_based_patterns': len(time_patterns),
                'actions_generated': 7 * 5,
                'current_hour': current_hour,
                'pattern_details': [
                    {
                        'frequency': p.frequency,
                        'automation_potential': p.automation_potential,
                        'metadata': p.metadata
                    } for p in time_patterns[:2]
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Time-based pattern test failed: {e}'
            }
    
    def test_pattern_similarity(self) -> Dict[str, Any]:
        """Test pattern similarity calculation methods."""
        try:
            analyzer = PatternAnalyzer()
            
            # Create test actions
            context = ApplicationContext(
                "TestApp", "test", "Test", ContextType.TEXT_EDITOR, UIState.IDLE, {}
            )
            
            action1 = ActionEvent(time.time(), 'click', coordinates=(100, 200), context=context)
            action2 = ActionEvent(time.time(), 'click', coordinates=(105, 205), context=context)  # Similar
            action3 = ActionEvent(time.time(), 'type', text_input='hello', context=context)  # Different
            
            # Test action similarity
            similar_actions = analyzer._are_actions_similar(action1, action2)
            different_actions = analyzer._are_actions_similar(action1, action3)
            
            # Test sequence similarity
            seq1 = [action1, action2]
            seq2 = [action1, action2]  # Identical
            seq3 = [action1, action3]  # Different
            
            identical_similarity = analyzer._calculate_sequence_similarity(seq1, seq2)
            different_similarity = analyzer._calculate_sequence_similarity(seq1, seq3)
            
            return {
                'success': similar_actions and not different_actions,
                'similar_actions_detected': similar_actions,
                'different_actions_detected': not different_actions,
                'identical_sequence_similarity': identical_similarity,
                'different_sequence_similarity': different_similarity,
                'similarity_calculation_works': identical_similarity > different_similarity
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Pattern similarity test failed: {e}'
            }
    
    def test_automation_potential(self) -> Dict[str, Any]:
        """Test automation potential calculation."""
        try:
            analyzer = PatternAnalyzer()
            
            # Create context
            context = ApplicationContext(
                "Calculator", "calc", "Calculator", ContextType.SYSTEM_UTILITY, UIState.IDLE, {}
            )
            
            # Create highly automatable pattern (repetitive, simple actions)
            high_potential_actions = []
            for i in range(10):  # Many repetitions
                high_potential_actions.append(ActionEvent(
                    timestamp=time.time() + i,
                    action_type='click',  # Simple action
                    coordinates=(100, 200),  # Same location
                    context=context,  # Same context
                    duration=0.1  # Fast execution
                ))
            
            # Create low automation potential pattern (complex, varied actions)
            low_potential_actions = []
            contexts = [
                ApplicationContext(f"App{i}", f"app{i}", f"Win{i}", 
                                ContextType.UNKNOWN, UIState.UNKNOWN, {})
                for i in range(5)
            ]
            
            for i in range(5):  # Few repetitions
                low_potential_actions.append(ActionEvent(
                    timestamp=time.time() + i * 10,
                    action_type='complex_action',  # Complex action
                    coordinates=(i * 100, i * 100),  # Different locations
                    context=contexts[i],  # Different contexts
                    duration=5.0  # Slow execution
                ))
            
            # Calculate automation potential
            high_potential = analyzer._calculate_automation_potential(high_potential_actions)
            low_potential = analyzer._calculate_automation_potential(low_potential_actions)
            empty_potential = analyzer._calculate_automation_potential([])
            
            return {
                'success': high_potential > low_potential,
                'high_automation_potential': high_potential,
                'low_automation_potential': low_potential,
                'empty_automation_potential': empty_potential,
                'potential_difference': high_potential - low_potential,
                'calculation_reasonable': 0 <= high_potential <= 1 and 0 <= low_potential <= 1
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Automation potential test failed: {e}'
            }
    
    def test_pattern_export(self) -> Dict[str, Any]:
        """Test pattern export and data persistence."""
        try:
            analyzer = PatternAnalyzer(max_history=100)
            
            # Generate some patterns
            context = ApplicationContext(
                "TestApp", "test", "Test", ContextType.TEXT_EDITOR, UIState.IDLE, {}
            )
            
            # Record actions to generate patterns
            for i in range(20):
                analyzer.record_action(ActionEvent(
                    timestamp=time.time() + i,
                    action_type='click',
                    coordinates=(100 + i % 5, 200),
                    context=context
                ))
            
            # Analyze to create patterns
            patterns = analyzer.analyze_patterns()
            
            # Export patterns
            exported_data = analyzer.export_patterns()
            
            # Validate export structure
            has_patterns = 'patterns' in exported_data
            has_stats = 'stats' in exported_data
            has_timestamp = 'exported_at' in exported_data
            
            # Check export content
            exported_patterns = exported_data.get('patterns', {})
            pattern_count = len(exported_patterns)
            
            # Validate pattern data structure
            valid_pattern_structure = True
            if exported_patterns:
                first_pattern = next(iter(exported_patterns.values()))
                required_fields = ['pattern_id', 'pattern_type', 'confidence', 'frequency']
                valid_pattern_structure = all(field in first_pattern for field in required_fields)
            
            return {
                'success': has_patterns and has_stats and has_timestamp,
                'export_structure_valid': has_patterns and has_stats and has_timestamp,
                'exported_pattern_count': pattern_count,
                'patterns_detected': len(patterns),
                'valid_pattern_structure': valid_pattern_structure,
                'export_data_keys': list(exported_data.keys())
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Pattern export test failed: {e}'
            }
    
    def test_performance_load(self) -> Dict[str, Any]:
        """Test performance under load with many actions."""
        try:
            analyzer = PatternAnalyzer(max_history=1000)
            
            # Create context
            context = ApplicationContext(
                "PerfTest", "perftest", "Performance Test", 
                ContextType.TEXT_EDITOR, UIState.IDLE, {}
            )
            
            # Generate large number of actions
            action_count = 500
            start_time = time.time()
            
            for i in range(action_count):
                analyzer.record_action(ActionEvent(
                    timestamp=time.time() + i * 0.01,  # 10ms apart
                    action_type='click' if i % 2 == 0 else 'type',
                    coordinates=(100 + i % 50, 200 + i % 30) if i % 2 == 0 else None,
                    text_input=f'text{i}' if i % 2 == 1 else None,
                    context=context,
                    duration=0.1
                ))
            
            recording_time = time.time() - start_time
            
            # Test pattern analysis performance
            analysis_start = time.time()
            patterns = analyzer.analyze_patterns()
            analysis_time = time.time() - analysis_start
            
            # Get final stats
            stats = analyzer.get_analysis_stats()
            
            # Performance thresholds
            recording_acceptable = recording_time < 5.0  # 5 seconds
            analysis_acceptable = analysis_time < 10.0   # 10 seconds
            
            return {
                'success': recording_acceptable and analysis_acceptable,
                'actions_generated': action_count,
                'recording_time': recording_time,
                'analysis_time': analysis_time,
                'patterns_detected': len(patterns),
                'recording_performance_acceptable': recording_acceptable,
                'analysis_performance_acceptable': analysis_acceptable,
                'final_stats': stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Performance load test failed: {e}'
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
                if 'Pattern Detection' in test_name:
                    report['recommendations'].append(
                        "Verify pattern detection algorithms and thresholds"
                    )
                elif 'Performance' in test_name:
                    report['recommendations'].append(
                        "Consider optimizing pattern analysis algorithms for large datasets"
                    )
                elif 'Similarity' in test_name:
                    report['recommendations'].append(
                        "Review similarity calculation methods and accuracy"
                    )
        
        return report
    
    def cleanup(self):
        """Clean up test resources."""
        if self.pattern_analyzer:
            self.pattern_analyzer.cleanup()


def main():
    """Run pattern analysis tests."""
    tester = PatternAnalyzerTester()
    
    try:
        report = tester.run_all_tests()
        
        # Save detailed report
        log_dir = Path(__file__).parent / "logs"
        report_file = log_dir / "pattern_analysis_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*60)
        print("🔍 PATTERN ANALYSIS TEST SUMMARY")
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