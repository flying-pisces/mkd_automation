"""
Test Logger System

Comprehensive test logging and reporting system for Week 3 integration tests.
Provides detailed logging, metrics collection, and test result analysis.
"""

import json
import time
import logging
import traceback
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from pathlib import Path
import os
import threading
from collections import defaultdict


class TestResult(Enum):
    """Test result status"""
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED" 
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"


class TestPriority(Enum):
    """Test priority levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class LogLevel(Enum):
    """Log severity levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class TestCase:
    """Individual test case information"""
    test_id: str
    name: str
    description: str
    category: str
    priority: TestPriority
    expected_result: str
    timeout: float = 30.0
    setup_required: bool = False
    teardown_required: bool = False
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class TestExecution:
    """Test execution result"""
    test_case: TestCase
    result: TestResult
    start_time: float
    end_time: float
    execution_time: float
    actual_result: Any = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)


@dataclass
class TestSuite:
    """Test suite information"""
    suite_id: str
    name: str
    description: str
    test_cases: List[TestCase]
    setup_function: Optional[Callable] = None
    teardown_function: Optional[Callable] = None
    parallel_execution: bool = False
    max_workers: int = 5


@dataclass
class TestRun:
    """Complete test run information"""
    run_id: str
    name: str
    start_time: float
    end_time: Optional[float] = None
    total_time: Optional[float] = None
    test_suites: List[TestSuite] = field(default_factory=list)
    executions: List[TestExecution] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)


