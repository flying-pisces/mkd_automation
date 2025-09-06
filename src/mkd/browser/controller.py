"""
Browser controller for automated web interactions.
"""
import time
import logging
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)


class BrowserType(Enum):
    """Supported browser types."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"


@dataclass
class BrowserConfig:
    """Browser configuration."""
    browser_type: BrowserType = BrowserType.CHROME
    headless: bool = False
    window_size: Tuple[int, int] = (1920, 1080)
    implicit_wait: int = 10
    page_load_timeout: int = 30
    user_data_dir: Optional[str] = None
    profile: Optional[str] = None
    extensions: List[str] = None


class BrowserController:
    """
    Controls browser automation for web interactions.
    
    This controller provides methods to:
    - Navigate to URLs
    - Interact with web elements (click, type, select)
    - Execute JavaScript
    - Handle alerts and popups
    - Take screenshots
    - Record and replay browser actions
    """
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        """Initialize browser controller with configuration."""
        self.config = config or BrowserConfig()
        self.driver: Optional[webdriver.Remote] = None
        self.wait: Optional[WebDriverWait] = None
        self._is_active = False
        
    def start(self) -> None:
        """Start the browser driver."""
        if self._is_active:
            logger.warning("Browser controller already active")
            return
            
        try:
            self.driver = self._create_driver()
            self.wait = WebDriverWait(self.driver, self.config.implicit_wait)
            self._is_active = True
            logger.info(f"Browser controller started with {self.config.browser_type.value}")
        except Exception as e:
            logger.error(f"Failed to start browser controller: {e}")
            raise
            
    def stop(self) -> None:
        """Stop the browser driver."""
        if not self._is_active:
            return
            
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.wait = None
            self._is_active = False
            logger.info("Browser controller stopped")
        except Exception as e:
            logger.error(f"Error stopping browser controller: {e}")
            
    def _create_driver(self) -> webdriver.Remote:
        """Create appropriate webdriver based on configuration."""
        if self.config.browser_type == BrowserType.CHROME:
            return self._create_chrome_driver()
        elif self.config.browser_type == BrowserType.FIREFOX:
            return self._create_firefox_driver()
        elif self.config.browser_type == BrowserType.EDGE:
            return self._create_edge_driver()
        else:
            raise ValueError(f"Unsupported browser type: {self.config.browser_type}")
            
    def _create_chrome_driver(self) -> webdriver.Chrome:
        """Create Chrome webdriver with options."""
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = Options()
        
        if self.config.headless:
            options.add_argument("--headless")
            
        options.add_argument(f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}")
        
        if self.config.user_data_dir:
            options.add_argument(f"--user-data-dir={self.config.user_data_dir}")
            
        if self.config.profile:
            options.add_argument(f"--profile-directory={self.config.profile}")
            
        if self.config.extensions:
            for ext_path in self.config.extensions:
                options.add_extension(ext_path)
                
        # Additional useful options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Set timeouts
        driver.set_page_load_timeout(self.config.page_load_timeout)
        driver.implicitly_wait(self.config.implicit_wait)
        
        return driver
        
    def _create_firefox_driver(self) -> webdriver.Firefox:
        """Create Firefox webdriver with options."""
        from selenium.webdriver.firefox.service import Service
        from selenium.webdriver.firefox.options import Options
        from webdriver_manager.firefox import GeckoDriverManager
        
        options = Options()
        
        if self.config.headless:
            options.add_argument("--headless")
            
        options.add_argument(f"--width={self.config.window_size[0]}")
        options.add_argument(f"--height={self.config.window_size[1]}")
        
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        
        driver.set_page_load_timeout(self.config.page_load_timeout)
        driver.implicitly_wait(self.config.implicit_wait)
        
        return driver
        
    def _create_edge_driver(self) -> webdriver.Edge:
        """Create Edge webdriver with options."""
        from selenium.webdriver.edge.service import Service
        from selenium.webdriver.edge.options import Options
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        
        options = Options()
        
        if self.config.headless:
            options.add_argument("--headless")
            
        options.add_argument(f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}")
        
        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        
        driver.set_page_load_timeout(self.config.page_load_timeout)
        driver.implicitly_wait(self.config.implicit_wait)
        
        return driver
        
    def navigate(self, url: str) -> None:
        """Navigate to a URL."""
        if not self._is_active:
            raise RuntimeError("Browser controller not active")
            
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)
        
    def click(self, selector: str, by: By = By.CSS_SELECTOR, wait: bool = True) -> None:
        """Click on an element."""
        element = self._find_element(selector, by, wait)
        element.click()
        logger.debug(f"Clicked element: {selector}")
        
    def type_text(self, selector: str, text: str, by: By = By.CSS_SELECTOR, 
                  clear: bool = True, wait: bool = True) -> None:
        """Type text into an element."""
        element = self._find_element(selector, by, wait)
        
        if clear:
            element.clear()
            
        element.send_keys(text)
        logger.debug(f"Typed text into element: {selector}")
        
    def get_text(self, selector: str, by: By = By.CSS_SELECTOR, wait: bool = True) -> str:
        """Get text from an element."""
        element = self._find_element(selector, by, wait)
        return element.text
        
    def get_attribute(self, selector: str, attribute: str, 
                     by: By = By.CSS_SELECTOR, wait: bool = True) -> str:
        """Get attribute value from an element."""
        element = self._find_element(selector, by, wait)
        return element.get_attribute(attribute)
        
    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript in the browser."""
        if not self._is_active:
            raise RuntimeError("Browser controller not active")
            
        return self.driver.execute_script(script, *args)
        
    def take_screenshot(self, filename: str = None) -> bytes:
        """Take a screenshot of the current page."""
        if not self._is_active:
            raise RuntimeError("Browser controller not active")
            
        if filename:
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved to: {filename}")
            
        return self.driver.get_screenshot_as_png()
        
    def wait_for_element(self, selector: str, by: By = By.CSS_SELECTOR, 
                        timeout: int = 10) -> None:
        """Wait for an element to be present."""
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.presence_of_element_located((by, selector)))
        
    def wait_for_url_change(self, timeout: int = 10) -> None:
        """Wait for URL to change from current."""
        current_url = self.driver.current_url
        
        def url_changed(driver):
            return driver.current_url != current_url
            
        wait = WebDriverWait(self.driver, timeout)
        wait.until(url_changed)
        
    def _find_element(self, selector: str, by: By = By.CSS_SELECTOR, wait: bool = True):
        """Find an element with optional wait."""
        if not self._is_active:
            raise RuntimeError("Browser controller not active")
            
        if wait and self.wait:
            return self.wait.until(
                EC.presence_of_element_located((by, selector))
            )
        else:
            return self.driver.find_element(by, selector)
            
    def get_current_url(self) -> str:
        """Get the current URL."""
        if not self._is_active:
            raise RuntimeError("Browser controller not active")
            
        return self.driver.current_url
        
    def get_page_title(self) -> str:
        """Get the current page title."""
        if not self._is_active:
            raise RuntimeError("Browser controller not active")
            
        return self.driver.title
        
    def switch_to_frame(self, frame_reference):
        """Switch to an iframe."""
        if not self._is_active:
            raise RuntimeError("Browser controller not active")
            
        self.driver.switch_to.frame(frame_reference)
        
    def switch_to_default_content(self):
        """Switch back to default content from iframe."""
        if not self._is_active:
            raise RuntimeError("Browser controller not active")
            
        self.driver.switch_to.default_content()
        
    def handle_alert(self, accept: bool = True, text: str = None) -> str:
        """Handle JavaScript alert."""
        if not self._is_active:
            raise RuntimeError("Browser controller not active")
            
        alert = self.driver.switch_to.alert
        alert_text = alert.text
        
        if text:
            alert.send_keys(text)
            
        if accept:
            alert.accept()
        else:
            alert.dismiss()
            
        return alert_text