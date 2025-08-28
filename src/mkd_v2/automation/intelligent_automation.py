#!/usr/bin/env python3
"""
Intelligent Automation Engine

Combines traditional automation with intelligence features for context-aware automation.
Provides smart recording, pattern-based automation, and adaptive execution.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from ..platform.base import PlatformInterface
from ..intelligence import ContextDetector, PatternAnalyzer, SmartRecorder
from ..intelligence.context_detector import ApplicationContext, ContextChangeEvent
from ..intelligence.pattern_analyzer import UserPattern, ActionEvent
from ..intelligence.smart_recorder import RecordingDecision, RecordingSession
from .automation_engine import AutomationEngine
from .element_detector import DetectionResult
from .window_manager import WindowInfo


logger = logging.getLogger(__name__)


@dataclass
class IntelligentActionResult:
    """Result of an intelligent automation action."""
    success: bool
    action_type: str
    context: ApplicationContext
    confidence: float
    execution_time: float
    
    # Intelligence insights
    pattern_matched: Optional[UserPattern] = None
    context_adapted: bool = False
    optimization_applied: bool = False
    
    # Traditional result data
    traditional_result: Any = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class IntelligentAutomationEngine:
    """
    Intelligent automation engine that combines traditional automation
    with context awareness and pattern analysis.
    """
    
    def __init__(self, platform: PlatformInterface):
        self.platform = platform
        
        # Traditional automation
        self.automation_engine = AutomationEngine(platform)
        
        # Intelligence components
        self.context_detector = ContextDetector(platform)
        self.pattern_analyzer = PatternAnalyzer()
        self.smart_recorder = SmartRecorder(self.context_detector, self.pattern_analyzer)
        
        # Integration state
        self.is_learning_mode = True
        self.is_recording = False
        self.current_session: Optional[RecordingSession] = None
        
        # Performance tracking
        self.performance_stats = {
            'intelligent_actions': 0,
            'pattern_matches': 0,
            'context_adaptations': 0,
            'optimizations_applied': 0,
            'avg_confidence': 0.0,
            'avg_execution_time': 0.0
        }
        
        # Configuration
        self.config = {
            'auto_pattern_learning': True,
            'context_adaptation_enabled': True,
            'min_confidence_threshold': 0.6,
            'max_execution_time': 30.0  # seconds
        }
        
        logger.info("Intelligent automation engine initialized")
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize all components of the intelligent automation engine."""
        try:
            # Initialize platform
            platform_result = self.platform.initialize()
            if not platform_result.get('success', False):
                return {
                    'success': False,
                    'error': 'Platform initialization failed',
                    'platform_result': platform_result
                }
            
            # Initialize traditional automation
            automation_status = self.automation_engine.get_automation_status()
            
            # Detect initial context
            initial_context = self.context_detector.detect_current_context()
            
            # Set up context change monitoring
            self.context_detector.add_change_listener(self._on_context_change)
            
            return {
                'success': True,
                'platform': self.platform.name,
                'initial_context': {
                    'app_name': initial_context.app_name,
                    'context_type': initial_context.context_type.value,
                    'confidence': initial_context.confidence
                },
                'automation_status': automation_status,
                'intelligence_enabled': True
            }
            
        except Exception as e:
            logger.error(f"Intelligent automation initialization failed: {e}")
            return {
                'success': False,
                'error': f'Initialization failed: {e}'
            }
    
    def click_at_coordinates_intelligent(self, x: int, y: int, 
                                       adapt_to_context: bool = True) -> IntelligentActionResult:
        """
        Perform intelligent click that adapts to context and learns patterns.
        
        Args:
            x, y: Coordinates to click
            adapt_to_context: Whether to adapt action based on context
            
        Returns:
            Intelligent action result with context and pattern information
        """
        start_time = time.time()
        
        try:
            # Detect current context
            context = self.context_detector.detect_current_context()
            
            # Check for pattern matches
            pattern_match = self._find_matching_pattern('click', x, y, context)
            
            # Adapt coordinates if needed
            adapted_x, adapted_y = x, y
            context_adapted = False
            
            if adapt_to_context and self.config['context_adaptation_enabled']:
                adapted_coords = self._adapt_coordinates_to_context(x, y, context)
                if adapted_coords:
                    adapted_x, adapted_y = adapted_coords
                    context_adapted = True
            
            # Perform the click
            traditional_result = self.automation_engine.click_at_coordinates(adapted_x, adapted_y)
            
            # Record action for learning
            if self.is_learning_mode:
                action_event = ActionEvent(
                    timestamp=time.time(),
                    action_type='click',
                    coordinates=(adapted_x, adapted_y),
                    context=context,
                    duration=time.time() - start_time
                )
                self.pattern_analyzer.record_action(action_event)
                
                # Update recording session if active
                if self.current_session:
                    self.smart_recorder.update_session_metrics(
                        self.current_session.session_id,
                        actions_recorded=1
                    )
            
            # Calculate confidence
            confidence = context.confidence
            if pattern_match:
                confidence = (confidence + pattern_match.confidence) / 2
            
            # Create intelligent result
            result = IntelligentActionResult(
                success=traditional_result,
                action_type='click',
                context=context,
                confidence=confidence,
                execution_time=time.time() - start_time,
                pattern_matched=pattern_match,
                context_adapted=context_adapted,
                traditional_result=traditional_result,
                metadata={
                    'original_coords': (x, y),
                    'adapted_coords': (adapted_x, adapted_y),
                    'adaptation_applied': context_adapted
                }
            )
            
            # Update statistics
            self._update_performance_stats(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Intelligent click failed: {e}")
            return IntelligentActionResult(
                success=False,
                action_type='click',
                context=self.context_detector._create_unknown_context(),
                confidence=0.0,
                execution_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    def type_text_intelligent(self, text: str, 
                            use_patterns: bool = True) -> IntelligentActionResult:
        """
        Perform intelligent text typing with pattern recognition and optimization.
        
        Args:
            text: Text to type
            use_patterns: Whether to use learned patterns for optimization
            
        Returns:
            Intelligent action result
        """
        start_time = time.time()
        
        try:
            # Detect context
            context = self.context_detector.detect_current_context()
            
            # Check for text patterns/templates
            pattern_match = None
            optimized_text = text
            optimization_applied = False
            
            if use_patterns:
                pattern_result = self._find_text_pattern(text, context)
                if pattern_result:
                    pattern_match, optimized_text = pattern_result
                    optimization_applied = optimized_text != text
            
            # Perform typing
            traditional_result = self.automation_engine.type_text(optimized_text)
            
            # Record action for learning
            if self.is_learning_mode:
                action_event = ActionEvent(
                    timestamp=time.time(),
                    action_type='type',
                    text_input=optimized_text,
                    context=context,
                    duration=time.time() - start_time
                )
                self.pattern_analyzer.record_action(action_event)
                
                # Update recording session
                if self.current_session:
                    self.smart_recorder.update_session_metrics(
                        self.current_session.session_id,
                        actions_recorded=1
                    )
            
            # Calculate confidence
            confidence = context.confidence
            if pattern_match:
                confidence = (confidence + pattern_match.confidence) / 2
            
            result = IntelligentActionResult(
                success=traditional_result,
                action_type='type',
                context=context,
                confidence=confidence,
                execution_time=time.time() - start_time,
                pattern_matched=pattern_match,
                optimization_applied=optimization_applied,
                traditional_result=traditional_result,
                metadata={
                    'original_text': text,
                    'optimized_text': optimized_text,
                    'optimization_applied': optimization_applied
                }
            )
            
            self._update_performance_stats(result)
            return result
            
        except Exception as e:
            logger.error(f"Intelligent type failed: {e}")
            return IntelligentActionResult(
                success=False,
                action_type='type',
                context=self.context_detector._create_unknown_context(),
                confidence=0.0,
                execution_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    def detect_elements_intelligent(self, x: int, y: int, radius: int = 100) -> IntelligentActionResult:
        """
        Perform intelligent element detection with context awareness.
        
        Args:
            x, y: Center coordinates
            radius: Detection radius
            
        Returns:
            Intelligent detection result
        """
        start_time = time.time()
        
        try:
            context = self.context_detector.detect_current_context()
            
            # Get traditional detection result
            detection_result = self.automation_engine.get_elements_in_region(
                x - radius, y - radius, radius * 2, radius * 2
            )
            
            # Enhance with context information
            enhanced_elements = self._enhance_elements_with_context(detection_result, context)
            
            # Check for element patterns
            pattern_match = self._find_element_pattern(x, y, context)
            
            confidence = context.confidence
            if pattern_match:
                confidence = (confidence + pattern_match.confidence) / 2
            
            result = IntelligentActionResult(
                success=len(enhanced_elements) > 0,
                action_type='detect_elements',
                context=context,
                confidence=confidence,
                execution_time=time.time() - start_time,
                pattern_matched=pattern_match,
                traditional_result=enhanced_elements,
                metadata={
                    'elements_found': len(enhanced_elements),
                    'detection_radius': radius
                }
            )
            
            self._update_performance_stats(result)
            return result
            
        except Exception as e:
            logger.error(f"Intelligent element detection failed: {e}")
            return IntelligentActionResult(
                success=False,
                action_type='detect_elements',
                context=self.context_detector._create_unknown_context(),
                confidence=0.0,
                execution_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    def start_intelligent_recording(self, manual: bool = False) -> Dict[str, Any]:
        """
        Start intelligent recording that adapts to context and patterns.
        
        Args:
            manual: Whether this is a manual recording request
            
        Returns:
            Recording start result
        """
        try:
            # Check if should record
            current_context = self.context_detector.detect_current_context()
            decision = self.smart_recorder.should_start_recording(current_context)
            
            # Override decision if manual
            if manual:
                decision.should_record = True
                decision.reason = "Manual recording request"
                decision.confidence = 1.0
            
            if not decision.should_record:
                return {
                    'success': False,
                    'reason': decision.reason,
                    'confidence': decision.confidence
                }
            
            # Start recording session
            session_id = self.smart_recorder.start_recording_session(decision)
            self.current_session = self.smart_recorder.active_sessions[session_id]
            self.is_recording = True
            
            return {
                'success': True,
                'session_id': session_id,
                'trigger': decision.trigger.value,
                'reason': decision.reason,
                'confidence': decision.confidence,
                'context': {
                    'app_name': current_context.app_name,
                    'context_type': current_context.context_type.value
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to start intelligent recording: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def stop_intelligent_recording(self) -> Dict[str, Any]:
        """Stop current intelligent recording session."""
        try:
            if not self.is_recording or not self.current_session:
                return {
                    'success': False,
                    'reason': 'No active recording session'
                }
            
            session_id = self.current_session.session_id
            self.smart_recorder.stop_recording_session(session_id, "Manual stop")
            
            # Get final session stats
            session_stats = {
                'duration': time.time() - self.current_session.start_time,
                'actions_recorded': self.current_session.actions_recorded,
                'contexts_seen': len(self.current_session.contexts_seen),
                'recording_quality': self.current_session.recording_quality
            }
            
            self.current_session = None
            self.is_recording = False
            
            return {
                'success': True,
                'session_id': session_id,
                'session_stats': session_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to stop intelligent recording: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_intelligent_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the intelligent automation system."""
        try:
            # Base automation status
            base_status = self.automation_engine.get_automation_status()
            
            # Intelligence status
            context = self.context_detector.detect_current_context()
            context_stats = self.context_detector.get_detection_stats()
            pattern_stats = self.pattern_analyzer.get_analysis_stats()
            recorder_stats = self.smart_recorder.get_smart_recorder_stats()
            
            # Recent patterns
            recent_patterns = self.pattern_analyzer.get_recent_patterns(hours=1)
            high_value_patterns = self.pattern_analyzer.get_high_value_patterns()
            
            return {
                'traditional_automation': base_status,
                'intelligence': {
                    'current_context': {
                        'app_name': context.app_name,
                        'context_type': context.context_type.value,
                        'ui_state': context.ui_state.value,
                        'confidence': context.confidence
                    },
                    'context_detection': context_stats,
                    'pattern_analysis': pattern_stats,
                    'smart_recording': recorder_stats,
                    'recent_patterns': len(recent_patterns),
                    'high_value_patterns': len(high_value_patterns)
                },
                'performance': self.performance_stats,
                'configuration': self.config,
                'learning_mode': self.is_learning_mode,
                'recording_active': self.is_recording
            }
            
        except Exception as e:
            logger.error(f"Failed to get intelligent status: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Get intelligent optimization suggestions based on patterns."""
        try:
            suggestions = []
            
            # Get high-value patterns for automation suggestions
            high_value_patterns = self.pattern_analyzer.get_high_value_patterns(
                min_automation_potential=0.6
            )
            
            for pattern in high_value_patterns[:5]:  # Top 5 suggestions
                suggestion = {
                    'type': 'automation_opportunity',
                    'pattern_type': pattern.pattern_type.value,
                    'frequency': pattern.frequency,
                    'automation_potential': pattern.automation_potential,
                    'suggested_optimizations': pattern.suggested_optimizations,
                    'context_apps': [ctx.app_name for ctx in pattern.contexts if ctx],
                    'estimated_time_savings': self._estimate_time_savings(pattern)
                }
                suggestions.append(suggestion)
            
            # Context-based suggestions
            current_context = self.context_detector.detect_current_context()
            if current_context.confidence < 0.5:
                suggestions.append({
                    'type': 'context_improvement',
                    'description': 'Current context detection confidence is low',
                    'recommendation': 'Consider stabilizing the current application state',
                    'confidence': current_context.confidence
                })
            
            # Recording suggestions
            if not self.is_recording:
                recording_decision = self.smart_recorder.should_start_recording()
                if recording_decision.should_record and recording_decision.confidence > 0.7:
                    suggestions.append({
                        'type': 'recording_opportunity',
                        'trigger': recording_decision.trigger.value,
                        'reason': recording_decision.reason,
                        'confidence': recording_decision.confidence
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate optimization suggestions: {e}")
            return []
    
    def _find_matching_pattern(self, action_type: str, x: int, y: int, 
                             context: ApplicationContext) -> Optional[UserPattern]:
        """Find patterns that match the current action and context."""
        try:
            recent_patterns = self.pattern_analyzer.get_recent_patterns(hours=24)
            
            for pattern in recent_patterns:
                # Check if pattern matches current context
                for pattern_context in pattern.contexts:
                    if (pattern_context and 
                        pattern_context.app_name == context.app_name and
                        pattern_context.context_type == context.context_type):
                        
                        # Check if pattern contains similar actions
                        for action in pattern.actions:
                            if (action.action_type == action_type and
                                action.coordinates and
                                abs(action.coordinates[0] - x) < 100 and
                                abs(action.coordinates[1] - y) < 100):
                                return pattern
            
            return None
            
        except Exception as e:
            logger.error(f"Pattern matching failed: {e}")
            return None
    
    def _adapt_coordinates_to_context(self, x: int, y: int, 
                                    context: ApplicationContext) -> Optional[tuple]:
        """Adapt coordinates based on context and learned patterns."""
        try:
            # Simple adaptation based on window bounds
            if context.window_bounds:
                window_x = context.window_bounds.get('x', 0)
                window_y = context.window_bounds.get('y', 0)
                
                # If coordinates seem to be relative to screen but window has offset,
                # consider adapting them
                if x < window_x or y < window_y:
                    # This might be a relative coordinate that needs adaptation
                    adapted_x = window_x + x
                    adapted_y = window_y + y
                    return (adapted_x, adapted_y)
            
            return None
            
        except Exception as e:
            logger.error(f"Coordinate adaptation failed: {e}")
            return None
    
    def _find_text_pattern(self, text: str, context: ApplicationContext) -> Optional[tuple]:
        """Find text patterns and optimizations."""
        try:
            recent_patterns = self.pattern_analyzer.get_recent_patterns(hours=1)
            
            for pattern in recent_patterns:
                for action in pattern.actions:
                    if (action.action_type == 'type' and 
                        action.text_input and
                        action.text_input.lower() in text.lower()):
                        
                        # Found a matching text pattern
                        return (pattern, text)  # For now, return original text
            
            return None
            
        except Exception as e:
            logger.error(f"Text pattern matching failed: {e}")
            return None
    
    def _find_element_pattern(self, x: int, y: int, 
                            context: ApplicationContext) -> Optional[UserPattern]:
        """Find element detection patterns."""
        # Similar to _find_matching_pattern but for element detection
        return self._find_matching_pattern('detect_elements', x, y, context)
    
    def _enhance_elements_with_context(self, elements: List[Any], 
                                     context: ApplicationContext) -> List[Dict[str, Any]]:
        """Enhance detected elements with context information."""
        enhanced = []
        
        for element in elements:
            enhanced_element = {
                'element': element,
                'context_app': context.app_name,
                'context_type': context.context_type.value,
                'ui_state': context.ui_state.value,
                'detection_confidence': context.confidence,
                'timestamp': time.time()
            }
            enhanced.append(enhanced_element)
        
        return enhanced
    
    def _estimate_time_savings(self, pattern: UserPattern) -> float:
        """Estimate time savings if pattern were automated."""
        # Simple estimation: frequency * average_duration * automation_potential
        return pattern.frequency * pattern.duration_avg * pattern.automation_potential
    
    def _update_performance_stats(self, result: IntelligentActionResult):
        """Update performance statistics."""
        self.performance_stats['intelligent_actions'] += 1
        
        if result.pattern_matched:
            self.performance_stats['pattern_matches'] += 1
        
        if result.context_adapted:
            self.performance_stats['context_adaptations'] += 1
        
        if result.optimization_applied:
            self.performance_stats['optimizations_applied'] += 1
        
        # Update averages
        count = self.performance_stats['intelligent_actions']
        
        current_conf_avg = self.performance_stats['avg_confidence']
        self.performance_stats['avg_confidence'] = (
            (current_conf_avg * (count - 1) + result.confidence) / count
        )
        
        current_time_avg = self.performance_stats['avg_execution_time']
        self.performance_stats['avg_execution_time'] = (
            (current_time_avg * (count - 1) + result.execution_time) / count
        )
    
    def _on_context_change(self, event: ContextChangeEvent):
        """Handle context change events."""
        # Record context change for pattern analysis
        self.pattern_analyzer.record_context_change(event)
        
        # Check if recording should stop due to context change
        if self.is_recording and self.current_session:
            should_stop = self.smart_recorder.should_stop_recording(
                self.current_session.session_id
            )
            if should_stop:
                self.stop_intelligent_recording()
    
    def set_learning_mode(self, enabled: bool):
        """Enable or disable learning mode."""
        self.is_learning_mode = enabled
        logger.info(f"Learning mode: {'enabled' if enabled else 'disabled'}")
    
    def update_config(self, **kwargs):
        """Update intelligent automation configuration."""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                logger.info(f"Updated intelligent config: {key} = {value}")
        
        # Also update smart recorder config if relevant
        recorder_keys = ['auto_recording_enabled', 'min_pattern_confidence']
        recorder_config = {k: v for k, v in kwargs.items() if k in recorder_keys}
        if recorder_config:
            self.smart_recorder.update_config(**recorder_config)
    
    def cleanup(self):
        """Clean up all intelligent automation resources."""
        try:
            # Stop recording if active
            if self.is_recording:
                self.stop_intelligent_recording()
            
            # Clean up components
            self.smart_recorder.cleanup()
            self.pattern_analyzer.cleanup()
            self.context_detector.cleanup()
            
            logger.info("Intelligent automation engine cleaned up")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    # Delegate traditional methods to base automation engine
    def click_at_coordinates(self, x: int, y: int) -> bool:
        """Traditional click - delegates to base engine."""
        return self.automation_engine.click_at_coordinates(x, y)
    
    def type_text(self, text: str) -> bool:
        """Traditional type - delegates to base engine."""
        return self.automation_engine.type_text(text)
    
    def get_elements_in_region(self, x: int, y: int, width: int, height: int) -> List[Any]:
        """Traditional element detection - delegates to base engine."""
        return self.automation_engine.get_elements_in_region(x, y, width, height)