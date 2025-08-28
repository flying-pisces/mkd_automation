"""
Cache Manager

Intelligent caching system for improving performance by storing
frequently accessed data and computation results.
"""

import time
import threading
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from enum import Enum
import json
import hashlib
import weakref
from collections import OrderedDict
import asyncio

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache eviction strategies"""
    LRU = "lru"              # Least Recently Used
    LFU = "lfu"              # Least Frequently Used
    TTL = "ttl"              # Time To Live
    FIFO = "fifo"            # First In First Out
    ADAPTIVE = "adaptive"     # Adaptive based on usage patterns


class CacheEntry:
    """Individual cache entry with metadata"""
    
    def __init__(self, key: str, value: Any, ttl: Optional[float] = None):
        self.key = key
        self.value = value
        self.created_time = time.time()
        self.last_accessed = self.created_time
        self.access_count = 0
        self.ttl = ttl
        self.size = self._calculate_size(value)
        
    def _calculate_size(self, value: Any) -> int:
        """Estimate the size of the cached value"""
        try:
            if isinstance(value, (str, bytes)):
                return len(value)
            elif isinstance(value, (int, float, bool)):
                return 8  # Approximate
            elif isinstance(value, (list, tuple)):
                return sum(self._calculate_size(item) for item in value)
            elif isinstance(value, dict):
                return sum(self._calculate_size(k) + self._calculate_size(v) for k, v in value.items())
            else:
                return len(str(value))  # Fallback
        except:
            return 64  # Default estimate
    
    def is_expired(self) -> bool:
        """Check if the entry has expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_time > self.ttl
    
    def touch(self) -> None:
        """Update access metadata"""
        self.last_accessed = time.time()
        self.access_count += 1
    
    def age(self) -> float:
        """Get age in seconds"""
        return time.time() - self.created_time


