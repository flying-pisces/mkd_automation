from mkd.platform.base import BasePlatform

class WindowsPlatform(BasePlatform):
    """Windows-specific implementation."""

    def start_capture(self, on_event):
        """Starts capturing input events."""
        # TODO: Implement using pynput
        print("Starting capture on Windows")

    def stop_capture(self):
        """Stops capturing input events."""
        # TODO: Implement using pynput
        print("Stopping capture on Windows")
