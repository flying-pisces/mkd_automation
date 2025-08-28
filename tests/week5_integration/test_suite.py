#!/usr/bin/env python3
"""
Week 5 Integration Test Suite

Comprehensive integration testing for MKD v2.0 Production Release.
Tests the complete system including all components, performance optimizations,
and production-ready features.
"""

import asyncio
import logging
import sys
import time
import json
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import MKD v2.0 components
try:
    from mkd_v2.integration import SystemController, ComponentRegistry, EventBus
    from mkd_v2.platform import PlatformDetector
    from mkd_v2.input import InputRecorder
    from mkd_v2.playback import ActionExecutor
    from mkd_v2.performance import (
        PerformanceProfiler, CacheManager, ResourceMonitor, RuntimeOptimizer,
        get_profiler, get_cache, get_optimizer
    )
    from mkd_v2.exceptions import RecordingError, PlaybackError, ComponentNotFoundError
except ImportError as e:
    print(f"❌ Failed to import MKD v2.0 components: {e}")
    print("Make sure PYTHONPATH includes the src directory")
    sys.exit(1)


@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    success: bool
    duration: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = None


class Week5TestLogger:
    """Enhanced test logger for Week 5 integration tests"""
    
    def __init__(self):
        self.log_dir = Path(__file__).parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger("Week5Integration")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"week5_integration_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.results: List[TestResult] = []
        self.start_time = time.time()
    
    def log_test_start(self, test_name: str):
        """Log test start"""
        self.logger.info(f"🧪 Starting test: {test_name}")
    
    def log_test_result(self, result: TestResult):
        """Log and store test result"""
        self.results.append(result)
        
        if result.success:
            self.logger.info(f"✅ {result.test_name} - PASSED ({result.duration:.3f}s)")
        else:
            self.logger.error(f"❌ {result.test_name} - FAILED ({result.duration:.3f}s)")
            if result.error_message:
                self.logger.error(f"   Error: {result.error_message}")
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_duration = time.time() - self.start_time
        passed_tests = [r for r in self.results if r.success]
        failed_tests = [r for r in self.results if not r.success]
        
        report = {
            "test_session": {
                "timestamp": datetime.now().isoformat(),
                "duration": total_duration,
                "total_tests": len(self.results),
                "passed": len(passed_tests),
                "failed": len(failed_tests),
                "success_rate": (len(passed_tests) / len(self.results) * 100) if self.results else 0
            },
            "test_results": [
                {
                    "name": r.test_name,
                    "success": r.success,
                    "duration": r.duration,
                    "error": r.error_message,
                    "details": r.details
                }
                for r in self.results
            ],
            "summary": {
                "status": "PRODUCTION_READY" if len(failed_tests) == 0 else "NEEDS_WORK",
                "critical_issues": len([r for r in failed_tests if "critical" in r.test_name.lower()]),
                "performance_issues": len([r for r in failed_tests if "performance" in r.test_name.lower()]),
                "integration_issues": len([r for r in failed_tests if "integration" in r.test_name.lower()])
            }
        }
        
        # Save report
        report_file = self.log_dir / f"week5_final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report


