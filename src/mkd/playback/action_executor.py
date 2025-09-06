from typing import Optional, Any
import logging

from mkd.platforms.base import BasePlatform
from mkd.platforms.detector import get_platform

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Executes recorded actions."""

    def __init__(self):
        self.platform: BasePlatform = get_platform()
        self.browser_integration = None

    def set_browser_integration(self, integration):
        """Set browser integration for handling browser actions."""
        self.browser_integration = integration
        logger.debug("Browser integration attached to action executor")

    def execute_action(self, action) -> Any:
        """Executes a single action."""
        # Check if this is a browser action
        if hasattr(action, 'type') and action.type == 'browser':
            if not self.browser_integration:
                logger.warning("Browser action encountered but no browser integration available")
                return None
                
            # Extract browser action from MKD action data
            from ..browser.actions import BrowserAction, BrowserActionType
            from selenium.webdriver.common.by import By
            
            data = action.data
            browser_action = BrowserAction(
                type=BrowserActionType(data['browser_type']),
                target=data.get('target'),
                value=data.get('value'),
                by=getattr(By, data.get('by', 'CSS_SELECTOR').replace('By.', ''), By.CSS_SELECTOR),
                wait=data.get('wait', True),
                timestamp=action.timestamp,
                metadata=data.get('metadata', {})
            )
            
            # Execute through browser integration
            return self.browser_integration.execute_browser_action(browser_action)
        else:
            # Regular desktop action
            return self.platform.execute_action(action)
