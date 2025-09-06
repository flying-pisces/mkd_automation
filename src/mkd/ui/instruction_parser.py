"""
Natural Language Instruction Parser for MKD Automation.

This module parses user instructions and converts them into
actionable commands for browser and desktop automation.
"""

import re
import sys
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CommandType(Enum):
    """Types of commands that can be executed."""
    BROWSER_NAVIGATE = "browser_navigate"
    BROWSER_CLICK = "browser_click"
    BROWSER_TYPE = "browser_type"
    BROWSER_SEARCH = "browser_search"
    BROWSER_SCREENSHOT = "browser_screenshot"
    BROWSER_SCROLL = "browser_scroll"
    BROWSER_WAIT = "browser_wait"
    
    EMAILJS_CREATE = "emailjs_create"
    EMAILJS_EDIT = "emailjs_edit"
    
    RECORDING_START = "recording_start"
    RECORDING_STOP = "recording_stop"
    RECORDING_SAVE = "recording_save"
    RECORDING_LOAD = "recording_load"
    
    DESKTOP_SCREENSHOT = "desktop_screenshot"
    DESKTOP_CLICK = "desktop_click"
    DESKTOP_TYPE = "desktop_type"
    DESKTOP_HOTKEY = "desktop_hotkey"
    DESKTOP_MOUSE_MOVE = "desktop_mouse_move"
    DESKTOP_DRAG = "desktop_drag"
    
    # Application management
    LAUNCH_APPLICATION = "launch_application"
    CLOSE_APPLICATION = "close_application"
    SWITCH_APPLICATION = "switch_application"
    
    # Window management
    MINIMIZE_WINDOW = "minimize_window"
    MAXIMIZE_WINDOW = "maximize_window"
    RESIZE_WINDOW = "resize_window"
    MOVE_WINDOW = "move_window"
    
    # File operations
    OPEN_FILE = "open_file"
    OPEN_FOLDER = "open_folder"
    CREATE_FILE = "create_file"
    DELETE_FILE = "delete_file"
    COPY_FILE = "copy_file"
    MOVE_FILE = "move_file"
    
    # System operations
    RUN_COMMAND_PROMPT = "run_command_prompt"
    RUN_POWERSHELL = "run_powershell"
    OPEN_TASK_MANAGER = "open_task_manager"
    OPEN_CONTROL_PANEL = "open_control_panel"
    LOCK_COMPUTER = "lock_computer"
    
    SESSION_START = "session_start"
    SESSION_STOP = "session_stop"
    
    FILE_SAVE = "file_save"
    FILE_LOAD = "file_load"
    FILE_EXPORT = "file_export"
    
    HELP = "help"
    STATUS = "status"
    UNKNOWN = "unknown"


@dataclass
class ParsedCommand:
    """Represents a parsed command with parameters."""
    type: CommandType
    parameters: Dict[str, Any]
    confidence: float  # 0-1, how confident we are about the parsing
    raw_instruction: str
    suggestions: List[str] = None  # Alternative interpretations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            'type': self.type.value,
            'parameters': self.parameters,
            'confidence': self.confidence,
            'raw_instruction': self.raw_instruction,
            'suggestions': self.suggestions or []
        }


