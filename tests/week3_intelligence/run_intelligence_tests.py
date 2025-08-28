#!/usr/bin/env python3
"""
Week 3 Intelligence Test Runner

Master test runner for all Week 3 intelligence features including:
- Context Detection System
- Pattern Analysis Engine
- Smart Recording System
- Intelligent Automation Integration
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List

# Ensure proper Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import logging

# Configure logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "week3_intelligence_master.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Week3IntelligenceTestRunner:
    """Master test runner for Week 3 intelligence features."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {}
        self.overall_stats = {
            'total_suites': 0,
            'passed_suites': 0,
            'failed_suites': 0,
            'error_suites': 0,
            'total_individual_tests': 0,
            'passed_individual_tests': 0,
            'start_time': time.time(),
            'end_time': None
        }
    
    def run_all_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """Run all Week 3 intelligence test suites."""
        logger.info("🧠 Starting Week 3 Intelligence Test Suite")
        logger.info("=" * 70)
        
        # Define test suites in dependency order
        test_suites = [
            {
                'name': 'Context Detection',
                'module': 'test_context_detector',
                'description': 'Application context detection and UI state analysis'
            },
            {
                'name': 'Pattern Analysis',
                'module': 'test_pattern_analyzer', 
                'description': 'User behavior pattern detection and analysis'
            },
            {
                'name': 'Smart Recording',
                'module': 'test_smart_recorder',
                'description': 'Intelligent recording decision system'
            },
            {
                'name': 'Intelligent Automation',
                'module': 'test_intelligent_automation',
                'description': 'Integrated intelligent automation engine'
            }
        ]
        
        self.overall_stats['total_suites'] = len(test_suites)
        
        # Run each test suite
        for suite in test_suites:
            logger.info(f"\n🔍 Running {suite['name']} Tests")
            logger.info(f"📋 {suite['description']}")
            logger.info("-" * 60)
            
            try:
                result = self._run_test_suite(suite, verbose)
                self.results[suite['name']] = result
                
                if result['success']:
                    self.overall_stats['passed_suites'] += 1
                    logger.info(f"✅ {suite['name']}: PASSED")
                else:
                    self.overall_stats['failed_suites'] += 1  
                    logger.error(f"❌ {suite['name']}: FAILED")
                
                # Update individual test counts
                if 'summary' in result:
                    summary = result['summary']
                    self.overall_stats['total_individual_tests'] += summary.get('total_tests', 0)
                    self.overall_stats['passed_individual_tests'] += summary.get('passed', 0)
                
            except Exception as e:
                self.overall_stats['error_suites'] += 1
                self.results[suite['name']] = {
                    'success': False,
                    'error': str(e),
                    'module': suite['module']
                }
                logger.error(f"💥 {suite['name']}: ERROR - {e}")
        
        self.overall_stats['end_time'] = time.time()
        
        # Generate final report
        return self._generate_master_report()
    
    def _run_test_suite(self, suite: Dict[str, Any], verbose: bool) -> Dict[str, Any]:
        """Run a single test suite."""
        module_name = suite['module']
        test_file = self.test_dir / f"{module_name}.py"
        
        if not test_file.exists():
            raise FileNotFoundError(f"Test module not found: {test_file}")
        
        try:
            # Run test module as subprocess for isolation
            cmd = [sys.executable, str(test_file)]
            
            start_time = time.time()
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per suite
                cwd=str(self.test_dir)
            )
            execution_time = time.time() - start_time
            
            # Parse results
            suite_success = process.returncode == 0
            
            # Try to load detailed report if available
            report_file = self.test_dir / "logs" / f"{module_name.replace('test_', '')}_report.json"
            detailed_report = None
            
            if report_file.exists():
                try:
                    with open(report_file, 'r') as f:
                        detailed_report = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load detailed report for {module_name}: {e}")
            
            result = {
                'success': suite_success,
                'module': module_name,
                'execution_time': execution_time,
                'return_code': process.returncode,
                'stdout': process.stdout,
                'stderr': process.stderr,
            }
            
            # Add detailed report if available
            if detailed_report:
                result.update(detailed_report)
            
            # Display output if verbose
            if verbose and process.stdout:
                print(process.stdout)
            
            if process.stderr:
                logger.error(f"Errors in {module_name}:")
                logger.error(process.stderr)
            
            return result
            
        except subprocess.TimeoutExpired:
            logger.error(f"Test suite {module_name} timed out after 5 minutes")
            return {
                'success': False,
                'error': 'Test suite timed out',
                'module': module_name
            }
        except Exception as e:
            logger.error(f"Failed to run test suite {module_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'module': module_name
            }
    
    def _generate_master_report(self) -> Dict[str, Any]:
        """Generate comprehensive master report."""
        duration = self.overall_stats['end_time'] - self.overall_stats['start_time']
        
        # Calculate success rates
        suite_success_rate = (self.overall_stats['passed_suites'] / 
                            self.overall_stats['total_suites'] * 100) if self.overall_stats['total_suites'] > 0 else 0
        
        individual_success_rate = (self.overall_stats['passed_individual_tests'] / 
                                 self.overall_stats['total_individual_tests'] * 100) if self.overall_stats['total_individual_tests'] > 0 else 0
        
        # Collect recommendations
        all_recommendations = []
        for suite_name, result in self.results.items():
            if not result['success']:
                all_recommendations.append(f"Fix issues in {suite_name} test suite")
            
            # Add specific recommendations from detailed reports
            if 'recommendations' in result:
                for rec in result['recommendations']:
                    all_recommendations.append(f"{suite_name}: {rec}")
        
        # Create summary by feature
        feature_summary = {}
        for suite_name, result in self.results.items():
            feature_summary[suite_name] = {
                'status': 'PASS' if result['success'] else 'FAIL',
                'execution_time': result.get('execution_time', 0),
                'individual_tests': result.get('summary', {}).get('total_tests', 0),
                'individual_passed': result.get('summary', {}).get('passed', 0),
                'success_rate': result.get('summary', {}).get('success_rate', 0)
            }
        
        master_report = {
            'week3_intelligence_summary': {
                'overall_success': suite_success_rate >= 75,  # 75% suite success threshold
                'suite_success_rate': suite_success_rate,
                'individual_test_success_rate': individual_success_rate,
                'total_duration': duration,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.overall_stats['end_time']))
            },
            'suite_statistics': self.overall_stats,
            'feature_summary': feature_summary,
            'detailed_results': self.results,
            'recommendations': all_recommendations,
            'next_steps': self._generate_next_steps()
        }
        
        return master_report
    
    def _generate_next_steps(self) -> List[str]:
        """Generate next steps based on test results."""
        next_steps = []
        
        # Check overall status
        suite_success_rate = (self.overall_stats['passed_suites'] / 
                            self.overall_stats['total_suites'] * 100) if self.overall_stats['total_suites'] > 0 else 0
        
        if suite_success_rate >= 90:
            next_steps.append("✅ Week 3 intelligence system is ready for production integration")
            next_steps.append("🚀 Proceed to Week 3 Phase 2: Advanced Playback Features")
        elif suite_success_rate >= 75:
            next_steps.append("⚠️ Week 3 intelligence has good foundation but needs refinement")
            next_steps.append("🔧 Address failing tests before proceeding to next phase")
        else:
            next_steps.append("❌ Week 3 intelligence needs significant work")
            next_steps.append("🛠️ Focus on core intelligence components before advancing")
        
        # Feature-specific next steps
        failed_features = [name for name, result in self.results.items() if not result['success']]
        if failed_features:
            next_steps.append(f"🎯 Priority fixes needed: {', '.join(failed_features)}")
        
        return next_steps
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> Path:
        """Save master report to file."""
        if filename is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"week3_intelligence_report_{timestamp}.json"
        
        report_file = self.test_dir / "logs" / filename
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report_file
    
    def print_summary(self, report: Dict[str, Any]):
        """Print formatted test summary."""
        summary = report['week3_intelligence_summary']
        stats = report['suite_statistics']
        
        print("\n" + "=" * 70)
        print("🧠 WEEK 3 INTELLIGENCE TEST RESULTS")
        print("=" * 70)
        
        print(f"Overall Status: {'✅ SUCCESS' if summary['overall_success'] else '❌ NEEDS WORK'}")
        print(f"Duration: {summary['total_duration']:.1f} seconds")
        print(f"Completed: {summary['timestamp']}")
        print()
        
        print("📊 SUITE STATISTICS:")
        print(f"  Total Suites: {stats['total_suites']}")
        print(f"  Passed: {stats['passed_suites']} ✅")
        print(f"  Failed: {stats['failed_suites']} ❌") 
        print(f"  Errors: {stats['error_suites']} 💥")
        print(f"  Suite Success Rate: {summary['suite_success_rate']:.1f}%")
        print()
        
        print("🔍 INDIVIDUAL TEST STATISTICS:")
        print(f"  Total Individual Tests: {stats['total_individual_tests']}")
        print(f"  Passed Individual Tests: {stats['passed_individual_tests']}")
        print(f"  Individual Success Rate: {summary['individual_test_success_rate']:.1f}%")
        print()
        
        print("🎯 FEATURE BREAKDOWN:")
        for feature, details in report['feature_summary'].items():
            status_icon = "✅" if details['status'] == 'PASS' else "❌"
            print(f"  {status_icon} {feature}: {details['individual_passed']}/{details['individual_tests']} tests ({details['success_rate']:.1f}%)")
        print()
        
        if report['recommendations']:
            print("🔧 RECOMMENDATIONS:")
            for rec in report['recommendations'][:10]:  # Show first 10
                print(f"  • {rec}")
            if len(report['recommendations']) > 10:
                print(f"  ... and {len(report['recommendations']) - 10} more")
            print()
        
        print("📋 NEXT STEPS:")
        for step in report['next_steps']:
            print(f"  {step}")
        
        print("=" * 70)


def main():
    """Main test runner entry point."""
    # Parse command line arguments
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    quiet = '--quiet' in sys.argv or '-q' in sys.argv
    
    runner = Week3IntelligenceTestRunner()
    
    try:
        # Run all tests
        report = runner.run_all_tests(verbose=verbose and not quiet)
        
        # Save report
        report_file = runner.save_report(report)
        logger.info(f"📄 Master report saved to: {report_file}")
        
        # Print summary unless quiet
        if not quiet:
            runner.print_summary(report)
        
        # Return appropriate exit code
        overall_success = report['week3_intelligence_summary']['overall_success']
        return 0 if overall_success else 1
        
    except KeyboardInterrupt:
        logger.info("⚡ Testing interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"💥 Master test runner failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())