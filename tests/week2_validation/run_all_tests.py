#!/usr/bin/env python3
"""
Week 2 Validation Test Runner

Comprehensive test runner for all Week 2 MKD Automation Platform features.
Runs all test suites and generates consolidated reports.
"""

import sys
import json
import time
import subprocess
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Configure paths
TESTS_DIR = Path(__file__).parent
LOG_DIR = TESTS_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Test modules
TEST_MODULES = [
    ("Chrome Integration", "test_chrome_integration.py"),
    ("Input Capture", "test_input_capture.py"),
    ("Visual Overlays", "test_visual_overlays.py"), 
    ("UI Automation", "test_ui_automation.py"),
    ("Playback Engine", "test_playback_engine.py")
]

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "master_test_runner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Week2TestRunner:
    """Master test runner for Week 2 validation."""
    
    def __init__(self):
        self.start_time = None
        self.test_results = []
        self.consolidated_report = {}
        
    def run_all_tests(self, skip_visual: bool = False, quick_mode: bool = False) -> Dict[str, Any]:
        """Run all Week 2 validation tests."""
        self.start_time = time.time()
        
        print("🚀 MKD AUTOMATION PLATFORM v2.0 - WEEK 2 VALIDATION")
        print("=" * 70)
        print(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Log Directory: {LOG_DIR}")
        print()
        
        # Run each test suite
        for test_name, test_file in TEST_MODULES:
            # Skip visual tests in headless environments
            if skip_visual and "visual" in test_file.lower():
                logger.info(f"⏭️  Skipping {test_name} (visual tests disabled)")
                continue
                
            self._run_test_suite(test_name, test_file, quick_mode)
        
        # Generate consolidated report
        self._generate_consolidated_report()
        
        # Show summary
        self._show_summary()
        
        return self.consolidated_report
    
    def _run_test_suite(self, test_name: str, test_file: str, quick_mode: bool = False):
        """Run individual test suite."""
        print(f"📋 Running {test_name} Tests...")
        print("-" * 50)
        
        test_path = TESTS_DIR / test_file
        
        if not test_path.exists():
            logger.error(f"Test file not found: {test_file}")
            self.test_results.append({
                'name': test_name,
                'status': 'ERROR',
                'error': f'Test file not found: {test_file}',
                'execution_time': 0
            })
            return
        
        start_time = time.time()
        
        try:
            # Set environment variables for test execution
            env = {
                'PYTHONPATH': str(Path(__file__).parent.parent.parent / "src"),
                'MKD_QUICK_MODE': '1' if quick_mode else '0'
            }
            
            # Run test
            result = subprocess.run([
                sys.executable, str(test_path)
            ], capture_output=True, text=True, timeout=300, env={**dict(os.environ), **env})
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                status = 'PASS'
                print(f"✅ {test_name}: PASSED ({execution_time:.1f}s)")
            else:
                status = 'FAIL'
                print(f"❌ {test_name}: FAILED ({execution_time:.1f}s)")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
            
            # Parse test output for details
            test_details = self._parse_test_output(result.stdout, result.stderr)
            
            self.test_results.append({
                'name': test_name,
                'status': status,
                'execution_time': execution_time,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'details': test_details
            })
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f"⏱️  {test_name}: TIMEOUT ({execution_time:.1f}s)")
            self.test_results.append({
                'name': test_name,
                'status': 'TIMEOUT',
                'execution_time': execution_time,
                'error': 'Test execution timed out'
            })
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"🚨 {test_name}: ERROR ({execution_time:.1f}s) - {e}")
            self.test_results.append({
                'name': test_name,
                'status': 'ERROR',
                'execution_time': execution_time,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        
        print()  # Add spacing between tests
    
    def _parse_test_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse test output for key information."""
        details = {
            'has_summary': False,
            'success_rate': None,
            'total_tests': None,
            'passed_tests': None
        }
        
        try:
            # Look for success rate in output
            lines = stdout.split('\n')
            for line in lines:
                if 'Success Rate:' in line:
                    details['has_summary'] = True
                    # Extract percentage
                    parts = line.split('%')
                    if parts:
                        try:
                            details['success_rate'] = float(parts[0].split()[-1])
                        except:
                            pass
                elif 'Total Tests:' in line:
                    try:
                        details['total_tests'] = int(line.split(':')[-1].strip())
                    except:
                        pass
                elif 'Passed:' in line and '✅' in line:
                    try:
                        details['passed_tests'] = int(line.split(':')[1].split('✅')[0].strip())
                    except:
                        pass
        except:
            pass
        
        return details
    
    def _generate_consolidated_report(self):
        """Generate consolidated test report."""
        total_execution_time = time.time() - self.start_time
        
        # Calculate overall statistics
        total_suites = len(self.test_results)
        passed_suites = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_suites = len([r for r in self.test_results if r['status'] == 'FAIL'])
        error_suites = len([r for r in self.test_results if r['status'] == 'ERROR'])
        timeout_suites = len([r for r in self.test_results if r['status'] == 'TIMEOUT'])
        
        # Collect individual test statistics
        individual_test_stats = []
        for result in self.test_results:
            if result.get('details', {}).get('success_rate') is not None:
                individual_test_stats.append({
                    'suite': result['name'],
                    'success_rate': result['details']['success_rate'],
                    'total_tests': result['details'].get('total_tests', 0),
                    'passed_tests': result['details'].get('passed_tests', 0)
                })
        
        # Calculate overall success rate across all individual tests
        total_individual_tests = sum(stat['total_tests'] for stat in individual_test_stats if stat['total_tests'])
        total_passed_tests = sum(stat['passed_tests'] for stat in individual_test_stats if stat['passed_tests'])
        overall_success_rate = (total_passed_tests / total_individual_tests * 100) if total_individual_tests > 0 else 0
        
        self.consolidated_report = {
            'metadata': {
                'week': 2,
                'platform': 'MKD Automation Platform v2.0',
                'test_run_time': datetime.now().isoformat(),
                'total_execution_time': total_execution_time,
                'log_directory': str(LOG_DIR)
            },
            'summary': {
                'total_test_suites': total_suites,
                'passed_suites': passed_suites,
                'failed_suites': failed_suites,
                'error_suites': error_suites,
                'timeout_suites': timeout_suites,
                'suite_success_rate': (passed_suites / total_suites * 100) if total_suites > 0 else 0,
                'overall_success_rate': overall_success_rate,
                'total_individual_tests': total_individual_tests,
                'total_passed_individual_tests': total_passed_tests
            },
            'test_suites': self.test_results,
            'individual_test_statistics': individual_test_stats,
            'recommendations': self._generate_recommendations()
        }
        
        # Save consolidated report
        report_file = LOG_DIR / f"week2_consolidated_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.consolidated_report, f, indent=2, default=str)
        
        # Also save latest report
        latest_report = LOG_DIR / "week2_latest_report.json"
        with open(latest_report, 'w') as f:
            json.dump(self.consolidated_report, f, indent=2, default=str)
        
        logger.info(f"Consolidated report saved to: {report_file}")
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if r['status'] in ['FAIL', 'ERROR', 'TIMEOUT']]
        
        for result in failed_tests:
            test_name = result['name']
            
            if 'Chrome Integration' in test_name:
                recommendations.append(
                    "📋 Chrome Integration Issues: Run 'python install_native_host.py' and restart Chrome"
                )
            
            elif 'Input Capture' in test_name:
                recommendations.append(
                    "🖱️  Input Capture Issues: Grant Accessibility permissions (macOS) or install pynput"
                )
            
            elif 'Visual Overlays' in test_name:
                recommendations.append(
                    "🎨 Visual Issues: Ensure GUI access and install tkinter dependencies"
                )
            
            elif 'UI Automation' in test_name:
                recommendations.append(
                    "🤖 Automation Issues: Check system permissions and install cv2/tesseract for better detection"
                )
            
            elif 'Playback Engine' in test_name:
                recommendations.append(
                    "⏯️  Playback Issues: Verify platform initialization and action execution permissions"
                )
        
        # Add general recommendations
        if len(failed_tests) > 2:
            recommendations.append(
                "🔧 Multiple test failures detected. Check system dependencies and permissions"
            )
        
        if not recommendations:
            recommendations.append("✨ All tests passed! Week 2 implementation is ready for production")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _show_summary(self):
        """Display test execution summary."""
        print("\n" + "=" * 70)
        print("📊 WEEK 2 VALIDATION SUMMARY")
        print("=" * 70)
        
        summary = self.consolidated_report['summary']
        
        print(f"Total Test Suites: {summary['total_test_suites']}")
        print(f"✅ Passed: {summary['passed_suites']}")
        print(f"❌ Failed: {summary['failed_suites']}")
        print(f"🚨 Errors: {summary['error_suites']}")
        print(f"⏱️  Timeouts: {summary['timeout_suites']}")
        print()
        print(f"Suite Success Rate: {summary['suite_success_rate']:.1f}%")
        print(f"Individual Test Success Rate: {summary['overall_success_rate']:.1f}%")
        print(f"Total Execution Time: {self.consolidated_report['metadata']['total_execution_time']:.1f}s")
        
        print(f"\n📈 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = {
                'PASS': '✅',
                'FAIL': '❌', 
                'ERROR': '🚨',
                'TIMEOUT': '⏱️'
            }.get(result['status'], '❓')
            
            print(f"  {status_icon} {result['name']}: {result['status']} ({result['execution_time']:.1f}s)")
            
            # Show individual test details if available
            details = result.get('details', {})
            if details.get('success_rate') is not None:
                print(f"     └─ {details.get('passed_tests', 0)}/{details.get('total_tests', 0)} tests passed ({details['success_rate']:.1f}%)")
        
        print(f"\n🔧 RECOMMENDATIONS:")
        for rec in self.consolidated_report['recommendations']:
            print(f"  • {rec}")
        
        print(f"\n📄 Reports saved to: {LOG_DIR}")
        print(f"📋 Latest report: {LOG_DIR / 'week2_latest_report.json'}")
        
        # Overall assessment
        overall_success = summary['suite_success_rate'] >= 80 and summary['overall_success_rate'] >= 70
        if overall_success:
            print(f"\n🎉 WEEK 2 VALIDATION: SUCCESS")
            print("   Platform is ready for Week 3 development!")
        else:
            print(f"\n⚠️  WEEK 2 VALIDATION: NEEDS ATTENTION")
            print("   Please address recommendations before proceeding to Week 3")


def main():
    """Main test runner entry point."""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Week 2 MKD Automation Platform Validation')
    parser.add_argument('--skip-visual', action='store_true',
                       help='Skip visual overlay tests (for headless environments)')
    parser.add_argument('--quick', action='store_true',
                       help='Run tests in quick mode (reduced iterations)')
    parser.add_argument('--test', choices=[m[1] for m in TEST_MODULES],
                       help='Run specific test module only')
    
    args = parser.parse_args()
    
    runner = Week2TestRunner()
    
    if args.test:
        # Run specific test
        test_name = None
        for name, file in TEST_MODULES:
            if file == args.test:
                test_name = name
                break
        
        if test_name:
            runner._run_test_suite(test_name, args.test, args.quick)
            print(f"\n✅ Individual test completed: {test_name}")
        else:
            print(f"❌ Test not found: {args.test}")
            return 1
    else:
        # Run all tests
        report = runner.run_all_tests(skip_visual=args.skip_visual, quick_mode=args.quick)
        
        # Return appropriate exit code
        success_rate = report['summary']['suite_success_rate']
        return 0 if success_rate >= 80 else 1


if __name__ == "__main__":
    try:
        import os
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚡ Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n🚨 Test runner failed: {e}")
        sys.exit(1)