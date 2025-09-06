"""
Conversation UI Panel for MKD Automation.

This module provides a chat-like interface where users can type natural language
instructions and MKD will execute them through browser and desktop automation.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import threading
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
import logging
import re

from ..browser.integration import BrowserIntegration
from ..core.session import Session
from .instruction_parser import InstructionParser, CommandType

logger = logging.getLogger(__name__)


class Message:
    """Represents a conversation message."""
    
    def __init__(self, content: str, sender: str, timestamp: datetime = None, 
                 message_type: str = "text", metadata: Dict = None):
        self.content = content
        self.sender = sender  # "user" or "mkd"
        self.timestamp = timestamp or datetime.now()
        self.message_type = message_type  # "text", "action", "error", "success"
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for storage."""
        return {
            'content': self.content,
            'sender': self.sender,
            'timestamp': self.timestamp.isoformat(),
            'message_type': self.message_type,
            'metadata': self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        return cls(
            content=data['content'],
            sender=data['sender'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            message_type=data.get('message_type', 'text'),
            metadata=data.get('metadata', {})
        )


class ConversationPanel(ttk.Frame):
    """
    Chat-like conversation interface for MKD Automation.
    
    Features:
    - Natural language instruction input
    - Chat history display
    - Real-time execution feedback
    - Save/load conversation sessions
    - Integration with browser and desktop automation
    """
    
    def __init__(self, parent, session: Session = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.session = session or Session()
        self.browser_integration = None
        self.messages: List[Message] = []
        self.is_executing = False
        self.current_thread = None
        self.parser = InstructionParser()
        
        # Callbacks for external integration
        self.on_command_execute: Optional[Callable] = None
        self.on_session_start: Optional[Callable] = None
        self.on_session_stop: Optional[Callable] = None
        
        self._setup_ui()
        self._setup_bindings()
        
        # Add welcome message
        self._add_system_message("👋 Welcome to MKD Conversation Mode!\n\n" +
                                "Type natural language instructions and I'll execute them.\n" +
                                "Examples:\n" +
                                "• \"Open google.com and search for Python tutorials\"\n" +
                                "• \"Create EmailJS template for contact form\"\n" +
                                "• \"Record browser actions for 30 seconds\"\n" +
                                "• \"Take a screenshot and save it\"")
        
    def _setup_ui(self):
        """Setup the conversation UI components."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Header with title and controls
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text="🤖 MKD Assistant", font=('Arial', 12, 'bold'))
        title_label.grid(row=0, column=0, sticky='w')
        
        # Control buttons
        btn_frame = ttk.Frame(header_frame)
        btn_frame.grid(row=0, column=1, sticky='e')
        
        self.clear_btn = ttk.Button(btn_frame, text="Clear", command=self._clear_conversation, width=8)
        self.clear_btn.pack(side='left', padx=(0, 5))
        
        self.save_btn = ttk.Button(btn_frame, text="Save", command=self._save_conversation, width=8)
        self.save_btn.pack(side='left', padx=(0, 5))
        
        self.load_btn = ttk.Button(btn_frame, text="Load", command=self._load_conversation, width=8)
        self.load_btn.pack(side='left', padx=(0, 5))
        
        self.browser_btn = ttk.Button(btn_frame, text="Browser", command=self._toggle_browser, width=8)
        self.browser_btn.pack(side='left')
        
        # Chat history area
        history_frame = ttk.Frame(main_frame)
        history_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 5))
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)
        
        self.chat_display = scrolledtext.ScrolledText(
            history_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=20,
            font=('Consolas', 10),
            bg='#f8f9fa',
            fg='#212529'
        )
        self.chat_display.grid(row=0, column=0, sticky='nsew')
        
        # Configure text tags for styling
        self.chat_display.tag_configure('user', foreground='#0066cc', font=('Consolas', 10, 'bold'))
        self.chat_display.tag_configure('mkd', foreground='#28a745', font=('Consolas', 10, 'bold'))
        self.chat_display.tag_configure('system', foreground='#6c757d', font=('Consolas', 9, 'italic'))
        self.chat_display.tag_configure('error', foreground='#dc3545', font=('Consolas', 10, 'bold'))
        self.chat_display.tag_configure('success', foreground='#28a745')
        self.chat_display.tag_configure('action', foreground='#fd7e14')
        self.chat_display.tag_configure('timestamp', foreground='#6c757d', font=('Consolas', 8))
        
        # Input area
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, sticky='ew')
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Input field
        self.input_field = tk.Text(
            input_frame,
            height=3,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='white',
            fg='black'
        )
        self.input_field.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        
        # Send button
        self.send_btn = ttk.Button(
            input_frame,
            text="Send\n(Ctrl+Enter)",
            command=self._send_message,
            width=12
        )
        self.send_btn.grid(row=0, column=1, sticky='ns')
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=3, column=0, sticky='ew', pady=(5, 0))
        
        # Progress bar (hidden by default)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            mode='indeterminate'
        )
        
    def _setup_bindings(self):
        """Setup keyboard bindings and events."""
        # Ctrl+Enter to send message
        self.input_field.bind('<Control-Return>', lambda e: self._send_message())
        
        # Focus input field initially
        self.input_field.focus_set()
        
        # Bind to session events if available
        if hasattr(self.session, 'on_action_executed'):
            self.session.on_action_executed = self._on_action_executed
            
    def _add_message(self, message: Message):
        """Add a message to the chat display."""
        self.messages.append(message)
        
        # Enable text widget for editing
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp_str = message.timestamp.strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp_str}] ", 'timestamp')
        
        # Add sender and content with appropriate styling
        if message.sender == 'user':
            self.chat_display.insert(tk.END, "You: ", 'user')
        elif message.sender == 'mkd':
            self.chat_display.insert(tk.END, "MKD: ", 'mkd')
        else:
            self.chat_display.insert(tk.END, f"{message.sender}: ", 'system')
            
        # Add content with message type styling
        tag = message.message_type if message.message_type != 'text' else None
        self.chat_display.insert(tk.END, message.content + "\n\n", tag)
        
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        
        # Disable text widget
        self.chat_display.config(state=tk.DISABLED)
        
        # Force UI update
        self.update_idletasks()
        
    def _add_system_message(self, content: str, message_type: str = "system"):
        """Add a system message."""
        message = Message(content, "System", message_type=message_type)
        self._add_message(message)
        
    def _send_message(self):
        """Send user message and process it."""
        if self.is_executing:
            messagebox.showwarning("Busy", "Please wait for the current command to finish.")
            return
            
        content = self.input_field.get("1.0", tk.END).strip()
        if not content:
            return
            
        # Add user message
        user_message = Message(content, "user")
        self._add_message(user_message)
        
        # Clear input field
        self.input_field.delete("1.0", tk.END)
        
        # Process message in background thread
        self.is_executing = True
        self.send_btn.config(state='disabled')
        self.status_var.set("Processing...")
        self.progress_bar.grid(row=4, column=0, sticky='ew', pady=(2, 0))
        self.progress_bar.start()
        
        # Execute command in thread
        self.current_thread = threading.Thread(
            target=self._process_command,
            args=(content,),
            daemon=True
        )
        self.current_thread.start()
        
    def _process_command(self, command: str):
        """Process user command in background thread."""
        try:
            # Parse and execute command
            result = self._execute_instruction(command)
            
            # Update UI on main thread
            self.after(0, self._command_completed, result, None)
            
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            self.after(0, self._command_completed, None, str(e))
            
    def _command_completed(self, result: Any, error: str):
        """Handle command completion on main thread."""
        self.is_executing = False
        self.send_btn.config(state='normal')
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        
        if error:
            self.status_var.set("Error")
            self._add_system_message(f"❌ Error: {error}", "error")
        else:
            self.status_var.set("Ready")
            if result:
                self._add_system_message(f"✅ {result}", "success")
            else:
                self._add_system_message("✅ Command executed successfully", "success")
                
        # Re-focus input field
        self.input_field.focus_set()
        
    def _execute_instruction(self, instruction: str) -> str:
        """Execute natural language instruction using the parser."""
        # Parse the instruction
        parsed_command = self.parser.parse(instruction)
        
        # Log the parsed command
        logger.debug(f"Parsed command: {parsed_command.to_dict()}")
        
        # Show parsing info if confidence is low
        if parsed_command.confidence < 0.5:
            confidence_msg = f"⚠️ Low confidence ({parsed_command.confidence:.1%}) - trying anyway..."
            self._add_system_message(confidence_msg, "action")
            
        # Execute based on command type
        try:
            result = self._execute_parsed_command(parsed_command)
            
            # Add suggestions if available and command was unknown
            if parsed_command.type == CommandType.UNKNOWN and parsed_command.suggestions:
                suggestion_text = "\n💡 Suggestions:\n" + "\n".join(f"• {s}" for s in parsed_command.suggestions)
                result += suggestion_text
                
            return result
            
        except Exception as e:
            logger.error(f"Error executing parsed command: {e}")
            return f"Error executing command: {e}"
            
    def _execute_parsed_command(self, command) -> str:
        """Execute a parsed command."""
        command_type = command.type
        params = command.parameters
        
        if command_type == CommandType.BROWSER_NAVIGATE:
            return self._execute_browser_navigate(params)
        elif command_type == CommandType.BROWSER_SEARCH:
            return self._execute_browser_search(params)
        elif command_type == CommandType.BROWSER_CLICK:
            return self._execute_browser_click(params)
        elif command_type == CommandType.BROWSER_TYPE:
            return self._execute_browser_type(params)
        elif command_type == CommandType.BROWSER_SCREENSHOT:
            return self._execute_browser_screenshot(params)
        elif command_type == CommandType.BROWSER_SCROLL:
            return self._execute_browser_scroll(params)
        elif command_type == CommandType.BROWSER_WAIT:
            return self._execute_browser_wait(params)
        elif command_type == CommandType.EMAILJS_CREATE:
            return self._execute_emailjs_create(params)
        elif command_type == CommandType.RECORDING_START:
            return self._execute_recording_start(params)
        elif command_type == CommandType.RECORDING_STOP:
            return self._execute_recording_stop(params)
        elif command_type == CommandType.RECORDING_SAVE:
            return self._execute_recording_save(params)
        elif command_type == CommandType.RECORDING_LOAD:
            return self._execute_recording_load(params)
        elif command_type == CommandType.DESKTOP_SCREENSHOT:
            return self._execute_desktop_screenshot(params)
        elif command_type == CommandType.DESKTOP_HOTKEY:
            return self._execute_desktop_hotkey(params)
        elif command_type == CommandType.DESKTOP_CLICK:
            return self._execute_desktop_click(params)
        elif command_type == CommandType.DESKTOP_MOUSE_MOVE:
            return self._execute_desktop_mouse_move(params)
        elif command_type == CommandType.DESKTOP_DRAG:
            return self._execute_desktop_drag(params)
        elif command_type == CommandType.DESKTOP_TYPE:
            return self._execute_desktop_type(params)
        elif command_type == CommandType.LAUNCH_APPLICATION:
            return self._execute_launch_application(params)
        elif command_type == CommandType.CLOSE_APPLICATION:
            return self._execute_close_application(params)
        elif command_type == CommandType.MINIMIZE_WINDOW:
            return self._execute_minimize_window(params)
        elif command_type == CommandType.MAXIMIZE_WINDOW:
            return self._execute_maximize_window(params)
        elif command_type == CommandType.RESIZE_WINDOW:
            return self._execute_resize_window(params)
        elif command_type == CommandType.MOVE_WINDOW:
            return self._execute_move_window(params)
        elif command_type == CommandType.OPEN_FILE:
            return self._execute_open_file(params)
        elif command_type == CommandType.OPEN_FOLDER:
            return self._execute_open_folder(params)
        elif command_type == CommandType.CREATE_FILE:
            return self._execute_create_file(params)
        elif command_type == CommandType.DELETE_FILE:
            return self._execute_delete_file(params)
        elif command_type == CommandType.COPY_FILE:
            return self._execute_copy_file(params)
        elif command_type == CommandType.MOVE_FILE:
            return self._execute_move_file_cmd(params)
        elif command_type == CommandType.RUN_COMMAND_PROMPT:
            return self._execute_run_command_prompt(params)
        elif command_type == CommandType.RUN_POWERSHELL:
            return self._execute_run_powershell(params)
        elif command_type == CommandType.OPEN_TASK_MANAGER:
            return self._execute_open_task_manager(params)
        elif command_type == CommandType.OPEN_CONTROL_PANEL:
            return self._execute_open_control_panel(params)
        elif command_type == CommandType.LOCK_COMPUTER:
            return self._execute_lock_computer(params)
        elif command_type == CommandType.HELP:
            return self.parser.get_help_text()
        elif command_type == CommandType.STATUS:
            return self._get_status_info()
        elif command_type == CommandType.UNKNOWN:
            return f"❓ I don't understand: '{command.raw_instruction}'\n\nSay 'help' to see available commands."
        else:
            return f"Command type {command_type.value} not implemented yet."
            
    def _execute_browser_navigate(self, params: Dict[str, Any]) -> str:
        """Execute browser navigation command."""
        if not self.browser_integration:
            self.browser_integration = BrowserIntegration(self.session)
            self.browser_integration.start_browser_session()
            self._add_system_message("🌐 Browser session started", "action")
            
        url = params.get('url', '')
        if not url:
            return "❌ No URL specified for navigation"
            
        self.browser_integration.browser_session.browser_controller.navigate(url)
        return f"✅ Navigated to {url}"
        
    def _execute_browser_search(self, params: Dict[str, Any]) -> str:
        """Execute browser search command."""
        if not self.browser_integration:
            self.browser_integration = BrowserIntegration(self.session)
            self.browser_integration.start_browser_session()
            self._add_system_message("🌐 Browser session started", "action")
            
        query = params.get('query', '')
        engine = params.get('engine', 'google')
        
        if not query:
            return "❌ No search query specified"
            
        controller = self.browser_integration.browser_session.browser_controller
        
        # Navigate to search engine
        if engine.lower() == 'google':
            controller.navigate("https://www.google.com")
        elif engine.lower() == 'bing':
            controller.navigate("https://www.bing.com")
        else:
            controller.navigate("https://www.google.com")
            
        time.sleep(2)
        
        # Perform search
        try:
            controller.type_text("input[name='q'], input[name='search']", query)
            controller.execute_script("document.querySelector('input[name=\"q\"], input[name=\"search\"]').form.submit()")
            return f"✅ Searched {engine} for: {query}"
        except Exception as e:
            return f"❌ Search failed: {e}"
            
    def _execute_browser_click(self, params: Dict[str, Any]) -> str:
        """Execute browser click command."""
        if not self.browser_integration:
            return "❌ Browser session not active. Start browser first."
            
        target = params.get('target', '')
        if not target:
            return "❌ No click target specified"
            
        try:
            # Try multiple selector strategies
            selectors = [
                f"button:contains('{target}')",
                f"a:contains('{target}')",
                f"[aria-label*='{target}']",
                f"[title*='{target}']",
                f".{target}",
                f"#{target}",
                target
            ]
            
            controller = self.browser_integration.browser_session.browser_controller
            
            for selector in selectors:
                try:
                    controller.click(selector, wait=False)
                    return f"✅ Clicked: {target}"
                except:
                    continue
                    
            return f"❌ Could not find clickable element: {target}"
            
        except Exception as e:
            return f"❌ Click failed: {e}"
            
    def _execute_browser_type(self, params: Dict[str, Any]) -> str:
        """Execute browser type command."""
        if not self.browser_integration:
            return "❌ Browser session not active. Start browser first."
            
        text = params.get('text', '')
        target = params.get('target', '')
        
        if not text:
            return "❌ No text to type specified"
            
        try:
            controller = self.browser_integration.browser_session.browser_controller
            
            if target:
                # Try to find specific target field
                selectors = [
                    f"input[placeholder*='{target}']",
                    f"input[name*='{target}']",
                    f"textarea[placeholder*='{target}']",
                    f"[aria-label*='{target}']",
                    target
                ]
                
                for selector in selectors:
                    try:
                        controller.type_text(selector, text)
                        return f"✅ Typed '{text}' in {target}"
                    except:
                        continue
                        
                return f"❌ Could not find input field: {target}"
            else:
                # Type in focused element or first input
                controller.execute_script(f"document.activeElement.value = '{text}';")
                return f"✅ Typed: {text}"
                
        except Exception as e:
            return f"❌ Type failed: {e}"
            
    def _execute_browser_screenshot(self, params: Dict[str, Any]) -> str:
        """Execute browser screenshot command."""
        if not self.browser_integration:
            return "❌ Browser session not active. Start browser first."
            
        try:
            filename = "mkd_browser_screenshot.png"
            self.browser_integration.browser_session.browser_controller.take_screenshot(filename)
            return f"✅ Browser screenshot saved to {filename}"
        except Exception as e:
            return f"❌ Screenshot failed: {e}"
            
    def _execute_browser_scroll(self, params: Dict[str, Any]) -> str:
        """Execute browser scroll command."""
        if not self.browser_integration:
            return "❌ Browser session not active. Start browser first."
            
        try:
            controller = self.browser_integration.browser_session.browser_controller
            # Simple scroll down
            controller.execute_script("window.scrollBy(0, 500);")
            return "✅ Scrolled page"
        except Exception as e:
            return f"❌ Scroll failed: {e}"
            
    def _execute_browser_wait(self, params: Dict[str, Any]) -> str:
        """Execute browser wait command."""
        seconds = params.get('seconds', 5)
        time.sleep(seconds)
        return f"✅ Waited {seconds} seconds"
        
    def _execute_emailjs_create(self, params: Dict[str, Any]) -> str:
        """Execute EmailJS template creation."""
        from ..browser.emailjs_automation import EmailJSAutomation
        
        # Extract parameters
        email = params.get('email', params.get('emails', ['user@example.com'])[0] if params.get('emails') else 'user@example.com')
        template_name = params.get('quoted_strings', ['Contact Form'])[0] if params.get('quoted_strings') else 'Contact Form'
        
        automation = EmailJSAutomation()
        try:
            automation.start()
            
            template_config = {
                'template_name': template_name,
                'subject': 'New message from {{from_name}}',
                'content': '''Hello,

You have received a new message:

Name: {{from_name}}
Email: {{from_email}}
Message: {{message}}

Best regards''',
                'to_email': email,
                'reply_to': '{{from_email}}'
            }
            
            self._add_system_message(f"🚀 Creating EmailJS template '{template_name}' for {email}...", "action")
            template_id = automation.create_template(template_config)
            
            if template_id:
                return f"✅ EmailJS template created successfully! ID: {template_id}"
            else:
                return "✅ EmailJS template creation completed (please check browser)"
                
        except Exception as e:
            return f"❌ EmailJS automation failed: {e}"
        finally:
            # Keep browser open for user verification
            pass
            
    def _execute_recording_start(self, params: Dict[str, Any]) -> str:
        """Execute recording start command."""
        if not self.browser_integration:
            self.browser_integration = BrowserIntegration(self.session)
            self.browser_integration.start_browser_session()
            self._add_system_message("🌐 Browser session started", "action")
            
        try:
            self.browser_integration.start_browser_recording()
            return "✅ Browser recording started. Say 'stop recording' when done"
        except Exception as e:
            return f"❌ Recording start failed: {e}"
            
    def _execute_recording_stop(self, params: Dict[str, Any]) -> str:
        """Execute recording stop command."""
        if self.browser_integration and self.browser_integration._is_recording:
            actions = self.browser_integration.stop_browser_recording()
            return f"✅ Recording stopped. Captured {len(actions)} actions"
        else:
            return "❌ No recording in progress"
            
    def _execute_recording_save(self, params: Dict[str, Any]) -> str:
        """Execute recording save command."""
        filename = params.get('filename', 'recording.json')
        # Implementation would go here
        return f"✅ Recording save functionality not implemented yet. Would save to: {filename}"
        
    def _execute_recording_load(self, params: Dict[str, Any]) -> str:
        """Execute recording load command."""
        filename = params.get('filename', 'recording.json')
        # Implementation would go here
        return f"✅ Recording load functionality not implemented yet. Would load from: {filename}"
        
    def _execute_desktop_screenshot(self, params: Dict[str, Any]) -> str:
        """Execute desktop screenshot command."""
        return "❌ Desktop screenshot functionality not implemented yet"
        
    def _execute_desktop_hotkey(self, params: Dict[str, Any]) -> str:
        """Execute desktop hotkey command."""
        modifier = params.get('modifier', '')
        key = params.get('key', '')
        return f"❌ Desktop hotkey functionality not implemented yet. Would press: {modifier}+{key}"
        
    def _get_status_info(self) -> str:
        """Get current status information."""
        status_info = "📊 MKD Status:\n\n"
        
        # Browser status
        if self.browser_integration and self.browser_integration.browser_session:
            status_info += "🌐 Browser: Running\n"
            if self.browser_integration._is_recording:
                status_info += "🎬 Recording: Active\n"
            else:
                status_info += "🎬 Recording: Stopped\n"
        else:
            status_info += "🌐 Browser: Stopped\n"
            
        # Session status
        status_info += f"💼 Session: {'Active' if self.session else 'None'}\n"
        
        # Message count
        status_info += f"💬 Messages: {len(self.messages)}\n"
        
        return status_info
        
    def _get_desktop_controller(self):
        """Get desktop controller instance (lazy initialization)."""
        if not hasattr(self, '_desktop_controller'):
            from ..desktop.controller import DesktopController
            self._desktop_controller = DesktopController()
        return self._desktop_controller
        
    def _execute_desktop_click(self, params: Dict[str, Any]) -> str:
        """Execute desktop mouse click."""
        try:
            numbers = params.get('numbers', [])
            if len(numbers) >= 2:
                x, y = numbers[0], numbers[1]
                
                from ..desktop.actions import DesktopAction
                action = DesktopAction.mouse_click(x, y)
                
                controller = self._get_desktop_controller()
                controller.execute_action(action)
                
                return f"✅ Clicked at position ({x}, {y})"
            else:
                return "❌ Invalid coordinates. Use format: 'click at 100 200'"
        except Exception as e:
            return f"❌ Desktop click failed: {e}"
            
    def _execute_desktop_mouse_move(self, params: Dict[str, Any]) -> str:
        """Execute desktop mouse move."""
        try:
            numbers = params.get('numbers', [])
            if len(numbers) >= 2:
                x, y = numbers[0], numbers[1]
                
                from ..desktop.actions import DesktopAction
                action = DesktopAction.mouse_move(x, y)
                
                controller = self._get_desktop_controller()
                controller.execute_action(action)
                
                return f"✅ Moved mouse to ({x}, {y})"
            else:
                return "❌ Invalid coordinates. Use format: 'move mouse to 100 200'"
        except Exception as e:
            return f"❌ Mouse move failed: {e}"
            
    def _execute_desktop_drag(self, params: Dict[str, Any]) -> str:
        """Execute desktop mouse drag."""
        try:
            numbers = params.get('numbers', [])
            if len(numbers) >= 4:
                start_x, start_y, end_x, end_y = numbers[0], numbers[1], numbers[2], numbers[3]
                
                from ..desktop.actions import DesktopAction, DesktopActionType
                action = DesktopAction(
                    type=DesktopActionType.MOUSE_DRAG,
                    parameters={"start_x": start_x, "start_y": start_y, "end_x": end_x, "end_y": end_y}
                )
                
                controller = self._get_desktop_controller()
                controller.execute_action(action)
                
                return f"✅ Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"
            else:
                return "❌ Invalid coordinates. Use format: 'drag from 100 200 to 300 400'"
        except Exception as e:
            return f"❌ Desktop drag failed: {e}"
            
    def _execute_desktop_type(self, params: Dict[str, Any]) -> str:
        """Execute desktop text typing."""
        try:
            quoted_strings = params.get('quoted_strings', [])
            if quoted_strings:
                text = quoted_strings[0]
                
                from ..desktop.actions import DesktopAction
                action = DesktopAction.type_text(text)
                
                controller = self._get_desktop_controller()
                controller.execute_action(action)
                
                return f"✅ Typed: '{text}'"
            else:
                return "❌ No text specified. Use quotes: 'type \"Hello World\"'"
        except Exception as e:
            return f"❌ Desktop typing failed: {e}"
            
    def _execute_launch_application(self, params: Dict[str, Any]) -> str:
        """Execute launch application."""
        try:
            # Extract app name from instruction
            instruction = params.get('instruction', '')
            
            # Try to extract app name from quoted strings or direct text
            app_name = None
            if params.get('quoted_strings'):
                app_name = params['quoted_strings'][0]
            else:
                # Look for common app names in the instruction
                common_apps = ['notepad', 'calculator', 'paint', 'cmd', 'powershell', 'explorer', 
                              'chrome', 'firefox', 'edge', 'vscode', 'discord', 'spotify']
                for app in common_apps:
                    if app in instruction.lower():
                        app_name = app
                        break
                        
            if not app_name:
                return "❌ Could not identify application to launch. Try: 'launch notepad' or 'open calculator'"
                
            from ..desktop.application_manager import ApplicationManager
            app_manager = ApplicationManager()
            
            result = app_manager.launch_application(app_name)
            
            if result:
                return f"✅ Launched {app_name} (PID: {result['pid']})"
            else:
                return f"❌ Failed to launch {app_name}"
                
        except Exception as e:
            return f"❌ Application launch failed: {e}"
            
    def _execute_close_application(self, params: Dict[str, Any]) -> str:
        """Execute close application."""
        try:
            instruction = params.get('instruction', '')
            
            app_name = None
            if params.get('quoted_strings'):
                app_name = params['quoted_strings'][0]
            else:
                # Extract app name from instruction
                words = instruction.lower().split()
                if len(words) > 1:
                    app_name = words[-1]  # Last word is likely the app name
                    
            if not app_name:
                return "❌ Could not identify application to close. Try: 'close notepad'"
                
            from ..desktop.application_manager import ApplicationManager
            app_manager = ApplicationManager()
            
            success = app_manager.close_application(app_name)
            
            if success:
                return f"✅ Closed {app_name}"
            else:
                return f"❌ Failed to close {app_name} (may not be running)"
                
        except Exception as e:
            return f"❌ Application close failed: {e}"
            
    def _execute_open_file(self, params: Dict[str, Any]) -> str:
        """Execute open file."""
        try:
            quoted_strings = params.get('quoted_strings', [])
            instruction = params.get('instruction', '')
            
            file_path = None
            if quoted_strings:
                file_path = quoted_strings[0]
            else:
                # Try to extract file path from instruction
                words = instruction.split()
                for word in words:
                    if '\\' in word or '/' in word or '.' in word:
                        file_path = word
                        break
                        
            if not file_path:
                return "❌ No file path specified. Use: 'open file \"C:\\path\\to\\file.txt\"'"
                
            from ..desktop.file_operations import FileOperations
            file_ops = FileOperations()
            
            success = file_ops.open_file(file_path)
            
            if success:
                return f"✅ Opened file: {file_path}"
            else:
                return f"❌ Failed to open file: {file_path}"
                
        except Exception as e:
            return f"❌ File open failed: {e}"
            
    def _execute_open_folder(self, params: Dict[str, Any]) -> str:
        """Execute open folder."""
        try:
            quoted_strings = params.get('quoted_strings', [])
            instruction = params.get('instruction', '')
            
            folder_path = None
            if quoted_strings:
                folder_path = quoted_strings[0]
            else:
                # Try to extract folder path from instruction
                words = instruction.split()
                for word in words:
                    if '\\' in word or '/' in word:
                        folder_path = word
                        break
                        
            if not folder_path:
                # Default common folders
                if 'desktop' in instruction.lower():
                    import os
                    folder_path = os.path.join(os.path.expanduser('~'), 'Desktop')
                elif 'documents' in instruction.lower():
                    import os
                    folder_path = os.path.join(os.path.expanduser('~'), 'Documents')
                elif 'downloads' in instruction.lower():
                    import os
                    folder_path = os.path.join(os.path.expanduser('~'), 'Downloads')
                else:
                    return "❌ No folder path specified. Use: 'open folder \"C:\\path\\to\\folder\"'"
                    
            from ..desktop.file_operations import FileOperations
            file_ops = FileOperations()
            
            success = file_ops.open_folder(folder_path)
            
            if success:
                return f"✅ Opened folder: {folder_path}"
            else:
                return f"❌ Failed to open folder: {folder_path}"
                
        except Exception as e:
            return f"❌ Folder open failed: {e}"
            
    def _execute_create_file(self, params: Dict[str, Any]) -> str:
        """Execute create file."""
        try:
            quoted_strings = params.get('quoted_strings', [])
            
            if not quoted_strings:
                return "❌ No file name specified. Use: 'create file \"myfile.txt\"'"
                
            file_path = quoted_strings[0]
            
            from ..desktop.file_operations import FileOperations
            file_ops = FileOperations()
            
            success = file_ops.create_file(file_path)
            
            if success:
                return f"✅ Created file: {file_path}"
            else:
                return f"❌ Failed to create file: {file_path}"
                
        except Exception as e:
            return f"❌ File creation failed: {e}"
            
    def _execute_delete_file(self, params: Dict[str, Any]) -> str:
        """Execute delete file."""
        return "⚠️ File deletion not implemented for safety. Use file explorer manually."
        
    def _execute_copy_file(self, params: Dict[str, Any]) -> str:
        """Execute copy file."""
        return "❌ File copy functionality not implemented yet."
        
    def _execute_move_file_cmd(self, params: Dict[str, Any]) -> str:
        """Execute move file."""
        return "❌ File move functionality not implemented yet."
        
    def _execute_run_command_prompt(self, params: Dict[str, Any]) -> str:
        """Execute run command prompt."""
        try:
            from ..desktop.windows_automation import WindowsDesktopAutomation
            win_automation = WindowsDesktopAutomation()
            
            pid = win_automation.open_command_prompt()
            
            return f"✅ Opened Command Prompt (PID: {pid})"
            
        except Exception as e:
            return f"❌ Failed to open Command Prompt: {e}"
            
    def _execute_run_powershell(self, params: Dict[str, Any]) -> str:
        """Execute run PowerShell."""
        try:
            from ..desktop.windows_automation import WindowsDesktopAutomation
            win_automation = WindowsDesktopAutomation()
            
            pid = win_automation.open_powershell()
            
            return f"✅ Opened PowerShell (PID: {pid})"
            
        except Exception as e:
            return f"❌ Failed to open PowerShell: {e}"
            
    def _execute_open_task_manager(self, params: Dict[str, Any]) -> str:
        """Execute open task manager."""
        try:
            from ..desktop.windows_automation import WindowsDesktopAutomation
            win_automation = WindowsDesktopAutomation()
            
            success = win_automation.open_task_manager()
            
            if success:
                return "✅ Opened Task Manager"
            else:
                return "❌ Failed to open Task Manager"
                
        except Exception as e:
            return f"❌ Failed to open Task Manager: {e}"
            
    def _execute_open_control_panel(self, params: Dict[str, Any]) -> str:
        """Execute open control panel."""
        try:
            from ..desktop.windows_automation import WindowsDesktopAutomation
            win_automation = WindowsDesktopAutomation()
            
            success = win_automation.open_control_panel()
            
            if success:
                return "✅ Opened Control Panel"
            else:
                return "❌ Failed to open Control Panel"
                
        except Exception as e:
            return f"❌ Failed to open Control Panel: {e}"
            
    def _execute_lock_computer(self, params: Dict[str, Any]) -> str:
        """Execute lock computer."""
        try:
            from ..desktop.windows_automation import WindowsDesktopAutomation
            win_automation = WindowsDesktopAutomation()
            
            success = win_automation.lock_workstation()
            
            if success:
                return "✅ Computer locked"
            else:
                return "❌ Failed to lock computer"
                
        except Exception as e:
            return f"❌ Failed to lock computer: {e}"
            
    def _execute_minimize_window(self, params: Dict[str, Any]) -> str:
        """Execute minimize window."""
        try:
            from ..desktop.actions import DesktopAction
            action = DesktopAction(
                type=DesktopActionType.MINIMIZE_WINDOW,
                parameters={}
            )
            
            controller = self._get_desktop_controller()
            controller.execute_action(action)
            
            return "✅ Window minimized"
            
        except Exception as e:
            return f"❌ Window minimize failed: {e}"
            
    def _execute_maximize_window(self, params: Dict[str, Any]) -> str:
        """Execute maximize window."""
        try:
            from ..desktop.actions import DesktopAction
            action = DesktopAction(
                type=DesktopActionType.MAXIMIZE_WINDOW,
                parameters={}
            )
            
            controller = self._get_desktop_controller()
            controller.execute_action(action)
            
            return "✅ Window maximized"
            
        except Exception as e:
            return f"❌ Window maximize failed: {e}"
            
    def _execute_resize_window(self, params: Dict[str, Any]) -> str:
        """Execute resize window."""
        try:
            numbers = params.get('numbers', [])
            if len(numbers) >= 2:
                width, height = numbers[0], numbers[1]
                
                from ..desktop.actions import DesktopAction
                action = DesktopAction.resize_window(width, height)
                
                controller = self._get_desktop_controller()
                controller.execute_action(action)
                
                return f"✅ Window resized to {width}x{height}"
            else:
                return "❌ Invalid dimensions. Use format: 'resize window to 800x600'"
                
        except Exception as e:
            return f"❌ Window resize failed: {e}"
            
    def _execute_move_window(self, params: Dict[str, Any]) -> str:
        """Execute move window."""
        try:
            numbers = params.get('numbers', [])
            if len(numbers) >= 2:
                x, y = numbers[0], numbers[1]
                
                from ..desktop.actions import DesktopAction
                action = DesktopAction.move_window(x, y)
                
                controller = self._get_desktop_controller()
                controller.execute_action(action)
                
                return f"✅ Window moved to ({x}, {y})"
            else:
                return "❌ Invalid coordinates. Use format: 'move window to 100 200'"
                
        except Exception as e:
            return f"❌ Window move failed: {e}"
            
    def _execute_browser_instruction(self, instruction: str) -> str:
        """Execute browser-related instruction."""
        if not self.browser_integration:
            # Auto-start browser session
            self.browser_integration = BrowserIntegration(self.session)
            self.browser_integration.start_browser_session()
            self._add_system_message("🌐 Browser session started", "action")
            
        # Parse common browser actions
        instruction_lower = instruction.lower()
        
        # Extract URL
        import re
        url_match = re.search(r'(?:open|go to|navigate to)\s+([^\s,]+)', instruction_lower)
        if url_match:
            url = url_match.group(1)
            if not url.startswith('http'):
                url = f"https://{url}"
            
            self.browser_integration.browser_session.browser_controller.navigate(url)
            return f"Navigated to {url}"
            
        # Search functionality
        search_match = re.search(r'search (?:for )?"?([^"]+)"?', instruction_lower)
        if search_match and 'google' in instruction_lower:
            search_term = search_match.group(1).strip()
            controller = self.browser_integration.browser_session.browser_controller
            
            # Navigate to Google if not already there
            current_url = controller.get_current_url()
            if 'google.com' not in current_url:
                controller.navigate("https://www.google.com")
                time.sleep(2)
                
            # Perform search
            controller.type_text("input[name='q']", search_term)
            controller.execute_script("document.querySelector('input[name=\"q\"]').form.submit()")
            return f"Searched Google for: {search_term}"
            
        return "Browser instruction executed"
        
    def _execute_emailjs_instruction(self, instruction: str) -> str:
        """Execute EmailJS-related instruction."""
        from ..browser.emailjs_automation import EmailJSAutomation
        
        # Extract parameters from instruction
        email_match = re.search(r'email[:\s]+([^\s,]+@[^\s,]+)', instruction)
        name_match = re.search(r'(?:name|template)[:\s]+"?([^",]+)"?', instruction)
        
        to_email = email_match.group(1) if email_match else "user@example.com"
        template_name = name_match.group(1).strip() if name_match else "Contact Form"
        
        automation = EmailJSAutomation()
        try:
            automation.start()
            
            template_config = {
                'template_name': template_name,
                'subject': 'New message from {{from_name}}',
                'content': '''Hello,

You have received a new message:

Name: {{from_name}}
Email: {{from_email}}
Message: {{message}}

Best regards''',
                'to_email': to_email,
                'reply_to': '{{from_email}}'
            }
            
            self._add_system_message(f"🚀 Creating EmailJS template '{template_name}'...", "action")
            template_id = automation.create_template(template_config)
            
            if template_id:
                return f"EmailJS template created successfully! ID: {template_id}"
            else:
                return "EmailJS template creation completed (please check browser)"
                
        finally:
            # Keep browser open for user verification
            pass
            
    def _execute_screenshot_instruction(self, instruction: str) -> str:
        """Execute screenshot instruction."""
        if self.browser_integration and self.browser_integration.browser_session:
            # Browser screenshot
            filename = "mkd_screenshot.png"
            self.browser_integration.browser_session.browser_controller.take_screenshot(filename)
            return f"Browser screenshot saved to {filename}"
        else:
            # Desktop screenshot would go here
            return "Desktop screenshot functionality not implemented yet"
            
    def _execute_recording_instruction(self, instruction: str) -> str:
        """Execute recording instruction."""
        if 'stop' in instruction.lower():
            if self.browser_integration and self.browser_integration._is_recording:
                actions = self.browser_integration.stop_browser_recording()
                return f"Recording stopped. Captured {len(actions)} actions"
            else:
                return "No recording in progress"
        else:
            if not self.browser_integration:
                self.browser_integration = BrowserIntegration(self.session)
                self.browser_integration.start_browser_session()
                
            self.browser_integration.start_browser_recording()
            return "Browser recording started. Say 'stop recording' when done"
            
    def _execute_file_instruction(self, instruction: str) -> str:
        """Execute file-related instruction."""
        # This would implement save/load functionality
        return "File operations not implemented yet"
        
    def _execute_general_instruction(self, instruction: str) -> str:
        """Execute general instruction."""
        # Fallback for unrecognized instructions
        return f"I'm not sure how to: {instruction}\n\nTry commands like:\n• 'Open google.com'\n• 'Create EmailJS template'\n• 'Take screenshot'\n• 'Start recording'"
        
    def _clear_conversation(self):
        """Clear the conversation history."""
        if messagebox.askyesno("Clear Conversation", "Are you sure you want to clear all messages?"):
            self.messages.clear()
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self._add_system_message("Conversation cleared.")
            
    def _save_conversation(self):
        """Save conversation to file."""
        if not self.messages:
            messagebox.showwarning("Nothing to Save", "No conversation to save.")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save Conversation",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                data = {
                    'timestamp': datetime.now().isoformat(),
                    'messages': [msg.to_dict() for msg in self.messages]
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
                self._add_system_message(f"Conversation saved to {filename}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save conversation:\n{e}")
                
    def _load_conversation(self):
        """Load conversation from file."""
        filename = filedialog.askopenfilename(
            title="Load Conversation",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Clear current conversation
                self.messages.clear()
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete(1.0, tk.END)
                self.chat_display.config(state=tk.DISABLED)
                
                # Load messages
                for msg_data in data['messages']:
                    message = Message.from_dict(msg_data)
                    self._add_message(message)
                    
                self._add_system_message(f"Conversation loaded from {filename}")
                
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load conversation:\n{e}")
                
    def _toggle_browser(self):
        """Toggle browser session on/off."""
        if self.browser_integration and self.browser_integration.browser_session:
            self.browser_integration.stop_browser_session()
            self.browser_integration = None
            self.browser_btn.config(text="Browser")
            self._add_system_message("🌐 Browser session stopped", "action")
        else:
            self.browser_integration = BrowserIntegration(self.session)
            self.browser_integration.start_browser_session()
            self.browser_btn.config(text="Stop Browser")
            self._add_system_message("🌐 Browser session started", "action")
            
    def _on_action_executed(self, action, result):
        """Callback when action is executed."""
        self._add_system_message(f"🎯 Action executed: {action.type}", "action")
        
    def cleanup(self):
        """Cleanup resources when panel is destroyed."""
        if self.browser_integration:
            self.browser_integration.stop_browser_session()
            
        if self.current_thread and self.current_thread.is_alive():
            # Note: In a real implementation, you'd want proper thread cancellation
            pass