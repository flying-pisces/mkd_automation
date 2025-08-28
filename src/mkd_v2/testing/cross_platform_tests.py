"""
Cross-Platform Tests

Platform compatibility validation across macOS, Windows, Linux
with browser support and hardware compatibility testing.
"""

import sys
import os
import platform
import subprocess
import logging
import asyncio
import time
import psutil
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Tuple
from enum import Enum
from pathlib import Path
import tempfile
import json

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported platforms"""
    MACOS = "macos"
    WINDOWS = "windows"  
    LINUX = "linux"
    UNKNOWN = "unknown"


class Browser(Enum):
    """Supported browsers"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"


class TestResult(Enum):
    """Platform test results"""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class PlatformInfo:
    """Platform information"""
    platform: Platform
    system: str
    release: str
    version: str
    machine: str
    processor: str
    architecture: str
    python_version: str
    available_memory_gb: float
    cpu_count: int
    disk_space_gb: float
    
    @classmethod
    def detect_current(cls) -> 'PlatformInfo':
        """Detect current platform information"""
        
        # Determine platform
        system_name = platform.system().lower()
        if system_name == "darwin":
            detected_platform = Platform.MACOS
        elif system_name == "windows":
            detected_platform = Platform.WINDOWS
        elif system_name == "linux":
            detected_platform = Platform.LINUX
        else:
            detected_platform = Platform.UNKNOWN
        
        # Get memory info
        memory_info = psutil.virtual_memory()
        available_memory_gb = memory_info.available / (1024**3)
        
        # Get disk info
        disk_info = psutil.disk_usage('/')
        disk_space_gb = disk_info.free / (1024**3)
        
        return cls(
            platform=detected_platform,
            system=platform.system(),
            release=platform.release(),
            version=platform.version(),
            machine=platform.machine(),
            processor=platform.processor(),
            architecture=platform.architecture()[0],
            python_version=platform.python_version(),
            available_memory_gb=available_memory_gb,
            cpu_count=psutil.cpu_count(),
            disk_space_gb=disk_space_gb
        )


