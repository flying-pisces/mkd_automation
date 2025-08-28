"""
Week 4 Integration Test Suite

Comprehensive testing for Platform Integration & Production Deployment features.
Tests system integration, CLI interface, cross-platform compatibility, and deployment capabilities.
"""

import asyncio
import sys
import os
import time
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mkd_v2.integration.system_controller import SystemController
from mkd_v2.integration.component_registry import ComponentRegistry, ComponentType, RegistrationInfo
from mkd_v2.integration.event_bus import EventBus, Event, EventType
from mkd_v2.integration.lifecycle_manager import LifecycleManager, LifecyclePhase
from mkd_v2.cli.main_cli import MKDCli
from mkd_v2.cli.command_router import CommandRouter, Command, CommandType, CommandParameter
from mkd_v2.cli.interactive_mode import InteractiveMode
from mkd_v2.testing.test_orchestrator import TestOrchestrator, TestSuite, TestCategory, TestPriority
from mkd_v2.testing.cross_platform_tests import CrossPlatformValidator
from mkd_v2.deployment.package_builder import PackageBuilder, PackageType, PackageConfig, PackageMetadata
from mkd_v2.deployment.configuration_manager import ConfigurationManager, DeploymentEnvironment

# Import test logger
sys.path.insert(0, str(Path(__file__).parent))
from test_logger import Week4TestLogger

logger = logging.getLogger(__name__)


