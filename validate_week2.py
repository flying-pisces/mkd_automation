#!/usr/bin/env python3
"""
Week 2 Validation Entry Point

Quick validation script for MKD Automation Platform v2.0 Week 2 features.
This is the main entry point for validating all Week 2 implementations.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Run Week 2 validation."""
    print("🚀 MKD Automation Platform v2.0 - Week 2 Validation")
    print("=" * 60)
    
    # Path to test runner
    test_runner = Path(__file__).parent / "tests" / "week2_validation" / "run_all_tests.py"
    
    if not test_runner.exists():
        print("❌ Test runner not found!")
        print(f"Expected: {test_runner}")
        return 1
    
    print("🔍 Running comprehensive Week 2 validation tests...")
    print("📋 This will test:")
    print("  • Chrome Extension & Native Messaging")
    print("  • Real Input Capture (pynput)")
    print("  • Visual Overlay Rendering")
    print("  • UI Automation & Element Detection")
    print("  • Playback Engine Foundation")
    print()
    
    # Run the test suite
    try:
        # Forward command line arguments to test runner
        cmd = [sys.executable, str(test_runner)] + sys.argv[1:]
        result = subprocess.run(cmd)
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⚡ Validation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n🚨 Validation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())