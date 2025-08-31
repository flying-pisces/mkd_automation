#!/usr/bin/env python
"""
MKD Automation Self-Test Suite
Comprehensive testing with logging and reporting
"""

import sys
import os
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
import subprocess
import platform

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Setup paths
SELF_TEST_DIR = Path(__file__).parent
LOG_DIR = SELF_TEST_DIR / "logs"
REPORT_DIR = SELF_TEST_DIR / "reports"

# Ensure directories exist
LOG_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

# Setup logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = LOG_DIR / f"self_test_{timestamp}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("self_test")

class TestResult:
    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.status = "pending"
        self.message = ""
        self.error = None
        self.start_time = None
        self.end_time = None
        self.duration = 0
        
    def start(self):
        self.start_time = datetime.now()
        logger.info(f"Starting test: {self.category}/{self.name}")
        
    def success(self, message=""):
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.status = "passed"
        self.message = message
        logger.info(f"[PASS] {self.category}/{self.name}: {message}")
        
    def fail(self, error):
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.status = "failed"
        self.error = str(error)
        logger.error(f"[FAIL] {self.category}/{self.name}: {error}")
        
    def skip(self, reason):
        self.status = "skipped"
        self.message = reason
        logger.warning(f"[SKIP] {self.category}/{self.name}: {reason}")
        
    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "status": self.status,
            "message": self.message,
            "error": self.error,
            "duration": self.duration
        }

