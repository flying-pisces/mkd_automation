#!/usr/bin/env python
"""
Comprehensive Test Suite for Replay System

Tests both Visual Replay and Action Replay functionality.
"""

import sys
import os
import time
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test result tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "errors": [],
    "start_time": None,
    "end_time": None
}


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_test(test_name: str, result: str, message: str = ""):
    """Print test result."""
    symbols = {
        "PASS": "[OK]",
        "FAIL": "[FAIL]",
        "SKIP": "[SKIP]",
        "ERROR": "[ERROR]"
    }
    
    symbol = symbols.get(result, "[?]")
    print(f"  {symbol} {test_name}")
    if message:
        print(f"       {message}")
    
    # Update statistics
    test_results["total"] += 1
    if result == "PASS":
        test_results["passed"] += 1
    elif result == "FAIL":
        test_results["failed"] += 1
        test_results["errors"].append(f"{test_name}: {message}")
    elif result == "SKIP":
        test_results["skipped"] += 1


def test_dependencies() -> bool:
    """Test if required dependencies are installed."""
    print_header("Testing Dependencies")
    
    all_ok = True
    
    # Test pynput
    try:
        import pynput
        print_test("pynput library", "PASS", f"Version: {pynput.__version__ if hasattr(pynput, '__version__') else 'Unknown'}")
    except ImportError as e:
        print_test("pynput library", "FAIL", "Not installed - required for input capture/replay")
        all_ok = False
    
    # Test PIL/Pillow
    try:
        from PIL import Image, ImageDraw, ImageTk
        import PIL
        print_test("PIL/Pillow library", "PASS", f"Version: {PIL.__version__}")
    except ImportError:
        print_test("PIL/Pillow library", "FAIL", "Not installed - required for screenshots")
        all_ok = False
    
    # Test tkinter
    try:
        import tkinter
        print_test("tkinter library", "PASS", "Available")
    except ImportError:
        print_test("tkinter library", "FAIL", "Not installed - required for GUI")
        all_ok = False
    
    # Test msgpack (optional)
    try:
        import msgpack
        print_test("msgpack library", "PASS", f"Version: {msgpack.version}")
    except ImportError:
        print_test("msgpack library", "SKIP", "Optional - using JSON fallback")
    
    return all_ok


def test_replay_modules() -> bool:
    """Test if replay modules can be imported."""
    print_header("Testing Replay Modules")
    
    all_ok = True
    
    # Test visual replay module
    try:
        from mkd.replay.visual_replay import VisualReplayEngine, Annotation, AnnotationType
        engine = VisualReplayEngine()
        print_test("Visual Replay Engine", "PASS", "Module loaded successfully")
    except Exception as e:
        print_test("Visual Replay Engine", "FAIL", str(e))
        all_ok = False
    
    # Test action replay module
    try:
        from mkd.replay.action_replay import ActionReplayEngine, ReplayOptions, SafetyMonitor
        engine = ActionReplayEngine()
        print_test("Action Replay Engine", "PASS", "Module loaded successfully")
    except Exception as e:
        print_test("Action Replay Engine", "FAIL", str(e))
        all_ok = False
    
    # Test replay manager
    try:
        from mkd.replay.replay_manager import ReplayManager, ReplayMode
        manager = ReplayManager()
        print_test("Replay Manager", "PASS", "Module loaded successfully")
    except Exception as e:
        print_test("Replay Manager", "FAIL", str(e))
        all_ok = False
    
    return all_ok


