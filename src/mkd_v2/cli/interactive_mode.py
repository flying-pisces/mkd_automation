"""
Interactive Mode

REPL-style interactive interface for complex workflows and exploration.
Provides command completion, history, and enhanced user experience.
"""

import asyncio
import sys
import os
from typing import Dict, Any, Optional, List
try:
    import readline
except ImportError:
    # Windows compatibility - readline not available
    readline = None
import atexit
from pathlib import Path
import json
import time
import logging
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.syntax import Syntax
from rich.text import Text

from .command_router import CommandRouter

logger = logging.getLogger(__name__)


class InteractiveSession:
    """Interactive session state and management"""
    
    def __init__(self, console: Console):
        self.console = console
        self.session_id = f"session_{int(time.time())}"
        self.start_time = time.time()
        self.command_count = 0
        self.variables = {}
        self.bookmarks = {}
        self.session_history = []
        
        # Session configuration
        self.config = {
            "prompt_style": "mkd",
            "auto_complete": True,
            "history_size": 500,
            "timeout": 1800,  # 30 minutes
            "save_session": True
        }
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        
        duration = time.time() - self.start_time
        return {
            "session_id": self.session_id,
            "duration_seconds": duration,
            "commands_executed": self.command_count,
            "variables_set": len(self.variables),
            "bookmarks": len(self.bookmarks)
        }
    
    def add_variable(self, name: str, value: Any) -> None:
        """Add session variable"""
        self.variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        """Get session variable"""
        return self.variables.get(name)
    
    def add_bookmark(self, name: str, command: str) -> None:
        """Add command bookmark"""
        self.bookmarks[name] = command
    
    def get_bookmark(self, name: str) -> Optional[str]:
        """Get bookmarked command"""
        return self.bookmarks.get(name)


