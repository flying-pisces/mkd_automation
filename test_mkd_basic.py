#!/usr/bin/env python
"""
Basic test script to verify MKD functionality without GUI
Run this from terminal to test core components
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all core modules can be imported"""
    print("Testing imports...")
    try:
        from mkd.core import config_manager, session_manager, script_manager
        print("[OK] Core modules imported")
        
        from mkd.recording import recording_engine, input_capturer
        print("[OK] Recording modules imported")
        
        from mkd.playback import playback_engine, action_executor
        print("[OK] Playback modules imported")
        
        from mkd.platform import detector
        print("[OK] Platform modules imported")
        
        from mkd.data import script_storage, encryption
        print("[OK] Data modules imported")
        
        return True
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_platform_detection():
    """Test platform detection"""
    print("\nTesting platform detection...")
    try:
        from mkd.platform.detector import PlatformDetector
        detector = PlatformDetector()
        platform = detector.get_platform()
        print(f"[OK] Detected platform: {platform}")
        
        impl = detector.get_implementation()
        print(f"[OK] Platform implementation loaded: {impl.__class__.__name__}")
        return True
    except Exception as e:
        print(f"[FAIL] Platform detection failed: {e}")
        return False

def test_config_manager():
    """Test configuration manager"""
    print("\nTesting configuration manager...")
    try:
        from mkd.core.config_manager import ConfigManager
        config = ConfigManager()
        
        # Test default settings
        recording_settings = config.get_recording_settings()
        print(f"[OK] Recording settings: sample_rate={recording_settings.get('sample_rate', 60)} Hz")
        
        playback_settings = config.get_playback_settings()
        print(f"[OK] Playback settings: speed={playback_settings.get('speed_multiplier', 1.0)}x")
        
        return True
    except Exception as e:
        print(f"[FAIL] Config manager failed: {e}")
        return False

def test_session_manager():
    """Test session manager initialization"""
    print("\nTesting session manager...")
    try:
        from mkd.core.session_manager import SessionManager
        session = SessionManager()
        
        print(f"[OK] Session ID: {session.session_id}")
        print(f"[OK] Session state: {session.get_state()}")
        
        # Test state transitions
        session.start_recording()
        print(f"[OK] Started recording: {session.is_recording()}")
        
        session.stop_recording()
        print(f"[OK] Stopped recording: {not session.is_recording()}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Session manager failed: {e}")
        return False

def test_script_storage():
    """Test script storage functionality"""
    print("\nTesting script storage...")
    try:
        from mkd.data.script_storage import ScriptStorage
        from mkd.data.models import AutomationScript, Action
        import tempfile
        import datetime
        
        storage = ScriptStorage()
        
        # Create a test script
        test_script = AutomationScript(
            name="Test Script",
            description="Test script for verification",
            created_at=datetime.datetime.now(),
            actions=[
                Action(type="mouse_move", data={"x": 100, "y": 100}, timestamp=0.0),
                Action(type="mouse_click", data={"button": "left"}, timestamp=1.0),
                Action(type="keyboard", data={"key": "a", "action": "press"}, timestamp=2.0)
            ]
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.mkd', delete=False) as f:
            temp_path = f.name
        
        storage.save(test_script, temp_path)
        print(f"[OK] Script saved to: {temp_path}")
        
        # Load it back
        loaded_script = storage.load(temp_path)
        print(f"[OK] Script loaded: {loaded_script.name}")
        print(f"[OK] Actions count: {len(loaded_script.actions)}")
        
        # Clean up
        os.unlink(temp_path)
        
        return True
    except Exception as e:
        print(f"[FAIL] Script storage failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recording_engine():
    """Test recording engine initialization"""
    print("\nTesting recording engine...")
    try:
        from mkd.recording.recording_engine import RecordingEngine
        
        engine = RecordingEngine()
        print(f"[OK] Recording engine initialized")
        print(f"[OK] Recording state: {engine.is_recording}")
        
        # Note: We won't actually start recording as it requires GUI interaction
        print("[OK] Recording engine ready (actual recording requires GUI)")
        
        return True
    except Exception as e:
        print(f"[FAIL] Recording engine failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("MKD Automation Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_platform_detection,
        test_config_manager,
        test_session_manager,
        test_script_storage,
        test_recording_engine
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[OK] All basic tests passed!")
    else:
        print("[FAIL] Some tests failed. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)