@dataclass
class PlatformTest:
    """Individual platform compatibility test"""
    name: str
    description: str
    test_function: Callable
    target_platforms: List[Platform] = field(default_factory=lambda: list(Platform))
    required_browsers: List[Browser] = field(default_factory=list)
    min_memory_gb: float = 1.0
    min_disk_space_gb: float = 1.0
    requires_admin: bool = False
    requires_network: bool = False
    timeout: float = 60.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestExecutionResult:
    """Result of executing a platform test"""
    test_name: str
    platform: PlatformInfo
    result: TestResult
    start_time: float
    end_time: float
    duration: float
    output: str = ""
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class CrossPlatformValidator:
    """Cross-platform compatibility validation system"""
    
    def __init__(self):
        self.current_platform = PlatformInfo.detect_current()
        self.registered_tests: Dict[str, PlatformTest] = {}
        self.test_results: List[TestExecutionResult] = []
        
        # Browser detection
        self.available_browsers = self._detect_browsers()
        
        # Test configuration
        self.config = {
            "run_platform_specific_only": False,
            "skip_admin_tests": False,
            "skip_network_tests": False,
            "timeout_multiplier": 1.0,
            "detailed_logging": True
        }
        
        # Register built-in tests
        self._register_builtin_tests()
        
        logger.info(f"CrossPlatformValidator initialized on {self.current_platform.platform.value}")
    
    def _detect_browsers(self) -> List[Browser]:
        """Detect available browsers on current platform"""
        
        available = []
        
        try:
            # Chrome detection
            chrome_paths = {
                Platform.MACOS: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                Platform.WINDOWS: r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                Platform.LINUX: "/usr/bin/google-chrome"
            }
            
            chrome_path = chrome_paths.get(self.current_platform.platform)
            if chrome_path and Path(chrome_path).exists():
                available.append(Browser.CHROME)
            
            # Firefox detection  
            firefox_paths = {
                Platform.MACOS: "/Applications/Firefox.app/Contents/MacOS/firefox",
                Platform.WINDOWS: r"C:\Program Files\Mozilla Firefox\firefox.exe",
                Platform.LINUX: "/usr/bin/firefox"
            }
            
            firefox_path = firefox_paths.get(self.current_platform.platform)
            if firefox_path and Path(firefox_path).exists():
                available.append(Browser.FIREFOX)
            
            # Safari detection (macOS only)
            if self.current_platform.platform == Platform.MACOS:
                safari_path = "/Applications/Safari.app/Contents/MacOS/Safari"
                if Path(safari_path).exists():
                    available.append(Browser.SAFARI)
            
            # Edge detection (Windows only)
            if self.current_platform.platform == Platform.WINDOWS:
                edge_paths = [
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
                ]
                for edge_path in edge_paths:
                    if Path(edge_path).exists():
                        available.append(Browser.EDGE)
                        break
                        
        except Exception as e:
            logger.debug(f"Browser detection error: {e}")
        
        logger.info(f"Available browsers: {[b.value for b in available]}")
        return available
    
    def register_test(self, test: PlatformTest) -> str:
        """Register a platform compatibility test"""
        
        test_id = f"{test.name}_{id(test)}"
        self.registered_tests[test_id] = test
        
        logger.debug(f"Registered platform test: {test.name}")
        return test_id
    
    async def run_all_tests(self, platform_filter: Platform = None) -> Dict[str, Any]:
        """Run all registered platform tests"""
        
        start_time = time.time()
        results = []
        
        # Filter tests for current platform
        applicable_tests = []
        for test_id, test in self.registered_tests.items():
            # Check platform compatibility
            if platform_filter and platform_filter != self.current_platform.platform:
                continue
            
            if (not test.target_platforms or 
                self.current_platform.platform in test.target_platforms):
                applicable_tests.append((test_id, test))
        
        logger.info(f"Running {len(applicable_tests)} platform compatibility tests")
        
        # Run tests
        for test_id, test in applicable_tests:
            result = await self._execute_test(test_id, test)
            results.append(result)
            self.test_results.append(result)
        
        # Compile results
        end_time = time.time()
        total_duration = end_time - start_time
        
        summary = {
            "platform": {
                "system": self.current_platform.system,
                "platform": self.current_platform.platform.value,
                "version": self.current_platform.version,
                "architecture": self.current_platform.architecture,
                "python_version": self.current_platform.python_version
            },
            "execution": {
                "start_time": start_time,
                "end_time": end_time,
                "duration": total_duration,
                "total_tests": len(applicable_tests)
            },
            "results": {
                "passed": len([r for r in results if r.result == TestResult.PASS]),
                "failed": len([r for r in results if r.result == TestResult.FAIL]),
                "skipped": len([r for r in results if r.result == TestResult.SKIP]),
                "errors": len([r for r in results if r.result == TestResult.ERROR]),
                "not_applicable": len([r for r in results if r.result == TestResult.NOT_APPLICABLE])
            },
            "test_results": results,
            "available_browsers": [b.value for b in self.available_browsers],
            "system_requirements_met": self._check_system_requirements()
        }
        
        success_rate = (summary["results"]["passed"] / max(len(applicable_tests), 1)) * 100
        summary["success_rate"] = success_rate
        
        logger.info(f"Platform tests completed: {success_rate:.1f}% success rate")
        return summary
    
    async def _execute_test(self, test_id: str, test: PlatformTest) -> TestExecutionResult:
        """Execute a single platform test"""
        
        start_time = time.time()
        
        # Check prerequisites
        if not await self._check_test_prerequisites(test):
            return TestExecutionResult(
                test_name=test.name,
                platform=self.current_platform,
                result=TestResult.SKIP,
                start_time=start_time,
                end_time=time.time(),
                duration=0.0,
                output="Prerequisites not met"
            )
        
        logger.debug(f"Executing platform test: {test.name}")
        
        try:
            # Execute test with timeout
            timeout = test.timeout * self.config["timeout_multiplier"]
            
            if asyncio.iscoroutinefunction(test.test_function):
                result = await asyncio.wait_for(
                    test.test_function(self.current_platform, self.available_browsers),
                    timeout=timeout
                )
            else:
                result = test.test_function(self.current_platform, self.available_browsers)
            
            end_time = time.time()
            
            # Determine test result
            if isinstance(result, bool):
                test_result = TestResult.PASS if result else TestResult.FAIL
                output = "Test completed"
            elif isinstance(result, tuple) and len(result) == 2:
                test_result, output = result
            else:
                test_result = TestResult.PASS
                output = str(result) if result is not None else "Test completed"
            
            return TestExecutionResult(
                test_name=test.name,
                platform=self.current_platform,
                result=test_result,
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
                output=output
            )
            
        except asyncio.TimeoutError:
            return TestExecutionResult(
                test_name=test.name,
                platform=self.current_platform,
                result=TestResult.ERROR,
                start_time=start_time,
                end_time=time.time(),
                duration=time.time() - start_time,
                error_message=f"Test timed out after {timeout}s"
            )
            
        except Exception as e:
            return TestExecutionResult(
                test_name=test.name,
                platform=self.current_platform,
                result=TestResult.ERROR,
                start_time=start_time,
                end_time=time.time(),
                duration=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _check_test_prerequisites(self, test: PlatformTest) -> bool:
        """Check if test prerequisites are met"""
        
        # Check memory requirements
        if test.min_memory_gb > self.current_platform.available_memory_gb:
            logger.debug(f"Test {test.name} requires {test.min_memory_gb}GB memory, only {self.current_platform.available_memory_gb:.1f}GB available")
            return False
        
        # Check disk space requirements
        if test.min_disk_space_gb > self.current_platform.disk_space_gb:
            logger.debug(f"Test {test.name} requires {test.min_disk_space_gb}GB disk space, only {self.current_platform.disk_space_gb:.1f}GB available")
            return False
        
        # Check browser requirements
        if test.required_browsers:
            missing_browsers = set(test.required_browsers) - set(self.available_browsers)
            if missing_browsers:
                logger.debug(f"Test {test.name} requires browsers {[b.value for b in missing_browsers]} which are not available")
                return False
        
        # Check admin requirements
        if test.requires_admin and self.config.get("skip_admin_tests"):
            logger.debug(f"Test {test.name} requires admin privileges but admin tests are disabled")
            return False
        
        # Check network requirements  
        if test.requires_network and self.config.get("skip_network_tests"):
            logger.debug(f"Test {test.name} requires network but network tests are disabled")
            return False
        
        return True
    
    def _check_system_requirements(self) -> Dict[str, bool]:
        """Check if system meets minimum requirements"""
        
        requirements = {
            "minimum_python_version": self._check_python_version("3.8"),
            "sufficient_memory": self.current_platform.available_memory_gb >= 2.0,
            "sufficient_disk_space": self.current_platform.disk_space_gb >= 5.0,
            "supported_platform": self.current_platform.platform != Platform.UNKNOWN,
            "has_browser": len(self.available_browsers) > 0
        }
        
        return requirements
    
    def _check_python_version(self, min_version: str) -> bool:
        """Check if Python version meets minimum requirement"""
        
        current = tuple(map(int, self.current_platform.python_version.split('.')))
        minimum = tuple(map(int, min_version.split('.')))
        
        return current >= minimum
    
    def _register_builtin_tests(self) -> None:
        """Register built-in platform compatibility tests"""
        
        # File system operations test
        def test_file_operations(platform_info: PlatformInfo, browsers: List[Browser]) -> Tuple[TestResult, str]:
            """Test basic file system operations"""
            try:
                # Create temp directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    
                    # Test file creation
                    test_file = temp_path / "test_file.txt"
                    test_file.write_text("Test content")
                    
                    # Test file reading
                    content = test_file.read_text()
                    assert content == "Test content"
                    
                    # Test directory operations
                    test_subdir = temp_path / "subdir"
                    test_subdir.mkdir()
                    assert test_subdir.exists()
                    
                    # Test file deletion
                    test_file.unlink()
                    assert not test_file.exists()
                    
                    return TestResult.PASS, "File system operations successful"
                    
            except Exception as e:
                return TestResult.FAIL, f"File system operations failed: {e}"
        
        self.register_test(PlatformTest(
            name="file_system_operations",
            description="Test basic file system operations",
            test_function=test_file_operations,
            target_platforms=list(Platform)
        ))
        
        # Process management test
        def test_process_management(platform_info: PlatformInfo, browsers: List[Browser]) -> Tuple[TestResult, str]:
            """Test process creation and management"""
            try:
                # Test subprocess execution
                if platform_info.platform == Platform.WINDOWS:
                    result = subprocess.run(["echo", "test"], capture_output=True, text=True, timeout=5)
                else:
                    result = subprocess.run(["echo", "test"], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0 and "test" in result.stdout:
                    return TestResult.PASS, "Process management successful"
                else:
                    return TestResult.FAIL, f"Subprocess failed: {result.stderr}"
                    
            except subprocess.TimeoutExpired:
                return TestResult.FAIL, "Process management timeout"
            except Exception as e:
                return TestResult.FAIL, f"Process management failed: {e}"
        
        self.register_test(PlatformTest(
            name="process_management", 
            description="Test process creation and management",
            test_function=test_process_management,
            target_platforms=list(Platform)
        ))
        
        # Network connectivity test
        def test_network_connectivity(platform_info: PlatformInfo, browsers: List[Browser]) -> Tuple[TestResult, str]:
            """Test network connectivity"""
            try:
                import socket
                import urllib.request
                
                # Test DNS resolution
                socket.gethostbyname("google.com")
                
                # Test HTTP request
                with urllib.request.urlopen("http://httpbin.org/status/200", timeout=10) as response:
                    if response.status == 200:
                        return TestResult.PASS, "Network connectivity successful"
                    else:
                        return TestResult.FAIL, f"HTTP request failed: {response.status}"
                        
            except Exception as e:
                return TestResult.FAIL, f"Network connectivity failed: {e}"
        
        self.register_test(PlatformTest(
            name="network_connectivity",
            description="Test network connectivity",
            test_function=test_network_connectivity,
            target_platforms=list(Platform),
            requires_network=True
        ))
        
        # Browser compatibility test
        def test_browser_compatibility(platform_info: PlatformInfo, browsers: List[Browser]) -> Tuple[TestResult, str]:
            """Test browser compatibility"""
            if not browsers:
                return TestResult.SKIP, "No browsers available"
            
            compatible_browsers = []
            
            for browser in browsers:
                try:
                    # Test browser launch (without actually opening)
                    browser_paths = {
                        Browser.CHROME: {
                            Platform.MACOS: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                            Platform.WINDOWS: r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                            Platform.LINUX: "/usr/bin/google-chrome"
                        },
                        Browser.FIREFOX: {
                            Platform.MACOS: "/Applications/Firefox.app/Contents/MacOS/firefox",
                            Platform.WINDOWS: r"C:\Program Files\Mozilla Firefox\firefox.exe", 
                            Platform.LINUX: "/usr/bin/firefox"
                        },
                        Browser.SAFARI: {
                            Platform.MACOS: "/Applications/Safari.app/Contents/MacOS/Safari"
                        },
                        Browser.EDGE: {
                            Platform.WINDOWS: r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
                        }
                    }
                    
                    browser_path = browser_paths.get(browser, {}).get(platform_info.platform)
                    if browser_path and Path(browser_path).exists():
                        # Test version detection
                        if browser == Browser.CHROME:
                            result = subprocess.run([browser_path, "--version"], 
                                                  capture_output=True, text=True, timeout=5)
                            if result.returncode == 0 and "Google Chrome" in result.stdout:
                                compatible_browsers.append(browser.value)
                        elif browser == Browser.FIREFOX:
                            result = subprocess.run([browser_path, "--version"],
                                                  capture_output=True, text=True, timeout=5) 
                            if result.returncode == 0:
                                compatible_browsers.append(browser.value)
                        else:
                            # For Safari and Edge, just check if executable exists
                            compatible_browsers.append(browser.value)
                            
                except Exception as e:
                    logger.debug(f"Browser {browser.value} compatibility check failed: {e}")
            
            if compatible_browsers:
                return TestResult.PASS, f"Compatible browsers: {', '.join(compatible_browsers)}"
            else:
                return TestResult.FAIL, "No compatible browsers found"
        
        self.register_test(PlatformTest(
            name="browser_compatibility",
            description="Test browser compatibility",
            test_function=test_browser_compatibility,
            target_platforms=list(Platform),
            required_browsers=[]  # Will test all available browsers
        ))
        
        # Memory stress test
        def test_memory_usage(platform_info: PlatformInfo, browsers: List[Browser]) -> Tuple[TestResult, str]:
            """Test memory allocation and usage"""
            try:
                import gc
                
                # Get initial memory
                process = psutil.Process()
                initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
                
                # Allocate some memory
                test_data = []
                for _ in range(1000):
                    test_data.append("x" * 1000)  # 1KB strings
                
                # Check memory increase
                current_memory = process.memory_info().rss / (1024 * 1024)
                memory_increase = current_memory - initial_memory
                
                # Clean up
                del test_data
                gc.collect()
                
                # Check cleanup
                final_memory = process.memory_info().rss / (1024 * 1024)
                
                if memory_increase > 0.5:  # At least 0.5MB increase
                    return TestResult.PASS, f"Memory test successful: {memory_increase:.1f}MB allocated, {final_memory:.1f}MB final"
                else:
                    return TestResult.FAIL, "Insufficient memory allocation detected"
                    
            except Exception as e:
                return TestResult.FAIL, f"Memory test failed: {e}"
        
        self.register_test(PlatformTest(
            name="memory_usage",
            description="Test memory allocation and usage", 
            test_function=test_memory_usage,
            target_platforms=list(Platform),
            min_memory_gb=0.5
        ))
        
        logger.info(f"Registered {len(self.registered_tests)} built-in platform tests")
    
    def get_platform_report(self) -> Dict[str, Any]:
        """Generate comprehensive platform compatibility report"""
        
        return {
            "platform_info": {
                "system": self.current_platform.system,
                "platform": self.current_platform.platform.value,
                "release": self.current_platform.release,
                "version": self.current_platform.version,
                "machine": self.current_platform.machine,
                "processor": self.current_platform.processor,
                "architecture": self.current_platform.architecture,
                "python_version": self.current_platform.python_version,
                "available_memory_gb": self.current_platform.available_memory_gb,
                "cpu_count": self.current_platform.cpu_count,
                "disk_space_gb": self.current_platform.disk_space_gb
            },
            "browser_info": {
                "available_browsers": [b.value for b in self.available_browsers],
                "browser_count": len(self.available_browsers)
            },
            "system_requirements": self._check_system_requirements(),
            "registered_tests": len(self.registered_tests),
            "test_results": len(self.test_results),
            "config": self.config.copy()
        }