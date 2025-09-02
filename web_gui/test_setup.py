#!/usr/bin/env python3
"""Test script to verify web GUI setup."""

import sys
import os
from pathlib import Path

def test_dependencies():
    """Test required dependencies."""
    print("Testing dependencies...")
    
    # Test websockets
    try:
        import websockets
        print("+ websockets module available")
        websockets_ok = True
    except ImportError:
        print("- websockets module NOT available")
        websockets_ok = False
    
    # Test json (built-in)
    try:
        import json
        print("+ json module available")
        json_ok = True
    except ImportError:
        print("- json module NOT available")
        json_ok = False
    
    # Test asyncio (built-in)
    try:
        import asyncio
        print("+ asyncio module available")
        asyncio_ok = True
    except ImportError:
        print("- asyncio module NOT available")
        asyncio_ok = False
    
    return websockets_ok and json_ok and asyncio_ok

def test_files():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    
    required_files = [
        "index.html",
        "styles.css", 
        "script.js",
        "backend_server.py",
        "start_web_gui.py",
        "README.md"
    ]
    
    all_files_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"+ {file} exists")
        else:
            print(f"- {file} missing")
            all_files_exist = False
    
    return all_files_exist

def test_mkd_integration():
    """Test MKD system integration."""
    print("\nTesting MKD integration...")
    
    # Add src to path
    src_path = Path("..") / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    
    try:
        from mkd.core.session_manager import SessionManager
        print("+ MKD SessionManager available")
        mkd_ok = True
    except ImportError as e:
        print(f"- MKD modules not available: {e}")
        mkd_ok = False
    
    return mkd_ok

def main():
    """Run all tests."""
    print("=" * 50)
    print("MKD Web GUI Setup Test")
    print("=" * 50)
    
    deps_ok = test_dependencies()
    files_ok = test_files()
    mkd_ok = test_mkd_integration()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Dependencies: {'PASS' if deps_ok else 'FAIL'}")
    print(f"File Structure: {'PASS' if files_ok else 'FAIL'}")
    print(f"MKD Integration: {'PASS' if mkd_ok else 'WARN (optional)'}")
    
    if deps_ok and files_ok:
        print("\nWeb GUI is ready to run!")
        print("Run: python start_web_gui.py")
    else:
        print("\nSetup incomplete. Please fix the issues above.")
        if not deps_ok:
            print("Install dependencies: pip install websockets")
    
    return 0 if (deps_ok and files_ok) else 1

if __name__ == "__main__":
    sys.exit(main())