class CacheManager:
    """Intelligent cache manager with multiple strategies"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: float = 100.0, 
                 default_ttl: float = 3600.0, strategy: CacheStrategy = CacheStrategy.LRU):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self.strategy = strategy
        
        # Cache storage
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.memory_usage = 0
        
        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired": 0,
            "memory_peak": 0,
            "total_requests": 0
        }
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Background cleanup
        self.cleanup_enabled = True
        self.cleanup_interval = 60.0  # seconds
        self.cleanup_task: Optional[asyncio.Task] = None
        
        logger.info(f"CacheManager initialized: strategy={strategy.value}, max_size={max_size}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        
        with self.lock:
            self.stats["total_requests"] += 1
            
            if key not in self.cache:
                self.stats["misses"] += 1
                return default
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired():
                self._remove_entry(key)
                self.stats["expired"] += 1
                self.stats["misses"] += 1
                return default
            
            # Update access info
            entry.touch()
            
            # Move to end for LRU
            if self.strategy == CacheStrategy.LRU:
                self.cache.move_to_end(key)
            
            self.stats["hits"] += 1
            return entry.value
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Put value in cache"""
        
        with self.lock:
            # Use default TTL if not specified
            if ttl is None:
                ttl = self.default_ttl
            
            # Create cache entry
            entry = CacheEntry(key, value, ttl)
            
            # Check if we need to evict before adding
            if key not in self.cache:
                # Ensure we have space
                while len(self.cache) >= self.max_size:
                    self._evict_entry()
                
                # Check memory limit
                if self.memory_usage + entry.size > self.max_memory_bytes:
                    # Try to free up memory
                    freed_space = self._free_memory(entry.size)
                    if freed_space < entry.size:
                        logger.warning(f"Cannot cache {key}: insufficient memory")
                        return False
            
            # Remove existing entry if updating
            if key in self.cache:
                self._remove_entry(key)
            
            # Add new entry
            self.cache[key] = entry
            self.memory_usage += entry.size
            
            # Update memory peak
            self.stats["memory_peak"] = max(self.stats["memory_peak"], self.memory_usage)
            
            logger.debug(f"Cached {key}: size={entry.size}, ttl={ttl}")
            return True
    
    def remove(self, key: str) -> bool:
        """Remove entry from cache"""
        
        with self.lock:
            if key in self.cache:
                self._remove_entry(key)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        
        with self.lock:
            self.cache.clear()
            self.memory_usage = 0
            logger.info("Cache cleared")
    
    def get_or_compute(self, key: str, compute_func: Callable[[], Any], 
                      ttl: Optional[float] = None) -> Any:
        """Get from cache or compute and cache the result"""
        
        # Try cache first
        result = self.get(key)
        if result is not None:
            return result
        
        # Compute result
        try:
            result = compute_func()
            if result is not None:
                self.put(key, result, ttl)
            return result
        except Exception as e:
            logger.error(f"Failed to compute value for key {key}: {e}")
            raise
    
    async def get_or_compute_async(self, key: str, compute_func: Callable[[], Any],
                                  ttl: Optional[float] = None) -> Any:
        """Async version of get_or_compute"""
        
        # Try cache first
        result = self.get(key)
        if result is not None:
            return result
        
        # Compute result
        try:
            if asyncio.iscoroutinefunction(compute_func):
                result = await compute_func()
            else:
                result = compute_func()
                
            if result is not None:
                self.put(key, result, ttl)
            return result
        except Exception as e:
            logger.error(f"Failed to compute async value for key {key}: {e}")
            raise
    
    def _remove_entry(self, key: str) -> None:
        """Remove entry and update memory usage"""
        if key in self.cache:
            entry = self.cache[key]
            self.memory_usage -= entry.size
            del self.cache[key]
    
    def _evict_entry(self) -> bool:
        """Evict an entry based on strategy"""
        
        if not self.cache:
            return False
        
        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used (first in OrderedDict)
            key = next(iter(self.cache))
            
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            key = min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
            
        elif self.strategy == CacheStrategy.TTL:
            # Remove expired entries first, then oldest
            expired_keys = [k for k, entry in self.cache.items() if entry.is_expired()]
            if expired_keys:
                key = expired_keys[0]
            else:
                key = min(self.cache.keys(), key=lambda k: self.cache[k].created_time)
                
        elif self.strategy == CacheStrategy.FIFO:
            # Remove first inserted (first in OrderedDict)
            key = next(iter(self.cache))
            
        else:  # ADAPTIVE
            # Adaptive strategy based on usage patterns
            key = self._adaptive_eviction()
        
        self._remove_entry(key)
        self.stats["evictions"] += 1
        
        logger.debug(f"Evicted cache entry: {key}")
        return True
    
    def _adaptive_eviction(self) -> str:
        """Adaptive eviction strategy"""
        
        # Score each entry based on multiple factors
        scores = {}
        current_time = time.time()
        
        for key, entry in self.cache.items():
            # Factors: recency, frequency, size, age
            recency_score = 1.0 / (current_time - entry.last_accessed + 1)
            frequency_score = entry.access_count / (entry.age() + 1)
            size_penalty = entry.size / 1000  # Penalize large entries
            
            # Combined score (higher = keep longer)
            score = (recency_score + frequency_score) / size_penalty
            scores[key] = score
        
        # Return key with lowest score
        return min(scores.keys(), key=lambda k: scores[k])
    
    def _free_memory(self, required_bytes: int) -> int:
        """Free up memory by evicting entries"""
        
        freed_bytes = 0
        
        while freed_bytes < required_bytes and self.cache:
            entry_key = next(iter(self.cache))
            entry_size = self.cache[entry_key].size
            
            self._remove_entry(entry_key)
            freed_bytes += entry_size
            self.stats["evictions"] += 1
        
        return freed_bytes
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        
        with self.lock:
            expired_keys = []
            
            for key, entry in self.cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove_entry(key)
                self.stats["expired"] += 1
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        
        with self.lock:
            hit_rate = 0.0
            if self.stats["total_requests"] > 0:
                hit_rate = self.stats["hits"] / self.stats["total_requests"] * 100
            
            return {
                "configuration": {
                    "max_size": self.max_size,
                    "max_memory_mb": self.max_memory_bytes / (1024 * 1024),
                    "default_ttl": self.default_ttl,
                    "strategy": self.strategy.value
                },
                "usage": {
                    "current_entries": len(self.cache),
                    "memory_usage_mb": self.memory_usage / (1024 * 1024),
                    "memory_utilization": (self.memory_usage / self.max_memory_bytes) * 100,
                    "size_utilization": (len(self.cache) / self.max_size) * 100
                },
                "performance": {
                    "hit_rate": hit_rate,
                    "total_requests": self.stats["total_requests"],
                    "hits": self.stats["hits"],
                    "misses": self.stats["misses"],
                    "evictions": self.stats["evictions"],
                    "expired": self.stats["expired"]
                },
                "memory": {
                    "current_usage": self.memory_usage,
                    "peak_usage": self.stats["memory_peak"],
                    "average_entry_size": self.memory_usage / len(self.cache) if self.cache else 0
                }
            }
    
    def start_background_cleanup(self) -> None:
        """Start background cleanup task"""
        
        if self.cleanup_task is None or self.cleanup_task.done():
            self.cleanup_enabled = True
            self.cleanup_task = asyncio.create_task(self._background_cleanup())
            logger.info("Started background cache cleanup")
    
    def stop_background_cleanup(self) -> None:
        """Stop background cleanup task"""
        
        self.cleanup_enabled = False
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            logger.info("Stopped background cache cleanup")
    
    async def _background_cleanup(self) -> None:
        """Background cleanup task"""
        
        while self.cleanup_enabled:
            try:
                expired_count = self.cleanup_expired()
                
                # Log significant cleanups
                if expired_count > 10:
                    logger.info(f"Background cleanup removed {expired_count} expired entries")
                
                await asyncio.sleep(self.cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background cleanup error: {e}")
                await asyncio.sleep(self.cleanup_interval)


# Convenience functions for common cache patterns

def memoize(ttl: Optional[float] = None, cache_manager: Optional[CacheManager] = None):
    """Decorator to memoize function results"""
    
    def decorator(func):
        cache = cache_manager or _get_default_cache()
        
        def make_key(*args, **kwargs) -> str:
            """Create cache key from function arguments"""
            key_parts = [func.__name__]
            
            # Add positional args
            for arg in args:
                key_parts.append(str(hash(str(arg))))
            
            # Add keyword args
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}:{hash(str(v))}")
            
            return ":".join(key_parts)
        
        def wrapper(*args, **kwargs):
            key = make_key(*args, **kwargs)
            
            return cache.get_or_compute(
                key,
                lambda: func(*args, **kwargs),
                ttl
            )
        
        return wrapper
    
    return decorator


def cached_property(ttl: Optional[float] = None):
    """Decorator for caching property results"""
    
    def decorator(func):
        cache_attr = f"_cached_{func.__name__}"
        ttl_attr = f"_cached_{func.__name__}_time"
        
        def wrapper(self):
            current_time = time.time()
            
            # Check if we have cached value
            if hasattr(self, cache_attr):
                if ttl is None:
                    return getattr(self, cache_attr)
                
                # Check TTL
                cached_time = getattr(self, ttl_attr, 0)
                if current_time - cached_time < ttl:
                    return getattr(self, cache_attr)
            
            # Compute and cache value
            value = func(self)
            setattr(self, cache_attr, value)
            setattr(self, ttl_attr, current_time)
            
            return value
        
        return property(wrapper)
    
    return decorator


# Global cache instance
_default_cache: Optional[CacheManager] = None


def _get_default_cache() -> CacheManager:
    """Get or create the default cache manager"""
    global _default_cache
    if _default_cache is None:
        _default_cache = CacheManager()
    return _default_cache


def get_cache() -> CacheManager:
    """Get the default cache manager"""
    return _get_default_cache()