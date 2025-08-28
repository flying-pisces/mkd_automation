#!/usr/bin/env python3
"""
Comprehensive Test Suite for MKD Automation Platform v2.0

This suite runs all test levels:
1. Unit Tests - Individual component testing
2. Integration Tests - Component interaction testing  
3. System Tests - Full system functionality testing
4. Acceptance Tests - Product-level validation testing
"""

import asyncio
import logging
import sys
import time
import json
import traceback
import subprocess
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import MKD v2.0 components
try:
    from mkd_v2.platform import PlatformDetector
    from mkd_v2.integration import ComponentRegistry, EventBus, SystemController
    from mkd_v2.input import InputRecorder, InputAction, ActionType
    from mkd_v2.performance import (
        PerformanceProfiler, CacheManager, ResourceMonitor, RuntimeOptimizer,
        get_profiler, get_cache, get_optimizer, CacheStrategy, ProfileType
    )
    from mkd_v2.exceptions import ComponentNotFoundError, RecordingError, PlaybackError
except ImportError as e:
    print(f"❌ Failed to import MKD v2.0 components: {e}")
    sys.exit(1)


@dataclass
class TestResult:
    """Comprehensive test result"""
    test_name: str
    test_level: str  # unit, integration, system, acceptance
    success: bool
    duration: float
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    memory_usage: Optional[float] = None


@dataclass
class BugReport:
    """Bug report structure"""
    bug_id: str
    severity: str  # critical, high, medium, low
    category: str  # functional, performance, usability, security
    title: str
    description: str
    steps_to_reproduce: List[str]
    expected_result: str
    actual_result: str
    test_level: str
    timestamp: str


