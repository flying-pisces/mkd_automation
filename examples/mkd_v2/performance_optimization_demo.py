#!/usr/bin/env python3
"""
Performance Optimization Demo

This example demonstrates MKD v2.0's advanced performance optimization features:
1. Performance profiling
2. Intelligent caching
3. Resource monitoring with alerts
4. Runtime optimization
"""

import asyncio
import logging
import time
import random
from typing import List

from mkd_v2.performance import (
    get_profiler, get_cache, get_optimizer,
    PerformanceProfiler, ProfileType,
    CacheManager, CacheStrategy,
    ResourceMonitor, ResourceType, AlertLevel,
    RuntimeOptimizer, OptimizationStrategy
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceDemo:
    """Demo class showcasing performance optimization features"""
    
    def __init__(self):
        self.profiler = get_profiler()
        self.cache = get_cache()
        self.optimizer = get_optimizer()
        self.resource_monitor = ResourceMonitor()
    
    async def initialize(self):
        """Initialize performance monitoring systems"""
        logger.info("🚀 Initializing performance monitoring...")
        
        # Configure resource monitoring with alerts
        self.resource_monitor.set_threshold(ResourceType.CPU_USAGE, AlertLevel.WARNING, 70.0)
        self.resource_monitor.set_threshold(ResourceType.MEMORY_USAGE, AlertLevel.WARNING, 80.0)
        self.resource_monitor.set_threshold(ResourceType.CPU_USAGE, AlertLevel.CRITICAL, 90.0)
        
        # Add alert callback
        def alert_handler(alert):
            logger.warning(f"🚨 ALERT: {alert.resource_type.value} at {alert.value:.1f}% ({alert.level.value})")
        
        self.resource_monitor.add_alert_callback(alert_handler)
        
        # Start monitoring
        await self.resource_monitor.start_monitoring(interval=2.0)
        
        # Start optimizer
        await self.optimizer.start()
        
        logger.info("✅ Performance monitoring initialized")
    
    async def cleanup(self):
        """Clean up monitoring systems"""
        logger.info("🧹 Cleaning up performance monitoring...")
        await self.resource_monitor.stop_monitoring()
        await self.optimizer.stop()
    
    @get_profiler().profile("expensive_operation", ProfileType.CPU_TIME)
    def expensive_cpu_operation(self, iterations: int = 1000) -> float:
        """Simulate an expensive CPU operation"""
        logger.info(f"🔄 Running expensive CPU operation ({iterations} iterations)...")
        
        total = 0
        for i in range(iterations):
            # Simulate complex computation
            total += sum(j ** 2 for j in range(100))
            
            # Add some randomness to make it more realistic
            if random.random() < 0.01:  # 1% chance
                time.sleep(0.001)  # Small delay
        
        return total / iterations
    
    @get_profiler().profile("memory_intensive_operation", ProfileType.MEMORY_USAGE)
    def memory_intensive_operation(self, size_mb: int = 50) -> List[int]:
        """Simulate a memory-intensive operation"""
        logger.info(f"🧠 Running memory-intensive operation ({size_mb}MB)...")
        
        # Create large data structure
        data_size = (size_mb * 1024 * 1024) // 4  # 4 bytes per int
        large_list = list(range(data_size))
        
        # Process the data
        processed = [x * 2 for x in large_list if x % 1000 == 0]
        
        return processed
    
    def cacheable_operation(self, input_data: str) -> str:
        """Operation that benefits from caching"""
        logger.info(f"💾 Processing cacheable operation: {input_data[:20]}...")
        
        # Simulate expensive processing
        time.sleep(0.5)  # 500ms delay
        
        # Simple "processing" - reverse and uppercase
        result = input_data[::-1].upper()
        return f"PROCESSED: {result}"
    
    async def demonstrate_caching(self):
        """Demonstrate intelligent caching capabilities"""
        logger.info("\n" + "="*50)
        logger.info("📦 CACHING DEMONSTRATION")
        logger.info("="*50)
        
        test_inputs = [
            "hello world",
            "automation testing", 
            "performance optimization",
            "hello world",  # Duplicate - should hit cache
            "caching demo",
            "automation testing"  # Another duplicate
        ]
        
        # Clear any existing cache
        self.cache.clear()
        
        total_time_without_cache = 0
        total_time_with_cache = 0
        
        # Test without cache first
        logger.info("🐌 Running without cache...")
        start_time = time.time()
        for input_data in test_inputs:
            result = self.cacheable_operation(input_data)
        total_time_without_cache = time.time() - start_time
        
        # Now test with cache
        logger.info("🚀 Running with cache...")
        start_time = time.time()
        for input_data in test_inputs:
            result = self.cache.get_or_compute(
                f"cacheable_op:{input_data}",
                lambda: self.cacheable_operation(input_data),
                ttl=300  # Cache for 5 minutes
            )
        total_time_with_cache = time.time() - start_time
        
        # Show results
        cache_stats = self.cache.get_cache_statistics()
        improvement = ((total_time_without_cache - total_time_with_cache) / total_time_without_cache) * 100
        
        logger.info(f"⏱️  Time without cache: {total_time_without_cache:.3f}s")
        logger.info(f"⏱️  Time with cache: {total_time_with_cache:.3f}s")
        logger.info(f"🚀 Performance improvement: {improvement:.1f}%")
        logger.info(f"📊 Cache hit rate: {cache_stats['performance']['hit_rate']:.1f}%")
        logger.info(f"💾 Cache entries: {cache_stats['usage']['current_entries']}")
    
    async def demonstrate_profiling(self):
        """Demonstrate performance profiling capabilities"""
        logger.info("\n" + "="*50)
        logger.info("📊 PROFILING DEMONSTRATION")
        logger.info("="*50)
        
        # Run various operations with profiling
        with self.profiler.profile_context("demo_initialization"):
            await asyncio.sleep(0.1)  # Simulate initialization
        
        # CPU-intensive operation
        result1 = self.expensive_cpu_operation(500)
        
        # Memory-intensive operation  
        result2 = self.memory_intensive_operation(25)
        
        # I/O simulation
        with self.profiler.profile_context("io_simulation", ProfileType.IO_OPERATIONS):
            await asyncio.sleep(0.3)  # Simulate I/O wait
        
        # Get performance analysis
        analysis = self.profiler.analyze_performance(time_window=60.0)
        
        logger.info(f"📈 Performance Analysis Results:")
        logger.info(f"   • Total operations: {analysis.summary['total_operations']}")
        logger.info(f"   • Average duration: {analysis.summary['average_duration']:.3f}s")
        logger.info(f"   • Max duration: {analysis.summary['max_duration']:.3f}s")
        logger.info(f"   • Memory delta: {analysis.summary.get('average_memory_delta', 0):.1f}MB")
        
        # Show top operations by duration
        if 'operations_by_duration' in analysis.summary:
            logger.info("🔝 Top operations by duration:")
            for op, duration in analysis.summary['operations_by_duration'][:3]:
                logger.info(f"     {op}: {duration:.3f}s")
        
        # Show recommendations
        if analysis.recommendations:
            logger.info("💡 Optimization recommendations:")
            for rec in analysis.recommendations:
                logger.info(f"     • {rec}")
    
    async def demonstrate_resource_monitoring(self):
        """Demonstrate resource monitoring and alerting"""
        logger.info("\n" + "="*50)
        logger.info("📡 RESOURCE MONITORING DEMONSTRATION")
        logger.info("="*50)
        
        # Get current metrics
        metrics = self.resource_monitor.get_current_metrics()
        if metrics:
            logger.info("📊 Current Resource Usage:")
            logger.info(f"   • CPU: {metrics.cpu_usage:.1f}%")
            logger.info(f"   • Memory: {metrics.memory_usage:.1f}%")
            logger.info(f"   • Disk: {metrics.disk_usage:.1f}%")
        
        # Simulate resource-intensive operations to trigger alerts
        logger.info("🔥 Running resource-intensive operations...")
        
        # This should trigger some resource usage
        tasks = []
        for i in range(3):
            task = asyncio.create_task(self.stress_test_operation(i))
            tasks.append(task)
        
        # Wait for operations to complete
        await asyncio.gather(*tasks)
        
        # Show resource history
        cpu_history = self.resource_monitor.get_resource_history(ResourceType.CPU_USAGE, 30.0)
        memory_history = self.resource_monitor.get_resource_history(ResourceType.MEMORY_USAGE, 30.0)
        
        if cpu_history:
            avg_cpu = sum(cpu_history) / len(cpu_history)
            max_cpu = max(cpu_history)
            logger.info(f"📈 CPU Usage (last 30s): avg={avg_cpu:.1f}%, max={max_cpu:.1f}%")
        
        if memory_history:
            avg_mem = sum(memory_history) / len(memory_history)
            max_mem = max(memory_history)
            logger.info(f"📈 Memory Usage (last 30s): avg={avg_mem:.1f}%, max={max_mem:.1f}%")
    
    async def stress_test_operation(self, worker_id: int):
        """Stress test operation to demonstrate resource monitoring"""
        logger.info(f"⚡ Worker {worker_id} starting stress test...")
        
        # CPU stress
        total = 0
        for i in range(10000):
            total += i ** 2
            if i % 1000 == 0:
                await asyncio.sleep(0.001)  # Small yield
        
        # Memory stress
        large_data = [random.random() for _ in range(100000)]
        processed = sum(large_data)
        
        logger.info(f"✅ Worker {worker_id} completed stress test")
        return processed
    
    async def demonstrate_runtime_optimization(self):
        """Demonstrate runtime optimization capabilities"""
        logger.info("\n" + "="*50)
        logger.info("🎯 RUNTIME OPTIMIZATION DEMONSTRATION")
        logger.info("="*50)
        
        # The optimizer runs automatically, but we can get a report
        report = self.optimizer.get_optimization_report()
        
        logger.info("🔧 Optimizer Status:")
        logger.info(f"   • Strategy: {report['configuration']['strategy']}")
        logger.info(f"   • Auto-optimization: {report['configuration']['enable_auto_optimization']}")
        logger.info(f"   • Active optimizations: {len(report['active_optimizations'])}")
        logger.info(f"   • Total optimizations: {report['statistics']['total_optimizations']}")
        logger.info(f"   • Success rate: {report['statistics']['successful_optimizations']}/{report['statistics']['total_optimizations']}")
        
        # Show available optimization rules
        logger.info("📋 Available optimization rules:")
        for rule_name, rule_info in report['rules'].items():
            status = "✅ enabled" if rule_info['enabled'] else "❌ disabled"
            logger.info(f"     • {rule_name} ({rule_info['target']}) - {status}")
        
        # Trigger a manual optimization cycle
        logger.info("🔄 Running manual optimization cycle...")
        
        # Create some load to potentially trigger optimizations
        for i in range(5):
            self.expensive_cpu_operation(200)
            await asyncio.sleep(0.1)
        
        # Note: In a real scenario, the optimizer would detect patterns and apply optimizations
        logger.info("✅ Manual optimization cycle completed")


async def main():
    """Main demo function"""
    print("MKD Automation Platform v2.0 - Performance Optimization Demo")
    print("=" * 70)
    
    demo = PerformanceDemo()
    
    try:
        # Initialize performance monitoring
        await demo.initialize()
        
        # Give system a moment to start monitoring
        await asyncio.sleep(2)
        
        # Run demonstrations
        await demo.demonstrate_caching()
        await demo.demonstrate_profiling()
        await demo.demonstrate_resource_monitoring()
        await demo.demonstrate_runtime_optimization()
        
        # Final system metrics
        print("\n" + "="*50)
        print("📊 FINAL SYSTEM METRICS")
        print("="*50)
        
        # Cache statistics
        cache_stats = demo.cache.get_cache_statistics()
        print(f"💾 Cache Performance:")
        print(f"   • Hit rate: {cache_stats['performance']['hit_rate']:.1f}%")
        print(f"   • Total requests: {cache_stats['performance']['total_requests']}")
        print(f"   • Memory usage: {cache_stats['usage']['memory_usage_mb']:.1f}MB")
        
        # Profiler statistics  
        profiler_stats = demo.profiler.get_profiler_statistics()
        print(f"📊 Profiler Statistics:")
        print(f"   • Total profiles: {profiler_stats['statistics']['total_profiles']}")
        print(f"   • Total duration: {profiler_stats['statistics']['total_duration']:.3f}s")
        
        print("\n🎉 Performance optimization demo completed successfully!")
        print("Key takeaways:")
        print("  • Caching can dramatically improve performance for repeated operations")
        print("  • Profiling helps identify bottlenecks and optimization opportunities")
        print("  • Resource monitoring enables proactive system management")
        print("  • Runtime optimization can automatically improve system performance")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        await demo.cleanup()


if __name__ == "__main__":
    asyncio.run(main())