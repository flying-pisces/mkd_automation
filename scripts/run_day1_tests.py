#!/usr/bin/env python3
"""
Day 1 Test Runner for MKD Automation Platform v2.0
Executes all Day 1 priority tests and generates reports.
"""

import sys
import subprocess
import os
import time
import json
from pathlib import Path
from datetime import datetime


class Day1TestRunner:
    """Test runner for Day 1 implementation."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            'start_time': None,
            'end_time': None,
            'duration': None,
            'python_tests': {},
            'chrome_tests': {},
            'coverage': {},
            'summary': {}
        }
    
    def run_python_unit_tests(self):
        """Run Python unit tests with coverage."""
        print("🐍 Running Python Unit Tests...")
        print("-" * 50)
        
        # Run Day 1 priority tests specifically
        day1_test_files = [
            'tests/unit/core/test_message_broker.py',
            'tests/unit/platform/test_detector.py',
            'tests/unit/chrome_extension/test_messaging.py',
        ]
        
        cmd = [
            'python', '-m', 'pytest',
            *day1_test_files,
            '--cov=src/mkd_v2',
            '--cov-report=html:htmlcov',
            '--cov-report=xml:coverage.xml',
            '--cov-report=term-missing',
            '--cov-fail-under=80',  # Lower threshold for Day 1
            '-v',
            '--tb=short',
            '--json-report',
            '--json-report-file=test-results/python-results.json'
        ]
        
        try:
            # Create results directory
            os.makedirs('test-results', exist_ok=True)
            
            # Run tests
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            end_time = time.time()
            
            # Store results
            self.results['python_tests'] = {
                'returncode': result.returncode,
                'duration': end_time - start_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'passed': result.returncode == 0
            }
            
            # Parse coverage if available
            self.parse_python_coverage()
            
            print(f"Python tests completed in {end_time - start_time:.2f}s")
            print(f"Exit code: {result.returncode}")
            
            if result.returncode == 0:
                print("✅ Python tests PASSED")
            else:
                print("❌ Python tests FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running Python tests: {e}")
            self.results['python_tests'] = {
                'returncode': 1,
                'error': str(e),
                'passed': False
            }
            return False
    
    def run_chrome_extension_tests(self):
        """Run Chrome extension JavaScript tests."""
        print("\n🌐 Running Chrome Extension Tests...")
        print("-" * 50)
        
        # Check if npm is available
        try:
            subprocess.run(['npm', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ npm not found. Installing Node.js dependencies manually...")
            return False
        
        # Install dependencies if needed
        if not (self.project_root / 'node_modules').exists():
            print("📦 Installing npm dependencies...")
            install_result = subprocess.run(
                ['npm', 'install'], 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            if install_result.returncode != 0:
                print(f"❌ Failed to install dependencies: {install_result.stderr}")
                return False
        
        # Run Jest tests
        cmd = [
            'npm', 'test', '--',
            '--testMatch=**/chrome_extension/**/*.test.js',
            '--coverage',
            '--json',
            '--outputFile=test-results/chrome-results.json'
        ]
        
        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            end_time = time.time()
            
            # Store results
            self.results['chrome_tests'] = {
                'returncode': result.returncode,
                'duration': end_time - start_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'passed': result.returncode == 0
            }
            
            print(f"Chrome extension tests completed in {end_time - start_time:.2f}s")
            print(f"Exit code: {result.returncode}")
            
            if result.returncode == 0:
                print("✅ Chrome extension tests PASSED")
            else:
                print("❌ Chrome extension tests FAILED")
                if result.stdout:
                    print("STDOUT:", result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running Chrome extension tests: {e}")
            self.results['chrome_tests'] = {
                'returncode': 1,
                'error': str(e),
                'passed': False
            }
            return False
    
    def parse_python_coverage(self):
        """Parse Python coverage results."""
        coverage_xml = self.project_root / 'coverage.xml'
        if coverage_xml.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(coverage_xml)
                root = tree.getroot()
                
                # Extract overall coverage
                coverage_elem = root.find('.//coverage')
                if coverage_elem is not None:
                    line_rate = float(coverage_elem.get('line-rate', 0)) * 100
                    branch_rate = float(coverage_elem.get('branch-rate', 0)) * 100
                    
                    self.results['coverage']['python'] = {
                        'line_coverage': line_rate,
                        'branch_coverage': branch_rate
                    }
                    
            except Exception as e:
                print(f"Warning: Could not parse coverage data: {e}")
    
    def validate_day1_requirements(self):
        """Validate Day 1 specific requirements."""
        print("\n✅ Validating Day 1 Requirements...")
        print("-" * 50)
        
        requirements = {
            'test_infrastructure': self.check_test_infrastructure(),
            'unit_test_coverage': self.check_unit_test_coverage(),
            'chrome_extension_tests': self.check_chrome_extension_tests(),
            'documentation': self.check_documentation(),
            'ci_cd_setup': self.check_ci_cd_setup()
        }
        
        all_passed = all(requirements.values())
        
        print("Day 1 Requirements Validation:")
        for requirement, passed in requirements.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {requirement.replace('_', ' ').title()}: {status}")
        
        self.results['day1_validation'] = requirements
        return all_passed
    
    def check_test_infrastructure(self):
        """Check if test infrastructure is properly set up."""
        required_files = [
            'tests/conftest.py',
            'package.json',
            'tests/chrome_extension/setup.js',
            'pyproject.toml'
        ]
        
        return all((self.project_root / file).exists() for file in required_files)
    
    def check_unit_test_coverage(self):
        """Check if unit test coverage meets Day 1 targets."""
        coverage_data = self.results.get('coverage', {}).get('python', {})
        line_coverage = coverage_data.get('line_coverage', 0)
        
        # Day 1 target is 80% (lower than final 90% target)
        return line_coverage >= 80.0
    
    def check_chrome_extension_tests(self):
        """Check if Chrome extension tests are working."""
        return self.results.get('chrome_tests', {}).get('passed', False)
    
    def check_documentation(self):
        """Check if Day 1 documentation exists."""
        required_docs = [
            'docs/DAY1_TEST_PLAN.md',
            'docs/TEST_DEVELOPMENT_PLAN.md',
            'tests/chrome_extension/setup.js'
        ]
        
        return all((self.project_root / doc).exists() for doc in required_docs)
    
    def check_ci_cd_setup(self):
        """Check if CI/CD pipeline is set up."""
        github_workflow = self.project_root / '.github' / 'workflows'
        return github_workflow.exists() or (self.project_root / '.github').exists()
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n📊 Generating Day 1 Test Report...")
        print("=" * 60)
        
        # Calculate summary
        python_passed = self.results.get('python_tests', {}).get('passed', False)
        chrome_passed = self.results.get('chrome_tests', {}).get('passed', False)
        validation_passed = all(
            self.results.get('day1_validation', {}).values()
        )
        
        overall_success = python_passed and chrome_passed and validation_passed
        
        self.results['summary'] = {
            'overall_success': overall_success,
            'python_tests_passed': python_passed,
            'chrome_tests_passed': chrome_passed,
            'day1_validation_passed': validation_passed,
            'total_duration': self.results['duration']
        }
        
        # Print summary
        print(f"📈 Overall Result: {'✅ SUCCESS' if overall_success else '❌ FAILURE'}")
        print(f"🐍 Python Tests: {'✅ PASSED' if python_passed else '❌ FAILED'}")
        print(f"🌐 Chrome Tests: {'✅ PASSED' if chrome_passed else '❌ FAILED'}")
        print(f"✅ Day 1 Validation: {'✅ PASSED' if validation_passed else '❌ FAILED'}")
        print(f"⏱️  Total Duration: {self.results['duration']:.2f}s")
        
        # Coverage information
        python_coverage = self.results.get('coverage', {}).get('python', {})
        if python_coverage:
            line_cov = python_coverage.get('line_coverage', 0)
            print(f"📊 Line Coverage: {line_cov:.1f}%")
        
        # Save detailed results
        results_file = self.project_root / 'test-results' / 'day1-summary.json'
        os.makedirs(results_file.parent, exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        # Generate HTML report if possible
        self.generate_html_report()
        
        return overall_success
    
    def generate_html_report(self):
        """Generate HTML test report."""
        try:
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MKD Automation Day 1 Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .section {{ margin: 20px 0; padding: 10px; border: 1px solid #ddd; }}
        .summary {{ background-color: #f0f0f0; }}
    </style>
</head>
<body>
    <h1>MKD Automation Platform v2.0 - Day 1 Test Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="section summary">
        <h2>Summary</h2>
        <p>Overall Result: <span class="{'success' if self.results['summary']['overall_success'] else 'failure'}">
            {'SUCCESS' if self.results['summary']['overall_success'] else 'FAILURE'}
        </span></p>
        <p>Total Duration: {self.results['duration']:.2f} seconds</p>
    </div>
    
    <div class="section">
        <h2>Python Tests</h2>
        <p>Status: <span class="{'success' if self.results['summary']['python_tests_passed'] else 'failure'}">
            {'PASSED' if self.results['summary']['python_tests_passed'] else 'FAILED'}
        </span></p>
        <p>Duration: {self.results.get('python_tests', {}).get('duration', 0):.2f}s</p>
    </div>
    
    <div class="section">
        <h2>Chrome Extension Tests</h2>
        <p>Status: <span class="{'success' if self.results['summary']['chrome_tests_passed'] else 'failure'}">
            {'PASSED' if self.results['summary']['chrome_tests_passed'] else 'FAILED'}
        </span></p>
        <p>Duration: {self.results.get('chrome_tests', {}).get('duration', 0):.2f}s</p>
    </div>
    
    <div class="section">
        <h2>Coverage Information</h2>
        <p>Python Line Coverage: {self.results.get('coverage', {}).get('python', {}).get('line_coverage', 0):.1f}%</p>
    </div>
</body>
</html>
"""
            
            html_file = self.project_root / 'test-results' / 'day1-report.html'
            with open(html_file, 'w') as f:
                f.write(html_content)
            
            print(f"📊 HTML report saved to: {html_file}")
            
        except Exception as e:
            print(f"Warning: Could not generate HTML report: {e}")
    
    def run(self):
        """Run all Day 1 tests and validation."""
        print("🚀 Starting MKD Automation Day 1 Test Suite")
        print("=" * 60)
        
        self.results['start_time'] = datetime.now()
        start_time = time.time()
        
        # Run tests
        python_success = self.run_python_unit_tests()
        chrome_success = self.run_chrome_extension_tests()
        
        # Validate requirements
        validation_success = self.validate_day1_requirements()
        
        # Calculate duration
        end_time = time.time()
        self.results['end_time'] = datetime.now()
        self.results['duration'] = end_time - start_time
        
        # Generate report
        overall_success = self.generate_report()
        
        return overall_success


def main():
    """Main entry point."""
    runner = Day1TestRunner()
    success = runner.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()