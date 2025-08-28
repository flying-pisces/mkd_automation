#!/usr/bin/env python3
"""
Smart Recording System

Provides intelligent recording decisions based on context analysis and user patterns.
Determines when to start/stop recording, what to capture, and how to optimize recordings.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum

from .context_detector import ContextDetector, ApplicationContext, ContextChangeEvent
from .pattern_analyzer import PatternAnalyzer, UserPattern, PatternType, ActionEvent


logger = logging.getLogger(__name__)


class RecordingTrigger(Enum):
    """Types of recording triggers."""
    MANUAL = "manual"
    CONTEXT_CHANGE = "context_change"
    PATTERN_DETECTED = "pattern_detected" 
    TIME_BASED = "time_based"
    ERROR_RECOVERY = "error_recovery"
    EFFICIENCY_OPPORTUNITY = "efficiency_opportunity"


class RecordingPriority(Enum):
    """Recording priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class RecordingDecision:
    """Represents a smart recording decision."""
    should_record: bool
    trigger: RecordingTrigger
    priority: RecordingPriority
    context: ApplicationContext
    
    # Decision details
    confidence: float  # 0.0-1.0, confidence in this decision
    reason: str  # Human-readable reason for the decision
    expected_duration: float = 0.0  # Expected recording duration in seconds
    
    # Recording parameters
    capture_video: bool = False
    capture_audio: bool = False
    capture_keyboard: bool = True
    capture_mouse: bool = True
    
    # Optimization hints
    focus_areas: List[Dict[str, int]] = field(default_factory=list)  # Screen regions to focus on
    ignore_areas: List[Dict[str, int]] = field(default_factory=list)  # Areas to ignore
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecordingSession:
    """Represents an active recording session."""
    session_id: str
    start_time: float
    trigger: RecordingTrigger
    initial_context: ApplicationContext
    
    # Session tracking
    contexts_seen: List[ApplicationContext] = field(default_factory=list)
    actions_recorded: int = 0
    significant_events: List[str] = field(default_factory=list)
    
    # Quality metrics
    context_stability: float = 1.0  # How stable the context has been
    user_engagement: float = 1.0    # How actively the user is working
    recording_quality: float = 1.0  # Overall recording quality
    
    # Auto-stop conditions
    max_duration: float = 300.0  # 5 minutes default
    auto_stop_on_idle: bool = True
    auto_stop_on_context_loss: bool = True
    
    metadata: Dict[str, Any] = field(default_factory=dict)


