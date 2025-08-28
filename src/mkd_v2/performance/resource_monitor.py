"""
Resource Monitor

Real-time system resource monitoring and optimization for the MKD platform.
Tracks CPU, memory, disk, and network usage with alerting capabilities.
"""

import time
import asyncio
import threading
import logging
import psutil
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from collections import deque, defaultdict
import json

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of system resources to monitor"""
    CPU = "cpu"
    CPU_USAGE = "cpu_usage"  # Alias for test compatibility
    MEMORY = "memory"
    MEMORY_USAGE = "memory_usage"  # Alias for test compatibility
    DISK = "disk"
    DISK_USAGE = "disk_usage"
    NETWORK = "network"
    THREADS = "threads"
    FILE_DESCRIPTORS = "file_descriptors"


class AlertLevel(Enum):
    """Resource alert levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class ResourceMetrics:
    """System resource metrics snapshot"""
    timestamp: float
    cpu_percent: float
    memory_rss_mb: float
    memory_vms_mb: float
    memory_percent: float
    disk_read_bytes: int = 0
    disk_write_bytes: int = 0
    network_sent_bytes: int = 0
    network_recv_bytes: int = 0
    thread_count: int = 0
    fd_count: int = 0


@dataclass
class ResourceAlert:
    """Resource usage alert"""
    timestamp: float
    resource_type: ResourceType
    level: AlertLevel
    message: str
    current_value: float
    threshold: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResourceMonitor:
    """Advanced system resource monitoring"""
    
    def __init__(self, sampling_interval: float = 1.0, history_size: int = 3600):
        self.sampling_interval = sampling_interval
        self.history_size = history_size
        
        # Resource tracking
        self.metrics_history: deque = deque(maxlen=history_size)
        self.last_metrics: Optional[ResourceMetrics] = None
        
        # Monitoring state
        self.monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
        
        # Alert configuration
        self.thresholds = {
            ResourceType.CPU: {
                AlertLevel.WARNING: 70.0,
                AlertLevel.CRITICAL: 85.0,
                AlertLevel.EMERGENCY: 95.0
            },
            ResourceType.MEMORY: {
                AlertLevel.WARNING: 70.0,
                AlertLevel.CRITICAL: 85.0,
                AlertLevel.EMERGENCY: 95.0
            },
            ResourceType.THREADS: {
                AlertLevel.WARNING: 100,
                AlertLevel.CRITICAL: 200,
                AlertLevel.EMERGENCY: 500
            }
        }
        
        # Alert tracking
        self.active_alerts: Dict[str, ResourceAlert] = {}
        self.alert_history: List[ResourceAlert] = []
        self.alert_callbacks: List[Callable[[ResourceAlert], None]] = []
        
        # Statistics
        self.stats = {
            "total_samples": 0,
            "monitoring_duration": 0.0,
            "peak_cpu": 0.0,
            "peak_memory": 0.0,
            "total_alerts": 0
        }
        
        # Process reference
        try:
            self.process = psutil.Process()
        except psutil.NoSuchProcess:
            self.process = None
            logger.warning("Could not get process reference for monitoring")
        
        logger.info("ResourceMonitor initialized")
    
    async def start_monitoring(self) -> None:
        """Start resource monitoring"""
        
        if self.monitoring:
            logger.warning("Resource monitoring already running")
            return
        
        if not self.process:
            logger.error("Cannot start monitoring without process reference")
            return
        
        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info(f"Started resource monitoring (interval: {self.sampling_interval}s)")
    
    async def stop_monitoring(self) -> None:
        """Stop resource monitoring"""
        
        self.monitoring = False
        
        if self.monitor_task and not self.monitor_task.done():
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped resource monitoring")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        
        start_time = time.time()
        
        while self.monitoring:
            try:
                # Collect metrics
                metrics = await self._collect_metrics()
                
                if metrics:
                    # Store metrics
                    self.metrics_history.append(metrics)
                    self.last_metrics = metrics
                    
                    # Update statistics
                    self.stats["total_samples"] += 1
                    self.stats["peak_cpu"] = max(self.stats["peak_cpu"], metrics.cpu_percent)
                    self.stats["peak_memory"] = max(self.stats["peak_memory"], metrics.memory_percent)
                    
                    # Check for alerts
                    await self._check_alerts(metrics)
                
                await asyncio.sleep(self.sampling_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.sampling_interval)
        
        # Update final statistics
        self.stats["monitoring_duration"] = time.time() - start_time
    
    async def _collect_metrics(self) -> Optional[ResourceMetrics]:
        """Collect current resource metrics"""
        
        if not self.process:
            return None
        
        try:
            # Basic process metrics
            cpu_percent = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            # Additional metrics
            thread_count = self.process.num_threads()
            
            # File descriptors (Unix only)
            fd_count = 0
            try:
                fd_count = self.process.num_fds()
            except (AttributeError, psutil.AccessDenied):
                pass  # Windows or no permission
            
            # I/O metrics
            disk_read, disk_write = 0, 0
            net_sent, net_recv = 0, 0
            
            try:
                io_counters = self.process.io_counters()
                disk_read = io_counters.read_bytes
                disk_write = io_counters.write_bytes
            except (AttributeError, psutil.AccessDenied):
                pass
            
            # Network metrics (system-wide)
            try:
                net_io = psutil.net_io_counters()
                if net_io:
                    net_sent = net_io.bytes_sent
                    net_recv = net_io.bytes_recv
            except (AttributeError, psutil.AccessDenied):
                pass
            
            return ResourceMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_rss_mb=memory_info.rss / (1024 * 1024),
                memory_vms_mb=memory_info.vms / (1024 * 1024),
                memory_percent=memory_percent,
                disk_read_bytes=disk_read,
                disk_write_bytes=disk_write,
                network_sent_bytes=net_sent,
                network_recv_bytes=net_recv,
                thread_count=thread_count,
                fd_count=fd_count
            )
            
        except psutil.NoSuchProcess:
            logger.warning("Process no longer exists")
            return None
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return None
    
    async def _check_alerts(self, metrics: ResourceMetrics) -> None:
        """Check metrics against thresholds and generate alerts"""
        
        # CPU alerts
        await self._check_resource_threshold(
            ResourceType.CPU,
            metrics.cpu_percent,
            metrics.timestamp
        )
        
        # Memory alerts
        await self._check_resource_threshold(
            ResourceType.MEMORY,
            metrics.memory_percent,
            metrics.timestamp
        )
        
        # Thread count alerts
        await self._check_resource_threshold(
            ResourceType.THREADS,
            float(metrics.thread_count),
            metrics.timestamp
        )
        
        # Custom checks
        await self._check_custom_conditions(metrics)
    
    async def _check_resource_threshold(self, resource_type: ResourceType, 
                                       value: float, timestamp: float) -> None:
        """Check a specific resource against its thresholds"""
        
        thresholds = self.thresholds.get(resource_type, {})
        alert_key = f"{resource_type.value}_threshold"
        
        # Determine alert level
        alert_level = None
        threshold_value = 0.0
        
        for level in [AlertLevel.EMERGENCY, AlertLevel.CRITICAL, AlertLevel.WARNING]:
            if level in thresholds and value >= thresholds[level]:
                alert_level = level
                threshold_value = thresholds[level]
                break
        
        if alert_level:
            # Create or update alert
            if alert_key not in self.active_alerts or \
               self.active_alerts[alert_key].level != alert_level:
                
                alert = ResourceAlert(
                    timestamp=timestamp,
                    resource_type=resource_type,
                    level=alert_level,
                    message=f"{resource_type.value.title()} usage at {value:.1f}% "
                            f"(threshold: {threshold_value:.1f}%)",
                    current_value=value,
                    threshold=threshold_value
                )
                
                self.active_alerts[alert_key] = alert
                self.alert_history.append(alert)
                self.stats["total_alerts"] += 1
                
                # Trigger callbacks
                await self._trigger_alert_callbacks(alert)
        
        else:
            # Clear alert if below all thresholds
            if alert_key in self.active_alerts:
                del self.active_alerts[alert_key]
    
    async def _check_custom_conditions(self, metrics: ResourceMetrics) -> None:
        """Check for custom alert conditions"""
        
        # Memory leak detection
        if len(self.metrics_history) > 60:  # Need at least 1 minute of data
            recent_memory = [m.memory_rss_mb for m in list(self.metrics_history)[-60:]]
            if len(recent_memory) > 1:
                growth_rate = (recent_memory[-1] - recent_memory[0]) / len(recent_memory)
                
                # Alert if memory growing > 1MB per minute
                if growth_rate > 1.0:
                    alert_key = "memory_leak"
                    if alert_key not in self.active_alerts:
                        alert = ResourceAlert(
                            timestamp=metrics.timestamp,
                            resource_type=ResourceType.MEMORY,
                            level=AlertLevel.WARNING,
                            message=f"Possible memory leak detected: growing at {growth_rate:.2f}MB/min",
                            current_value=metrics.memory_rss_mb,
                            threshold=growth_rate,
                            metadata={"growth_rate_mb_per_min": growth_rate}
                        )
                        
                        self.active_alerts[alert_key] = alert
                        self.alert_history.append(alert)
                        await self._trigger_alert_callbacks(alert)
        
        # High I/O activity
        if self.last_metrics:
            time_delta = metrics.timestamp - self.last_metrics.timestamp
            if time_delta > 0:
                read_rate = (metrics.disk_read_bytes - self.last_metrics.disk_read_bytes) / time_delta
                write_rate = (metrics.disk_write_bytes - self.last_metrics.disk_write_bytes) / time_delta
                
                # Alert if I/O > 100MB/s
                if read_rate + write_rate > 100 * 1024 * 1024:
                    alert_key = "high_io"
                    if alert_key not in self.active_alerts:
                        total_rate_mb = (read_rate + write_rate) / (1024 * 1024)
                        alert = ResourceAlert(
                            timestamp=metrics.timestamp,
                            resource_type=ResourceType.DISK,
                            level=AlertLevel.WARNING,
                            message=f"High I/O activity: {total_rate_mb:.1f}MB/s",
                            current_value=total_rate_mb,
                            threshold=100.0,
                            metadata={"read_rate_mb": read_rate/(1024*1024), "write_rate_mb": write_rate/(1024*1024)}
                        )
                        
                        self.active_alerts[alert_key] = alert
                        self.alert_history.append(alert)
                        await self._trigger_alert_callbacks(alert)
    
    async def _trigger_alert_callbacks(self, alert: ResourceAlert) -> None:
        """Trigger registered alert callbacks"""
        
        logger.warning(f"Resource alert: {alert.message}")
        
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    def add_alert_callback(self, callback: Callable[[ResourceAlert], None]) -> None:
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
        logger.debug(f"Added alert callback: {callback.__name__}")
    
    def remove_alert_callback(self, callback: Callable[[ResourceAlert], None]) -> None:
        """Remove alert callback function"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
            logger.debug(f"Removed alert callback: {callback.__name__}")
    
    def set_threshold(self, resource_type: ResourceType, level: AlertLevel, value: float) -> None:
        """Set custom threshold for resource type"""
        
        if resource_type not in self.thresholds:
            self.thresholds[resource_type] = {}
        
        self.thresholds[resource_type][level] = value
        logger.info(f"Set {resource_type.value} {level.value} threshold to {value}")
    
    def get_current_metrics(self) -> Optional[ResourceMetrics]:
        """Get the most recent metrics"""
        return self.last_metrics
    
    def get_metrics_history(self, duration_seconds: float = 300) -> List[ResourceMetrics]:
        """Get metrics history for specified duration"""
        
        if not self.metrics_history:
            return []
        
        cutoff_time = time.time() - duration_seconds
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
    
    def get_resource_statistics(self, duration_seconds: float = 300) -> Dict[str, Any]:
        """Get comprehensive resource statistics"""
        
        recent_metrics = self.get_metrics_history(duration_seconds)
        
        if not recent_metrics:
            return {"error": "No metrics available"}
        
        # Calculate statistics
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        thread_values = [m.thread_count for m in recent_metrics]
        
        def safe_avg(values):
            return sum(values) / len(values) if values else 0.0
        
        def safe_max(values):
            return max(values) if values else 0.0
        
        def safe_min(values):
            return min(values) if values else 0.0
        
        return {
            "timeframe": {
                "duration_seconds": duration_seconds,
                "samples": len(recent_metrics),
                "start_time": recent_metrics[0].timestamp if recent_metrics else 0,
                "end_time": recent_metrics[-1].timestamp if recent_metrics else 0
            },
            "cpu": {
                "average": safe_avg(cpu_values),
                "maximum": safe_max(cpu_values),
                "minimum": safe_min(cpu_values),
                "current": recent_metrics[-1].cpu_percent if recent_metrics else 0
            },
            "memory": {
                "average_percent": safe_avg(memory_values),
                "maximum_percent": safe_max(memory_values),
                "current_rss_mb": recent_metrics[-1].memory_rss_mb if recent_metrics else 0,
                "current_percent": recent_metrics[-1].memory_percent if recent_metrics else 0
            },
            "threads": {
                "average": safe_avg(thread_values),
                "maximum": safe_max(thread_values),
                "current": recent_metrics[-1].thread_count if recent_metrics else 0
            },
            "alerts": {
                "active_count": len(self.active_alerts),
                "total_alerts": self.stats["total_alerts"],
                "active_alerts": list(self.active_alerts.keys())
            },
            "monitoring": {
                "is_running": self.monitoring,
                "total_samples": self.stats["total_samples"],
                "monitoring_duration": self.stats["monitoring_duration"],
                "peak_cpu": self.stats["peak_cpu"],
                "peak_memory": self.stats["peak_memory"]
            }
        }
    
    def export_metrics(self, filepath: str, duration_seconds: float = 3600) -> bool:
        """Export metrics to JSON file"""
        
        try:
            recent_metrics = self.get_metrics_history(duration_seconds)
            
            data = {
                "export_time": time.time(),
                "duration_seconds": duration_seconds,
                "total_samples": len(recent_metrics),
                "metrics": [
                    {
                        "timestamp": m.timestamp,
                        "cpu_percent": m.cpu_percent,
                        "memory_rss_mb": m.memory_rss_mb,
                        "memory_percent": m.memory_percent,
                        "thread_count": m.thread_count,
                        "fd_count": m.fd_count
                    }
                    for m in recent_metrics
                ],
                "statistics": self.get_resource_statistics(duration_seconds),
                "alerts": [
                    {
                        "timestamp": a.timestamp,
                        "resource_type": a.resource_type.value,
                        "level": a.level.value,
                        "message": a.message,
                        "current_value": a.current_value,
                        "threshold": a.threshold
                    }
                    for a in self.alert_history[-100:]  # Last 100 alerts
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Resource metrics exported to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            return False
    
    def optimize_resources(self) -> Dict[str, Any]:
        """Suggest resource optimizations based on monitoring data"""
        
        if not self.metrics_history:
            return {"error": "No monitoring data available"}
        
        recommendations = []
        recent_metrics = list(self.metrics_history)[-60:]  # Last minute
        
        if recent_metrics:
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            avg_threads = sum(m.thread_count for m in recent_metrics) / len(recent_metrics)
            
            # CPU recommendations
            if avg_cpu > 80:
                recommendations.append("High CPU usage: Consider optimizing CPU-intensive operations or adding more workers")
            elif avg_cpu < 10:
                recommendations.append("Low CPU usage: May be able to handle more concurrent operations")
            
            # Memory recommendations
            if avg_memory > 80:
                recommendations.append("High memory usage: Consider implementing memory cleanup or caching optimizations")
            
            # Thread recommendations
            if avg_threads > 100:
                recommendations.append("High thread count: Consider using async operations or thread pooling")
        
        # Alert-based recommendations
        if len(self.active_alerts) > 0:
            recommendations.append(f"Active alerts: {len(self.active_alerts)} resource issues need attention")
        
        return {
            "timestamp": time.time(),
            "monitoring_health": "good" if len(self.active_alerts) == 0 else "needs_attention",
            "recommendations": recommendations,
            "active_alerts": len(self.active_alerts),
            "resource_summary": self.get_resource_statistics()
        }


# Global monitor instance
_global_monitor: Optional[ResourceMonitor] = None


def get_resource_monitor() -> ResourceMonitor:
    """Get the global resource monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = ResourceMonitor()
    return _global_monitor


def start_monitoring(interval: float = 1.0) -> None:
    """Start global resource monitoring"""
    monitor = get_resource_monitor()
    monitor.sampling_interval = interval
    asyncio.create_task(monitor.start_monitoring())