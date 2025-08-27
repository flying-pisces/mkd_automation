#!/usr/bin/env python3
"""
Visual Overlay Rendering System Tests

Tests the cross-platform overlay rendering including:
- Overlay renderer initialization
- Overlay creation and management
- Cross-platform compatibility
- Visual feedback systems
- Performance and cleanup
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mkd_v2.ui.overlay_renderer import create_overlay_renderer, OverlayRenderer
from mkd_v2.ui.overlay import ScreenOverlay, BorderConfig, TimerConfig
from mkd_v2.platform.detector import PlatformDetector

import logging

# Configure logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "visual_overlays.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VisualOverlayTester:
    """Test visual overlay rendering functionality."""
    
    def __init__(self):
        self.renderer = None
        self.overlay_ids = []
        self.results = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all visual overlay tests."""
        logger.info("🚀 Starting Visual Overlay Tests")
        
        tests = [
            ("Overlay Renderer Creation", self.test_renderer_creation),
            ("Basic Overlay Creation", self.test_basic_overlay_creation),
            ("Multiple Overlays", self.test_multiple_overlays),
            ("Overlay Updates", self.test_overlay_updates),
            ("Overlay Styles", self.test_overlay_styles),
            ("Screen Overlay System", self.test_screen_overlay_system),
            ("Performance Test", self.test_performance),
            ("Cleanup Test", self.test_cleanup)
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
    
    def test_renderer_creation(self) -> Dict[str, Any]:
        """Test overlay renderer creation."""
        try:
            # Create renderer
            self.renderer = create_overlay_renderer()
            
            # Check renderer type and properties
            renderer_type = type(self.renderer).__name__
            
            return {
                'success': self.renderer is not None,
                'renderer_type': renderer_type,
                'has_create_method': hasattr(self.renderer, 'create_overlay'),
                'has_update_method': hasattr(self.renderer, 'update_overlay'),
                'has_destroy_method': hasattr(self.renderer, 'destroy_overlay')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Renderer creation failed: {e}'
            }
    
    def test_basic_overlay_creation(self) -> Dict[str, Any]:
        """Test basic overlay creation."""
        try:
            if not self.renderer:
                self.renderer = create_overlay_renderer()
            
            # Create a simple overlay
            overlay_id = self.renderer.create_overlay(
                x=200, y=200, width=100, height=100,
                style="recording", color="red", opacity=0.8
            )
            
            if overlay_id:
                self.overlay_ids.append(overlay_id)
                
                # Let it display briefly
                time.sleep(1)
                
                # Clean up
                destroy_result = self.renderer.destroy_overlay(overlay_id)
                if overlay_id in self.overlay_ids:
                    self.overlay_ids.remove(overlay_id)
            else:
                destroy_result = False
            
            return {
                'success': bool(overlay_id),
                'overlay_id': overlay_id,
                'destroy_result': destroy_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Basic overlay creation failed: {e}'
            }
    
    def test_multiple_overlays(self) -> Dict[str, Any]:
        """Test creating multiple overlays."""
        try:
            if not self.renderer:
                self.renderer = create_overlay_renderer()
            
            # Create multiple overlays
            overlay_configs = [
                {'x': 100, 'y': 100, 'width': 50, 'height': 50, 'style': 'recording', 'color': 'red'},
                {'x': 300, 'y': 100, 'width': 50, 'height': 50, 'style': 'border', 'color': 'blue'},
                {'x': 500, 'y': 100, 'width': 50, 'height': 50, 'style': 'highlight', 'color': 'green'}
            ]
            
            created_overlays = []
            for config in overlay_configs:
                overlay_id = self.renderer.create_overlay(**config)
                if overlay_id:
                    created_overlays.append(overlay_id)
                    self.overlay_ids.append(overlay_id)
            
            # Let them display
            time.sleep(2)
            
            # Clean up all
            destroyed_count = 0
            for overlay_id in created_overlays:
                if self.renderer.destroy_overlay(overlay_id):
                    destroyed_count += 1
                if overlay_id in self.overlay_ids:
                    self.overlay_ids.remove(overlay_id)
            
            return {
                'success': len(created_overlays) == len(overlay_configs),
                'requested_overlays': len(overlay_configs),
                'created_overlays': len(created_overlays),
                'destroyed_overlays': destroyed_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Multiple overlays test failed: {e}'
            }
    
    def test_overlay_updates(self) -> Dict[str, Any]:
        """Test overlay property updates."""
        try:
            if not self.renderer:
                self.renderer = create_overlay_renderer()
            
            # Create overlay
            overlay_id = self.renderer.create_overlay(
                x=400, y=300, width=80, height=80,
                style="recording", color="red", opacity=0.8
            )
            
            if not overlay_id:
                return {
                    'success': False,
                    'error': 'Failed to create overlay for update test'
                }
            
            self.overlay_ids.append(overlay_id)
            
            # Initial display
            time.sleep(1)
            
            # Test updates
            update_results = []
            
            # Update color
            result = self.renderer.update_overlay(overlay_id, color='green')
            update_results.append(('color', result))
            time.sleep(0.5)
            
            # Update opacity
            result = self.renderer.update_overlay(overlay_id, opacity=0.5)
            update_results.append(('opacity', result))
            time.sleep(0.5)
            
            # Update position
            result = self.renderer.update_overlay(overlay_id, x=450, y=350)
            update_results.append(('position', result))
            time.sleep(0.5)
            
            # Clean up
            self.renderer.destroy_overlay(overlay_id)
            if overlay_id in self.overlay_ids:
                self.overlay_ids.remove(overlay_id)
            
            successful_updates = [r for r in update_results if r[1]]
            
            return {
                'success': len(successful_updates) >= len(update_results) // 2,  # At least half should work
                'update_results': update_results,
                'successful_updates': len(successful_updates),
                'total_updates': len(update_results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Overlay updates test failed: {e}'
            }
    
    def test_overlay_styles(self) -> Dict[str, Any]:
        """Test different overlay styles."""
        try:
            if not self.renderer:
                self.renderer = create_overlay_renderer()
            
            # Test different styles
            styles = ['recording', 'border', 'highlight']
            style_results = []
            created_overlays = []
            
            for i, style in enumerate(styles):
                overlay_id = self.renderer.create_overlay(
                    x=200 + i * 120, y=250, width=60, height=60,
                    style=style, color='orange', opacity=0.7
                )
                
                if overlay_id:
                    created_overlays.append(overlay_id)
                    self.overlay_ids.append(overlay_id)
                    style_results.append((style, True))
                else:
                    style_results.append((style, False))
            
            # Let them display
            time.sleep(2)
            
            # Clean up
            for overlay_id in created_overlays:
                self.renderer.destroy_overlay(overlay_id)
                if overlay_id in self.overlay_ids:
                    self.overlay_ids.remove(overlay_id)
            
            successful_styles = [r for r in style_results if r[1]]
            
            return {
                'success': len(successful_styles) >= len(styles) // 2,
                'tested_styles': styles,
                'successful_styles': [r[0] for r in successful_styles],
                'failed_styles': [r[0] for r in style_results if not r[1]]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Overlay styles test failed: {e}'
            }
    
    def test_screen_overlay_system(self) -> Dict[str, Any]:
        """Test the higher-level screen overlay system."""
        try:
            platform = PlatformDetector.detect()
            platform.initialize()
            
            # Create screen overlay
            screen_overlay = ScreenOverlay(platform)
            
            # Test configuration
            border_config = BorderConfig(
                show_border=True,
                color="#FF0000",
                width=3,
                opacity=0.8
            )
            
            timer_config = TimerConfig(
                show_timer=True,
                position="top-right",
                font_size=14
            )
            
            # Show recording indicators
            show_result = screen_overlay.show_recording_indicators(
                border_config=border_config,
                timer_config=timer_config
            )
            
            if show_result:
                # Let it display
                time.sleep(2)
                
                # Get status
                status = screen_overlay.get_status()
                
                # Hide indicators
                hide_result = screen_overlay.hide_recording_indicators()
            else:
                status = {}
                hide_result = False
            
            # Clean up
            screen_overlay.cleanup()
            
            return {
                'success': show_result,
                'show_result': show_result,
                'hide_result': hide_result,
                'status': status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Screen overlay system test failed: {e}'
            }
    
    def test_performance(self) -> Dict[str, Any]:
        """Test overlay performance with rapid creation/destruction."""
        try:
            if not self.renderer:
                self.renderer = create_overlay_renderer()
            
            # Performance test parameters
            num_overlays = 10
            iterations = 3
            
            total_create_time = 0
            total_destroy_time = 0
            successful_creates = 0
            successful_destroys = 0
            
            for iteration in range(iterations):
                overlay_batch = []
                
                # Create batch
                create_start = time.time()
                for i in range(num_overlays):
                    overlay_id = self.renderer.create_overlay(
                        x=100 + (i % 5) * 80, y=150 + (i // 5) * 80,
                        width=40, height=40, style='recording'
                    )
                    if overlay_id:
                        overlay_batch.append(overlay_id)
                        successful_creates += 1
                
                create_time = time.time() - create_start
                total_create_time += create_time
                
                # Brief display
                time.sleep(0.5)
                
                # Destroy batch
                destroy_start = time.time()
                for overlay_id in overlay_batch:
                    if self.renderer.destroy_overlay(overlay_id):
                        successful_destroys += 1
                
                destroy_time = time.time() - destroy_start
                total_destroy_time += destroy_time
            
            avg_create_time = total_create_time / iterations
            avg_destroy_time = total_destroy_time / iterations
            
            return {
                'success': successful_creates >= (num_overlays * iterations * 0.8),  # 80% success rate
                'total_overlays_requested': num_overlays * iterations,
                'successful_creates': successful_creates,
                'successful_destroys': successful_destroys,
                'average_create_time': avg_create_time,
                'average_destroy_time': avg_destroy_time,
                'creates_per_second': successful_creates / total_create_time if total_create_time > 0 else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Performance test failed: {e}'
            }
    
    def test_cleanup(self) -> Dict[str, Any]:
        """Test overlay cleanup functionality."""
        try:
            if not self.renderer:
                self.renderer = create_overlay_renderer()
            
            # Create some overlays to clean up
            test_overlays = []
            for i in range(5):
                overlay_id = self.renderer.create_overlay(
                    x=150 + i * 60, y=200, width=40, height=40,
                    style='recording', color='purple'
                )
                if overlay_id:
                    test_overlays.append(overlay_id)
                    self.overlay_ids.append(overlay_id)
            
            time.sleep(1)
            
            # Test cleanup
            cleanup_result = self.renderer.cleanup()
            
            # Clear our tracking list since cleanup should have handled everything
            self.overlay_ids = []
            
            return {
                'success': cleanup_result,
                'cleanup_result': cleanup_result,
                'overlays_created': len(test_overlays)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Cleanup test failed: {e}'
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
                if 'Renderer Creation' in test_name:
                    report['recommendations'].append(
                        "Install tkinter: sudo apt-get install python3-tk (Linux) or ensure GUI support"
                    )
                elif 'Overlay Creation' in test_name:
                    report['recommendations'].append(
                        "Check display access and GUI permissions"
                    )
                elif 'Screen Overlay' in test_name:
                    report['recommendations'].append(
                        "Verify platform initialization and monitor detection"
                    )
        
        return report
    
    def cleanup_remaining_overlays(self):
        """Clean up any remaining overlays."""
        if self.renderer and self.overlay_ids:
            for overlay_id in self.overlay_ids[:]:
                try:
                    self.renderer.destroy_overlay(overlay_id)
                    self.overlay_ids.remove(overlay_id)
                except:
                    pass
            
            # Final cleanup
            try:
                self.renderer.cleanup()
            except:
                pass


def main():
    """Run visual overlay tests."""
    tester = VisualOverlayTester()
    
    try:
        report = tester.run_all_tests()
        
        # Save detailed report
        log_dir = Path(__file__).parent / "logs"
        report_file = log_dir / "visual_overlays_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*60)
        print("🎨 VISUAL OVERLAYS TEST SUMMARY")
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
        
        return report['summary']['success_rate'] >= 75  # 75% pass rate threshold
        
    finally:
        # Always try to clean up
        tester.cleanup_remaining_overlays()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)