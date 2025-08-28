"""
Performance Optimizer

Provides performance monitoring and optimization for automation playback:
- Execution timing analysis
- Resource usage optimization
- Batch processing capabilities
- Smart scheduling and prioritization
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum
import time
import threading
from collections import defaultdict, deque
import statistics
import logging

logger = logging.getLogger(__name__)


class OptimizationLevel(Enum):
    """Performance optimization levels"""
    MINIMAL = "minimal"
    BALANCED = "balanced" 
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"


class ResourceType(Enum):
    """Types of resources to monitor and optimize"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK = "network"
    UI_THREAD = "ui_thread"


@dataclass
class PerformanceMetrics:
    """Performance metrics for optimization analysis"""
    execution_time: float
    resource_usage: Dict[ResourceType, float]
    throughput: float
    error_rate: float
    queue_size: int
    latency_p95: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class OptimizationRule:
    """Rule for performance optimization"""
    name: str
    condition: Callable[[PerformanceMetrics], bool]
    action: Callable[[], None]
    priority: int
    cooldown: float = 30.0
    last_applied: Optional[float] = None


@dataclass
class BatchConfig:
    """Configuration for batch processing optimization"""
    max_batch_size: int = 10
    batch_timeout: float = 5.0
    parallel_batches: int = 3
    priority_based: bool = True
    adaptive_sizing: bool = True


@dataclass
class OptimizationResult:
    """Result of performance optimization"""
    success: bool
    improvements: Dict[str, float]
    recommendations: List[str]
    metrics_before: PerformanceMetrics
    metrics_after: Optional[PerformanceMetrics] = None
    applied_optimizations: List[str] = field(default_factory=list)


