from mkd.platform.base import BasePlatform

class MacOSPlatform(BasePlatform):
    """macOS-specific implementation."""

    def start_capture(self, on_event):
        """Starts capturing input events."""
        # TODO: Implement using pynput
        print("Starting capture on macOS")

    def stop_capture(self):
        """Stops capturing input events."""
        # TODO: Implement using pynput
        print("Stopping capture on macOS")