class TestLogger:
    """Comprehensive test logging system"""
    
    def __init__(self, log_directory: str = "tests/week3_integration/logs"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize logging
        self.logger = logging.getLogger('week3_test_logger')
        self.logger.setLevel(logging.DEBUG)
        
        # Create formatters
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        self.simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Setup file handlers
        self._setup_file_handlers()
        
        # Test execution tracking
        self.current_run: Optional[TestRun] = None
        self.execution_history: List[TestRun] = []
        self.metrics_collector = TestMetricsCollector()
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Performance monitoring
        self.performance_tracker = PerformanceTracker()
        
        # Report generators
        self.report_generator = TestReportGenerator(self.log_directory)
    
    def _setup_file_handlers(self) -> None:
        """Setup file logging handlers"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Detailed log file
        detailed_log_file = self.log_directory / f"detailed_{timestamp}.log"
        detailed_handler = logging.FileHandler(detailed_log_file)
        detailed_handler.setLevel(logging.DEBUG)
        detailed_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(detailed_handler)
        
        # Summary log file
        summary_log_file = self.log_directory / f"summary_{timestamp}.log"
        summary_handler = logging.FileHandler(summary_log_file)
        summary_handler.setLevel(logging.INFO)
        summary_handler.setFormatter(self.simple_formatter)
        self.logger.addHandler(summary_handler)
        
        # Error log file
        error_log_file = self.log_directory / f"errors_{timestamp}.log"
        error_handler = logging.FileHandler(error_log_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(error_handler)
        
        # Console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.simple_formatter)
        self.logger.addHandler(console_handler)
    
    def start_test_run(self, run_name: str, environment: Dict[str, Any] = None, 
                      configuration: Dict[str, Any] = None) -> str:
        """Start a new test run"""
        with self.lock:
            run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.current_run = TestRun(
                run_id=run_id,
                name=run_name,
                start_time=time.time(),
                environment=environment or {},
                configuration=configuration or {}
            )
            
            self.logger.info(f"Started test run: {run_name} (ID: {run_id})")
            self.logger.info(f"Environment: {environment}")
            self.logger.info(f"Configuration: {configuration}")
            
            return run_id
    
    def add_test_suite(self, test_suite: TestSuite) -> None:
        """Add test suite to current run"""
        if not self.current_run:
            raise ValueError("No active test run. Call start_test_run() first.")
        
        with self.lock:
            self.current_run.test_suites.append(test_suite)
            self.logger.info(f"Added test suite: {test_suite.name} ({len(test_suite.test_cases)} test cases)")
    
    def log_test_start(self, test_case: TestCase) -> float:
        """Log test case start"""
        start_time = time.time()
        
        self.logger.info(f"Starting test: {test_case.test_id} - {test_case.name}")
        self.logger.debug(f"Test description: {test_case.description}")
        self.logger.debug(f"Test priority: {test_case.priority.value}")
        self.logger.debug(f"Expected result: {test_case.expected_result}")
        
        # Start performance tracking
        self.performance_tracker.start_test(test_case.test_id)
        
        return start_time
    
    def log_test_result(self, test_case: TestCase, result: TestResult, 
                       start_time: float, actual_result: Any = None,
                       error_message: str = None, performance_metrics: Dict[str, float] = None) -> None:
        """Log test case result"""
        if not self.current_run:
            raise ValueError("No active test run. Call start_test_run() first.")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Stop performance tracking
        perf_metrics = self.performance_tracker.stop_test(test_case.test_id)
        if performance_metrics:
            perf_metrics.update(performance_metrics)
        
        # Create execution record
        execution = TestExecution(
            test_case=test_case,
            result=result,
            start_time=start_time,
            end_time=end_time,
            execution_time=execution_time,
            actual_result=actual_result,
            error_message=error_message,
            performance_metrics=perf_metrics
        )
        
        # Add stack trace if error occurred
        if result in [TestResult.FAILED, TestResult.ERROR] and not execution.stack_trace:
            execution.stack_trace = traceback.format_exc()
        
        with self.lock:
            self.current_run.executions.append(execution)
        
        # Log result
        log_level = logging.INFO if result == TestResult.PASSED else logging.ERROR
        self.logger.log(log_level, 
                       f"Test {test_case.test_id}: {result.value} ({execution_time:.3f}s)")
        
        if error_message:
            self.logger.error(f"Error: {error_message}")
        
        if actual_result is not None:
            self.logger.debug(f"Actual result: {actual_result}")
        
        # Collect metrics
        self.metrics_collector.record_execution(execution)
    
    def log_test_step(self, test_id: str, step_name: str, step_result: bool, 
                     details: str = None, performance_data: Dict[str, float] = None) -> None:
        """Log individual test step"""
        status = "✓" if step_result else "✗"
        self.logger.info(f"  {status} {step_name}")
        
        if details:
            self.logger.debug(f"    Details: {details}")
        
        if performance_data:
            for metric, value in performance_data.items():
                self.logger.debug(f"    {metric}: {value}")
    
    def log_performance_metric(self, test_id: str, metric_name: str, value: float, unit: str = "") -> None:
        """Log performance metric"""
        self.logger.debug(f"Performance [{test_id}] {metric_name}: {value} {unit}")
        
        # Store in current execution if available
        if self.current_run and self.current_run.executions:
            current_execution = self.current_run.executions[-1]
            if current_execution.test_case.test_id == test_id:
                current_execution.performance_metrics[metric_name] = value
    
    def log_resource_usage(self, test_id: str, cpu_usage: float, memory_usage: float, 
                          disk_io: float = 0, network_io: float = 0) -> None:
        """Log resource usage metrics"""
        self.logger.debug(f"Resources [{test_id}] CPU: {cpu_usage:.1f}%, Memory: {memory_usage:.1f}MB, "
                         f"Disk: {disk_io:.1f}MB/s, Network: {network_io:.1f}KB/s")
        
        resource_data = {
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'disk_io': disk_io,
            'network_io': network_io
        }
        
        # Store in current execution
        if self.current_run and self.current_run.executions:
            current_execution = self.current_run.executions[-1]
            if current_execution.test_case.test_id == test_id:
                current_execution.resource_usage.update(resource_data)
    
    def log_screenshot(self, test_id: str, screenshot_path: str, description: str = "") -> None:
        """Log screenshot capture"""
        self.logger.info(f"Screenshot captured [{test_id}]: {screenshot_path}")
        if description:
            self.logger.debug(f"Screenshot description: {description}")
        
        # Add to current execution
        if self.current_run and self.current_run.executions:
            current_execution = self.current_run.executions[-1]
            if current_execution.test_case.test_id == test_id:
                current_execution.screenshots.append(screenshot_path)
    
    def log_artifact(self, test_id: str, artifact_path: str, artifact_type: str = "file") -> None:
        """Log test artifact"""
        self.logger.debug(f"Test artifact [{test_id}] ({artifact_type}): {artifact_path}")
        
        # Add to current execution
        if self.current_run and self.current_run.executions:
            current_execution = self.current_run.executions[-1]
            if current_execution.test_case.test_id == test_id:
                current_execution.artifacts.append(artifact_path)
    
    def end_test_run(self) -> TestRun:
        """End current test run and generate summary"""
        if not self.current_run:
            raise ValueError("No active test run to end.")
        
        with self.lock:
            self.current_run.end_time = time.time()
            self.current_run.total_time = self.current_run.end_time - self.current_run.start_time
            
            # Generate summary
            self.current_run.summary = self._generate_run_summary(self.current_run)
            
            # Add to history
            self.execution_history.append(self.current_run)
            
            # Generate reports
            self.report_generator.generate_reports(self.current_run)
            
            # Log summary
            self._log_run_summary(self.current_run)
            
            completed_run = self.current_run
            self.current_run = None
            
            return completed_run
    
    def _generate_run_summary(self, test_run: TestRun) -> Dict[str, Any]:
        """Generate test run summary"""
        executions = test_run.executions
        
        # Count results
        result_counts = defaultdict(int)
        for execution in executions:
            result_counts[execution.result.value] += 1
        
        total_tests = len(executions)
        passed_tests = result_counts[TestResult.PASSED.value]
        failed_tests = result_counts[TestResult.FAILED.value]
        error_tests = result_counts[TestResult.ERROR.value]
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Performance metrics
        if executions:
            avg_execution_time = sum(e.execution_time for e in executions) / len(executions)
            min_execution_time = min(e.execution_time for e in executions)
            max_execution_time = max(e.execution_time for e in executions)
        else:
            avg_execution_time = min_execution_time = max_execution_time = 0
        
        # Priority breakdown
        priority_breakdown = defaultdict(lambda: {'total': 0, 'passed': 0})
        for execution in executions:
            priority = execution.test_case.priority.value
            priority_breakdown[priority]['total'] += 1
            if execution.result == TestResult.PASSED:
                priority_breakdown[priority]['passed'] += 1
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'error_tests': error_tests,
            'skipped_tests': result_counts[TestResult.SKIPPED.value],
            'timeout_tests': result_counts[TestResult.TIMEOUT.value],
            'success_rate': success_rate,
            'total_execution_time': test_run.total_time,
            'average_test_time': avg_execution_time,
            'min_test_time': min_execution_time,
            'max_test_time': max_execution_time,
            'priority_breakdown': dict(priority_breakdown),
            'test_suites': len(test_run.test_suites),
            'result_distribution': dict(result_counts)
        }
    
    def _log_run_summary(self, test_run: TestRun) -> None:
        """Log test run summary"""
        summary = test_run.summary
        
        self.logger.info("=" * 80)
        self.logger.info(f"TEST RUN SUMMARY: {test_run.name}")
        self.logger.info("=" * 80)
        self.logger.info(f"Run ID: {test_run.run_id}")
        self.logger.info(f"Duration: {summary['total_execution_time']:.2f} seconds")
        self.logger.info(f"Test Suites: {summary['test_suites']}")
        self.logger.info(f"Total Tests: {summary['total_tests']}")
        self.logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        self.logger.info("")
        self.logger.info("RESULTS BREAKDOWN:")
        self.logger.info(f"  ✓ Passed:  {summary['passed_tests']}")
        self.logger.info(f"  ✗ Failed:  {summary['failed_tests']}")
        self.logger.info(f"  ⚠ Errors:  {summary['error_tests']}")
        self.logger.info(f"  ⊘ Skipped: {summary['skipped_tests']}")
        self.logger.info(f"  ⏱ Timeout: {summary['timeout_tests']}")
        self.logger.info("")
        self.logger.info("PERFORMANCE METRICS:")
        self.logger.info(f"  Average Test Time: {summary['average_test_time']:.3f}s")
        self.logger.info(f"  Fastest Test:      {summary['min_test_time']:.3f}s")
        self.logger.info(f"  Slowest Test:      {summary['max_test_time']:.3f}s")
        self.logger.info("")
        
        # Priority breakdown
        self.logger.info("PRIORITY BREAKDOWN:")
        for priority, data in summary['priority_breakdown'].items():
            success_rate = (data['passed'] / data['total'] * 100) if data['total'] > 0 else 0
            self.logger.info(f"  {priority}: {data['passed']}/{data['total']} ({success_rate:.1f}%)")
        
        self.logger.info("=" * 80)
    
    def save_test_data(self, test_run: TestRun, filename: str = None) -> str:
        """Save test run data to JSON file"""
        if not filename:
            filename = f"test_run_{test_run.run_id}.json"
        
        filepath = self.log_directory / filename
        
        # Convert to serializable format
        test_data = asdict(test_run)
        
        # Convert enums to strings
        def convert_enums(obj):
            if isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            elif isinstance(obj, Enum):
                return obj.value
            else:
                return obj
        
        test_data = convert_enums(test_data)
        
        with open(filepath, 'w') as f:
            json.dump(test_data, f, indent=2, default=str)
        
        self.logger.info(f"Test data saved to: {filepath}")
        return str(filepath)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        return self.metrics_collector.get_summary()


class TestMetricsCollector:
    """Collects and analyzes test execution metrics"""
    
    def __init__(self):
        self.executions: List[TestExecution] = []
        self.performance_data: Dict[str, List[float]] = defaultdict(list)
        self.resource_data: Dict[str, List[float]] = defaultdict(list)
    
    def record_execution(self, execution: TestExecution) -> None:
        """Record test execution for metrics analysis"""
        self.executions.append(execution)
        
        # Record performance metrics
        for metric, value in execution.performance_metrics.items():
            self.performance_data[metric].append(value)
        
        # Record resource usage
        for resource, value in execution.resource_usage.items():
            self.resource_data[resource].append(value)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        if not self.executions:
            return {"status": "No execution data available"}
        
        # Basic statistics
        total_executions = len(self.executions)
        successful_executions = len([e for e in self.executions if e.result == TestResult.PASSED])
        success_rate = successful_executions / total_executions * 100
        
        # Execution time statistics
        execution_times = [e.execution_time for e in self.executions]
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        # Performance metrics summary
        performance_summary = {}
        for metric, values in self.performance_data.items():
            if values:
                performance_summary[metric] = {
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }
        
        # Resource usage summary
        resource_summary = {}
        for resource, values in self.resource_data.items():
            if values:
                resource_summary[resource] = {
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }
        
        return {
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'success_rate': success_rate,
            'execution_time': {
                'average': avg_time,
                'min': min_time,
                'max': max_time
            },
            'performance_metrics': performance_summary,
            'resource_usage': resource_summary
        }


class PerformanceTracker:
    """Tracks performance metrics during test execution"""
    
    def __init__(self):
        self.active_tests: Dict[str, float] = {}
        self.metrics: Dict[str, Dict[str, float]] = {}
    
    def start_test(self, test_id: str) -> None:
        """Start performance tracking for test"""
        self.active_tests[test_id] = time.time()
        self.metrics[test_id] = {}
    
    def stop_test(self, test_id: str) -> Dict[str, float]:
        """Stop performance tracking and return metrics"""
        if test_id not in self.active_tests:
            return {}
        
        end_time = time.time()
        start_time = self.active_tests.pop(test_id)
        
        metrics = self.metrics.get(test_id, {})
        metrics['total_time'] = end_time - start_time
        
        return metrics
    
    def record_metric(self, test_id: str, metric_name: str, value: float) -> None:
        """Record performance metric for test"""
        if test_id in self.metrics:
            self.metrics[test_id][metric_name] = value


class TestReportGenerator:
    """Generates comprehensive test reports"""
    
    def __init__(self, output_directory: Path):
        self.output_directory = output_directory
        self.reports_directory = output_directory / "reports"
        self.reports_directory.mkdir(parents=True, exist_ok=True)
    
    def generate_reports(self, test_run: TestRun) -> Dict[str, str]:
        """Generate all test reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        reports = {
            'html_report': self._generate_html_report(test_run, timestamp),
            'json_report': self._generate_json_report(test_run, timestamp),
            'csv_report': self._generate_csv_report(test_run, timestamp),
            'summary_report': self._generate_summary_report(test_run, timestamp)
        }
        
        return reports
    
    def _generate_html_report(self, test_run: TestRun, timestamp: str) -> str:
        """Generate HTML test report"""
        filename = f"test_report_{timestamp}.html"
        filepath = self.reports_directory / filename
        
        # Simple HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Report - {test_run.name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; }}
                .summary {{ margin: 20px 0; }}
                .test-case {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
                .passed {{ background-color: #d4edda; }}
                .failed {{ background-color: #f8d7da; }}
                .error {{ background-color: #fff3cd; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Test Report: {test_run.name}</h1>
                <p>Run ID: {test_run.run_id}</p>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Tests: {test_run.summary['total_tests']}</p>
                <p>Success Rate: {test_run.summary['success_rate']:.1f}%</p>
                <p>Duration: {test_run.summary['total_execution_time']:.2f} seconds</p>
            </div>
            
            <h2>Test Results</h2>
            <table>
                <tr>
                    <th>Test ID</th>
                    <th>Name</th>
                    <th>Result</th>
                    <th>Duration</th>
                    <th>Priority</th>
                </tr>
        """
        
        for execution in test_run.executions:
            css_class = execution.result.value.lower()
            html_content += f"""
                <tr class="{css_class}">
                    <td>{execution.test_case.test_id}</td>
                    <td>{execution.test_case.name}</td>
                    <td>{execution.result.value}</td>
                    <td>{execution.execution_time:.3f}s</td>
                    <td>{execution.test_case.priority.value}</td>
                </tr>
            """
        
        html_content += """
            </table>
        </body>
        </html>
        """
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def _generate_json_report(self, test_run: TestRun, timestamp: str) -> str:
        """Generate JSON test report"""
        filename = f"test_report_{timestamp}.json"
        filepath = self.reports_directory / filename
        
        # Convert to serializable format
        report_data = asdict(test_run)
        
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return str(filepath)
    
    def _generate_csv_report(self, test_run: TestRun, timestamp: str) -> str:
        """Generate CSV test report"""
        filename = f"test_report_{timestamp}.csv"
        filepath = self.reports_directory / filename
        
        import csv
        
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = ['test_id', 'name', 'result', 'execution_time', 'priority', 'category', 'error_message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for execution in test_run.executions:
                writer.writerow({
                    'test_id': execution.test_case.test_id,
                    'name': execution.test_case.name,
                    'result': execution.result.value,
                    'execution_time': execution.execution_time,
                    'priority': execution.test_case.priority.value,
                    'category': execution.test_case.category,
                    'error_message': execution.error_message or ''
                })
        
        return str(filepath)
    
    def _generate_summary_report(self, test_run: TestRun, timestamp: str) -> str:
        """Generate summary text report"""
        filename = f"test_summary_{timestamp}.txt"
        filepath = self.reports_directory / filename
        
        with open(filepath, 'w') as f:
            f.write(f"TEST RUN SUMMARY REPORT\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"Run Name: {test_run.name}\n")
            f.write(f"Run ID: {test_run.run_id}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"OVERVIEW:\n")
            f.write(f"Total Tests: {test_run.summary['total_tests']}\n")
            f.write(f"Success Rate: {test_run.summary['success_rate']:.1f}%\n")
            f.write(f"Total Duration: {test_run.summary['total_execution_time']:.2f} seconds\n\n")
            
            f.write(f"RESULTS BREAKDOWN:\n")
            for result_type, count in test_run.summary['result_distribution'].items():
                f.write(f"{result_type}: {count}\n")
            
            f.write(f"\nFAILED TESTS:\n")
            failed_tests = [e for e in test_run.executions if e.result in [TestResult.FAILED, TestResult.ERROR]]
            for execution in failed_tests:
                f.write(f"- {execution.test_case.test_id}: {execution.error_message or 'No error message'}\n")
        
        return str(filepath)