class PerformanceOptimizer:
    """Advanced performance optimizer for automation playback"""
    
    def __init__(self, optimization_level: OptimizationLevel = OptimizationLevel.BALANCED):
        self.optimization_level = optimization_level
        self.metrics_history: deque = deque(maxlen=1000)
        self.resource_monitors: Dict[ResourceType, Any] = {}
        self.optimization_rules: List[OptimizationRule] = []
        self.batch_config = BatchConfig()
        self.action_queue: deque = deque()
        self.priority_queues: Dict[int, deque] = defaultdict(deque)
        self.processing_lock = threading.Lock()
        self.stats_lock = threading.Lock()
        self.current_metrics = PerformanceMetrics(0, {}, 0, 0, 0, 0)
        
        self._initialize_optimization_rules()
        self._start_monitoring()
    
    def _initialize_optimization_rules(self) -> None:
        """Initialize performance optimization rules based on level"""
        base_rules = [
            OptimizationRule(
                name="high_latency_mitigation",
                condition=lambda m: m.latency_p95 > 500,  # >500ms latency
                action=self._reduce_batch_size,
                priority=1
            ),
            OptimizationRule(
                name="queue_overflow_prevention",
                condition=lambda m: m.queue_size > 100,
                action=self._increase_parallel_processing,
                priority=2
            ),
            OptimizationRule(
                name="error_rate_optimization",
                condition=lambda m: m.error_rate > 0.05,  # >5% error rate
                action=self._enable_conservative_mode,
                priority=3
            )
        ]
        
        if self.optimization_level in [OptimizationLevel.BALANCED, OptimizationLevel.AGGRESSIVE]:
            base_rules.extend([
                OptimizationRule(
                    name="adaptive_batch_sizing",
                    condition=lambda m: m.throughput < self._calculate_optimal_throughput(),
                    action=self._optimize_batch_size,
                    priority=4
                ),
                OptimizationRule(
                    name="resource_balancing",
                    condition=self._check_resource_imbalance,
                    action=self._balance_resources,
                    priority=5
                )
            ])
        
        if self.optimization_level == OptimizationLevel.AGGRESSIVE:
            base_rules.extend([
                OptimizationRule(
                    name="predictive_caching",
                    condition=lambda m: True,  # Always consider caching
                    action=self._optimize_caching,
                    priority=6,
                    cooldown=60.0
                ),
                OptimizationRule(
                    name="memory_optimization",
                    condition=lambda m: m.resource_usage.get(ResourceType.MEMORY, 0) > 0.8,
                    action=self._optimize_memory_usage,
                    priority=7
                )
            ])
        
        self.optimization_rules = base_rules
    
    def _start_monitoring(self) -> None:
        """Start background performance monitoring"""
        def monitor_loop():
            while True:
                try:
                    metrics = self._collect_metrics()
                    with self.stats_lock:
                        self.metrics_history.append(metrics)
                        self.current_metrics = metrics
                    
                    # Apply optimization rules if needed
                    self._apply_optimization_rules(metrics)
                    
                    time.sleep(1.0)  # Monitor every second
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(5.0)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        with self.processing_lock:
            queue_size = len(self.action_queue) + sum(len(q) for q in self.priority_queues.values())
        
        # Calculate metrics from recent history
        recent_metrics = list(self.metrics_history)[-10:] if self.metrics_history else []
        
        if recent_metrics:
            avg_exec_time = statistics.mean(m.execution_time for m in recent_metrics)
            avg_throughput = statistics.mean(m.throughput for m in recent_metrics)
            avg_error_rate = statistics.mean(m.error_rate for m in recent_metrics)
            latencies = [m.latency_p95 for m in recent_metrics]
            latency_p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 5 else max(latencies) if latencies else 0
        else:
            avg_exec_time = avg_throughput = avg_error_rate = latency_p95 = 0
        
        return PerformanceMetrics(
            execution_time=avg_exec_time,
            resource_usage=self._get_resource_usage(),
            throughput=avg_throughput,
            error_rate=avg_error_rate,
            queue_size=queue_size,
            latency_p95=latency_p95
        )
    
    def _get_resource_usage(self) -> Dict[ResourceType, float]:
        """Get current resource usage metrics"""
        # Simplified resource usage - in production would use psutil or similar
        return {
            ResourceType.CPU: 0.5,  # Mock values
            ResourceType.MEMORY: 0.3,
            ResourceType.DISK_IO: 0.2,
            ResourceType.NETWORK: 0.1,
            ResourceType.UI_THREAD: 0.4
        }
    
    def _apply_optimization_rules(self, metrics: PerformanceMetrics) -> None:
        """Apply optimization rules based on current metrics"""
        current_time = time.time()
        
        for rule in sorted(self.optimization_rules, key=lambda r: r.priority):
            # Check cooldown
            if rule.last_applied and (current_time - rule.last_applied) < rule.cooldown:
                continue
            
            # Check condition
            try:
                if rule.condition(metrics):
                    logger.info(f"Applying optimization rule: {rule.name}")
                    rule.action()
                    rule.last_applied = current_time
            except Exception as e:
                logger.error(f"Error applying rule {rule.name}: {e}")
    
    def optimize_execution(self, actions: List[Dict[str, Any]], 
                          target_level: OptimizationLevel = None) -> OptimizationResult:
        """Optimize execution of action sequence"""
        target_level = target_level or self.optimization_level
        metrics_before = self.current_metrics
        
        try:
            # Apply pre-execution optimizations
            optimized_actions = self._optimize_action_sequence(actions)
            batched_actions = self._create_optimal_batches(optimized_actions)
            
            # Execute with optimization
            start_time = time.time()
            results = self._execute_optimized_batches(batched_actions)
            execution_time = time.time() - start_time
            
            # Collect post-execution metrics
            metrics_after = self._collect_metrics()
            
            improvements = self._calculate_improvements(metrics_before, metrics_after)
            recommendations = self._generate_recommendations(metrics_after)
            
            return OptimizationResult(
                success=True,
                improvements=improvements,
                recommendations=recommendations,
                metrics_before=metrics_before,
                metrics_after=metrics_after,
                applied_optimizations=[
                    "sequence_optimization",
                    "batch_processing", 
                    "adaptive_scheduling"
                ]
            )
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return OptimizationResult(
                success=False,
                improvements={},
                recommendations=[f"Optimization failed: {str(e)}"],
                metrics_before=metrics_before
            )
    
    def _optimize_action_sequence(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize the sequence of actions for better performance"""
        if not actions:
            return actions
        
        # Group similar actions together
        grouped_actions = self._group_similar_actions(actions)
        
        # Reorder for optimal execution
        optimized_sequence = []
        for group in grouped_actions:
            # Sort within group by priority/efficiency
            sorted_group = sorted(group, key=self._calculate_action_priority, reverse=True)
            optimized_sequence.extend(sorted_group)
        
        return optimized_sequence
    
    def _group_similar_actions(self, actions: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group similar actions for batch processing"""
        groups = defaultdict(list)
        
        for action in actions:
            # Group by action type and target application
            key = (
                action.get('type', ''),
                action.get('application', ''),
                action.get('window_title', '')
            )
            groups[key].append(action)
        
        return list(groups.values())
    
    def _calculate_action_priority(self, action: Dict[str, Any]) -> float:
        """Calculate priority score for action ordering"""
        # Higher score = higher priority
        base_priority = 1.0
        
        # Prioritize user interactions
        if action.get('type') in ['click', 'key_press', 'type']:
            base_priority += 2.0
        
        # Prioritize actions with coordinates (faster execution)
        if 'coordinates' in action:
            base_priority += 1.0
        
        # Prioritize actions in currently focused application
        if action.get('is_focused', False):
            base_priority += 1.5
        
        return base_priority
    
    def _create_optimal_batches(self, actions: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Create optimal batches for parallel processing"""
        if not actions:
            return []
        
        batches = []
        current_batch = []
        current_batch_complexity = 0
        max_complexity = self._calculate_max_batch_complexity()
        
        for action in actions:
            action_complexity = self._calculate_action_complexity(action)
            
            # Check if adding this action would exceed batch limits
            if (len(current_batch) >= self.batch_config.max_batch_size or
                current_batch_complexity + action_complexity > max_complexity):
                
                if current_batch:
                    batches.append(current_batch)
                    current_batch = []
                    current_batch_complexity = 0
            
            current_batch.append(action)
            current_batch_complexity += action_complexity
        
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def _calculate_max_batch_complexity(self) -> float:
        """Calculate maximum complexity allowed per batch"""
        base_complexity = 10.0
        
        # Adjust based on current system performance
        cpu_usage = self.current_metrics.resource_usage.get(ResourceType.CPU, 0)
        memory_usage = self.current_metrics.resource_usage.get(ResourceType.MEMORY, 0)
        
        if cpu_usage > 0.8 or memory_usage > 0.8:
            base_complexity *= 0.5
        elif cpu_usage < 0.3 and memory_usage < 0.3:
            base_complexity *= 1.5
        
        return base_complexity
    
    def _calculate_action_complexity(self, action: Dict[str, Any]) -> float:
        """Calculate complexity score for an action"""
        base_complexity = 1.0
        
        # Complex actions take more resources
        if action.get('type') == 'drag':
            base_complexity = 3.0
        elif action.get('type') in ['scroll', 'wait']:
            base_complexity = 2.0
        elif action.get('type') == 'type' and len(action.get('text', '')) > 50:
            base_complexity = 2.5
        
        # OCR or image matching increases complexity
        if action.get('use_ocr', False) or action.get('image_template'):
            base_complexity *= 2.0
        
        return base_complexity
    
    def _execute_optimized_batches(self, batches: List[List[Dict[str, Any]]]) -> List[Any]:
        """Execute batches with optimization"""
        results = []
        
        # Execute batches in parallel where possible
        if len(batches) <= self.batch_config.parallel_batches:
            # Small number of batches - execute in parallel
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(batches)) as executor:
                futures = [executor.submit(self._execute_batch, batch) for batch in batches]
                for future in concurrent.futures.as_completed(futures):
                    results.extend(future.result())
        else:
            # Large number of batches - execute sequentially with some parallelism
            for batch in batches:
                batch_results = self._execute_batch(batch)
                results.extend(batch_results)
        
        return results
    
    def _execute_batch(self, batch: List[Dict[str, Any]]) -> List[Any]:
        """Execute a single batch of actions"""
        # Mock execution - in real implementation would call actual action executor
        results = []
        for action in batch:
            # Simulate action execution
            time.sleep(0.01)  # Minimal delay
            results.append({"success": True, "action": action})
        return results
    
    def _calculate_improvements(self, before: PerformanceMetrics, after: PerformanceMetrics) -> Dict[str, float]:
        """Calculate performance improvements"""
        improvements = {}
        
        if before.execution_time > 0:
            time_improvement = (before.execution_time - after.execution_time) / before.execution_time
            improvements['execution_time'] = time_improvement * 100
        
        if before.throughput > 0:
            throughput_improvement = (after.throughput - before.throughput) / before.throughput
            improvements['throughput'] = throughput_improvement * 100
        
        if before.error_rate > after.error_rate:
            error_improvement = (before.error_rate - after.error_rate) / max(before.error_rate, 0.001)
            improvements['error_rate'] = error_improvement * 100
        
        latency_improvement = (before.latency_p95 - after.latency_p95) / max(before.latency_p95, 0.001)
        improvements['latency'] = latency_improvement * 100
        
        return improvements
    
    def _generate_recommendations(self, metrics: PerformanceMetrics) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if metrics.latency_p95 > 1000:  # >1s latency
            recommendations.append("Consider reducing batch sizes or enabling more aggressive caching")
        
        if metrics.error_rate > 0.02:  # >2% error rate
            recommendations.append("Enable more conservative execution with additional verification")
        
        cpu_usage = metrics.resource_usage.get(ResourceType.CPU, 0)
        if cpu_usage > 0.9:
            recommendations.append("CPU usage high - consider reducing parallel processing")
        elif cpu_usage < 0.2:
            recommendations.append("CPU underutilized - consider increasing parallelism")
        
        memory_usage = metrics.resource_usage.get(ResourceType.MEMORY, 0)
        if memory_usage > 0.9:
            recommendations.append("Memory usage high - enable garbage collection optimizations")
        
        if metrics.queue_size > 50:
            recommendations.append("Queue size large - consider increasing processing capacity")
        
        return recommendations
    
    # Optimization rule actions
    def _reduce_batch_size(self) -> None:
        """Reduce batch size to improve latency"""
        self.batch_config.max_batch_size = max(1, int(self.batch_config.max_batch_size * 0.8))
        logger.info(f"Reduced batch size to {self.batch_config.max_batch_size}")
    
    def _increase_parallel_processing(self) -> None:
        """Increase parallel processing to handle queue overflow"""
        self.batch_config.parallel_batches = min(10, self.batch_config.parallel_batches + 1)
        logger.info(f"Increased parallel batches to {self.batch_config.parallel_batches}")
    
    def _enable_conservative_mode(self) -> None:
        """Enable conservative mode to reduce errors"""
        self.batch_config.max_batch_size = max(1, int(self.batch_config.max_batch_size * 0.7))
        self.batch_config.batch_timeout *= 1.5
        logger.info("Enabled conservative mode")
    
    def _calculate_optimal_throughput(self) -> float:
        """Calculate optimal throughput based on system capabilities"""
        # Simple heuristic - could be more sophisticated
        return 10.0  # actions per second
    
    def _check_resource_imbalance(self, metrics: PerformanceMetrics) -> bool:
        """Check if resources are imbalanced"""
        usage_values = list(metrics.resource_usage.values())
        if not usage_values:
            return False
        
        max_usage = max(usage_values)
        min_usage = min(usage_values)
        return (max_usage - min_usage) > 0.5  # 50% imbalance
    
    def _optimize_batch_size(self) -> None:
        """Optimize batch size based on performance"""
        if self.batch_config.adaptive_sizing:
            recent_metrics = list(self.metrics_history)[-5:]
            if recent_metrics:
                avg_latency = statistics.mean(m.latency_p95 for m in recent_metrics)
                if avg_latency < 200:  # Low latency - can increase batch size
                    self.batch_config.max_batch_size = min(20, self.batch_config.max_batch_size + 1)
                elif avg_latency > 800:  # High latency - reduce batch size
                    self.batch_config.max_batch_size = max(1, self.batch_config.max_batch_size - 1)
    
    def _balance_resources(self) -> None:
        """Balance resource usage across different components"""
        logger.info("Balancing resource usage")
        # Implementation would adjust resource allocation
    
    def _optimize_caching(self) -> None:
        """Optimize caching strategies"""
        logger.info("Optimizing caching strategies")
        # Implementation would adjust cache policies
    
    def _optimize_memory_usage(self) -> None:
        """Optimize memory usage"""
        logger.info("Optimizing memory usage")
        # Implementation would trigger garbage collection, clear caches, etc.
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        with self.stats_lock:
            recent_metrics = list(self.metrics_history)[-100:]  # Last 100 data points
        
        if not recent_metrics:
            return {"status": "No metrics available"}
        
        return {
            "current_metrics": {
                "execution_time": self.current_metrics.execution_time,
                "throughput": self.current_metrics.throughput,
                "error_rate": self.current_metrics.error_rate,
                "queue_size": self.current_metrics.queue_size,
                "latency_p95": self.current_metrics.latency_p95,
            },
            "trends": {
                "avg_execution_time": statistics.mean(m.execution_time for m in recent_metrics),
                "avg_throughput": statistics.mean(m.throughput for m in recent_metrics),
                "avg_error_rate": statistics.mean(m.error_rate for m in recent_metrics),
            },
            "optimization_config": {
                "level": self.optimization_level.value,
                "batch_size": self.batch_config.max_batch_size,
                "parallel_batches": self.batch_config.parallel_batches,
                "batch_timeout": self.batch_config.batch_timeout,
            },
            "active_rules": len([r for r in self.optimization_rules if r.last_applied]),
            "recommendations": self._generate_recommendations(self.current_metrics)
        }