def create_test_recording() -> Path:
    """Create a test recording for replay testing."""
    print_header("Creating Test Recording")
    
    # Create test directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = Path("test_recordings") / f"test_{timestamp}"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test actions
    test_actions = [
        {
            "id": 1,
            "type": "mouse_move",
            "timestamp": 0.0,
            "data": {"x": 100, "y": 100}
        },
        {
            "id": 2,
            "type": "mouse_click",
            "timestamp": 0.5,
            "data": {"x": 200, "y": 200, "button": "left"}
        },
        {
            "id": 3,
            "type": "key_press",
            "timestamp": 1.0,
            "data": {"key": "A"}
        },
        {
            "id": 4,
            "type": "key_press",
            "timestamp": 1.2,
            "data": {"key": "B"}
        },
        {
            "id": 5,
            "type": "mouse_move",
            "timestamp": 1.5,
            "data": {"x": 300, "y": 300}
        },
        {
            "id": 6,
            "type": "mouse_click",
            "timestamp": 2.0,
            "data": {"x": 300, "y": 300, "button": "right"}
        }
    ]
    
    # Save metadata
    metadata = {
        "version": "2.0",
        "duration": 2.5,
        "platform": sys.platform,
        "actions": test_actions,
        "action_count": len(test_actions),
        "screen_resolution": [1920, 1080]
    }
    
    metadata_file = test_dir / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print_test("Test metadata created", "PASS", f"{len(test_actions)} test actions")
    
    # Create dummy screenshots
    try:
        from PIL import Image, ImageDraw
        
        for i in range(6):  # Create 6 frames (3 seconds at 2 FPS)
            img = Image.new('RGB', (1920, 1080), color='white')
            draw = ImageDraw.Draw(img)
            
            # Draw frame number
            draw.text((50, 50), f"Test Frame {i}", fill='black')
            
            # Draw action indicators based on frame
            if i == 1:  # Mouse click at 0.5s
                draw.ellipse([190, 190, 210, 210], fill='red')
            elif i == 2:  # Keyboard at 1.0s
                draw.text((100, 200), "Keyboard: A", fill='blue')
            elif i == 4:  # Mouse click at 2.0s
                draw.ellipse([290, 290, 310, 310], fill='green')
            
            filename = test_dir / f"frame_{i:04d}.png"
            img.save(filename)
        
        print_test("Test screenshots created", "PASS", "6 frames created")
        
    except Exception as e:
        print_test("Test screenshots created", "FAIL", str(e))
    
    # Create dummy .mkd file
    mkd_file = test_dir / "recording.mkd"
    mkd_file.write_text("Dummy MKD content for testing")
    print_test("Test .mkd file created", "PASS", str(mkd_file))
    
    return test_dir


def test_visual_replay(test_dir: Path) -> bool:
    """Test Visual Replay functionality."""
    print_header("Testing Visual Replay")
    
    try:
        from mkd.replay.visual_replay import VisualReplayEngine
        
        engine = VisualReplayEngine()
        
        # Test loading recording
        if engine.load_recording(test_dir):
            print_test("Load recording", "PASS", f"Loaded {len(engine.screenshots)} screenshots")
        else:
            print_test("Load recording", "FAIL", "Failed to load recording")
            return False
        
        # Test annotation generation
        if len(engine.annotations) > 0:
            print_test("Generate annotations", "PASS", f"Created {len(engine.annotations)} annotations")
        else:
            print_test("Generate annotations", "FAIL", "No annotations created")
        
        # Test frame rendering
        try:
            frame = engine.render_frame(0)
            if frame:
                print_test("Render frame", "PASS", "Frame rendered successfully")
            else:
                print_test("Render frame", "FAIL", "Frame is None")
        except Exception as e:
            print_test("Render frame", "FAIL", str(e))
        
        # Test timeline functions
        frame_num = engine.get_frame_at_time(1.0)
        if frame_num == 2:  # 1.0 second at 2 FPS = frame 2
            print_test("Timeline calculation", "PASS", f"Correct frame for timestamp")
        else:
            print_test("Timeline calculation", "FAIL", f"Expected frame 2, got {frame_num}")
        
        return True
        
    except Exception as e:
        print_test("Visual Replay", "ERROR", str(e))
        return False


