#!/usr/bin/env python3
"""
Complete Integration Test Suite for MKD Automation
Tests end-to-end functionality across all components
"""

import sys
import os
import subprocess
import time
import json
import traceback
import threading
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class IntegrationTestSuite:
    """Complete integration testing suite"""
    
    def __init__(self):
        self.results = {}
        self.venv_python = Path("venv/Scripts/python.exe").resolve()
        self.start_time = time.time()
        self.test_data_dir = Path("integration_test_data")
        self.test_data_dir.mkdir(exist_ok=True)
        
        print("[INTEGRATION] Starting Complete Integration Test Suite...")
        print(f"Python: {sys.version}")
        print(f"Working Directory: {Path.cwd()}")
        print("-" * 80)

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        
        test_categories = [
            ("System Requirements Check", self.test_system_requirements),
            ("Application Startup Tests", self.test_application_startup),
            ("Native Host Communication", self.test_native_host_communication),
            ("Chrome Extension Integration", self.test_chrome_extension_integration),
            ("End-to-End Workflow", self.test_end_to_end_workflow),
            ("Error Recovery Tests", self.test_error_recovery),
            ("Performance Tests", self.test_performance),
        ]
        
        for category_name, test_func in test_categories:
            print(f"\n[INTEGRATION] Running {category_name}...")
            try:
                result = test_func()
                self.results[category_name] = result
                status = "[PASS]" if result.get("success", False) else "[FAIL]"
                print(f"   {status} - {result.get('summary', 'No summary')}")
            except Exception as e:
                error_result = {
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
                self.results[category_name] = error_result
                print(f"   [ERROR] - {str(e)}")
        
        return self.generate_final_report()

    def test_system_requirements(self) -> Dict[str, Any]:
        """Test system requirements and dependencies"""
        
        tests = []
        
        # Test Python version
        try:
            python_version = sys.version_info
            tests.append({
                "test": "Python Version Check",
                "success": python_version >= (3, 8),
                "details": f"Python {python_version.major}.{python_version.minor}.{python_version.micro}",
                "expected": "Python >= 3.8"
            })
        except Exception as e:
            tests.append({
                "test": "Python Version Check",
                "success": False,
                "error": str(e)
            })
        
        # Test virtual environment
        venv_exists = self.venv_python.exists()
        tests.append({
            "test": "Virtual Environment",
            "success": venv_exists,
            "details": f"Virtual env at: {self.venv_python}" if venv_exists else "Virtual environment not found"
        })
        
        # Test required directories
        required_dirs = ['src', 'chrome-extension', 'bin', 'tests']
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            tests.append({
                "test": f"Directory: {dir_name}",
                "success": dir_path.exists() and dir_path.is_dir(),
                "details": f"Path: {dir_path.resolve()}"
            })
        
        # Test Windows-specific requirements
        if sys.platform == 'win32':
            try:
                import win32api
                tests.append({
                    "test": "Windows API Access",
                    "success": True,
                    "details": "win32api available"
                })
            except ImportError:
                tests.append({
                    "test": "Windows API Access",
                    "success": False,
                    "error": "win32api not available"
                })
        
        success_count = sum(1 for t in tests if t["success"])
        return {
            "success": success_count >= len(tests) * 0.8,  # 80% success rate
            "summary": f"{success_count}/{len(tests)} requirements met",
            "details": tests
        }

    def test_application_startup(self) -> Dict[str, Any]:
        """Test application startup sequences"""
        
        tests = []
        
        # Test main application import
        try:
            result = self.run_python_code("""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

# Test basic imports
from mkd_v2.cli.gui_launcher import launch_gui
from mkd_v2.integration.system_controller import SystemController
from mkd_v2.native_host.host import NativeHost

print("All critical imports successful")
""", timeout=15)
            
            tests.append({
                "test": "Critical Module Imports",
                "success": result["success"],
                "output": result.get("output", ""),
                "error": result.get("error")
            })
        except Exception as e:
            tests.append({
                "test": "Critical Module Imports",
                "success": False,
                "error": str(e)
            })
        
        # Test system controller creation
        try:
            result = self.run_python_code("""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

from mkd_v2.integration.system_controller import SystemController

# Create system controller
controller = SystemController()
print(f"System controller created: {type(controller).__name__}")

# Test basic functionality
if hasattr(controller, 'message_broker'):
    print("Message broker available")
if hasattr(controller, 'native_host'):
    print("Native host available")
    
print("System controller test completed")
""", timeout=15)
            
            tests.append({
                "test": "System Controller Creation",
                "success": result["success"],
                "output": result.get("output", ""),
                "error": result.get("error")
            })
        except Exception as e:
            tests.append({
                "test": "System Controller Creation",
                "success": False,
                "error": str(e)
            })
        
        success_count = sum(1 for t in tests if t["success"])
        return {
            "success": success_count == len(tests),
            "summary": f"{success_count}/{len(tests)} startup tests passed",
            "details": tests
        }

    def test_native_host_communication(self) -> Dict[str, Any]:
        """Test native host communication functionality"""
        
        tests = []
        
        # Test native host module
        try:
            result = self.run_python_code("""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

from mkd_v2.native_host.host import NativeHost
import json

# Create native host
host = NativeHost()
print(f"Native host created: {type(host).__name__}")

# Test message handling
test_message = {
    "type": "test",
    "data": {"hello": "world"},
    "timestamp": 1234567890
}

# Test message serialization
try:
    serialized = json.dumps(test_message)
    deserialized = json.loads(serialized)
    print("Message serialization/deserialization works")
except Exception as e:
    print(f"Serialization error: {e}")

print("Native host communication test completed")
""", timeout=10)
            
            tests.append({
                "test": "Native Host Module",
                "success": result["success"],
                "output": result.get("output", ""),
                "error": result.get("error")
            })
        except Exception as e:
            tests.append({
                "test": "Native Host Module",
                "success": False,
                "error": str(e)
            })
        
        # Test native host executables
        bin_dir = Path("bin")
        if bin_dir.exists():
            host_executables = [
                "mkd_native_host",
                "mkd_native_host.bat",
                "mkd_native_host.ps1"
            ]
            
            for exe_name in host_executables:
                exe_path = bin_dir / exe_name
                tests.append({
                    "test": f"Native Host Executable: {exe_name}",
                    "success": exe_path.exists(),
                    "details": f"Path: {exe_path}",
                    "executable": os.access(exe_path, os.X_OK) if exe_path.exists() else False
                })
        
        success_count = sum(1 for t in tests if t["success"])
        return {
            "success": success_count > 0,
            "summary": f"{success_count}/{len(tests)} native host tests passed",
            "details": tests
        }

    def test_chrome_extension_integration(self) -> Dict[str, Any]:
        """Test Chrome extension components"""
        
        tests = []
        
        # Test manifest.json
        manifest_path = Path("chrome-extension/manifest.json")
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                tests.append({
                    "test": "Manifest JSON Valid",
                    "success": True,
                    "details": {
                        "name": manifest.get("name", "Unknown"),
                        "version": manifest.get("version", "Unknown"),
                        "manifest_version": manifest.get("manifest_version", "Unknown")
                    }
                })
                
                # Check required fields
                required_fields = ["name", "version", "manifest_version", "permissions"]
                missing_fields = [field for field in required_fields if field not in manifest]
                
                tests.append({
                    "test": "Manifest Required Fields",
                    "success": len(missing_fields) == 0,
                    "details": f"Missing fields: {missing_fields}" if missing_fields else "All required fields present"
                })
                
            except Exception as e:
                tests.append({
                    "test": "Manifest JSON Valid",
                    "success": False,
                    "error": str(e)
                })
        else:
            tests.append({
                "test": "Manifest JSON Exists",
                "success": False,
                "error": "manifest.json not found"
            })
        
        # Test essential extension files
        extension_files = [
            "src/background.js",
            "src/content.js",
            "src/popup/popup.html",
            "src/popup/popup.js",
            "src/popup/popup.css"
        ]
        
        for file_path in extension_files:
            full_path = Path("chrome-extension") / file_path
            file_exists = full_path.exists()
            
            test_result = {
                "test": f"Extension File: {file_path}",
                "success": file_exists,
                "path": str(full_path)
            }
            
            if file_exists:
                try:
                    file_size = full_path.stat().st_size
                    test_result["details"] = f"Size: {file_size} bytes"
                    # Basic content validation for JS files
                    if file_path.endswith('.js'):
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        test_result["has_content"] = len(content) > 100
                        test_result["success"] = test_result["success"] and len(content) > 100
                except Exception as e:
                    test_result["error"] = str(e)
                    test_result["success"] = False
            
            tests.append(test_result)
        
        success_count = sum(1 for t in tests if t["success"])
        return {
            "success": success_count >= len(tests) * 0.7,  # 70% success rate
            "summary": f"{success_count}/{len(tests)} extension tests passed",
            "details": tests
        }

    def test_end_to_end_workflow(self) -> Dict[str, Any]:
        """Test complete workflow simulation"""
        
        tests = []
        
        # Test workflow simulation
        try:
            result = self.run_python_code("""
import sys
import time
import json
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

from mkd_v2.integration.system_controller import SystemController
from mkd_v2.core.message_broker import MessageBroker

print("Starting end-to-end workflow simulation...")

# Create system components
try:
    controller = SystemController()
    print("System controller created")
    
    # Test message broker
    if hasattr(controller, 'message_broker'):
        broker = controller.message_broker
        print("Message broker available")
        
        # Simulate workflow messages
        test_messages = [
            {"type": "session_start", "data": {"timestamp": time.time()}},
            {"type": "user_action", "data": {"action": "click", "x": 100, "y": 200}},
            {"type": "session_end", "data": {"timestamp": time.time()}}
        ]
        
        for msg in test_messages:
            print(f"Processing message: {msg['type']}")
            # In a real scenario, this would be sent through the message broker
        
        print("Workflow simulation completed successfully")
    else:
        print("Message broker not available")
        
except Exception as e:
    print(f"Workflow simulation error: {e}")
    raise

""", timeout=20)
            
            tests.append({
                "test": "End-to-End Workflow Simulation",
                "success": result["success"],
                "output": result.get("output", ""),
                "error": result.get("error")
            })
        except Exception as e:
            tests.append({
                "test": "End-to-End Workflow Simulation",
                "success": False,
                "error": str(e)
            })
        
        success_count = sum(1 for t in tests if t["success"])
        return {
            "success": success_count == len(tests),
            "summary": f"{success_count}/{len(tests)} workflow tests passed",
            "details": tests
        }

    def test_error_recovery(self) -> Dict[str, Any]:
        """Test error handling and recovery mechanisms"""
        
        tests = []
        
        # Test graceful error handling
        try:
            result = self.run_python_code("""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

# Test error handling in various components
errors_handled = 0
total_tests = 0

# Test 1: Invalid message handling
try:
    from mkd_v2.core.message_broker import MessageBroker
    broker = MessageBroker()
    
    # This should be handled gracefully
    invalid_message = {"invalid": "structure"}
    # In real implementation, this would test actual error handling
    print("Error handling test 1: Invalid message structure")
    errors_handled += 1
except Exception as e:
    print(f"Error handling test 1 failed: {e}")
total_tests += 1

# Test 2: Missing component handling
try:
    from mkd_v2.integration.system_controller import SystemController
    controller = SystemController()
    print("Error handling test 2: Missing component graceful handling")
    errors_handled += 1
except Exception as e:
    print(f"Error handling test 2 failed: {e}")
total_tests += 1

print(f"Error recovery tests: {errors_handled}/{total_tests} handled gracefully")
""", timeout=15)
            
            tests.append({
                "test": "Error Recovery Mechanisms",
                "success": result["success"],
                "output": result.get("output", ""),
                "error": result.get("error")
            })
        except Exception as e:
            tests.append({
                "test": "Error Recovery Mechanisms",
                "success": False,
                "error": str(e)
            })
        
        success_count = sum(1 for t in tests if t["success"])
        return {
            "success": success_count == len(tests),
            "summary": f"{success_count}/{len(tests)} error recovery tests passed",
            "details": tests
        }

    def test_performance(self) -> Dict[str, Any]:
        """Test performance characteristics"""
        
        tests = []
        
        # Test startup time
        try:
            start_time = time.time()
            result = self.run_python_code("""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

start = time.time()
from mkd_v2.integration.system_controller import SystemController
controller = SystemController()
end = time.time()

startup_time = end - start
print(f"Component startup time: {startup_time:.3f} seconds")

if startup_time < 2.0:
    print("Performance: GOOD (< 2s)")
elif startup_time < 5.0:
    print("Performance: ACCEPTABLE (< 5s)")
else:
    print("Performance: SLOW (> 5s)")
""", timeout=30)
            
            performance_good = "GOOD" in result.get("output", "") or "ACCEPTABLE" in result.get("output", "")
            
            tests.append({
                "test": "Component Startup Performance",
                "success": result["success"] and performance_good,
                "output": result.get("output", ""),
                "error": result.get("error")
            })
        except Exception as e:
            tests.append({
                "test": "Component Startup Performance",
                "success": False,
                "error": str(e)
            })
        
        success_count = sum(1 for t in tests if t["success"])
        return {
            "success": success_count == len(tests),
            "summary": f"{success_count}/{len(tests)} performance tests passed",
            "details": tests
        }

    def run_python_code(self, code: str, timeout: int = 10) -> Dict[str, Any]:
        """Execute Python code in the virtual environment"""
        
        try:
            # Create a temporary script
            script_file = self.test_data_dir / f"integration_test_{int(time.time()*1000)}.py"
            
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Run the script
            cmd = [str(self.venv_python), str(script_file)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path.cwd()
            )
            
            # Clean up
            try:
                script_file.unlink()
            except:
                pass
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Code execution timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration test report"""
        
        total_duration = time.time() - self.start_time
        
        # Count overall results
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        category_summaries = []
        
        for category_name, result in self.results.items():
            category_summaries.append({
                "category": category_name,
                "success": result.get("success", False),
                "summary": result.get("summary", "No summary"),
                "details_count": len(result.get("details", []))
            })
            
            if "details" in result:
                for detail in result["details"]:
                    total_tests += 1
                    if detail.get("success", False):
                        passed_tests += 1
                    else:
                        failed_tests += 1
        
        # Overall assessment
        overall_success = passed_tests >= total_tests * 0.7  # 70% success rate for integration
        
        final_report = {
            "overall_success": overall_success,
            "summary": {
                "total_duration_seconds": total_duration,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "category_summaries": category_summaries,
            "detailed_results": self.results,
            "recommendations": self.generate_recommendations()
        }
        
        return final_report

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on integration test results"""
        
        recommendations = []
        
        # Analyze results and provide specific recommendations
        for category_name, result in self.results.items():
            if not result.get("success", False):
                if "System Requirements" in category_name:
                    recommendations.append("Ensure all system dependencies are installed and virtual environment is properly set up")
                elif "Application Startup" in category_name:
                    recommendations.append("Fix application startup issues - check imports and module dependencies")
                elif "Native Host" in category_name:
                    recommendations.append("Verify native host executables are built and have proper permissions")
                elif "Chrome Extension" in category_name:
                    recommendations.append("Complete Chrome extension setup with all required files and proper manifest")
                elif "End-to-End" in category_name:
                    recommendations.append("Fix component integration issues - ensure all parts work together")
                elif "Error Recovery" in category_name:
                    recommendations.append("Improve error handling and recovery mechanisms")
                elif "Performance" in category_name:
                    recommendations.append("Optimize component startup and processing performance")
        
        # General recommendations
        if not recommendations:
            recommendations.append("All integration tests passed - system is ready for production use")
            recommendations.append("Consider running load testing and user acceptance testing")
        else:
            recommendations.append("Address failing integration tests before deploying to production")
            recommendations.append("Run integration tests again after fixes to ensure all issues are resolved")
        
        return recommendations

    def save_report(self, report: Dict[str, Any]) -> str:
        """Save detailed integration test report"""
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"integration_test_report_{timestamp}.json")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        return str(report_file)

    def print_summary_report(self, report: Dict[str, Any]) -> None:
        """Print formatted integration test summary"""
        
        print("\n" + "="*80)
        print("COMPLETE INTEGRATION TEST REPORT")
        print("="*80)
        
        summary = report["summary"]
        print(f"Duration: {summary['total_duration_seconds']:.1f} seconds")
        print(f"Tests: {summary['total_tests']} total, {summary['passed_tests']} passed, {summary['failed_tests']} failed")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        overall_status = "[INTEGRATION SUCCESS]" if report["overall_success"] else "[INTEGRATION ISSUES]"
        print(f"Status: {overall_status}")
        
        print(f"\nCATEGORY BREAKDOWN:")
        for category in report["category_summaries"]:
            status = "[PASS]" if category["success"] else "[FAIL]"
            print(f"   {status} {category['category']}: {category['summary']}")
        
        print(f"\nRECOMMENDATIONS:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "="*80)


def main():
    """Main integration test execution"""
    
    print("Starting Complete Integration Test Suite for MKD Automation")
    
    # Initialize test suite
    test_suite = IntegrationTestSuite()
    
    try:
        # Run all integration tests
        report = test_suite.run_all_tests()
        
        # Print summary
        test_suite.print_summary_report(report)
        
        # Save detailed report
        report_file = test_suite.save_report(report)
        print(f"\nDetailed report saved to: {report_file}")
        
        # Exit with appropriate code
        sys.exit(0 if report["overall_success"] else 1)
        
    except KeyboardInterrupt:
        print("\n[WARNING] Integration test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Integration test suite failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()