class SelfTestSuite:
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
        
    def run_all_tests(self):
        """Run all test categories"""
        self.start_time = datetime.now()
        logger.info("="*60)
        logger.info("MKD AUTOMATION SELF-TEST SUITE")
        logger.info(f"Started at: {self.start_time}")
        logger.info(f"Platform: {platform.system()} {platform.release()}")
        logger.info(f"Python: {sys.version}")
        logger.info("="*60)
        
        # Run test categories
        self.test_environment()
        self.test_imports()
        self.test_core_modules()
        self.test_data_modules()
        self.test_platform_modules()
        self.test_recording_modules()
        self.test_playback_modules()
        self.test_chrome_extension()
        self.test_integration()
        
        self.end_time = datetime.now()
        self.generate_report()
        
    def test_environment(self):
        """Test environment setup"""
        # Test Python version
        test = TestResult("python_version", "environment")
        test.start()
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                test.success(f"Python {version.major}.{version.minor}.{version.micro}")
            else:
                test.fail(f"Python version too old: {version}")
        except Exception as e:
            test.fail(str(e))
        self.results.append(test)
        
        # Test required packages
        packages = ["pytest", "msgpack", "cryptography"]
        for pkg in packages:
            test = TestResult(f"package_{pkg}", "environment")
            test.start()
            try:
                __import__(pkg)
                test.success(f"{pkg} installed")
            except ImportError:
                test.fail(f"{pkg} not installed")
            self.results.append(test)
            
    def test_imports(self):
        """Test all module imports"""
        modules = [
            ("mkd.core", ["config_manager", "session_manager", "script_manager"]),
            ("mkd.recording", ["recording_engine", "input_capturer"]),
            ("mkd.playback", ["playback_engine", "action_executor"]),
            ("mkd.platform", ["detector"]),
            ("mkd.data", ["script_storage", "encryption"])
        ]
        
        for module_path, submodules in modules:
            for submodule in submodules:
                test = TestResult(f"{module_path}.{submodule}", "imports")
                test.start()
                try:
                    full_path = f"{module_path}.{submodule}"
                    __import__(full_path)
                    test.success()
                except Exception as e:
                    test.fail(str(e))
                self.results.append(test)
                
    def test_core_modules(self):
        """Test core module functionality"""
        # ConfigManager
        test = TestResult("ConfigManager", "core")
        test.start()
        try:
            from mkd.core.config_manager import ConfigManager
            config = ConfigManager()
            settings = config.get_recording_settings()
            assert "sample_rate" in settings
            test.success(f"Sample rate: {settings['sample_rate']} Hz")
        except Exception as e:
            test.fail(str(e))
        self.results.append(test)
        
        # SessionManager
        test = TestResult("SessionManager", "core")
        test.start()
        try:
            from mkd.core.session_manager import SessionManager
            session = SessionManager()
            session.start_recording()
            assert session.is_recording()
            session.stop_recording()
            assert not session.is_recording()
            test.success(f"Session ID: {session.session_id}")
        except Exception as e:
            test.fail(str(e))
        self.results.append(test)
        
    def test_data_modules(self):
        """Test data module functionality"""
        test = TestResult("ScriptStorage", "data")
        test.start()
        try:
            from mkd.data.script_storage import ScriptStorage
            from mkd.data.models import AutomationScript, Action
            import tempfile
            
            storage = ScriptStorage()
            script = AutomationScript(
                name="Test",
                description="Test script",
                created_at=datetime.now(),
                actions=[
                    Action(type="mouse_move", data={"x": 100, "y": 100}, timestamp=0.0)
                ]
            )
            
            with tempfile.NamedTemporaryFile(suffix='.mkd', delete=False) as f:
                temp_path = f.name
            
            storage.save(script, temp_path)
            loaded = storage.load(temp_path)
            os.unlink(temp_path)
            
            assert loaded.name == script.name
            test.success("Save/load working")
        except Exception as e:
            test.fail(str(e))
        self.results.append(test)
        
    def test_platform_modules(self):
        """Test platform detection"""
        test = TestResult("PlatformDetector", "platform")
        test.start()
        try:
            from mkd.platform.detector import PlatformDetector
            detector = PlatformDetector()
            platform_name = detector.get_platform()
            impl = detector.get_implementation()
            test.success(f"Platform: {platform_name}, Implementation: {impl.__class__.__name__}")
        except Exception as e:
            test.fail(str(e))
        self.results.append(test)
        
    def test_recording_modules(self):
        """Test recording modules"""
        test = TestResult("RecordingEngine", "recording")
        test.start()
        try:
            from mkd.recording.recording_engine import RecordingEngine
            engine = RecordingEngine()
            assert not engine.is_recording
            test.success("Recording engine initialized")
        except Exception as e:
            test.fail(str(e))
        self.results.append(test)
        
    def test_playback_modules(self):
        """Test playback modules"""
        test = TestResult("PlaybackEngine", "playback")
        test.start()
        try:
            from mkd.playback.playback_engine import PlaybackEngine
            engine = PlaybackEngine()
            test.success("Playback engine initialized")
        except Exception as e:
            test.fail(str(e))
        self.results.append(test)
        
    def test_chrome_extension(self):
        """Test Chrome extension files"""
        test = TestResult("extension_files", "chrome")
        test.start()
        try:
            ext_dir = Path(__file__).parent.parent / "chrome-extension"
            required_files = [
                "manifest.json",
                "src/background.js",
                "src/content.js",
                "src/popup/popup.html",
                "src/popup/popup.js",
                "src/popup/popup.css"
            ]
            
            missing = []
            for file in required_files:
                if not (ext_dir / file).exists():
                    missing.append(file)
                    
            if missing:
                test.fail(f"Missing files: {', '.join(missing)}")
            else:
                test.success("All extension files present")
        except Exception as e:
            test.fail(str(e))
        self.results.append(test)
        
        # Validate manifest
        test = TestResult("manifest_validation", "chrome")
        test.start()
        try:
            manifest_path = Path(__file__).parent.parent / "chrome-extension" / "manifest.json"
            with open(manifest_path) as f:
                manifest = json.load(f)
            
            required_keys = ["manifest_version", "name", "version", "content_scripts"]
            missing_keys = [k for k in required_keys if k not in manifest]
            
            if missing_keys:
                test.fail(f"Missing manifest keys: {missing_keys}")
            else:
                test.success(f"Manifest v{manifest['manifest_version']}, Extension v{manifest['version']}")
        except Exception as e:
            test.fail(str(e))
        self.results.append(test)
        
    def test_integration(self):
        """Test integration between components"""
        test = TestResult("end_to_end_flow", "integration")
        test.start()
        try:
            from mkd.core.session_manager import SessionManager
            from mkd.data.models import Action
            from mkd.data.script_storage import ScriptStorage
            import tempfile
            
            # Create session
            session = SessionManager()
            session.start_recording()
            
            # Add some actions
            session.add_action(Action(type="mouse_move", data={"x": 50, "y": 50}, timestamp=0.0))
            session.add_action(Action(type="mouse_click", data={"button": "left"}, timestamp=1.0))
            
            # Stop and convert to script
            session.stop_recording()
            script = session.to_script()
            
            # Save and load
            storage = ScriptStorage()
            with tempfile.NamedTemporaryFile(suffix='.mkd', delete=False) as f:
                temp_path = f.name
            
            storage.save(script, temp_path)
            loaded = storage.load(temp_path)
            os.unlink(temp_path)
            
            assert len(loaded.actions) == 2
            test.success("End-to-end flow working")
        except Exception as e:
            test.fail(str(e))
        self.results.append(test)
        
    def generate_report(self):
        """Generate test report"""
        duration = (self.end_time - self.start_time).total_seconds()
        
        # Count results
        passed = sum(1 for r in self.results if r.status == "passed")
        failed = sum(1 for r in self.results if r.status == "failed")
        skipped = sum(1 for r in self.results if r.status == "skipped")
        total = len(self.results)
        
        # Generate JSON report
        report = {
            "timestamp": self.start_time.isoformat(),
            "duration": duration,
            "platform": platform.system(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%"
            },
            "results": [r.to_dict() for r in self.results]
        }
        
        report_file = REPORT_DIR / f"test_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Generate text summary
        summary_file = REPORT_DIR / f"test_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("="*60 + "\n")
            f.write("MKD AUTOMATION SELF-TEST REPORT\n")
            f.write("="*60 + "\n\n")
            f.write(f"Timestamp: {self.start_time}\n")
            f.write(f"Duration: {duration:.2f} seconds\n")
            f.write(f"Platform: {platform.system()} {platform.release()}\n")
            f.write(f"Python: {sys.version}\n\n")
            
            f.write("SUMMARY\n")
            f.write("-"*40 + "\n")
            f.write(f"Total Tests: {total}\n")
            f.write(f"Passed: {passed} ({passed/total*100:.1f}%)\n")
            f.write(f"Failed: {failed} ({failed/total*100:.1f}%)\n")
            f.write(f"Skipped: {skipped}\n\n")
            
            # Group by category
            categories = {}
            for r in self.results:
                if r.category not in categories:
                    categories[r.category] = []
                categories[r.category].append(r)
                
            f.write("RESULTS BY CATEGORY\n")
            f.write("-"*40 + "\n")
            for cat, results in categories.items():
                f.write(f"\n{cat.upper()}:\n")
                for r in results:
                    status_symbol = "[OK]" if r.status == "passed" else "[FAIL]" if r.status == "failed" else "[SKIP]"
                    f.write(f"  {status_symbol} {r.name}")
                    if r.message:
                        f.write(f" - {r.message}")
                    if r.error:
                        f.write(f" - ERROR: {r.error}")
                    f.write("\n")
                    
            # Failed tests details
            if failed > 0:
                f.write("\nFAILED TESTS DETAILS\n")
                f.write("-"*40 + "\n")
                for r in self.results:
                    if r.status == "failed":
                        f.write(f"\n{r.category}/{r.name}:\n")
                        f.write(f"  Error: {r.error}\n")
                        
        # Print summary
        logger.info("="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
        logger.info(f"Pass Rate: {passed/total*100:.1f}%")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Log file: {log_file}")
        logger.info(f"JSON report: {report_file}")
        logger.info(f"Text summary: {summary_file}")
        
        if failed == 0:
            logger.info("[SUCCESS] All tests passed!")
        else:
            logger.warning(f"[WARNING] {failed} tests failed. Check logs for details.")
            
        return report

if __name__ == "__main__":
    suite = SelfTestSuite()
    report = suite.run_all_tests()
    
    # Exit with appropriate code
    if report:
        sys.exit(0 if report["summary"]["failed"] == 0 else 1)
    else:
        sys.exit(1)