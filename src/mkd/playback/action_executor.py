from mkd.platform.base import BasePlatform
from mkd.platform.detector import get_platform

class ActionExecutor:
    """Executes recorded actions."""

    def __init__(self):
        self.platform: BasePlatform = get_platform()

    def execute_action(self, action):
        """Executes a single action."""
        self.platform.execute_action(action)
