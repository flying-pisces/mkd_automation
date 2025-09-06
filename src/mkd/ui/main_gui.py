"""
Main GUI Application for MKD Automation with Conversation Interface.

This module provides the main GUI window with integrated conversation
capabilities for natural language automation control.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional
import threading
import sys
from pathlib import Path

from ..core.session import Session
from ..browser.integration import BrowserIntegration
from .conversation_panel import ConversationPanel
from .instruction_parser import InstructionParser

logger = logging.getLogger(__name__)


class MKDMainGUI:
    """
    Main GUI application for MKD Automation.
    
    Features:
    - Conversation interface for natural language commands
    - Browser automation integration
    - Session management
    - Real-time status updates
    """
    
    def __init__(self):
        """Initialize the main GUI application."""
        self.root = tk.Tk()
        self.session = Session()
        self.parser = InstructionParser()
        self.browser_integration: Optional[BrowserIntegration] = None
        
        # GUI components
        self.conversation_panel: Optional[ConversationPanel] = None
        self.status_var = tk.StringVar(value="Ready")
        self.session_var = tk.StringVar(value="No Session")
        
        self._setup_gui()
        self._setup_logging()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _setup_gui(self):
        """Setup the main GUI window and components."""
        # Window configuration
        self.root.title("MKD Automation - Conversation Mode")
        self.root.geometry("900x700")
        self.root.minsize(600, 500)
        
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main menu
        self._create_menu()
        
        # Status bar at top
        self._create_status_bar()
        
        # Main content area - Conversation Panel
        self.conversation_panel = ConversationPanel(
            self.root,
            session=self.session
        )
        self.conversation_panel.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        # Connect callbacks
        self.conversation_panel.on_session_start = self._on_session_start
        self.conversation_panel.on_session_stop = self._on_session_stop
        
        # Bottom status bar
        self._create_bottom_status()
        
    def _create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Session", command=self._new_session)
        file_menu.add_command(label="Save Session", command=self._save_session)
        file_menu.add_command(label="Load Session", command=self._load_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Browser menu
        browser_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Browser", menu=browser_menu)
        browser_menu.add_command(label="Start Browser Session", command=self._start_browser)
        browser_menu.add_command(label="Stop Browser Session", command=self._stop_browser)
        browser_menu.add_separator()
        browser_menu.add_command(label="Record Browser Actions", command=self._start_browser_recording)
        browser_menu.add_command(label="Stop Recording", command=self._stop_browser_recording)
        
        # Automation menu
        automation_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Automation", menu=automation_menu)
        automation_menu.add_command(label="EmailJS Template", command=self._emailjs_automation)
        automation_menu.add_command(label="Take Screenshot", command=self._take_screenshot)
        automation_menu.add_separator()
        automation_menu.add_command(label="Show Examples", command=self._show_examples)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Commands", command=self._show_help)
        help_menu.add_command(label="About", command=self._show_about)
        
    def _create_status_bar(self):
        """Create the top status bar."""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=(5, 0))
        status_frame.grid_columnconfigure(1, weight=1)
        
        # Session indicator
        ttk.Label(status_frame, text="Session:").grid(row=0, column=0, sticky='w')
        session_label = ttk.Label(status_frame, textvariable=self.session_var, foreground='blue')
        session_label.grid(row=0, column=1, sticky='w', padx=(5, 20))
        
        # Browser status
        ttk.Label(status_frame, text="Browser:").grid(row=0, column=2, sticky='w')
        self.browser_var = tk.StringVar(value="Stopped")
        browser_label = ttk.Label(status_frame, textvariable=self.browser_var, foreground='red')
        browser_label.grid(row=0, column=3, sticky='w', padx=(5, 20))
        
        # Quick action buttons
        quick_frame = ttk.Frame(status_frame)
        quick_frame.grid(row=0, column=4, sticky='e')
        
        ttk.Button(quick_frame, text="🌐", command=self._quick_browser, width=3).pack(side='left', padx=1)
        ttk.Button(quick_frame, text="📸", command=self._quick_screenshot, width=3).pack(side='left', padx=1)
        ttk.Button(quick_frame, text="🎬", command=self._quick_record, width=3).pack(side='left', padx=1)
        ttk.Button(quick_frame, text="❓", command=self._show_help, width=3).pack(side='left', padx=1)
        
    def _create_bottom_status(self):
        """Create the bottom status bar."""
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        status_frame.grid(row=2, column=0, sticky='ew')
        
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side='left', padx=5, pady=2)
        
        # Version info
        version_label = ttk.Label(status_frame, text="MKD Automation v1.0", foreground='gray')
        version_label.pack(side='right', padx=5, pady=2)
        
    def _setup_logging(self):
        """Setup logging to display in status bar."""
        class StatusHandler(logging.Handler):
            def __init__(self, status_var):
                super().__init__()
                self.status_var = status_var
                
            def emit(self, record):
                if record.levelno >= logging.INFO:
                    self.status_var.set(f"{record.levelname}: {record.getMessage()}")
        
        # Add status handler
        status_handler = StatusHandler(self.status_var)
        status_handler.setLevel(logging.INFO)
        logging.getLogger('mkd').addHandler(status_handler)
        
    def _new_session(self):
        """Create a new automation session."""
        if messagebox.askyesno("New Session", "Create a new session? Current session will be lost."):
            # Stop current browser session if active
            if self.browser_integration:
                self.browser_integration.stop_browser_session()
                self.browser_integration = None
                self.browser_var.set("Stopped")
            
            # Create new session
            self.session = Session()
            self.session_var.set("New Session")
            self.status_var.set("New session created")
            
            # Update conversation panel
            if self.conversation_panel:
                self.conversation_panel.session = self.session
                
    def _save_session(self):
        """Save current session."""
        messagebox.showinfo("Save Session", "Session save functionality not implemented yet.")
        
    def _load_session(self):
        """Load a session."""
        messagebox.showinfo("Load Session", "Session load functionality not implemented yet.")
        
    def _start_browser(self):
        """Start browser automation session."""
        try:
            if not self.browser_integration:
                self.browser_integration = BrowserIntegration(self.session)
                
            self.browser_integration.start_browser_session()
            self.browser_var.set("Running")
            self.status_var.set("Browser session started")
            
            # Update conversation panel
            if self.conversation_panel:
                self.conversation_panel.browser_integration = self.browser_integration
                
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            messagebox.showerror("Browser Error", f"Failed to start browser:\\n{e}")
            
    def _stop_browser(self):
        """Stop browser automation session."""
        if self.browser_integration:
            self.browser_integration.stop_browser_session()
            self.browser_integration = None
            self.browser_var.set("Stopped")
            self.status_var.set("Browser session stopped")
            
            # Update conversation panel
            if self.conversation_panel:
                self.conversation_panel.browser_integration = None
                
    def _start_browser_recording(self):
        """Start recording browser actions."""
        if not self.browser_integration:
            self._start_browser()
            
        if self.browser_integration:
            self.browser_integration.start_browser_recording()
            self.status_var.set("Recording browser actions...")
            
    def _stop_browser_recording(self):
        """Stop recording browser actions."""
        if self.browser_integration and self.browser_integration._is_recording:
            actions = self.browser_integration.stop_browser_recording()
            self.status_var.set(f"Recording stopped. Captured {len(actions)} actions")
        else:
            messagebox.showinfo("Recording", "No recording in progress.")
            
    def _emailjs_automation(self):
        """Launch EmailJS automation."""
        if self.conversation_panel:
            self.conversation_panel._add_system_message("🚀 Starting EmailJS automation...")
            # Use conversation panel to execute EmailJS command
            self.conversation_panel._execute_instruction("Create EmailJS template")
            
    def _take_screenshot(self):
        """Take a screenshot."""
        if self.conversation_panel:
            self.conversation_panel._execute_instruction("Take screenshot")
            
    def _show_examples(self):
        """Show example commands."""
        examples = """
