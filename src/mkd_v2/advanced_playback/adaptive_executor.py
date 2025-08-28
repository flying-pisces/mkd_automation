#!/usr/bin/env python3
"""
Adaptive Execution Engine

Smart action execution that adapts when UI elements move or change.
Provides intelligent adjustment for reliable playback in dynamic environments.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

from ..intelligence.context_detector import ContextDetector, ApplicationContext
from ..automation.intelligent_automation import IntelligentAutomationEngine
from ..platform.base import PlatformInterface
from .context_verifier import ContextVerifier, VerificationCriteria, VerificationLevel


logger = logging.getLogger(__name__)


class AdaptationType(Enum):
    """Types of execution adaptations."""
    COORDINATE_SHIFT = "coordinate_shift"
    ELEMENT_SEARCH = "element_search"
    CONTEXT_WAIT = "context_wait"
    SCALE_ADJUSTMENT = "scale_adjustment"
    RETRY_WITH_DELAY = "retry_with_delay"
    ALTERNATIVE_METHOD = "alternative_method"
    SEQUENCE_MODIFICATION = "sequence_modification"


class AdaptationStrategy(Enum):
    """Adaptation strategies for different scenarios."""
    CONSERVATIVE = "conservative"  # Minimal adaptations
    BALANCED = "balanced"         # Moderate adaptations
    AGGRESSIVE = "aggressive"     # Maximum adaptations
    LEARNING = "learning"         # ML-based adaptations


@dataclass
class AdaptationContext:
    """Context information for adaptation decisions."""
    original_action: Dict[str, Any]
    current_context: ApplicationContext
    expected_context: ApplicationContext
    
    # Environment differences
    resolution_changed: bool = False
    window_moved: bool = False
    window_resized: bool = False
    ui_elements_changed: bool = False
    
    # Timing information
    execution_attempt: int = 1
    last_attempt_time: float = 0.0
    total_adaptation_time: float = 0.0
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdaptationResult:
    """Result of adaptive execution."""
    success: bool
    adapted_action: Dict[str, Any]
    adaptation_type: AdaptationType
    confidence: float
    execution_time: float
    
    # Adaptation details
    original_coordinates: Optional[Tuple[int, int]] = None
    adapted_coordinates: Optional[Tuple[int, int]] = None
    coordinate_shift: Optional[Tuple[int, int]] = None
    scale_factor: Optional[float] = None
    
    # Process information
    attempts_made: int = 1
    adaptations_applied: List[str] = field(default_factory=list)
    fallback_used: bool = False
    
    # Quality metrics
    precision_score: float = 0.0  # How precisely the adaptation worked
    reliability_score: float = 0.0  # How reliable this adaptation type is
    
    error_info: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdaptiveExecutor:
    """
    Intelligent adaptive execution engine.
    
    Automatically adjusts actions when UI elements move, resize, or change
    to maintain reliable automation playback.
    """
    
    def __init__(self, automation_engine: IntelligentAutomationEngine, 
                 context_verifier: ContextVerifier):
        self.automation_engine = automation_engine
        self.context_verifier = context_verifier
        self.context_detector = automation_engine.context_detector
        
        # Adaptation learning
        self.adaptation_history: List[AdaptationResult] = []
        self.successful_adaptations: Dict[str, List[AdaptationResult]] = {}
        self.failed_adaptations: Dict[str, List[AdaptationResult]] = {}
        
        # Configuration
        self.config = {
            'max_adaptation_attempts': 3,
            'coordinate_search_radius': 100,
            'scale_tolerance': 0.1,
            'retry_delays': [0.5, 1.0, 2.0],  # seconds
            'adaptation_timeout': 30.0,  # seconds
            'learning_enabled': True
        }
        
        # Performance tracking
        self.stats = {
            'total_executions': 0,
            'successful_adaptations': 0,
            'failed_adaptations': 0,
            'avg_adaptation_time': 0.0,
            'adaptation_types_used': {},
            'precision_scores': []
        }
        
        logger.info("Adaptive executor initialized")
    
    def execute_with_adaptation(self, action: Dict[str, Any], 
                              strategy: AdaptationStrategy = AdaptationStrategy.BALANCED,
                              max_attempts: int = None) -> AdaptationResult:
        """
        Execute action with intelligent adaptation.
        
        Args:
            action: Action to execute (click, type, etc.)
            strategy: Adaptation strategy to use
            max_attempts: Maximum adaptation attempts (overrides config)
            
        Returns:
            Adaptation result with execution details
        """
        start_time = time.time()
        max_attempts = max_attempts or self.config['max_adaptation_attempts']
        
        try:
            # Initialize adaptation context
            adaptation_context = self._create_adaptation_context(action)
            
            # Try execution with adaptations
            for attempt in range(1, max_attempts + 1):
                logger.info(f"Adaptive execution attempt {attempt}/{max_attempts}")
                
                adaptation_context.execution_attempt = attempt
                adaptation_context.last_attempt_time = time.time()
                
                # Choose adaptation strategy for this attempt
                adapted_action, adaptation_type = self._adapt_action(
                    action, adaptation_context, strategy, attempt
                )
                
                # Execute adapted action
                execution_result = self._execute_adapted_action(adapted_action, adaptation_type)
                
                if execution_result['success']:
                    # Success! Create result
                    result = AdaptationResult(
                        success=True,
                        adapted_action=adapted_action,
                        adaptation_type=adaptation_type,
                        confidence=execution_result.get('confidence', 0.8),
                        execution_time=time.time() - start_time,
                        attempts_made=attempt,
                        adaptations_applied=self._get_adaptations_applied(action, adapted_action),
                        precision_score=self._calculate_precision_score(action, adapted_action, execution_result),
                        reliability_score=self._calculate_reliability_score(adaptation_type)
                    )
                    
                    # Learn from successful adaptation
                    self._learn_from_success(action, result, adaptation_context)
                    
                    return result
                
                # Failed - prepare for next attempt
                if attempt < max_attempts:
                    self._handle_failed_attempt(adaptation_context, execution_result)
                    time.sleep(self.config['retry_delays'][min(attempt-1, len(self.config['retry_delays'])-1)])
            
            # All attempts failed
            result = AdaptationResult(
                success=False,
                adapted_action=adapted_action,
                adaptation_type=adaptation_type,
                confidence=0.0,
                execution_time=time.time() - start_time,
                attempts_made=max_attempts,
                error_info=f"All {max_attempts} adaptation attempts failed",
                reliability_score=0.0
            )
            
            # Learn from failure
            self._learn_from_failure(action, result, adaptation_context)
            
            return result
            
        except Exception as e:
            logger.error(f"Adaptive execution failed: {e}")
            return AdaptationResult(
                success=False,
                adapted_action=action,
                adaptation_type=AdaptationType.RETRY_WITH_DELAY,
                confidence=0.0,
                execution_time=time.time() - start_time,
                attempts_made=1,
                error_info=f"Execution error: {e}"
            )
    
    def _create_adaptation_context(self, action: Dict[str, Any]) -> AdaptationContext:
        """Create adaptation context for the action."""
        current_context = self.context_detector.detect_current_context()
        
        # For now, use current context as expected (would be from recording)
        expected_context = current_context
        
        return AdaptationContext(
            original_action=action.copy(),
            current_context=current_context,
            expected_context=expected_context
        )
    
    def _adapt_action(self, action: Dict[str, Any], context: AdaptationContext,
                     strategy: AdaptationStrategy, attempt: int) -> Tuple[Dict[str, Any], AdaptationType]:
        """Adapt action based on context and strategy."""
        
        action_type = action.get('type', 'unknown')
        
        # Choose adaptation based on attempt and strategy
        if attempt == 1:
            # First attempt - minimal adaptation
            return self._apply_minimal_adaptation(action, context)
        elif attempt == 2:
            # Second attempt - moderate adaptation
            return self._apply_moderate_adaptation(action, context, strategy)
        else:
            # Final attempts - aggressive adaptation
            return self._apply_aggressive_adaptation(action, context, strategy)
    
    def _apply_minimal_adaptation(self, action: Dict[str, Any], 
                                context: AdaptationContext) -> Tuple[Dict[str, Any], AdaptationType]:
        """Apply minimal adaptations (small coordinate adjustments)."""
        
        adapted_action = action.copy()
        adaptation_type = AdaptationType.COORDINATE_SHIFT
        
        if action.get('type') in ['click', 'double_click']:
            # Small coordinate adjustment based on window movement
            if 'coordinates' in action:
                x, y = action['coordinates']
                
                # Check if window moved
                current_bounds = context.current_context.window_bounds
                expected_bounds = context.expected_context.window_bounds
                
                dx = current_bounds.get('x', 0) - expected_bounds.get('x', 0)
                dy = current_bounds.get('y', 0) - expected_bounds.get('y', 0)
                
                if abs(dx) > 5 or abs(dy) > 5:  # Window moved significantly
                    adapted_action['coordinates'] = (x + dx, y + dy)
                    logger.info(f"Applied window offset: ({dx}, {dy})")
                else:
                    # Small random adjustment to handle minor changes
                    import random
                    dx = random.randint(-5, 5)
                    dy = random.randint(-5, 5)
                    adapted_action['coordinates'] = (x + dx, y + dy)
        
        return adapted_action, adaptation_type
    
    def _apply_moderate_adaptation(self, action: Dict[str, Any], context: AdaptationContext,
                                 strategy: AdaptationStrategy) -> Tuple[Dict[str, Any], AdaptationType]:
        """Apply moderate adaptations (element search, scale adjustment)."""
        
        adapted_action = action.copy()
        
        if action.get('type') in ['click', 'double_click'] and 'coordinates' in action:
            # Try element search adaptation
            x, y = action['coordinates']
            radius = self.config['coordinate_search_radius']
            
            # Search for clickable elements around original coordinates
            elements = self.automation_engine.get_elements_in_region(
                x - radius//2, y - radius//2, radius, radius
            )
            
            if elements:
                # Find closest element to original coordinates
                closest_element = self._find_closest_element(elements, (x, y))
                if closest_element:
                    # Use element center as new coordinates
                    element_bounds = closest_element.get('bounds', {})
                    if element_bounds:
                        new_x = element_bounds.get('x', x) + element_bounds.get('width', 0) // 2
                        new_y = element_bounds.get('y', y) + element_bounds.get('height', 0) // 2
                        adapted_action['coordinates'] = (new_x, new_y)
                        return adapted_action, AdaptationType.ELEMENT_SEARCH
            
            # Fallback to scale adjustment
            scale_factor = self._calculate_scale_factor(context)
            if abs(scale_factor - 1.0) > self.config['scale_tolerance']:
                scaled_x = int(x * scale_factor)
                scaled_y = int(y * scale_factor)
                adapted_action['coordinates'] = (scaled_x, scaled_y)
                return adapted_action, AdaptationType.SCALE_ADJUSTMENT
        
        # For text input, try waiting for proper UI state
        if action.get('type') == 'type':
            return adapted_action, AdaptationType.CONTEXT_WAIT
        
        return adapted_action, AdaptationType.COORDINATE_SHIFT
    
    def _apply_aggressive_adaptation(self, action: Dict[str, Any], context: AdaptationContext,
                                   strategy: AdaptationStrategy) -> Tuple[Dict[str, Any], AdaptationType]:
        """Apply aggressive adaptations (alternative methods, sequence modification)."""
        
        adapted_action = action.copy()
        
        # Try alternative execution methods
        if action.get('type') == 'click':
            # Convert to keyboard shortcut if possible
            if 'text' in action and action['text'] in ['Save', 'Open', 'Copy', 'Paste']:
                keyboard_shortcuts = {
                    'Save': 'Ctrl+S',
                    'Open': 'Ctrl+O', 
                    'Copy': 'Ctrl+C',
                    'Paste': 'Ctrl+V'
                }
                
                if action['text'] in keyboard_shortcuts:
                    adapted_action = {
                        'type': 'key_combination',
                        'keys': keyboard_shortcuts[action['text']]
                    }
                    return adapted_action, AdaptationType.ALTERNATIVE_METHOD
        
        # For coordinates, try larger search area
        if action.get('type') in ['click', 'double_click'] and 'coordinates' in action:
            x, y = action['coordinates']
            
            # Expand search radius significantly
            large_radius = self.config['coordinate_search_radius'] * 2
            elements = self.automation_engine.get_elements_in_region(
                x - large_radius//2, y - large_radius//2, large_radius, large_radius
            )
            
            if elements:
                # Try to find element by type or attributes rather than just proximity
                best_element = self._find_best_matching_element(elements, action)
                if best_element:
                    element_bounds = best_element.get('bounds', {})
                    if element_bounds:
                        new_x = element_bounds.get('x', x) + element_bounds.get('width', 0) // 2
                        new_y = element_bounds.get('y', y) + element_bounds.get('height', 0) // 2
                        adapted_action['coordinates'] = (new_x, new_y)
                        return adapted_action, AdaptationType.ELEMENT_SEARCH
        
        # Sequence modification - add wait before action
        if context.execution_attempt >= 3:
            adapted_action['wait_before'] = 2.0  # Wait 2 seconds before execution
            return adapted_action, AdaptationType.SEQUENCE_MODIFICATION
        
        return adapted_action, AdaptationType.RETRY_WITH_DELAY
    
    def _execute_adapted_action(self, action: Dict[str, Any], 
                              adaptation_type: AdaptationType) -> Dict[str, Any]:
        """Execute the adapted action."""
        
        try:
            # Handle pre-execution wait if specified
            if 'wait_before' in action:
                time.sleep(action['wait_before'])
            
            action_type = action.get('type', 'unknown')
            
            if action_type == 'click':
                if 'coordinates' in action:
                    x, y = action['coordinates']
                    result = self.automation_engine.click_at_coordinates_intelligent(x, y)
                    return {
                        'success': result.success,
                        'confidence': result.confidence,
                        'execution_time': result.execution_time
                    }
            
            elif action_type == 'type':
                if 'text' in action:
                    result = self.automation_engine.type_text_intelligent(action['text'])
                    return {
                        'success': result.success,
                        'confidence': result.confidence,
                        'execution_time': result.execution_time
                    }
            
            elif action_type == 'key_combination':
                if 'keys' in action:
                    # Use traditional automation for key combinations
                    result = self.automation_engine.type_text(action['keys'])  # Simplified
                    return {
                        'success': result,
                        'confidence': 0.8,
                        'execution_time': 0.1
                    }
            
            elif action_type == 'double_click':
                if 'coordinates' in action:
                    x, y = action['coordinates']
                    # Double click = two quick clicks
                    result1 = self.automation_engine.click_at_coordinates_intelligent(x, y)
                    time.sleep(0.1)
                    result2 = self.automation_engine.click_at_coordinates_intelligent(x, y)
                    return {
                        'success': result1.success and result2.success,
                        'confidence': (result1.confidence + result2.confidence) / 2,
                        'execution_time': result1.execution_time + result2.execution_time
                    }
            
            # Unknown action type
            logger.warning(f"Unknown action type: {action_type}")
            return {'success': False, 'confidence': 0.0, 'execution_time': 0.0}
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {'success': False, 'confidence': 0.0, 'execution_time': 0.0, 'error': str(e)}
    
    def _find_closest_element(self, elements: List[Dict[str, Any]], 
                            coordinates: Tuple[int, int]) -> Optional[Dict[str, Any]]:
        """Find element closest to given coordinates."""
        if not elements:
            return None
        
        x, y = coordinates
        closest_element = None
        min_distance = float('inf')
        
        for element in elements:
            bounds = element.get('bounds', {})
            if bounds:
                # Calculate center of element
                elem_x = bounds.get('x', 0) + bounds.get('width', 0) // 2
                elem_y = bounds.get('y', 0) + bounds.get('height', 0) // 2
                
                # Calculate distance
                distance = ((elem_x - x) ** 2 + (elem_y - y) ** 2) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_element = element
        
        return closest_element
    
    def _find_best_matching_element(self, elements: List[Dict[str, Any]], 
                                  action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find element that best matches the action intent."""
        if not elements:
            return None
        
        # Look for specific element types based on action
        if action.get('type') == 'click':
            # Prefer interactive elements
            interactive_types = ['button', 'link', 'input', 'select']
            for element in elements:
                elem_type = element.get('type', '').lower()
                if any(itype in elem_type for itype in interactive_types):
                    return element
        
        # Fallback to first element
        return elements[0] if elements else None
    
    def _calculate_scale_factor(self, context: AdaptationContext) -> float:
        """Calculate scale factor based on resolution changes."""
        current_bounds = context.current_context.window_bounds
        expected_bounds = context.expected_context.window_bounds
        
        current_width = current_bounds.get('width', 1)
        expected_width = expected_bounds.get('width', 1)
        
        if expected_width > 0:
            return current_width / expected_width
        
        return 1.0
    
    def _get_adaptations_applied(self, original: Dict[str, Any], 
                               adapted: Dict[str, Any]) -> List[str]:
        """Get list of adaptations that were applied."""
        adaptations = []
        
        if 'coordinates' in original and 'coordinates' in adapted:
            if original['coordinates'] != adapted['coordinates']:
                adaptations.append('coordinate_adjustment')
        
        if 'type' in original and 'type' in adapted:
            if original['type'] != adapted['type']:
                adaptations.append('method_change')
        
        if 'wait_before' in adapted:
            adaptations.append('pre_execution_wait')
        
        return adaptations
    
    def _calculate_precision_score(self, original: Dict[str, Any], 
                                 adapted: Dict[str, Any], 
                                 result: Dict[str, Any]) -> float:
        """Calculate how precisely the adaptation worked."""
        base_score = 0.5
        
        # High precision if adaptation was minimal
        if 'coordinates' in original and 'coordinates' in adapted:
            orig_x, orig_y = original['coordinates']
            adapt_x, adapt_y = adapted['coordinates']
            distance = ((adapt_x - orig_x) ** 2 + (adapt_y - orig_y) ** 2) ** 0.5
            
            # Lower distance = higher precision
            if distance < 10:
                base_score += 0.3
            elif distance < 50:
                base_score += 0.1
        
        # Boost for high execution confidence
        execution_confidence = result.get('confidence', 0.0)
        base_score += execution_confidence * 0.2
        
        return min(1.0, base_score)
    
    def _calculate_reliability_score(self, adaptation_type: AdaptationType) -> float:
        """Calculate reliability score for adaptation type."""
        reliability_scores = {
            AdaptationType.COORDINATE_SHIFT: 0.7,
            AdaptationType.ELEMENT_SEARCH: 0.8,
            AdaptationType.CONTEXT_WAIT: 0.6,
            AdaptationType.SCALE_ADJUSTMENT: 0.7,
            AdaptationType.RETRY_WITH_DELAY: 0.5,
            AdaptationType.ALTERNATIVE_METHOD: 0.6,
            AdaptationType.SEQUENCE_MODIFICATION: 0.4
        }
        
        return reliability_scores.get(adaptation_type, 0.5)
    
    def _handle_failed_attempt(self, context: AdaptationContext, execution_result: Dict[str, Any]):
        """Handle failed adaptation attempt."""
        # Update context with failure information
        context.metadata['failed_attempts'] = context.metadata.get('failed_attempts', [])
        context.metadata['failed_attempts'].append({
            'attempt': context.execution_attempt,
            'error': execution_result.get('error', 'Unknown error'),
            'timestamp': time.time()
        })
        
        logger.info(f"Adaptation attempt {context.execution_attempt} failed: {execution_result.get('error', 'Unknown')}")
    
    def _learn_from_success(self, action: Dict[str, Any], result: AdaptationResult,
                          context: AdaptationContext):
        """Learn from successful adaptation."""
        if not self.config['learning_enabled']:
            return
        
        action_signature = self._get_action_signature(action)
        
        if action_signature not in self.successful_adaptations:
            self.successful_adaptations[action_signature] = []
        
        self.successful_adaptations[action_signature].append(result)
        
        # Keep only recent successes
        if len(self.successful_adaptations[action_signature]) > 20:
            self.successful_adaptations[action_signature] = \
                self.successful_adaptations[action_signature][-20:]
    
    def _learn_from_failure(self, action: Dict[str, Any], result: AdaptationResult,
                          context: AdaptationContext):
        """Learn from failed adaptation."""
        if not self.config['learning_enabled']:
            return
        
        action_signature = self._get_action_signature(action)
        
        if action_signature not in self.failed_adaptations:
            self.failed_adaptations[action_signature] = []
        
        self.failed_adaptations[action_signature].append(result)
        
        # Keep only recent failures
        if len(self.failed_adaptations[action_signature]) > 10:
            self.failed_adaptations[action_signature] = \
                self.failed_adaptations[action_signature][-10:]
    
    def _get_action_signature(self, action: Dict[str, Any]) -> str:
        """Get signature for action for learning purposes."""
        action_type = action.get('type', 'unknown')
        
        if action_type in ['click', 'double_click']:
            coords = action.get('coordinates', (0, 0))
            # Quantize coordinates to reduce signature space
            quantized_x = (coords[0] // 50) * 50
            quantized_y = (coords[1] // 50) * 50
            return f"{action_type}_{quantized_x}_{quantized_y}"
        elif action_type == 'type':
            text = action.get('text', '')
            if len(text) > 20:
                text = text[:20] + "..."
            return f"{action_type}_{text}"
        else:
            return action_type
    
    def get_adaptation_history(self, limit: int = 50) -> List[AdaptationResult]:
        """Get recent adaptation history."""
        return self.adaptation_history[-limit:]
    
    def get_adaptation_stats(self) -> Dict[str, Any]:
        """Get adaptation performance statistics."""
        stats = self.stats.copy()
        
        if stats['total_executions'] > 0:
            stats['success_rate'] = stats['successful_adaptations'] / stats['total_executions']
        else:
            stats['success_rate'] = 0.0
        
        if stats['precision_scores']:
            stats['avg_precision'] = sum(stats['precision_scores']) / len(stats['precision_scores'])
        else:
            stats['avg_precision'] = 0.0
        
        return stats
    
    def update_config(self, **kwargs):
        """Update executor configuration."""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                logger.info(f"Updated adaptive executor config: {key} = {value}")
    
    def cleanup(self):
        """Clean up executor resources."""
        self.adaptation_history.clear()
        self.successful_adaptations.clear()
        self.failed_adaptations.clear()
        logger.info("Adaptive executor cleaned up")