#!/usr/bin/env python3
"""
Week 2 Features Demonstration

Quick demo script showcasing key Week 2 MKD Automation Platform features.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def demo_chrome_integration():
    """Demo Chrome extension and native messaging."""
    print("📋 Chrome Extension & Native Messaging Demo")
    print("-" * 45)
    
    try:
        from mkd_v2.native_host.installer import NativeHostInstaller
        
        installer = NativeHostInstaller()
        status = installer.check_installation()
        
        print("Chrome Integration Status:")
        for browser, browser_status in status.items():
            if browser_status.get('installed'):
                print(f"  ✅ {browser.title()}: Installed and configured")
            else:
                print(f"  ❌ {browser.title()}: Not installed")
        
        print(f"  📄 Install info: {installer.get_installation_info()['host_name']}")
        print("  💡 To install: python install_native_host.py")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()


def demo_input_capture():
    """Demo real input capture with pynput."""
    print("🖱️  Real Input Capture Demo")
    print("-" * 30)
    
    try:
        from mkd_v2.platform.detector import PlatformDetector
        
        platform = PlatformDetector.detect()
        init_result = platform.initialize()
        
        print(f"Platform: {platform.name} v{getattr(platform, 'version', 'unknown')}")
        print(f"Initialization: {'✅ Success' if init_result.get('success') else '❌ Failed'}")
        
        capabilities = platform.get_capabilities()
        if capabilities.get('real_input_capture'):
            print("  ✅ Real input capture available (pynput)")
        else:
            print("  ❌ Real input capture not available")
        
        # Quick capture test
        captured_events = []
        def event_callback(event):
            captured_events.append(event)
        
        if platform.start_input_capture(event_callback):
            print("  🎯 Input capture started... (generating test events)")
            
            # Generate some test input
            from mkd_v2.platform.base import MouseAction, KeyboardAction
            platform.execute_mouse_action(MouseAction(action="move", x=500, y=400))
            time.sleep(0.2)
            platform.execute_keyboard_action(KeyboardAction(action="type", text="test"))
            time.sleep(0.3)
            
            platform.stop_input_capture()
            print(f"  📊 Captured {len(captured_events)} events")
        else:
            print("  ⚠️  Input capture failed (permissions needed)")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()


def demo_visual_overlays():
    """Demo visual overlay rendering."""
    print("🎨 Visual Overlay Rendering Demo")
    print("-" * 35)
    
    try:
        from mkd_v2.ui.overlay_renderer import create_overlay_renderer
        
        renderer = create_overlay_renderer()
        print(f"Renderer: {type(renderer).__name__}")
        
        # Create a demo overlay
        overlay_id = renderer.create_overlay(
            x=300, y=200, width=100, height=100,
            style="recording", color="red", opacity=0.8
        )
        
        if overlay_id:
            print(f"  ✅ Created overlay: {overlay_id}")
            print("  🎯 Overlay should be visible as red recording indicator")
            
            time.sleep(2)  # Display time
            
            # Update overlay
            success = renderer.update_overlay(overlay_id, color="green")
            print(f"  🔄 Updated color: {'✅ Success' if success else '❌ Failed'}")
            
            time.sleep(1)
            
            # Clean up
            success = renderer.destroy_overlay(overlay_id)
            print(f"  🗑️  Cleaned up: {'✅ Success' if success else '❌ Failed'}")
        else:
            print("  ❌ Failed to create overlay")
        
        renderer.cleanup()
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()


def demo_ui_automation():
    """Demo UI automation and element detection."""
    print("🤖 UI Automation & Element Detection Demo")
    print("-" * 45)
    
    try:
        from mkd_v2.automation import AutomationEngine
        from mkd_v2.platform.detector import PlatformDetector
        
        platform = PlatformDetector.detect()
        platform.initialize()
        automation = AutomationEngine(platform)
        
        status = automation.get_automation_status()
        print(f"Platform: {status['platform']}")
        
        # Window management demo
        windows = automation.window_manager.get_window_list()
        print(f"  📱 Found {len(windows)} windows")
        
        active_window = automation.window_manager.get_active_window()
        if active_window:
            print(f"  🎯 Active: {active_window.title}")
        
        # Element detection demo
        elements = automation.get_elements_in_region(400, 300, 200, 200)
        print(f"  🔍 Detected {len(elements)} UI elements in test region")
        
        # Safe automation test
        success = automation.click_at_coordinates(600, 400)
        print(f"  👆 Test click: {'✅ Success' if success else '❌ Failed'}")
        
        success = automation.type_text("demo")
        print(f"  ⌨️  Test typing: {'✅ Success' if success else '❌ Failed'}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()


def demo_playback_engine():
    """Demo playback engine functionality."""
    print("⏯️  Playback Engine Demo")
    print("-" * 25)
    
    try:
        from mkd_v2.playback import PlaybackEngine, SequenceValidator, ActionExecutor
        from mkd_v2.automation import AutomationEngine
        from mkd_v2.platform.detector import PlatformDetector
        
        platform = PlatformDetector.detect()
        platform.initialize()
        automation = AutomationEngine(platform)
        
        # Sequence validation demo
        validator = SequenceValidator(automation)
        test_sequence = [
            {'type': 'delay', 'duration': 0.1},
            {'type': 'mouse_move', 'x': 500, 'y': 400},
            {'type': 'type_text', 'text': 'hello'}
        ]
        
        validation = validator.validate_sequence(test_sequence)
        print(f"Sequence Validation: {'✅ Valid' if validation.is_valid else '❌ Invalid'}")
        if validation.issues:
            print(f"  ⚠️  Issues: {len(validation.issues)}")
        
        # Action execution demo
        executor = ActionExecutor(platform, automation)
        test_action = {'type': 'delay', 'duration': 0.1}
        result = executor.execute_action(test_action)
        print(f"Action Execution: {'✅ Success' if result.success else '❌ Failed'}")
        print(f"  ⏱️  Time: {result.execution_time:.3f}s")
        
        # Playback engine demo
        playback = PlaybackEngine(platform, automation)
        status = playback.get_playback_status()
        print(f"Engine Status: {status['status']}")
        
        # Speed control demo
        speed_set = playback.set_speed(2.0)
        print(f"Speed Control: {'✅ 2x speed set' if speed_set else '❌ Failed'}")
        playback.set_speed(1.0)  # Reset
        
        stats = executor.get_execution_stats()
        print(f"  📊 Executed {stats['total_actions']} actions, {stats['success_rate']:.1f}% success")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()


def main():
    """Run all feature demonstrations."""
    print("🚀 MKD Automation Platform v2.0 - Week 2 Features Demo")
    print("=" * 60)
    print("This demo showcases the key Week 2 features that have been implemented.")
    print("Some features may require system permissions or dependencies.")
    print()
    
    demos = [
        demo_chrome_integration,
        demo_input_capture,
        demo_visual_overlays,
        demo_ui_automation,
        demo_playback_engine
    ]
    
    for demo in demos:
        try:
            demo()
        except KeyboardInterrupt:
            print("Demo interrupted by user")
            break
        except Exception as e:
            print(f"Demo failed: {e}\n")
    
    print("🎉 Week 2 Features Demo Complete!")
    print("💡 To run full validation: python validate_week2.py")


if __name__ == "__main__":
    main()