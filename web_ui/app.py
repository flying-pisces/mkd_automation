"""
MKD Desktop Automation - Web UI
Flask-based web interface for comprehensive desktop control.
"""
import os
import sys
import json
import time
import base64
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import threading
import queue

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mkd.desktop.controller import DesktopController
from mkd.desktop.actions import DesktopAction
from mkd.desktop.application_manager import ApplicationManager
from mkd.desktop.file_operations import FileOperations
from mkd.desktop.windows_automation import WindowsDesktopAutomation
from mkd.ui.instruction_parser import InstructionParser

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mkd_automation_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global automation components
desktop_controller = None
app_manager = None
file_ops = None
win_automation = None
instruction_parser = None
command_queue = queue.Queue()

def initialize_automation():
    """Initialize all automation components."""
    global desktop_controller, app_manager, file_ops, win_automation, instruction_parser
    
    try:
        desktop_controller = DesktopController()
        app_manager = ApplicationManager()
        file_ops = FileOperations()
        win_automation = WindowsDesktopAutomation()
        instruction_parser = InstructionParser()
        
        print("[OK] All automation components initialized successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to initialize automation components: {e}")
        return False

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """Get system status."""
    return jsonify({
        'status': 'online',
        'desktop_controller': desktop_controller is not None,
        'app_manager': app_manager is not None,
        'file_ops': file_ops is not None,
        'win_automation': win_automation is not None and win_automation.is_available,
        'instruction_parser': instruction_parser is not None
    })

