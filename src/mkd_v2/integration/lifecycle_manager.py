"""
Lifecycle Manager

Manages system startup, shutdown, and lifecycle phases.
Coordinates proper initialization and cleanup of all system components.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum
import asyncio
import logging
import time
import threading
import signal
import sys
from pathlib import Path
import json

from .component_registry import ComponentRegistry, ComponentType
from .event_bus import EventBus, Event, EventType

logger = logging.getLogger(__name__)


class LifecyclePhase(Enum):
    """System lifecycle phases"""
    INITIALIZING = "initializing"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class LifecycleHookType(Enum):
    """Types of lifecycle hooks"""
    PRE_INIT = "pre_init"          # Before system initialization
    POST_INIT = "post_init"        # After system initialization
    PRE_START = "pre_start"        # Before system start
    POST_START = "post_start"      # After system start
    PRE_STOP = "pre_stop"          # Before system stop
    POST_STOP = "post_stop"        # After system stop
    ON_ERROR = "on_error"          # When error occurs
    ON_RECOVERY = "on_recovery"    # When recovering from error


@dataclass
class LifecycleHook:
    """Lifecycle hook definition"""
    hook_type: LifecycleHookType
    callback: Callable
    priority: int = 100  # Lower = higher priority
    async_hook: bool = False
    timeout: float = 30.0
    enabled: bool = True
    component_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseTransition:
    """Lifecycle phase transition record"""
    from_phase: LifecyclePhase
    to_phase: LifecyclePhase
    timestamp: float
    duration: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    hooks_executed: List[str] = field(default_factory=list)


class LifecycleManager:
    """Manages system lifecycle and component coordination"""
    
    def __init__(self, component_registry: ComponentRegistry, event_bus: EventBus):
        self.component_registry = component_registry
        self.event_bus = event_bus
        
        # Lifecycle state
        self.current_phase = LifecyclePhase.STOPPED
        self.phase_history: List[PhaseTransition] = []
        self.startup_time: Optional[float] = None
        self.shutdown_time: Optional[float] = None
        
        # Hook management
        self.hooks: Dict[LifecycleHookType, List[LifecycleHook]] = {
            hook_type: [] for hook_type in LifecycleHookType
        }
        
        # Error handling
        self.error_handlers: List[Callable] = []
        self.recovery_handlers: List[Callable] = []
        self.max_recovery_attempts = 3
        self.recovery_attempt_count = 0
        
        # Thread management
        self.main_thread = threading.current_thread()
        self.shutdown_event = threading.Event()
        self.lock = threading.RLock()
        
        # Configuration
        self.config = {
            "startup_timeout": 300.0,  # 5 minutes
            "shutdown_timeout": 60.0,   # 1 minute
            "hook_timeout": 30.0,       # 30 seconds
            "auto_recovery": True,
            "graceful_shutdown": True,
            "save_state": True
        }
        
        # Signal handlers
        self._setup_signal_handlers()
        
        logger.info("LifecycleManager initialized")
    
    async def initialize_system(self) -> bool:
        """Initialize the system"""
        
        try:
            await self._transition_to_phase(LifecyclePhase.INITIALIZING)
            
            # Execute pre-init hooks
            await self._execute_hooks(LifecycleHookType.PRE_INIT)
            
            # Auto-discover components
            discovery_count = self.component_registry.auto_discover_components()
            logger.info(f"Discovered {discovery_count} components")
            
            # Validate system dependencies
            dependency_issues = self.component_registry.validate_all_dependencies()
            if dependency_issues:
                logger.error(f"Dependency validation failed: {dependency_issues}")
                return False
            
            # Initialize core components first
            core_components = self.component_registry.get_components_by_type(ComponentType.CORE)
            for comp_id, reg_info in core_components.items():
                if reg_info.auto_start:
                    instance = self.component_registry.get_component(comp_id)
                    if instance and hasattr(instance, 'initialize'):
                        try:
                            if asyncio.iscoroutinefunction(instance.initialize):
                                await instance.initialize()
                            else:
                                instance.initialize()
                        except Exception as e:
                            logger.error(f"Failed to initialize component {comp_id}: {e}")
                            return False
            
            # Execute post-init hooks
            await self._execute_hooks(LifecycleHookType.POST_INIT)
            
            # Subscribe to system events
            self.event_bus.subscribe(EventType.SYSTEM_ERROR, self._handle_system_error)
            self.event_bus.subscribe(EventType.COMPONENT_FAILED, self._handle_component_failure)
            
            logger.info("System initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            await self._transition_to_phase(LifecyclePhase.ERROR)
            return False
    
    async def start_system(self) -> bool:
        """Start the system"""
        
        try:
            await self._transition_to_phase(LifecyclePhase.STARTING)
            self.startup_time = time.time()
            
            # Execute pre-start hooks
            await self._execute_hooks(LifecycleHookType.PRE_START)
            
            # Start components in dependency order
            start_order = self.component_registry.get_dependency_order()
            
            for comp_id in start_order:
                reg_info = self.component_registry.components.get(comp_id)
                if not reg_info or not reg_info.enabled or not reg_info.auto_start:
                    continue
                
                try:
                    instance = self.component_registry.get_component(comp_id)
                    if instance and hasattr(instance, 'start'):
                        if asyncio.iscoroutinefunction(instance.start):
                            await instance.start()
                        else:
                            instance.start()
                        
                        logger.debug(f"Started component: {comp_id}")
                        
                        # Publish component started event
                        await self.event_bus.publish(Event(
                            event_type=EventType.COMPONENT_STARTED,
                            data={"component_id": comp_id}
                        ))
                        
                except Exception as e:
                    logger.error(f"Failed to start component {comp_id}: {e}")
                    if reg_info.component_type == ComponentType.CORE:
                        # Core component failure is critical
                        return False
            
            # Execute post-start hooks
            await self._execute_hooks(LifecycleHookType.POST_START)
            
            # Transition to running state
            await self._transition_to_phase(LifecyclePhase.RUNNING)
            
            # Publish system started event
            await self.event_bus.publish(Event(
                event_type=EventType.SYSTEM_STARTED,
                data={
                    "startup_time": time.time() - self.startup_time,
                    "components_started": len(start_order)
                }
            ))
            
            logger.info("System started successfully")
            return True
            
        except Exception as e:
            logger.error(f"System start failed: {e}")
            await self._transition_to_phase(LifecyclePhase.ERROR)
            return False
    
    async def stop_system(self, graceful: bool = True) -> bool:
        """Stop the system"""
        
        try:
            if self.current_phase == LifecyclePhase.STOPPED:
                return True
            
            await self._transition_to_phase(LifecyclePhase.STOPPING)
            self.shutdown_time = time.time()
            
            # Signal shutdown to all threads
            self.shutdown_event.set()
            
            # Execute pre-stop hooks
            await self._execute_hooks(LifecycleHookType.PRE_STOP)
            
            # Stop components in reverse dependency order
            stop_order = list(reversed(self.component_registry.get_dependency_order()))
            
            for comp_id in stop_order:
                reg_info = self.component_registry.components.get(comp_id)
                if not reg_info:
                    continue
                
                try:
                    instance = self.component_registry.instances.get(comp_id)
                    if instance and hasattr(instance, 'stop'):
                        if asyncio.iscoroutinefunction(instance.stop):
                            await instance.stop()
                        else:
                            instance.stop()
                        
                        logger.debug(f"Stopped component: {comp_id}")
                        
                        # Publish component stopped event
                        await self.event_bus.publish(Event(
                            event_type=EventType.COMPONENT_STOPPED,
                            data={"component_id": comp_id}
                        ))
                        
                except Exception as e:
                    logger.error(f"Failed to stop component {comp_id}: {e}")
                    if not graceful:
                        continue
            
            # Execute post-stop hooks
            await self._execute_hooks(LifecycleHookType.POST_STOP)
            
            # Save system state if configured
            if self.config.get("save_state"):
                await self._save_system_state()
            
            # Transition to stopped state
            await self._transition_to_phase(LifecyclePhase.STOPPED)
            
            # Publish system stopped event
            await self.event_bus.publish(Event(
                event_type=EventType.SYSTEM_STOPPED,
                data={
                    "shutdown_time": time.time() - self.shutdown_time if self.shutdown_time else 0,
                    "graceful": graceful
                }
            ))
            
            logger.info("System stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"System stop failed: {e}")
            await self._transition_to_phase(LifecyclePhase.ERROR)
            return False
    
    async def restart_system(self) -> bool:
        """Restart the system"""
        
        logger.info("Restarting system...")
        
        # Stop the system
        if not await self.stop_system():
            logger.error("Failed to stop system for restart")
            return False
        
        # Wait a moment for cleanup
        await asyncio.sleep(1.0)
        
        # Initialize and start the system
        if not await self.initialize_system():
            logger.error("Failed to initialize system for restart")
            return False
        
        if not await self.start_system():
            logger.error("Failed to start system for restart")
            return False
        
        logger.info("System restarted successfully")
        return True
    
    def register_hook(self, hook: LifecycleHook) -> str:
        """Register a lifecycle hook"""
        
        with self.lock:
            # Generate hook ID
            hook_id = f"{hook.hook_type.value}_{len(self.hooks[hook.hook_type])}"
            
            # Add hook to appropriate list
            self.hooks[hook.hook_type].append(hook)
            
            # Sort hooks by priority
            self.hooks[hook.hook_type].sort(key=lambda h: h.priority)
            
            logger.debug(f"Registered lifecycle hook: {hook_id}")
            return hook_id
    
    def unregister_hook(self, hook_type: LifecycleHookType, hook_id: str) -> bool:
        """Unregister a lifecycle hook"""
        
        with self.lock:
            hooks_list = self.hooks.get(hook_type, [])
            
            # Find and remove hook
            for i, hook in enumerate(hooks_list):
                if getattr(hook, 'hook_id', None) == hook_id:
                    del hooks_list[i]
                    logger.debug(f"Unregistered lifecycle hook: {hook_id}")
                    return True
            
            return False
    
    async def _transition_to_phase(self, new_phase: LifecyclePhase) -> None:
        """Transition to a new lifecycle phase"""
        
        start_time = time.time()
        old_phase = self.current_phase
        
        try:
            # Update current phase
            self.current_phase = new_phase
            
            # Record transition
            transition = PhaseTransition(
                from_phase=old_phase,
                to_phase=new_phase,
                timestamp=start_time,
                duration=0.0,
                success=True
            )
            
            # Publish phase change event
            await self.event_bus.publish(Event(
                event_type=EventType.LIFECYCLE_PHASE_CHANGED,
                data={
                    "from_phase": old_phase.value,
                    "to_phase": new_phase.value,
                    "timestamp": start_time
                }
            ))
            
            # Complete transition record
            transition.duration = time.time() - start_time
            self.phase_history.append(transition)
            
            logger.info(f"Phase transition: {old_phase.value} -> {new_phase.value}")
            
        except Exception as e:
            # Handle transition failure
            transition.success = False
            transition.error_message = str(e)
            self.phase_history.append(transition)
            
            logger.error(f"Phase transition failed: {old_phase.value} -> {new_phase.value}: {e}")
            raise
    
    async def _execute_hooks(self, hook_type: LifecycleHookType) -> None:
        """Execute all hooks of a specific type"""
        
        hooks_list = self.hooks.get(hook_type, [])
        if not hooks_list:
            return
        
        logger.debug(f"Executing {len(hooks_list)} {hook_type.value} hooks")
        
        for hook in hooks_list:
            if not hook.enabled:
                continue
            
            try:
                # Execute hook with timeout
                if hook.async_hook:
                    await asyncio.wait_for(
                        hook.callback(),
                        timeout=hook.timeout
                    )
                else:
                    # Run sync hook in thread pool
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, hook.callback)
                
                logger.debug(f"Executed hook: {hook_type.value}")
                
            except asyncio.TimeoutError:
                logger.error(f"Hook timeout: {hook_type.value} (>{hook.timeout}s)")
            except Exception as e:
                logger.error(f"Hook execution failed: {hook_type.value}: {e}")
                
                # Execute error hooks
                if hook_type != LifecycleHookType.ON_ERROR:
                    await self._execute_hooks(LifecycleHookType.ON_ERROR)
    
    async def _handle_system_error(self, event: Event) -> None:
        """Handle system error events"""
        
        error_info = event.data
        logger.error(f"System error detected: {error_info}")
        
        # Execute error hooks
        await self._execute_hooks(LifecycleHookType.ON_ERROR)
        
        # Attempt recovery if configured
        if self.config.get("auto_recovery") and self.recovery_attempt_count < self.max_recovery_attempts:
            self.recovery_attempt_count += 1
            logger.info(f"Attempting system recovery (attempt {self.recovery_attempt_count})")
            
            try:
                # Execute recovery hooks
                await self._execute_hooks(LifecycleHookType.ON_RECOVERY)
                
                # Restart system
                if await self.restart_system():
                    logger.info("System recovery successful")
                    self.recovery_attempt_count = 0
                    return
                
            except Exception as e:
                logger.error(f"System recovery failed: {e}")
        
        # If recovery fails or is disabled, transition to error state
        await self._transition_to_phase(LifecyclePhase.ERROR)
    
    async def _handle_component_failure(self, event: Event) -> None:
        """Handle component failure events"""
        
        component_info = event.data
        component_id = component_info.get("component_id")
        
        logger.error(f"Component failure detected: {component_id}")
        
        # Try to restart the failed component
        try:
            reg_info = self.component_registry.components.get(component_id)
            if reg_info and reg_info.component_type == ComponentType.CORE:
                # Core component failure requires system restart
                logger.warning(f"Core component failed, restarting system: {component_id}")
                await self.restart_system()
            else:
                # Try to restart just this component
                instance = self.component_registry.get_component(component_id)
                if instance and hasattr(instance, 'restart'):
                    if asyncio.iscoroutinefunction(instance.restart):
                        await instance.restart()
                    else:
                        instance.restart()
                    
                    logger.info(f"Component restarted successfully: {component_id}")
        
        except Exception as e:
            logger.error(f"Component recovery failed: {component_id}: {e}")
    
    async def _save_system_state(self) -> None:
        """Save current system state"""
        
        try:
            state_data = {
                "current_phase": self.current_phase.value,
                "startup_time": self.startup_time,
                "components": {},
                "phase_history": [],
                "timestamp": time.time()
            }
            
            # Save component states
            for comp_id, instance in self.component_registry.instances.items():
                if hasattr(instance, 'get_state'):
                    try:
                        state_data["components"][comp_id] = instance.get_state()
                    except Exception as e:
                        logger.debug(f"Failed to get state for component {comp_id}: {e}")
            
            # Save phase history (last 100 transitions)
            for transition in self.phase_history[-100:]:
                state_data["phase_history"].append({
                    "from_phase": transition.from_phase.value,
                    "to_phase": transition.to_phase.value,
                    "timestamp": transition.timestamp,
                    "duration": transition.duration,
                    "success": transition.success,
                    "error_message": transition.error_message
                })
            
            # Write to file
            state_file = Path.home() / ".mkd" / "system_state.json"
            state_file.parent.mkdir(exist_ok=True)
            
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            logger.debug(f"System state saved to {state_file}")
            
        except Exception as e:
            logger.error(f"Failed to save system state: {e}")
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            
            # Create and run shutdown task
            loop = None
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if loop.is_running():
                # If event loop is already running, schedule the shutdown
                asyncio.create_task(self.stop_system())
            else:
                # Run shutdown in the loop
                loop.run_until_complete(self.stop_system())
        
        # Register signal handlers
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, signal_handler)
    
    def get_current_phase(self) -> LifecyclePhase:
        """Get current lifecycle phase"""
        return self.current_phase
    
    def is_running(self) -> bool:
        """Check if system is running"""
        return self.current_phase == LifecyclePhase.RUNNING
    
    def is_stopping(self) -> bool:
        """Check if system is stopping"""
        return self.current_phase == LifecyclePhase.STOPPING
    
    def get_phase_history(self) -> List[PhaseTransition]:
        """Get lifecycle phase history"""
        return self.phase_history.copy()
    
    def get_system_uptime(self) -> Optional[float]:
        """Get system uptime in seconds"""
        if self.startup_time and self.current_phase == LifecyclePhase.RUNNING:
            return time.time() - self.startup_time
        return None
    
    def get_lifecycle_statistics(self) -> Dict[str, Any]:
        """Get comprehensive lifecycle statistics"""
        
        phase_counts = {}
        for transition in self.phase_history:
            phase = transition.to_phase.value
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        total_transitions = len(self.phase_history)
        failed_transitions = len([t for t in self.phase_history if not t.success])
        
        return {
            "current_phase": self.current_phase.value,
            "uptime_seconds": self.get_system_uptime(),
            "total_phase_transitions": total_transitions,
            "failed_transitions": failed_transitions,
            "success_rate": (total_transitions - failed_transitions) / max(total_transitions, 1) * 100,
            "phase_distribution": phase_counts,
            "recovery_attempts": self.recovery_attempt_count,
            "hooks_registered": sum(len(hooks) for hooks in self.hooks.values()),
            "auto_recovery_enabled": self.config.get("auto_recovery", False)
        }


# Convenience hook decorators
def lifecycle_hook(hook_type: LifecycleHookType, 
                  priority: int = 100,
                  timeout: float = 30.0,
                  async_hook: bool = False):
    """Decorator to mark a function as a lifecycle hook"""
    
    def decorator(func):
        func._mkd_lifecycle_hook = LifecycleHook(
            hook_type=hook_type,
            callback=func,
            priority=priority,
            timeout=timeout,
            async_hook=async_hook
        )
        return func
    
    return decorator


# Hook type aliases for convenience
pre_init = lambda **kwargs: lifecycle_hook(LifecycleHookType.PRE_INIT, **kwargs)
post_init = lambda **kwargs: lifecycle_hook(LifecycleHookType.POST_INIT, **kwargs)
pre_start = lambda **kwargs: lifecycle_hook(LifecycleHookType.PRE_START, **kwargs)
post_start = lambda **kwargs: lifecycle_hook(LifecycleHookType.POST_START, **kwargs)
pre_stop = lambda **kwargs: lifecycle_hook(LifecycleHookType.PRE_STOP, **kwargs)
post_stop = lambda **kwargs: lifecycle_hook(LifecycleHookType.POST_STOP, **kwargs)
on_error = lambda **kwargs: lifecycle_hook(LifecycleHookType.ON_ERROR, **kwargs)
on_recovery = lambda **kwargs: lifecycle_hook(LifecycleHookType.ON_RECOVERY, **kwargs)