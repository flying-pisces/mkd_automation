"""
Event Bus

Inter-component communication system using publish-subscribe pattern.
Provides loose coupling between components with reliable event delivery.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Union, Set
from enum import Enum
import time
import asyncio
import threading
import logging
import uuid
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


class EventType(Enum):
    """System event types"""
    # System lifecycle events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_STARTED = "system.started"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_STOPPED = "system.stopped"
    SYSTEM_ERROR = "system.error"
    LIFECYCLE_PHASE_CHANGED = "lifecycle.phase_changed"
    
    # Component lifecycle events
    COMPONENT_STARTED = "component.started"
    COMPONENT_STOPPED = "component.stopped" 
    COMPONENT_FAILED = "component.failed"
    COMPONENT_ERROR = "component.error"
    COMPONENT_HEALTH_CHECK = "component.health_check"
    
    # Automation events
    RECORDING_STARTED = "recording.started"
    RECORDING_STOPPED = "recording.stopped"
    PLAYBACK_STARTED = "playback.started"
    PLAYBACK_STOPPED = "playback.stopped"
    ACTION_EXECUTED = "action.executed"
    ACTION_FAILED = "action.failed"
    
    # Intelligence events
    CONTEXT_CHANGED = "context.changed"
    PATTERN_DETECTED = "pattern.detected"
    SUGGESTION_GENERATED = "suggestion.generated"
    
    # Web automation events
    BROWSER_OPENED = "browser.opened"
    BROWSER_CLOSED = "browser.closed"
    TAB_CREATED = "tab.created"
    TAB_CLOSED = "tab.closed"
    SCRIPT_INJECTED = "script.injected"
    
    # Performance and monitoring events
    PERFORMANCE_METRIC = "performance.metric"
    HEALTH_CHECK = "health.check"
    ERROR_REPORTED = "error.reported"
    
    # User interface events
    UI_COMMAND = "ui.command"
    UI_NOTIFICATION = "ui.notification"
    
    # Custom events
    CUSTOM = "custom"


class EventPriority(Enum):
    """Event priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class Event:
    """Event message"""
    event_type: EventType
    data: Dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    source: Optional[str] = None
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Subscription:
    """Event subscription"""
    subscription_id: str
    event_type: EventType
    handler: Callable[[Event], Any]
    subscriber_id: str
    filter_func: Optional[Callable[[Event], bool]] = None
    created_at: float = field(default_factory=time.time)
    active: bool = True
    delivery_count: int = 0
    last_delivery: Optional[float] = None


@dataclass
class EventStats:
    """Event statistics"""
    total_published: int = 0
    total_delivered: int = 0
    failed_deliveries: int = 0
    avg_delivery_time: float = 0.0
    queue_size: int = 0
    active_subscriptions: int = 0


class EventHandler:
    """Base class for event handlers"""
    
    def __init__(self, handler_id: str = None):
        self.handler_id = handler_id or str(uuid.uuid4())
        self.handled_events = 0
        self.last_handled: Optional[float] = None
        self.errors = 0
    
    async def handle_event(self, event: Event) -> Any:
        """Handle an event (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement handle_event")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics"""
        return {
            "handler_id": self.handler_id,
            "handled_events": self.handled_events,
            "last_handled": self.last_handled,
            "errors": self.errors
        }


