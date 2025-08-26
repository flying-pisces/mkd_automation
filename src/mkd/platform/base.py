from abc import ABC, abstractmethod

class BasePlatform(ABC):
    """Abstract base class for platform-specific implementations."""

    @abstractmethod
    def start_capture(self, on_event):
        """Starts capturing input events."""
        pass

    @abstractmethod
    def stop_capture(self):
        """Stops capturing input events."""
        pass
