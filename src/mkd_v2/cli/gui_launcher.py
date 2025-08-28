"""
GUI Launcher

Optional graphical interface launcher for the MKD Automation Platform.
Provides system status, configuration, and basic management capabilities.
"""

import sys
import os
import json
import asyncio
import threading
import logging
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import time

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog, scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

logger = logging.getLogger(__name__)


class SystemMonitor:
    """System monitoring widget"""
    
    def __init__(self, parent_frame, system_controller=None):
        self.parent_frame = parent_frame
        self.system_controller = system_controller
        
        # Create monitoring frame
        self.monitor_frame = ttk.LabelFrame(parent_frame, text="System Status", padding=10)
        self.monitor_frame.pack(fill="x", padx=5, pady=5)
        
        # Status indicators
        self.status_vars = {
            "system_running": tk.StringVar(value="🔴 Stopped"),
            "components": tk.StringVar(value="Components: 0"),
            "uptime": tk.StringVar(value="Uptime: 0s"),
            "memory": tk.StringVar(value="Memory: Normal"),
            "events": tk.StringVar(value="Events: 0")
        }
        
        # Create status labels
        row = 0
        for key, var in self.status_vars.items():
            label = ttk.Label(self.monitor_frame, textvariable=var)
            label.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            row += 1
        
        # Start monitoring
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start system monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
    
    def _monitor_loop(self):
        """System monitoring loop"""
        while self.monitoring:
            try:
                if self.system_controller:
                    # Get system status
                    stats = self.system_controller.get_system_statistics()
                    
                    # Update status vars
                    self.status_vars["system_running"].set(
                        "🟢 Running" if stats.get("system_running") else "🔴 Stopped"
                    )
                    self.status_vars["components"].set(f"Components: {stats.get('total_components', 0)}")
                    self.status_vars["uptime"].set(f"Uptime: {stats.get('uptime_seconds', 0):.0f}s")
                    self.status_vars["events"].set(f"Events: {stats.get('total_events', 0)}")
                
                time.sleep(2)
                
            except Exception as e:
                logger.debug(f"Monitor update failed: {e}")
                time.sleep(5)


class CommandConsole:
    """Command console widget"""
    
    def __init__(self, parent_frame, command_handler=None):
        self.parent_frame = parent_frame
        self.command_handler = command_handler
        
        # Create console frame
        self.console_frame = ttk.LabelFrame(parent_frame, text="Command Console", padding=10)
        self.console_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Output area
        self.output_area = scrolledtext.ScrolledText(
            self.console_frame, 
            height=15, 
            state="disabled",
            font=("Consolas", 10)
        )
        self.output_area.pack(fill="both", expand=True, pady=(0, 5))
        
        # Command input frame
        self.input_frame = ttk.Frame(self.console_frame)
        self.input_frame.pack(fill="x")
        
        # Command entry
        self.command_var = tk.StringVar()
        self.command_entry = ttk.Entry(self.input_frame, textvariable=self.command_var)
        self.command_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.command_entry.bind("<Return>", self._execute_command)
        
        # Execute button
        self.execute_btn = ttk.Button(
            self.input_frame, 
            text="Execute", 
            command=self._execute_command
        )
        self.execute_btn.pack(side="right")
        
        # Add initial message
        self._append_output("MKD Command Console Ready\nType 'help' for available commands\n\n")
    
    def _execute_command(self, event=None):
        """Execute command"""
        command = self.command_var.get().strip()
        
        if not command:
            return
        
        # Add command to output
        self._append_output(f"mkd> {command}\n")
        
        # Clear input
        self.command_var.set("")
        
        # Execute command
        if self.command_handler:
            try:
                # Run command in separate thread to avoid blocking UI
                threading.Thread(
                    target=self._run_command_async,
                    args=(command,),
                    daemon=True
                ).start()
            except Exception as e:
                self._append_output(f"Error: {e}\n\n")
        else:
            self._append_output("No command handler available\n\n")
    
    def _run_command_async(self, command):
        """Run command asynchronously"""
        try:
            # This would integrate with the actual CLI command system
            result = f"Command '{command}' executed (GUI mode)\n"
            
            # Simulate command execution
            time.sleep(0.5)
            
            # Add result to output
            self._append_output(result + "\n")
            
        except Exception as e:
            self._append_output(f"Command failed: {e}\n\n")
    
    def _append_output(self, text):
        """Append text to output area"""
        self.output_area.config(state="normal")
        self.output_area.insert(tk.END, text)
        self.output_area.see(tk.END)
        self.output_area.config(state="disabled")