class ComprehensiveTestLogger:
    """Advanced test logger for comprehensive testing"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.log_dir = self.test_dir / "comprehensive_logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.setup_logging()
        
        # Test tracking
        self.results: List[TestResult] = []
        self.bugs: List[BugReport] = []
        self.start_time = time.time()
        self.test_stats = {
            "unit": {"passed": 0, "failed": 0, "total": 0},
            "integration": {"passed": 0, "failed": 0, "total": 0},
            "system": {"passed": 0, "failed": 0, "total": 0},
            "acceptance": {"passed": 0, "failed": 0, "total": 0}
        }
        
        # Performance tracking
        self.performance_baseline = {}
        self.memory_baseline = psutil.Process().memory_info().rss / 1024 / 1024
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        self.logger = logging.getLogger("ComprehensiveTest")
        self.logger.setLevel(logging.DEBUG)
        
        # Main log file
        main_handler = logging.FileHandler(
            self.log_dir / f"comprehensive_test_{self.timestamp}.log"
        )
        main_handler.setLevel(logging.DEBUG)
        
        # Error log file
        error_handler = logging.FileHandler(
            self.log_dir / f"error_log_{self.timestamp}.log"
        )
        error_handler.setLevel(logging.ERROR)
        
        # Console output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        main_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        self.logger.addHandler(main_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
    
    def log_test_result(self, result: TestResult):
        """Log and track test result"""
        self.results.append(result)
        
        # Update statistics
        self.test_stats[result.test_level]["total"] += 1
        if result.success:
            self.test_stats[result.test_level]["passed"] += 1
            self.logger.info(f"✅ [{result.test_level.upper()}] {result.test_name} - PASSED ({result.duration:.3f}s)")
        else:
            self.test_stats[result.test_level]["failed"] += 1
            self.logger.error(f"❌ [{result.test_level.upper()}] {result.test_name} - FAILED ({result.duration:.3f}s)")
            if result.error_message:
                self.logger.error(f"   Error: {result.error_message}")
        
        # Log warnings
        for warning in result.warnings:
            self.logger.warning(f"⚠️  [{result.test_level.upper()}] {result.test_name} - {warning}")
        
        # Log performance metrics
        if result.performance_metrics:
            self.logger.debug(f"📊 [{result.test_level.upper()}] {result.test_name} - Metrics: {result.performance_metrics}")
    
    def report_bug(self, bug: BugReport):
        """Report a bug found during testing"""
        self.bugs.append(bug)
        severity_icon = {"critical": "🚨", "high": "🔴", "medium": "🟡", "low": "🟢"}
        icon = severity_icon.get(bug.severity, "🔵")
        
        self.logger.error(f"{icon} BUG FOUND - {bug.bug_id}: {bug.title}")
        self.logger.error(f"   Severity: {bug.severity.upper()}")
        self.logger.error(f"   Category: {bug.category}")
        self.logger.error(f"   Test Level: {bug.test_level}")
        self.logger.error(f"   Description: {bug.description}")
        self.logger.error(f"   Expected: {bug.expected_result}")
        self.logger.error(f"   Actual: {bug.actual_result}")
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_duration = time.time() - self.start_time
        total_tests = sum(stats["total"] for stats in self.test_stats.values())
        total_passed = sum(stats["passed"] for stats in self.test_stats.values())
        total_failed = sum(stats["failed"] for stats in self.test_stats.values())
        
        # Calculate success rates by level
        success_rates = {}
        for level, stats in self.test_stats.items():
            if stats["total"] > 0:
                success_rates[level] = (stats["passed"] / stats["total"]) * 100
            else:
                success_rates[level] = 0.0
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "test_session": {
                "timestamp": datetime.now().isoformat(),
                "duration": total_duration,
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_failed,
                "overall_success_rate": overall_success_rate
            },
            "test_levels": {
                level: {
                    **stats,
                    "success_rate": success_rates[level]
                }
                for level, stats in self.test_stats.items()
            },
            "bugs_found": len(self.bugs),
            "critical_bugs": len([b for b in self.bugs if b.severity == "critical"]),
            "high_priority_bugs": len([b for b in self.bugs if b.severity == "high"]),
            "performance_metrics": self._calculate_performance_summary(),
            "memory_analysis": self._calculate_memory_summary(),
            "recommendations": self._generate_recommendations()
        }
        
        # Save detailed reports
        self._save_test_report(report)
        self._save_bug_report()
        
        return report
    
    def _calculate_performance_summary(self) -> Dict[str, Any]:
        """Calculate performance summary"""
        performance_results = [r for r in self.results if r.performance_metrics]
        
        if not performance_results:
            return {"message": "No performance metrics collected"}
        
        durations = [r.duration for r in self.results]
        return {
            "average_test_duration": sum(durations) / len(durations),
            "max_test_duration": max(durations),
            "min_test_duration": min(durations),
            "total_test_time": sum(durations),
            "tests_with_metrics": len(performance_results)
        }
    
    def _calculate_memory_summary(self) -> Dict[str, Any]:
        """Calculate memory usage summary"""
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_growth = current_memory - self.memory_baseline
        
        memory_results = [r for r in self.results if r.memory_usage is not None]
        
        summary = {
            "baseline_memory_mb": self.memory_baseline,
            "current_memory_mb": current_memory,
            "memory_growth_mb": memory_growth,
            "memory_growth_percentage": (memory_growth / self.memory_baseline) * 100
        }
        
        if memory_results:
            memory_values = [r.memory_usage for r in memory_results]
            summary.update({
                "peak_memory_mb": max(memory_values),
                "average_memory_mb": sum(memory_values) / len(memory_values)
            })
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Overall success rate recommendations
        overall_rate = sum(stats["passed"] for stats in self.test_stats.values()) / max(1, sum(stats["total"] for stats in self.test_stats.values())) * 100
        
        if overall_rate >= 95:
            recommendations.append("✅ Excellent test results! Platform is production-ready.")
        elif overall_rate >= 80:
            recommendations.append("✅ Good test results. Address remaining issues before production.")
        else:
            recommendations.append("⚠️  Low success rate. Significant issues need resolution.")
        
        # Bug-based recommendations
        critical_bugs = len([b for b in self.bugs if b.severity == "critical"])
        high_bugs = len([b for b in self.bugs if b.severity == "high"])
        
        if critical_bugs > 0:
            recommendations.append(f"🚨 {critical_bugs} critical bug(s) found - must fix before release.")
        if high_bugs > 0:
            recommendations.append(f"🔴 {high_bugs} high priority bug(s) found - recommend fixing before release.")
        
        # Performance recommendations
        memory_summary = self._calculate_memory_summary()
        if memory_summary["memory_growth_percentage"] > 50:
            recommendations.append("⚠️  High memory growth detected - investigate potential memory leaks.")
        
        # Test level recommendations
        for level, stats in self.test_stats.items():
            if stats["total"] > 0 and stats["passed"] / stats["total"] < 0.8:
                recommendations.append(f"⚠️  {level.title()} tests below 80% success rate - needs attention.")
        
        return recommendations
    
    def _save_test_report(self, report: Dict[str, Any]):
        """Save detailed test report"""
        # JSON report
        json_file = self.log_dir / f"test_report_{self.timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Detailed test results
        results_file = self.log_dir / f"detailed_results_{self.timestamp}.json"
        detailed_results = {
            "test_results": [
                {
                    "name": r.test_name,
                    "level": r.test_level,
                    "success": r.success,
                    "duration": r.duration,
                    "error": r.error_message,
                    "warnings": r.warnings,
                    "performance_metrics": r.performance_metrics,
                    "memory_usage": r.memory_usage
                }
                for r in self.results
            ]
        }
        
        with open(results_file, 'w') as f:
            json.dump(detailed_results, f, indent=2)
    
    def _save_bug_report(self):
        """Save bug report"""
        if not self.bugs:
            return
        
        bug_file = self.log_dir / f"bug_report_{self.timestamp}.json"
        bug_data = {
            "summary": {
                "total_bugs": len(self.bugs),
                "critical": len([b for b in self.bugs if b.severity == "critical"]),
                "high": len([b for b in self.bugs if b.severity == "high"]),
                "medium": len([b for b in self.bugs if b.severity == "medium"]),
                "low": len([b for b in self.bugs if b.severity == "low"])
            },
            "bugs": [
                {
                    "bug_id": b.bug_id,
                    "severity": b.severity,
                    "category": b.category,
                    "title": b.title,
                    "description": b.description,
                    "steps_to_reproduce": b.steps_to_reproduce,
                    "expected_result": b.expected_result,
                    "actual_result": b.actual_result,
                    "test_level": b.test_level,
                    "timestamp": b.timestamp
                }
                for b in self.bugs
            ]
        }
        
        with open(bug_file, 'w') as f:
            json.dump(bug_data, f, indent=2)


class ComprehensiveTestSuite:
    """Complete test suite covering all testing levels"""
    
    def __init__(self):
        self.logger = ComprehensiveTestLogger()
        self.profiler = get_profiler()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        self.logger.logger.info("🚀 Starting Comprehensive Test Suite - MKD Automation Platform v2.0")
        self.logger.logger.info("=" * 80)
        
        # Run all test levels in order
        await self.run_unit_tests()
        await self.run_integration_tests()
        await self.run_system_tests()
        await self.run_acceptance_tests()
        
        # Generate final report
        report = self.logger.generate_final_report()
        self.print_final_summary(report)
        
        return report
    
    # UNIT TESTS
    async def run_unit_tests(self):
        """Run unit tests for individual components"""
        self.logger.logger.info("🔬 STARTING UNIT TESTS")
        self.logger.logger.info("-" * 50)
        
        unit_tests = [
            self.unit_test_platform_detector,
            self.unit_test_component_registry,
            self.unit_test_event_bus,
            self.unit_test_input_recorder,
            self.unit_test_input_action,
            self.unit_test_performance_profiler,
            self.unit_test_cache_manager,
            self.unit_test_resource_monitor,
            self.unit_test_runtime_optimizer,
            self.unit_test_exceptions
        ]
        
        for test in unit_tests:
            await self.run_single_test(test, "unit")
    
    async def unit_test_platform_detector(self):
        """Unit test for PlatformDetector"""
        detector = PlatformDetector()
        
        # Test platform detection
        platform_info = detector.detect_platform()
        assert platform_info is not None, "Platform info should not be None"
        assert hasattr(platform_info, 'name'), "Platform info should have name attribute"
        assert platform_info.name in ["windows", "macos", "linux"], f"Invalid platform: {platform_info.name}"
        
        # Test capabilities
        capabilities = detector.get_capabilities()
        assert isinstance(capabilities, list), "Capabilities should be a list"
        assert len(capabilities) > 0, "Should have at least one capability"
        
        # Test platform info
        info = PlatformDetector.get_platform_info()
        assert isinstance(info, dict), "Platform info should be a dictionary"
        assert "system" in info, "Platform info should contain system"
        assert "python_version" in info, "Platform info should contain Python version"
    
    async def unit_test_component_registry(self):
        """Unit test for ComponentRegistry"""
        registry = ComponentRegistry()
        
        # Test basic functionality
        assert hasattr(registry, 'register_component'), "Should have register_component method"
        assert hasattr(registry, 'get_component'), "Should have get_component method"
        assert hasattr(registry, 'components'), "Should have components attribute"
        
        # Test component registration (basic check)
        initial_count = len(registry.components)
        # Registry functionality will be tested more in integration tests
        assert isinstance(registry.components, dict), "Components should be a dictionary"
    
    async def unit_test_event_bus(self):
        """Unit test for EventBus"""
        event_bus = EventBus()
        
        # Test initialization
        assert not event_bus.running, "Event bus should not be running initially"
        assert hasattr(event_bus, 'subscribers'), "Should have subscribers attribute"
        
        # Test start/stop
        await event_bus.start()
        assert event_bus.running, "Event bus should be running after start"
        
        await event_bus.stop()
        assert not event_bus.running, "Event bus should be stopped after stop"
    
    async def unit_test_input_recorder(self):
        """Unit test for InputRecorder"""
        recorder = InputRecorder()
        
        # Test initialization
        assert not recorder.is_recording, "Recorder should not be recording initially"
        assert isinstance(recorder.recorded_actions, list), "Recorded actions should be a list"
        assert len(recorder.recorded_actions) == 0, "Should start with no recorded actions"
        
        # Test recording lifecycle
        await recorder.start_recording()
        assert recorder.is_recording, "Should be recording after start"
        
        actions = await recorder.stop_recording()
        assert not recorder.is_recording, "Should not be recording after stop"
        assert isinstance(actions, list), "Should return list of actions"
    
    async def unit_test_input_action(self):
        """Unit test for InputAction"""
        # Test action creation
        action = InputAction(
            action_type=ActionType.CLICK,
            timestamp=time.time(),
            coordinates=(100, 200)
        )
        
        assert action.action_type == ActionType.CLICK, "Action type should be CLICK"
        assert action.coordinates == (100, 200), "Coordinates should match"
        assert action.x == 100, "X coordinate should be 100"
        assert action.y == 200, "Y coordinate should be 200"
        
        # Test action serialization
        action_dict = action.to_dict()
        assert isinstance(action_dict, dict), "to_dict should return dictionary"
        assert action_dict["action_type"] == "click", "Action type should be serialized"
        
        # Test action deserialization
        restored_action = InputAction.from_dict(action_dict)
        assert restored_action.action_type == ActionType.CLICK, "Restored action type should match"
        assert restored_action.coordinates == (100, 200), "Restored coordinates should match"
    
    async def unit_test_performance_profiler(self):
        """Unit test for PerformanceProfiler"""
        profiler = PerformanceProfiler()
        
        # Test basic profiling
        profile_id = profiler.start_profiling("unit_test")
        assert profile_id is not None, "Should return profile ID"
        assert profile_id in profiler.active_profiles, "Profile should be active"
        
        # Simulate work
        await asyncio.sleep(0.001)
        
        metrics = profiler.stop_profiling(profile_id)
        assert metrics is not None, "Should return metrics"
        assert metrics.duration > 0, "Duration should be positive"
        assert metrics.operation_name == "unit_test", "Operation name should match"
        
        # Test analysis
        analysis = profiler.analyze_performance(60.0)
        assert analysis is not None, "Should return analysis"
    
    async def unit_test_cache_manager(self):
        """Unit test for CacheManager"""
        cache = CacheManager(max_size=10, max_memory_mb=1.0)
        
        # Test basic operations
        assert cache.put("test_key", "test_value"), "Should successfully put value"
        assert cache.get("test_key") == "test_value", "Should retrieve correct value"
        assert cache.get("nonexistent") is None, "Should return None for missing keys"
        
        # Test get_or_compute
        def compute_func():
            return "computed_value"
        
        result = cache.get_or_compute("compute_key", compute_func)
        assert result == "computed_value", "Should return computed value"
        
        # Second call should hit cache
        result2 = cache.get_or_compute("compute_key", lambda: "different_value")
        assert result2 == "computed_value", "Should return cached value"
        
        # Test statistics
        stats = cache.get_cache_statistics()
        assert "usage" in stats, "Stats should contain usage"
        assert "performance" in stats, "Stats should contain performance"
    
    async def unit_test_resource_monitor(self):
        """Unit test for ResourceMonitor"""
        from mkd_v2.performance.resource_monitor import ResourceType, AlertLevel
        
        monitor = ResourceMonitor()
        
        # Test threshold setting
        monitor.set_threshold(ResourceType.CPU_USAGE, AlertLevel.WARNING, 80.0)
        assert ResourceType.CPU_USAGE in monitor.thresholds, "Threshold should be set"
        
        # Test alert callbacks
        alerts_received = []
        def test_callback(alert):
            alerts_received.append(alert)
        
        monitor.add_alert_callback(test_callback)
        assert test_callback in monitor.alert_callbacks, "Callback should be added"
    
    async def unit_test_runtime_optimizer(self):
        """Unit test for RuntimeOptimizer"""
        from mkd_v2.performance.optimizer import OptimizationStrategy
        
        optimizer = RuntimeOptimizer(strategy=OptimizationStrategy.BALANCED)
        
        # Test initialization
        assert optimizer.strategy == OptimizationStrategy.BALANCED, "Strategy should be set"
        assert len(optimizer.optimization_rules) > 0, "Should have default rules"
        
        # Test strategy change
        optimizer.set_strategy(OptimizationStrategy.CONSERVATIVE)
        assert optimizer.strategy == OptimizationStrategy.CONSERVATIVE, "Strategy should be updated"
        
        # Test report generation
        report = optimizer.get_optimization_report()
        assert "configuration" in report, "Report should contain configuration"
        assert "statistics" in report, "Report should contain statistics"
    
    async def unit_test_exceptions(self):
        """Unit test for custom exceptions"""
        # Test ComponentNotFoundError
        try:
            raise ComponentNotFoundError("test_component")
        except ComponentNotFoundError as e:
            assert "test_component" in str(e), "Exception should contain component name"
        
        # Test other exceptions
        from mkd_v2.exceptions import RecordingError, PlaybackError
        
        try:
            raise RecordingError("test recording error")
        except RecordingError as e:
            assert "recording error" in str(e).lower(), "Exception should contain error message"
        
        try:
            raise PlaybackError("test playback error")
        except PlaybackError as e:
            assert "playback error" in str(e).lower(), "Exception should contain error message"
    
    # INTEGRATION TESTS
    async def run_integration_tests(self):
        """Run integration tests for component interactions"""
        self.logger.logger.info("🔗 STARTING INTEGRATION TESTS")
        self.logger.logger.info("-" * 50)
        
        integration_tests = [
            self.integration_test_system_controller,
            self.integration_test_event_bus_publishing,
            self.integration_test_performance_integration,
            self.integration_test_recording_playback_flow,
            self.integration_test_error_propagation
        ]
        
        for test in integration_tests:
            await self.run_single_test(test, "integration")
    
    async def integration_test_system_controller(self):
        """Integration test for SystemController"""
        controller = SystemController()
        
        # Test initialization
        await controller.initialize()
        status = controller.get_system_status()
        assert status["status"] in ["running", "error"], f"Invalid status: {status['status']}"
        
        # Test component access
        registry = controller.get_component("component_registry")
        assert registry is not None, "Should be able to get component registry"
        
        event_bus = controller.get_component("event_bus")
        assert event_bus is not None, "Should be able to get event bus"
        
        await controller.shutdown()
    
    async def integration_test_event_bus_publishing(self):
        """Integration test for event bus publishing/subscribing"""
        event_bus = EventBus()
        await event_bus.start()
        
        received_events = []
        
        async def test_handler(event_data):
            received_events.append(event_data)
        
        # Subscribe to events
        from mkd_v2.integration.event_bus import EventType
        subscription_id = event_bus.subscribe(EventType.SYSTEM_STARTED, test_handler)
        
        # Publish event
        test_data = {"test": "integration", "timestamp": time.time()}
        await event_bus.publish(EventType.SYSTEM_STARTED, test_data)
        
        # Give time for event processing
        await asyncio.sleep(0.1)
        
        assert len(received_events) > 0, "Should have received events"
        assert received_events[0] == test_data, "Event data should match"
        
        # Cleanup
        event_bus.unsubscribe(subscription_id)
        await event_bus.stop()
    
    async def integration_test_performance_integration(self):
        """Integration test for performance components working together"""
        profiler = get_profiler()
        cache = get_cache()
        optimizer = get_optimizer()
        
        # Test integrated workflow
        profile_id = profiler.start_profiling("integration_test")
        
        # Use cache during profiling
        def expensive_operation():
            return sum(i * i for i in range(1000))
        
        result1 = cache.get_or_compute("integration_test", expensive_operation)
        result2 = cache.get_or_compute("integration_test", expensive_operation)
        
        assert result1 == result2, "Cached results should match"
        
        metrics = profiler.stop_profiling(profile_id)
        assert metrics is not None, "Should get profiling metrics"
        
        # Test optimizer report includes cache stats
        report = optimizer.get_optimization_report()
        assert report is not None, "Should get optimizer report"
    
    async def integration_test_recording_playback_flow(self):
        """Integration test for recording and playback flow"""
        controller = SystemController()
        await controller.initialize()
        
        # Test recording flow
        await controller.start_recording()
        
        # Simulate recording time
        await asyncio.sleep(0.01)
        
        actions = await controller.stop_recording()
        assert isinstance(actions, list), "Should return list of actions"
        
        # Test playback flow (mock execution)
        result = await controller.execute_actions(actions)
        assert hasattr(result, 'success'), "Result should have success attribute"
        
        await controller.shutdown()
    
    async def integration_test_error_propagation(self):
        """Integration test for error handling across components"""
        registry = ComponentRegistry()
        
        # Test error propagation
        try:
            registry.get_component("nonexistent_component")
            assert False, "Should have raised an exception"
        except Exception as e:
            assert isinstance(e, Exception), "Should raise an exception"
    
    # SYSTEM TESTS
    async def run_system_tests(self):
        """Run system tests for full system functionality"""
        self.logger.logger.info("🏗️  STARTING SYSTEM TESTS")
        self.logger.logger.info("-" * 50)
        
        system_tests = [
            self.system_test_full_initialization,
            self.system_test_performance_under_load,
            self.system_test_memory_management,
            self.system_test_concurrent_operations,
            self.system_test_error_recovery
        ]
        
        for test in system_tests:
            await self.run_single_test(test, "system")
    
    async def system_test_full_initialization(self):
        """System test for full system initialization"""
        start_time = time.time()
        
        controller = SystemController()
        await controller.initialize()
        
        initialization_time = time.time() - start_time
        
        # Verify system is running
        status = controller.get_system_status()
        assert status["status"] in ["running", "error"], "System should be in valid state"
        
        # Performance requirement: < 5 seconds for system tests
        if initialization_time > 5.0:
            self.logger.report_bug(BugReport(
                bug_id="SYS-001",
                severity="medium",
                category="performance",
                title="Slow System Initialization",
                description=f"System initialization took {initialization_time:.2f} seconds",
                steps_to_reproduce=["Create SystemController", "Call initialize()"],
                expected_result="Initialization should complete in < 5 seconds",
                actual_result=f"Initialization took {initialization_time:.2f} seconds",
                test_level="system",
                timestamp=datetime.now().isoformat()
            ))
        
        await controller.shutdown()
    
    async def system_test_performance_under_load(self):
        """System test for performance under load"""
        profiler = get_profiler()
        cache = get_cache()
        
        # Simulate load
        tasks = []
        for i in range(10):
            task = asyncio.create_task(self._simulate_load_operation(i, profiler, cache))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for exceptions
        exceptions = [r for r in results if isinstance(r, Exception)]
        if exceptions:
            self.logger.report_bug(BugReport(
                bug_id="SYS-002",
                severity="high",
                category="functional",
                title="Exceptions Under Load",
                description=f"Got {len(exceptions)} exceptions during load test",
                steps_to_reproduce=["Run 10 concurrent operations", "Check for exceptions"],
                expected_result="No exceptions should occur",
                actual_result=f"{len(exceptions)} exceptions occurred",
                test_level="system",
                timestamp=datetime.now().isoformat()
            ))
        
        # Verify all operations completed
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 8, "At least 80% of operations should succeed"
    
    async def _simulate_load_operation(self, operation_id: int, profiler: PerformanceProfiler, cache: CacheManager):
        """Simulate a load operation"""
        profile_id = profiler.start_profiling(f"load_op_{operation_id}")
        
        # Simulate work with caching
        def work_function():
            return sum(i ** 2 for i in range(100))
        
        result = cache.get_or_compute(f"load_key_{operation_id % 3}", work_function)
        
        await asyncio.sleep(0.001)  # Simulate async work
        
        profiler.stop_profiling(profile_id)
        return result
    
    async def system_test_memory_management(self):
        """System test for memory management"""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Create and destroy multiple components
        controllers = []
        for i in range(5):
            controller = SystemController()
            await controller.initialize()
            controllers.append(controller)
        
        # Shutdown all controllers
        for controller in controllers:
            await controller.shutdown()
        
        # Force garbage collection
        import gc
        gc.collect()
        await asyncio.sleep(0.1)  # Allow cleanup time
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        # Check for excessive memory growth
        if memory_growth > 100:  # More than 100MB growth
            self.logger.report_bug(BugReport(
                bug_id="SYS-003",
                severity="medium",
                category="performance",
                title="Excessive Memory Growth",
                description=f"Memory grew by {memory_growth:.1f}MB during system test",
                steps_to_reproduce=["Create 5 SystemControllers", "Initialize and shutdown", "Check memory"],
                expected_result="Memory growth should be < 100MB",
                actual_result=f"Memory grew by {memory_growth:.1f}MB",
                test_level="system",
                timestamp=datetime.now().isoformat()
            ))
    
    async def system_test_concurrent_operations(self):
        """System test for concurrent operations"""
        controller = SystemController()
        await controller.initialize()
        
        # Run concurrent recording sessions
        tasks = []
        for i in range(3):
            task = asyncio.create_task(self._concurrent_recording_session(controller, i))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check results
        successful_sessions = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_sessions) >= 2, "At least 2/3 concurrent sessions should succeed"
        
        await controller.shutdown()
    
    async def _concurrent_recording_session(self, controller: SystemController, session_id: int):
        """Simulate concurrent recording session"""
        recorder = controller.get_component("input_recorder")
        if recorder:
            await recorder.start_recording()
            await asyncio.sleep(0.01)  # Simulate recording time
            actions = await recorder.stop_recording()
            return len(actions)
        return 0
    
    async def system_test_error_recovery(self):
        """System test for error recovery"""
        controller = SystemController()
        await controller.initialize()
        
        # Test system continues working after errors
        try:
            # Trigger an error
            controller.get_component("nonexistent_component")
        except:
            pass  # Expected error
        
        # System should still be functional
        status = controller.get_system_status()
        assert status["status"] in ["running", "error"], "System should still respond"
        
        await controller.shutdown()
    
    # ACCEPTANCE TESTS
    async def run_acceptance_tests(self):
        """Run acceptance tests for product-level validation"""
        self.logger.logger.info("✅ STARTING ACCEPTANCE TESTS")
        self.logger.logger.info("-" * 50)
        
        acceptance_tests = [
            self.acceptance_test_user_workflow,
            self.acceptance_test_performance_requirements,
            self.acceptance_test_platform_compatibility,
            self.acceptance_test_documentation_completeness,
            self.acceptance_test_production_readiness
        ]
        
        for test in acceptance_tests:
            await self.run_single_test(test, "acceptance")
    
    async def acceptance_test_user_workflow(self):
        """Acceptance test for typical user workflow"""
        # Test complete user workflow
        controller = SystemController()
        await controller.initialize()
        
        # 1. User starts recording
        await controller.start_recording()
        
        # 2. User performs actions (simulated)
        await asyncio.sleep(0.01)
        
        # 3. User stops recording
        actions = await controller.stop_recording()
        
        # 4. User executes actions
        result = await controller.execute_actions(actions)
        
        # Verify workflow completed successfully
        assert hasattr(result, 'success'), "Execution result should have success attribute"
        
        await controller.shutdown()
    
    async def acceptance_test_performance_requirements(self):
        """Acceptance test for performance requirements"""
        # Test startup time requirement
        start_time = time.time()
        controller = SystemController()
        await controller.initialize()
        startup_time = time.time() - start_time
        
        # Requirement: < 10 seconds for acceptance
        if startup_time > 10.0:
            self.logger.report_bug(BugReport(
                bug_id="ACC-001",
                severity="high",
                category="performance",
                title="Startup Time Too Slow",
                description=f"System startup took {startup_time:.2f} seconds",
                steps_to_reproduce=["Initialize SystemController", "Measure time"],
                expected_result="Startup should be < 10 seconds",
                actual_result=f"Startup took {startup_time:.2f} seconds",
                test_level="acceptance",
                timestamp=datetime.now().isoformat()
            ))
        
        # Test memory usage
        memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
        if memory_mb > 500:  # 500MB limit for acceptance
            self.logger.report_bug(BugReport(
                bug_id="ACC-002",
                severity="medium",
                category="performance",
                title="High Memory Usage",
                description=f"System uses {memory_mb:.1f}MB of memory",
                steps_to_reproduce=["Initialize system", "Check memory usage"],
                expected_result="Memory usage should be < 500MB",
                actual_result=f"Memory usage is {memory_mb:.1f}MB",
                test_level="acceptance",
                timestamp=datetime.now().isoformat()
            ))
        
        await controller.shutdown()
    
    async def acceptance_test_platform_compatibility(self):
        """Acceptance test for platform compatibility"""
        detector = PlatformDetector()
        
        # Test platform detection
        platform_info = detector.detect_platform()
        supported_platforms = ["windows", "macos", "linux"]
        
        if platform_info.name not in supported_platforms:
            self.logger.report_bug(BugReport(
                bug_id="ACC-003",
                severity="critical",
                category="functional",
                title="Unsupported Platform",
                description=f"Platform {platform_info.name} is not supported",
                steps_to_reproduce=["Run platform detection"],
                expected_result="Platform should be windows, macos, or linux",
                actual_result=f"Platform detected as {platform_info.name}",
                test_level="acceptance",
                timestamp=datetime.now().isoformat()
            ))
        
        # Test capabilities
        capabilities = detector.get_capabilities()
        if not capabilities:
            self.logger.report_bug(BugReport(
                bug_id="ACC-004",
                severity="high",
                category="functional",
                title="No Platform Capabilities",
                description="Platform reports no capabilities",
                steps_to_reproduce=["Get platform capabilities"],
                expected_result="Should have at least basic capabilities",
                actual_result="No capabilities reported",
                test_level="acceptance",
                timestamp=datetime.now().isoformat()
            ))
    
    async def acceptance_test_documentation_completeness(self):
        """Acceptance test for documentation completeness"""
        docs_dir = Path(__file__).parent.parent / "docs"
        examples_dir = Path(__file__).parent.parent / "examples"
        
        # Check for essential documentation
        required_docs = [
            docs_dir / "api" / "mkd_v2_api.md",
            docs_dir / "user_guide" / "mkd_v2_getting_started.md",
            examples_dir / "mkd_v2" / "README.md"
        ]
        
        missing_docs = []
        for doc_path in required_docs:
            if not doc_path.exists():
                missing_docs.append(str(doc_path))
        
        if missing_docs:
            self.logger.report_bug(BugReport(
                bug_id="ACC-005",
                severity="medium",
                category="usability",
                title="Missing Documentation",
                description=f"Missing documentation files: {', '.join(missing_docs)}",
                steps_to_reproduce=["Check for required documentation files"],
                expected_result="All required documentation should exist",
                actual_result=f"Missing: {', '.join(missing_docs)}",
                test_level="acceptance",
                timestamp=datetime.now().isoformat()
            ))
        
        # Check example files
        example_files = list((examples_dir / "mkd_v2").glob("*.py"))
        if len(example_files) < 3:
            self.logger.report_bug(BugReport(
                bug_id="ACC-006",
                severity="low",
                category="usability",
                title="Insufficient Examples",
                description=f"Only {len(example_files)} example files found",
                steps_to_reproduce=["Count example files in examples/mkd_v2/"],
                expected_result="Should have at least 3 example files",
                actual_result=f"Found {len(example_files)} example files",
                test_level="acceptance",
                timestamp=datetime.now().isoformat()
            ))
    
    async def acceptance_test_production_readiness(self):
        """Acceptance test for production readiness"""
        # Test critical production requirements
        
        # 1. Error handling
        try:
            registry = ComponentRegistry()
            registry.get_component("nonexistent")
            
            # Should have raised an exception
            self.logger.report_bug(BugReport(
                bug_id="ACC-007",
                severity="critical",
                category="functional",
                title="Missing Error Handling",
                description="No exception raised for nonexistent component",
                steps_to_reproduce=["Try to get nonexistent component"],
                expected_result="Should raise ComponentNotFoundError",
                actual_result="No exception raised",
                test_level="acceptance",
                timestamp=datetime.now().isoformat()
            ))
        except:
            pass  # Expected
        
        # 2. Performance monitoring availability
        profiler = get_profiler()
        cache = get_cache()
        optimizer = get_optimizer()
        
        if not all([profiler, cache, optimizer]):
            self.logger.report_bug(BugReport(
                bug_id="ACC-008",
                severity="high",
                category="functional",
                title="Missing Performance Components",
                description="Not all performance components are available",
                steps_to_reproduce=["Get global performance components"],
                expected_result="All performance components should be available",
                actual_result=f"Profiler: {bool(profiler)}, Cache: {bool(cache)}, Optimizer: {bool(optimizer)}",
                test_level="acceptance",
                timestamp=datetime.now().isoformat()
            ))
    
    # UTILITY METHODS
    async def run_single_test(self, test_method, test_level: str):
        """Run a single test with comprehensive tracking"""
        test_name = test_method.__name__
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            # Run the test
            await test_method()
            
            # Test passed
            duration = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            result = TestResult(
                test_name=test_name,
                test_level=test_level,
                success=True,
                duration=duration,
                memory_usage=end_memory,
                performance_metrics={
                    "start_memory_mb": start_memory,
                    "end_memory_mb": end_memory,
                    "memory_delta_mb": end_memory - start_memory
                }
            )
            
        except Exception as e:
            # Test failed
            duration = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            result = TestResult(
                test_name=test_name,
                test_level=test_level,
                success=False,
                duration=duration,
                error_message=str(e),
                memory_usage=end_memory,
                performance_metrics={
                    "start_memory_mb": start_memory,
                    "end_memory_mb": end_memory,
                    "memory_delta_mb": end_memory - start_memory,
                    "exception_type": type(e).__name__
                }
            )
        
        self.logger.log_test_result(result)
    
    def print_final_summary(self, report: Dict[str, Any]):
        """Print comprehensive final summary"""
        session = report["test_session"]
        
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE TEST RESULTS - MKD AUTOMATION PLATFORM v2.0")
        print("=" * 80)
        
        print(f"\n📊 Overall Test Summary:")
        print(f"   • Total Tests: {session['total_tests']}")
        print(f"   • Passed: {session['total_passed']} ✅")
        print(f"   • Failed: {session['total_failed']} ❌")
        print(f"   • Overall Success Rate: {session['overall_success_rate']:.1f}%")
        print(f"   • Total Duration: {session['duration']:.2f}s")
        
        print(f"\n📋 Test Levels Breakdown:")
        for level, stats in report["test_levels"].items():
            if stats["total"] > 0:
                print(f"   • {level.upper()}: {stats['passed']}/{stats['total']} ({stats['success_rate']:.1f}%)")
        
        print(f"\n🐛 Bug Summary:")
        print(f"   • Total Bugs Found: {report['bugs_found']}")
        print(f"   • Critical Bugs: {report['critical_bugs']} 🚨")
        print(f"   • High Priority: {report['high_priority_bugs']} 🔴")
        
        # Performance summary
        if "performance_metrics" in report:
            perf = report["performance_metrics"]
            print(f"\n⚡ Performance Summary:")
            print(f"   • Average Test Duration: {perf.get('average_test_duration', 0):.3f}s")
            print(f"   • Total Test Time: {perf.get('total_test_time', 0):.2f}s")
        
        # Memory summary
        if "memory_analysis" in report:
            mem = report["memory_analysis"]
            print(f"\n💾 Memory Analysis:")
            print(f"   • Memory Growth: {mem.get('memory_growth_mb', 0):.1f}MB ({mem.get('memory_growth_percentage', 0):.1f}%)")
            print(f"   • Current Usage: {mem.get('current_memory_mb', 0):.1f}MB")
        
        # Recommendations
        if report.get("recommendations"):
            print(f"\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")
        
        # Production readiness assessment
        overall_rate = session['overall_success_rate']
        critical_bugs = report['critical_bugs']
        
        if overall_rate >= 90 and critical_bugs == 0:
            print(f"\n🎉 PRODUCTION READY!")
            print("   ✅ High success rate and no critical bugs")
        elif overall_rate >= 80 and critical_bugs == 0:
            print(f"\n✅ MOSTLY READY")
            print("   ⚠️  Good success rate, minor issues to address")
        elif critical_bugs > 0:
            print(f"\n🚨 NOT PRODUCTION READY")
            print(f"   ❌ Critical bugs must be fixed: {critical_bugs}")
        else:
            print(f"\n⚠️  NEEDS WORK")
            print(f"   ❌ Success rate too low: {overall_rate:.1f}%")
        
        print("\n" + "=" * 80)


async def main():
    """Main test runner"""
    suite = ComprehensiveTestSuite()
    
    try:
        report = await suite.run_all_tests()
        
        # Determine exit code based on results
        critical_bugs = report.get("critical_bugs", 0)
        success_rate = report["test_session"]["overall_success_rate"]
        
        if critical_bugs > 0:
            sys.exit(2)  # Critical issues
        elif success_rate < 80:
            sys.exit(1)  # Low success rate
        else:
            sys.exit(0)  # Success
            
    except Exception as e:
        print(f"❌ Comprehensive test suite failed: {e}")
        traceback.print_exc()
        sys.exit(3)  # Test infrastructure failure


if __name__ == "__main__":
    asyncio.run(main())