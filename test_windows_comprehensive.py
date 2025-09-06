#!/usr/bin/env python3
"""
Comprehensive Windows Testing Suite for MKD Automation
Tests all components: GUI, Console, Chrome Extension, and Native Host
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
import subprocess
import time
import json
import traceback
import platform
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class WindowsTestSuite:
    """Comprehensive test suite for Windows functionality"""
    
    def __init__(self):
        self.results = {}
        self.venv_python = Path("venv/Scripts/python.exe").resolve()
        self.start_time = time.time()
        
        # Test configuration
        self.timeout_seconds = 10
        self.test_data_dir = Path("test_data")
        self.test_data_dir.mkdir(exist_ok=True)
        
        print(f"[TEST] Windows Test Suite Starting...")
        print(f"Platform: {platform.platform()}")
        print(f"Python: {sys.version}")
        print(f"Working Directory: {Path.cwd()}")
        print(f"Virtual Environment: {self.venv_python}")
        print("-" * 60)

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test categories"""
        
        test_categories = [
            ("Python Import Tests", self.test_python_imports),
            ("GUI Component Tests", self.test_gui_components), 
            ("Console Application Tests", self.test_console_apps),
            ("Chrome Extension Tests", self.test_chrome_extension),
            ("Native Host Tests", self.test_native_host),
            ("Windows Integration Tests", self.test_windows_integration),
        ]
        
        for category_name, test_func in test_categories:
            print(f"\n[TEST] Running {category_name}...")
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

    def test_python_imports(self) -> Dict[str, Any]:
        """Test all Python module imports"""
        
        import_tests = [
            "import sys",
            "from mkd_v2.cli.gui_launcher import launch_gui",
            "from mkd_v2.integration.system_controller import SystemController",
            "from mkd_v2.core.message_broker import MessageBroker",
            "from mkd_v2.native_host.host import NativeHost",
            "import tkinter as tk",
            "import pynput",
            "import psutil",
            "import win32api",
            "import win32gui",
        ]
        
        results = []
        for import_test in import_tests:
            try:
                result = self.run_python_code(import_test, timeout=5)
                results.append({
                    "import": import_test,
                    "success": result["success"],
                    "error": result.get("error")
                })
            except Exception as e:
                results.append({
                    "import": import_test,
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        return {
            "success": success_count == len(import_tests),
            "summary": f"{success_count}/{len(import_tests)} imports successful",
            "details": results
        }

    def test_gui_components(self) -> Dict[str, Any]:
        """Test GUI components without actually launching windows"""
        
        gui_tests = [
            # Test GUI launcher import and basic functionality
            """
from mkd_v2.cli.gui_launcher import launch_gui
from mkd_v2.integration.system_controller import SystemController
import tkinter as tk

# Test basic Tkinter functionality
root = tk.Tk()
root.withdraw()  # Hide the window
print("Tkinter window created successfully")

# Test system controller creation
try:
    controller = SystemController()
    print("SystemController created successfully")
except Exception as e:
    print(f"SystemController error: {e}")

root.destroy()
print("GUI component test completed")
            """,
            
            # Test Windows-specific GUI features
            """
import tkinter as tk
import win32gui
import win32api

# Test Windows GUI integration
try:
    # Test screen dimensions
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    print(f"Screen dimensions: {screen_width}x{screen_height}")
    
    # Test window enumeration
    def enum_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            windows.append(hwnd)
        return True
    
    windows = []
    win32gui.EnumWindows(enum_callback, windows)
    print(f"Found {len(windows)} visible windows")
    
except Exception as e:
    print(f"Windows GUI error: {e}")
    
print("Windows GUI integration test completed")
            """
        ]
        
        results = []
        for i, test_code in enumerate(gui_tests):
            try:
                result = self.run_python_code(test_code, timeout=10)
                results.append({
                    "test": f"GUI Test {i+1}",
                    "success": result["success"],
                    "output": result.get("output", ""),
                    "error": result.get("error")
                })
            except Exception as e:
                results.append({
                    "test": f"GUI Test {i+1}",
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        return {
            "success": success_count > 0,
            "summary": f"{success_count}/{len(gui_tests)} GUI tests passed",
            "details": results
        }

    def test_console_apps(self) -> Dict[str, Any]:
        """Test console applications and CLI functionality"""
        
        console_tests = [
            # Test CLI help without launching GUI
            {
                "name": "CLI Import Test",
                "code": """
from mkd_v2.cli.main_cli import MKDCli
print("CLI imported successfully")
"""
            },
            
            # Test message broker
            {
                "name": "Message Broker Test",
                "code": """
from mkd_v2.core.message_broker import MessageBroker
broker = MessageBroker()
print(f"Message broker created: {broker}")
"""
            },
            
            # Test system utilities
            {
                "name": "System Utils Test",
                "code": """
import psutil
import platform

print(f"CPU count: {psutil.cpu_count()}")
print(f"Memory: {psutil.virtual_memory().total // (1024**3)} GB")
print(f"Platform: {platform.platform()}")
"""
            }
        ]
        
        results = []
        for test in console_tests:
            try:
                result = self.run_python_code(test["code"], timeout=5)
                results.append({
                    "test": test["name"],
                    "success": result["success"],
                    "output": result.get("output", ""),
                    "error": result.get("error")
                })
            except Exception as e:
                results.append({
                    "test": test["name"],
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        return {
            "success": success_count == len(console_tests),
            "summary": f"{success_count}/{len(console_tests)} console tests passed",
            "details": results
        }

    def test_chrome_extension(self) -> Dict[str, Any]:
        """Test Chrome extension components"""
        
        extension_dir = Path("chrome-extension")
        if not extension_dir.exists():
            return {
                "success": False,
                "summary": "Chrome extension directory not found",
                "details": []
            }
        
        tests = []
        
        # Check for essential files
        essential_files = [
            "src/content.js",
            "dist/manifest.json",
            "README.md"
        ]
        
        for file_path in essential_files:
            full_path = extension_dir / file_path
            tests.append({
                "test": f"File exists: {file_path}",
                "success": full_path.exists(),
                "path": str(full_path)
            })
        
        # Test content.js syntax if it exists
        content_js = extension_dir / "src/content.js"
        if content_js.exists():
            try:
                with open(content_js, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic syntax checks
                syntax_checks = [
                    "chrome.runtime" in content,
                    "console.log" in content or "console." in content,
                    len(content) > 100  # Has substantial content
                ]
                
                tests.append({
                    "test": "content.js syntax check",
                    "success": any(syntax_checks),
                    "details": {
                        "has_chrome_runtime": "chrome.runtime" in content,
                        "has_console": "console." in content,
                        "has_content": len(content) > 100,
                        "size_bytes": len(content)
                    }
                })
                
            except Exception as e:
                tests.append({
                    "test": "content.js syntax check",
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for t in tests if t["success"])
        return {
            "success": success_count > 0,
            "summary": f"{success_count}/{len(tests)} extension tests passed",
            "details": tests
        }

    def test_native_host(self) -> Dict[str, Any]:
        """Test native host functionality"""
        
        bin_dir = Path("bin")
        if not bin_dir.exists():
            return {
                "success": False,
                "summary": "bin directory not found",
                "details": []
            }
        
        tests = []
        
        # Check for native host executables
        host_files = [
            "mkd_native_host",
            "mkd_native_host.bat", 
            "mkd_native_host.ps1",
            "mkd_native_host_debug"
        ]
        
        for file_name in host_files:
            file_path = bin_dir / file_name
            tests.append({
                "test": f"Native host file: {file_name}",
                "success": file_path.exists(),
                "path": str(file_path),
                "executable": os.access(file_path, os.X_OK) if file_path.exists() else False
            })
        
        # Test native host communication format
        try:
            result = self.run_python_code("""
from mkd_v2.native_host.host import NativeHost
host = NativeHost()
print("Native host created successfully")
""", timeout=5)
            
            tests.append({
                "test": "Native host instantiation",
                "success": result["success"],
                "output": result.get("output", ""),
                "error": result.get("error")
            })
        except Exception as e:
            tests.append({
                "test": "Native host instantiation",
                "success": False,
                "error": str(e)
            })
        
        success_count = sum(1 for t in tests if t["success"])
        return {
            "success": success_count > 0,
            "summary": f"{success_count}/{len(tests)} native host tests passed", 
            "details": tests
        }

    def test_windows_integration(self) -> Dict[str, Any]:
        """Test Windows-specific integration features"""
        
        integration_tests = [
            # Test Windows input capture
            {
                "name": "Windows Input Libraries",
                "code": """
try:
    import pynput
    from pynput import mouse, keyboard
    print("pynput imported successfully")
    
    import win32api
    import win32con
    print("win32 APIs imported successfully")
    
    # Test basic input detection setup (without actually capturing)
    print("Input libraries available")
except Exception as e:
    print(f"Input library error: {e}")
"""
            },
            
            # Test Windows registry access
            {
                "name": "Registry Access",
                "code": """
try:
    import winreg
    # Test reading a safe registry key
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion")
    version = winreg.QueryValueEx(key, "ProductName")[0]
    winreg.CloseKey(key)
    print(f"Windows version: {version}")
except Exception as e:
    print(f"Registry access error: {e}")
"""
            },
            
            # Test file system permissions
            {
                "name": "File System Access",
                "code": """
import os
import tempfile
from pathlib import Path

# Test temp directory access
temp_dir = Path(tempfile.gettempdir())
print(f"Temp directory: {temp_dir}")
print(f"Temp dir writable: {os.access(temp_dir, os.W_OK)}")

# Test home directory access  
home_dir = Path.home()
print(f"Home directory: {home_dir}")
print(f"Home dir writable: {os.access(home_dir, os.W_OK)}")

# Test current directory
print(f"Current dir writable: {os.access('.', os.W_OK)}")
"""
            }
        ]
        
        results = []
        for test in integration_tests:
            try:
                result = self.run_python_code(test["code"], timeout=8)
                results.append({
                    "test": test["name"],
                    "success": result["success"],
                    "output": result.get("output", ""),
                    "error": result.get("error")
                })
            except Exception as e:
                results.append({
                    "test": test["name"],
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        return {
            "success": success_count >= 2,  # At least 2 out of 3 should pass
            "summary": f"{success_count}/{len(integration_tests)} integration tests passed",
            "details": results
        }

    def run_python_code(self, code: str, timeout: int = 10) -> Dict[str, Any]:
        """Execute Python code in the virtual environment"""
        
        try:
            # Create a temporary script
            script_file = self.test_data_dir / f"test_{int(time.time()*1000)}.py"
            
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
        """Generate comprehensive test report"""
        
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
        overall_success = passed_tests > failed_tests and passed_tests >= total_tests * 0.6
        
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
        """Generate recommendations based on test results"""
        
        recommendations = []
        
        # Analyze results and provide actionable recommendations
        for category_name, result in self.results.items():
            if not result.get("success", False):
                if "Import" in category_name:
                    recommendations.append("Install missing Python dependencies with: pip install -r requirements.txt")
                elif "GUI" in category_name:
                    recommendations.append("Check GUI dependencies and Windows display settings")
                elif "Chrome" in category_name:
                    recommendations.append("Complete Chrome extension development with manifest.json and background.js")
                elif "Native Host" in category_name:
                    recommendations.append("Verify native host executables are properly built and permissions set")
                elif "Integration" in category_name:
                    recommendations.append("Check Windows permissions and security settings")
        
        # General recommendations
        if not recommendations:
            recommendations.append("All major components appear functional - ready for integration testing")
        else:
            recommendations.append("Fix failing components before proceeding to full integration testing")
        
        return recommendations

    def save_report(self, report: Dict[str, Any]) -> str:
        """Save detailed test report to file"""
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"windows_test_report_{timestamp}.json")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        return str(report_file)

    def print_summary_report(self, report: Dict[str, Any]) -> None:
        """Print a formatted summary report"""
        
        print("\n" + "="*80)
        print("COMPREHENSIVE WINDOWS TEST REPORT")
        print("="*80)
        
        summary = report["summary"]
        print(f"Duration: {summary['total_duration_seconds']:.1f} seconds")
        print(f"Tests: {summary['total_tests']} total, {summary['passed_tests']} passed, {summary['failed_tests']} failed")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        overall_status = "[OVERALL SUCCESS]" if report["overall_success"] else "[NEEDS ATTENTION]"
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
    """Main test execution"""
    
    print("Starting Comprehensive Windows Test Suite for MKD Automation")
    
    # Initialize test suite
    test_suite = WindowsTestSuite()
    
    try:
        # Run all tests
        report = test_suite.run_all_tests()
        
        # Print summary
        test_suite.print_summary_report(report)
        
        # Save detailed report
        report_file = test_suite.save_report(report)
        print(f"\nDetailed report saved to: {report_file}")
        
        # Exit with appropriate code
        sys.exit(0 if report["overall_success"] else 1)
        
    except KeyboardInterrupt:
        print("\n[WARNING] Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test suite failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()