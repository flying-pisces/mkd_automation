"""
GUI Launcher for MKD Automation Conversation Mode.

This script launches the main GUI application with conversation interface.
"""

import sys
import os
import logging
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

# Set up environment
os.environ['MKD_GUI_MODE'] = '1'

def main():
    """Launch the MKD GUI application."""
    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('mkd_gui.log'),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info("Starting MKD GUI application")
        
        # Import and run GUI
        from mkd.ui.main_gui import main as run_gui
        run_gui()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install selenium webdriver-manager")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()