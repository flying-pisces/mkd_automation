#!/usr/bin/env python3
"""
Pattern Analysis System

Analyzes user behavior patterns to enable intelligent automation decisions.
Tracks workflows, identifies repetitive tasks, and suggests optimizations.
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
from datetime import datetime, timedelta

from .context_detector import ApplicationContext, ContextChangeEvent


logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of user patterns."""
    REPETITIVE_TASK = "repetitive_task"
    WORKFLOW_SEQUENCE = "workflow_sequence"
    CONTEXT_SWITCHING = "context_switching" 
    TIME_BASED = "time_based"
    ERROR_RECOVERY = "error_recovery"
    EFFICIENCY_OPPORTUNITY = "efficiency_opportunity"


class PatternConfidence(Enum):
    """Pattern detection confidence levels."""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.9


@dataclass
class ActionEvent:
    """Represents a user action event."""
    timestamp: float
    action_type: str  # "click", "type", "key", "scroll", "context_change"
    coordinates: Optional[Tuple[int, int]] = None
    text_input: Optional[str] = None
    key_combination: Optional[str] = None
    context: Optional[ApplicationContext] = None
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserPattern:
    """Represents a detected user behavior pattern."""
    pattern_id: str
    pattern_type: PatternType
    confidence: float
    
    # Pattern details
    actions: List[ActionEvent]
    contexts: List[ApplicationContext]
    frequency: int  # How often this pattern occurs
    duration_avg: float  # Average duration in seconds
    
    # Timing information
    first_seen: float
    last_seen: float
    occurrences: List[float]  # Timestamps of occurrences
    
    # Pattern characteristics
    is_repetitive: bool = False
    involves_context_switch: bool = False
    efficiency_score: float = 0.0  # 0.0-1.0, higher = more efficient
    
    # Suggestions
    automation_potential: float = 0.0  # 0.0-1.0, how automatable this is
    suggested_optimizations: List[str] = field(default_factory=list)
    
    metadata: Dict[str, Any] = field(default_factory=dict)


