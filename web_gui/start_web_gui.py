#!/usr/bin/env python3
"""
MKD Automation Web GUI Launcher

Launches both the backend WebSocket server and opens the web interface.
"""

import asyncio
import os
import sys
import webbrowser
import time
from pathlib import Path

def install_dependencies():
    """Install required dependencies."""
    try:
        import websockets
        print("✅ websockets library found")
    except ImportError:
        print("❌ websockets library not found")
        print("Installing websockets...")
        
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "websockets"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ websockets installed successfully")
        else:
            print("❌ Failed to install websockets")
            print(result.stderr)
            return False
    
    return True

def start_backend_server():
    """Start the backend WebSocket server."""
    print("🚀 Starting backend WebSocket server...")
    
    # Import and run the backend server
    try:
        from backend_server import main as backend_main
        return asyncio.create_task(backend_main())
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        return None

def open_web_interface():
    """Open the web interface in the default browser."""
    # Get the path to index.html
    web_gui_dir = Path(__file__).parent
    index_path = web_gui_dir / "index.html"
    
    if not index_path.exists():
        print(f"❌ Web interface not found: {index_path}")
        return False
    
    # Convert to file URL
    file_url = f"file://{index_path.absolute().as_uri().replace('file://', '')}"
    
    print(f"🌐 Opening web interface: {file_url}")
    
    try:
        webbrowser.open(file_url)
        return True
    except Exception as e:
        print(f"❌ Failed to open web browser: {e}")
        print(f"Please manually open: {index_path}")
        return False

async def main():
    """Main launcher function."""
    print("🎯 MKD Automation Web GUI Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return 1
    
    try:
        # Start backend server
        backend_task = start_backend_server()
        if not backend_task:
            return 1
        
        # Wait a moment for server to start
        await asyncio.sleep(2)
        
        # Open web interface
        open_web_interface()
        
        print("\n✅ Web GUI started successfully!")
        print("📱 Web interface should open in your browser")
        print("🔗 Backend server: ws://localhost:8765")
        print("🌐 Web interface: file:///.../index.html")
        print("\n📋 Instructions:")
        print("1. The web interface should open automatically")
        print("2. Check connection status in the System Information section")
        print("3. Use recording controls to capture and replay interactions")
        print("4. Press Ctrl+C here to stop the backend server")
        
        # Keep running until interrupted
        await backend_task
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    # Change to the web_gui directory
    os.chdir(Path(__file__).parent)
    
    # Run the launcher
    exit_code = asyncio.run(main())
    sys.exit(exit_code)