📋 Example Commands:

🌐 Browser Navigation:
• "Open google.com"
• "Go to dashboard.emailjs.com"
• "Navigate to github.com/user/repo"

🔍 Web Search:
• "Search for Python tutorials"
• "Google machine learning courses"

🖱️ Web Interaction:
• "Click the login button"
• "Type my email in the username field"
• "Fill contact form with test data"

📧 EmailJS Automation:
• "Create EmailJS template"
• "Setup email template for contact form"
• "Create template with email admin@example.com"

🎬 Recording:
• "Start recording browser actions"
• "Stop recording"
• "Save recording as automation.json"

📸 Screenshots:
• "Take screenshot"
• "Capture browser page"
• "Screenshot the current window"

⌨️ Desktop Actions:
• "Press Ctrl+C"
• "Use hotkey Alt+Tab"
• "Type Hello World"

💡 Tips:
• Be specific with button/field names
• Use quotes for exact text: "Hello World"
• Commands work in natural language
• Say "help" anytime for assistance
"""
        
        # Create example window
        example_window = tk.Toplevel(self.root)
        example_window.title("Command Examples")
        example_window.geometry("600x500")
        
        text_widget = tk.Text(example_window, wrap=tk.WORD, font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(example_window, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        text_widget.insert('1.0', examples)
        text_widget.config(state='disabled')
        
    def _show_help(self):
        """Show help information."""
        if self.conversation_panel:
            help_text = self.parser.get_help_text()
            self.conversation_panel._add_system_message(help_text)
            
    def _show_about(self):
        """Show about dialog."""
        about_text = """
MKD Automation - Conversation Mode
Version 1.0

A powerful automation tool that bridges the gap between
AI assistance and actual system control.

Features:
• Natural language command processing
• Browser automation with Selenium
• Desktop automation capabilities  
• Recording and playback functionality
• EmailJS template automation

© 2024 MKD Automation Project
"""
        messagebox.showinfo("About MKD Automation", about_text)
        
    def _quick_browser(self):
        """Quick browser toggle."""
        if self.browser_var.get() == "Stopped":
            self._start_browser()
        else:
            self._stop_browser()
            
    def _quick_screenshot(self):
        """Quick screenshot."""
        self._take_screenshot()
        
    def _quick_record(self):
        """Quick record toggle."""
        if self.browser_integration and self.browser_integration._is_recording:
            self._stop_browser_recording()
        else:
            self._start_browser_recording()
            
    def _on_session_start(self):
        """Callback when session starts."""
        self.session_var.set("Active")
        
    def _on_session_stop(self):
        """Callback when session stops."""
        self.session_var.set("Stopped")
        
    def _on_closing(self):
        """Handle application closing."""
        try:
            # Stop browser session
            if self.browser_integration:
                self.browser_integration.stop_browser_session()
                
            # Cleanup conversation panel
            if self.conversation_panel:
                self.conversation_panel.cleanup()
                
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            self.root.destroy()
            
    def run(self):
        """Start the GUI application."""
        logger.info("Starting MKD GUI application")
        self.root.mainloop()


def main():
    """Main entry point for the GUI application."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        app = MKDMainGUI()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error in GUI: {e}")
        messagebox.showerror("Fatal Error", f"Application error:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()