class InteractiveMode:
    """Interactive REPL interface for MKD CLI"""
    
    def __init__(self, command_router: CommandRouter, console: Console):
        self.command_router = command_router
        self.console = console
        self.session = None
        
        # History management
        self.history_file = Path.home() / ".mkd" / "cli_history"
        self.history_file.parent.mkdir(exist_ok=True)
        
        # Command completion
        self.completion_cache = {}
        
        # Setup readline if available
        self._setup_readline()
        
        logger.info("InteractiveMode initialized")
    
    def _setup_readline(self) -> None:
        """Setup readline for command history and completion"""
        
        if readline is None:
            # Readline not available on Windows
            logger.debug("Readline not available, completion disabled")
            return
        
        try:
            # Load command history
            if self.history_file.exists():
                readline.read_history_file(str(self.history_file))
            
            # Set history size
            readline.set_history_length(500)
            
            # Setup completion
            readline.set_completer(self._complete_command)
            readline.parse_and_bind("tab: complete")
            
            # Save history on exit
            atexit.register(self._save_history)
            
        except Exception as e:
            # Readline setup failed
            logger.debug(f"Readline setup failed: {e}")
    
    def _save_history(self) -> None:
        """Save command history to file"""
        
        if readline is None:
            return
        
        try:
            readline.write_history_file(str(self.history_file))
        except Exception as e:
            logger.debug(f"Failed to save history: {e}")
    
    def _complete_command(self, text: str, state: int) -> Optional[str]:
        """Command completion handler"""
        
        if readline is None:
            return None
        
        try:
            if state == 0:
                # Get current line
                line = readline.get_line_buffer()
                
                # Get completions from command router
                completions = self.command_router.get_command_completion(line)
                
                # Filter completions based on current text
                self.completion_matches = [
                    comp for comp in completions
                    if comp.startswith(text)
                ]
            
            if state < len(self.completion_matches):
                return self.completion_matches[state]
            
            return None
            
        except Exception as e:
            logger.debug(f"Command completion failed: {e}")
            return None
    
    async def start_session(self) -> None:
        """Start interactive session"""
        
        self.session = InteractiveSession(self.console)
        
        # Welcome message
        self._show_welcome()
        
        # Register session commands
        self._register_session_commands()
        
        try:
            # Main command loop
            while True:
                try:
                    # Get command input
                    prompt_text = self._get_prompt()
                    command_line = await self._get_user_input(prompt_text)
                    
                    if not command_line:
                        continue
                    
                    # Handle special commands
                    if await self._handle_special_commands(command_line):
                        continue
                    
                    # Execute command
                    await self._execute_interactive_command(command_line)
                    
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]Use 'exit' or Ctrl+D to quit[/yellow]")
                    continue
                except EOFError:
                    break
        
        except Exception as e:
            self.console.print(f"[red]Session error:[/red] {e}")
        
        finally:
            await self._end_session()
    
    def _show_welcome(self) -> None:
        """Show interactive mode welcome message"""
        
        welcome_text = """
🎯 Interactive Mode Active

Type 'help' for available commands
Type 'exit' or press Ctrl+D to quit
Use Tab for command completion

Session Commands:
  .vars          - Show session variables
  .bookmarks     - Show command bookmarks  
  .session       - Show session info
  .save          - Save current session
        """
        
        self.console.print(Panel(welcome_text, title="Welcome", style="bold green"))
    
    def _get_prompt(self) -> str:
        """Get command prompt text"""
        
        if self.session.config.get("prompt_style") == "simple":
            return "mkd> "
        elif self.session.config.get("prompt_style") == "detailed":
            return f"mkd[{self.session.command_count}]> "
        else:
            return "mkd ❯ "
    
    async def _get_user_input(self, prompt: str) -> str:
        """Get user input with async handling"""
        
        try:
            # Use asyncio to handle input without blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, input, prompt)
        except EOFError:
            raise
        except KeyboardInterrupt:
            raise
    
    async def _handle_special_commands(self, command_line: str) -> bool:
        """Handle special interactive commands"""
        
        command_line = command_line.strip()
        
        if command_line.startswith('.'):
            # Session command
            parts = command_line[1:].split()
            session_cmd = parts[0] if parts else ""
            
            if session_cmd == "vars":
                await self._show_variables()
            elif session_cmd == "bookmarks":
                await self._show_bookmarks()
            elif session_cmd == "session":
                await self._show_session_info()
            elif session_cmd == "save":
                await self._save_session()
            elif session_cmd == "load":
                session_name = parts[1] if len(parts) > 1 else None
                await self._load_session(session_name)
            elif session_cmd == "set":
                if len(parts) >= 3:
                    var_name = parts[1]
                    var_value = " ".join(parts[2:])
                    self.session.add_variable(var_name, var_value)
                    self.console.print(f"✅ Variable set: {var_name} = {var_value}")
            elif session_cmd == "bookmark":
                if len(parts) >= 3:
                    bookmark_name = parts[1]
                    bookmark_cmd = " ".join(parts[2:])
                    self.session.add_bookmark(bookmark_name, bookmark_cmd)
                    self.console.print(f"✅ Bookmark saved: {bookmark_name}")
            else:
                self.console.print(f"Unknown session command: .{session_cmd}")
            
            return True
        
        elif command_line.lower() in ['exit', 'quit', 'bye']:
            # Exit command
            raise EOFError()
        
        elif command_line.startswith('@'):
            # Bookmark execution
            bookmark_name = command_line[1:]
            bookmark_cmd = self.session.get_bookmark(bookmark_name)
            
            if bookmark_cmd:
                self.console.print(f"📖 Executing bookmark '{bookmark_name}': {bookmark_cmd}")
                await self._execute_interactive_command(bookmark_cmd)
            else:
                self.console.print(f"❌ Bookmark not found: {bookmark_name}")
            
            return True
        
        elif command_line.startswith('$'):
            # Variable substitution
            var_name = command_line[1:]
            var_value = self.session.get_variable(var_name)
            
            if var_value is not None:
                self.console.print(f"{var_name}: {var_value}")
            else:
                self.console.print(f"❌ Variable not found: {var_name}")
            
            return True
        
        return False
    
    async def _execute_interactive_command(self, command_line: str) -> None:
        """Execute command in interactive context"""
        
        # Variable substitution
        command_line = self._substitute_variables(command_line)
        
        # Add to session history
        self.session.session_history.append({
            "command": command_line,
            "timestamp": time.time()
        })
        
        # Execute command
        result = await self.command_router.execute_command(
            command_line,
            {"interactive_session": self.session}
        )
        
        self.session.command_count += 1
        
        # Display result
        if result["success"]:
            if "result" in result and result["result"]:
                if isinstance(result["result"], str):
                    self.console.print(result["result"])
                elif isinstance(result["result"], dict):
                    self._display_json_result(result["result"])
                else:
                    self.console.print(str(result["result"]))
        else:
            self.console.print(f"[red]Error:[/red] {'; '.join(result['errors'])}")
    
    def _substitute_variables(self, command_line: str) -> str:
        """Substitute session variables in command line"""
        
        for var_name, var_value in self.session.variables.items():
            placeholder = f"${var_name}"
            command_line = command_line.replace(placeholder, str(var_value))
        
        return command_line
    
    def _display_json_result(self, data: Dict[str, Any]) -> None:
        """Display JSON result with syntax highlighting"""
        
        try:
            json_str = json.dumps(data, indent=2)
            syntax = Syntax(json_str, "json", theme="monokai")
            self.console.print(syntax)
        except Exception:
            # Fallback to simple print
            self.console.print_json(data=data)
    
    async def _show_variables(self) -> None:
        """Show session variables"""
        
        if not self.session.variables:
            self.console.print("No session variables set")
            return
        
        table = Table(title="Session Variables")
        table.add_column("Name", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Type", style="dim")
        
        for name, value in self.session.variables.items():
            table.add_row(name, str(value), type(value).__name__)
        
        self.console.print(table)
    
    async def _show_bookmarks(self) -> None:
        """Show command bookmarks"""
        
        if not self.session.bookmarks:
            self.console.print("No command bookmarks saved")
            return
        
        table = Table(title="Command Bookmarks")
        table.add_column("Name", style="cyan")
        table.add_column("Command", style="green")
        
        for name, command in self.session.bookmarks.items():
            table.add_row(name, command)
        
        self.console.print(table)
    
    async def _show_session_info(self) -> None:
        """Show session information"""
        
        info = self.session.get_session_info()
        duration_min = info["duration_seconds"] / 60
        
        table = Table(title="Session Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Session ID", info["session_id"])
        table.add_row("Duration", f"{duration_min:.1f} minutes")
        table.add_row("Commands Executed", str(info["commands_executed"]))
        table.add_row("Variables Set", str(info["variables_set"]))
        table.add_row("Bookmarks", str(info["bookmarks"]))
        
        self.console.print(table)
    
    async def _save_session(self) -> None:
        """Save current session to file"""
        
        try:
            session_dir = Path.home() / ".mkd" / "sessions"
            session_dir.mkdir(exist_ok=True)
            
            session_file = session_dir / f"{self.session.session_id}.json"
            session_data = {
                "session_info": self.session.get_session_info(),
                "variables": self.session.variables,
                "bookmarks": self.session.bookmarks,
                "history": self.session.session_history[-50:],  # Save last 50 commands
                "config": self.session.config
            }
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            self.console.print(f"✅ Session saved to {session_file}")
            
        except Exception as e:
            self.console.print(f"❌ Failed to save session: {e}")
    
    async def _load_session(self, session_name: Optional[str] = None) -> None:
        """Load session from file"""
        
        try:
            session_dir = Path.home() / ".mkd" / "sessions"
            
            if session_name:
                session_file = session_dir / f"{session_name}.json"
            else:
                # List available sessions
                session_files = list(session_dir.glob("*.json"))
                if not session_files:
                    self.console.print("No saved sessions found")
                    return
                
                # Show available sessions
                table = Table(title="Available Sessions")
                table.add_column("Name", style="cyan")
                table.add_column("Date", style="green")
                
                for file in session_files:
                    name = file.stem
                    date = time.ctime(file.stat().st_mtime)
                    table.add_row(name, date)
                
                self.console.print(table)
                return
            
            if not session_file.exists():
                self.console.print(f"Session not found: {session_name}")
                return
            
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Restore session state
            self.session.variables.update(session_data.get("variables", {}))
            self.session.bookmarks.update(session_data.get("bookmarks", {}))
            self.session.config.update(session_data.get("config", {}))
            
            self.console.print(f"✅ Session loaded: {session_name}")
            
        except Exception as e:
            self.console.print(f"❌ Failed to load session: {e}")
    
    async def _end_session(self) -> None:
        """End interactive session"""
        
        # Show session summary
        info = self.session.get_session_info()
        duration_min = info["duration_seconds"] / 60
        
        summary = f"""
Session Summary:
- Duration: {duration_min:.1f} minutes
- Commands executed: {info['commands_executed']}
- Variables set: {info['variables_set']}
- Bookmarks: {info['bookmarks']}
        """
        
        self.console.print(Panel(summary, title="Session Ended", style="dim"))
        
        # Auto-save session if configured
        if self.session.config.get("save_session") and self.session.command_count > 0:
            await self._save_session()
        
        self.console.print("[dim]Goodbye![/dim]")
    
    def _register_session_commands(self) -> None:
        """Register session-specific commands"""
        
        # These would be additional commands specific to interactive mode
        # For now, they're handled in _handle_special_commands
        pass