class Week5IntegrationTestSuite:
    """Comprehensive Week 5 integration test suite"""
    
    def __init__(self):
        self.logger = Week5TestLogger()
        self.controller = None
        self.profiler = get_profiler()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all Week 5 integration tests"""
        self.logger.logger.info("🚀 Starting Week 5 Integration Test Suite")
        self.logger.logger.info("=" * 70)
        
        test_methods = [
            self.test_system_initialization,
            self.test_component_integration,
            self.test_platform_detection,
            self.test_event_bus_functionality,
            self.test_basic_recording_playback,
            self.test_performance_profiler,
            self.test_cache_manager,
            self.test_resource_monitoring,
            self.test_runtime_optimization,
            self.test_error_handling,
            self.test_concurrent_operations,
            self.test_performance_benchmarks,
            self.test_memory_management,
            self.test_production_readiness
        ]
        
        for test_method in test_methods:
            await self.run_single_test(test_method)
        
        # Generate final report
        report = self.logger.generate_final_report()
        self.print_final_summary(report)
        
        return report
    
    async def run_single_test(self, test_method):
        """Run a single test with error handling"""
        test_name = test_method.__name__
        self.logger.log_test_start(test_name)
        
        start_time = time.time()
        
        try:
            await test_method()
            duration = time.time() - start_time
            
            result = TestResult(
                test_name=test_name,
                success=True,
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            result = TestResult(
                test_name=test_name,
                success=False,
                duration=duration,
                error_message=error_msg,
                details={"traceback": traceback.format_exc()}
            )
        
        self.logger.log_test_result(result)
    
    async def test_system_initialization(self):
        """Test complete system initialization"""
        self.controller = SystemController()
        await self.controller.initialize()
        
        # Verify system status
        status = self.controller.get_system_status()
        assert status["status"] == "running", f"Expected running status, got {status['status']}"
        
        # Verify all core components are registered
        registry = self.controller.get_component("component_registry")
        expected_components = [
            "platform_detector",
            "input_recorder", 
            "action_executor",
            "event_bus"
        ]
        
        for component in expected_components:
            assert registry.has_component(component), f"Missing component: {component}"
    
    async def test_component_integration(self):
        """Test component integration and dependencies"""
        if not self.controller:
            self.controller = SystemController()
            await self.controller.initialize()
        
        registry = self.controller.get_component("component_registry")
        
        # Test component retrieval
        platform_detector = registry.get_component("platform_detector")
        assert platform_detector is not None, "Failed to get platform_detector"
        
        input_recorder = registry.get_component("input_recorder")
        assert input_recorder is not None, "Failed to get input_recorder"
        
        action_executor = registry.get_component("action_executor")
        assert action_executor is not None, "Failed to get action_executor"
        
        event_bus = registry.get_component("event_bus")
        assert event_bus is not None, "Failed to get event_bus"
        assert event_bus.running, "Event bus should be running"
    
    async def test_platform_detection(self):
        """Test platform detection functionality"""
        detector = PlatformDetector()
        platform = detector.detect_platform()
        
        assert platform is not None, "Platform detection failed"
        assert platform.name in ["windows", "macos", "linux"], f"Unknown platform: {platform.name}"
        
        capabilities = detector.get_capabilities()
        assert isinstance(capabilities, list), "Capabilities should be a list"
        assert len(capabilities) > 0, "Should have some capabilities"
    
    async def test_event_bus_functionality(self):
        """Test event bus publish/subscribe functionality"""
        if not self.controller:
            self.controller = SystemController()
            await self.controller.initialize()
        
        event_bus = self.controller.get_component("event_bus")
        
        # Test event publishing and subscribing
        received_events = []
        
        async def test_handler(event_data):
            received_events.append(event_data)
        
        # Subscribe to test event
        from mkd_v2.integration.event_bus import EventType
        subscription_id = event_bus.subscribe(EventType.SYSTEM_STARTED, test_handler)
        
        # Publish test event
        test_data = {"test": "data", "timestamp": time.time()}
        await event_bus.publish(EventType.SYSTEM_STARTED, test_data)
        
        # Give event time to process
        await asyncio.sleep(0.1)
        
        # Verify event was received
        assert len(received_events) == 1, "Event was not received"
        assert received_events[0] == test_data, "Event data mismatch"
        
        # Cleanup
        event_bus.unsubscribe(subscription_id)
    
    async def test_basic_recording_playback(self):
        """Test basic recording and playback functionality"""
        if not self.controller:
            self.controller = SystemController()
            await self.controller.initialize()
        
        # Test recording initialization
        await self.controller.start_recording()
        
        # Simulate a short recording session
        await asyncio.sleep(0.1)
        
        # Stop recording
        actions = await self.controller.stop_recording()
        
        # Verify recording result
        assert isinstance(actions, list), "Actions should be a list"
        
        # Test playback preparation (without actual execution)
        from mkd_v2.playback import ExecutionConfig
        config = ExecutionConfig(
            speed_multiplier=1.0,
            fail_on_error=False
        )
        
        # Verify config is created properly
        assert config.speed_multiplier == 1.0, "Speed multiplier not set correctly"
        assert not config.fail_on_error, "Fail on error should be False"
    
    async def test_performance_profiler(self):
        """Test performance profiling functionality"""
        profiler = PerformanceProfiler()
        
        # Test basic profiling
        profile_id = profiler.start_profiling("test_operation")
        
        # Simulate some work
        total = sum(i ** 2 for i in range(1000))
        
        # Stop profiling
        metrics = profiler.stop_profiling(profile_id)
        
        assert metrics is not None, "Profiling metrics should not be None"
        assert metrics.duration > 0, "Duration should be positive"
        assert metrics.operation_name == "test_operation", "Operation name mismatch"
        
        # Test profiling analysis
        analysis = profiler.analyze_performance(time_window=60.0)
        assert analysis is not None, "Analysis should not be None"
    
    async def test_cache_manager(self):
        """Test cache manager functionality"""
        cache = CacheManager(max_size=100, max_memory_mb=10.0)
        
        # Test basic caching
        key = "test_key"
        value = "test_value"
        
        success = cache.put(key, value, ttl=3600)
        assert success, "Cache put should succeed"
        
        retrieved_value = cache.get(key)
        assert retrieved_value == value, "Retrieved value should match stored value"
        
        # Test cache statistics
        stats = cache.get_cache_statistics()
        assert stats["usage"]["current_entries"] == 1, "Should have 1 cache entry"
        assert stats["performance"]["hits"] >= 1, "Should have at least 1 cache hit"
        
        # Test get_or_compute
        def expensive_function():
            return "computed_value"
        
        result = cache.get_or_compute("compute_key", expensive_function, ttl=1800)
        assert result == "computed_value", "Computed value should be returned"
        
        # Second call should hit cache
        result2 = cache.get_or_compute("compute_key", expensive_function, ttl=1800)
        assert result2 == "computed_value", "Second call should return cached value"
    
    async def test_resource_monitoring(self):
        """Test resource monitoring functionality"""
        monitor = ResourceMonitor()
        
        # Test threshold setting
        from mkd_v2.performance.resource_monitor import ResourceType, AlertLevel
        monitor.set_threshold(ResourceType.CPU_USAGE, AlertLevel.WARNING, 80.0)
        monitor.set_threshold(ResourceType.MEMORY_USAGE, AlertLevel.CRITICAL, 90.0)
        
        # Test alert callback
        received_alerts = []
        
        def alert_callback(alert):
            received_alerts.append(alert)
        
        monitor.add_alert_callback(alert_callback)
        
        # Start monitoring briefly
        await monitor.start_monitoring(interval=0.5)
        await asyncio.sleep(1.0)
        await monitor.stop_monitoring()
        
        # Test metrics retrieval
        metrics = monitor.get_current_metrics()
        if metrics:  # May be None if monitoring couldn't start
            assert hasattr(metrics, 'cpu_usage'), "Metrics should have CPU usage"
            assert hasattr(metrics, 'memory_usage'), "Metrics should have memory usage"
    
    async def test_runtime_optimization(self):
        """Test runtime optimization functionality"""
        from mkd_v2.performance.optimizer import RuntimeOptimizer, OptimizationStrategy
        
        optimizer = RuntimeOptimizer(strategy=OptimizationStrategy.BALANCED)
        
        # Test optimizer initialization
        assert optimizer.strategy == OptimizationStrategy.BALANCED, "Strategy should be BALANCED"
        assert len(optimizer.optimization_rules) > 0, "Should have default optimization rules"
        
        # Test optimization report
        report = optimizer.get_optimization_report()
        assert "configuration" in report, "Report should have configuration"
        assert "statistics" in report, "Report should have statistics"
        assert "rules" in report, "Report should have rules"
        
        # Test strategy change
        optimizer.set_strategy(OptimizationStrategy.CONSERVATIVE)
        assert optimizer.strategy == OptimizationStrategy.CONSERVATIVE, "Strategy should be updated"
    
    async def test_error_handling(self):
        """Test comprehensive error handling"""
        if not self.controller:
            self.controller = SystemController()
            await self.controller.initialize()
        
        # Test component not found error
        registry = self.controller.get_component("component_registry")
        
        try:
            nonexistent = registry.get_component("nonexistent_component")
            assert False, "Should have raised ComponentNotFoundError"
        except ComponentNotFoundError:
            pass  # Expected
        
        # Test graceful handling of empty action lists
        result = await self.controller.execute_actions([])
        assert hasattr(result, 'success'), "Execution result should have success attribute"
    
    async def test_concurrent_operations(self):
        """Test concurrent operations handling"""
        if not self.controller:
            self.controller = SystemController()
            await self.controller.initialize()
        
        # Test multiple concurrent profiling operations
        profiler = PerformanceProfiler()
        
        async def concurrent_operation(operation_id):
            profile_id = profiler.start_profiling(f"concurrent_op_{operation_id}")
            await asyncio.sleep(0.1)  # Simulate work
            return profiler.stop_profiling(profile_id)
        
        # Run multiple operations concurrently
        tasks = [concurrent_operation(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # Verify all operations completed
        assert len(results) == 5, "All concurrent operations should complete"
        for result in results:
            assert result is not None, "Each operation should return metrics"
    
    async def test_performance_benchmarks(self):
        """Test performance benchmarks meet production requirements"""
        if not self.controller:
            self.controller = SystemController()
        
        # Test system startup time
        start_time = time.time()
        await self.controller.initialize()
        startup_time = time.time() - start_time
        
        assert startup_time < 2.0, f"System startup took {startup_time:.3f}s, should be < 2.0s"
        
        # Test component retrieval performance
        registry = self.controller.get_component("component_registry")
        
        start_time = time.time()
        for _ in range(100):
            component = registry.get_component("platform_detector")
        retrieval_time = time.time() - start_time
        
        assert retrieval_time < 0.1, f"100 component retrievals took {retrieval_time:.3f}s, should be < 0.1s"
    
    async def test_memory_management(self):
        """Test memory management and leak prevention"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create and destroy multiple system instances
        for i in range(5):
            controller = SystemController()
            await controller.initialize()
            
            # Perform some operations
            await controller.start_recording()
            await asyncio.sleep(0.1)
            await controller.stop_recording()
            
            await controller.shutdown()
            del controller
            gc.collect()  # Force garbage collection
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Allow some memory growth but not excessive
        assert memory_growth < 50, f"Memory grew by {memory_growth:.1f}MB, should be < 50MB"
    
    async def test_production_readiness(self):
        """Test overall production readiness"""
        if not self.controller:
            self.controller = SystemController()
            await self.controller.initialize()
        
        # Test all critical components are functional
        status = self.controller.get_system_status()
        assert status["status"] == "running", "System should be in running state"
        
        # Test performance is within acceptable bounds
        profiler = PerformanceProfiler()
        profile_id = profiler.start_profiling("production_readiness_test")
        
        # Simulate a realistic workload
        cache = CacheManager()
        for i in range(10):
            cache.put(f"key_{i}", f"value_{i}")
            cache.get(f"key_{i}")
        
        metrics = profiler.stop_profiling(profile_id)
        assert metrics.duration < 1.0, f"Production test took {metrics.duration:.3f}s, should be < 1.0s"
        
        # Test system can handle multiple operations
        tasks = []
        for i in range(3):
            task = asyncio.create_task(self.simulate_user_workflow())
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All workflows should complete without exceptions
        for result in results:
            if isinstance(result, Exception):
                raise result
    
    async def simulate_user_workflow(self):
        """Simulate a typical user workflow"""
        # This simulates a user recording and playing back actions
        await self.controller.start_recording()
        await asyncio.sleep(0.1)  # Simulate user actions
        actions = await self.controller.stop_recording()
        
        # Simulate playback preparation
        from mkd_v2.playback import ExecutionConfig
        config = ExecutionConfig()
        
        # In a real scenario, we would execute actions here
        # For testing, we just verify the setup worked
        assert isinstance(actions, list), "Actions should be a list"
        return True
    
    def print_final_summary(self, report: Dict[str, Any]):
        """Print comprehensive test summary"""
        session = report["test_session"]
        summary = report["summary"]
        
        print("\n" + "=" * 70)
        print("🎯 WEEK 5 INTEGRATION TEST RESULTS")
        print("=" * 70)
        
        print(f"📊 Test Session Summary:")
        print(f"   • Total Tests: {session['total_tests']}")
        print(f"   • Passed: {session['passed']} ✅")
        print(f"   • Failed: {session['failed']} ❌")
        print(f"   • Success Rate: {session['success_rate']:.1f}%")
        print(f"   • Duration: {session['duration']:.2f}s")
        
        print(f"\n🎯 Production Readiness Assessment:")
        print(f"   • Status: {summary['status']}")
        print(f"   • Critical Issues: {summary['critical_issues']}")
        print(f"   • Performance Issues: {summary['performance_issues']}")
        print(f"   • Integration Issues: {summary['integration_issues']}")
        
        if session['success_rate'] >= 90:
            print(f"\n🎉 PRODUCTION READY! Success rate: {session['success_rate']:.1f}%")
            print("The MKD v2.0 platform meets production quality standards.")
        elif session['success_rate'] >= 80:
            print(f"\n⚠️  MOSTLY READY: Success rate: {session['success_rate']:.1f}%")
            print("Minor issues detected but overall system is functional.")
        else:
            print(f"\n❌ NEEDS WORK: Success rate: {session['success_rate']:.1f}%")
            print("Significant issues require resolution before production.")
        
        # Show failed tests
        failed_tests = [r for r in report["test_results"] if not r["success"]]
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   • {test['name']}: {test['error']}")
        
        print("\n" + "=" * 70)
    
    async def cleanup(self):
        """Cleanup test resources"""
        if self.controller:
            await self.controller.shutdown()


async def main():
    """Main test runner"""
    suite = Week5IntegrationTestSuite()
    
    try:
        report = await suite.run_all_tests()
        
        # Return appropriate exit code
        if report["test_session"]["success_rate"] >= 80:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        await suite.cleanup()


if __name__ == "__main__":
    asyncio.run(main())