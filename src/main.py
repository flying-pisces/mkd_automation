#!/usr/bin/env python3
"""
MKD Automation - Main Entry Point
Cross-platform automation tool for capturing and reproducing user interactions.
"""

import sys
import os
from pathlib import Path

# Add src directory to path for imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

def main():
    """Main entry point for MKD Automation."""
    try:
        from mkd_v2.cli.gui_launcher import launch_gui
        from mkd_v2.integration.system_controller import SystemController
        from mkd_v2.integration.component_registry import ComponentRegistry
        from mkd_v2.integration.event_bus import EventBus
        from mkd_v2.integration.lifecycle_manager import LifecycleManager
        
        # Initialize system controller (it creates its own components internally)
        system_controller = SystemController()
        
        # Launch GUI
        success = launch_gui(system_controller)
        return 0 if success else 1
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed.")
        return 1
    except Exception as e:
        print(f"Startup error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())