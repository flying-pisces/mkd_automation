"""
Sequence Validator - Validates action sequences before playback.

Performs pre-execution validation to catch potential issues and ensure
sequence integrity before attempting playback.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Set
from enum import Enum

from ..automation.automation_engine import AutomationEngine

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Represents a validation issue found in sequence."""
    severity: ValidationSeverity
    message: str
    action_index: Optional[int] = None
    action_type: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of sequence validation."""
    is_valid: bool
    issues: List[ValidationIssue]
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if not self.issues:
            self.issues = []
    
    @property
    def has_errors(self) -> bool:
        """Check if validation found any errors."""
        return any(issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] 
                  for issue in self.issues)
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation found any warnings."""
        return any(issue.severity == ValidationSeverity.WARNING for issue in self.issues)
    
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get issues filtered by severity."""
        return [issue for issue in self.issues if issue.severity == severity]


class SequenceValidator:
    """
    Validates automation action sequences before execution.
    
    Performs checks for:
    - Action structure and required fields
    - Logical sequence consistency
    - Platform compatibility
    - Timing and resource constraints
    - Context dependencies
    """
    
    def __init__(self, automation_engine: AutomationEngine):
        self.automation_engine = automation_engine
        
        # Validation configuration
        self.max_sequence_length = 10000
        self.max_delay_duration = 300.0  # 5 minutes
        self.required_action_fields = {
            'mouse_click': {'type', 'coordinates'},
            'mouse_move': {'type', 'coordinates'},
            'key_press': {'type', 'key'},
            'type_text': {'type', 'text'},
            'click_element': {'type', 'target'},
            'delay': {'type', 'duration'},
            'scroll': {'type', 'dx', 'dy'}
        }
        
        logger.info("SequenceValidator initialized")
    
    def validate_sequence(self, actions: List[Dict[str, Any]]) -> ValidationResult:
        """
        Validate a complete action sequence.
        
        Args:
            actions: List of action dictionaries to validate
            
        Returns:
            ValidationResult with validation details
        """
        issues = []
        
        try:
            logger.debug(f"Validating sequence with {len(actions)} actions")
            
            # Check sequence length
            if len(actions) == 0:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message="Empty action sequence",
                    suggestion="Ensure the sequence contains at least one action"
                ))
                return ValidationResult(is_valid=False, issues=issues)
            
            if len(actions) > self.max_sequence_length:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Sequence length ({len(actions)}) exceeds recommended maximum ({self.max_sequence_length})",
                    suggestion="Consider breaking large sequences into smaller parts"
                ))
            
            # Validate individual actions
            for i, action in enumerate(actions):
                action_issues = self._validate_action(action, i)
                issues.extend(action_issues)
            
            # Validate sequence logic
            logic_issues = self._validate_sequence_logic(actions)
            issues.extend(logic_issues)
            
            # Check for platform compatibility
            platform_issues = self._validate_platform_compatibility(actions)
            issues.extend(platform_issues)
            
            # Determine if sequence is valid
            is_valid = not any(issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] 
                             for issue in issues)
            
            result = ValidationResult(is_valid=is_valid, issues=issues)
            
            logger.debug(f"Sequence validation complete: valid={is_valid}, issues={len(issues)}")
            return result
            
        except Exception as e:
            logger.error(f"Error during sequence validation: {e}")
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Validation error: {e}"
                )],
                error_message=str(e)
            )
    
    def _validate_action(self, action: Dict[str, Any], index: int) -> List[ValidationIssue]:
        """Validate a single action."""
        issues = []
        
        # Check action structure
        if not isinstance(action, dict):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Action must be a dictionary",
                action_index=index
            ))
            return issues
        
        # Check action type
        action_type = action.get('type')
        if not action_type:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Action missing required 'type' field",
                action_index=index,
                suggestion="Add 'type' field specifying action type"
            ))
            return issues
        
        action_type = action_type.lower()
        
        # Check required fields for action type
        if action_type in self.required_action_fields:
            required_fields = self.required_action_fields[action_type]
            for field in required_fields:
                if field not in action:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Action '{action_type}' missing required field '{field}'",
                        action_index=index,
                        action_type=action_type,
                        suggestion=f"Add '{field}' field to action"
                    ))
        
        # Validate specific action types
        action_issues = self._validate_specific_action_type(action, action_type, index)
        issues.extend(action_issues)
        
        return issues
    
    def _validate_specific_action_type(self, action: Dict[str, Any], action_type: str, index: int) -> List[ValidationIssue]:
        """Validate action-type-specific requirements."""
        issues = []
        
        if action_type in ['mouse_click', 'mouse_move']:
            # Validate coordinates
            coords = action.get('coordinates')
            if coords:
                if not isinstance(coords, (list, tuple)) or len(coords) != 2:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message="Coordinates must be [x, y] array",
                        action_index=index,
                        action_type=action_type
                    ))
                else:
                    x, y = coords
                    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            message="Coordinate values must be numbers",
                            action_index=index,
                            action_type=action_type
                        ))
                    elif x < 0 or y < 0 or x > 10000 or y > 10000:
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            message="Coordinates appear to be outside normal screen bounds",
                            action_index=index,
                            action_type=action_type,
                            suggestion="Verify coordinates are correct for target display"
                        ))
        
        elif action_type == 'key_press':
            # Validate key field
            key = action.get('key')
            if key and not isinstance(key, str):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message="Key field must be a string",
                    action_index=index,
                    action_type=action_type
                ))
        
        elif action_type == 'type_text':
            # Validate text field
            text = action.get('text')
            if text is not None and not isinstance(text, str):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message="Text field must be a string",
                    action_index=index,
                    action_type=action_type
                ))
            elif isinstance(text, str) and len(text) > 10000:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message="Text length is very large, may cause performance issues",
                    action_index=index,
                    action_type=action_type,
                    suggestion="Consider breaking large text into smaller chunks"
                ))
        
        elif action_type == 'delay':
            # Validate delay duration
            duration = action.get('duration')
            if duration is not None:
                if not isinstance(duration, (int, float)):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message="Delay duration must be a number",
                        action_index=index,
                        action_type=action_type
                    ))
                elif duration < 0:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message="Delay duration cannot be negative",
                        action_index=index,
                        action_type=action_type
                    ))
                elif duration > self.max_delay_duration:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Delay duration ({duration}s) is very long",
                        action_index=index,
                        action_type=action_type,
                        suggestion="Consider if such a long delay is necessary"
                    ))
        
        elif action_type == 'click_element':
            # Validate target specification
            target = action.get('target', {})
            if not isinstance(target, dict):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message="Target must be a dictionary",
                    action_index=index,
                    action_type=action_type
                ))
            elif not target.get('text') and not target.get('coordinates'):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message="Target must specify either 'text' or 'coordinates'",
                    action_index=index,
                    action_type=action_type,
                    suggestion="Add 'text' field for text-based targeting or 'coordinates' for position-based"
                ))
        
        return issues
    
    def _validate_sequence_logic(self, actions: List[Dict[str, Any]]) -> List[ValidationIssue]:
        """Validate logical consistency of action sequence."""
        issues = []
        
        try:
            # Track sequence patterns
            consecutive_clicks = 0
            total_delay_time = 0.0
            action_types = set()
            
            for i, action in enumerate(actions):
                action_type = action.get('type', '').lower()
                action_types.add(action_type)
                
                # Check for excessive consecutive clicks
                if action_type in ['mouse_click', 'click_element']:
                    consecutive_clicks += 1
                else:
                    if consecutive_clicks > 10:
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            message=f"Found {consecutive_clicks} consecutive clicks",
                            action_index=i - 1,
                            suggestion="Consider adding delays between clicks to avoid rate limiting"
                        ))
                    consecutive_clicks = 0
                
                # Track total delay time
                if action_type == 'delay':
                    duration = action.get('duration', 0)
                    if isinstance(duration, (int, float)):
                        total_delay_time += duration
            
            # Check for sequences with excessive delays
            if total_delay_time > 600:  # 10 minutes
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Sequence contains {total_delay_time:.1f}s of delays",
                    suggestion="Review if all delays are necessary"
                ))
            
            # Check for sequences with no interaction
            interactive_actions = {'mouse_click', 'click_element', 'type_text', 'key_press'}
            if not action_types.intersection(interactive_actions):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message="Sequence contains no interactive actions",
                    suggestion="Ensure sequence includes user interactions"
                ))
            
        except Exception as e:
            logger.error(f"Error validating sequence logic: {e}")
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message=f"Could not validate sequence logic: {e}"
            ))
        
        return issues
    
    def _validate_platform_compatibility(self, actions: List[Dict[str, Any]]) -> List[ValidationIssue]:
        """Validate platform compatibility of actions."""
        issues = []
        
        try:
            platform_name = self.automation_engine.platform.name
            
            # Check for platform-specific issues
            for i, action in enumerate(actions):
                action_type = action.get('type', '').lower()
                
                # Check key combinations
                if action_type == 'key_press':
                    key = action.get('key', '').lower()
                    
                    # Platform-specific key mapping warnings
                    if platform_name == "macOS":
                        if 'ctrl+' in key and 'cmd+' not in key:
                            issues.append(ValidationIssue(
                                severity=ValidationSeverity.WARNING,
                                message="Using Ctrl key on macOS, consider Cmd instead",
                                action_index=i,
                                action_type=action_type,
                                suggestion="macOS typically uses Cmd for shortcuts"
                            ))
                    elif platform_name in ["Windows", "Linux"]:
                        if 'cmd+' in key:
                            issues.append(ValidationIssue(
                                severity=ValidationSeverity.WARNING,
                                message="Using Cmd key on non-Mac platform",
                                action_index=i,
                                action_type=action_type,
                                suggestion="Use Ctrl instead of Cmd on Windows/Linux"
                            ))
                
                # Check coordinate bounds for different platforms
                if action_type in ['mouse_click', 'mouse_move']:
                    coords = action.get('coordinates', [0, 0])
                    if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                        x, y = coords[0], coords[1]
                        
                        # Very high coordinates might indicate scaling issues
                        if x > 5000 or y > 5000:
                            issues.append(ValidationIssue(
                                severity=ValidationSeverity.INFO,
                                message="High coordinate values detected",
                                action_index=i,
                                action_type=action_type,
                                suggestion="Verify coordinates account for display scaling"
                            ))
        
        except Exception as e:
            logger.error(f"Error validating platform compatibility: {e}")
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message=f"Could not validate platform compatibility: {e}"
            ))
        
        return issues
    
    def validate_single_action(self, action: Dict[str, Any]) -> ValidationResult:
        """Validate a single action in isolation."""
        issues = self._validate_action(action, 0)
        
        is_valid = not any(issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] 
                          for issue in issues)
        
        return ValidationResult(is_valid=is_valid, issues=issues)