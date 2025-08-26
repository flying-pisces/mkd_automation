from mkd.platform.base import BasePlatform
from mkd.platform.detector import get_platform

class InputCapturer:
    """Captures mouse and keyboard events."""

    def __init__(self):
        self.platform: BasePlatform = get_platform()

    def start_capture(self):
        """Starts capturing input events."""
        self.platform.start_capture(self._on_event)

    def stop_capture(self):
        """Stops capturing input events."""
        self.platform.stop_capture()

    def _on_event(self, event):
        """Callback function for handling captured events."""
        print(event)
