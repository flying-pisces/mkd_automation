"""
Component Registry

Automatic component discovery and management system.
Handles component registration, dependency resolution, and lifecycle coordination.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Type, Set, Callable
from enum import Enum
import inspect
import importlib
import pkgutil
import logging
import time
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class ComponentType(Enum):
    """Types of system components"""
    CORE = "core"                      # Core system components
    INTELLIGENCE = "intelligence"      # AI and intelligence components  
    PLAYBACK = "playback"             # Playbook execution components
    WEB = "web"                       # Web automation components
    PLATFORM = "platform"            # Platform-specific components
    UI = "ui"                         # User interface components
    RECORDING = "recording"           # Input recording components
    AUTOMATION = "automation"         # Automation engine components
    INTEGRATION = "integration"       # Integration components
    SERVICE = "service"               # Background services
    PLUGIN = "plugin"                 # Third-party plugins


class ComponentScope(Enum):
    """Component scope and lifecycle"""
    SINGLETON = "singleton"    # Single instance per system
    TRANSIENT = "transient"    # New instance per request
    SCOPED = "scoped"         # Instance per scope/session


@dataclass
class RegistrationInfo:
    """Component registration information"""
    component_type: ComponentType
    component_class: Type
    dependencies: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    scope: ComponentScope = ComponentScope.SINGLETON
    priority: int = 100  # Lower number = higher priority
    enabled: bool = True
    auto_start: bool = True
    health_check: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentMetadata:
    """Extended component metadata"""
    registration_time: float
    discovery_method: str  # "manual", "auto_discovery", "plugin"
    source_path: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)


class ComponentRegistry:
    """Central registry for all system components"""
    
    def __init__(self):
        self.components: Dict[str, RegistrationInfo] = {}
        self.metadata: Dict[str, ComponentMetadata] = {}
        self.instances: Dict[str, Any] = {}  # Singleton instances
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.discovery_paths: List[str] = []
        self.auto_discovery_enabled = True
        self.lock = threading.RLock()
        
        # Component factories for custom instantiation
        self.factories: Dict[str, Callable] = {}
        
        # Event callbacks
        self.registration_callbacks: List[Callable] = []
        self.unregistration_callbacks: List[Callable] = []
        
        logger.info("ComponentRegistry initialized")
    
    def register_component(self, component_id: str, 
                          registration_info: RegistrationInfo,
                          metadata: ComponentMetadata = None) -> str:
        """Register a component with the system"""
        
        with self.lock:
            if component_id in self.components:
                logger.warning(f"Component {component_id} is already registered, updating...")
            
            # Validate component class
            if not inspect.isclass(registration_info.component_class):
                raise ValueError(f"Component {component_id} must be a class")
            
            # Store registration info
            self.components[component_id] = registration_info
            
            # Store metadata
            if metadata is None:
                metadata = ComponentMetadata(
                    registration_time=time.time(),
                    discovery_method="manual"
                )
            self.metadata[component_id] = metadata
            
            # Build dependency graph
            self._update_dependency_graph(component_id, registration_info.dependencies)
            
            # Validate dependency graph for cycles
            if self._has_circular_dependencies():
                # Clean up failed registration
                del self.components[component_id]
                if component_id in self.metadata:
                    del self.metadata[component_id]
                self._rebuild_dependency_graph()
                
                # Find the cycle for better error reporting
                cycle_path = self._find_dependency_cycle()
                cycle_str = " -> ".join(cycle_path) if cycle_path else "unknown"
                raise ValueError(f"Component {component_id} creates circular dependency: {cycle_str}")
            
            logger.info(f"Component registered: {component_id} ({registration_info.component_type.value})")
            
            # Notify callbacks
            for callback in self.registration_callbacks:
                try:
                    callback(component_id, registration_info)
                except Exception as e:
                    logger.error(f"Registration callback failed: {e}")
            
            return component_id
    
    def unregister_component(self, component_id: str) -> bool:
        """Unregister a component"""
        
        with self.lock:
            if component_id not in self.components:
                return False
            
            # Remove singleton instance if exists
            if component_id in self.instances:
                instance = self.instances[component_id]
                # Try to clean up the instance
                if hasattr(instance, 'cleanup'):
                    try:
                        instance.cleanup()
                    except Exception as e:
                        logger.error(f"Error cleaning up component {component_id}: {e}")
                del self.instances[component_id]
            
            # Remove from registry
            registration_info = self.components[component_id]
            del self.components[component_id]
            del self.metadata[component_id]
            
            # Rebuild dependency graph
            self._rebuild_dependency_graph()
            
            logger.info(f"Component unregistered: {component_id}")
            
            # Notify callbacks
            for callback in self.unregistration_callbacks:
                try:
                    callback(component_id, registration_info)
                except Exception as e:
                    logger.error(f"Unregistration callback failed: {e}")
            
            return True
    
    def has_component(self, component_id: str) -> bool:
        """Check if a component is registered"""
        with self.lock:
            return component_id in self.components
    
    def get_component(self, component_id: str) -> Any:
        """Get component instance, creating if necessary"""
        
        with self.lock:
            registration_info = self.components.get(component_id)
            if not registration_info:
                from ..exceptions import ComponentNotFoundError
                raise ComponentNotFoundError(component_id)
            
            # Check if component is enabled
            if not registration_info.enabled:
                from ..exceptions import ComponentNotFoundError
                raise ComponentNotFoundError(f"{component_id} (disabled)")
            
            # Handle different scopes
            if registration_info.scope == ComponentScope.SINGLETON:
                # Return existing instance or create new one
                if component_id not in self.instances:
                    self.instances[component_id] = self._create_instance(component_id, registration_info)
                return self.instances[component_id]
            
            elif registration_info.scope == ComponentScope.TRANSIENT:
                # Always create new instance
                return self._create_instance(component_id, registration_info)
            
            elif registration_info.scope == ComponentScope.SCOPED:
                # For now, treat as singleton (can be enhanced with scope context)
                if component_id not in self.instances:
                    self.instances[component_id] = self._create_instance(component_id, registration_info)
                return self.instances[component_id]
            
            return None
    
    def _create_instance(self, component_id: str, registration_info: RegistrationInfo) -> Any:
        """Create component instance"""
        
        try:
            # Check if custom factory exists
            if component_id in self.factories:
                logger.debug(f"Using custom factory for component: {component_id}")
                return self.factories[component_id]()
            
            # Resolve dependencies
            dependencies = {}
            for dep_id in registration_info.dependencies:
                dep_instance = self.get_component(dep_id)
                if dep_instance is None:
                    raise RuntimeError(f"Failed to resolve dependency: {dep_id}")
                dependencies[dep_id] = dep_instance
            
            # Create instance with configuration and dependencies
            component_class = registration_info.component_class
            
            # Inspect constructor to determine how to pass parameters
            signature = inspect.signature(component_class.__init__)
            params = {}
            
            # Add configuration parameters
            for param_name, param in signature.parameters.items():
                if param_name in ['self']:
                    continue
                
                # Check if parameter is in configuration
                if param_name in registration_info.configuration:
                    params[param_name] = registration_info.configuration[param_name]
                # Check if parameter matches a dependency
                elif param_name in dependencies:
                    params[param_name] = dependencies[param_name]
                # Check if parameter has a default value
                elif param.default != param.empty:
                    continue  # Use default value
                else:
                    # Required parameter not provided
                    logger.warning(f"Required parameter '{param_name}' not provided for component {component_id}")
            
            # Create instance
            instance = component_class(**params)
            
            logger.debug(f"Component instance created: {component_id}")
            return instance
            
        except Exception as e:
            logger.error(f"Failed to create component instance {component_id}: {e}")
            raise RuntimeError(f"Component instantiation failed: {component_id}") from e
    
    def register_factory(self, component_id: str, factory: Callable) -> None:
        """Register a custom factory function for a component"""
        with self.lock:
            self.factories[component_id] = factory
            logger.debug(f"Custom factory registered for component: {component_id}")
    
    def get_all_components(self) -> Dict[str, RegistrationInfo]:
        """Get all registered components"""
        with self.lock:
            return self.components.copy()
    
    def get_components_by_type(self, component_type: ComponentType) -> Dict[str, RegistrationInfo]:
        """Get all components of a specific type"""
        with self.lock:
            return {
                comp_id: reg_info 
                for comp_id, reg_info in self.components.items()
                if reg_info.component_type == component_type
            }
    
    def get_dependency_order(self) -> List[str]:
        """Get components in dependency order (topological sort)"""
        with self.lock:
            return self._topological_sort()
    
    def _update_dependency_graph(self, component_id: str, dependencies: List[str]) -> None:
        """Update the dependency graph"""
        self.dependency_graph[component_id] = set(dependencies)
    
    def _rebuild_dependency_graph(self) -> None:
        """Rebuild the entire dependency graph"""
        self.dependency_graph.clear()
        for comp_id, reg_info in self.components.items():
            self.dependency_graph[comp_id] = set(reg_info.dependencies)
    
    def _has_circular_dependencies(self) -> bool:
        """Check for circular dependencies using DFS"""
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {comp_id: WHITE for comp_id in self.components}
        
        def has_cycle(node: str) -> bool:
            if colors[node] == GRAY:
                return True  # Back edge found, cycle detected
            if colors[node] == BLACK:
                return False  # Already processed
            
            colors[node] = GRAY
            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor in colors and has_cycle(neighbor):
                    return True
            colors[node] = BLACK
            return False
        
        for comp_id in self.components:
            if colors[comp_id] == WHITE:
                if has_cycle(comp_id):
                    return True
        
        return False
    
    def _find_dependency_cycle(self) -> List[str]:
        """Find and return the dependency cycle path"""
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {comp_id: WHITE for comp_id in self.components}
        path = []
        
        def find_cycle(node: str) -> List[str]:
            if colors[node] == GRAY:
                # Found back edge, cycle detected
                cycle_start = path.index(node)
                return path[cycle_start:] + [node]
            if colors[node] == BLACK:
                return []
            
            colors[node] = GRAY
            path.append(node)
            
            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor in colors:
                    cycle = find_cycle(neighbor)
                    if cycle:
                        return cycle
            
            colors[node] = BLACK
            path.remove(node)
            return []
        
        for comp_id in self.components:
            if colors[comp_id] == WHITE:
                cycle = find_cycle(comp_id)
                if cycle:
                    return cycle
        
        return []
    
    def _topological_sort(self) -> List[str]:
        """Perform topological sort of components"""
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {comp_id: WHITE for comp_id in self.components}
        result = []
        
        def visit(node: str):
            if colors[node] == GRAY:
                raise RuntimeError("Circular dependency detected")
            if colors[node] == BLACK:
                return
            
            colors[node] = GRAY
            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor in colors:
                    visit(neighbor)
            colors[node] = BLACK
            result.append(node)
        
        # Sort by priority first, then by dependencies
        priority_sorted = sorted(
            self.components.items(),
            key=lambda x: x[1].priority
        )
        
        for comp_id, _ in priority_sorted:
            if colors[comp_id] == WHITE:
                visit(comp_id)
        
        return result
    
    def auto_discover_components(self, base_package: str = "mkd_v2") -> int:
        """Automatically discover and register components"""
        
        if not self.auto_discovery_enabled:
            return 0
        
        logger.info(f"Starting auto-discovery in package: {base_package}")
        discovered_count = 0
        
        try:
            # Import base package
            base_module = importlib.import_module(base_package)
            base_path = Path(base_module.__file__).parent
            
            # Walk through all modules in the package
            for module_info in pkgutil.walk_packages([str(base_path)], f"{base_package}."):
                try:
                    module = importlib.import_module(module_info.name)
                    discovered_count += self._scan_module_for_components(module, module_info.name)
                except Exception as e:
                    logger.debug(f"Failed to scan module {module_info.name}: {e}")
            
        except Exception as e:
            logger.error(f"Auto-discovery failed: {e}")
        
        logger.info(f"Auto-discovery completed: {discovered_count} components found")
        return discovered_count
    
    def _scan_module_for_components(self, module: Any, module_name: str) -> int:
        """Scan a module for components with registration decorators"""
        discovered_count = 0
        
        for name in dir(module):
            obj = getattr(module, name)
            
            # Check if it's a class with component registration info
            if inspect.isclass(obj) and hasattr(obj, '_mkd_component_info'):
                try:
                    component_info = obj._mkd_component_info
                    
                    # Create registration info from decorator data
                    registration_info = RegistrationInfo(
                        component_type=component_info.get('type', ComponentType.CORE),
                        component_class=obj,
                        dependencies=component_info.get('dependencies', []),
                        configuration=component_info.get('config', {}),
                        scope=component_info.get('scope', ComponentScope.SINGLETON),
                        priority=component_info.get('priority', 100),
                        enabled=component_info.get('enabled', True),
                        auto_start=component_info.get('auto_start', True)
                    )
                    
                    # Create metadata
                    metadata = ComponentMetadata(
                        registration_time=time.time(),
                        discovery_method="auto_discovery",
                        source_path=module_name,
                        version=getattr(obj, '__version__', None),
                        author=getattr(obj, '__author__', None),
                        description=getattr(obj, '__doc__', None),
                        tags=component_info.get('tags', [])
                    )
                    
                    # Register component
                    component_id = f"{module_name}.{name}"
                    self.register_component(component_id, registration_info, metadata)
                    discovered_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to register discovered component {name}: {e}")
        
        return discovered_count
    
    def validate_all_dependencies(self) -> Dict[str, List[str]]:
        """Validate all component dependencies"""
        issues = {}
        
        with self.lock:
            for comp_id, reg_info in self.components.items():
                comp_issues = []
                
                for dep_id in reg_info.dependencies:
                    if dep_id not in self.components:
                        comp_issues.append(f"Missing dependency: {dep_id}")
                    elif not self.components[dep_id].enabled:
                        comp_issues.append(f"Dependency disabled: {dep_id}")
                
                if comp_issues:
                    issues[comp_id] = comp_issues
        
        return issues
    
    def get_registry_statistics(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics"""
        with self.lock:
            type_counts = {}
            for reg_info in self.components.values():
                comp_type = reg_info.component_type.value
                type_counts[comp_type] = type_counts.get(comp_type, 0) + 1
            
            scope_counts = {}
            for reg_info in self.components.values():
                scope = reg_info.scope.value
                scope_counts[scope] = scope_counts.get(scope, 0) + 1
            
            return {
                "total_components": len(self.components),
                "enabled_components": len([r for r in self.components.values() if r.enabled]),
                "singleton_instances": len(self.instances),
                "component_types": type_counts,
                "component_scopes": scope_counts,
                "dependency_issues": len(self.validate_all_dependencies()),
                "auto_discovery_enabled": self.auto_discovery_enabled
            }
    
    def add_registration_callback(self, callback: Callable[[str, RegistrationInfo], None]) -> None:
        """Add callback for component registration events"""
        self.registration_callbacks.append(callback)
    
    def add_unregistration_callback(self, callback: Callable[[str, RegistrationInfo], None]) -> None:
        """Add callback for component unregistration events"""
        self.unregistration_callbacks.append(callback)
    
    def enable_component(self, component_id: str) -> bool:
        """Enable a component"""
        with self.lock:
            if component_id in self.components:
                self.components[component_id].enabled = True
                logger.info(f"Component enabled: {component_id}")
                return True
            return False
    
    def disable_component(self, component_id: str) -> bool:
        """Disable a component"""
        with self.lock:
            if component_id in self.components:
                self.components[component_id].enabled = False
                # Remove singleton instance if exists
                if component_id in self.instances:
                    del self.instances[component_id]
                logger.info(f"Component disabled: {component_id}")
                return True
            return False


# Decorator for automatic component registration
def component(component_type: ComponentType = ComponentType.CORE,
              dependencies: List[str] = None,
              config: Dict[str, Any] = None,
              scope: ComponentScope = ComponentScope.SINGLETON,
              priority: int = 100,
              enabled: bool = True,
              auto_start: bool = True,
              tags: List[str] = None):
    """Decorator to mark a class as a system component"""
    
    def decorator(cls):
        cls._mkd_component_info = {
            'type': component_type,
            'dependencies': dependencies or [],
            'config': config or {},
            'scope': scope,
            'priority': priority,
            'enabled': enabled,
            'auto_start': auto_start,
            'tags': tags or []
        }
        return cls
    
    return decorator