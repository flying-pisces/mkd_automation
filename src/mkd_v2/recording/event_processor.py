"""
Event Processor - Processes and enriches captured input events.

Adds context information, filters noise, and prepares events
for storage and playback.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EventCategory(Enum):
    """Event categories for processing."""
    USER_INPUT = "user_input"
    SYSTEM_EVENT = "system_event"
    UI_INTERACTION = "ui_interaction"
    APPLICATION_EVENT = "application_event"


@dataclass
class ProcessedEvent:
    """Processed event with context information."""
    original_event: Dict[str, Any]
    category: EventCategory
    confidence: float  # 0.0 to 1.0
    context: Dict[str, Any]
    metadata: Dict[str, Any]


class EventProcessor:
    """
    Processes input events and adds contextual information.
    
    Features:
    - Event categorization
    - Context enrichment
    - Noise filtering
    - Intent detection
    """
    
    def __init__(self):
        self.initialized = False
        
        # Processing settings
        self.min_confidence = 0.3
        self.context_window = 1.0  # seconds
        self.enable_ui_detection = True
        
        # Event history for context
        self.event_history: List[Dict[str, Any]] = []
        self.max_history_size = 100
        
        # Statistics
        self.stats = {
            'events_processed': 0,
            'events_filtered': 0,
            'high_confidence_events': 0,
            'ui_interactions_detected': 0,
            'context_enrichments': 0
        }
        
        logger.info("EventProcessor initialized")
    
    def initialize(self):
        """Initialize event processor."""
        try:
            logger.info("Initializing event processor")
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize event processor: {e}")
            raise
    
    def process_event(self, raw_event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a raw input event.
        
        Args:
            raw_event: Raw event from input capturer
            
        Returns:
            Processed event dictionary or None if filtered
        """
        if not self.initialized:
            raise RuntimeError("EventProcessor not initialized")
        
        try:
            self.stats['events_processed'] += 1
            
            # Categorize event
            category = self._categorize_event(raw_event)
            
            # Calculate confidence
            confidence = self._calculate_confidence(raw_event, category)
            
            # Filter low confidence events
            if confidence < self.min_confidence:
                self.stats['events_filtered'] += 1
                return None
            
            # Add context information
            context = self._extract_context(raw_event)
            
            # Detect UI interactions
            ui_info = self._detect_ui_interaction(raw_event) if self.enable_ui_detection else {}
            
            # Create processed event
            processed = {
                'timestamp': raw_event.get('timestamp', time.time()),
                'type': raw_event.get('type'),
                'source': raw_event.get('source'),
                'data': raw_event.get('data', {}),
                'category': category.value,
                'confidence': confidence,
                'context': context,
                'ui_info': ui_info,
                'metadata': {
                    'processor_version': '1.0.0',
                    'processing_time': time.time()
                }
            }
            
            # Update statistics
            if confidence > 0.8:
                self.stats['high_confidence_events'] += 1
            
            if ui_info:
                self.stats['ui_interactions_detected'] += 1
                
            if context:
                self.stats['context_enrichments'] += 1
            
            # Add to history
            self._add_to_history(processed)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            return None
    
    def _categorize_event(self, event: Dict[str, Any]) -> EventCategory:
        """
        Categorize event based on type and content.
        
        Args:
            event: Raw event data
            
        Returns:
            Event category
        """
        event_type = event.get('type', '')
        source = event.get('source', '')
        data = event.get('data', {})
        
        # Mouse clicks are likely UI interactions
        if event_type == 'mouse_click':
            return EventCategory.UI_INTERACTION
        
        # Keyboard shortcuts might be application events
        if event_type in ['key_press', 'key_release']:
            modifiers = data.get('modifiers', [])
            if modifiers:  # Has modifier keys
                return EventCategory.APPLICATION_EVENT
        
        # Mouse movements are user input
        if event_type == 'mouse_move':
            return EventCategory.USER_INPUT
        
        # Default to user input
        return EventCategory.USER_INPUT
    
    def _calculate_confidence(self, event: Dict[str, Any], category: EventCategory) -> float:
        """
        Calculate confidence score for event.
        
        Args:
            event: Raw event data
            category: Event category
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = 0.5
        event_type = event.get('type', '')
        data = event.get('data', {})
        
        # Higher confidence for clear interactions
        if event_type == 'mouse_click':
            base_confidence = 0.9
        elif event_type in ['key_press', 'key_release']:
            # Higher confidence for printable characters
            if data.get('char') and data.get('char').isprintable():
                base_confidence = 0.8
            else:
                base_confidence = 0.7
        elif event_type == 'mouse_move':
            # Lower confidence for mouse moves
            base_confidence = 0.4
        
        # Adjust based on context
        if self._has_recent_interaction():
            base_confidence += 0.1
        
        # Ensure within bounds
        return max(0.0, min(1.0, base_confidence))
    
    def _extract_context(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract contextual information for event.
        
        Args:
            event: Raw event data
            
        Returns:
            Context dictionary
        """
        context = {}
        current_time = event.get('timestamp', time.time())
        
        # Recent events context
        recent_events = [
            e for e in self.event_history
            if current_time - e.get('timestamp', 0) <= self.context_window
        ]
        
        if recent_events:
            context['recent_event_count'] = len(recent_events)
            context['recent_event_types'] = list(set(
                e.get('type') for e in recent_events
            ))
        
        # Sequence detection
        if len(recent_events) >= 2:
            context['sequence_detected'] = self._detect_sequence(recent_events)
        
        # Timing context
        if self.event_history:
            last_event = self.event_history[-1]
            context['time_since_last'] = current_time - last_event.get('timestamp', 0)
        
        return context
    
    def _detect_ui_interaction(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect UI interaction information.
        
        Args:
            event: Raw event data
            
        Returns:
            UI interaction information
        """
        ui_info = {}
        event_type = event.get('type', '')
        data = event.get('data', {})
        
        # For mouse events, try to get screen position info
        if event_type.startswith('mouse'):
            x = data.get('x', 0)
            y = data.get('y', 0)
            
            ui_info.update({
                'screen_position': {'x': x, 'y': y},
                'interaction_type': 'mouse',
                'estimated_target': self._estimate_ui_target(x, y, event_type)
            })
        
        # For keyboard events, try to detect input patterns
        elif event_type.startswith('key'):
            key = data.get('key', '')
            char = data.get('char', '')
            modifiers = data.get('modifiers', [])
            
            ui_info.update({
                'interaction_type': 'keyboard',
                'key_info': {'key': key, 'char': char, 'modifiers': modifiers},
                'estimated_intent': self._estimate_keyboard_intent(key, char, modifiers)
            })
        
        return ui_info
    
    def _estimate_ui_target(self, x: int, y: int, event_type: str) -> str:
        """
        Estimate UI target type based on position and event.
        
        Args:
            x: X coordinate
            y: Y coordinate
            event_type: Type of mouse event
            
        Returns:
            Estimated target type
        """
        # Basic heuristics - in a real implementation,
        # this would use accessibility APIs or screen analysis
        
        if event_type == 'mouse_click':
            # Simple position-based guessing
            if y < 100:  # Top of screen
                return 'menu_or_toolbar'
            elif y > 800:  # Bottom of screen  
                return 'taskbar_or_dock'
            else:
                return 'content_area'
        elif event_type == 'mouse_move':
            return 'cursor_movement'
        else:
            return 'unknown'
    
    def _estimate_keyboard_intent(self, key: str, char: str, modifiers: List[str]) -> str:
        """
        Estimate keyboard input intent.
        
        Args:
            key: Key pressed
            char: Character (if printable)
            modifiers: Modifier keys
            
        Returns:
            Estimated intent
        """
        if modifiers:
            if 'ctrl' in modifiers or 'cmd' in modifiers:
                return 'keyboard_shortcut'
            elif 'alt' in modifiers:
                return 'menu_navigation'
            else:
                return 'modified_input'
        
        if char and char.isprintable():
            return 'text_input'
        elif key in ['Enter', 'Return']:
            return 'submit_action'
        elif key in ['Escape']:
            return 'cancel_action'
        elif key.startswith('Arrow'):
            return 'navigation'
        elif key in ['Tab']:
            return 'focus_change'
        else:
            return 'special_key'
    
    def _detect_sequence(self, events: List[Dict[str, Any]]) -> str:
        """
        Detect event sequences.
        
        Args:
            events: Recent events
            
        Returns:
            Detected sequence type
        """
        if len(events) < 2:
            return 'none'
        
        event_types = [e.get('type') for e in events]
        
        # Detect common patterns
        if event_types == ['mouse_click', 'mouse_click']:
            return 'double_click'
        elif 'mouse_move' in event_types and 'mouse_click' in event_types:
            return 'click_sequence'
        elif all(t.startswith('key_') for t in event_types):
            return 'typing_sequence'
        else:
            return 'mixed_sequence'
    
    def _has_recent_interaction(self) -> bool:
        """
        Check if there was a recent user interaction.
        
        Returns:
            True if recent interaction detected
        """
        if not self.event_history:
            return False
        
        last_event = self.event_history[-1]
        current_time = time.time()
        time_diff = current_time - last_event.get('timestamp', 0)
        
        return time_diff < self.context_window
    
    def _add_to_history(self, event: Dict[str, Any]):
        """
        Add event to history.
        
        Args:
            event: Processed event
        """
        self.event_history.append(event)
        
        # Trim history if too large
        if len(self.event_history) > self.max_history_size:
            self.event_history = self.event_history[-self.max_history_size:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            'initialized': self.initialized,
            'stats': self.stats.copy(),
            'settings': {
                'min_confidence': self.min_confidence,
                'context_window': self.context_window,
                'enable_ui_detection': self.enable_ui_detection
            },
            'history_size': len(self.event_history)
        }
    
    def cleanup(self):
        """Clean up event processor resources."""
        logger.info("Cleaning up EventProcessor")
        self.event_history.clear()
        self.initialized = False
        logger.info("EventProcessor cleanup complete")