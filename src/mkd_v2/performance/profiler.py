"""
Performance Profiler

Advanced performance profiling tools for identifying bottlenecks
and optimizing system performance across all components.
"""

import time
import asyncio
import threading
import logging
import psutil
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, ContextManager
from enum import Enum
import functools
import traceback
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class ProfileType(Enum):
    """Types of performance profiling"""
    CPU_TIME = "cpu_time"
    MEMORY_USAGE = "memory_usage"
    IO_OPERATIONS = "io_operations"
    ASYNC_AWAIT = "async_await"
    FUNCTION_CALLS = "function_calls"
    SYSTEM_RESOURCES = "system_resources"


@dataclass
class ProfileMetrics:
    """Performance metrics for a profiled operation"""
    operation_name: str
    profile_type: ProfileType
    start_time: float
    end_time: float
    duration: float
    cpu_time: float = 0.0
    memory_before: float = 0.0
    memory_after: float = 0.0
    memory_delta: float = 0.0
    call_count: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProfileResult:
    """Comprehensive profiling result"""
    session_id: str
    start_time: float
    end_time: float
    total_duration: float
    metrics: List[ProfileMetrics] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class PerformanceProfiler:
    """Advanced performance profiler for system optimization"""
    
    def __init__(self):
        # Profile tracking
        self.active_profiles: Dict[str, ProfileMetrics] = {}
        self.completed_profiles: List[ProfileMetrics] = []
        self.profile_stack: List[str] = []  # For nested profiling
        
        # Configuration
        self.config = {
            "auto_profile": False,
            "profile_memory": True,
            "profile_cpu": True,
            "profile_io": True,
            "min_duration_ms": 1.0,  # Only profile operations > 1ms
            "max_profiles": 10000,    # Memory limit
            "enable_recommendations": True
        }
        
        # Statistics
        self.stats = {
            "total_profiles": 0,
            "active_sessions": 0,
            "total_duration": 0.0,
            "memory_peaks": [],
            "cpu_peaks": []
        }
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info("PerformanceProfiler initialized")
    
    def start_profiling(self, operation_name: str, profile_type: ProfileType = ProfileType.CPU_TIME) -> str:
        """Start profiling an operation"""
        
        profile_id = f"{operation_name}_{time.time()}_{threading.current_thread().ident}"
        
        with self.lock:
            # Get initial metrics
            process = psutil.Process()
            
            metrics = ProfileMetrics(
                operation_name=operation_name,
                profile_type=profile_type,
                start_time=time.time(),
                end_time=0.0,
                duration=0.0,
                memory_before=process.memory_info().rss / (1024 * 1024)  # MB
            )
            
            self.active_profiles[profile_id] = metrics
            self.profile_stack.append(profile_id)
            
            logger.debug(f"Started profiling: {operation_name} (ID: {profile_id})")
            
        return profile_id
    
    def stop_profiling(self, profile_id: str) -> Optional[ProfileMetrics]:
        """Stop profiling and return metrics"""
        
        with self.lock:
            if profile_id not in self.active_profiles:
                logger.warning(f"Profile ID not found: {profile_id}")
                return None
            
            metrics = self.active_profiles[profile_id]
            
            # Calculate final metrics
            end_time = time.time()
            process = psutil.Process()
            
            metrics.end_time = end_time
            metrics.duration = end_time - metrics.start_time
            metrics.memory_after = process.memory_info().rss / (1024 * 1024)  # MB
            metrics.memory_delta = metrics.memory_after - metrics.memory_before
            
            # Only keep profiles that meet minimum duration
            if metrics.duration * 1000 >= self.config["min_duration_ms"]:
                self.completed_profiles.append(metrics)
                
                # Manage memory by keeping only recent profiles
                if len(self.completed_profiles) > self.config["max_profiles"]:
                    self.completed_profiles = self.completed_profiles[-self.config["max_profiles"]:]
            
            # Remove from active profiles
            del self.active_profiles[profile_id]
            if profile_id in self.profile_stack:
                self.profile_stack.remove(profile_id)
            
            # Update statistics
            self.stats["total_profiles"] += 1
            self.stats["total_duration"] += metrics.duration
            
            logger.debug(f"Stopped profiling: {metrics.operation_name} ({metrics.duration:.3f}s)")
            
            return metrics
    
    def profile(self, operation_name: str = None, profile_type: ProfileType = ProfileType.CPU_TIME):
        """Decorator for profiling functions"""
        
        def decorator(func):
            name = operation_name or f"{func.__module__}.{func.__name__}"
            
            if asyncio.iscoroutinefunction(func):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    profile_id = self.start_profiling(name, profile_type)
                    try:
                        result = await func(*args, **kwargs)
                        return result
                    finally:
                        self.stop_profiling(profile_id)
                
                return async_wrapper
            
            else:
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    profile_id = self.start_profiling(name, profile_type)
                    try:
                        result = func(*args, **kwargs)
                        return result
                    finally:
                        self.stop_profiling(profile_id)
                
                return sync_wrapper
        
        return decorator
    
    def profile_context(self, operation_name: str, profile_type: ProfileType = ProfileType.CPU_TIME):
        """Context manager for profiling code blocks"""
        
        class ProfileContext:
            def __init__(self, profiler, name, ptype):
                self.profiler = profiler
                self.operation_name = name
                self.profile_type = ptype
                self.profile_id = None
            
            def __enter__(self):
                self.profile_id = self.profiler.start_profiling(self.operation_name, self.profile_type)
                return self.profile_id
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.profile_id:
                    metrics = self.profiler.stop_profiling(self.profile_id)
                    if exc_type:
                        # Add exception info to metadata
                        if metrics:
                            metrics.metadata["exception"] = {
                                "type": exc_type.__name__,
                                "message": str(exc_val),
                                "traceback": traceback.format_tb(exc_tb)[:3]  # First 3 frames
                            }
        
        return ProfileContext(self, operation_name, profile_type)
    
    def analyze_performance(self, time_window: float = 300.0) -> ProfileResult:
        """Analyze performance over a time window"""
        
        current_time = time.time()
        cutoff_time = current_time - time_window
        
        # Filter profiles within time window
        recent_profiles = [
            p for p in self.completed_profiles
            if p.start_time >= cutoff_time
        ]
        
        if not recent_profiles:
            return ProfileResult(
                session_id=f"analysis_{current_time}",
                start_time=current_time,
                end_time=current_time,
                total_duration=0.0
            )
        
        # Calculate summary statistics
        total_duration = sum(p.duration for p in recent_profiles)
        avg_duration = total_duration / len(recent_profiles)
        max_duration = max(p.duration for p in recent_profiles)
        
        # Memory analysis
        memory_deltas = [p.memory_delta for p in recent_profiles if abs(p.memory_delta) > 0.1]
        avg_memory_delta = sum(memory_deltas) / len(memory_deltas) if memory_deltas else 0.0
        max_memory_usage = max(p.memory_after for p in recent_profiles)
        
        # Operation analysis
        operation_stats = defaultdict(lambda: {"count": 0, "total_time": 0.0, "max_time": 0.0})
        
        for profile in recent_profiles:
            op_stat = operation_stats[profile.operation_name]
            op_stat["count"] += 1
            op_stat["total_time"] += profile.duration
            op_stat["max_time"] = max(op_stat["max_time"], profile.duration)
        
        # Create summary
        summary = {
            "time_window_seconds": time_window,
            "total_operations": len(recent_profiles),
            "total_duration": total_duration,
            "average_duration": avg_duration,
            "max_duration": max_duration,
            "average_memory_delta": avg_memory_delta,
            "max_memory_usage": max_memory_usage,
            "operations_by_frequency": sorted(
                [(op, stats["count"]) for op, stats in operation_stats.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "operations_by_duration": sorted(
                [(op, stats["total_time"]) for op, stats in operation_stats.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
        
        # Generate recommendations
        recommendations = []
        
        if self.config["enable_recommendations"]:
            recommendations = self._generate_recommendations(recent_profiles, summary)
        
        return ProfileResult(
            session_id=f"analysis_{current_time}",
            start_time=cutoff_time,
            end_time=current_time,
            total_duration=total_duration,
            metrics=recent_profiles,
            summary=summary,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, profiles: List[ProfileMetrics], summary: Dict[str, Any]) -> List[str]:
        """Generate performance optimization recommendations"""
        
        recommendations = []
        
        # Slow operation detection
        slow_threshold = 0.1  # 100ms
        slow_operations = [p for p in profiles if p.duration > slow_threshold]
        
        if slow_operations:
            top_slow = sorted(slow_operations, key=lambda x: x.duration, reverse=True)[:3]
            for op in top_slow:
                recommendations.append(
                    f"Optimize '{op.operation_name}' - takes {op.duration:.3f}s "
                    f"({op.duration*1000:.1f}ms), consider caching or async optimization"
                )
        
        # Memory leak detection
        memory_growth = [p for p in profiles if p.memory_delta > 10.0]  # > 10MB growth
        if memory_growth:
            recommendations.append(
                f"Memory leak detected: {len(memory_growth)} operations show significant memory growth. "
                f"Check for unreleased resources."
            )
        
        # High frequency operations
        if summary["operations_by_frequency"]:
            top_frequent = summary["operations_by_frequency"][0]
            if top_frequent[1] > 100:  # More than 100 calls
                recommendations.append(
                    f"High frequency operation '{top_frequent[0]}' called {top_frequent[1]} times. "
                    f"Consider caching or batching."
                )
        
        # Overall system recommendations
        if summary["max_memory_usage"] > 500:  # > 500MB
            recommendations.append("High memory usage detected. Consider implementing lazy loading and cleanup.")
        
        if summary["average_duration"] > 0.05:  # > 50ms average
            recommendations.append("High average operation time. Profile individual operations for optimization.")
        
        return recommendations
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        
        try:
            process = psutil.Process()
            
            # CPU metrics
            cpu_percent = process.cpu_percent()
            cpu_times = process.cpu_times()
            
            # Memory metrics
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # System metrics
            system_cpu = psutil.cpu_percent(interval=0.1)
            system_memory = psutil.virtual_memory()
            
            return {
                "process": {
                    "cpu_percent": cpu_percent,
                    "cpu_times": {
                        "user": cpu_times.user,
                        "system": cpu_times.system
                    },
                    "memory_rss": memory_info.rss / (1024 * 1024),  # MB
                    "memory_vms": memory_info.vms / (1024 * 1024),  # MB
                    "memory_percent": memory_percent,
                    "pid": process.pid,
                    "num_threads": process.num_threads()
                },
                "system": {
                    "cpu_percent": system_cpu,
                    "memory_total": system_memory.total / (1024 * 1024 * 1024),  # GB
                    "memory_available": system_memory.available / (1024 * 1024 * 1024),  # GB
                    "memory_used_percent": system_memory.percent
                },
                "profiler": {
                    "active_profiles": len(self.active_profiles),
                    "completed_profiles": len(self.completed_profiles),
                    "total_profiles": self.stats["total_profiles"],
                    "total_profiling_duration": self.stats["total_duration"]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {"error": str(e)}
    
    def export_profile_data(self, filepath: str, format: str = "json") -> bool:
        """Export profile data to file"""
        
        try:
            data = {
                "export_time": time.time(),
                "config": self.config,
                "stats": self.stats,
                "completed_profiles": [
                    {
                        "operation_name": p.operation_name,
                        "profile_type": p.profile_type.value,
                        "start_time": p.start_time,
                        "end_time": p.end_time,
                        "duration": p.duration,
                        "memory_before": p.memory_before,
                        "memory_after": p.memory_after,
                        "memory_delta": p.memory_delta,
                        "call_count": p.call_count,
                        "metadata": p.metadata
                    }
                    for p in self.completed_profiles
                ]
            }
            
            if format.lower() == "json":
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
            
            logger.info(f"Profile data exported to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export profile data: {e}")
            return False
    
    def clear_profiles(self) -> None:
        """Clear all profile data"""
        
        with self.lock:
            self.completed_profiles.clear()
            self.active_profiles.clear()
            self.profile_stack.clear()
            
            # Reset statistics
            self.stats = {
                "total_profiles": 0,
                "active_sessions": 0,
                "total_duration": 0.0,
                "memory_peaks": [],
                "cpu_peaks": []
            }
            
        logger.info("All profile data cleared")
    
    def get_profiler_statistics(self) -> Dict[str, Any]:
        """Get comprehensive profiler statistics"""
        
        return {
            "configuration": self.config.copy(),
            "statistics": self.stats.copy(),
            "active_profiles": len(self.active_profiles),
            "completed_profiles": len(self.completed_profiles),
            "memory_usage": sum(len(str(p)) for p in self.completed_profiles),  # Rough estimate
            "top_operations": self._get_top_operations(),
            "system_metrics": self.get_system_metrics()
        }
    
    def _get_top_operations(self) -> List[Dict[str, Any]]:
        """Get top operations by various metrics"""
        
        if not self.completed_profiles:
            return []
        
        # Group by operation name
        operation_stats = defaultdict(lambda: {
            "count": 0,
            "total_time": 0.0,
            "max_time": 0.0,
            "avg_time": 0.0,
            "total_memory": 0.0
        })
        
        for profile in self.completed_profiles:
            stats = operation_stats[profile.operation_name]
            stats["count"] += 1
            stats["total_time"] += profile.duration
            stats["max_time"] = max(stats["max_time"], profile.duration)
            stats["total_memory"] += abs(profile.memory_delta)
        
        # Calculate averages
        for stats in operation_stats.values():
            stats["avg_time"] = stats["total_time"] / stats["count"]
        
        # Convert to list and sort by total time
        top_operations = [
            {
                "operation": op_name,
                **stats
            }
            for op_name, stats in operation_stats.items()
        ]
        
        return sorted(top_operations, key=lambda x: x["total_time"], reverse=True)[:10]


# Global profiler instance
_global_profiler: Optional[PerformanceProfiler] = None


def get_profiler() -> PerformanceProfiler:
    """Get the global profiler instance"""
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = PerformanceProfiler()
    return _global_profiler


def profile(operation_name: str = None, profile_type: ProfileType = ProfileType.CPU_TIME):
    """Convenience decorator for profiling functions"""
    return get_profiler().profile(operation_name, profile_type)


def profile_context(operation_name: str, profile_type: ProfileType = ProfileType.CPU_TIME):
    """Convenience context manager for profiling code blocks"""
    return get_profiler().profile_context(operation_name, profile_type)