"""
Test Orchestrator

Automated testing pipeline with comprehensive coverage, parallel execution,
and detailed reporting for the entire MKD platform.
"""

import asyncio
import time
import logging
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
import json
import uuid
from pathlib import Path
import traceback
import sys
import importlib
import inspect
import importlib.util

logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    TIMEOUT = "timeout"


class TestPriority(Enum):
    """Test priority levels"""
    CRITICAL = "critical"    # Must pass for system to be viable
    HIGH = "high"           # Important functionality  
    MEDIUM = "medium"       # Standard functionality
    LOW = "low"            # Nice-to-have functionality


class TestCategory(Enum):
    """Test categories"""
    UNIT = "unit"                    # Unit tests
    INTEGRATION = "integration"      # Integration tests
    SYSTEM = "system"               # System-level tests
    PERFORMANCE = "performance"      # Performance tests
    SECURITY = "security"           # Security tests
    COMPATIBILITY = "compatibility"  # Cross-platform compatibility
    REGRESSION = "regression"       # Regression tests
    SMOKE = "smoke"                 # Smoke tests


@dataclass
class TestMetadata:
    """Test metadata and requirements"""
    requires_system: bool = False
    requires_gui: bool = False
    requires_network: bool = False
    requires_admin: bool = False
    platform_specific: Optional[str] = None  # "windows", "macos", "linux"
    min_python_version: str = "3.8"
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    timeout: float = 60.0
    retry_count: int = 0


@dataclass
class TestResult:
    """Individual test result"""
    test_id: str
    name: str
    status: TestStatus
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    output: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.end_time and self.duration is None:
            self.duration = self.end_time - self.start_time


@dataclass
class TestSuite:
    """Test suite configuration"""
    name: str
    description: str
    tests: List[Callable] = field(default_factory=list)
    setup_method: Optional[Callable] = None
    teardown_method: Optional[Callable] = None
    priority: TestPriority = TestPriority.MEDIUM
    category: TestCategory = TestCategory.UNIT
    metadata: TestMetadata = field(default_factory=TestMetadata)
    parallel_safe: bool = True


