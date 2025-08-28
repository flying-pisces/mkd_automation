"""
Command Router

Professional command routing and validation system.
Provides structured command hierarchy with help and completion.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
import inspect
import shlex
import re
import logging

logger = logging.getLogger(__name__)


class CommandType(Enum):
    """Types of commands"""
    SYSTEM = "system"       # System management commands
    PLAYBOOK = "playbook"   # Playbook operations
    RECORD = "record"       # Recording operations
    WEB = "web"            # Web automation
    AI = "ai"              # AI/Intelligence operations
    CONFIG = "config"       # Configuration management
    DEBUG = "debug"         # Debugging and diagnostics
    UTIL = "util"          # Utility commands


class ValidationLevel(Enum):
    """Command validation levels"""
    NONE = "none"          # No validation
    BASIC = "basic"        # Basic parameter validation
    STRICT = "strict"      # Strict validation with type checking
    SECURITY = "security"  # Security-focused validation


@dataclass
class CommandParameter:
    """Command parameter definition"""
    name: str
    param_type: type = str
    required: bool = False
    default: Any = None
    description: str = ""
    validation_pattern: Optional[str] = None
    choices: Optional[List[str]] = None
    sensitive: bool = False  # For passwords, tokens, etc.
    
    def validate(self, value: Any) -> tuple[bool, str]:
        """Validate parameter value"""
        try:
            # Type validation
            if value is not None:
                if self.param_type == bool and isinstance(value, str):
                    # Handle boolean string conversion
                    if value.lower() in ('true', '1', 'yes', 'on'):
                        value = True
                    elif value.lower() in ('false', '0', 'no', 'off'):
                        value = False
                    else:
                        return False, f"Invalid boolean value: {value}"
                else:
                    # Try to convert to target type
                    value = self.param_type(value)
            
            # Required validation
            if self.required and value is None:
                return False, f"Required parameter '{self.name}' is missing"
            
            # Pattern validation
            if self.validation_pattern and value is not None:
                if not re.match(self.validation_pattern, str(value)):
                    return False, f"Parameter '{self.name}' doesn't match required pattern"
            
            # Choices validation
            if self.choices and value is not None:
                if str(value) not in self.choices:
                    return False, f"Parameter '{self.name}' must be one of: {', '.join(self.choices)}"
            
            return True, ""
            
        except (ValueError, TypeError) as e:
            return False, f"Invalid value for parameter '{self.name}': {e}"


@dataclass
class Command:
    """Command definition"""
    name: str
    description: str
    handler: Callable
    command_type: CommandType = CommandType.UTIL
    parameters: List[CommandParameter] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    validation_level: ValidationLevel = ValidationLevel.BASIC
    requires_system: bool = False  # Requires system to be running
    admin_only: bool = False
    async_handler: bool = False
    hidden: bool = False  # Hidden from help listings
    deprecated: bool = False
    replacement: Optional[str] = None
    
    def validate_parameters(self, params: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate all command parameters"""
        errors = []
        
        # Validate each defined parameter
        for param in self.parameters:
            value = params.get(param.name)
            is_valid, error = param.validate(value)
            
            if not is_valid:
                errors.append(error)
        
        # Check for unknown parameters in strict mode
        if self.validation_level == ValidationLevel.STRICT:
            known_params = {p.name for p in self.parameters}
            unknown_params = set(params.keys()) - known_params
            
            if unknown_params:
                errors.extend([f"Unknown parameter: {p}" for p in unknown_params])
        
        return len(errors) == 0, errors


@dataclass
class CommandGroup:
    """Command group for organizing related commands"""
    name: str
    description: str
    commands: Dict[str, Command] = field(default_factory=dict)
    subgroups: Dict[str, 'CommandGroup'] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    hidden: bool = False