@app.route('/api/desktop/click', methods=['POST'])
def api_desktop_click():
    """Execute desktop mouse click."""
    try:
        data = request.get_json()
        x = data.get('x', 0)
        y = data.get('y', 0)
        button = data.get('button', 'left')
        
        action = DesktopAction.mouse_click(x, y, button=button)
        desktop_controller.execute_action(action)
        
        return jsonify({'success': True, 'message': f'Clicked at ({x}, {y})'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/desktop/move', methods=['POST'])
def api_desktop_move():
    """Execute desktop mouse move."""
    try:
        data = request.get_json()
        x = data.get('x', 0)
        y = data.get('y', 0)
        smooth = data.get('smooth', True)
        
        action = DesktopAction.mouse_move(x, y, smooth=smooth)
        desktop_controller.execute_action(action)
        
        return jsonify({'success': True, 'message': f'Moved mouse to ({x}, {y})'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/desktop/type', methods=['POST'])
def api_desktop_type():
    """Execute desktop text typing."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        delay = data.get('delay', 0.05)
        
        action = DesktopAction.type_text(text, delay=delay)
        desktop_controller.execute_action(action)
        
        return jsonify({'success': True, 'message': f'Typed: "{text}"'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/desktop/key', methods=['POST'])
def api_desktop_key():
    """Execute desktop key press."""
    try:
        data = request.get_json()
        keys = data.get('keys', [])
        
        if len(keys) == 1:
            action = DesktopAction.key_press(keys[0])
        else:
            action = DesktopAction.key_combination(keys)
        
        desktop_controller.execute_action(action)
        
        return jsonify({'success': True, 'message': f'Pressed: {"+".join(keys)}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/desktop/screenshot', methods=['POST'])
def api_desktop_screenshot():
    """Take desktop screenshot."""
    try:
        timestamp = int(time.time())
        filename = f'web_screenshot_{timestamp}.png'
        
        action = DesktopAction.screenshot(filename)
        result = desktop_controller.execute_action(action)
        
        # Return the image as base64 for display
        try:
            with open(result, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                return jsonify({
                    'success': True, 
                    'message': f'Screenshot saved: {result}',
                    'image_data': f'data:image/png;base64,{img_data}',
                    'filename': result
                })
        except Exception:
            return jsonify({'success': True, 'message': f'Screenshot saved: {result}', 'filename': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/apps/list')
def api_apps_list():
    """Get list of running applications."""
    try:
        apps = app_manager.get_running_applications()[:20]  # Limit to top 20
        return jsonify({'success': True, 'apps': apps})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/apps/launch', methods=['POST'])
def api_apps_launch():
    """Launch an application."""
    try:
        data = request.get_json()
        app_name = data.get('app_name', '')
        args = data.get('args', [])
        
        result = app_manager.launch_application(app_name, args)
        
        if result:
            # Create a JSON-serializable version of the result
            serializable_result = {
                'pid': result.get('pid'),
                'command': result.get('command'),
                'args': result.get('args', [])
            }
            return jsonify({
                'success': True, 
                'message': f'Launched {app_name} (PID: {result["pid"]})',
                'app_info': serializable_result
            })
        else:
            return jsonify({'success': False, 'error': f'Failed to launch {app_name}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/apps/close', methods=['POST'])
def api_apps_close():
    """Close an application."""
    try:
        data = request.get_json()
        app_name = data.get('app_name', '')
        pid = data.get('pid')
        force = data.get('force', False)
        
        success = app_manager.close_application(app_name if app_name else None, pid, force)
        
        if success:
            return jsonify({'success': True, 'message': f'Closed {app_name or f"PID {pid}"}'})
        else:
            return jsonify({'success': False, 'error': f'Failed to close {app_name or f"PID {pid}"}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/files/list', methods=['POST'])
def api_files_list():
    """List files in directory."""
    try:
        data = request.get_json()
        directory = data.get('directory', str(Path.home()))
        include_hidden = data.get('include_hidden', False)
        
        files = file_ops.list_directory(directory, include_hidden)
        
        return jsonify({'success': True, 'files': files, 'directory': directory})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/files/create', methods=['POST'])
def api_files_create():
    """Create a file."""
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        content = data.get('content', '')
        overwrite = data.get('overwrite', False)
        
        success = file_ops.create_file(file_path, content, overwrite)
        
        if success:
            return jsonify({'success': True, 'message': f'Created file: {file_path}'})
        else:
            return jsonify({'success': False, 'error': f'Failed to create file: {file_path}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/files/open', methods=['POST'])
def api_files_open():
    """Open a file or folder."""
    try:
        data = request.get_json()
        path = data.get('path', '')
        app = data.get('app')
        
        if Path(path).is_dir():
            success = file_ops.open_folder(path)
        else:
            success = file_ops.open_file(path, app)
        
        if success:
            return jsonify({'success': True, 'message': f'Opened: {path}'})
        else:
            return jsonify({'success': False, 'error': f'Failed to open: {path}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/windows/list')
def api_windows_list():
    """Get list of open windows."""
    try:
        if win_automation and win_automation.is_available:
            windows = win_automation.get_window_list()
            # Clean up window titles for display
            for window in windows:
                try:
                    window['title'] = window['title'].encode('ascii', 'ignore').decode('ascii')
                except:
                    window['title'] = '[Window]'
            return jsonify({'success': True, 'windows': windows})
        else:
            return jsonify({'success': False, 'error': 'Windows automation not available'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/windows/manage', methods=['POST'])
def api_windows_manage():
    """Manage window (minimize, maximize, close, etc.)."""
    try:
        data = request.get_json()
        action = data.get('action', '')
        hwnd = data.get('hwnd')
        
        if not win_automation or not win_automation.is_available:
            return jsonify({'success': False, 'error': 'Windows automation not available'})
        
        success = False
        if action == 'minimize' and hwnd:
            success = win_automation.minimize_window(hwnd)
        elif action == 'maximize' and hwnd:
            success = win_automation.maximize_window(hwnd)
        elif action == 'close' and hwnd:
            success = win_automation.close_window(hwnd)
        elif action == 'activate' and hwnd:
            success = win_automation.activate_window(hwnd)
        
        if success:
            return jsonify({'success': True, 'message': f'Window {action} successful'})
        else:
            return jsonify({'success': False, 'error': f'Window {action} failed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/command/parse', methods=['POST'])
def api_command_parse():
    """Parse natural language command."""
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        result = instruction_parser.parse(command)
        
        return jsonify({
            'success': True,
            'command': command,
            'type': result.type.value if result.type else 'unknown',
            'confidence': result.confidence,
            'parameters': result.parameters,
            'suggestions': result.suggestions or []
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/command/execute', methods=['POST'])
def api_command_execute():
    """Execute natural language command."""
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        # Parse the command
        parsed = instruction_parser.parse(command)
        
        # Execute based on command type
        if parsed.confidence < 0.5:
            return jsonify({'success': False, 'error': f'Low confidence command recognition: {parsed.confidence:.2f}'})
        
        result = execute_parsed_command(parsed)
        
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'command': command,
            'type': parsed.type.value,
            'confidence': parsed.confidence
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def execute_parsed_command(parsed):
    """Execute a parsed command."""
    try:
        cmd_type = parsed.type.value
        params = parsed.parameters
        
        # Desktop click commands
        if 'click' in cmd_type and 'numbers' in params and len(params['numbers']) >= 2:
            x, y = params['numbers'][0], params['numbers'][1]
            action = DesktopAction.mouse_click(x, y)
            desktop_controller.execute_action(action)
            return {'success': True, 'message': f'Clicked at ({x}, {y})'}
        
        # Desktop mouse move commands
        if 'mouse_move' in cmd_type and 'numbers' in params and len(params['numbers']) >= 2:
            x, y = params['numbers'][0], params['numbers'][1]
            action = DesktopAction.mouse_move(x, y)
            desktop_controller.execute_action(action)
            return {'success': True, 'message': f'Moved mouse to ({x}, {y})'}
        
        # Application launch commands
        if 'launch_application' in cmd_type:
            # Extract app name from command
            command_text = parsed.raw_instruction.lower()
            if 'notepad' in command_text:
                result = app_manager.launch_application('notepad')
                return {'success': True, 'message': f'Launched Notepad (PID: {result["pid"]})'}
            elif 'calculator' in command_text:
                result = app_manager.launch_application('calculator')
                return {'success': True, 'message': f'Launched Calculator (PID: {result["pid"]})'}
        
        # Screenshot commands
        if 'screenshot' in cmd_type:
            timestamp = int(time.time())
            filename = f'command_screenshot_{timestamp}.png'
            action = DesktopAction.screenshot(filename)
            result = desktop_controller.execute_action(action)
            return {'success': True, 'message': f'Screenshot saved: {result}'}
        
        # Key combination commands
        if 'hotkey' in cmd_type and 'modifier' in params and 'key' in params:
            keys = [params['modifier'], params['key']]
            action = DesktopAction.key_combination(keys)
            desktop_controller.execute_action(action)
            return {'success': True, 'message': f'Pressed {"+".join(keys)}'}
        
        return {'success': False, 'message': f'Command type {cmd_type} not yet implemented in web execution'}
        
    except Exception as e:
        return {'success': False, 'message': f'Execution error: {e}'}

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    print('Client connected')
    emit('status', {'message': 'Connected to MKD Automation'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    print('Client disconnected')

@socketio.on('live_command')
def handle_live_command(data):
    """Handle real-time command execution."""
    try:
        command = data.get('command', '')
        result = instruction_parser.parse(command)
        
        # Execute the command
        exec_result = execute_parsed_command(result)
        
        # Emit result back to client
        emit('command_result', {
            'command': command,
            'success': exec_result['success'],
            'message': exec_result['message'],
            'type': result.type.value,
            'confidence': result.confidence
        })
    except Exception as e:
        emit('command_result', {
            'command': command,
            'success': False,
            'message': f'Error: {e}',
            'type': 'error',
            'confidence': 0
        })

if __name__ == '__main__':
    print("=== MKD Desktop Automation Web UI ===")
    print("Initializing automation components...")
    
    if initialize_automation():
        print("[OK] Automation system ready")
        print("Starting web server...")
        print("Access the web interface at: http://localhost:5000")
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    else:
        print("[ERROR] Failed to initialize automation system")
        sys.exit(1)