class TestOrchestrator:
    """Automated testing pipeline and orchestration system"""
    
    def __init__(self, max_workers: int = None, results_dir: str = None):
        self.max_workers = max_workers or min(32, multiprocessing.cpu_count() * 2)
        self.results_dir = Path(results_dir or Path.cwd() / "test_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Test registry
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_functions: Dict[str, Callable] = {}
        
        # Execution state
        self.current_run_id: Optional[str] = None
        self.test_results: Dict[str, TestResult] = {}
        self.suite_results: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.config = {
            "fail_fast": False,
            "parallel_execution": True,
            "timeout_multiplier": 1.0,
            "retry_failed": True,
            "coverage_threshold": 80.0,
            "performance_baseline": True,
            "detailed_logging": True
        }
        
        # Statistics
        self.stats = {
            "total_runs": 0,
            "total_tests": 0,
            "total_passed": 0,
            "total_failed": 0,
            "total_skipped": 0,
            "total_errors": 0,
            "average_duration": 0.0
        }
        
        # Event callbacks
        self.callbacks = {
            "test_started": [],
            "test_completed": [],
            "suite_started": [],
            "suite_completed": [],
            "run_started": [],
            "run_completed": []
        }
        
        logger.info(f"TestOrchestrator initialized with {self.max_workers} max workers")
    
    def register_test_suite(self, suite: TestSuite) -> str:
        """Register a test suite"""
        
        suite_id = f"{suite.name}_{uuid.uuid4().hex[:8]}"
        
        # Validate test functions
        validated_tests = []
        for test_func in suite.tests:
            if callable(test_func):
                # Register individual test function
                test_id = f"{suite_id}_{test_func.__name__}"
                self.test_functions[test_id] = test_func
                validated_tests.append(test_func)
            else:
                logger.warning(f"Invalid test function in suite {suite.name}: {test_func}")
        
        suite.tests = validated_tests
        self.test_suites[suite_id] = suite
        
        logger.debug(f"Registered test suite: {suite.name} ({len(validated_tests)} tests)")
        return suite_id
    
    def auto_discover_tests(self, base_path: str = "tests", pattern: str = "test_*.py") -> int:
        """Automatically discover and register test functions"""
        
        discovered_count = 0
        base_path = Path(base_path)
        
        if not base_path.exists():
            logger.warning(f"Test discovery path not found: {base_path}")
            return 0
        
        # Find test files
        test_files = list(base_path.glob(f"**/{pattern}"))
        
        for test_file in test_files:
            try:
                # Import test module
                module_name = test_file.stem
                spec = importlib.util.spec_from_file_location(module_name, test_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find test functions and classes
                suite_tests = []
                
                for name in dir(module):
                    obj = getattr(module, name)
                    
                    # Test functions (start with "test_")
                    if name.startswith("test_") and callable(obj):
                        suite_tests.append(obj)
                    
                    # Test classes (start with "Test")
                    elif name.startswith("Test") and inspect.isclass(obj):
                        for method_name in dir(obj):
                            if method_name.startswith("test_"):
                                method = getattr(obj, method_name)
                                if callable(method):
                                    # Create instance method wrapper
                                    instance = obj()
                                    wrapper = lambda inst=instance, m=method_name: getattr(inst, m)()
                                    wrapper.__name__ = f"{name}.{method_name}"
                                    suite_tests.append(wrapper)
                
                if suite_tests:
                    # Create test suite from discovered tests
                    suite = TestSuite(
                        name=f"discovered_{module_name}",
                        description=f"Auto-discovered tests from {test_file.name}",
                        tests=suite_tests,
                        category=TestCategory.UNIT
                    )
                    
                    self.register_test_suite(suite)
                    discovered_count += len(suite_tests)
                
            except Exception as e:
                logger.error(f"Failed to discover tests in {test_file}: {e}")
        
        logger.info(f"Auto-discovery completed: {discovered_count} tests found")
        return discovered_count
    
    async def run_all_tests(self, suite_filter: str = None, 
                           category_filter: TestCategory = None,
                           priority_filter: TestPriority = None) -> Dict[str, Any]:
        """Run all registered tests with optional filtering"""
        
        self.current_run_id = f"run_{uuid.uuid4().hex[:8]}_{int(time.time())}"
        start_time = time.time()
        
        # Filter test suites
        suites_to_run = {}
        for suite_id, suite in self.test_suites.items():
            # Apply filters
            if suite_filter and suite_filter not in suite.name:
                continue
            if category_filter and suite.category != category_filter:
                continue
            if priority_filter and suite.priority != priority_filter:
                continue
            
            suites_to_run[suite_id] = suite
        
        logger.info(f"Starting test run {self.current_run_id} with {len(suites_to_run)} suites")
        
        # Emit run started event
        await self._emit_event("run_started", {
            "run_id": self.current_run_id,
            "total_suites": len(suites_to_run),
            "start_time": start_time
        })
        
        # Execute test suites
        if self.config["parallel_execution"]:
            await self._run_suites_parallel(suites_to_run)
        else:
            await self._run_suites_sequential(suites_to_run)
        
        # Calculate results
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Compile run results
        run_results = {
            "run_id": self.current_run_id,
            "start_time": start_time,
            "end_time": end_time,
            "duration": total_duration,
            "total_suites": len(suites_to_run),
            "suite_results": self.suite_results.copy(),
            "test_results": {k: v for k, v in self.test_results.items() if v.start_time >= start_time},
            "summary": self._calculate_run_summary(),
            "config": self.config.copy()
        }
        
        # Update statistics
        self._update_statistics(run_results)
        
        # Save results
        await self._save_run_results(run_results)
        
        # Emit run completed event
        await self._emit_event("run_completed", run_results)
        
        logger.info(f"Test run completed: {run_results['summary']}")
        return run_results
    
    async def _run_suites_parallel(self, suites: Dict[str, TestSuite]) -> None:
        """Run test suites in parallel"""
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parallel-safe suites
            future_to_suite = {}
            sequential_suites = []
            
            for suite_id, suite in suites.items():
                if suite.parallel_safe:
                    future = executor.submit(self._run_suite_sync, suite_id, suite)
                    future_to_suite[future] = (suite_id, suite)
                else:
                    sequential_suites.append((suite_id, suite))
            
            # Wait for parallel suites to complete
            for future in as_completed(future_to_suite):
                suite_id, suite = future_to_suite[future]
                try:
                    result = future.result()
                    self.suite_results[suite_id] = result
                except Exception as e:
                    logger.error(f"Suite {suite.name} failed with exception: {e}")
                    self.suite_results[suite_id] = {
                        "status": "error",
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    }
            
            # Run sequential suites one by one
            for suite_id, suite in sequential_suites:
                try:
                    result = self._run_suite_sync(suite_id, suite)
                    self.suite_results[suite_id] = result
                except Exception as e:
                    logger.error(f"Sequential suite {suite.name} failed: {e}")
                    self.suite_results[suite_id] = {
                        "status": "error",
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    }
    
    async def _run_suites_sequential(self, suites: Dict[str, TestSuite]) -> None:
        """Run test suites sequentially"""
        
        for suite_id, suite in suites.items():
            try:
                result = self._run_suite_sync(suite_id, suite)
                self.suite_results[suite_id] = result
                
                # Check fail-fast
                if self.config["fail_fast"] and result.get("failed_count", 0) > 0:
                    logger.info("Fail-fast enabled, stopping execution")
                    break
                    
            except Exception as e:
                logger.error(f"Suite {suite.name} failed with exception: {e}")
                self.suite_results[suite_id] = {
                    "status": "error",
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
                
                if self.config["fail_fast"]:
                    break
    
    def _run_suite_sync(self, suite_id: str, suite: TestSuite) -> Dict[str, Any]:
        """Run a test suite synchronously"""
        
        start_time = time.time()
        suite_results = {
            "suite_id": suite_id,
            "name": suite.name,
            "start_time": start_time,
            "test_results": [],
            "passed_count": 0,
            "failed_count": 0,
            "skipped_count": 0,
            "error_count": 0,
            "status": "running"
        }
        
        logger.info(f"Running test suite: {suite.name}")
        
        try:
            # Run suite setup
            if suite.setup_method:
                suite.setup_method()
            
            # Run individual tests
            for test_func in suite.tests:
                test_result = self._run_single_test(suite, test_func)
                suite_results["test_results"].append(test_result.test_id)
                self.test_results[test_result.test_id] = test_result
                
                # Update counters
                if test_result.status == TestStatus.PASSED:
                    suite_results["passed_count"] += 1
                elif test_result.status == TestStatus.FAILED:
                    suite_results["failed_count"] += 1
                elif test_result.status == TestStatus.SKIPPED:
                    suite_results["skipped_count"] += 1
                else:
                    suite_results["error_count"] += 1
            
            # Run suite teardown
            if suite.teardown_method:
                suite.teardown_method()
            
            # Determine suite status
            if suite_results["error_count"] > 0:
                suite_results["status"] = "error"
            elif suite_results["failed_count"] > 0:
                suite_results["status"] = "failed"
            elif suite_results["passed_count"] > 0:
                suite_results["status"] = "passed"
            else:
                suite_results["status"] = "skipped"
            
        except Exception as e:
            suite_results["status"] = "error"
            suite_results["error"] = str(e)
            suite_results["traceback"] = traceback.format_exc()
            logger.error(f"Suite setup/teardown failed for {suite.name}: {e}")
        
        finally:
            suite_results["end_time"] = time.time()
            suite_results["duration"] = suite_results["end_time"] - start_time
        
        return suite_results
    
    def _run_single_test(self, suite: TestSuite, test_func: Callable) -> TestResult:
        """Run a single test function"""
        
        test_id = f"{suite.name}_{test_func.__name__}_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        test_result = TestResult(
            test_id=test_id,
            name=test_func.__name__,
            status=TestStatus.RUNNING,
            start_time=start_time
        )
        
        try:
            # Apply timeout
            timeout = suite.metadata.timeout * self.config["timeout_multiplier"]
            
            # Run test with timeout
            if asyncio.iscoroutinefunction(test_func):
                # Async test function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(asyncio.wait_for(test_func(), timeout=timeout))
                finally:
                    loop.close()
            else:
                # Sync test function
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Test timed out after {timeout}s")
                
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(timeout))
                
                try:
                    test_func()
                finally:
                    signal.alarm(0)
            
            test_result.status = TestStatus.PASSED
            
        except TimeoutError as e:
            test_result.status = TestStatus.TIMEOUT
            test_result.error_message = str(e)
            
        except AssertionError as e:
            test_result.status = TestStatus.FAILED
            test_result.error_message = str(e)
            test_result.error_traceback = traceback.format_exc()
            
        except Exception as e:
            test_result.status = TestStatus.ERROR
            test_result.error_message = str(e)
            test_result.error_traceback = traceback.format_exc()
        
        finally:
            test_result.end_time = time.time()
            test_result.duration = test_result.end_time - start_time
        
        logger.debug(f"Test completed: {test_func.__name__} -> {test_result.status.value}")
        return test_result
    
    def _calculate_run_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics for the current run"""
        
        total_tests = len(self.test_results)
        if total_tests == 0:
            return {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0, "success_rate": 0.0}
        
        passed = sum(1 for r in self.test_results.values() if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.test_results.values() if r.status == TestStatus.FAILED)
        skipped = sum(1 for r in self.test_results.values() if r.status == TestStatus.SKIPPED)
        errors = sum(1 for r in self.test_results.values() if r.status == TestStatus.ERROR)
        timeouts = sum(1 for r in self.test_results.values() if r.status == TestStatus.TIMEOUT)
        
        success_rate = (passed / total_tests) * 100
        average_duration = sum(r.duration or 0 for r in self.test_results.values()) / total_tests
        
        return {
            "total": total_tests,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "timeouts": timeouts,
            "success_rate": success_rate,
            "average_duration": average_duration
        }
    
    def _update_statistics(self, run_results: Dict[str, Any]) -> None:
        """Update overall statistics"""
        
        summary = run_results["summary"]
        
        self.stats["total_runs"] += 1
        self.stats["total_tests"] += summary["total"]
        self.stats["total_passed"] += summary["passed"]
        self.stats["total_failed"] += summary["failed"]
        self.stats["total_skipped"] += summary["skipped"]
        self.stats["total_errors"] += summary["errors"]
        
        # Update average duration
        total_duration = self.stats["average_duration"] * (self.stats["total_runs"] - 1)
        total_duration += run_results["duration"]
        self.stats["average_duration"] = total_duration / self.stats["total_runs"]
    
    async def _save_run_results(self, run_results: Dict[str, Any]) -> None:
        """Save run results to file"""
        
        try:
            # Save detailed results
            results_file = self.results_dir / f"run_{run_results['run_id']}.json"
            
            with open(results_file, 'w') as f:
                json.dump(run_results, f, indent=2, default=str)
            
            # Save summary
            summary_file = self.results_dir / "latest_summary.json"
            summary_data = {
                "run_id": run_results["run_id"],
                "timestamp": run_results["start_time"],
                "summary": run_results["summary"],
                "duration": run_results["duration"]
            }
            
            with open(summary_file, 'w') as f:
                json.dump(summary_data, f, indent=2, default=str)
            
            logger.debug(f"Test results saved to {results_file}")
            
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit event to registered callbacks"""
        
        callbacks = self.callbacks.get(event_type, [])
        
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Event callback failed for {event_type}: {e}")
    
    def add_callback(self, event_type: str, callback: Callable) -> None:
        """Add event callback"""
        
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
        else:
            logger.warning(f"Unknown event type: {event_type}")
    
    def get_test_statistics(self) -> Dict[str, Any]:
        """Get comprehensive test statistics"""
        
        return {
            "orchestrator_stats": self.stats.copy(),
            "registered_suites": len(self.test_suites),
            "registered_tests": len(self.test_functions),
            "config": self.config.copy(),
            "last_run_id": self.current_run_id,
            "results_directory": str(self.results_dir)
        }
    
    def generate_html_report(self, run_id: str = None) -> str:
        """Generate HTML test report"""
        
        if not run_id:
            run_id = self.current_run_id
        
        if not run_id:
            return "<html><body><h1>No test run data available</h1></body></html>"
        
        # Load run results
        results_file = self.results_dir / f"run_{run_id}.json"
        
        if not results_file.exists():
            return f"<html><body><h1>Test run {run_id} not found</h1></body></html>"
        
        with open(results_file, 'r') as f:
            run_results = json.load(f)
        
        # Generate HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MKD Test Report - {run_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .error {{ color: orange; }}
                .skipped {{ color: gray; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>MKD Automation Platform - Test Report</h1>
            <div class="summary">
                <h2>Run Summary</h2>
                <p><strong>Run ID:</strong> {run_id}</p>
                <p><strong>Duration:</strong> {run_results['duration']:.2f} seconds</p>
                <p><strong>Total Tests:</strong> {run_results['summary']['total']}</p>
                <p><strong>Success Rate:</strong> {run_results['summary']['success_rate']:.1f}%</p>
                <p>
                    <span class="passed">✅ Passed: {run_results['summary']['passed']}</span> |
                    <span class="failed">❌ Failed: {run_results['summary']['failed']}</span> |
                    <span class="error">⚠️ Errors: {run_results['summary']['errors']}</span> |
                    <span class="skipped">⏭️ Skipped: {run_results['summary']['skipped']}</span>
                </p>
            </div>
            
            <h2>Test Results</h2>
            <table>
                <tr>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Error Message</th>
                </tr>
        """
        
        for test_result in run_results['test_results'].values():
            status_class = test_result['status']
            status_icon = {
                'passed': '✅',
                'failed': '❌', 
                'error': '⚠️',
                'skipped': '⏭️',
                'timeout': '⏱️'
            }.get(test_result['status'], '❓')
            
            html += f"""
                <tr>
                    <td>{test_result['name']}</td>
                    <td class="{status_class}">{status_icon} {test_result['status'].title()}</td>
                    <td>{test_result.get('duration', 0):.3f}s</td>
                    <td>{test_result.get('error_message', '')}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        return html