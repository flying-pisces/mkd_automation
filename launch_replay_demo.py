#!/usr/bin/env python
"""
Simple launcher for MKD Replay System Demo

Quick start script for the replay system demonstration.
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the replay system demo."""
    print("\n" + "=" * 60)
    print("  MKD AUTOMATION REPLAY SYSTEM")
    print("=" * 60)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / "demo_replay_system.py").exists():
        print("\n  [ERROR] Please run from the MKD automation directory")
        print(f"  Current directory: {current_dir}")
        print("  Expected files: demo_replay_system.py, gui_recorder_stopwatch.py")
        return 1
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"\n  [ERROR] Python 3.8+ required (found {sys.version_info.major}.{sys.version_info.minor})")
        return 1
    
    print(f"\n  Python: {sys.version.split()[0]}")
    print(f"  Platform: {sys.platform}")
    print(f"  Directory: {current_dir}")
    
    # Check dependencies
    missing_deps = []
    try:
        import pynput
    except ImportError:
        missing_deps.append("pynput")
    
    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("pillow")
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    if missing_deps:
        print("\n  [WARNING] Missing dependencies:")
        for dep in missing_deps:
            print(f"    - {dep}")
        print("\n  Install with: pip install", " ".join(missing_deps))
        print("  (tkinter is usually included with Python)")
    
    # Launch demo
    print("\n  Launching demo interface...")
    print("\n" + "=" * 60)
    
    try:
        from demo_replay_system import main as demo_main
        return demo_main()
    except ImportError as e:
        print(f"\n  [ERROR] Failed to import demo: {e}")
        print("  Make sure you're in the correct directory")
        return 1
    except Exception as e:
        print(f"\n  [ERROR] Demo failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())