def test_action_replay(test_dir: Path) -> bool:
    """Test Action Replay functionality."""
    print_header("Testing Action Replay")
    
    try:
        from mkd.replay.action_replay import ActionReplayEngine, ReplayOptions, ActionExecutor
        
        engine = ActionReplayEngine()
        
        # Test loading recording
        if engine.load_recording(test_dir):
            print_test("Load recording", "PASS", f"Loaded {len(engine.actions)} actions")
        else:
            print_test("Load recording", "FAIL", "Failed to load recording")
            return False
        
        # Test executor initialization
        executor = ActionExecutor()
        print_test("Action Executor", "PASS", "Initialized successfully")
        
        # Test dry run execution
        test_action = {
            "type": "mouse_click",
            "data": {"x": 100, "y": 100, "button": "left"}
        }
        
        if executor.execute_action(test_action, dry_run=True):
            print_test("Dry run execution", "PASS", "Test action executed in dry run")
        else:
            print_test("Dry run execution", "FAIL", "Failed to execute test action")
        
        # Test replay options
        options = ReplayOptions(
            playback_speed=2.0,
            dry_run=True,
            confirm_start=False
        )
        print_test("Replay Options", "PASS", f"Speed: {options.playback_speed}x, Dry run: {options.dry_run}")
        
        # Test safety monitor
        from mkd.replay.action_replay import SafetyMonitor
        monitor = SafetyMonitor()
        monitor.activate("esc", max_duration=10.0)
        
        if monitor.check_safety():
            print_test("Safety Monitor", "PASS", "Safety check passed")
        else:
            print_test("Safety Monitor", "FAIL", "Safety check failed")
        
        monitor.deactivate()
        
        return True
        
    except Exception as e:
        print_test("Action Replay", "ERROR", str(e))
        return False


def test_replay_manager(test_dir: Path) -> bool:
    """Test Replay Manager functionality."""
    print_header("Testing Replay Manager")
    
    try:
        from mkd.replay.replay_manager import ReplayManager, ReplayMode
        
        manager = ReplayManager()
        
        # Test loading recording
        if manager.load_recording(test_dir):
            print_test("Load recording", "PASS", "Recording loaded into manager")
        else:
            print_test("Load recording", "FAIL", "Failed to load recording")
            return False
        
        # Test getting recording info
        info = manager.get_recording_info()
        if info.get("screenshot_count", 0) > 0:
            print_test("Recording info", "PASS", 
                      f"Screenshots: {info['screenshot_count']}, Actions: {info.get('action_count', 0)}")
        else:
            print_test("Recording info", "FAIL", "No recording info retrieved")
        
        # Test replay mode enum
        modes = [ReplayMode.VISUAL, ReplayMode.ACTION]
        print_test("Replay modes", "PASS", f"Available modes: {[m.value for m in modes]}")
        
        return True
        
    except Exception as e:
        print_test("Replay Manager", "ERROR", str(e))
        return False


def test_integration() -> bool:
    """Test end-to-end integration."""
    print_header("Testing Integration")
    
    try:
        # Test full workflow
        from mkd.core.session_manager import SessionManager
        from mkd.data.models import Action
        
        # Create a new session
        session_mgr = SessionManager()
        session_id = session_mgr.start_recording()
        
        # Add test actions
        test_actions = [
            Action("mouse_move", {"x": 50, "y": 50}, 0.0),
            Action("mouse_click", {"x": 100, "y": 100, "button": "left"}, 0.5),
            Action("key_press", {"key": "T"}, 1.0),
            Action("key_press", {"key": "E"}, 1.1),
            Action("key_press", {"key": "S"}, 1.2),
            Action("key_press", {"key": "T"}, 1.3),
        ]
        
        for action in test_actions:
            session_mgr.add_action(action)
        
        # Stop recording
        completed = session_mgr.stop_recording()
        
        if completed and len(completed.actions) == len(test_actions):
            print_test("Session recording", "PASS", f"Recorded {len(completed.actions)} actions")
        else:
            print_test("Session recording", "FAIL", "Session recording failed")
            return False
        
        # Test script conversion
        script = completed.to_script("Test Script", "Integration test script")
        if script:
            print_test("Script conversion", "PASS", "Session converted to script")
        else:
            print_test("Script conversion", "FAIL", "Failed to convert to script")
        
        return True
        
    except Exception as e:
        print_test("Integration", "ERROR", str(e))
        return False


