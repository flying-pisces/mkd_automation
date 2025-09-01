"""
Message Broker - Central communication hub for MKD Automation Platform v2.0.

Handles message routing between application components,
event publishing/subscribing, and command dispatch with middleware support.
"""

import asyncio
import json
import logging
import threading
import time
from typing import Dict, List, Callable, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid


logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages handled by the broker."""
    COMMAND = "command"
    EVENT = "event"
    RESPONSE = "response"
    ERROR = "error"


@dataclass
class Message:
    """Standard message format for all communications."""
    id: str
    type: MessageType
    command: Optional[str] = None
    event: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: float = 0.0
    source: str = "unknown"
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass  
class Response:
    """Standard response format."""
    id: str
    status: str  # SUCCESS, ERROR, PARTIAL
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class MessageBroker:
    """
    Central message broker for routing commands and events.
    
    Features:
    - Command routing with middleware support
    - Event publishing/subscribing
    - Asynchronous message handling
    - Error recovery and logging
    - Message validation and transformation
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.command_handlers: Dict[str, Callable] = {}
        self.middleware: List[Callable] = []
        self._running = False
        self._lock = threading.RLock()
        self._event_loop = None
        self._tasks = []
        
        # Message queues for async processing
        self._command_queue = asyncio.Queue()
        self._event_queue = asyncio.Queue()
        
        # Statistics tracking
        self.stats = {
            'messages_processed': 0,
            'commands_executed': 0,
            'events_published': 0,
            'errors_encountered': 0,
            'start_time': None
        }
        
        logger.info("MessageBroker initialized")
    
    def start(self) -> bool:
        """Start the message broker."""
        try:
            with self._lock:
                if self._running:
                    logger.warning("MessageBroker already running")
                    return True
                
                self._running = True
                self.stats['start_time'] = time.time()
                
                # Start event loop in separate thread
                self._event_loop = asyncio.new_event_loop()
                broker_thread = threading.Thread(
                    target=self._run_event_loop,
                    daemon=True,
                    name="MessageBroker"
                )
                broker_thread.start()
                
                # Start async message processors
                task1 = asyncio.run_coroutine_threadsafe(
                    self._process_commands(),
                    self._event_loop
                )
                task2 = asyncio.run_coroutine_threadsafe(
                    self._process_events(), 
                    self._event_loop
                )
                self._tasks.extend([task1, task2])
                
                logger.info("MessageBroker started successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to start MessageBroker: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the message broker gracefully."""
        try:
            with self._lock:
                if not self._running:
                    return True
                
                self._running = False
                
                if self._event_loop:
                    for task in self._tasks:
                        task.cancel()
                    
                    # Give tasks a moment to cancel
                    time.sleep(0.1)

                    self._event_loop.call_soon_threadsafe(
                        self._event_loop.stop
                    )
                
                logger.info("MessageBroker stopped")
                return True
                
        except Exception as e:
            logger.error(f"Error stopping MessageBroker: {e}")
            return False
    
    def _run_event_loop(self):
        """Run the async event loop in dedicated thread."""
        asyncio.set_event_loop(self._event_loop)
        try:
            self._event_loop.run_forever()
        except Exception as e:
            logger.error(f"Event loop error: {e}")
        finally:
            # Gather all tasks and cancel them
            tasks = asyncio.all_tasks(loop=self._event_loop)
            for task in tasks:
                task.cancel()
            
            # Wait for all tasks to be cancelled
            group = asyncio.gather(*tasks, return_exceptions=True)
            self._event_loop.run_until_complete(group)

            self._event_loop.close()
    
    async def _process_commands(self):
        """Process commands from the queue asynchronously."""
        while self._running:
            try:
                message = await asyncio.wait_for(
                    self._command_queue.get(), 
                    timeout=1.0
                )
                response = await self._execute_command(message)
                self.stats['commands_executed'] += 1
                
                # Command queue task done
                self._command_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Command processing error: {e}")
                self.stats['errors_encountered'] += 1
    
    async def _process_events(self):
        """Process events from the queue asynchronously."""
        while self._running:
            try:
                message = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=1.0
                )
                await self._publish_event(message)
                self.stats['events_published'] += 1
                
                # Event queue task done
                self._event_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event processing error: {e}")
                self.stats['errors_encountered'] += 1
    
    def subscribe(self, event_type: str, handler: Callable, priority: str = "normal"):
        """
        Subscribe to events.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Callback function to handle the event
            priority: Handler priority (high, normal, low)
        """
        with self._lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            
            # Insert based on priority
            if priority == "high":
                self.subscribers[event_type].insert(0, handler)
            else:
                self.subscribers[event_type].append(handler)
            
            logger.debug(f"Subscribed handler to {event_type} with priority {priority}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> bool:
        """
        Unsubscribe from events.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler function to remove
            
        Returns:
            True if handler was found and removed
        """
        with self._lock:
            if event_type in self.subscribers and handler in self.subscribers[event_type]:
                self.subscribers[event_type].remove(handler)
                logger.debug(f"Unsubscribed handler from {event_type}")
                return True
            return False
    
    def publish(self, event_type: str, data: Any) -> bool:
        """
        Publish an event asynchronously.
        
        Args:
            event_type: Type of event to publish
            data: Event data
            
        Returns:
            True if event was queued successfully
        """
        try:
            message = Message(
                id=str(uuid.uuid4()),
                type=MessageType.EVENT,
                event=event_type,
                data=data,
                source="message_broker"
            )
            
            if self._event_loop:
                asyncio.run_coroutine_threadsafe(
                    self._event_queue.put(message),
                    self._event_loop
                )
                return True
            else:
                # Fallback to synchronous processing
                self._publish_event_sync(message)
                return True
                
        except Exception as e:
            logger.error(f"Error publishing event {event_type}: {e}")
            self.stats['errors_encountered'] += 1
            return False
    
    async def _publish_event(self, message: Message):
        """Publish event to all subscribers."""
        if message.event not in self.subscribers:
            return
        
        for handler in self.subscribers[message.event]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message.data)
                else:
                    handler(message.data)
            except Exception as e:
                logger.error(f"Event handler error for {message.event}: {e}")
                self.stats['errors_encountered'] += 1
    
    def _publish_event_sync(self, message: Message):
        """Synchronous event publishing fallback."""
        if message.event not in self.subscribers:
            return
        
        for handler in self.subscribers[message.event]:
            try:
                handler(message.data)
            except Exception as e:
                logger.error(f"Sync event handler error for {message.event}: {e}")
                self.stats['errors_encountered'] += 1
    
    def register_command(self, command: str, handler: Callable):
        """
        Register a command handler.
        
        Args:
            command: Command name to register
            handler: Function to handle the command
        """
        with self._lock:
            self.command_handlers[command] = handler
            logger.debug(f"Registered command handler: {command}")
    
    def unregister_command(self, command: str) -> bool:
        """
        Unregister a command handler.
        
        Args:
            command: Command name to unregister
            
        Returns:
            True if command was found and removed
        """
        with self._lock:
            if command in self.command_handlers:
                del self.command_handlers[command]
                logger.debug(f"Unregistered command handler: {command}")
                return True
            return False
    
    def dispatch_command(self, message_data: Dict[str, Any]) -> Response:
        """
        Dispatch a command synchronously.
        
        Args:
            message_data: Message data containing command info
            
        Returns:
            Response object with result
        """
        try:
            # Validate message format
            if not self._validate_message(message_data):
                return Response(
                    id=message_data.get('id', str(uuid.uuid4())),
                    status='ERROR',
                    error='Invalid message format'
                )
            
            # Create message object
            message = Message(
                id=message_data['id'],
                type=MessageType.COMMAND,
                command=message_data['command'],
                data=message_data.get('params', {}),
                source=message_data.get('source', 'chrome_extension')
            )
            
            # Execute command
            if self._event_loop and self._event_loop.is_running():
                # Queue for async processing
                future = asyncio.run_coroutine_threadsafe(
                    self._execute_command(message),
                    self._event_loop
                )
                return future.result(timeout=30.0)  # 30 second timeout
            else:
                # Execute synchronously
                return self._execute_command_sync(message)
                
        except Exception as e:
            logger.error(f"Command dispatch error: {e}")
            self.stats['errors_encountered'] += 1
            return Response(
                id=message_data.get('id', str(uuid.uuid4())),
                status='ERROR',
                error=str(e)
            )
    
    async def _execute_command(self, message: Message) -> Response:
        """Execute command asynchronously."""
        try:
            # Apply middleware
            for middleware in self.middleware:
                if asyncio.iscoroutinefunction(middleware):
                    message = await middleware(message)
                else:
                    message = middleware(message)
                
                if message is None:
                    return Response(
                        id=message.id,
                        status='ERROR',
                        error='Request blocked by middleware'
                    )
            
            # Find and execute handler
            if message.command not in self.command_handlers:
                return Response(
                    id=message.id,
                    status='ERROR',
                    error=f'Unknown command: {message.command}'
                )
            
            handler = self.command_handlers[message.command]
            
            if asyncio.iscoroutinefunction(handler):
                result = await handler(message)
            else:
                result = handler(message)
            
            self.stats['messages_processed'] += 1
            
            return Response(
                id=message.id,
                status='SUCCESS',
                data=result if isinstance(result, dict) else {'result': result}
            )
            
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            self.stats['errors_encountered'] += 1
            return Response(
                id=message.id,
                status='ERROR',
                error=str(e)
            )
    
    def _execute_command_sync(self, message: Message) -> Response:
        """Execute command synchronously."""
        try:
            # Apply middleware (sync only)
            for middleware in self.middleware:
                if not asyncio.iscoroutinefunction(middleware):
                    message = middleware(message)
                    if message is None:
                        return Response(
                            id=message.id,
                            status='ERROR',
                            error='Request blocked by middleware'
                        )
            
            # Find and execute handler
            if message.command not in self.command_handlers:
                return Response(
                    id=message.id,
                    status='ERROR',
                    error=f'Unknown command: {message.command}'
                )
            
            handler = self.command_handlers[message.command]
            
            if asyncio.iscoroutinefunction(handler):
                # Cannot execute async handler synchronously
                return Response(
                    id=message.id,
                    status='ERROR',
                    error='Async handler requires async execution'
                )
            
            result = handler(message)
            self.stats['messages_processed'] += 1
            
            return Response(
                id=message.id,
                status='SUCCESS',
                data=result if isinstance(result, dict) else {'result': result}
            )
            
        except Exception as e:
            logger.error(f"Sync command execution error: {e}")
            self.stats['errors_encountered'] += 1
            return Response(
                id=message.id,
                status='ERROR',
                error=str(e)
            )
    
    def add_middleware(self, middleware: Callable):
        """
        Add middleware for command processing.
        
        Args:
            middleware: Function that takes message and returns modified message or None
        """
        self.middleware.append(middleware)
        logger.debug("Added middleware to message broker")
    
    def _validate_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Validate message format.
        
        Args:
            message_data: Raw message data
            
        Returns:
            True if message is valid
        """
        required_fields = ['id', 'command']
        
        if not isinstance(message_data, dict):
            return False
        
        for field in required_fields:
            if field not in message_data:
                return False
            if not message_data[field]:  # Check for empty strings
                return False
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get broker status and statistics."""
        uptime = (time.time() - self.stats['start_time']) if self.stats['start_time'] else 0
        
        return {
            'running': self._running,
            'uptime_seconds': uptime,
            'statistics': self.stats.copy(),
            'registered_commands': list(self.command_handlers.keys()),
            'event_subscriptions': {
                event: len(handlers) for event, handlers in self.subscribers.items()
            },
            'middleware_count': len(self.middleware)
        }
    
    def shutdown(self):
        """Shutdown the message broker gracefully."""
        logger.info("Shutting down MessageBroker...")
        
        # Stop processing
        self.stop()
        
        # Clear handlers and subscribers
        with self._lock:
            self.command_handlers.clear()
            self.subscribers.clear()
            self.middleware.clear()
        
        logger.info("MessageBroker shutdown complete")