class Week4TestSuite:
    """Week 4 comprehensive integration test suite"""
    
    def __init__(self):
        self.test_logger = Week4TestLogger("Week4TestSuite")
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
        # Test components
        self.temp_dir = None
        self.system_controller = None
        self.component_registry = None
        self.event_bus = None
        self.lifecycle_manager = None
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all Week 4 integration tests"""
        
        self.start_time = time.time()
        self.test_logger.start_test_session("Week 4 Integration Tests")
        
        try:
            # Setup test environment
            await self._setup_test_environment()
            
            # Run test categories
            await self._test_system_integration()
            await self._test_cli_interface()
            await self._test_cross_platform_compatibility()
            await self._test_deployment_capabilities()
            await self._test_end_to_end_scenarios()
            
            # Generate final report
            return await self._generate_final_report()
            
        except Exception as e:
            self.test_logger.log_error("Critical test suite failure", str(e))
            return {"status": "CRITICAL_FAILURE", "error": str(e)}
        
        finally:
            await self._cleanup_test_environment()
            self.end_time = time.time()
    
    async def _setup_test_environment(self) -> None:
        """Setup test environment"""
        
        self.test_logger.log_info("Setting up Week 4 test environment")
        
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mkd_week4_test_"))
        
        # Initialize core system components  
        self.system_controller = SystemController()
        
        # Get references to the internal components
        self.component_registry = self.system_controller.component_registry
        self.event_bus = self.system_controller.event_bus
        self.lifecycle_manager = self.system_controller.lifecycle_manager
        
        self.test_logger.log_info("Test environment setup complete")
    
    async def _cleanup_test_environment(self) -> None:
        """Cleanup test environment"""
        
        try:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                
            if self.system_controller and hasattr(self.system_controller, 'stop_system'):
                await self.system_controller.stop_system()
            elif self.lifecycle_manager:
                await self.lifecycle_manager.stop_system()
                
            self.test_logger.log_info("Test environment cleanup complete")
            
        except Exception as e:
            self.test_logger.log_warning("Test cleanup failed", str(e))
    
    async def _test_system_integration(self) -> None:
        """Test system integration components"""
        
        self.test_logger.start_test_category("System Integration")
        category_results = {}
        
        # Test 1: Component Registry Functionality
        try:
            self.test_logger.start_test("Component Registry Basic Operations")
            
            # Test component registration
            from mkd_v2.integration.component_registry import component, ComponentScope
            
            @component(ComponentType.CORE, scope=ComponentScope.SINGLETON)
            class TestComponent:
                def __init__(self):
                    self.initialized = True
                
                def get_status(self):
                    return "healthy"
            
            # Register component
            registration_info = RegistrationInfo(
                component_type=ComponentType.CORE,
                component_class=TestComponent,
                scope=ComponentScope.SINGLETON
            )
            
            comp_id = self.component_registry.register_component("test_component", registration_info)
            
            # Test component retrieval
            instance = self.component_registry.get_component("test_component")
            
            assert instance is not None, "Component instance should not be None"
            assert hasattr(instance, 'initialized'), "Component should be initialized"
            assert instance.get_status() == "healthy", "Component should be healthy"
            
            # Test component statistics
            stats = self.component_registry.get_registry_statistics()
            assert stats["total_components"] >= 1, "Should have at least 1 component"
            
            category_results["component_registry"] = {
                "status": "PASS",
                "message": "Component registry operations successful"
            }
            self.test_logger.log_success("Component Registry Basic Operations")
            
        except Exception as e:
            category_results["component_registry"] = {
                "status": "FAIL", 
                "error": str(e)
            }
            self.test_logger.log_error("Component Registry Basic Operations", str(e))
        
        # Test 2: Event Bus Messaging
        try:
            self.test_logger.start_test("Event Bus Messaging")
            
            received_events = []
            
            async def test_handler(event):
                received_events.append(event)
            
            # Subscribe to events
            self.event_bus.subscribe(EventType.SYSTEM_STARTED, test_handler)
            
            # Publish event
            test_event = Event(
                event_type=EventType.SYSTEM_STARTED,
                data={"test": "data"}
            )
            
            await self.event_bus.publish(test_event)
            
            # Wait for event processing
            await asyncio.sleep(0.1)
            
            assert len(received_events) == 1, "Should have received 1 event"
            assert received_events[0].data["test"] == "data", "Event data should match"
            
            # Test event statistics
            stats = self.event_bus.get_event_statistics()
            assert stats["total_published"] >= 1, "Should have published at least 1 event"
            
            category_results["event_bus"] = {
                "status": "PASS",
                "message": "Event bus messaging successful"
            }
            self.test_logger.log_success("Event Bus Messaging")
            
        except Exception as e:
            category_results["event_bus"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.test_logger.log_error("Event Bus Messaging", str(e))
        
        # Test 3: Lifecycle Management
        try:
            self.test_logger.start_test("Lifecycle Management")
            
            # Test phase transitions
            initial_phase = self.lifecycle_manager.get_current_phase()
            assert initial_phase == LifecyclePhase.STOPPED, "Should start in STOPPED phase"
            
            # Test system initialization
            init_success = await self.lifecycle_manager.initialize_system()
            assert init_success, "System initialization should succeed"
            
            # Test system startup
            start_success = await self.lifecycle_manager.start_system()
            assert start_success, "System start should succeed"
            
            current_phase = self.lifecycle_manager.get_current_phase()
            assert current_phase == LifecyclePhase.RUNNING, "Should be in RUNNING phase"
            
            # Test system stop
            stop_success = await self.lifecycle_manager.stop_system()
            assert stop_success, "System stop should succeed"
            
            final_phase = self.lifecycle_manager.get_current_phase()
            assert final_phase == LifecyclePhase.STOPPED, "Should return to STOPPED phase"
            
            # Test lifecycle statistics
            stats = self.lifecycle_manager.get_lifecycle_statistics()
            assert stats["total_phase_transitions"] >= 3, "Should have at least 3 phase transitions"
            
            category_results["lifecycle_management"] = {
                "status": "PASS",
                "message": "Lifecycle management successful"
            }
            self.test_logger.log_success("Lifecycle Management")
            
        except Exception as e:
            category_results["lifecycle_management"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.test_logger.log_error("Lifecycle Management", str(e))
        
        # Test 4: System Controller Integration
        try:
            self.test_logger.start_test("System Controller Integration")
            
            # Test system controller initialization
            controller_stats = self.system_controller.get_system_statistics()
            assert "total_components" in controller_stats, "Controller should provide statistics"
            
            # Test health monitoring
            health_status = await self.system_controller.check_system_health()
            assert health_status is not None, "Health check should return status"
            
            category_results["system_controller"] = {
                "status": "PASS",
                "message": "System controller integration successful"
            }
            self.test_logger.log_success("System Controller Integration")
            
        except Exception as e:
            category_results["system_controller"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.test_logger.log_error("System Controller Integration", str(e))
        
        self.test_results["system_integration"] = category_results
        self.test_logger.end_test_category("System Integration", category_results)
    
    async def _test_cli_interface(self) -> None:
        """Test CLI interface functionality"""
        
        self.test_logger.start_test_category("CLI Interface")
        category_results = {}
        
        # Test 1: Command Router
        try:
            self.test_logger.start_test("Command Router Functionality")
            
            router = CommandRouter()
            
            # Test command registration
            def test_handler(params, context):
                return f"Test command executed with {len(params)} parameters"
            
            test_command = Command(
                name="test",
                description="Test command",
                handler=test_handler,
                command_type=CommandType.UTIL,
                parameters=[
                    CommandParameter("param1", str, False, "default", "Test parameter")
                ]
            )
            
            router.register_command(test_command)
            
            # Test command parsing
            command, params, errors = router.parse_command("test --param1 value")
            assert command is not None, "Command should be parsed successfully"
            assert len(errors) == 0, "Should have no parsing errors"
            assert params.get("param1") == "value", "Parameter should be parsed correctly"
            
            # Test command execution
            result = await router.execute_command("test --param1 hello")
            assert result["success"], "Command execution should succeed"
            assert "hello" in str(result["result"]), "Result should contain parameter value"
            
            # Test help generation
            help_text = router.get_command_help("test")
            assert "test" in help_text.lower(), "Help should contain command name"
            assert "Test command" in help_text, "Help should contain description"
            
            category_results["command_router"] = {
                "status": "PASS",
                "message": "Command router functionality successful"
            }
            self.test_logger.log_success("Command Router Functionality")
            
        except Exception as e:
            category_results["command_router"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.test_logger.log_error("Command Router Functionality", str(e))
        
        # Test 2: CLI Main Interface
        try:
            self.test_logger.start_test("CLI Main Interface")
            
            # Initialize CLI
            cli = MKDCli()
            
            # Test CLI configuration
            assert cli.config is not None, "CLI should have configuration"
            assert cli.command_router is not None, "CLI should have command router"
            
            # Test context setup
            assert "system_running" in cli.context, "CLI context should have system_running flag"
            
            category_results["cli_main"] = {
                "status": "PASS",
                "message": "CLI main interface successful"
            }
            self.test_logger.log_success("CLI Main Interface")
            
        except Exception as e:
            category_results["cli_main"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.test_logger.log_error("CLI Main Interface", str(e))
        
        # Test 3: Interactive Mode
        try:
            self.test_logger.start_test("Interactive Mode")
            
            from rich.console import Console
            
            console = Console()
            router = CommandRouter()
            
            # Test interactive mode initialization
            interactive = InteractiveMode(router, console)
            assert interactive.command_router is not None, "Interactive mode should have command router"
            
            # Test session creation
            from mkd_v2.cli.interactive_mode import InteractiveSession
            session = InteractiveSession(console)
            
            # Test session variables
            session.add_variable("test_var", "test_value")
            assert session.get_variable("test_var") == "test_value", "Session variable should be stored"
            
            # Test bookmarks
            session.add_bookmark("test_bookmark", "test command")
            assert session.get_bookmark("test_bookmark") == "test command", "Bookmark should be stored"
            
            category_results["interactive_mode"] = {
                "status": "PASS",
                "message": "Interactive mode successful"
            }
            self.test_logger.log_success("Interactive Mode")
            
        except Exception as e:
            category_results["interactive_mode"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.test_logger.log_error("Interactive Mode", str(e))
        
        self.test_results["cli_interface"] = category_results
        self.test_logger.end_test_category("CLI Interface", category_results)
    
    async def _test_cross_platform_compatibility(self) -> None:
        """Test cross-platform compatibility"""
        
        self.test_logger.start_test_category("Cross-Platform Compatibility")
        category_results = {}
        
        # Test 1: Platform Detection
        try:
            self.test_logger.start_test("Platform Detection")
            
            from mkd_v2.testing.cross_platform_tests import PlatformInfo
            
            # Test platform info detection
            platform_info = PlatformInfo.detect_current()
            
            assert platform_info.platform.value in ["macos", "windows", "linux", "unknown"], "Should detect valid platform"
            assert platform_info.python_version, "Should detect Python version"
            assert platform_info.available_memory_gb > 0, "Should detect available memory"
            assert platform_info.cpu_count > 0, "Should detect CPU count"
            
            category_results["platform_detection"] = {
                "status": "PASS",
                "message": f"Platform detection successful: {platform_info.platform.value}"
            }
            self.test_logger.log_success("Platform Detection")
            
        except Exception as e:
            category_results["platform_detection"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.test_logger.log_error("Platform Detection", str(e))
        
        # Test 2: Cross-Platform Validator
        try:
            self.test_logger.start_test("Cross-Platform Validator")
            
            validator = CrossPlatformValidator()
            
            # Test validator initialization
            assert validator.current_platform is not None, "Validator should detect platform"
            assert len(validator.registered_tests) > 0, "Should have registered tests"
            
            # Run platform tests (subset for speed)
            test_results = await validator.run_all_tests()
            
            assert "platform" in test_results, "Should return platform info"
            assert "results" in test_results, "Should return test results"
            assert test_results["execution"]["total_tests"] > 0, "Should have run tests"
            
            category_results["cross_platform_validator"] = {
                "status": "PASS",
                "message": f"Cross-platform validation successful: {test_results['success_rate']:.1f}% success rate",
                "details": {
                    "total_tests": test_results["execution"]["total_tests"],
                    "success_rate": test_results["success_rate"]
                }
            }
            self.test_logger.log_success("Cross-Platform Validator")
            
        except Exception as e:
            category_results["cross_platform_validator"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.test_logger.log_error("Cross-Platform Validator", str(e))
        
        # Test 3: Test Orchestrator
        try:
            self.test_logger.start_test("Test Orchestrator")
            
            orchestrator = TestOrchestrator()
            
            # Create simple test suite
            def simple_test():
                assert True, "Simple test should pass"
                return True
            
            def failing_test():
                assert False, "This test should fail"
            
            test_suite = TestSuite(
                name="test_orchestrator_suite",
                description="Test suite for orchestrator",
                tests=[simple_test, failing_test],
                category=TestCategory.UNIT,
                priority=TestPriority.HIGH
            )
            
            # Register and run tests
            suite_id = orchestrator.register_test_suite(test_suite)
            assert suite_id, "Suite should be registered successfully"
            
            # Run tests
            results = await orchestrator.run_all_tests()
            
            assert results["success"] != None, "Should return results"
            assert results["summary"]["total"] >= 2, "Should have run at least 2 tests"
            
            category_results["test_orchestrator"] = {
                "status": "PASS",
                "message": "Test orchestrator successful",
                "details": {
                    "total_tests": results["summary"]["total"],
                    "success_rate": results["summary"]["success_rate"]
                }
            }
            self.test_logger.log_success("Test Orchestrator")
            
        except Exception as e:
            category_results["test_orchestrator"] = {
                "status": "FAIL", 
                "error": str(e)
            }
            self.test_logger.log_error("Test Orchestrator", str(e))
        
        self.test_results["cross_platform"] = category_results
        self.test_logger.end_test_category("Cross-Platform Compatibility", category_results)
    
    async def _test_deployment_capabilities(self) -> None:
        """Test deployment capabilities"""
        
        self.test_logger.start_test_category("Deployment Capabilities")
        category_results = {}
        
        # Test 1: Package Builder
        try:
            self.test_logger.start_test("Package Builder")
            
            builder = PackageBuilder(str(self.temp_dir / "package_build"))
            
            # Create test source directory
            test_src = self.temp_dir / "test_package_src"
            test_src.mkdir()
            
            # Create simple Python module
            (test_src / "__init__.py").write_text("")
            (test_src / "main.py").write_text("print('Hello from package')")
            
            # Test package configuration
            metadata = PackageMetadata(
                name="test-package",
                version="1.0.0", 
                description="Test package for Week 4",
                author="Test Author"
            )
            
            config = PackageConfig(
                package_type=PackageType.ZIP_ARCHIVE,
                metadata=metadata,
                source_directory=str(test_src),
                output_directory=str(self.temp_dir / "package_output")
            )
            
            # Build package
            result = await builder.build_package(config)
            
            assert result["success"], f"Package build should succeed: {result.get('error_message', '')}"
            assert len(result["output_files"]) > 0, "Should create output files"
            
            # Verify output file exists
            for file_path in result["output_files"]:
                if file_path.endswith('.zip'):
                    assert Path(file_path).exists(), f"Output file should exist: {file_path}"
            
            category_results["package_builder"] = {
                "status": "PASS",
                "message": "Package builder successful",
                "details": {
                    "output_files": len(result["output_files"]),
                    "duration": result.get("duration", 0)
                }
            }
            self.test_logger.log_success("Package Builder")
            
        except Exception as e:
            category_results["package_builder"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.test_logger.log_error("Package Builder", str(e))
        
        # Test 2: Configuration Manager
        try:
            self.test_logger.start_test("Configuration Manager")
            
            config_dir = self.temp_dir / "config"
            config_manager = ConfigurationManager(str(config_dir))
            
            # Test environment creation
            env_config = config_manager.create_environment_config(DeploymentEnvironment.DEVELOPMENT)
            assert env_config.environment == DeploymentEnvironment.DEVELOPMENT, "Should create dev environment"
            
            # Test configuration values
            config_manager.set_config_value("test_setting", "test_value", DeploymentEnvironment.DEVELOPMENT)
            value = config_manager.get_config_value("test_setting", environment=DeploymentEnvironment.DEVELOPMENT)
            assert value == "test_value", "Should store and retrieve config value"
            
            # Test feature flags
            config_manager.set_feature_flag("test_flag", True, DeploymentEnvironment.DEVELOPMENT)
            flag_value = config_manager.get_feature_flag("test_flag", environment=DeploymentEnvironment.DEVELOPMENT)
            assert flag_value == True, "Should store and retrieve feature flag"
            
            # Test configuration validation
            validation_result = config_manager.validate_configuration(DeploymentEnvironment.DEVELOPMENT)
            assert isinstance(validation_result, dict), "Should return validation results"
            
            # Test configuration save/load
            save_success = config_manager.save_configuration(DeploymentEnvironment.DEVELOPMENT)
            assert save_success, "Should save configuration successfully"
            
            # Create new manager and load
            config_manager2 = ConfigurationManager(str(config_dir))
            load_success = config_manager2.load_configuration(DeploymentEnvironment.DEVELOPMENT)
            assert load_success, "Should load configuration successfully"
            
            # Verify loaded values
            loaded_value = config_manager2.get_config_value("test_setting", environment=DeploymentEnvironment.DEVELOPMENT)
            assert loaded_value == "test_value", "Loaded config should match saved config"
            
            category_results["configuration_manager"] = {
                "status": "PASS",
                "message": "Configuration manager successful"
            }
            self.test_logger.log_success("Configuration Manager")
            
        except Exception as e:
            category_results["configuration_manager"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.test_logger.log_error("Configuration Manager", str(e))
        
        self.test_results["deployment"] = category_results
        self.test_logger.end_test_category("Deployment Capabilities", category_results)
    
    async def _test_end_to_end_scenarios(self) -> None:
        """Test end-to-end scenarios"""
        
        self.test_logger.start_test_category("End-to-End Scenarios")
        category_results = {}
        
        # Test 1: Complete System Lifecycle
        try:
            self.test_logger.start_test("Complete System Lifecycle")
            
            # Initialize fresh components for E2E test
            system_controller = SystemController()
            registry = system_controller.component_registry
            event_bus = system_controller.event_bus
            lifecycle_manager = system_controller.lifecycle_manager
            
            # Test complete lifecycle
            # 1. System initialization
            init_success = await lifecycle_manager.initialize_system()
            assert init_success, "System should initialize successfully"
            
            # 2. System startup
            start_success = await lifecycle_manager.start_system()
            assert start_success, "System should start successfully"
            
            # 3. Verify running state
            assert lifecycle_manager.is_running(), "System should be in running state"
            
            # 4. Check system health
            health = await system_controller.check_system_health()
            assert health is not None, "System health check should work"
            
            # 5. Get system statistics
            stats = system_controller.get_system_statistics()
            assert "uptime_seconds" in stats, "System should provide uptime statistics"
            
            # 6. System shutdown
            stop_success = await lifecycle_manager.stop_system()
            assert stop_success, "System should stop successfully"
            
            # 7. Verify stopped state
            assert not lifecycle_manager.is_running(), "System should be stopped"
            
            category_results["system_lifecycle"] = {
                "status": "PASS",
                "message": "Complete system lifecycle successful"
            }
            self.test_logger.log_success("Complete System Lifecycle")
            
        except Exception as e:
            category_results["system_lifecycle"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.test_logger.log_error("Complete System Lifecycle", str(e))
        
        # Test 2: CLI to System Integration
        try:
            self.test_logger.start_test("CLI to System Integration")
            
            # Create CLI with system components
            cli = MKDCli()
            
            # Test CLI command execution
            result = await cli.command_router.execute_command("help")
            assert result["success"], "CLI help command should work"
            
            result = await cli.command_router.execute_command("config get")
            assert result["success"], "CLI config command should work"
            
            category_results["cli_integration"] = {
                "status": "PASS",
                "message": "CLI to system integration successful"
            }
            self.test_logger.log_success("CLI to System Integration")
            
        except Exception as e:
            category_results["cli_integration"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.test_logger.log_error("CLI to System Integration", str(e))
        
        # Test 3: Testing Framework Integration
        try:
            self.test_logger.start_test("Testing Framework Integration")
            
            # Test orchestrator with cross-platform validator
            orchestrator = TestOrchestrator()
            validator = CrossPlatformValidator()
            
            # Auto-discover would normally find tests in test directories
            discovered_count = orchestrator.auto_discover_tests(str(self.temp_dir / "fake_tests"))
            # This will be 0 since we don't have real test files, but should not error
            
            # Test with platform tests
            results = await validator.run_all_tests()
            assert "success_rate" in results, "Validator should return success rate"
            
            category_results["testing_integration"] = {
                "status": "PASS",
                "message": "Testing framework integration successful"
            }
            self.test_logger.log_success("Testing Framework Integration")
            
        except Exception as e:
            category_results["testing_integration"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.test_logger.log_error("Testing Framework Integration", str(e))
        
        self.test_results["end_to_end"] = category_results
        self.test_logger.end_test_category("End-to-End Scenarios", category_results)
    
    async def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final comprehensive test report"""
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        # Calculate totals across all categories
        for category, results in self.test_results.items():
            for test_name, result in results.items():
                total_tests += 1
                if result["status"] == "PASS":
                    passed_tests += 1
                else:
                    failed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        duration = (self.end_time or time.time()) - self.start_time
        
        report = {
            "week": 4,
            "test_suite": "Platform Integration & Production Deployment",
            "execution_summary": {
                "start_time": self.start_time,
                "end_time": self.end_time or time.time(),
                "duration_seconds": duration,
                "total_test_categories": len(self.test_results),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate
            },
            "category_results": self.test_results,
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "test_environment": "integration"
            },
            "coverage_analysis": {
                "system_integration": len(self.test_results.get("system_integration", {})),
                "cli_interface": len(self.test_results.get("cli_interface", {})),
                "cross_platform": len(self.test_results.get("cross_platform", {})),
                "deployment": len(self.test_results.get("deployment", {})),
                "end_to_end": len(self.test_results.get("end_to_end", {}))
            },
            "recommendations": self._generate_recommendations(),
            "status": "COMPLETE" if success_rate >= 50 else "NEEDS_ATTENTION"
        }
        
        # Log final summary
        self.test_logger.log_info(f"Week 4 Test Suite Complete: {success_rate:.1f}% success rate ({passed_tests}/{total_tests} tests passed)")
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        
        recommendations = []
        
        # Analyze results and provide recommendations
        for category, results in self.test_results.items():
            failed_tests = [name for name, result in results.items() if result["status"] != "PASS"]
            
            if failed_tests:
                recommendations.append(f"Review failed tests in {category}: {', '.join(failed_tests)}")
        
        # Add general recommendations
        recommendations.extend([
            "Continue monitoring system integration stability",
            "Consider adding more cross-platform test coverage",
            "Implement automated deployment pipeline testing",
            "Add performance regression tests for CLI interface"
        ])
        
        return recommendations