def cleanup_test_recordings():
    """Clean up test recordings."""
    print_header("Cleanup")
    
    test_dir = Path("test_recordings")
    if test_dir.exists():
        try:
            shutil.rmtree(test_dir)
            print_test("Cleanup test recordings", "PASS", "Test recordings removed")
        except Exception as e:
            print_test("Cleanup test recordings", "FAIL", str(e))
    else:
        print_test("Cleanup test recordings", "SKIP", "No test recordings to clean")


def generate_report():
    """Generate test report."""
    print_header("Test Report")
    
    duration = test_results["end_time"] - test_results["start_time"]
    
    print(f"\n  Total Tests: {test_results['total']}")
    print(f"  Passed: {test_results['passed']} ({test_results['passed']/test_results['total']*100:.1f}%)")
    print(f"  Failed: {test_results['failed']}")
    print(f"  Skipped: {test_results['skipped']}")
    print(f"  Duration: {duration:.2f} seconds")
    
    if test_results["failed"] > 0:
        print("\n  Failed Tests:")
        for error in test_results["errors"]:
            print(f"    - {error}")
    
    # Generate report file
    report_file = Path("test_report_replay.txt")
    with open(report_file, 'w') as f:
        f.write("MKD AUTOMATION - REPLAY SYSTEM TEST REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Platform: {sys.platform}\n")
        f.write(f"Python Version: {sys.version.split()[0]}\n\n")
        
        f.write("TEST RESULTS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total Tests: {test_results['total']}\n")
        f.write(f"Passed: {test_results['passed']} ({test_results['passed']/test_results['total']*100:.1f}%)\n")
        f.write(f"Failed: {test_results['failed']}\n")
        f.write(f"Skipped: {test_results['skipped']}\n")
        f.write(f"Duration: {duration:.2f} seconds\n\n")
        
        if test_results["failed"] > 0:
            f.write("FAILED TESTS\n")
            f.write("-" * 40 + "\n")
            for error in test_results["errors"]:
                f.write(f"- {error}\n")
            f.write("\n")
        
        # Add recommendations
        f.write("RECOMMENDATIONS\n")
        f.write("-" * 40 + "\n")
        
        if test_results["passed"] == test_results["total"]:
            f.write("[OK] All tests passed! System is ready for use.\n")
            f.write("[OK] Both Visual and Action Replay modes are functional.\n")
            f.write("[OK] Safety systems are operational.\n")
        else:
            f.write("[WARNING] Some tests failed. Please review the errors above.\n")
            f.write("[WARNING] Ensure all dependencies are installed: pip install pynput pillow\n")
            f.write("[WARNING] Check that the src/mkd directory is in the Python path.\n")
    
    print(f"\n  Report saved to: {report_file}")
    
    return test_results["passed"] == test_results["total"]


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  MKD AUTOMATION - REPLAY SYSTEM TEST SUITE")
    print("=" * 60)
    
    test_results["start_time"] = time.time()
    
    # Run tests
    all_passed = True
    
    if not test_dependencies():
        print("\n  [WARNING] Some dependencies are missing")
        all_passed = False
    
    if not test_replay_modules():
        print("\n  [WARNING] Some modules failed to load")
        all_passed = False
    
    # Create test recording
    test_dir = create_test_recording()
    
    # Run replay tests
    if not test_visual_replay(test_dir):
        all_passed = False
    
    if not test_action_replay(test_dir):
        all_passed = False
    
    if not test_replay_manager(test_dir):
        all_passed = False
    
    if not test_integration():
        all_passed = False
    
    # Cleanup
    cleanup_test_recordings()
    
    test_results["end_time"] = time.time()
    
    # Generate report
    report_passed = generate_report()
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed and report_passed:
        print("  [OK] ALL TESTS PASSED - SYSTEM READY")
    else:
        print("  [WARNING] SOME TESTS FAILED - REVIEW REPORT")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())