class InstructionParser:
    """
    Parses natural language instructions into executable commands.
    
    The parser uses pattern matching and keyword detection to understand
    user intentions and extract relevant parameters.
    """
    
    def __init__(self):
        """Initialize the parser with patterns and keywords."""
        self.patterns = self._init_patterns()
        self.keywords = self._init_keywords()
        
    def _init_patterns(self) -> Dict[CommandType, List[str]]:
        """Initialize regex patterns for different command types."""
        return {
            CommandType.BROWSER_NAVIGATE: [
                r'(?:open|go to|navigate to|visit)\s+([^\s,]+(?:\.[a-z]{2,})?)',
                r'browse\s+(?:to\s+)?([^\s,]+)',
                r'load\s+(?:the\s+)?(?:page|site|website)\s+([^\s,]+)',
            ],
            
            CommandType.BROWSER_SEARCH: [
                r'search\s+(?:for\s+)?"?([^"]+?)"?\s+(?:on|in)\s+(google|bing|duckduckgo)',
                r'(?:google|search)\s+(?:for\s+)?"?([^"]+)"?',
                r'find\s+"?([^"]+)"?\s+(?:on\s+)?(?:the\s+)?(?:web|internet)',
            ],
            
            CommandType.BROWSER_CLICK: [
                r'click\s+(?:on\s+)?(?:the\s+)?"?([^"]+)"?',
                r'press\s+(?:the\s+)?"?([^"]+)"?\s+button',
                r'select\s+(?:the\s+)?"?([^"]+)"?',
            ],
            
            CommandType.BROWSER_TYPE: [
                r'type\s+"([^"]+)"\s+(?:in|into)\s+(?:the\s+)?"?([^"]+)"?',
                r'enter\s+"([^"]+)"\s+(?:in|into)\s+(?:the\s+)?"?([^"]+)"?',
                r'fill\s+(?:in\s+)?(?:the\s+)?"?([^"]+)"?\s+with\s+"([^"]+)"',
                r'input\s+"([^"]+)"',
            ],
            
            CommandType.BROWSER_SCREENSHOT: [
                r'(?:take|capture)\s+(?:a\s+)?screenshot',
                r'screenshot\s+(?:the\s+)?(?:page|browser|website)',
                r'save\s+(?:a\s+)?(?:picture|image)\s+of\s+(?:the\s+)?page',
            ],
            
            CommandType.BROWSER_SCROLL: [
                r'scroll\s+(?:down|up|to\s+(?:the\s+)?bottom|to\s+(?:the\s+)?top)',
                r'(?:go|move)\s+to\s+(?:the\s+)?(?:top|bottom)\s+of\s+(?:the\s+)?page',
            ],
            
            CommandType.BROWSER_WAIT: [
                r'wait\s+(\d+)\s+seconds?',
                r'pause\s+(?:for\s+)?(\d+)\s+seconds?',
                r'delay\s+(\d+)',
            ],
            
            CommandType.EMAILJS_CREATE: [
                r'create\s+(?:an?\s+)?emailjs\s+template',
                r'(?:make|setup|configure)\s+(?:an?\s+)?email\s+template',
                r'emailjs.*(?:template|setup|create)',
                r'setup\s+email\s+(?:service|automation)',
            ],
            
            CommandType.RECORDING_START: [
                r'(?:start|begin)\s+recording',
                r'record\s+(?:my\s+)?(?:actions|interactions)',
                r'capture\s+(?:my\s+)?(?:mouse|keyboard|actions)',
            ],
            
            CommandType.RECORDING_STOP: [
                r'(?:stop|end|finish)\s+recording',
                r'stop\s+(?:capturing|recording)',
            ],
            
            CommandType.RECORDING_SAVE: [
                r'save\s+(?:the\s+)?recording',
                r'export\s+(?:the\s+)?(?:recording|script)',
                r'save\s+(?:as|to)\s+(.+)',
            ],
            
            CommandType.RECORDING_LOAD: [
                r'load\s+(?:the\s+)?recording\s+(.+)',
                r'open\s+(?:the\s+)?script\s+(.+)',
                r'import\s+(.+)',
            ],
            
            CommandType.DESKTOP_SCREENSHOT: [
                r'(?:take|capture)\s+(?:a\s+)?(?:desktop|screen)\s+screenshot',
                r'screenshot\s+(?:the\s+)?(?:desktop|screen)',
            ],
            
            CommandType.DESKTOP_CLICK: [
                r'click\s+(?:at\s+)?(?:position\s+)?(\d+),?\s*(\d+)',
                r'(?:left|right|middle)\s+click\s+(?:at\s+)?(\d+),?\s*(\d+)',
                r'click\s+(?:mouse\s+)?(?:at\s+)?coordinates\s+(\d+),?\s*(\d+)',
            ],
            
            CommandType.DESKTOP_MOUSE_MOVE: [
                r'move\s+mouse\s+(?:to\s+)?(\d+),?\s*(\d+)',
                r'move\s+(?:cursor\s+)?(?:to\s+)?position\s+(\d+),?\s*(\d+)',
            ],
            
            CommandType.DESKTOP_DRAG: [
                r'drag\s+from\s+(\d+),?\s*(\d+)\s+to\s+(\d+),?\s*(\d+)',
                r'drag\s+mouse\s+from\s+(\d+),?\s*(\d+)\s+to\s+(\d+),?\s*(\d+)',
            ],
            
            CommandType.DESKTOP_TYPE: [
                r'type\s+"([^"]+)"',
                r'enter\s+text\s+"([^"]+)"',
                r'input\s+"([^"]+)"',
            ],
            
            CommandType.DESKTOP_HOTKEY: [
                r'press\s+(ctrl|alt|shift|win)\s*\+\s*(.+)',
                r'(?:use|press)\s+(?:the\s+)?(?:hotkey|shortcut)\s+(.+)',
                r'keyboard\s+shortcut\s+(.+)',
            ],
            
            CommandType.LAUNCH_APPLICATION: [
                r'(?:launch|open|start|run)\s+(?:application\s+)?(.+)',
                r'open\s+(?:the\s+)?(?:app\s+)?(.+)',
                r'start\s+(?:program\s+)?(.+)',
            ],
            
            CommandType.CLOSE_APPLICATION: [
                r'close\s+(?:application\s+)?(.+)',
                r'quit\s+(.+)',
                r'exit\s+(.+)',
                r'kill\s+(?:process\s+)?(.+)',
            ],
            
            CommandType.MINIMIZE_WINDOW: [
                r'minimize\s+(?:window|(.+))',
                r'minimize\s+(?:the\s+)?(?:current\s+)?window',
            ],
            
            CommandType.MAXIMIZE_WINDOW: [
                r'maximize\s+(?:window|(.+))',
                r'maximize\s+(?:the\s+)?(?:current\s+)?window',
            ],
            
            CommandType.RESIZE_WINDOW: [
                r'resize\s+window\s+to\s+(\d+)x(\d+)',
                r'resize\s+(.+)\s+to\s+(\d+)x(\d+)',
                r'set\s+window\s+size\s+(\d+)x(\d+)',
            ],
            
            CommandType.MOVE_WINDOW: [
                r'move\s+window\s+to\s+(\d+),?\s*(\d+)',
                r'move\s+(.+)\s+to\s+(\d+),?\s*(\d+)',
            ],
            
            CommandType.OPEN_FILE: [
                r'open\s+file\s+(.+)',
                r'open\s+"([^"]+)"',
                r'launch\s+file\s+(.+)',
            ],
            
            CommandType.OPEN_FOLDER: [
                r'open\s+folder\s+(.+)',
                r'open\s+directory\s+(.+)',
                r'browse\s+(?:to\s+)?(.+)',
            ],
            
            CommandType.CREATE_FILE: [
                r'create\s+file\s+(.+)',
                r'new\s+file\s+(.+)',
                r'make\s+file\s+(.+)',
            ],
            
            CommandType.DELETE_FILE: [
                r'delete\s+file\s+(.+)',
                r'remove\s+file\s+(.+)',
                r'del\s+(.+)',
            ],
            
            CommandType.COPY_FILE: [
                r'copy\s+(.+)\s+to\s+(.+)',
                r'copy\s+file\s+(.+)\s+to\s+(.+)',
            ],
            
            CommandType.MOVE_FILE: [
                r'move\s+(.+)\s+to\s+(.+)',
                r'move\s+file\s+(.+)\s+to\s+(.+)',
            ],
            
            CommandType.RUN_COMMAND_PROMPT: [
                r'(?:open|launch|start)\s+(?:command\s+prompt|cmd)',
                r'open\s+cmd',
                r'command\s+prompt',
            ],
            
            CommandType.RUN_POWERSHELL: [
                r'(?:open|launch|start)\s+powershell',
                r'open\s+powershell',
                r'start\s+powershell',
            ],
            
            CommandType.OPEN_TASK_MANAGER: [
                r'(?:open|launch|start)\s+task\s+manager',
                r'task\s+manager',
                r'taskmgr',
            ],
            
            CommandType.OPEN_CONTROL_PANEL: [
                r'(?:open|launch|start)\s+control\s+panel',
                r'control\s+panel',
            ],
            
            CommandType.LOCK_COMPUTER: [
                r'lock\s+(?:computer|workstation|screen)',
                r'lock\s+(?:the\s+)?(?:pc|system)',
            ],
            
            CommandType.HELP: [
                r'help',
                r'what\s+can\s+you\s+do',
                r'(?:show\s+)?(?:commands|instructions|options)',
                r'how\s+(?:do\s+i|to)',
            ],
            
            CommandType.STATUS: [
                r'status',
                r'what(?:\s+are\s+you|\s+is\s+happening)',
                r'current\s+(?:state|status)',
            ],
        }
    
    def _init_keywords(self) -> Dict[str, List[str]]:
        """Initialize keyword mappings for context detection."""
        return {
            'browser': [
                'browser', 'web', 'website', 'page', 'url', 'link', 'chrome', 
                'firefox', 'edge', 'safari', 'internet', 'online'
            ],
            'emailjs': [
                'emailjs', 'email', 'template', 'contact', 'form', 'message',
                'mail', 'smtp', 'send', 'recipient'
            ],
            'recording': [
                'record', 'capture', 'save', 'script', 'automation', 'playback',
                'replay', 'sequence', 'actions'
            ],
            'desktop': [
                'desktop', 'screen', 'window', 'application', 'app', 'program',
                'mouse', 'keyboard', 'click', 'type', 'shortcut', 'hotkey'
            ],
            'file': [
                'file', 'save', 'load', 'export', 'import', 'document',
                'folder', 'directory', 'path'
            ]
        }
    
    def parse(self, instruction: str) -> ParsedCommand:
        """
        Parse a natural language instruction.
        
        Args:
            instruction: The user's instruction text
            
        Returns:
            ParsedCommand object with type, parameters, and confidence
        """
        instruction = instruction.strip()
        instruction_lower = instruction.lower()
        
        logger.debug(f"Parsing instruction: {instruction}")
        
        # Try to match against patterns
        for command_type, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, instruction_lower)
                if match:
                    confidence = self._calculate_confidence(instruction, command_type, match)
                    parameters = self._extract_parameters(instruction, command_type, match)
                    
                    return ParsedCommand(
                        type=command_type,
                        parameters=parameters,
                        confidence=confidence,
                        raw_instruction=instruction
                    )
        
        # If no exact pattern match, try context-based classification
        context_result = self._classify_by_context(instruction)
        if context_result:
            return context_result
            
        # Default to unknown command
        return ParsedCommand(
            type=CommandType.UNKNOWN,
            parameters={'instruction': instruction},
            confidence=0.0,
            raw_instruction=instruction,
            suggestions=self._generate_suggestions(instruction)
        )
    
    def _calculate_confidence(self, instruction: str, command_type: CommandType, 
                           match: re.Match) -> float:
        """Calculate confidence score for a parsed command."""
        base_confidence = 0.7  # Base confidence for pattern match
        
        # Boost confidence based on keyword presence
        instruction_lower = instruction.lower()
        relevant_keywords = []
        
        for category, keywords in self.keywords.items():
            if any(keyword in instruction_lower for keyword in keywords):
                if self._is_keyword_relevant(category, command_type):
                    relevant_keywords.extend(keywords)
        
        keyword_boost = min(0.3, len(relevant_keywords) * 0.1)
        
        # Reduce confidence for ambiguous matches
        ambiguity_penalty = 0.0
        if len(match.groups()) == 0:  # No capture groups
            ambiguity_penalty = 0.1
        
        confidence = base_confidence + keyword_boost - ambiguity_penalty
        return min(1.0, max(0.0, confidence))
    
    def _is_keyword_relevant(self, category: str, command_type: CommandType) -> bool:
        """Check if keyword category is relevant to command type."""
        relevance_map = {
            'browser': [
                CommandType.BROWSER_NAVIGATE, CommandType.BROWSER_CLICK,
                CommandType.BROWSER_TYPE, CommandType.BROWSER_SEARCH,
                CommandType.BROWSER_SCREENSHOT, CommandType.BROWSER_SCROLL,
                CommandType.BROWSER_WAIT
            ],
            'emailjs': [CommandType.EMAILJS_CREATE, CommandType.EMAILJS_EDIT],
            'recording': [
                CommandType.RECORDING_START, CommandType.RECORDING_STOP,
                CommandType.RECORDING_SAVE, CommandType.RECORDING_LOAD
            ],
            'desktop': [
                CommandType.DESKTOP_SCREENSHOT, CommandType.DESKTOP_CLICK,
                CommandType.DESKTOP_TYPE, CommandType.DESKTOP_HOTKEY
            ],
            'file': [
                CommandType.FILE_SAVE, CommandType.FILE_LOAD,
                CommandType.FILE_EXPORT, CommandType.RECORDING_SAVE,
                CommandType.RECORDING_LOAD
            ]
        }
        
        return command_type in relevance_map.get(category, [])
    
    def _extract_parameters(self, instruction: str, command_type: CommandType,
                          match: re.Match) -> Dict[str, Any]:
        """Extract parameters from matched instruction."""
        params = {}
        groups = match.groups()
        
        if command_type == CommandType.BROWSER_NAVIGATE:
            url = groups[0] if groups else ""
            # Ensure URL has protocol
            if url and not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            params['url'] = url
            
        elif command_type == CommandType.BROWSER_SEARCH:
            if len(groups) >= 2:
                params['query'] = groups[0].strip()
                params['engine'] = groups[1].strip()
            elif len(groups) >= 1:
                params['query'] = groups[0].strip()
                params['engine'] = 'google'  # default
                
        elif command_type == CommandType.BROWSER_CLICK:
            params['target'] = groups[0] if groups else ""
            
        elif command_type == CommandType.BROWSER_TYPE:
            if len(groups) >= 2:
                params['text'] = groups[0].strip()
                params['target'] = groups[1].strip()
            elif len(groups) >= 1:
                params['text'] = groups[0].strip()
                
        elif command_type == CommandType.BROWSER_WAIT:
            params['seconds'] = int(groups[0]) if groups and groups[0].isdigit() else 5
            
        elif command_type in [CommandType.RECORDING_SAVE, CommandType.RECORDING_LOAD]:
            if groups:
                params['filename'] = groups[0].strip()
                
        elif command_type == CommandType.DESKTOP_HOTKEY:
            if len(groups) >= 2:
                params['modifier'] = groups[0].strip()
                params['key'] = groups[1].strip()
            elif len(groups) >= 1:
                # Try to parse combined hotkey like "ctrl+c"
                hotkey = groups[0].strip()
                if '+' in hotkey:
                    parts = [p.strip() for p in hotkey.split('+')]
                    params['modifier'] = parts[0]
                    params['key'] = '+'.join(parts[1:])
                else:
                    params['key'] = hotkey
        
        # Extract common parameters
        self._extract_common_parameters(instruction, params)
        
        return params
    
    def _extract_common_parameters(self, instruction: str, params: Dict[str, Any]):
        """Extract common parameters like email addresses, filenames, etc."""
        instruction_lower = instruction.lower()
        
        # Extract email addresses
        email_pattern = r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
        email_matches = re.findall(email_pattern, instruction)
        if email_matches:
            params['emails'] = email_matches
            params['email'] = email_matches[0]  # First email as primary
            
        # Extract quoted strings (likely names, titles, etc.)
        quote_pattern = r'"([^"]+)"'
        quoted_strings = re.findall(quote_pattern, instruction)
        if quoted_strings:
            params['quoted_strings'] = quoted_strings
            
        # Extract file extensions/types
        file_pattern = r'\b\w+\.([a-zA-Z]{2,4})\b'
        file_matches = re.findall(file_pattern, instruction)
        if file_matches:
            params['file_types'] = file_matches
            
        # Extract numbers
        number_pattern = r'\b(\d+)\b'
        numbers = [int(m) for m in re.findall(number_pattern, instruction)]
        if numbers:
            params['numbers'] = numbers
            
    def _classify_by_context(self, instruction: str) -> Optional[ParsedCommand]:
        """Classify instruction based on keyword context when no pattern matches."""
        instruction_lower = instruction.lower()
        context_scores = {}
        
        # Score each context based on keyword presence
        for category, keywords in self.keywords.items():
            score = sum(1 for keyword in keywords if keyword in instruction_lower)
            if score > 0:
                context_scores[category] = score
                
        if not context_scores:
            return None
            
        # Get the highest scoring context
        best_context = max(context_scores, key=context_scores.get)
        max_score = context_scores[best_context]
        
        # Map context to likely command types
        context_commands = {
            'browser': CommandType.BROWSER_NAVIGATE,
            'emailjs': CommandType.EMAILJS_CREATE,
            'recording': CommandType.RECORDING_START,
            'desktop': CommandType.DESKTOP_SCREENSHOT,
            'file': CommandType.FILE_SAVE
        }
        
        command_type = context_commands.get(best_context, CommandType.UNKNOWN)
        confidence = min(0.6, max_score * 0.2)  # Lower confidence for context-only
        
        return ParsedCommand(
            type=command_type,
            parameters={'instruction': instruction, 'context': best_context},
            confidence=confidence,
            raw_instruction=instruction
        )
    
    def _generate_suggestions(self, instruction: str) -> List[str]:
        """Generate helpful suggestions for unknown instructions."""
        suggestions = []
        instruction_lower = instruction.lower()
        
        # Suggest based on partial keywords
        if any(word in instruction_lower for word in ['open', 'go', 'browse']):
            suggestions.append("Try: 'Open google.com' or 'Navigate to website.com'")
            
        if any(word in instruction_lower for word in ['email', 'template']):
            suggestions.append("Try: 'Create EmailJS template' or 'Setup email template'")
            
        if any(word in instruction_lower for word in ['record', 'capture']):
            suggestions.append("Try: 'Start recording' or 'Capture my actions'")
            
        if any(word in instruction_lower for word in ['click', 'button']):
            suggestions.append("Try: 'Click the submit button' or 'Press the login button'")
            
        # General suggestions
        if not suggestions:
            suggestions.extend([
                "Try: 'Open google.com'",
                "Try: 'Create EmailJS template'",
                "Try: 'Start recording'",
                "Try: 'Take screenshot'",
                "Say 'help' to see all available commands"
            ])
            
        return suggestions[:3]  # Limit to 3 suggestions
    
    def get_help_text(self) -> str:
        """Get help text with example commands."""
        return """
🤖 MKD Assistant Commands

📍 Browser Navigation:
• "Open google.com" or "Go to website.com"
• "Navigate to dashboard.emailjs.com"

🔍 Web Search:
• "Search for Python tutorials" 
• "Google machine learning"

🖱️ Browser Interaction:
• "Click the login button"
• "Type 'username' in the email field"
• "Fill name field with 'John Doe'"

📸 Screenshots:
• "Take screenshot" or "Capture page"
• "Screenshot the browser"

📧 EmailJS Automation:
• "Create EmailJS template"
• "Setup email template for contact form"

🎬 Recording:
• "Start recording" or "Record my actions"
• "Stop recording" 
• "Save recording as myfile.json"

⌨️ Desktop Actions:
• "Press Ctrl+C" or "Use hotkey Alt+Tab"
• "Take desktop screenshot"

💾 File Operations:
• "Save conversation"
• "Load recording file.json"

❓ Help & Status:
• "Help" - Show this help
• "Status" - Show current status

🔧 Tips:
• Be specific: "Click submit button" vs "click button"
• Use quotes for exact text: Type "Hello World"
• Commands are case-insensitive
"""