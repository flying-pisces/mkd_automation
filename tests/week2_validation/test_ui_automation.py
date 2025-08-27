#!/usr/bin/env python3
"""
UI Automation and Element Detection Tests

Tests the intelligent UI automation system including:
- Element detection and recognition
- Window management
- Automation engine functionality
- Context-aware interactions
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mkd_v2.automation import AutomationEngine, ElementDetector, WindowManager
from mkd_v2.automation.element_detector import create_element_detector, VisualElementDetector
from mkd_v2.automation.window_manager import create_window_manager
from mkd_v2.platform.detector import PlatformDetector

import logging

# Configure logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "ui_automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class UIAutomationTester:
    """Test UI automation and element detection functionality."""
    
    def __init__(self):
        self.platform = None
        self.automation_engine = None
        self.window_manager = None
        self.element_detector = None
        self.results = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all UI automation tests."""
        logger.info("🚀 Starting UI Automation Tests")
        
        tests = [
            ("Platform Setup", self.test_platform_setup),
            ("Window Manager", self.test_window_manager),
            ("Element Detector", self.test_element_detector),
            ("Automation Engine", self.test_automation_engine),
            ("Window Operations", self.test_window_operations),
            ("Element Detection", self.test_element_detection),
            ("Coordinate Interactions", self.test_coordinate_interactions),
            ("Automation Status", self.test_automation_status)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"📝 Running: {test_name}")
            try:
                result = test_func()
                self.results.append({
                    'test': test_name,
                    'status': 'PASS' if result.get('success', False) else 'FAIL',
                    'details': result
                })
                logger.info(f"✅ {test_name}: {'PASS' if result.get('success', False) else 'FAIL'}")
            except Exception as e:
                self.results.append({
                    'test': test_name,
                    'status': 'ERROR',
                    'error': str(e)
                })
                logger.error(f"❌ {test_name}: ERROR - {e}")
        
        return self._generate_report()
    
    def test_platform_setup(self) -> Dict[str, Any]:
        """Test platform and automation setup."""
        try:
            # Initialize platform
            self.platform = PlatformDetector.detect()
            init_result = self.platform.initialize()
            
            # Create automation engine
            self.automation_engine = AutomationEngine(self.platform)
            
            # Create components
            self.window_manager = create_window_manager()
            self.element_detector = create_element_detector(
                screenshot_func=self.platform.take_screenshot
            )
            
            return {
                'success': init_result.get('success', False),
                'platform_name': self.platform.name,
                'platform_version': getattr(self.platform, 'version', 'unknown'),
                'automation_engine_created': self.automation_engine is not None,
                'window_manager_created': self.window_manager is not None,
                'element_detector_created': self.element_detector is not None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Platform setup failed: {e}'
            }
    
    def test_window_manager(self) -> Dict[str, Any]:
        """Test window manager functionality."""
        try:
            if not self.window_manager:
                self.window_manager = create_window_manager()
            
            # Test active window detection
            active_window = self.window_manager.get_active_window()
            
            # Test window list
            window_list = self.window_manager.get_window_list()
            
            # Test window at point (safe coordinates)
            window_at_point = self.window_manager.get_window_at_point(400, 300)
            
            return {
                'success': len(window_list) > 0,  # Should have at least some windows
                'active_window_detected': active_window is not None,
                'active_window_title': active_window.title if active_window else None,
                'total_windows': len(window_list),
                'window_at_point_detected': window_at_point is not None,
                'sample_windows': [
                    {'title': w.title, 'process_name': w.process_name} 
                    for w in window_list[:5]  # First 5 windows
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Window manager test failed: {e}'
            }
    
    def test_element_detector(self) -> Dict[str, Any]:
        """Test element detector functionality."""
        try:
            if not self.element_detector:
                self.element_detector = create_element_detector()
            
            # Test element detection at point
            point_result = self.element_detector.detect_elements_at_point(400, 300, radius=100)
            
            # Test element detection in region
            region_result = self.element_detector.detect_elements_in_region(300, 200, 200, 200)
            
            # Test text element detection
            text_result = self.element_detector.detect_text_elements()
            
            # Test element search by text
            test_element = self.element_detector.find_element_by_text("test", fuzzy=True)
            
            return {
                'success': True,  # Basic functionality test
                'point_detection': {
                    'success': point_result.success,
                    'elements_found': len(point_result.elements),
                    'detection_time': point_result.detection_time
                },
                'region_detection': {
                    'success': region_result.success,
                    'elements_found': len(region_result.elements),
                    'detection_time': region_result.detection_time
                },
                'text_detection': {
                    'success': text_result.success,
                    'elements_found': len(text_result.elements),
                    'detection_time': text_result.detection_time
                },
                'element_search': test_element is not None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Element detector test failed: {e}'
            }
    
    def test_automation_engine(self) -> Dict[str, Any]:
        """Test automation engine functionality."""
        try:
            if not self.automation_engine:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
                self.automation_engine = AutomationEngine(self.platform)
            
            # Test automation status
            status = self.automation_engine.get_automation_status()
            
            # Test safe coordinate click (empty area)
            click_result = self.automation_engine.click_at_coordinates(600, 500)
            
            # Test text typing (safe)
            type_result = self.automation_engine.type_text("test automation")
            
            # Test element region detection
            elements = self.automation_engine.get_elements_in_region(400, 300, 100, 100)
            
            return {
                'success': status is not None,
                'status': status,
                'click_result': click_result,
                'type_result': type_result,
                'elements_detected': len(elements)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Automation engine test failed: {e}'
            }
    
    def test_window_operations(self) -> Dict[str, Any]:
        """Test window management operations."""
        try:
            if not self.window_manager:
                self.window_manager = create_window_manager()
            
            # Get current active window
            initial_window = self.window_manager.get_active_window()
            
            # Try to focus a different window (if available)
            window_list = self.window_manager.get_window_list()
            
            focus_results = []
            if len(window_list) > 1:
                for window in window_list[:3]:  # Try first 3 windows
                    if window != initial_window:
                        focus_result = self.window_manager.focus_window(window.window_id)
                        focus_results.append({
                            'window_title': window.title,
                            'focus_success': focus_result
                        })
                        break
            
            # Test window screenshot (optional - may not work on all platforms)
            screenshot_result = None
            if initial_window:
                try:
                    screenshot_data = self.window_manager.get_window_screenshot(initial_window.window_id)
                    screenshot_result = screenshot_data is not None
                except:
                    screenshot_result = False
            
            return {
                'success': len(window_list) > 0,
                'initial_window': initial_window.title if initial_window else None,
                'total_windows': len(window_list),
                'focus_operations': focus_results,
                'screenshot_available': screenshot_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Window operations test failed: {e}'
            }
    
    def test_element_detection(self) -> Dict[str, Any]:
        """Test various element detection scenarios."""
        try:
            if not self.element_detector:
                self.element_detector = create_element_detector()
            
            test_scenarios = []
            
            # Test detection at different screen locations
            test_points = [
                (100, 100), (400, 300), (700, 400), (200, 500)
            ]
            
            for x, y in test_points:
                result = self.element_detector.detect_elements_at_point(x, y, radius=50)
                test_scenarios.append({
                    'location': f"({x}, {y})",
                    'success': result.success,
                    'elements_found': len(result.elements),
                    'detection_time': result.detection_time
                })
            
            # Test region detection with different sizes
            region_tests = [
                {'x': 300, 'y': 200, 'width': 100, 'height': 100},
                {'x': 100, 'y': 100, 'width': 200, 'height': 150},
                {'x': 500, 'y': 300, 'width': 150, 'height': 100}
            ]
            
            region_results = []
            for region in region_tests:
                result = self.element_detector.detect_elements_in_region(**region)
                region_results.append({
                    'region': region,
                    'success': result.success,
                    'elements_found': len(result.elements)
                })
            
            total_elements = sum(len(r.elements) for r in [
                self.element_detector.detect_elements_at_point(400, 300, 100)
            ])
            
            return {
                'success': True,  # Basic functionality exists
                'point_tests': test_scenarios,
                'region_tests': region_results,
                'total_elements_sample': total_elements
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Element detection test failed: {e}'
            }
    
    def test_coordinate_interactions(self) -> Dict[str, Any]:
        """Test coordinate-based interactions."""
        try:
            if not self.automation_engine:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
                self.automation_engine = AutomationEngine(self.platform)
            
            # Test safe coordinate interactions
            interaction_results = []
            
            # Test clicks at safe locations
            safe_coordinates = [
                (600, 400),  # Middle-right area
                (400, 500),  # Lower-middle area
                (700, 300)   # Right-middle area
            ]
            
            for x, y in safe_coordinates:
                # Small delay between clicks
                time.sleep(0.2)
                
                click_result = self.automation_engine.click_at_coordinates(x, y)
                interaction_results.append({
                    'coordinates': (x, y),
                    'action': 'click',
                    'success': click_result
                })
            
            # Test text input (minimal)
            time.sleep(0.5)
            type_result = self.automation_engine.type_text("hi")
            
            return {
                'success': any(r['success'] for r in interaction_results),
                'click_results': interaction_results,
                'type_result': type_result,
                'total_interactions': len(interaction_results) + 1
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Coordinate interactions test failed: {e}'
            }
    
    def test_automation_status(self) -> Dict[str, Any]:
        """Test automation engine status and monitoring."""
        try:
            if not self.automation_engine:
                self.platform = PlatformDetector.detect()
                self.platform.initialize()
                self.automation_engine = AutomationEngine(self.platform)
            
            # Get initial status
            initial_status = self.automation_engine.get_automation_status()
            
            # Perform some operations
            self.automation_engine.click_at_coordinates(500, 400)
            time.sleep(0.1)
            self.automation_engine.type_text("status test")
            
            # Get status after operations
            final_status = self.automation_engine.get_automation_status()
            
            # Check for status changes
            history_changed = (
                final_status['history']['operations_count'] > 
                initial_status['history']['operations_count']
            )
            
            return {
                'success': initial_status is not None and final_status is not None,
                'initial_status': initial_status,
                'final_status': final_status,
                'history_tracking': history_changed,
                'platform': final_status.get('platform'),
                'configuration': final_status.get('configuration', {})
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Automation status test failed: {e}'
            }
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.results if r['status'] == 'ERROR'])
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'errors': error_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'results': self.results,
            'recommendations': []
        }
        
        # Add recommendations based on failures
        for result in self.results:
            if result['status'] != 'PASS':
                test_name = result['test']
                if 'Element Detection' in test_name:
                    report['recommendations'].append(
                        "Install OpenCV and Tesseract for better element detection: pip install opencv-python pytesseract"
                    )
                elif 'Window Manager' in test_name:
                    report['recommendations'].append(
                        "Check platform-specific window management permissions"
                    )
                elif 'Platform Setup' in test_name:
                    report['recommendations'].append(
                        "Ensure platform initialization and required dependencies are installed"
                    )
        
        return report


def main():
    """Run UI automation tests."""
    tester = UIAutomationTester()
    report = tester.run_all_tests()
    
    # Save detailed report
    log_dir = Path(__file__).parent / "logs"
    report_file = log_dir / "ui_automation_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "="*60)
    print("🤖 UI AUTOMATION TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']} ✅")
    print(f"Failed: {report['summary']['failed']} ❌")
    print(f"Errors: {report['summary']['errors']} 🚨")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    
    if report['recommendations']:
        print("\n🔧 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    return report['summary']['success_rate'] >= 70  # 70% pass rate threshold


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)