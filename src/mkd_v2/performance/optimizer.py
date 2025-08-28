"""
Runtime Optimizer

Advanced runtime optimization system that dynamically optimizes system
performance based on real-time metrics and usage patterns.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum
import json
import threading
from collections import defaultdict, deque

from .profiler import PerformanceProfiler, ProfileType
from .cache_manager import CacheManager, CacheStrategy
from .resource_monitor import ResourceMonitor, AlertLevel

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Optimization strategies"""
    CONSERVATIVE = "conservative"    # Minimal optimizations
    BALANCED = "balanced"           # Balanced approach
    AGGRESSIVE = "aggressive"       # Maximum optimizations
    ADAPTIVE = "adaptive"          # Adapt based on conditions


class OptimizationTarget(Enum):
    """Optimization targets"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    RESOURCE_EFFICIENCY = "resource_efficiency"


@dataclass
class OptimizationRule:
    """Rules for optimization decisions"""
    name: str
    target: OptimizationTarget
    condition: Callable[[Dict[str, Any]], bool]
    action: Callable[[Dict[str, Any]], Any]
    priority: int = 1
    cooldown_seconds: float = 60.0
    last_applied: float = 0.0
    enabled: bool = True


@dataclass
class OptimizationResult:
    """Result of an optimization operation"""
    rule_name: str
    target: OptimizationTarget
    applied: bool
    improvement: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class RuntimeOptimizer:
    """Advanced runtime optimizer for dynamic performance tuning"""
    
    def __init__(self, strategy: OptimizationStrategy = OptimizationStrategy.BALANCED):
        self.strategy = strategy
        
        # Core components
        self.profiler = PerformanceProfiler()
        self.cache_manager = CacheManager()
        self.resource_monitor = ResourceMonitor()
        
        # Optimization state
        self.optimization_rules: Dict[str, OptimizationRule] = {}
        self.optimization_history: deque = deque(maxlen=1000)
        self.active_optimizations: Set[str] = set()
        
        # Configuration
        self.config = {
            "optimization_interval": 30.0,  # seconds
            "min_data_points": 10,          # minimum metrics before optimizing
            "max_concurrent_optimizations": 3,
            "enable_auto_optimization": True,
            "performance_baseline": {},      # baseline performance metrics
            "target_improvements": {         # target improvement percentages
                "cpu_usage": 10.0,
                "memory_usage": 15.0,
                "response_time": 20.0
            }
        }
        
        # Statistics
        self.stats = {
            "total_optimizations": 0,
            "successful_optimizations": 0,
            "failed_optimizations": 0,
            "total_improvement": 0.0,
            "optimization_sessions": 0,
            "last_optimization": 0.0
        }
        
        # Threading
        self.lock = threading.RLock()
        self.optimization_task: Optional[asyncio.Task] = None
        self.running = False
        
        # Initialize default rules
        self._initialize_default_rules()
        
        logger.info(f"RuntimeOptimizer initialized with strategy: {strategy.value}")
    
    def _initialize_default_rules(self) -> None:
        """Initialize default optimization rules"""
        
        # Memory optimization rules
        self.add_optimization_rule(OptimizationRule(
            name="high_memory_cache_cleanup",
            target=OptimizationTarget.MEMORY_USAGE,
            condition=lambda metrics: metrics.get("memory_percent", 0) > 80,
            action=self._cleanup_cache,
            priority=1,
            cooldown_seconds=120.0
        ))
        
        self.add_optimization_rule(OptimizationRule(
            name="adaptive_cache_strategy",
            target=OptimizationTarget.MEMORY_USAGE,
            condition=lambda metrics: metrics.get("memory_percent", 0) > 60,
            action=self._optimize_cache_strategy,
            priority=2,
            cooldown_seconds=300.0
        ))
        
        # CPU optimization rules
        self.add_optimization_rule(OptimizationRule(
            name="high_cpu_throttling",
            target=OptimizationTarget.CPU_USAGE,
            condition=lambda metrics: metrics.get("cpu_percent", 0) > 85,
            action=self._throttle_operations,
            priority=1,
            cooldown_seconds=60.0
        ))
        
        self.add_optimization_rule(OptimizationRule(
            name="async_optimization",
            target=OptimizationTarget.THROUGHPUT,
            condition=lambda metrics: metrics.get("average_response_time", 0) > 1.0,
            action=self._optimize_async_operations,
            priority=3,
            cooldown_seconds=600.0
        ))
        
        # Response time optimization
        self.add_optimization_rule(OptimizationRule(
            name="slow_operation_caching",
            target=OptimizationTarget.RESPONSE_TIME,
            condition=lambda metrics: len(metrics.get("slow_operations", [])) > 0,
            action=self._cache_slow_operations,
            priority=2,
            cooldown_seconds=180.0
        ))
    
    def add_optimization_rule(self, rule: OptimizationRule) -> None:
        """Add an optimization rule"""
        with self.lock:
            self.optimization_rules[rule.name] = rule
            logger.debug(f"Added optimization rule: {rule.name}")
    
    def remove_optimization_rule(self, rule_name: str) -> bool:
        """Remove an optimization rule"""
        with self.lock:
            if rule_name in self.optimization_rules:
                del self.optimization_rules[rule_name]
                logger.debug(f"Removed optimization rule: {rule_name}")
                return True
            return False
    
    def enable_rule(self, rule_name: str) -> bool:
        """Enable an optimization rule"""
        with self.lock:
            if rule_name in self.optimization_rules:
                self.optimization_rules[rule_name].enabled = True
                return True
            return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """Disable an optimization rule"""
        with self.lock:
            if rule_name in self.optimization_rules:
                self.optimization_rules[rule_name].enabled = False
                return True
            return False
    
    async def start(self) -> None:
        """Start the runtime optimizer"""
        if self.running:
            logger.warning("RuntimeOptimizer is already running")
            return
        
        self.running = True
        
        # Start component systems
        await self.resource_monitor.start_monitoring()
        
        # Start optimization loop if enabled
        if self.config["enable_auto_optimization"]:
            self.optimization_task = asyncio.create_task(self._optimization_loop())
        
        logger.info("RuntimeOptimizer started")
    
    async def stop(self) -> None:
        """Stop the runtime optimizer"""
        if not self.running:
            return
        
        self.running = False
        
        # Stop optimization loop
        if self.optimization_task and not self.optimization_task.done():
            self.optimization_task.cancel()
            try:
                await self.optimization_task
            except asyncio.CancelledError:
                pass
        
        # Stop component systems
        await self.resource_monitor.stop_monitoring()
        
        logger.info("RuntimeOptimizer stopped")
    
    async def _optimization_loop(self) -> None:
        """Main optimization loop"""
        while self.running:
            try:
                await self._run_optimization_cycle()
                await asyncio.sleep(self.config["optimization_interval"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(self.config["optimization_interval"])
    
    async def _run_optimization_cycle(self) -> List[OptimizationResult]:
        """Run a complete optimization cycle"""
        
        # Collect current metrics
        metrics = await self._collect_metrics()
        
        # Check if we have enough data
        if len(metrics.get("profiles", [])) < self.config["min_data_points"]:
            logger.debug("Insufficient data for optimization")
            return []
        
        # Analyze and apply optimizations
        results = await self._analyze_and_optimize(metrics)
        
        # Update statistics
        self.stats["optimization_sessions"] += 1
        self.stats["last_optimization"] = time.time()
        
        if results:
            logger.info(f"Optimization cycle completed: {len(results)} optimizations applied")
        
        return results
    
    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive performance metrics"""
        
        # System metrics
        system_metrics = self.resource_monitor.get_current_metrics()
        
        # Profiler metrics
        profiler_analysis = self.profiler.analyze_performance(time_window=300.0)
        
        # Cache metrics
        cache_stats = self.cache_manager.get_cache_statistics()
        
        # Combine all metrics
        metrics = {
            "timestamp": time.time(),
            "system": system_metrics,
            "profiles": profiler_analysis.metrics,
            "cache": cache_stats,
            "summary": profiler_analysis.summary,
            "recommendations": profiler_analysis.recommendations
        }
        
        # Extract key performance indicators
        if system_metrics and "process" in system_metrics:
            metrics["memory_percent"] = system_metrics["process"].get("memory_percent", 0)
            metrics["cpu_percent"] = system_metrics["process"].get("cpu_percent", 0)
        
        if profiler_analysis.summary:
            metrics["average_response_time"] = profiler_analysis.summary.get("average_duration", 0)
            metrics["slow_operations"] = [
                op for op, duration in profiler_analysis.summary.get("operations_by_duration", [])
                if duration > 0.1  # > 100ms
            ][:5]
        
        return metrics
    
    async def _analyze_and_optimize(self, metrics: Dict[str, Any]) -> List[OptimizationResult]:
        """Analyze metrics and apply optimizations"""
        
        results = []
        current_time = time.time()
        
        # Check if we're at max concurrent optimizations
        if len(self.active_optimizations) >= self.config["max_concurrent_optimizations"]:
            logger.debug("Max concurrent optimizations reached")
            return results
        
        # Sort rules by priority
        sorted_rules = sorted(
            [(name, rule) for name, rule in self.optimization_rules.items() if rule.enabled],
            key=lambda x: x[1].priority
        )
        
        for rule_name, rule in sorted_rules:
            try:
                # Check cooldown
                if current_time - rule.last_applied < rule.cooldown_seconds:
                    continue
                
                # Check condition
                if not rule.condition(metrics):
                    continue
                
                # Apply optimization
                self.active_optimizations.add(rule_name)
                try:
                    logger.info(f"Applying optimization rule: {rule_name}")
                    
                    # Measure before state
                    before_metrics = await self._collect_metrics()
                    
                    # Apply the optimization
                    optimization_data = await self._execute_optimization(rule, metrics)
                    
                    # Measure after state (brief delay to see effect)
                    await asyncio.sleep(5.0)
                    after_metrics = await self._collect_metrics()
                    
                    # Calculate improvement
                    improvement = self._calculate_improvement(
                        before_metrics, after_metrics, rule.target
                    )
                    
                    # Create result
                    result = OptimizationResult(
                        rule_name=rule_name,
                        target=rule.target,
                        applied=True,
                        improvement=improvement,
                        metadata=optimization_data
                    )
                    
                    results.append(result)
                    self.optimization_history.append(result)
                    
                    # Update rule state
                    rule.last_applied = current_time
                    
                    # Update statistics
                    self.stats["total_optimizations"] += 1
                    if improvement and improvement > 0:
                        self.stats["successful_optimizations"] += 1
                        self.stats["total_improvement"] += improvement
                    else:
                        self.stats["failed_optimizations"] += 1
                    
                    logger.info(f"Optimization {rule_name} applied with {improvement:.1f}% improvement")
                    
                finally:
                    self.active_optimizations.discard(rule_name)
                
            except Exception as e:
                logger.error(f"Failed to apply optimization {rule_name}: {e}")
                self.active_optimizations.discard(rule_name)
                
                result = OptimizationResult(
                    rule_name=rule_name,
                    target=rule.target,
                    applied=False,
                    metadata={"error": str(e)}
                )
                results.append(result)
                self.optimization_history.append(result)
        
        return results
    
    async def _execute_optimization(self, rule: OptimizationRule, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an optimization rule"""
        
        if asyncio.iscoroutinefunction(rule.action):
            return await rule.action(metrics)
        else:
            return rule.action(metrics)
    
    def _calculate_improvement(self, before: Dict[str, Any], after: Dict[str, Any], 
                             target: OptimizationTarget) -> Optional[float]:
        """Calculate improvement percentage for a target metric"""
        
        try:
            if target == OptimizationTarget.MEMORY_USAGE:
                before_val = before.get("memory_percent", 0)
                after_val = after.get("memory_percent", 0)
                if before_val > 0:
                    return ((before_val - after_val) / before_val) * 100
                    
            elif target == OptimizationTarget.CPU_USAGE:
                before_val = before.get("cpu_percent", 0)
                after_val = after.get("cpu_percent", 0)
                if before_val > 0:
                    return ((before_val - after_val) / before_val) * 100
                    
            elif target == OptimizationTarget.RESPONSE_TIME:
                before_val = before.get("average_response_time", 0)
                after_val = after.get("average_response_time", 0)
                if before_val > 0:
                    return ((before_val - after_val) / before_val) * 100
                    
        except Exception as e:
            logger.error(f"Failed to calculate improvement: {e}")
        
        return None
    
    # Optimization action methods
    
    def _cleanup_cache(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up cache to free memory"""
        
        initial_entries = len(self.cache_manager.cache)
        initial_memory = self.cache_manager.memory_usage
        
        # Clean expired entries first
        expired_count = self.cache_manager.cleanup_expired()
        
        # If still high memory usage, reduce cache size
        if self.cache_manager.memory_usage > self.cache_manager.max_memory_bytes * 0.7:
            # Reduce max size temporarily
            original_max_size = self.cache_manager.max_size
            self.cache_manager.max_size = max(100, int(self.cache_manager.max_size * 0.7))
            
            # Force eviction to new size
            while len(self.cache_manager.cache) > self.cache_manager.max_size:
                self.cache_manager._evict_entry()
        
        final_entries = len(self.cache_manager.cache)
        final_memory = self.cache_manager.memory_usage
        
        return {
            "expired_cleaned": expired_count,
            "entries_before": initial_entries,
            "entries_after": final_entries,
            "memory_freed": initial_memory - final_memory
        }
    
    def _optimize_cache_strategy(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize cache strategy based on usage patterns"""
        
        current_strategy = self.cache_manager.strategy
        cache_stats = metrics.get("cache", {}).get("performance", {})
        
        hit_rate = cache_stats.get("hit_rate", 0)
        
        # Choose strategy based on performance
        new_strategy = current_strategy
        
        if hit_rate < 50:  # Low hit rate
            if current_strategy != CacheStrategy.ADAPTIVE:
                new_strategy = CacheStrategy.ADAPTIVE
        elif hit_rate > 80:  # High hit rate
            if current_strategy != CacheStrategy.LRU:
                new_strategy = CacheStrategy.LRU
        
        if new_strategy != current_strategy:
            self.cache_manager.strategy = new_strategy
            logger.info(f"Changed cache strategy from {current_strategy.value} to {new_strategy.value}")
        
        return {
            "old_strategy": current_strategy.value,
            "new_strategy": new_strategy.value,
            "hit_rate": hit_rate
        }
    
    def _throttle_operations(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Throttle operations to reduce CPU usage"""
        
        # This would integrate with operation scheduling
        # For now, we'll just log the action
        logger.info("CPU throttling activated - reducing operation frequency")
        
        return {
            "action": "throttling_enabled",
            "cpu_percent": metrics.get("cpu_percent", 0)
        }
    
    def _optimize_async_operations(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize async operations for better throughput"""
        
        # This would optimize async patterns in the system
        logger.info("Async optimization activated - improving async patterns")
        
        return {
            "action": "async_optimization",
            "response_time": metrics.get("average_response_time", 0)
        }
    
    def _cache_slow_operations(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Cache results of slow operations"""
        
        slow_ops = metrics.get("slow_operations", [])
        cached_operations = []
        
        for op in slow_ops:
            # Mark operation for caching (would integrate with profiler)
            cached_operations.append(op)
            logger.info(f"Marked slow operation for caching: {op}")
        
        return {
            "cached_operations": cached_operations,
            "count": len(cached_operations)
        }
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report"""
        
        recent_optimizations = list(self.optimization_history)[-20:]  # Last 20
        
        return {
            "configuration": {
                "strategy": self.strategy.value,
                "optimization_interval": self.config["optimization_interval"],
                "enable_auto_optimization": self.config["enable_auto_optimization"]
            },
            "statistics": self.stats.copy(),
            "active_optimizations": list(self.active_optimizations),
            "rules": {
                name: {
                    "target": rule.target.value,
                    "priority": rule.priority,
                    "enabled": rule.enabled,
                    "last_applied": rule.last_applied,
                    "cooldown_seconds": rule.cooldown_seconds
                }
                for name, rule in self.optimization_rules.items()
            },
            "recent_optimizations": [
                {
                    "rule_name": opt.rule_name,
                    "target": opt.target.value,
                    "applied": opt.applied,
                    "improvement": opt.improvement,
                    "timestamp": opt.timestamp
                }
                for opt in recent_optimizations
            ],
            "performance_metrics": self.profiler.get_profiler_statistics(),
            "resource_metrics": self.resource_monitor.get_current_metrics()
        }
    
    def set_strategy(self, strategy: OptimizationStrategy) -> None:
        """Change optimization strategy"""
        old_strategy = self.strategy
        self.strategy = strategy
        
        # Adjust configuration based on strategy
        if strategy == OptimizationStrategy.CONSERVATIVE:
            self.config["optimization_interval"] = 60.0
            self.config["min_data_points"] = 20
        elif strategy == OptimizationStrategy.AGGRESSIVE:
            self.config["optimization_interval"] = 15.0
            self.config["min_data_points"] = 5
        elif strategy == OptimizationStrategy.ADAPTIVE:
            self.config["optimization_interval"] = 30.0
            self.config["min_data_points"] = 10
        
        logger.info(f"Changed optimization strategy from {old_strategy.value} to {strategy.value}")


# Global optimizer instance
_global_optimizer: Optional[RuntimeOptimizer] = None


def get_optimizer() -> RuntimeOptimizer:
    """Get the global optimizer instance"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = RuntimeOptimizer()
    return _global_optimizer