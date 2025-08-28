"""
MKD Integration Module

Provides system-wide integration and coordination:
- System controller for unified coordination
- Component registry for automatic discovery
- Event bus for inter-component communication
- Lifecycle management for startup/shutdown
"""

from .system_controller import SystemController, SystemStatus, ComponentInfo
from .component_registry import ComponentRegistry, ComponentType, RegistrationInfo
from .event_bus import EventBus, Event, EventType, EventHandler
from .lifecycle_manager import LifecycleManager, LifecyclePhase, LifecycleHook

__all__ = [
    'SystemController',
    'SystemStatus',
    'ComponentInfo',
    'ComponentRegistry',
    'ComponentType',
    'RegistrationInfo',
    'EventBus',
    'Event',
    'EventType',
    'EventHandler',
    'LifecycleManager',
    'LifecyclePhase',
    'LifecycleHook'
]