def main():
    """Main test execution"""
    
    async def run_tests():
        suite = Week4TestSuite()
        return await suite.run_all_tests()
    
    # Run the test suite
    results = asyncio.run(run_tests())
    
    # Print summary
    print("\n" + "="*80)
    print("WEEK 4 INTEGRATION TEST SUMMARY")
    print("="*80)
    print(f"Status: {results['status']}")
    
    if 'execution_summary' in results:
        print(f"Success Rate: {results['execution_summary']['success_rate']:.1f}%")
        print(f"Total Tests: {results['execution_summary']['total_tests']}")
        print(f"Passed: {results['execution_summary']['passed_tests']}")
        print(f"Failed: {results['execution_summary']['failed_tests']}")
        print(f"Duration: {results['execution_summary']['duration_seconds']:.1f}s")
    else:
        print(f"Error: {results.get('error', 'Unknown error occurred')}")
    
    if 'category_results' in results:
        print("\nCategory Breakdown:")
        for category, tests in results['category_results'].items():
            category_passed = len([t for t in tests.values() if t['status'] == 'PASS'])
            category_total = len(tests)
            category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            print(f"  {category.title().replace('_', ' ')}: {category_rate:.1f}% ({category_passed}/{category_total})")
    
    if results['status'] != 'COMPLETE':
        print(f"\n⚠️  Issues detected: {results.get('error', 'See detailed results')}")
        return 1
    else:
        print(f"\n✅ Week 4 Integration Tests Complete!")
        return 0


if __name__ == "__main__":
    exit(main())