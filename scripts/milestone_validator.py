#!/usr/bin/env python
"""
Milestone Validator
Validates completion of weekly milestones for Chrome extension development
"""

import sys
import os
import subprocess
from pathlib import Path
import argparse

class MilestoneValidator:
    """Validates development milestones."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests" / "milestones"
        
    def validate_week_1(self):
        """Validate Week 1: Security & Store Compliance milestones."""
        print("🔒 Validating Week 1: Security & Store Compliance")
        print("=" * 60)
        
        tests = [
            ("Security Audit", "test_security_audit.py"),
            ("Icon Validation", "validate_icons.py"),
            ("CSP Validation", "validate_csp.py"),
            ("Privacy Policy", "test_privacy_policy.py"),
            ("Store Compliance", "test_store_compliance.py")
        ]
        
        results = []
        for test_name, test_file in tests:
            print(f"\n📋 Running: {test_name}")
            success = self._run_test(test_file)
            results.append((test_name, success))
            
            if success:
                print(f"  ✅ {test_name}: PASSED")
            else:
                print(f"  ❌ {test_name}: FAILED")
        
        return self._generate_weekly_report("Week 1", results)
    
    def validate_week_2(self):
        """Validate Week 2: Integration & Cross-Platform milestones."""
        print("🔗 Validating Week 2: Integration & Cross-Platform")
        print("=" * 60)
        
        tests = [
            ("Windows Native Host", "test_native_host_windows.py"),
            ("Registry Integration", "test_registry_integration.py"),
            ("Message Protocol", "test_message_protocol.py"),
            ("Recording Integration", "test_recording_integration.py"),
            ("Content Script", "test_content_script.py")
        ]
        
        results = []
        for test_name, test_file in tests:
            print(f"\n📋 Running: {test_name}")
            success = self._run_test(test_file)
            results.append((test_name, success))
            
            if success:
                print(f"  ✅ {test_name}: PASSED")
            else:
                print(f"  ❌ {test_name}: FAILED")
        
        return self._generate_weekly_report("Week 2", results)
    
    def validate_week_3(self):
        """Validate Week 3: Testing, Polish & Deployment milestones."""
        print("🚀 Validating Week 3: Testing, Polish & Deployment")
        print("=" * 60)
        
        tests = [
            ("E2E Test Suite", "run_e2e_tests.py"),
            ("Cross Browser", "test_cross_browser.py"),
            ("Performance", "test_performance.py"),
            ("User Experience", "test_user_experience.py"),
            ("Production Build", "test_production_build.py"),
            ("Final Security Audit", "run_security_audit.py")
        ]
        
        results = []
        for test_name, test_file in tests:
            print(f"\n📋 Running: {test_name}")
            success = self._run_test(test_file)
            results.append((test_name, success))
            
            if success:
                print(f"  ✅ {test_name}: PASSED")
            else:
                print(f"  ❌ {test_name}: FAILED")
        
        return self._generate_weekly_report("Week 3", results)
    
    def validate_all(self):
        """Validate all milestones across all weeks."""
        print("🎯 Validating All Milestones")
        print("=" * 60)
        
        week1_success = self.validate_week_1()
        print("\n" + "-" * 40)
        week2_success = self.validate_week_2()
        print("\n" + "-" * 40)
        week3_success = self.validate_week_3()
        
        overall_success = week1_success and week2_success and week3_success
        
        print("\n" + "=" * 60)
        print("📊 OVERALL VALIDATION RESULTS")
        print("=" * 60)
        
        if overall_success:
            print("🎉 ALL MILESTONES COMPLETED!")
            print("   Extension is ready for Chrome Web Store submission")
            return True
        else:
            print("⚠️  MILESTONES INCOMPLETE")
            print("   Complete failed milestones before store submission")
            return False
    
    def _run_test(self, test_file):
        """Run a single test file."""
        test_path = self.tests_dir / test_file
        
        if not test_path.exists():
            print(f"  ⚠️  Test file not found: {test_file}")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_path)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True
            else:
                print(f"  ❌ Test failed with exit code {result.returncode}")
                if result.stdout:
                    print("     STDOUT:", result.stdout[-200:])  # Last 200 chars
                if result.stderr:
                    print("     STDERR:", result.stderr[-200:])
                return False
                
        except subprocess.TimeoutExpired:
            print(f"  ❌ Test timed out after 30 seconds")
            return False
        except Exception as e:
            print(f"  ❌ Test execution error: {e}")
            return False
    
    def _generate_weekly_report(self, week_name, results):
        """Generate weekly validation report."""
        passed = sum(1 for _, success in results if success)
        total = len(results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"\n📈 {week_name} Summary:")
        print(f"   Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if passed == total:
            print(f"   🎯 {week_name} COMPLETE - All milestones achieved")
            return True
        else:
            print(f"   ⏳ {week_name} IN PROGRESS - {total - passed} milestones remaining")
            
            # Show failed tests
            failed_tests = [name for name, success in results if not success]
            if failed_tests:
                print("   Failed Tests:")
                for test_name in failed_tests:
                    print(f"     - {test_name}")
            
            return False

def main():
    """Main validation entry point."""
    parser = argparse.ArgumentParser(description="Validate Chrome extension development milestones")
    parser.add_argument("--week", type=int, choices=[1, 2, 3], help="Validate specific week")
    parser.add_argument("--all", action="store_true", help="Validate all weeks")
    
    args = parser.parse_args()
    
    validator = MilestoneValidator()
    
    if args.week == 1:
        success = validator.validate_week_1()
    elif args.week == 2:
        success = validator.validate_week_2()
    elif args.week == 3:
        success = validator.validate_week_3()
    elif args.all:
        success = validator.validate_all()
    else:
        print("Please specify --week 1|2|3 or --all")
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())