class SmartRecorder:
    """
    Intelligent recording system.
    
    Makes smart decisions about when and how to record user actions
    based on context analysis and behavior patterns.
    """
    
    def __init__(self, context_detector: ContextDetector, pattern_analyzer: PatternAnalyzer):
        self.context_detector = context_detector
        self.pattern_analyzer = pattern_analyzer
        
        self.active_sessions: Dict[str, RecordingSession] = {}
        self.recording_history: List[RecordingSession] = []
        
        # Configuration
        self.config = {
            'auto_recording_enabled': True,
            'min_pattern_confidence': 0.6,
            'min_context_stability': 2.0,  # seconds
            'max_concurrent_sessions': 3,
            'idle_timeout': 30.0,  # seconds
            'context_loss_timeout': 10.0  # seconds
        }
        
        # Decision weights
        self.decision_weights = {
            'context_confidence': 0.3,
            'pattern_strength': 0.25,
            'user_activity': 0.2,
            'efficiency_potential': 0.15,
            'resource_availability': 0.1
        }
        
        # Statistics
        self.stats = {
            'decisions_made': 0,
            'recordings_started': 0,
            'recordings_stopped': 0,
            'auto_recordings': 0,
            'manual_recordings': 0,
            'avg_decision_time': 0.0
        }
        
        # Set up context change listener
        self.context_detector.add_change_listener(self._on_context_change)
        
        logger.info("Smart recorder initialized")
    
    def should_start_recording(self, current_context: Optional[ApplicationContext] = None) -> RecordingDecision:
        """
        Determine if recording should start based on current conditions.
        
        Args:
            current_context: Current context (detected automatically if None)
            
        Returns:
            Recording decision with details
        """
        start_time = time.time()
        
        try:
            # Get current context
            if current_context is None:
                current_context = self.context_detector.detect_current_context()
            
            # Check if already recording in this context
            if self._is_already_recording_context(current_context):
                return RecordingDecision(
                    should_record=False,
                    trigger=RecordingTrigger.MANUAL,
                    priority=RecordingPriority.LOW,
                    context=current_context,
                    confidence=0.9,
                    reason="Already recording in this context"
                )
            
            # Analyze different triggers
            decisions = []
            
            # Manual trigger (always allowed)
            decisions.append(self._evaluate_manual_trigger(current_context))
            
            # Context-based trigger
            decisions.append(self._evaluate_context_trigger(current_context))
            
            # Pattern-based trigger
            decisions.append(self._evaluate_pattern_trigger(current_context))
            
            # Time-based trigger
            decisions.append(self._evaluate_time_trigger(current_context))
            
            # Select best decision
            best_decision = self._select_best_decision(decisions)
            
            # Update statistics
            decision_time = time.time() - start_time
            self._update_decision_stats(decision_time)
            
            if best_decision.should_record:
                logger.info(f"Recording decision: START ({best_decision.trigger.value}) - {best_decision.reason}")
            
            return best_decision
            
        except Exception as e:
            logger.error(f"Recording decision failed: {e}")
            return RecordingDecision(
                should_record=False,
                trigger=RecordingTrigger.MANUAL,
                priority=RecordingPriority.LOW,
                context=current_context or self.context_detector._create_unknown_context(),
                confidence=0.0,
                reason=f"Error in decision making: {e}"
            )
    
    def start_recording_session(self, decision: RecordingDecision) -> str:
        """
        Start a new recording session based on a decision.
        
        Args:
            decision: Recording decision from should_start_recording
            
        Returns:
            Session ID
        """
        if not decision.should_record:
            raise ValueError("Cannot start recording: decision is negative")
        
        # Check session limits
        if len(self.active_sessions) >= self.config['max_concurrent_sessions']:
            # Stop lowest priority session
            self._stop_lowest_priority_session()
        
        # Create session
        session_id = f"session_{int(time.time())}_{len(self.active_sessions)}"
        
        session = RecordingSession(
            session_id=session_id,
            start_time=time.time(),
            trigger=decision.trigger,
            initial_context=decision.context,
            max_duration=decision.expected_duration if decision.expected_duration > 0 else 300.0,
            metadata={
                'decision_confidence': decision.confidence,
                'decision_reason': decision.reason,
                'capture_settings': {
                    'video': decision.capture_video,
                    'audio': decision.capture_audio,
                    'keyboard': decision.capture_keyboard,
                    'mouse': decision.capture_mouse
                }
            }
        )
        
        self.active_sessions[session_id] = session
        self.stats['recordings_started'] += 1
        
        if decision.trigger != RecordingTrigger.MANUAL:
            self.stats['auto_recordings'] += 1
        else:
            self.stats['manual_recordings'] += 1
        
        logger.info(f"Started recording session: {session_id} ({decision.trigger.value})")
        return session_id
    
    def should_stop_recording(self, session_id: str) -> bool:
        """
        Determine if a recording session should stop.
        
        Args:
            session_id: ID of active recording session
            
        Returns:
            True if recording should stop
        """
        if session_id not in self.active_sessions:
            return True  # Session doesn't exist, should stop
        
        session = self.active_sessions[session_id]
        current_time = time.time()
        session_duration = current_time - session.start_time
        
        # Check max duration
        if session_duration >= session.max_duration:
            logger.info(f"Stopping session {session_id}: max duration reached")
            return True
        
        # Check idle timeout
        if session.auto_stop_on_idle:
            # This would check actual user activity - simplified for now
            if self._is_user_idle():
                logger.info(f"Stopping session {session_id}: user idle")
                return True
        
        # Check context loss
        if session.auto_stop_on_context_loss:
            current_context = self.context_detector.detect_current_context()
            if not self._is_context_relevant(session.initial_context, current_context):
                logger.info(f"Stopping session {session_id}: context lost")
                return True
        
        # Check recording quality
        if session.recording_quality < 0.3:  # Very poor quality
            logger.info(f"Stopping session {session_id}: poor quality")
            return True
        
        return False
    
    def stop_recording_session(self, session_id: str, reason: str = "Manual stop"):
        """
        Stop a recording session.
        
        Args:
            session_id: ID of session to stop
            reason: Reason for stopping
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Cannot stop session {session_id}: not found")
            return
        
        session = self.active_sessions[session_id]
        session.metadata['stop_reason'] = reason
        session.metadata['final_duration'] = time.time() - session.start_time
        
        # Move to history
        self.recording_history.append(session)
        del self.active_sessions[session_id]
        
        self.stats['recordings_stopped'] += 1
        
        logger.info(f"Stopped recording session: {session_id} - {reason}")
    
    def update_session_metrics(self, session_id: str, actions_recorded: int = 0, 
                             context_changes: int = 0):
        """Update metrics for an active recording session."""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        session.actions_recorded += actions_recorded
        
        # Update quality metrics
        current_context = self.context_detector.detect_current_context()
        
        # Context stability (how much context has changed)
        context_similarity = self._calculate_context_similarity(
            session.initial_context, current_context
        )
        session.context_stability = (session.context_stability + context_similarity) / 2
        
        # User engagement (based on action frequency)
        session_duration = time.time() - session.start_time
        if session_duration > 0:
            actions_per_second = session.actions_recorded / session_duration
            engagement = min(1.0, actions_per_second / 0.5)  # Normalize to 0.5 actions/sec
            session.user_engagement = (session.user_engagement + engagement) / 2
        
        # Overall quality
        session.recording_quality = (
            session.context_stability * 0.5 +
            session.user_engagement * 0.5
        )
    
    def _evaluate_manual_trigger(self, context: ApplicationContext) -> RecordingDecision:
        """Evaluate manual recording trigger."""
        return RecordingDecision(
            should_record=True,  # Manual is always allowed
            trigger=RecordingTrigger.MANUAL,
            priority=RecordingPriority.HIGH,
            context=context,
            confidence=1.0,
            reason="Manual recording request",
            expected_duration=60.0,  # Default 1 minute
            capture_video=True,
            capture_keyboard=True,
            capture_mouse=True
        )
    
    def _evaluate_context_trigger(self, context: ApplicationContext) -> RecordingDecision:
        """Evaluate context-based recording trigger."""
        should_record = False
        confidence = 0.0
        reason = "Context analysis"
        
        # Check if context is worth recording
        if context.confidence >= 0.8:  # High confidence context
            should_record = True
            confidence = context.confidence
            reason = f"High-confidence context: {context.app_name}"
        
        # Check for interesting context types
        interesting_contexts = {
            'WEB_BROWSER', 'DEVELOPMENT_IDE', 'TEXT_EDITOR'
        }
        if context.context_type.name in interesting_contexts:
            should_record = True
            confidence = max(confidence, 0.6)
            reason = f"Interesting context type: {context.context_type.name}"
        
        # Check context stability
        if self.context_detector.is_context_stable(duration=3.0):
            confidence += 0.2
            reason += " (stable context)"
        
        return RecordingDecision(
            should_record=should_record,
            trigger=RecordingTrigger.CONTEXT_CHANGE,
            priority=RecordingPriority.MEDIUM,
            context=context,
            confidence=min(confidence, 1.0),
            reason=reason,
            expected_duration=120.0,  # 2 minutes
            capture_video=False,  # Context-based doesn't need video by default
            capture_keyboard=True,
            capture_mouse=True
        )
    
    def _evaluate_pattern_trigger(self, context: ApplicationContext) -> RecordingDecision:
        """Evaluate pattern-based recording trigger."""
        should_record = False
        confidence = 0.0
        reason = "Pattern analysis"
        
        # Get high-value patterns
        high_value_patterns = self.pattern_analyzer.get_high_value_patterns(
            min_automation_potential=0.7
        )
        
        if high_value_patterns:
            # Check if current context matches high-value patterns
            for pattern in high_value_patterns:
                if self._pattern_matches_context(pattern, context):
                    should_record = True
                    confidence = pattern.confidence * pattern.automation_potential
                    reason = f"High-value pattern detected: {pattern.pattern_type.value}"
                    break
        
        # Check for repetitive patterns that could be automated
        recent_patterns = self.pattern_analyzer.get_recent_patterns(hours=1)
        repetitive_patterns = [p for p in recent_patterns 
                             if p.pattern_type == PatternType.REPETITIVE_TASK]
        
        if repetitive_patterns and not should_record:
            best_pattern = max(repetitive_patterns, key=lambda p: p.frequency)
            if best_pattern.frequency >= 3:  # Repeated at least 3 times
                should_record = True
                confidence = 0.7
                reason = f"Repetitive pattern: {best_pattern.frequency} occurrences"
        
        return RecordingDecision(
            should_record=should_record,
            trigger=RecordingTrigger.PATTERN_DETECTED,
            priority=RecordingPriority.HIGH if confidence > 0.8 else RecordingPriority.MEDIUM,
            context=context,
            confidence=confidence,
            reason=reason,
            expected_duration=180.0,  # 3 minutes
            capture_video=True,  # Pattern-based benefits from video
            capture_keyboard=True,
            capture_mouse=True
        )
    
    def _evaluate_time_trigger(self, context: ApplicationContext) -> RecordingDecision:
        """Evaluate time-based recording trigger."""
        should_record = False
        confidence = 0.0
        reason = "Time-based analysis"
        
        # Check for time-based patterns
        time_patterns = self.pattern_analyzer.get_patterns_by_type(PatternType.TIME_BASED)
        current_hour = time.localtime().tm_hour
        
        for pattern in time_patterns:
            pattern_hour = pattern.metadata.get('hour', -1)
            if pattern_hour == current_hour and pattern.frequency >= 3:
                should_record = True
                confidence = 0.5
                reason = f"Time-based pattern at {current_hour}:00"
                break
        
        return RecordingDecision(
            should_record=should_record,
            trigger=RecordingTrigger.TIME_BASED,
            priority=RecordingPriority.LOW,
            context=context,
            confidence=confidence,
            reason=reason,
            expected_duration=90.0,  # 1.5 minutes
            capture_video=False,
            capture_keyboard=True,
            capture_mouse=True
        )
    
    def _select_best_decision(self, decisions: List[RecordingDecision]) -> RecordingDecision:
        """Select the best recording decision from candidates."""
        if not decisions:
            # Default negative decision
            return RecordingDecision(
                should_record=False,
                trigger=RecordingTrigger.MANUAL,
                priority=RecordingPriority.LOW,
                context=self.context_detector._create_unknown_context(),
                confidence=0.0,
                reason="No valid decisions available"
            )
        
        # Filter positive decisions
        positive_decisions = [d for d in decisions if d.should_record]
        
        if not positive_decisions:
            # Return the best negative decision
            return max(decisions, key=lambda d: d.confidence)
        
        # Score decisions based on multiple factors
        scored_decisions = []
        for decision in positive_decisions:
            score = self._calculate_decision_score(decision)
            scored_decisions.append((score, decision))
        
        # Return highest scoring decision
        best_score, best_decision = max(scored_decisions, key=lambda x: x[0])
        return best_decision
    
    def _calculate_decision_score(self, decision: RecordingDecision) -> float:
        """Calculate a composite score for a recording decision."""
        score = 0.0
        
        # Base confidence
        score += decision.confidence * self.decision_weights['context_confidence']
        
        # Priority weighting
        priority_multiplier = {
            RecordingPriority.LOW: 0.5,
            RecordingPriority.MEDIUM: 0.75,
            RecordingPriority.HIGH: 1.0,
            RecordingPriority.CRITICAL: 1.25
        }
        score *= priority_multiplier[decision.priority]
        
        # Trigger type weighting
        trigger_multiplier = {
            RecordingTrigger.MANUAL: 1.0,
            RecordingTrigger.PATTERN_DETECTED: 0.9,
            RecordingTrigger.CONTEXT_CHANGE: 0.8,
            RecordingTrigger.TIME_BASED: 0.6,
            RecordingTrigger.ERROR_RECOVERY: 1.1,
            RecordingTrigger.EFFICIENCY_OPPORTUNITY: 0.95
        }
        score *= trigger_multiplier.get(decision.trigger, 0.5)
        
        # Resource consideration (prefer lighter recordings when resources are limited)
        resource_cost = 0.1  # Base cost
        if decision.capture_video:
            resource_cost += 0.3
        if decision.capture_audio:
            resource_cost += 0.2
        
        resource_factor = max(0.1, 1.0 - resource_cost)
        score *= resource_factor
        
        return score
    
    def _is_already_recording_context(self, context: ApplicationContext) -> bool:
        """Check if already recording in similar context."""
        for session in self.active_sessions.values():
            if self._is_context_relevant(session.initial_context, context):
                return True
        return False
    
    def _is_context_relevant(self, context1: ApplicationContext, context2: ApplicationContext) -> bool:
        """Check if two contexts are similar enough to be considered the same."""
        return (
            context1.process_name == context2.process_name and
            context1.context_type == context2.context_type
        )
    
    def _calculate_context_similarity(self, context1: ApplicationContext, context2: ApplicationContext) -> float:
        """Calculate similarity between two contexts (0.0-1.0)."""
        similarity = 0.0
        
        if context1.process_name == context2.process_name:
            similarity += 0.4
        
        if context1.context_type == context2.context_type:
            similarity += 0.3
        
        if context1.window_title == context2.window_title:
            similarity += 0.2
        
        if context1.ui_state == context2.ui_state:
            similarity += 0.1
        
        return similarity
    
    def _pattern_matches_context(self, pattern: UserPattern, context: ApplicationContext) -> bool:
        """Check if a pattern matches the current context."""
        # Check if pattern contexts include current context
        for pattern_context in pattern.contexts:
            if pattern_context and self._is_context_relevant(pattern_context, context):
                return True
        return False
    
    def _is_user_idle(self) -> bool:
        """Check if user appears to be idle (simplified implementation)."""
        # This would check actual user activity metrics
        # For now, use a simple heuristic based on context stability
        return self.context_detector.is_context_stable(duration=30.0)
    
    def _stop_lowest_priority_session(self):
        """Stop the session with lowest priority to make room for new ones."""
        if not self.active_sessions:
            return
        
        # Find session with lowest priority/score
        lowest_session_id = None
        lowest_score = float('inf')
        
        for session_id, session in self.active_sessions.items():
            # Simple scoring based on trigger priority
            trigger_scores = {
                RecordingTrigger.MANUAL: 4,
                RecordingTrigger.PATTERN_DETECTED: 3,
                RecordingTrigger.CONTEXT_CHANGE: 2,
                RecordingTrigger.TIME_BASED: 1
            }
            
            score = trigger_scores.get(session.trigger, 0)
            if score < lowest_score:
                lowest_score = score
                lowest_session_id = session_id
        
        if lowest_session_id:
            self.stop_recording_session(lowest_session_id, "Session limit reached")
    
    def _update_decision_stats(self, decision_time: float):
        """Update decision-making statistics."""
        self.stats['decisions_made'] += 1
        count = self.stats['decisions_made']
        current_avg = self.stats['avg_decision_time']
        self.stats['avg_decision_time'] = (current_avg * (count - 1) + decision_time) / count
    
    def _on_context_change(self, event: ContextChangeEvent):
        """Handle context change events."""
        # Check if this context change should trigger recording
        if event.significance > 0.5:  # Significant change
            decision = self.should_start_recording(event.new_context)
            if decision.should_record and self.config['auto_recording_enabled']:
                try:
                    session_id = self.start_recording_session(decision)
                    logger.info(f"Auto-started recording due to context change: {session_id}")
                except Exception as e:
                    logger.error(f"Failed to auto-start recording: {e}")
        
        # Update existing sessions
        for session in self.active_sessions.values():
            session.contexts_seen.append(event.new_context)
            if event.significance > 0.3:
                session.significant_events.append(f"Context change: {event.change_type}")
    
    def get_active_sessions(self) -> List[RecordingSession]:
        """Get all active recording sessions."""
        return list(self.active_sessions.values())
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a recording session."""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        return {
            'session_id': session_id,
            'start_time': session.start_time,
            'duration': time.time() - session.start_time,
            'trigger': session.trigger.value,
            'actions_recorded': session.actions_recorded,
            'context_stability': session.context_stability,
            'user_engagement': session.user_engagement,
            'recording_quality': session.recording_quality,
            'contexts_seen': len(session.contexts_seen),
            'significant_events': len(session.significant_events)
        }
    
    def get_smart_recorder_stats(self) -> Dict[str, Any]:
        """Get smart recorder statistics."""
        stats = self.stats.copy()
        stats['active_sessions'] = len(self.active_sessions)
        stats['total_sessions'] = len(self.recording_history) + len(self.active_sessions)
        stats['config'] = self.config.copy()
        return stats
    
    def update_config(self, **kwargs):
        """Update recorder configuration."""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                logger.info(f"Updated config: {key} = {value}")
    
    def cleanup(self):
        """Clean up recorder resources."""
        # Stop all active sessions
        for session_id in list(self.active_sessions.keys()):
            self.stop_recording_session(session_id, "Cleanup")
        
        # Remove context listener
        self.context_detector.remove_change_listener(self._on_context_change)
        
        logger.info("Smart recorder cleaned up")