class EventBus:
    """Central event bus for inter-component communication"""
    
    def __init__(self, max_queue_size: int = 10000):
        self.max_queue_size = max_queue_size
        
        # Event storage and queuing
        self.event_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.priority_queues: Dict[EventPriority, deque] = {
            priority: deque() for priority in EventPriority
        }
        
        # Subscriptions
        self.subscriptions: Dict[EventType, List[Subscription]] = defaultdict(list)
        self.subscribers: Dict[str, List[str]] = defaultdict(list)  # subscriber_id -> subscription_ids
        
        # Event processing
        self.running = False
        self.auto_start_attempted = False
        self.processor_task: Optional[asyncio.Task] = None
        self.delivery_tasks: Set[asyncio.Task] = set()
        
        # Statistics and monitoring
        self.stats = EventStats()
        self.event_history: deque = deque(maxlen=1000)  # Keep last 1000 events
        self.failed_events: deque = deque(maxlen=100)   # Keep last 100 failed events
        
        # Configuration
        self.retry_attempts = 3
        self.retry_delay = 1.0
        self.delivery_timeout = 30.0
        
        # Thread safety
        self.lock = asyncio.Lock()
        
        logger.info("EventBus initialized")
    
    async def ensure_started(self) -> None:
        """Ensure the event bus is started"""
        if not self.running and not self.auto_start_attempted:
            self.auto_start_attempted = True
            try:
                await self.start()
            except Exception as e:
                logger.error(f"Failed to auto-start EventBus: {e}")
                self.auto_start_attempted = False
    
    async def start(self) -> None:
        """Start the event bus"""
        if self.running:
            logger.warning("EventBus is already running")
            return
        
        logger.info("Starting EventBus...")
        self.running = True
        
        # Start event processor
        self.processor_task = asyncio.create_task(self._event_processor())
        
        logger.info("EventBus started")
    
    async def stop(self) -> None:
        """Stop the event bus"""
        if not self.running:
            return
        
        logger.info("Stopping EventBus...")
        self.running = False
        
        # Cancel processor task
        if self.processor_task and not self.processor_task.done():
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass
        
        # Cancel delivery tasks
        for task in list(self.delivery_tasks):
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.delivery_tasks.clear()
        
        logger.info("EventBus stopped")
    
    async def publish(self, event: Event) -> bool:
        """Publish an event to the bus"""
        # Ensure event bus is started before publishing
        if not self.running:
            await self.ensure_started()
        
        if not self.running:
            logger.warning("Cannot publish event: EventBus failed to start")
            return False
        
        try:
            # Add event to appropriate queue based on priority
            if event.priority == EventPriority.CRITICAL:
                # Critical events bypass queue size limits
                self.priority_queues[EventPriority.CRITICAL].appendleft(event)
            else:
                # Check queue size for non-critical events
                if self.event_queue.qsize() >= self.max_queue_size:
                    logger.warning("Event queue is full, dropping event")
                    return False
                
                await self.event_queue.put(event)
            
            self.stats.total_published += 1
            self.event_history.append(event)
            
            logger.debug(f"Event published: {event.event_type.value} (ID: {event.event_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False
    
    def publish_sync(self, event: Event) -> bool:
        """Synchronously publish an event (creates async task)"""
        if not self.running:
            return False
        
        try:
            # Create task to publish event
            loop = asyncio.get_event_loop()
            task = loop.create_task(self.publish(event))
            return True
        except Exception as e:
            logger.error(f"Failed to create publish task: {e}")
            return False
    
    def subscribe(self, event_type: EventType, 
                  handler: Callable[[Event], Any],
                  subscriber_id: str = None,
                  filter_func: Callable[[Event], bool] = None) -> str:
        """Subscribe to events of a specific type"""
        
        subscription_id = str(uuid.uuid4())
        subscriber_id = subscriber_id or f"subscriber_{subscription_id[:8]}"
        
        subscription = Subscription(
            subscription_id=subscription_id,
            event_type=event_type,
            handler=handler,
            subscriber_id=subscriber_id,
            filter_func=filter_func
        )
        
        # Add to subscriptions
        self.subscriptions[event_type].append(subscription)
        self.subscribers[subscriber_id].append(subscription_id)
        
        self.stats.active_subscriptions += 1
        
        logger.debug(f"Subscription created: {event_type.value} (ID: {subscription_id})")
        return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events"""
        
        # Find and remove subscription
        for event_type, subs in self.subscriptions.items():
            for i, sub in enumerate(subs):
                if sub.subscription_id == subscription_id:
                    # Remove from subscriptions
                    del subs[i]
                    
                    # Remove from subscribers
                    subscriber_subs = self.subscribers[sub.subscriber_id]
                    if subscription_id in subscriber_subs:
                        subscriber_subs.remove(subscription_id)
                    
                    # Clean up empty subscriber entries
                    if not subscriber_subs:
                        del self.subscribers[sub.subscriber_id]
                    
                    self.stats.active_subscriptions -= 1
                    
                    logger.debug(f"Subscription removed: {subscription_id}")
                    return True
        
        logger.warning(f"Subscription not found: {subscription_id}")
        return False
    
    def unsubscribe_all(self, subscriber_id: str) -> int:
        """Unsubscribe all subscriptions for a subscriber"""
        
        subscriber_subs = self.subscribers.get(subscriber_id, [])
        removed_count = 0
        
        for subscription_id in subscriber_subs.copy():
            if self.unsubscribe(subscription_id):
                removed_count += 1
        
        logger.info(f"Removed {removed_count} subscriptions for subscriber: {subscriber_id}")
        return removed_count
    
    async def _event_processor(self) -> None:
        """Background event processing loop"""
        logger.info("Event processor started")
        
        while self.running:
            try:
                # Process critical events first
                await self._process_priority_events()
                
                # Process regular events
                try:
                    event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                    await self._deliver_event(event)
                except asyncio.TimeoutError:
                    continue  # No events, continue loop
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event processor error: {e}")
                await asyncio.sleep(1.0)
        
        logger.info("Event processor stopped")
    
    async def _process_priority_events(self) -> None:
        """Process priority events from priority queues"""
        
        # Process in priority order
        for priority in [EventPriority.CRITICAL, EventPriority.HIGH]:
            queue = self.priority_queues[priority]
            
            while queue:
                event = queue.popleft()
                await self._deliver_event(event)
    
    async def _deliver_event(self, event: Event) -> None:
        """Deliver event to all subscribers"""
        
        start_time = time.time()
        subscriptions = self.subscriptions.get(event.event_type, [])
        
        if not subscriptions:
            logger.debug(f"No subscribers for event: {event.event_type.value}")
            return
        
        # Create delivery tasks for all subscriptions
        delivery_tasks = []
        
        for subscription in subscriptions:
            if subscription.active:
                # Apply filter if specified
                if subscription.filter_func and not subscription.filter_func(event):
                    continue
                
                task = asyncio.create_task(
                    self._deliver_to_subscription(event, subscription)
                )
                delivery_tasks.append(task)
                self.delivery_tasks.add(task)
        
        # Wait for all deliveries to complete
        if delivery_tasks:
            results = await asyncio.gather(*delivery_tasks, return_exceptions=True)
            
            # Process results
            delivered_count = 0
            for i, result in enumerate(results):
                task = delivery_tasks[i]
                self.delivery_tasks.discard(task)
                
                if isinstance(result, Exception):
                    logger.error(f"Event delivery failed: {result}")
                    self.stats.failed_deliveries += 1
                    
                    # Store failed event for debugging
                    self.failed_events.append({
                        'event': event,
                        'subscription_id': subscriptions[i].subscription_id,
                        'error': str(result),
                        'timestamp': time.time()
                    })
                else:
                    delivered_count += 1
            
            self.stats.total_delivered += delivered_count
            
            # Update delivery time statistics
            delivery_time = time.time() - start_time
            if self.stats.total_delivered > 0:
                self.stats.avg_delivery_time = (
                    (self.stats.avg_delivery_time * (self.stats.total_delivered - delivered_count) +
                     delivery_time * delivered_count) / self.stats.total_delivered
                )
            
            logger.debug(f"Event delivered: {event.event_type.value} to {delivered_count} subscribers")
    
    async def _deliver_to_subscription(self, event: Event, subscription: Subscription) -> None:
        """Deliver event to a single subscription with retry logic"""
        
        for attempt in range(self.retry_attempts):
            try:
                # Execute handler with timeout
                if asyncio.iscoroutinefunction(subscription.handler):
                    await asyncio.wait_for(
                        subscription.handler(event),
                        timeout=self.delivery_timeout
                    )
                else:
                    # Run synchronous handler in thread pool
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, subscription.handler, event)
                
                # Update subscription stats
                subscription.delivery_count += 1
                subscription.last_delivery = time.time()
                
                return  # Successful delivery
                
            except asyncio.TimeoutError:
                logger.warning(f"Event delivery timeout: {subscription.subscription_id}")
                if attempt == self.retry_attempts - 1:
                    raise
                
            except Exception as e:
                logger.error(f"Event delivery error (attempt {attempt + 1}): {e}")
                if attempt == self.retry_attempts - 1:
                    raise
                
                # Wait before retry
                await asyncio.sleep(self.retry_delay * (attempt + 1))
    
    def get_queue_size(self) -> int:
        """Get current event queue size"""
        regular_size = self.event_queue.qsize()
        priority_size = sum(len(queue) for queue in self.priority_queues.values())
        return regular_size + priority_size
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive event bus statistics"""
        self.stats.queue_size = self.get_queue_size()
        
        # Calculate subscription stats by event type
        subscription_stats = {}
        for event_type, subs in self.subscriptions.items():
            active_subs = [s for s in subs if s.active]
            subscription_stats[event_type.value] = {
                "total": len(subs),
                "active": len(active_subs),
                "total_deliveries": sum(s.delivery_count for s in active_subs)
            }
        
        return {
            "running": self.running,
            "queue_size": self.stats.queue_size,
            "max_queue_size": self.max_queue_size,
            "total_published": self.stats.total_published,
            "total_delivered": self.stats.total_delivered,
            "failed_deliveries": self.stats.failed_deliveries,
            "avg_delivery_time_ms": self.stats.avg_delivery_time * 1000,
            "active_subscriptions": self.stats.active_subscriptions,
            "subscription_stats": subscription_stats,
            "recent_events": len(self.event_history),
            "failed_events": len(self.failed_events),
            "active_delivery_tasks": len(self.delivery_tasks)
        }
    
    def get_recent_events(self, limit: int = 100) -> List[Event]:
        """Get recent events from history"""
        return list(self.event_history)[-limit:]
    
    def get_failed_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent failed events"""
        return list(self.failed_events)[-limit:]
    
    def get_subscriptions(self, event_type: EventType = None) -> List[Subscription]:
        """Get subscriptions, optionally filtered by event type"""
        if event_type:
            return self.subscriptions.get(event_type, [])
        
        all_subscriptions = []
        for subs in self.subscriptions.values():
            all_subscriptions.extend(subs)
        return all_subscriptions
    
    async def wait_for_event(self, event_type: EventType, 
                            timeout: float = 10.0,
                            filter_func: Callable[[Event], bool] = None) -> Optional[Event]:
        """Wait for a specific event to occur"""
        
        result_event = None
        event_received = asyncio.Event()
        
        def handler(event: Event):
            nonlocal result_event
            if not filter_func or filter_func(event):
                result_event = event
                event_received.set()
        
        # Subscribe temporarily
        subscription_id = self.subscribe(event_type, handler, f"waiter_{uuid.uuid4()}")
        
        try:
            # Wait for event or timeout
            await asyncio.wait_for(event_received.wait(), timeout=timeout)
            return result_event
        except asyncio.TimeoutError:
            return None
        finally:
            # Clean up subscription
            self.unsubscribe(subscription_id)
    
    def create_event(self, event_type: EventType, 
                    data: Dict[str, Any],
                    source: str = None,
                    priority: EventPriority = EventPriority.NORMAL,
                    correlation_id: str = None) -> Event:
        """Create a new event with specified parameters"""
        
        return Event(
            event_type=event_type,
            data=data,
            source=source,
            priority=priority,
            correlation_id=correlation_id
        )