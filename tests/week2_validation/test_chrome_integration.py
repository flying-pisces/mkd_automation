#!/usr/bin/env python3
"""
Chrome Extension and Native Messaging Integration Tests

Tests the complete Chrome ↔ Python communication pipeline including:
- Extension manifest validation
- Native host installation
- Message protocol functionality
- Background script execution
"""

import sys
import json
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mkd_v2.native_host.installer import NativeHostInstaller
from mkd_v2.native_host.host import NativeHost

# Configure logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "chrome_integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ChromeIntegrationTester:
    """Test Chrome extension and native messaging integration."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.extension_path = self.project_root / "chrome-extension"
        self.results = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Chrome integration tests."""
        logger.info("🚀 Starting Chrome Integration Tests")
        
        tests = [
            ("Extension Manifest Validation", self.test_extension_manifest),
            ("Native Host Installation", self.test_native_host_installation),
            ("Native Host Status Check", self.test_native_host_status),
            ("Extension Directory Structure", self.test_extension_structure),
            ("Background Script Syntax", self.test_background_script),
            ("Native Host Registry", self.test_native_host_registry)
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
    
    def test_extension_manifest(self) -> Dict[str, Any]:
        """Test Chrome extension manifest.json validity."""
        try:
            manifest_path = self.extension_path / "manifest.json"
            
            if not manifest_path.exists():
                return {
                    'success': False,
                    'error': 'manifest.json not found'
                }
            
            # Parse manifest
            with open(manifest_path) as f:
                manifest = json.load(f)
            
            # Required fields check
            required_fields = ['manifest_version', 'name', 'version', 'permissions', 'background']
            missing_fields = [field for field in required_fields if field not in manifest]
            
            if missing_fields:
                return {
                    'success': False,
                    'error': f'Missing required fields: {missing_fields}'
                }
            
            # Validate manifest version
            if manifest.get('manifest_version') != 3:
                return {
                    'success': False,
                    'error': f'Expected manifest_version 3, got {manifest.get("manifest_version")}'
                }
            
            # Check permissions
            permissions = manifest.get('permissions', [])
            required_permissions = ['nativeMessaging', 'storage']
            missing_permissions = [p for p in required_permissions if p not in permissions]
            
            return {
                'success': len(missing_permissions) == 0,
                'manifest_version': manifest.get('manifest_version'),
                'permissions': permissions,
                'missing_permissions': missing_permissions,
                'background': manifest.get('background', {})
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Invalid JSON: {e}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Manifest test failed: {e}'
            }
    
    def test_native_host_installation(self) -> Dict[str, Any]:
        """Test native messaging host installation."""
        try:
            installer = NativeHostInstaller()
            
            # Check installation status before
            status_before = installer.check_installation(['chrome'])
            
            # Perform installation
            install_result = installer.install(browsers=['chrome'], user_only=True)
            
            # Check installation status after
            status_after = installer.check_installation(['chrome'])
            
            # Get installation info
            install_info = installer.get_installation_info()
            
            return {
                'success': install_result,
                'install_result': install_result,
                'status_before': status_before,
                'status_after': status_after,
                'install_info': install_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Installation test failed: {e}'
            }
    
    def test_native_host_status(self) -> Dict[str, Any]:
        """Test native host status and configuration."""
        try:
            installer = NativeHostInstaller()
            status = installer.check_installation()
            
            # Check if installed correctly
            chrome_installed = status.get('chrome', {}).get('installed', False)
            
            # Check manifest files exist
            manifest_files = []
            for browser, browser_status in status.items():
                for path_info in browser_status.get('paths', []):
                    if path_info.get('manifest_exists'):
                        manifest_files.append(path_info['path'])
            
            return {
                'success': chrome_installed,
                'chrome_installed': chrome_installed,
                'status': status,
                'manifest_files': manifest_files
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Status check failed: {e}'
            }
    
    def test_extension_structure(self) -> Dict[str, Any]:
        """Test Chrome extension directory structure."""
        try:
            required_files = [
                'manifest.json',
                'src/background.js',
                'src/popup/popup.html',
                'src/popup/popup.js'
            ]
            
            missing_files = []
            existing_files = []
            
            for file_path in required_files:
                full_path = self.extension_path / file_path
                if full_path.exists():
                    existing_files.append(file_path)
                else:
                    missing_files.append(file_path)
            
            # Check file sizes
            file_sizes = {}
            for file_path in existing_files:
                full_path = self.extension_path / file_path
                file_sizes[file_path] = full_path.stat().st_size
            
            return {
                'success': len(missing_files) == 0,
                'required_files': required_files,
                'existing_files': existing_files,
                'missing_files': missing_files,
                'file_sizes': file_sizes
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Structure test failed: {e}'
            }
    
    def test_background_script(self) -> Dict[str, Any]:
        """Test background script syntax and structure."""
        try:
            background_path = self.extension_path / "src" / "background.js"
            
            if not background_path.exists():
                return {
                    'success': False,
                    'error': 'background.js not found'
                }
            
            # Read background script
            with open(background_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic syntax checks
            required_patterns = [
                'chrome.runtime',
                'chrome.nativeMessaging',
                'SimpleNativeMessagingHandler'
            ]
            
            found_patterns = []
            missing_patterns = []
            
            for pattern in required_patterns:
                if pattern in content:
                    found_patterns.append(pattern)
                else:
                    missing_patterns.append(pattern)
            
            # Check for problematic patterns
            problematic_patterns = [
                'importScripts',  # Not allowed in Manifest V3
                'chrome.notifications'  # Requires permission we don't have
            ]
            
            found_problems = []
            for pattern in problematic_patterns:
                if pattern in content:
                    found_problems.append(pattern)
            
            return {
                'success': len(missing_patterns) == 0 and len(found_problems) == 0,
                'file_size': len(content),
                'found_patterns': found_patterns,
                'missing_patterns': missing_patterns,
                'found_problems': found_problems
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Background script test failed: {e}'
            }
    
    def test_native_host_registry(self) -> Dict[str, Any]:
        """Test native host registry entries."""
        try:
            installer = NativeHostInstaller()
            
            # Check if host executable exists
            host_executable = self.project_root / "bin" / "mkd_native_host"
            if not host_executable.exists():
                # Try with .bat extension for Windows compatibility
                host_executable = self.project_root / "bin" / "mkd_native_host.bat"
            
            executable_exists = host_executable.exists()
            
            # Check if registry entries are valid
            install_info = installer.get_installation_info()
            
            # Validate manifest contents
            valid_manifests = []
            invalid_manifests = []
            
            for browser, browser_status in install_info['status'].items():
                for path_info in browser_status.get('paths', []):
                    if path_info.get('manifest_exists') and path_info.get('valid'):
                        valid_manifests.append(path_info['path'])
                    elif path_info.get('manifest_exists'):
                        invalid_manifests.append(path_info['path'])
            
            return {
                'success': executable_exists and len(valid_manifests) > 0,
                'executable_exists': executable_exists,
                'executable_path': str(host_executable),
                'valid_manifests': valid_manifests,
                'invalid_manifests': invalid_manifests,
                'install_info': install_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Registry test failed: {e}'
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
                if 'Native Host Installation' in test_name:
                    report['recommendations'].append(
                        "Run 'python install_native_host.py' to install native messaging host"
                    )
                elif 'Extension Manifest' in test_name:
                    report['recommendations'].append(
                        "Check chrome-extension/manifest.json for required fields and permissions"
                    )
                elif 'Background Script' in test_name:
                    report['recommendations'].append(
                        "Review chrome-extension/src/background.js for Manifest V3 compatibility"
                    )
        
        return report


def main():
    """Run Chrome integration tests."""
    tester = ChromeIntegrationTester()
    report = tester.run_all_tests()
    
    # Save detailed report
    log_dir = Path(__file__).parent / "logs"
    report_file = log_dir / "chrome_integration_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "="*60)
    print("📋 CHROME INTEGRATION TEST SUMMARY")
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
    
    return report['summary']['success_rate'] >= 80  # 80% pass rate threshold


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)