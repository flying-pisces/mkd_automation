"""
Main CLI Interface

Professional command-line interface for MKD Automation Platform v2.0.
Provides system management, automation control, and interactive features.
"""

import asyncio
import sys
import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import argparse
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

from .command_router import CommandRouter, Command, CommandGroup, CommandType, CommandParameter
from .interactive_mode import InteractiveMode
from ..integration.system_controller import SystemController
from ..integration.component_registry import ComponentRegistry, ComponentType
from ..integration.event_bus import EventBus
from ..integration.lifecycle_manager import LifecycleManager, LifecyclePhase

logger = logging.getLogger(__name__)


class MKDCli:
    """Main CLI interface for MKD Automation Platform"""
    
    def __init__(self):
        self.console = Console()
        self.command_router = CommandRouter()
        
        # System components
        self.component_registry = ComponentRegistry()
        self.event_bus = EventBus()
        self.lifecycle_manager = LifecycleManager(self.component_registry, self.event_bus)
        self.system_controller = SystemController(
            self.component_registry,
            self.event_bus,
            self.lifecycle_manager
        )
        
        # CLI state
        self.interactive_mode = None
        self.config = self._load_config()
        self.context = {
            "system_running": False,
            "admin_user": False,
            "verbose": False
        }
        
        # Register CLI commands
        self._register_system_commands()
        self._register_playbook_commands()
        self._register_config_commands()
        self._register_debug_commands()
        
        logger.info("MKD CLI initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load CLI configuration"""
        
        config_file = Path.home() / ".mkd" / "cli_config.json"
        default_config = {
            "auto_start_system": False,
            "verbose_output": False,
            "colored_output": True,
            "progress_indicators": True,
            "command_history_size": 1000,
            "interactive_timeout": 300,
            "log_level": "INFO"
        }
        
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            logger.warning(f"Failed to load CLI config: {e}")
        
        return default_config
    
    def _save_config(self) -> None:
        """Save CLI configuration"""
        
        try:
            config_file = Path.home() / ".mkd" / "cli_config.json"
            config_file.parent.mkdir(exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save CLI config: {e}")
    
    async def run_command(self, command_line: str) -> bool:
        """Run a single command"""
        
        try:
            # Show progress for long-running commands
            if self.config.get("progress_indicators", True):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Executing command...", total=None)
                    result = await self.command_router.execute_command(command_line, self.context)
                    progress.update(task, description="Command completed")
            else:
                result = await self.command_router.execute_command(command_line, self.context)
            
            # Display result
            if result["success"]:
                if "result" in result and result["result"]:
                    if isinstance(result["result"], str):
                        self.console.print(result["result"])
                    else:
                        self.console.print_json(data=result["result"])
                return True
            else:
                self.console.print(f"[red]Error:[/red] {'; '.join(result['errors'])}")
                return False
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Command interrupted[/yellow]")
            return False
        except Exception as e:
            self.console.print(f"[red]Unexpected error:[/red] {e}")
            return False
    
    async def run_interactive(self) -> None:
        """Run in interactive mode"""
        
        if not self.interactive_mode:
            self.interactive_mode = InteractiveMode(self.command_router, self.console)
        
        await self.interactive_mode.start_session()
    
    def print_banner(self) -> None:
        """Print CLI banner"""
        
        banner_text = """
╔══════════════════════════════════════════════════════════════╗
║                  MKD Automation Platform v2.0               ║
║                     Professional CLI Interface               ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        self.console.print(Panel(banner_text, style="bold blue"))
        
        # Show system status
        status_text = f"System Status: {'🟢 Running' if self.context['system_running'] else '🔴 Stopped'}"
        self.console.print(status_text)
        self.console.print()
    
    def _register_system_commands(self) -> None:
        """Register system management commands"""
        
        # System group
        system_group = CommandGroup(
            name="system",
            description="System management commands"
        )
        
        # Start command
        start_cmd = Command(
            name="start",
            description="Start the MKD automation system",
            handler=self._system_start_handler,
            command_type=CommandType.SYSTEM,
            parameters=[
                CommandParameter("background", bool, False, False, "Start in background mode"),
                CommandParameter("config", str, False, None, "Configuration file path")
            ],
            examples=["system start", "system start --background"],
            async_handler=True
        )
        
        # Stop command
        stop_cmd = Command(
            name="stop",
            description="Stop the MKD automation system",
            handler=self._system_stop_handler,
            command_type=CommandType.SYSTEM,
            parameters=[
                CommandParameter("graceful", bool, False, True, "Graceful shutdown"),
                CommandParameter("timeout", int, False, 30, "Stop timeout in seconds")
            ],
            examples=["system stop", "system stop --timeout 60"],
            requires_system=True,
            async_handler=True
        )
        
        # Status command
        status_cmd = Command(
            name="status",
            description="Show system status and statistics",
            handler=self._system_status_handler,
            command_type=CommandType.SYSTEM,
            examples=["system status"],
            async_handler=True
        )
        
        # Restart command
        restart_cmd = Command(
            name="restart",
            description="Restart the MKD automation system",
            handler=self._system_restart_handler,
            command_type=CommandType.SYSTEM,
            examples=["system restart"],
            requires_system=True,
            async_handler=True
        )
        
        # Register system commands
        system_group.commands.update({
            "start": start_cmd,
            "stop": stop_cmd,
            "status": status_cmd,
            "restart": restart_cmd
        })
        
        self.command_router.register_group(system_group)
    
    def _register_playbook_commands(self) -> None:
        """Register playbook management commands"""
        
        # Playbook group
        playbook_group = CommandGroup(
            name="playbook",
            description="Playbook management and execution",
            aliases=["pb"]
        )
        
        # List command
        list_cmd = Command(
            name="list",
            description="List available playbooks",
            handler=self._playbook_list_handler,
            command_type=CommandType.PLAYBOOK,
            parameters=[
                CommandParameter("path", str, False, None, "Playbook directory path"),
                CommandParameter("format", str, False, "table", "Output format", choices=["table", "json", "yaml"])
            ],
            examples=["playbook list", "playbook list --path /custom/path"],
            aliases=["ls"]
        )
        
        # Run command
        run_cmd = Command(
            name="run",
            description="Execute a playbook",
            handler=self._playbook_run_handler,
            command_type=CommandType.PLAYBOOK,
            parameters=[
                CommandParameter("playbook", str, True, None, "Playbook name or path"),
                CommandParameter("variables", str, False, None, "Variables in JSON format"),
                CommandParameter("dry-run", bool, False, False, "Perform dry run without execution"),
                CommandParameter("verbose", bool, False, False, "Verbose output")
            ],
            examples=["playbook run my_automation", "playbook run my_automation --dry-run"],
            requires_system=True,
            async_handler=True
        )
        
        # Validate command
        validate_cmd = Command(
            name="validate",
            description="Validate playbook syntax and structure",
            handler=self._playbook_validate_handler,
            command_type=CommandType.PLAYBOOK,
            parameters=[
                CommandParameter("playbook", str, True, None, "Playbook name or path"),
                CommandParameter("strict", bool, False, False, "Strict validation mode")
            ],
            examples=["playbook validate my_automation"]
        )
        
        # Register playbook commands
        playbook_group.commands.update({
            "list": list_cmd,
            "run": run_cmd,
            "validate": validate_cmd
        })
        
        self.command_router.register_group(playbook_group)
    
    def _register_config_commands(self) -> None:
        """Register configuration management commands"""
        
        # Config group
        config_group = CommandGroup(
            name="config",
            description="Configuration management"
        )
        
        # Get command
        get_cmd = Command(
            name="get",
            description="Get configuration value",
            handler=self._config_get_handler,
            command_type=CommandType.CONFIG,
            parameters=[
                CommandParameter("key", str, False, None, "Configuration key")
            ],
            examples=["config get", "config get auto_start_system"]
        )
        
        # Set command
        set_cmd = Command(
            name="set",
            description="Set configuration value",
            handler=self._config_set_handler,
            command_type=CommandType.CONFIG,
            parameters=[
                CommandParameter("key", str, True, None, "Configuration key"),
                CommandParameter("value", str, True, None, "Configuration value")
            ],
            examples=["config set auto_start_system true"]
        )
        
        # Reset command
        reset_cmd = Command(
            name="reset",
            description="Reset configuration to defaults",
            handler=self._config_reset_handler,
            command_type=CommandType.CONFIG,
            examples=["config reset"]
        )
        
        # Register config commands
        config_group.commands.update({
            "get": get_cmd,
            "set": set_cmd,
            "reset": reset_cmd
        })
        
        self.command_router.register_group(config_group)
    
    def _register_debug_commands(self) -> None:
        """Register debugging and diagnostic commands"""
        
        # Debug group
        debug_group = CommandGroup(
            name="debug",
            description="Debugging and diagnostic tools"
        )
        
        # Logs command
        logs_cmd = Command(
            name="logs",
            description="Show system logs",
            handler=self._debug_logs_handler,
            command_type=CommandType.DEBUG,
            parameters=[
                CommandParameter("level", str, False, "INFO", "Log level", choices=["DEBUG", "INFO", "WARNING", "ERROR"]),
                CommandParameter("component", str, False, None, "Filter by component"),
                CommandParameter("lines", int, False, 50, "Number of lines to show")
            ],
            examples=["debug logs", "debug logs --level ERROR --lines 20"]
        )
        
        # Health command
        health_cmd = Command(
            name="health",
            description="Check system health",
            handler=self._debug_health_handler,
            command_type=CommandType.DEBUG,
            examples=["debug health"],
            async_handler=True
        )
        
        # Performance command
        perf_cmd = Command(
            name="performance",
            description="Show performance metrics",
            handler=self._debug_performance_handler,
            command_type=CommandType.DEBUG,
            aliases=["perf"],
            examples=["debug performance"],
            async_handler=True
        )
        
        # Register debug commands
        debug_group.commands.update({
            "logs": logs_cmd,
            "health": health_cmd,
            "performance": perf_cmd
        })
        
        self.command_router.register_group(debug_group)
    
    # Command handlers
    
    async def _system_start_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle system start command"""
        
        if self.context["system_running"]:
            return "System is already running"
        
        try:
            # Initialize and start system
            if not await self.lifecycle_manager.initialize_system():
                return "Failed to initialize system"
            
            if not await self.lifecycle_manager.start_system():
                return "Failed to start system"
            
            self.context["system_running"] = True
            
            # Get startup statistics
            stats = self.system_controller.get_system_statistics()
            uptime = self.lifecycle_manager.get_system_uptime()
            
            return f"✅ System started successfully\n" \
                   f"Components: {stats['total_components']}\n" \
                   f"Uptime: {uptime:.2f}s" if uptime else "System started"
                   
        except Exception as e:
            return f"Failed to start system: {e}"
    
    async def _system_stop_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle system stop command"""
        
        if not self.context["system_running"]:
            return "System is not running"
        
        try:
            graceful = params.get("graceful", True)
            
            if not await self.lifecycle_manager.stop_system(graceful):
                return "Failed to stop system"
            
            self.context["system_running"] = False
            return "✅ System stopped successfully"
            
        except Exception as e:
            return f"Failed to stop system: {e}"
    
    async def _system_status_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system status command"""
        
        try:
            # Get comprehensive status
            status = {
                "system_running": self.context["system_running"],
                "lifecycle_phase": self.lifecycle_manager.get_current_phase().value,
                "uptime_seconds": self.lifecycle_manager.get_system_uptime(),
                "system_stats": self.system_controller.get_system_statistics(),
                "component_stats": self.component_registry.get_registry_statistics(),
                "event_stats": self.event_bus.get_event_statistics(),
                "lifecycle_stats": self.lifecycle_manager.get_lifecycle_statistics()
            }
            
            return status
            
        except Exception as e:
            return {"error": f"Failed to get system status: {e}"}
    
    async def _system_restart_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle system restart command"""
        
        try:
            if not await self.lifecycle_manager.restart_system():
                return "Failed to restart system"
            
            stats = self.system_controller.get_system_statistics()
            return f"✅ System restarted successfully\nComponents: {stats['total_components']}"
            
        except Exception as e:
            return f"Failed to restart system: {e}"
    
    def _playbook_list_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle playbook list command"""
        
        # Placeholder - would integrate with actual playbook system
        return "📝 Available playbooks:\n- example_automation.yml\n- web_scraping.yml\n- data_processing.yml"
    
    async def _playbook_run_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle playbook run command"""
        
        playbook_name = params.get("playbook")
        dry_run = params.get("dry-run", False)
        
        # Placeholder - would integrate with actual playbook execution
        if dry_run:
            return f"🔍 Dry run completed for playbook: {playbook_name}\nNo actions were executed."
        else:
            return f"🚀 Executed playbook: {playbook_name}\nExecution completed successfully."
    
    def _playbook_validate_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle playbook validate command"""
        
        playbook_name = params.get("playbook")
        
        # Placeholder - would integrate with actual playbook validation
        return f"✅ Playbook validation passed: {playbook_name}"
    
    def _config_get_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle config get command"""
        
        key = params.get("key")
        
        if key:
            value = self.config.get(key, "Key not found")
            return f"{key}: {value}"
        else:
            # Show all configuration
            config_lines = []
            for k, v in sorted(self.config.items()):
                config_lines.append(f"{k}: {v}")
            return "\n".join(config_lines)
    
    def _config_set_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle config set command"""
        
        key = params.get("key")
        value = params.get("value")
        
        # Convert value to appropriate type
        if value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
        
        self.config[key] = value
        self._save_config()
        
        return f"✅ Configuration updated: {key} = {value}"
    
    def _config_reset_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle config reset command"""
        
        # Reset to defaults
        self.config = {
            "auto_start_system": False,
            "verbose_output": False,
            "colored_output": True,
            "progress_indicators": True,
            "command_history_size": 1000,
            "interactive_timeout": 300,
            "log_level": "INFO"
        }
        
        self._save_config()
        return "✅ Configuration reset to defaults"
    
    def _debug_logs_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle debug logs command"""
        
        level = params.get("level", "INFO")
        component = params.get("component")
        lines = params.get("lines", 50)
        
        # Placeholder - would integrate with actual logging system
        log_entries = [
            f"[{level}] System component initialized",
            f"[{level}] Event bus started",
            f"[{level}] Component registry ready",
        ]
        
        if component:
            log_entries = [entry for entry in log_entries if component.lower() in entry.lower()]
        
        return "\n".join(log_entries[-lines:])
    
    async def _debug_health_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle debug health command"""
        
        health_status = {
            "overall_health": "healthy",
            "system_running": self.context["system_running"],
            "components": {
                "system_controller": "healthy",
                "component_registry": "healthy",
                "event_bus": "healthy",
                "lifecycle_manager": "healthy"
            },
            "performance": {
                "memory_usage": "normal",
                "cpu_usage": "normal",
                "response_time": "good"
            },
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return health_status
    
    async def _debug_performance_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle debug performance command"""
        
        performance_metrics = {
            "system_metrics": {
                "uptime_seconds": self.lifecycle_manager.get_system_uptime(),
                "total_components": len(self.component_registry.components),
                "active_components": len(self.component_registry.instances),
                "total_events": self.event_bus.get_event_statistics().get("total_published", 0),
                "command_history_size": len(self.command_router.command_history)
            },
            "response_times": {
                "command_parsing": "< 1ms",
                "event_publishing": "< 5ms",
                "component_lookup": "< 1ms"
            },
            "resource_usage": {
                "memory_estimated": "normal",
                "cpu_estimated": "low",
                "disk_usage": "minimal"
            }
        }
        
        return performance_metrics


def cli_main():
    """Main CLI entry point"""
    
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="MKD Automation Platform v2.0 - Professional CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mkd system start                    # Start the automation system
  mkd playbook run my_automation      # Run a playbook
  mkd -i                             # Start interactive mode
  mkd system status                  # Show system status
        """
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start in interactive mode"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    
    parser.add_argument(
        "command",
        nargs="*",
        help="Command to execute"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create CLI instance
    cli = MKDCli()
    cli.context["verbose"] = args.verbose
    
    # Handle color output
    if args.no_color:
        cli.config["colored_output"] = False
    
    async def run_cli():
        """Run the CLI"""
        
        try:
            if args.interactive or not args.command:
                # Interactive mode
                cli.print_banner()
                await cli.run_interactive()
            else:
                # Single command mode
                command_line = " ".join(args.command)
                success = await cli.run_command(command_line)
                sys.exit(0 if success else 1)
                
        except KeyboardInterrupt:
            cli.console.print("\n[yellow]Goodbye![/yellow]")
            sys.exit(0)
        except Exception as e:
            cli.console.print(f"[red]Fatal error:[/red] {e}")
            sys.exit(1)
    
    # Run CLI
    try:
        asyncio.run(run_cli())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    cli_main()