class PatternAnalyzer:
    """
    Intelligent pattern analysis system.
    
    Analyzes user behavior to detect patterns, workflows, and optimization opportunities.
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.action_history: deque = deque(maxlen=max_history)
        self.context_history: deque = deque(maxlen=max_history)
        
        self.detected_patterns: Dict[str, UserPattern] = {}
        self.pattern_templates: Dict[PatternType, Dict[str, Any]] = {}
        
        # Analysis parameters
        self.min_pattern_frequency = 3  # Minimum occurrences to consider a pattern
        self.max_pattern_gap = 300.0  # Max seconds between pattern actions
        self.similarity_threshold = 0.7  # Minimum similarity to match patterns
        
        # Statistics
        self.analysis_stats = {
            'total_actions': 0,
            'patterns_detected': 0,
            'analysis_runs': 0,
            'avg_analysis_time': 0.0
        }
        
        self._initialize_pattern_templates()
        logger.info("Pattern analyzer initialized")
    
    def _initialize_pattern_templates(self):
        """Initialize pattern detection templates."""
        
        # Repetitive task template
        self.pattern_templates[PatternType.REPETITIVE_TASK] = {
            'min_frequency': 3,
            'max_time_gap': 60.0,  # 1 minute
            'similarity_threshold': 0.8,
            'min_actions': 2
        }
        
        # Workflow sequence template
        self.pattern_templates[PatternType.WORKFLOW_SEQUENCE] = {
            'min_frequency': 2,
            'max_time_gap': 300.0,  # 5 minutes
            'similarity_threshold': 0.6,
            'min_actions': 5
        }
        
        # Context switching template
        self.pattern_templates[PatternType.CONTEXT_SWITCHING] = {
            'min_frequency': 3,
            'max_time_gap': 120.0,  # 2 minutes
            'context_switches_required': 2,
            'min_actions': 3
        }
        
        # Time-based patterns
        self.pattern_templates[PatternType.TIME_BASED] = {
            'min_frequency': 5,
            'time_window': 3600.0,  # 1 hour
            'min_actions': 1
        }
    
    def record_action(self, action_event: ActionEvent):
        """Record a user action for pattern analysis."""
        self.action_history.append(action_event)
        self.analysis_stats['total_actions'] += 1
        
        # Trigger pattern analysis periodically
        if len(self.action_history) % 50 == 0:  # Every 50 actions
            self.analyze_patterns()
    
    def record_context_change(self, context_event: ContextChangeEvent):
        """Record a context change for pattern analysis."""
        # Convert context change to action event
        action_event = ActionEvent(
            timestamp=context_event.timestamp,
            action_type="context_change",
            context=context_event.new_context,
            metadata={
                'change_type': context_event.change_type,
                'significance': context_event.significance,
                'previous_context': context_event.previous_context.app_name if context_event.previous_context else None
            }
        )
        
        self.record_action(action_event)
        self.context_history.append(context_event)
    
    def analyze_patterns(self) -> List[UserPattern]:
        """
        Analyze recent actions to detect patterns.
        
        Returns:
            List of newly detected patterns
        """
        start_time = time.time()
        
        try:
            new_patterns = []
            
            # Analyze different pattern types
            new_patterns.extend(self._detect_repetitive_patterns())
            new_patterns.extend(self._detect_workflow_patterns())
            new_patterns.extend(self._detect_context_switching_patterns())
            new_patterns.extend(self._detect_time_based_patterns())
            
            # Update pattern database
            for pattern in new_patterns:
                self.detected_patterns[pattern.pattern_id] = pattern
                self.analysis_stats['patterns_detected'] += 1
            
            # Update existing patterns
            self._update_existing_patterns()
            
            # Update statistics
            analysis_time = time.time() - start_time
            self._update_analysis_stats(analysis_time)
            
            if new_patterns:
                logger.info(f"Detected {len(new_patterns)} new patterns")
            
            return new_patterns
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return []
    
    def _detect_repetitive_patterns(self) -> List[UserPattern]:
        """Detect repetitive task patterns."""
        patterns = []
        
        if len(self.action_history) < 10:
            return patterns
        
        # Group actions by similarity
        action_groups = self._group_similar_actions()
        
        for group_key, actions in action_groups.items():
            if len(actions) >= self.min_pattern_frequency:
                # Check if actions are close in time
                time_gaps = []
                for i in range(1, len(actions)):
                    gap = actions[i].timestamp - actions[i-1].timestamp
                    time_gaps.append(gap)
                
                # If most gaps are small, this is repetitive
                small_gaps = [g for g in time_gaps if g < 60.0]  # 1 minute
                if len(small_gaps) / len(time_gaps) > 0.7:  # 70% small gaps
                    pattern = self._create_repetitive_pattern(actions)
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_workflow_patterns(self) -> List[UserPattern]:
        """Detect workflow sequence patterns."""
        patterns = []
        
        if len(self.action_history) < 20:
            return patterns
        
        # Look for sequences of 5-15 actions that repeat
        sequence_length = 10
        recent_actions = list(self.action_history)[-200:]  # Last 200 actions
        
        sequences = []
        for i in range(len(recent_actions) - sequence_length):
            sequence = recent_actions[i:i + sequence_length]
            sequences.append(sequence)
        
        # Find similar sequences
        similar_groups = self._group_similar_sequences(sequences)
        
        for group in similar_groups:
            if len(group) >= 2:  # At least 2 similar sequences
                pattern = self._create_workflow_pattern(group)
                patterns.append(pattern)
        
        return patterns
    
    def _detect_context_switching_patterns(self) -> List[UserPattern]:
        """Detect context switching patterns."""
        patterns = []
        
        if len(self.context_history) < 10:
            return patterns
        
        # Look for repeated context switch sequences
        context_switches = list(self.context_history)[-50:]  # Recent switches
        
        switch_sequences = []
        for i in range(len(context_switches) - 3):
            sequence = context_switches[i:i + 3]  # 3-context sequences
            switch_sequences.append(sequence)
        
        # Group by similarity
        similar_groups = defaultdict(list)
        for seq in switch_sequences:
            key = self._get_context_sequence_key(seq)
            similar_groups[key].append(seq)
        
        for key, sequences in similar_groups.items():
            if len(sequences) >= self.min_pattern_frequency:
                pattern = self._create_context_switching_pattern(sequences)
                patterns.append(pattern)
        
        return patterns
    
    def _detect_time_based_patterns(self) -> List[UserPattern]:
        """Detect time-based patterns."""
        patterns = []
        
        # Group actions by time of day (hourly buckets)
        time_buckets = defaultdict(list)
        
        for action in self.action_history:
            hour = datetime.fromtimestamp(action.timestamp).hour
            time_buckets[hour].append(action)
        
        # Look for patterns in specific hours
        for hour, actions in time_buckets.items():
            if len(actions) >= 10:  # Sufficient actions in this hour
                # Analyze what types of actions are common at this time
                action_types = defaultdict(int)
                contexts = defaultdict(int)
                
                for action in actions:
                    action_types[action.action_type] += 1
                    if action.context:
                        contexts[action.context.app_name] += 1
                
                # If there's a dominant pattern, create time-based pattern
                most_common_action = max(action_types, key=action_types.get)
                if action_types[most_common_action] / len(actions) > 0.6:  # 60% of actions
                    pattern = self._create_time_based_pattern(hour, actions, most_common_action)
                    patterns.append(pattern)
        
        return patterns
    
    def _group_similar_actions(self) -> Dict[str, List[ActionEvent]]:
        """Group actions by similarity."""
        groups = defaultdict(list)
        
        for action in self.action_history:
            # Create a key based on action characteristics
            key_parts = [action.action_type]
            
            if action.coordinates:
                # Group by approximate location (100px grid)
                grid_x = action.coordinates[0] // 100
                grid_y = action.coordinates[1] // 100
                key_parts.append(f"grid_{grid_x}_{grid_y}")
            
            if action.context:
                key_parts.append(action.context.app_name)
            
            if action.text_input and len(action.text_input) < 20:
                key_parts.append(f"text_{action.text_input}")
            
            key = "|".join(key_parts)
            groups[key].append(action)
        
        return groups
    
    def _group_similar_sequences(self, sequences: List[List[ActionEvent]]) -> List[List[List[ActionEvent]]]:
        """Group similar action sequences."""
        if not sequences:
            return []
        
        groups = []
        used = set()
        
        for i, seq1 in enumerate(sequences):
            if i in used:
                continue
            
            group = [seq1]
            used.add(i)
            
            for j, seq2 in enumerate(sequences[i+1:], i+1):
                if j in used:
                    continue
                
                if self._calculate_sequence_similarity(seq1, seq2) >= self.similarity_threshold:
                    group.append(seq2)
                    used.add(j)
            
            if len(group) >= 2:  # At least 2 similar sequences
                groups.append(group)
        
        return groups
    
    def _calculate_sequence_similarity(self, seq1: List[ActionEvent], seq2: List[ActionEvent]) -> float:
        """Calculate similarity between two action sequences."""
        if len(seq1) != len(seq2):
            return 0.0
        
        matches = 0
        for a1, a2 in zip(seq1, seq2):
            if self._are_actions_similar(a1, a2):
                matches += 1
        
        return matches / len(seq1)
    
    def _are_actions_similar(self, a1: ActionEvent, a2: ActionEvent) -> bool:
        """Check if two actions are similar."""
        # Same action type
        if a1.action_type != a2.action_type:
            return False
        
        # Similar coordinates (within 50px)
        if a1.coordinates and a2.coordinates:
            dx = abs(a1.coordinates[0] - a2.coordinates[0])
            dy = abs(a1.coordinates[1] - a2.coordinates[1])
            if dx > 50 or dy > 50:
                return False
        
        # Same context
        if a1.context and a2.context:
            if a1.context.app_name != a2.context.app_name:
                return False
        
        # Similar text input
        if a1.text_input and a2.text_input:
            if a1.text_input != a2.text_input:
                return False
        
        return True
    
    def _get_context_sequence_key(self, sequence: List[ContextChangeEvent]) -> str:
        """Get a key representing a context switch sequence."""
        apps = [event.new_context.app_name for event in sequence]
        return "->".join(apps)
    
    def _create_repetitive_pattern(self, actions: List[ActionEvent]) -> UserPattern:
        """Create a repetitive task pattern."""
        pattern_id = f"rep_{int(time.time())}_{hash(str(actions[0].action_type))}"
        
        # Calculate metrics
        occurrences = [a.timestamp for a in actions]
        duration_avg = sum(a.duration for a in actions) / len(actions)
        efficiency_score = self._calculate_efficiency_score(actions)
        automation_potential = self._calculate_automation_potential(actions)
        
        pattern = UserPattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.REPETITIVE_TASK,
            confidence=PatternConfidence.HIGH.value,
            actions=actions,
            contexts=[a.context for a in actions if a.context],
            frequency=len(actions),
            duration_avg=duration_avg,
            first_seen=actions[0].timestamp,
            last_seen=actions[-1].timestamp,
            occurrences=occurrences,
            is_repetitive=True,
            efficiency_score=efficiency_score,
            automation_potential=automation_potential,
            suggested_optimizations=self._suggest_repetitive_optimizations(actions)
        )
        
        return pattern
    
    def _create_workflow_pattern(self, sequence_group: List[List[ActionEvent]]) -> UserPattern:
        """Create a workflow sequence pattern."""
        pattern_id = f"work_{int(time.time())}_{len(sequence_group)}"
        
        # Use first sequence as representative
        representative_actions = sequence_group[0]
        all_actions = [action for seq in sequence_group for action in seq]
        
        occurrences = [seq[0].timestamp for seq in sequence_group]
        contexts = list(set([a.context for a in all_actions if a.context]))
        
        pattern = UserPattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.WORKFLOW_SEQUENCE,
            confidence=PatternConfidence.MEDIUM.value,
            actions=representative_actions,
            contexts=contexts,
            frequency=len(sequence_group),
            duration_avg=sum(seq[-1].timestamp - seq[0].timestamp for seq in sequence_group) / len(sequence_group),
            first_seen=min(occurrences),
            last_seen=max(occurrences),
            occurrences=occurrences,
            involves_context_switch=len(set(a.context.app_name for a in all_actions if a.context)) > 1,
            efficiency_score=self._calculate_efficiency_score(all_actions),
            automation_potential=self._calculate_automation_potential(representative_actions),
            suggested_optimizations=self._suggest_workflow_optimizations(representative_actions)
        )
        
        return pattern
    
    def _create_context_switching_pattern(self, sequences: List[List[ContextChangeEvent]]) -> UserPattern:
        """Create a context switching pattern."""
        pattern_id = f"ctx_{int(time.time())}_{len(sequences)}"
        
        # Convert to action events
        actions = []
        for seq in sequences:
            for event in seq:
                action = ActionEvent(
                    timestamp=event.timestamp,
                    action_type="context_change",
                    context=event.new_context,
                    metadata={'change_type': event.change_type}
                )
                actions.append(action)
        
        occurrences = [seq[0].timestamp for seq in sequences]
        contexts = list(set([event.new_context for seq in sequences for event in seq]))
        
        pattern = UserPattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.CONTEXT_SWITCHING,
            confidence=PatternConfidence.MEDIUM.value,
            actions=actions[:len(sequences[0])],  # Representative sequence
            contexts=contexts,
            frequency=len(sequences),
            duration_avg=sum(seq[-1].timestamp - seq[0].timestamp for seq in sequences) / len(sequences),
            first_seen=min(occurrences),
            last_seen=max(occurrences),
            occurrences=occurrences,
            involves_context_switch=True,
            efficiency_score=self._calculate_context_switch_efficiency(sequences),
            automation_potential=0.4,  # Context switches are moderately automatable
            suggested_optimizations=["Consider grouping related tasks to reduce context switching"]
        )
        
        return pattern
    
    def _create_time_based_pattern(self, hour: int, actions: List[ActionEvent], dominant_action: str) -> UserPattern:
        """Create a time-based pattern."""
        pattern_id = f"time_{hour}_{dominant_action}_{int(time.time())}"
        
        # Filter to dominant action type
        filtered_actions = [a for a in actions if a.action_type == dominant_action]
        occurrences = [a.timestamp for a in filtered_actions]
        
        pattern = UserPattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.TIME_BASED,
            confidence=PatternConfidence.LOW.value,
            actions=filtered_actions[:5],  # Representative sample
            contexts=[a.context for a in filtered_actions if a.context][:5],
            frequency=len(filtered_actions),
            duration_avg=sum(a.duration for a in filtered_actions) / len(filtered_actions) if filtered_actions else 0,
            first_seen=min(occurrences) if occurrences else 0,
            last_seen=max(occurrences) if occurrences else 0,
            occurrences=occurrences,
            efficiency_score=0.5,
            automation_potential=0.6,
            suggested_optimizations=[f"Consider automating {dominant_action} tasks around {hour}:00"],
            metadata={'hour': hour, 'dominant_action': dominant_action}
        )
        
        return pattern
    
    def _calculate_efficiency_score(self, actions: List[ActionEvent]) -> float:
        """Calculate efficiency score for actions (higher = more efficient)."""
        if not actions:
            return 0.0
        
        score = 0.5  # Base score
        
        # Reward fast execution
        avg_duration = sum(a.duration for a in actions) / len(actions)
        if avg_duration < 1.0:  # Less than 1 second per action
            score += 0.2
        elif avg_duration > 5.0:  # More than 5 seconds per action
            score -= 0.2
        
        # Reward consistent timing
        durations = [a.duration for a in actions]
        if durations:
            variance = sum((d - avg_duration) ** 2 for d in durations) / len(durations)
            if variance < 1.0:  # Low variance
                score += 0.1
        
        # Penalty for too many different contexts
        unique_contexts = len(set(a.context.app_name for a in actions if a.context))
        if unique_contexts > 3:
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _calculate_automation_potential(self, actions: List[ActionEvent]) -> float:
        """Calculate how automatable a sequence of actions is."""
        if not actions:
            return 0.0
        
        potential = 0.3  # Base potential
        
        # High potential for repetitive actions
        if len(actions) >= 5:
            potential += 0.3
        
        # Actions in same context are easier to automate
        unique_contexts = len(set(a.context.app_name for a in actions if a.context))
        if unique_contexts <= 2:
            potential += 0.2
        
        # Simple action types are easier to automate
        simple_actions = ['click', 'type', 'key']
        simple_count = sum(1 for a in actions if a.action_type in simple_actions)
        if simple_count / len(actions) > 0.8:
            potential += 0.2
        
        return min(1.0, potential)
    
    def _calculate_context_switch_efficiency(self, sequences: List[List[ContextChangeEvent]]) -> float:
        """Calculate efficiency of context switching patterns."""
        if not sequences:
            return 0.0
        
        # Lower score for more context switches (less efficient)
        avg_switches = sum(len(seq) for seq in sequences) / len(sequences)
        efficiency = max(0.1, 1.0 - (avg_switches - 2) * 0.1)
        
        return min(1.0, efficiency)
    
    def _suggest_repetitive_optimizations(self, actions: List[ActionEvent]) -> List[str]:
        """Suggest optimizations for repetitive patterns."""
        suggestions = []
        
        if len(actions) >= 5:
            suggestions.append("Consider creating a macro or automation for this repetitive task")
        
        # Check for inefficient coordinate clicking
        click_actions = [a for a in actions if a.action_type == 'click']
        if len(click_actions) >= 3:
            suggestions.append("Consider using keyboard shortcuts instead of mouse clicks")
        
        # Check for repetitive typing
        type_actions = [a for a in actions if a.action_type == 'type']
        if len(type_actions) >= 3:
            suggestions.append("Consider using text templates or snippets")
        
        return suggestions
    
    def _suggest_workflow_optimizations(self, actions: List[ActionEvent]) -> List[str]:
        """Suggest optimizations for workflow patterns."""
        suggestions = []
        
        # Check for context switches
        unique_contexts = len(set(a.context.app_name for a in actions if a.context))
        if unique_contexts > 2:
            suggestions.append("Consider grouping tasks by application to reduce context switching")
        
        # Check for long sequences
        if len(actions) > 10:
            suggestions.append("Consider breaking this workflow into smaller, focused tasks")
        
        return suggestions
    
    def _update_existing_patterns(self):
        """Update existing patterns with new occurrences."""
        # This would analyze recent actions against existing patterns
        # and update their frequency, last_seen, etc.
        pass
    
    def _update_analysis_stats(self, analysis_time: float):
        """Update analysis performance statistics."""
        self.analysis_stats['analysis_runs'] += 1
        runs = self.analysis_stats['analysis_runs']
        current_avg = self.analysis_stats['avg_analysis_time']
        self.analysis_stats['avg_analysis_time'] = (current_avg * (runs - 1) + analysis_time) / runs
    
    def get_patterns_by_type(self, pattern_type: PatternType) -> List[UserPattern]:
        """Get patterns of a specific type."""
        return [p for p in self.detected_patterns.values() if p.pattern_type == pattern_type]
    
    def get_high_value_patterns(self, min_automation_potential: float = 0.7) -> List[UserPattern]:
        """Get patterns with high automation potential."""
        return [p for p in self.detected_patterns.values() 
                if p.automation_potential >= min_automation_potential]
    
    def get_recent_patterns(self, hours: int = 24) -> List[UserPattern]:
        """Get patterns detected in recent hours."""
        cutoff = time.time() - (hours * 3600)
        return [p for p in self.detected_patterns.values() if p.last_seen >= cutoff]
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get pattern analysis statistics."""
        stats = self.analysis_stats.copy()
        stats['total_patterns'] = len(self.detected_patterns)
        stats['pattern_types'] = {
            pattern_type.value: len(self.get_patterns_by_type(pattern_type))
            for pattern_type in PatternType
        }
        return stats
    
    def export_patterns(self) -> Dict[str, Any]:
        """Export patterns for storage or analysis."""
        return {
            'patterns': {
                pid: {
                    'pattern_id': p.pattern_id,
                    'pattern_type': p.pattern_type.value,
                    'confidence': p.confidence,
                    'frequency': p.frequency,
                    'duration_avg': p.duration_avg,
                    'first_seen': p.first_seen,
                    'last_seen': p.last_seen,
                    'automation_potential': p.automation_potential,
                    'suggested_optimizations': p.suggested_optimizations,
                    'metadata': p.metadata
                } for pid, p in self.detected_patterns.items()
            },
            'stats': self.get_analysis_stats(),
            'exported_at': time.time()
        }
    
    def cleanup(self):
        """Clean up analyzer resources."""
        self.action_history.clear()
        self.context_history.clear()
        self.detected_patterns.clear()
        logger.info("Pattern analyzer cleaned up")