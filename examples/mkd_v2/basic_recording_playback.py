#!/usr/bin/env python3
"""
Basic Recording and Playback Example

This example demonstrates the fundamental MKD v2.0 workflow:
1. Initialize the system
2. Record user actions
3. Play back the recorded actions
4. Handle errors gracefully
"""

import asyncio
import logging
from pathlib import Path

from mkd_v2.integration import SystemController
from mkd_v2.playback import ExecutionConfig
from mkd_v2.exceptions import RecordingError, PlaybackError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def basic_recording_playback():
    """
    Basic example of recording user actions and playing them back.
    """
    controller = None
    
    try:
        # Initialize the system
        logger.info("🚀 Initializing MKD v2.0 System...")
        controller = SystemController()
        await controller.initialize()
        
        # Check system status
        status = controller.get_system_status()
        logger.info(f"System Status: {status['status']}")
        
        # Wait for user to get ready
        print("\n" + "="*50)
        print("📹 RECORDING MODE")
        print("="*50)
        print("The system will start recording your actions in 5 seconds.")
        print("Perform some simple actions like:")
        print("  • Click somewhere on screen")
        print("  • Type some text")
        print("  • Press some keys")
        print("Recording will stop automatically after 15 seconds.")
        print("="*50)
        
        for i in range(5, 0, -1):
            print(f"Starting recording in {i}...")
            await asyncio.sleep(1)
        
        # Start recording
        logger.info("🔴 Recording started - perform your actions now!")
        await controller.start_recording()
        
        # Record for 15 seconds
        recording_duration = 15
        for remaining in range(recording_duration, 0, -1):
            if remaining <= 3:
                print(f"⏱️  Recording stops in {remaining}...")
            await asyncio.sleep(1)
        
        # Stop recording and get actions
        actions = await controller.stop_recording()
        logger.info(f"✅ Recording completed! Captured {len(actions)} actions")
        
        if not actions:
            print("❌ No actions were recorded. Please try again.")
            return
        
        # Display recorded actions
        print("\n" + "="*50)
        print("📋 RECORDED ACTIONS")
        print("="*50)
        for i, action in enumerate(actions, 1):
            if hasattr(action, 'coordinates') and action.coordinates:
                print(f"{i:2d}. {action.action_type.value} at ({action.coordinates[0]}, {action.coordinates[1]})")
            elif hasattr(action, 'text') and action.text:
                print(f"{i:2d}. {action.action_type.value}: '{action.text[:30]}{'...' if len(action.text) > 30 else ''}'")
            elif hasattr(action, 'key') and action.key:
                print(f"{i:2d}. {action.action_type.value}: {action.key}")
            else:
                print(f"{i:2d}. {action.action_type.value}")
        print("="*50)
        
        # Ask user if they want to play back
        print("\n🎬 Ready to play back the recorded actions!")
        print("This will repeat your actions exactly as recorded.")
        
        # Wait before playback
        print("Starting playback in 5 seconds...")
        for i in range(5, 0, -1):
            print(f"Playback starts in {i}...")
            await asyncio.sleep(1)
        
        # Configure execution
        config = ExecutionConfig(
            speed_multiplier=1.0,  # Normal speed
            fail_on_error=False,   # Continue on errors
            screenshot_on_error=True,  # Take screenshots on errors
            max_retry_attempts=2,  # Retry failed actions once
        )
        
        # Execute the recorded actions
        logger.info("▶️  Playing back actions...")
        result = await controller.execute_actions(actions, config=config)
        
        # Report results
        if result.success:
            logger.info(f"✅ Playback completed successfully!")
            logger.info(f"   • Total actions: {len(actions)}")
            logger.info(f"   • Successful: {result.successful_actions}")
            logger.info(f"   • Duration: {result.duration:.2f} seconds")
        else:
            logger.warning(f"⚠️  Playback completed with errors:")
            logger.warning(f"   • Total actions: {len(actions)}")
            logger.warning(f"   • Successful: {result.successful_actions}")
            logger.warning(f"   • Failed: {result.failed_actions}")
            logger.warning(f"   • Error: {result.error}")
        
        # Save actions to file for later use
        actions_file = Path("recorded_actions.json")
        controller.save_actions_to_file(actions, actions_file)
        logger.info(f"💾 Actions saved to: {actions_file.absolute()}")
        
        print("\n" + "="*50)
        print("🎉 Example completed successfully!")
        print("="*50)
        print("You can now:")
        print(f"  • Replay the actions: python -c \"from mkd_v2.integration import SystemController; import asyncio; controller = SystemController(); asyncio.run(controller.load_and_execute_actions('{actions_file}'))\"")
        print("  • Modify the recorded actions programmatically")
        print("  • Use the actions as a template for other automations")
        print("="*50)
        
    except RecordingError as e:
        logger.error(f"❌ Recording failed: {e}")
        print("\nTroubleshooting tips:")
        print("  • Make sure you have the necessary permissions")
        print("  • Try running the script with elevated privileges")
        print("  • Check that your input devices are working properly")
        
    except PlaybackError as e:
        logger.error(f"❌ Playback failed: {e}")
        print("\nTroubleshooting tips:")
        print("  • Screen layout might have changed since recording")
        print("  • Applications might not be in the same state")
        print("  • Try recording and playing back immediately")
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Always clean up
        if controller:
            logger.info("🧹 Cleaning up system resources...")
            await controller.shutdown()
            logger.info("✅ System shutdown complete")


async def demonstrate_error_handling():
    """
    Demonstrates comprehensive error handling in MKD v2.0.
    """
    controller = SystemController()
    
    try:
        await controller.initialize()
        
        # This will likely fail because we're not providing proper user input
        print("Testing error handling with empty recording...")
        
        await controller.start_recording()
        await asyncio.sleep(1)  # Very short recording
        actions = await controller.stop_recording()
        
        if not actions:
            print("✅ Handled empty recording gracefully")
        
        # Test execution with no actions
        result = await controller.execute_actions([])
        print(f"✅ Handled empty action list: success={result.success}")
        
    except Exception as e:
        print(f"Error handling test: {e}")
    finally:
        await controller.shutdown()


def main():
    """Main entry point"""
    print("MKD Automation Platform v2.0 - Basic Recording & Playback Example")
    print("=" * 70)
    
    # Run the basic example
    asyncio.run(basic_recording_playback())
    
    print("\n" + "=" * 70)
    print("Testing error handling...")
    asyncio.run(demonstrate_error_handling())


if __name__ == "__main__":
    main()