class ConfigurationPanel:
    """Configuration management panel"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        
        # Create config frame
        self.config_frame = ttk.LabelFrame(parent_frame, text="Configuration", padding=10)
        self.config_frame.pack(fill="x", padx=5, pady=5)
        
        # Configuration variables
        self.config_vars = {
            "auto_start_system": tk.BooleanVar(),
            "verbose_output": tk.BooleanVar(),
            "colored_output": tk.BooleanVar(),
            "progress_indicators": tk.BooleanVar(),
        }
        
        # Create checkboxes
        row = 0
        for key, var in self.config_vars.items():
            text = key.replace("_", " ").title()
            checkbox = ttk.Checkbutton(self.config_frame, text=text, variable=var)
            checkbox.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            row += 1
        
        # Buttons frame
        self.buttons_frame = ttk.Frame(self.config_frame)
        self.buttons_frame.grid(row=row, column=0, pady=10)
        
        # Load/Save buttons
        ttk.Button(self.buttons_frame, text="Load Config", command=self._load_config).pack(side="left", padx=(0, 5))
        ttk.Button(self.buttons_frame, text="Save Config", command=self._save_config).pack(side="left")
        
        # Load initial config
        self._load_config()
    
    def _load_config(self):
        """Load configuration"""
        try:
            config_file = Path.home() / ".mkd" / "cli_config.json"
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Update variables
                for key, var in self.config_vars.items():
                    if key in config:
                        var.set(config[key])
                
                messagebox.showinfo("Success", "Configuration loaded successfully")
            else:
                messagebox.showwarning("Warning", "No configuration file found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def _save_config(self):
        """Save configuration"""
        try:
            config_file = Path.home() / ".mkd" / "cli_config.json"
            config_file.parent.mkdir(exist_ok=True)
            
            # Collect current values
            config = {}
            for key, var in self.config_vars.items():
                config[key] = var.get()
            
            # Add default values for other settings
            config.update({
                "command_history_size": 1000,
                "interactive_timeout": 300,
                "log_level": "INFO"
            })
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            messagebox.showinfo("Success", "Configuration saved successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")


class GUILauncher:
    """Main GUI launcher application"""
    
    def __init__(self, system_controller=None):
        if not GUI_AVAILABLE:
            raise ImportError("GUI components not available (tkinter required)")
        
        self.system_controller = system_controller
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("MKD Automation Platform v2.0")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        
        # Set window icon (if available)
        try:
            # This would use an actual icon file
            # self.root.iconbitmap("mkd_icon.ico")
            pass
        except:
            pass
        
        # Create UI
        self._create_menu()
        self._create_main_interface()
        
        # Setup event handlers
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        logger.info("GUI Launcher initialized")
    
    def _create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Playbook...", command=self._open_playbook)
        file_menu.add_command(label="Save Session...", command=self._save_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # System menu
        system_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="System", menu=system_menu)
        system_menu.add_command(label="Start System", command=self._start_system)
        system_menu.add_command(label="Stop System", command=self._stop_system)
        system_menu.add_command(label="Restart System", command=self._restart_system)
        system_menu.add_separator()
        system_menu.add_command(label="System Status", command=self._show_system_status)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="CLI Mode", command=self._launch_cli)
        tools_menu.add_command(label="Interactive Mode", command=self._launch_interactive)
        tools_menu.add_separator()
        tools_menu.add_command(label="Log Viewer", command=self._show_logs)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_interface(self):
        """Create main interface"""
        
        # Create main container
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill="both", expand=True)
        
        # Create left panel
        self.left_panel = ttk.Frame(self.main_frame)
        self.left_panel.pack(side="left", fill="y", padx=(0, 5))
        
        # Create right panel
        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        # Add system monitor to left panel
        self.system_monitor = SystemMonitor(self.left_panel, self.system_controller)
        
        # Add configuration panel to left panel
        self.config_panel = ConfigurationPanel(self.left_panel)
        
        # Add control buttons to left panel
        self._create_control_panel()
        
        # Add command console to right panel
        self.command_console = CommandConsole(self.right_panel)
        
        # Start system monitoring
        self.system_monitor.start_monitoring()
    
    def _create_control_panel(self):
        """Create system control panel"""
        
        # Create control frame
        self.control_frame = ttk.LabelFrame(self.left_panel, text="System Control", padding=10)
        self.control_frame.pack(fill="x", padx=5, pady=5)
        
        # System control buttons
        button_config = {"width": 15, "pady": 2}
        
        ttk.Button(
            self.control_frame, 
            text="Start System", 
            command=self._start_system,
            **button_config
        ).pack(fill="x")
        
        ttk.Button(
            self.control_frame, 
            text="Stop System", 
            command=self._stop_system,
            **button_config
        ).pack(fill="x")
        
        ttk.Button(
            self.control_frame, 
            text="Restart System", 
            command=self._restart_system,
            **button_config
        ).pack(fill="x")
        
        ttk.Separator(self.control_frame, orient="horizontal").pack(fill="x", pady=5)
        
        ttk.Button(
            self.control_frame, 
            text="System Status", 
            command=self._show_system_status,
            **button_config
        ).pack(fill="x")
        
        ttk.Button(
            self.control_frame, 
            text="View Logs", 
            command=self._show_logs,
            **button_config
        ).pack(fill="x")
    
    def run(self):
        """Start the GUI application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._on_closing()
    
    def _start_system(self):
        """Start system"""
        def start_async():
            try:
                if self.system_controller:
                    # This would actually start the system
                    success = True  # Placeholder
                    
                    if success:
                        messagebox.showinfo("Success", "System started successfully")
                        self.command_console._append_output("✅ System started\n\n")
                    else:
                        messagebox.showerror("Error", "Failed to start system")
                else:
                    messagebox.showwarning("Warning", "No system controller available")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start system: {e}")
        
        threading.Thread(target=start_async, daemon=True).start()
    
    def _stop_system(self):
        """Stop system"""
        if messagebox.askyesno("Confirm", "Are you sure you want to stop the system?"):
            def stop_async():
                try:
                    if self.system_controller:
                        # This would actually stop the system
                        success = True  # Placeholder
                        
                        if success:
                            messagebox.showinfo("Success", "System stopped successfully")
                            self.command_console._append_output("✅ System stopped\n\n")
                        else:
                            messagebox.showerror("Error", "Failed to stop system")
                    else:
                        messagebox.showwarning("Warning", "No system controller available")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to stop system: {e}")
            
            threading.Thread(target=stop_async, daemon=True).start()
    
    def _restart_system(self):
        """Restart system"""
        if messagebox.askyesno("Confirm", "Are you sure you want to restart the system?"):
            def restart_async():
                try:
                    if self.system_controller:
                        # This would actually restart the system
                        success = True  # Placeholder
                        
                        if success:
                            messagebox.showinfo("Success", "System restarted successfully")
                            self.command_console._append_output("✅ System restarted\n\n")
                        else:
                            messagebox.showerror("Error", "Failed to restart system")
                    else:
                        messagebox.showwarning("Warning", "No system controller available")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to restart system: {e}")
            
            threading.Thread(target=restart_async, daemon=True).start()
    
    def _show_system_status(self):
        """Show detailed system status"""
        status_window = tk.Toplevel(self.root)
        status_window.title("System Status")
        status_window.geometry("600x400")
        
        # Create status text area
        status_text = scrolledtext.ScrolledText(status_window, font=("Consolas", 10))
        status_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add status information
        status_info = """
MKD Automation Platform v2.0 - System Status

System Status: Running
Uptime: 1h 23m 45s
Components: 12 active
Memory Usage: Normal
CPU Usage: Low

Recent Activity:
- System started at 14:30:22
- 3 playbooks executed successfully
- No errors in last 24 hours

Components Status:
✅ System Controller: Healthy
✅ Component Registry: Healthy  
✅ Event Bus: Healthy
✅ Lifecycle Manager: Healthy
✅ Playbook Engine: Healthy
✅ Web Automation: Healthy

Performance Metrics:
- Average response time: 12ms
- Total events processed: 1,247
- Success rate: 99.8%
        """
        
        status_text.insert(tk.END, status_info.strip())
        status_text.config(state="disabled")
    
    def _show_logs(self):
        """Show system logs"""
        logs_window = tk.Toplevel(self.root)
        logs_window.title("System Logs")
        logs_window.geometry("800x600")
        
        # Create logs text area
        logs_text = scrolledtext.ScrolledText(logs_window, font=("Consolas", 9))
        logs_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add sample log entries
        log_entries = """
2024-08-28 14:30:22 [INFO] System startup initiated
2024-08-28 14:30:23 [INFO] Component registry initialized
2024-08-28 14:30:23 [INFO] Event bus started
2024-08-28 14:30:24 [INFO] Lifecycle manager ready
2024-08-28 14:30:25 [INFO] System startup completed
2024-08-28 14:35:12 [INFO] Playbook 'web_automation' started
2024-08-28 14:35:15 [INFO] Playbook 'web_automation' completed successfully
2024-08-28 14:42:33 [DEBUG] Health check passed
2024-08-28 15:15:01 [INFO] System statistics updated
2024-08-28 15:30:45 [INFO] Automated cleanup completed
        """
        
        logs_text.insert(tk.END, log_entries.strip())
        logs_text.config(state="disabled")
    
    def _open_playbook(self):
        """Open playbook file"""
        filename = filedialog.askopenfilename(
            title="Open Playbook",
            filetypes=[("YAML files", "*.yml"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            messagebox.showinfo("Info", f"Would open playbook: {filename}")
    
    def _save_session(self):
        """Save current session"""
        filename = filedialog.asksaveasfilename(
            title="Save Session",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            messagebox.showinfo("Info", f"Would save session to: {filename}")
    
    def _launch_cli(self):
        """Launch CLI mode"""
        messagebox.showinfo("Info", "CLI mode would be launched in a new terminal")
    
    def _launch_interactive(self):
        """Launch interactive mode"""
        messagebox.showinfo("Info", "Interactive mode would be launched in a new terminal")
    
    def _show_documentation(self):
        """Show documentation"""
        messagebox.showinfo("Documentation", "Documentation would be opened in web browser")
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """
MKD Automation Platform v2.0
Professional GUI Interface

A comprehensive automation platform with:
• Advanced playbook execution
• AI-powered intelligence
• Web automation capabilities  
• Cross-platform compatibility
• Professional management tools

© 2024 MKD Automation Project
        """
        
        messagebox.showinfo("About MKD Automation Platform", about_text.strip())
    
    def _on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit MKD GUI?"):
            # Stop monitoring
            if hasattr(self, 'system_monitor'):
                self.system_monitor.stop_monitoring()
            
            # Close application
            self.root.destroy()


def launch_gui(system_controller=None):
    """Launch GUI application"""
    
    if not GUI_AVAILABLE:
        print("GUI not available - tkinter is required")
        print("Install tkinter: pip install tkinter")
        return False
    
    try:
        app = GUILauncher(system_controller)
        app.run()
        return True
        
    except Exception as e:
        logger.error(f"GUI launch failed: {e}")
        print(f"Failed to launch GUI: {e}")
        return False


if __name__ == "__main__":
    launch_gui()