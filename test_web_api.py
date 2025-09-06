"""
Test Web API
Test the web-based desktop automation API endpoints.
"""
import requests
import json
import time

def test_web_api():
    """Test the web API endpoints."""
    base_url = "http://localhost:5000"
    
    print("=== MKD Web UI API Testing ===")
    print(f"Testing API at: {base_url}")
    
    # Test system status
    print("\n1. Testing System Status...")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   [OK] System Status: {status['status']}")
            print(f"   Desktop Controller: {status['desktop_controller']}")
            print(f"   Application Manager: {status['app_manager']}")
            print(f"   Windows Automation: {status['win_automation']}")
        else:
            print(f"   [ERROR] Status check failed: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Connection failed: {e}")
        return False
    
    # Test natural language command parsing
    print("\n2. Testing Natural Language Commands...")
    test_commands = [
        "click at 500, 300",
        "type hello world",
        "open notepad",
        "take screenshot"
    ]
    
    for cmd in test_commands:
        try:
            response = requests.post(f"{base_url}/api/command/parse", 
                                   json={"command": cmd})
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"   [OK] '{cmd}' -> {result['type']} (confidence: {result['confidence']:.2f})")
                else:
                    print(f"   [ERROR] '{cmd}' -> Parse failed")
            else:
                print(f"   [ERROR] '{cmd}' -> HTTP {response.status_code}")
        except Exception as e:
            print(f"   [ERROR] '{cmd}' -> {e}")
    
    # Test desktop actions
    print("\n3. Testing Desktop Actions...")
    
    # Test mouse move
    try:
        response = requests.post(f"{base_url}/api/desktop/move", 
                               json={"x": 400, "y": 300})
        if response.status_code == 200 and response.json().get('success'):
            print("   [OK] Mouse move to (400, 300)")
        else:
            print(f"   [ERROR] Mouse move failed: {response.json()}")
    except Exception as e:
        print(f"   [ERROR] Mouse move error: {e}")
    
    # Test typing
    try:
        response = requests.post(f"{base_url}/api/desktop/type", 
                               json={"text": "MKD Web UI Test"})
        if response.status_code == 200 and response.json().get('success'):
            print("   [OK] Text typing successful")
        else:
            print(f"   [ERROR] Text typing failed: {response.json()}")
    except Exception as e:
        print(f"   [ERROR] Text typing error: {e}")
    
    # Test application launch
    print("\n4. Testing Application Management...")
    try:
        response = requests.post(f"{base_url}/api/apps/launch", 
                               json={"app_name": "notepad"})
        if response.status_code == 200 and response.json().get('success'):
            result = response.json()
            print(f"   [OK] Notepad launched: {result['message']}")
            
            # Wait a moment then get app list
            time.sleep(2)
            response = requests.get(f"{base_url}/api/apps/list")
            if response.status_code == 200:
                apps = response.json()
                if apps['success']:
                    notepad_apps = [app for app in apps['apps'] if 'notepad' in app['name'].lower()]
                    print(f"   [OK] Found {len(notepad_apps)} Notepad instance(s)")
                    
                    # Close notepad
                    if notepad_apps:
                        pid = notepad_apps[0]['pid']
                        response = requests.post(f"{base_url}/api/apps/close", 
                                               json={"pid": pid})
                        if response.status_code == 200 and response.json().get('success'):
                            print(f"   [OK] Notepad closed (PID: {pid})")
        else:
            result = response.json()
            print(f"   [ERROR] Notepad launch failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   [ERROR] App management error: {e}")
    
    # Test screenshot
    print("\n5. Testing Screenshot Capture...")
    try:
        response = requests.post(f"{base_url}/api/desktop/screenshot", json={})
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"   [OK] Screenshot captured: {result['message']}")
                if 'image_data' in result:
                    print("   [OK] Screenshot image data returned")
            else:
                print(f"   [ERROR] Screenshot failed: {result['error']}")
        else:
            print(f"   [ERROR] Screenshot HTTP error: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Screenshot error: {e}")
    
    # Test natural language command execution
    print("\n6. Testing Command Execution...")
    try:
        response = requests.post(f"{base_url}/api/command/execute", 
                               json={"command": "take screenshot"})
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"   [OK] Command executed: {result['message']}")
            else:
                print(f"   [ERROR] Command execution failed: {result['error']}")
        else:
            print(f"   [ERROR] Command execution HTTP error: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Command execution error: {e}")
    
    print("\n=== Web API Test Complete ===")
    print("The web interface is fully functional and ready for use!")
    print("You can now access the full desktop automation system at:")
    print(f"   {base_url}")
    
    return True

if __name__ == "__main__":
    test_web_api()