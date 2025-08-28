"""
MKD v2.0 Exception Classes

Custom exception classes for the MKD Automation Platform.
"""


class MKDException(Exception):
    """Base exception class for MKD platform"""
    pass


class ComponentNotFoundError(MKDException):
    """Raised when a requested component is not found in the registry"""
    def __init__(self, component_name: str):
        self.component_name = component_name
        super().__init__(f"Component not found: {component_name}")


class ComponentInitializationError(MKDException):
    """Raised when a component fails to initialize"""
    def __init__(self, component_name: str, reason: str):
        self.component_name = component_name
        self.reason = reason
        super().__init__(f"Component '{component_name}' initialization failed: {reason}")


class DependencyError(MKDException):
    """Raised when component dependencies cannot be resolved"""
    def __init__(self, message: str):
        super().__init__(f"Dependency error: {message}")


class CircularDependencyError(DependencyError):
    """Raised when circular dependencies are detected"""
    def __init__(self, cycle_path: list):
        self.cycle_path = cycle_path
        cycle_str = " -> ".join(cycle_path)
        super().__init__(f"Circular dependency detected: {cycle_str}")


class RecordingError(MKDException):
    """Raised when recording operations fail"""
    def __init__(self, message: str):
        super().__init__(f"Recording error: {message}")


class PlaybackError(MKDException):
    """Raised when playback operations fail"""
    def __init__(self, message: str):
        super().__init__(f"Playback error: {message}")


class ActionExecutionError(PlaybackError):
    """Raised when a specific action fails to execute"""
    def __init__(self, action_type: str, reason: str):
        self.action_type = action_type
        self.reason = reason
        super().__init__(f"Action '{action_type}' execution failed: {reason}")


class PlatformNotSupportedError(MKDException):
    """Raised when the current platform is not supported"""
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        super().__init__(f"Platform not supported: {platform_name}")


class ConfigurationError(MKDException):
    """Raised when configuration is invalid or missing"""
    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")


class ValidationError(MKDException):
    """Raised when data validation fails"""
    def __init__(self, field: str, value: any, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Validation failed for '{field}' = {value}: {reason}")


class TimeoutError(MKDException):
    """Raised when operations timeout"""
    def __init__(self, operation: str, timeout_seconds: float):
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        super().__init__(f"Operation '{operation}' timed out after {timeout_seconds}s")


class PermissionError(MKDException):
    """Raised when insufficient permissions are detected"""
    def __init__(self, operation: str, required_permission: str):
        self.operation = operation
        self.required_permission = required_permission
        super().__init__(f"Permission denied for '{operation}': requires {required_permission}")


class SystemNotReadyError(MKDException):
    """Raised when the system is not ready for the requested operation"""
    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.reason = reason
        super().__init__(f"System not ready for '{operation}': {reason}")


class EventBusError(MKDException):
    """Raised when event bus operations fail"""
    def __init__(self, message: str):
        super().__init__(f"Event bus error: {message}")


class SerializationError(MKDException):
    """Raised when serialization/deserialization fails"""
    def __init__(self, data_type: str, operation: str, reason: str):
        self.data_type = data_type
        self.operation = operation
        self.reason = reason
        super().__init__(f"Serialization error for {data_type} during {operation}: {reason}")


class CacheError(MKDException):
    """Raised when cache operations fail"""
    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.reason = reason
        super().__init__(f"Cache error during {operation}: {reason}")


class PerformanceError(MKDException):
    """Raised when performance monitoring fails"""
    def __init__(self, metric: str, reason: str):
        self.metric = metric
        self.reason = reason
        super().__init__(f"Performance monitoring error for {metric}: {reason}")


class OptimizationError(MKDException):
    """Raised when optimization operations fail"""
    def __init__(self, optimization: str, reason: str):
        self.optimization = optimization
        self.reason = reason
        super().__init__(f"Optimization error for {optimization}: {reason}")


class ResourceError(MKDException):
    """Raised when system resources are unavailable or exhausted"""
    def __init__(self, resource: str, reason: str):
        self.resource = resource
        self.reason = reason
        super().__init__(f"Resource error for {resource}: {reason}")


class NetworkError(MKDException):
    """Raised when network operations fail"""
    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.reason = reason
        super().__init__(f"Network error during {operation}: {reason}")


class DataIntegrityError(MKDException):
    """Raised when data integrity checks fail"""
    def __init__(self, data_source: str, reason: str):
        self.data_source = data_source
        self.reason = reason
        super().__init__(f"Data integrity error in {data_source}: {reason}")


class VersionCompatibilityError(MKDException):
    """Raised when version compatibility issues are detected"""
    def __init__(self, component: str, current_version: str, required_version: str):
        self.component = component
        self.current_version = current_version
        self.required_version = required_version
        super().__init__(
            f"Version compatibility error for {component}: "
            f"current={current_version}, required={required_version}"
        )