class CommandRouter:
    """Professional command routing and management system"""
    
    def __init__(self):
        self.root_group = CommandGroup("root", "Root command group")
        self.command_history: List[str] = []
        self.command_aliases: Dict[str, str] = {}
        
        # Built-in commands
        self._register_builtin_commands()
        
        logger.info("CommandRouter initialized")
    
    def register_command(self, command: Command, group_path: str = "") -> bool:
        """Register a command in the specified group"""
        
        try:
            # Navigate to target group
            target_group = self._get_or_create_group(group_path)
            
            # Register command
            target_group.commands[command.name] = command
            
            # Register aliases
            for alias in command.aliases:
                if alias in self.command_aliases:
                    logger.warning(f"Command alias '{alias}' already exists, overriding")
                self.command_aliases[alias] = f"{group_path}.{command.name}" if group_path else command.name
            
            logger.debug(f"Registered command: {group_path}.{command.name}" if group_path else command.name)
            return True
            
        except Exception as e:
            logger.error(f"Failed to register command {command.name}: {e}")
            return False
    
    def register_group(self, group: CommandGroup, parent_path: str = "") -> bool:
        """Register a command group"""
        
        try:
            # Navigate to parent group
            parent_group = self._get_or_create_group(parent_path)
            
            # Register group
            parent_group.subgroups[group.name] = group
            
            # Register aliases
            for alias in group.aliases:
                self.command_aliases[alias] = f"{parent_path}.{group.name}" if parent_path else group.name
            
            logger.debug(f"Registered command group: {parent_path}.{group.name}" if parent_path else group.name)
            return True
            
        except Exception as e:
            logger.error(f"Failed to register command group {group.name}: {e}")
            return False
    
    def parse_command(self, command_line: str) -> tuple[Optional[Command], Dict[str, Any], List[str]]:
        """Parse command line into command and parameters"""
        
        try:
            # Tokenize command line
            tokens = shlex.split(command_line.strip())
            
            if not tokens:
                return None, {}, ["Empty command"]
            
            # Resolve command path
            command_path = tokens[0]
            
            # Check for alias
            if command_path in self.command_aliases:
                command_path = self.command_aliases[command_path]
            
            # Find command
            command = self._find_command(command_path)
            if not command:
                return None, {}, [f"Unknown command: {tokens[0]}"]
            
            # Parse parameters
            params = {}
            errors = []
            
            i = 1
            while i < len(tokens):
                token = tokens[i]
                
                if token.startswith('--'):
                    # Long parameter (--name=value or --name value)
                    if '=' in token:
                        param_name = token[2:].split('=', 1)[0]
                        param_value = token.split('=', 1)[1]
                    else:
                        param_name = token[2:]
                        if i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                            param_value = tokens[i + 1]
                            i += 1
                        else:
                            param_value = True  # Boolean flag
                    
                    params[param_name] = param_value
                
                elif token.startswith('-'):
                    # Short parameter (-n value or -n)
                    param_name = token[1:]
                    if i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                        param_value = tokens[i + 1]
                        i += 1
                    else:
                        param_value = True  # Boolean flag
                    
                    params[param_name] = param_value
                
                else:
                    # Positional parameter - map to first unnamed parameter
                    positional_params = [p for p in command.parameters if not p.name.startswith('-')]
                    if positional_params:
                        param_name = positional_params[0].name
                        params[param_name] = token
                    else:
                        errors.append(f"Unexpected positional argument: {token}")
                
                i += 1
            
            # Validate parameters
            is_valid, validation_errors = command.validate_parameters(params)
            if not is_valid:
                errors.extend(validation_errors)
            
            return command, params, errors
            
        except Exception as e:
            return None, {}, [f"Failed to parse command: {e}"]
    
    async def execute_command(self, command_line: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a command"""
        
        # Add to history
        self.command_history.append(command_line)
        
        # Parse command
        command, params, errors = self.parse_command(command_line)
        
        if errors:
            return {
                "success": False,
                "errors": errors,
                "command": command_line
            }
        
        if not command:
            return {
                "success": False,
                "errors": ["Command not found"],
                "command": command_line
            }
        
        try:
            # Check system requirements
            if command.requires_system and context and not context.get("system_running"):
                return {
                    "success": False,
                    "errors": ["Command requires system to be running"],
                    "command": command_line
                }
            
            # Check admin requirements
            if command.admin_only and context and not context.get("admin_user"):
                return {
                    "success": False,
                    "errors": ["Command requires administrator privileges"],
                    "command": command_line
                }
            
            # Execute command
            if command.async_handler:
                result = await command.handler(params, context or {})
            else:
                result = command.handler(params, context or {})
            
            return {
                "success": True,
                "result": result,
                "command": command_line
            }
            
        except Exception as e:
            logger.error(f"Command execution failed: {command_line}: {e}")
            return {
                "success": False,
                "errors": [f"Execution error: {e}"],
                "command": command_line
            }
    
    def get_command_help(self, command_path: str = None) -> str:
        """Generate help text for command or group"""
        
        if not command_path:
            return self._generate_group_help(self.root_group, "")
        
        # Try to find command first
        command = self._find_command(command_path)
        if command:
            return self._generate_command_help(command)
        
        # Try to find group
        group = self._find_group(command_path)
        if group:
            return self._generate_group_help(group, command_path)
        
        return f"No help available for: {command_path}"
    
    def get_command_completion(self, partial_command: str) -> List[str]:
        """Get command completion suggestions"""
        
        try:
            tokens = shlex.split(partial_command)
            
            if not tokens:
                # Return top-level commands and groups
                completions = []
                completions.extend(self.root_group.commands.keys())
                completions.extend(self.root_group.subgroups.keys())
                completions.extend(self.command_aliases.keys())
                return sorted(completions)
            
            if len(tokens) == 1 and not partial_command.endswith(' '):
                # Complete command name
                prefix = tokens[0].lower()
                completions = []
                
                # Check commands
                for name in self.root_group.commands:
                    if name.lower().startswith(prefix):
                        completions.append(name)
                
                # Check groups
                for name in self.root_group.subgroups:
                    if name.lower().startswith(prefix):
                        completions.append(name)
                
                # Check aliases
                for alias in self.command_aliases:
                    if alias.lower().startswith(prefix):
                        completions.append(alias)
                
                return sorted(completions)
            
            # Complete parameters for known command
            command_name = tokens[0]
            command = self._find_command(command_name)
            
            if command:
                completions = []
                
                # Add parameter names
                for param in command.parameters:
                    completions.append(f"--{param.name}")
                    if len(param.name) == 1:
                        completions.append(f"-{param.name}")
                
                # Add choices for parameters
                if len(tokens) >= 2:
                    last_token = tokens[-1]
                    if last_token.startswith('--'):
                        param_name = last_token[2:]
                        for param in command.parameters:
                            if param.name == param_name and param.choices:
                                return param.choices
                
                return sorted(completions)
            
            return []
            
        except Exception as e:
            logger.debug(f"Command completion failed: {e}")
            return []
    
    def _get_or_create_group(self, group_path: str) -> CommandGroup:
        """Get or create command group by path"""
        
        if not group_path:
            return self.root_group
        
        path_parts = group_path.split('.')
        current_group = self.root_group
        
        for part in path_parts:
            if part not in current_group.subgroups:
                current_group.subgroups[part] = CommandGroup(part, f"Command group: {part}")
            current_group = current_group.subgroups[part]
        
        return current_group
    
    def _find_command(self, command_path: str) -> Optional[Command]:
        """Find command by path"""
        
        # Check alias first
        if command_path in self.command_aliases:
            command_path = self.command_aliases[command_path]
        
        path_parts = command_path.split('.')
        current_group = self.root_group
        
        # Navigate to parent group
        for part in path_parts[:-1]:
            if part not in current_group.subgroups:
                return None
            current_group = current_group.subgroups[part]
        
        # Find command
        command_name = path_parts[-1]
        return current_group.commands.get(command_name)
    
    def _find_group(self, group_path: str) -> Optional[CommandGroup]:
        """Find group by path"""
        
        if not group_path:
            return self.root_group
        
        path_parts = group_path.split('.')
        current_group = self.root_group
        
        for part in path_parts:
            if part not in current_group.subgroups:
                return None
            current_group = current_group.subgroups[part]
        
        return current_group
    
    def _generate_command_help(self, command: Command) -> str:
        """Generate help text for a command"""
        
        help_text = [f"{command.name} - {command.description}"]
        
        if command.deprecated:
            help_text.append(f"⚠️  DEPRECATED: Use '{command.replacement}' instead" if command.replacement else "⚠️  DEPRECATED")
        
        if command.parameters:
            help_text.append("\nParameters:")
            for param in command.parameters:
                param_line = f"  --{param.name}"
                if param.param_type != bool:
                    param_line += f" <{param.param_type.__name__}>"
                
                if param.required:
                    param_line += " (required)"
                elif param.default is not None:
                    param_line += f" (default: {param.default})"
                
                if param.description:
                    param_line += f" - {param.description}"
                
                if param.choices:
                    param_line += f" [choices: {', '.join(param.choices)}]"
                
                help_text.append(param_line)
        
        if command.examples:
            help_text.append("\nExamples:")
            for example in command.examples:
                help_text.append(f"  {example}")
        
        if command.aliases:
            help_text.append(f"\nAliases: {', '.join(command.aliases)}")
        
        return '\n'.join(help_text)
    
    def _generate_group_help(self, group: CommandGroup, group_path: str) -> str:
        """Generate help text for a command group"""
        
        help_text = [f"{group.name} - {group.description}"]
        
        if group.commands:
            help_text.append("\nCommands:")
            for name, cmd in sorted(group.commands.items()):
                if not cmd.hidden:
                    prefix = f"{group_path}.{name}" if group_path else name
                    status = " [DEPRECATED]" if cmd.deprecated else ""
                    help_text.append(f"  {prefix:<20} - {cmd.description}{status}")
        
        if group.subgroups:
            help_text.append("\nSubgroups:")
            for name, subgroup in sorted(group.subgroups.items()):
                if not subgroup.hidden:
                    prefix = f"{group_path}.{name}" if group_path else name
                    help_text.append(f"  {prefix:<20} - {subgroup.description}")
        
        return '\n'.join(help_text)
    
    def _register_builtin_commands(self) -> None:
        """Register built-in commands"""
        
        # Help command
        help_cmd = Command(
            name="help",
            description="Show help information",
            handler=self._help_handler,
            command_type=CommandType.UTIL,
            parameters=[
                CommandParameter("command", str, False, None, "Command or group to show help for")
            ],
            examples=["help", "help system", "help system.start"],
            aliases=["h", "?"]
        )
        self.register_command(help_cmd)
        
        # History command
        history_cmd = Command(
            name="history",
            description="Show command history",
            handler=self._history_handler,
            command_type=CommandType.UTIL,
            parameters=[
                CommandParameter("limit", int, False, 20, "Maximum number of commands to show")
            ],
            examples=["history", "history --limit 10"]
        )
        self.register_command(history_cmd)
        
        # Clear command
        clear_cmd = Command(
            name="clear",
            description="Clear the screen",
            handler=self._clear_handler,
            command_type=CommandType.UTIL,
            aliases=["cls"]
        )
        self.register_command(clear_cmd)
    
    def _help_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handler for help command"""
        command_path = params.get("command", "")
        return self.get_command_help(command_path)
    
    def _history_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handler for history command"""
        limit = params.get("limit", 20)
        
        if not self.command_history:
            return "No command history available"
        
        history_lines = []
        start_idx = max(0, len(self.command_history) - limit)
        
        for i, cmd in enumerate(self.command_history[start_idx:], start=start_idx + 1):
            history_lines.append(f"{i:3d}  {cmd}")
        
        return '\n'.join(history_lines)
    
    def _clear_handler(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handler for clear command"""
        # Return ANSI escape sequence to clear screen
        return '\033[2J\033[H'
    
    def get_router_statistics(self) -> Dict[str, Any]:
        """Get comprehensive router statistics"""
        
        def count_items(group: CommandGroup) -> tuple[int, int]:
            """Recursively count commands and groups"""
            cmd_count = len(group.commands)
            group_count = len(group.subgroups)
            
            for subgroup in group.subgroups.values():
                sub_cmds, sub_groups = count_items(subgroup)
                cmd_count += sub_cmds
                group_count += sub_groups
            
            return cmd_count, group_count
        
        total_commands, total_groups = count_items(self.root_group)
        
        return {
            "total_commands": total_commands,
            "total_groups": total_groups,
            "total_aliases": len(self.command_aliases),
            "command_history_size": len(self.command_history),
            "root_level_commands": len(self.root_group.commands),
            "root_level_groups": len(self.root_group.subgroups)
        }