#!/usr/bin/env python3
"""
Error Recovery Engine

Intelligent failure detection and recovery for robust automation playback.
Handles various failure scenarios with appropriate recovery strategies.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from ..intelligence.context_detector import ContextDetector, ApplicationContext
from .context_verifier import ContextVerifier, VerificationCriteria, VerificationLevel
from .adaptive_executor import AdaptiveExecutor, AdaptationResult


logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of execution failures."""
    CONTEXT_MISMATCH = "context_mismatch"
    ELEMENT_NOT_FOUND = "element_not_found"
    TIMEOUT = "timeout"
    APPLICATION_CRASH = "application_crash"
    PERMISSION_DENIED = "permission_denied"
    NETWORK_ERROR = "network_error"
    UI_STATE_ERROR = "ui_state_error"
    COORDINATE_INVALID = "coordinate_invalid"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    UNKNOWN_ERROR = "unknown_error"


class RecoveryStrategy(Enum):
    """Recovery strategies for different failure types."""
    RETRY_IMMEDIATELY = "retry_immediately"
    RETRY_WITH_DELAY = "retry_with_delay"
    CONTEXT_RESTORATION = "context_restoration"
    APPLICATION_RESTART = "application_restart"
    ALTERNATIVE_METHOD = "alternative_method"
    SKIP_AND_CONTINUE = "skip_and_continue"
    USER_INTERVENTION = "user_intervention"
    ABORT_SEQUENCE = "abort_sequence"


@dataclass
class FailureInfo:
    """Information about an execution failure."""
    failure_type: FailureType
    error_message: str
    failed_action: Dict[str, Any]
    context_at_failure: ApplicationContext
    timestamp: float
    
    # Execution context
    sequence_position: int = 0
    previous_failures: int = 0
    execution_time: float = 0.0
    
    # Diagnostic information
    screenshot_available: bool = False
    log_entries: List[str] = field(default_factory=list)
    system_state: Dict[str, Any] = field(default_factory=dict)
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryAction:
    """A recovery action to be executed."""
    strategy: RecoveryStrategy
    description: str
    action: Callable
    timeout: float = 30.0
    
    # Recovery parameters
    retry_count: int = 0
    delay_before: float = 0.0
    delay_after: float = 0.0
    
    # Success criteria
    success_check: Optional[Callable] = None
    fallback_action: Optional['RecoveryAction'] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryResult:
    """Result of recovery attempt."""
    success: bool
    strategy_used: RecoveryStrategy
    recovery_time: float
    actions_executed: int
    
    # Recovery details
    original_failure: FailureInfo
    recovery_actions_performed: List[str] = field(default_factory=list)
    context_after_recovery: Optional[ApplicationContext] = None
    
    # Quality metrics
    reliability_score: float = 0.0  # How reliable this recovery was
    robustness_score: float = 0.0   # How well it handles edge cases
    
    # Continuation information
    can_continue_sequence: bool = True
    suggested_next_action: Optional[Dict[str, Any]] = None
    
    error_info: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class RecoveryEngine:
    """
    Intelligent error recovery system.
    
    Detects execution failures and applies appropriate recovery strategies
    to maintain robust automation playback.
    """
    
    def __init__(self, context_detector: ContextDetector, context_verifier: ContextVerifier):
        self.context_detector = context_detector
        self.context_verifier = context_verifier
        
        # Recovery history and learning
        self.recovery_history: List[RecoveryResult] = []
        self.successful_strategies: Dict[FailureType, List[RecoveryStrategy]] = {}
        self.failed_strategies: Dict[FailureType, List[RecoveryStrategy]] = {}
        
        # Configuration
        self.config = {
            'max_recovery_attempts': 3,
            'recovery_timeout': 60.0,  # seconds
            'context_restoration_timeout': 30.0,
            'application_restart_timeout': 45.0,
            'user_intervention_timeout': 300.0,  # 5 minutes
            'learning_enabled': True,
            'aggressive_recovery': False
        }
        
        # Recovery strategy mappings
        self.strategy_map = {
            FailureType.CONTEXT_MISMATCH: [
                RecoveryStrategy.CONTEXT_RESTORATION,
                RecoveryStrategy.RETRY_WITH_DELAY,
                RecoveryStrategy.ALTERNATIVE_METHOD
            ],
            FailureType.ELEMENT_NOT_FOUND: [
                RecoveryStrategy.RETRY_WITH_DELAY,
                RecoveryStrategy.ALTERNATIVE_METHOD,
                RecoveryStrategy.CONTEXT_RESTORATION
            ],
            FailureType.TIMEOUT: [
                RecoveryStrategy.RETRY_WITH_DELAY,
                RecoveryStrategy.CONTEXT_RESTORATION,
                RecoveryStrategy.SKIP_AND_CONTINUE
            ],
            FailureType.APPLICATION_CRASH: [
                RecoveryStrategy.APPLICATION_RESTART,
                RecoveryStrategy.CONTEXT_RESTORATION,
                RecoveryStrategy.USER_INTERVENTION
            ],
            FailureType.PERMISSION_DENIED: [
                RecoveryStrategy.USER_INTERVENTION,
                RecoveryStrategy.ALTERNATIVE_METHOD,
                RecoveryStrategy.SKIP_AND_CONTINUE
            ],
            FailureType.UI_STATE_ERROR: [
                RecoveryStrategy.CONTEXT_RESTORATION,
                RecoveryStrategy.RETRY_WITH_DELAY,
                RecoveryStrategy.ALTERNATIVE_METHOD
            ]
        }
        
        # Performance tracking
        self.stats = {
            'total_recoveries': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0,
            'avg_recovery_time': 0.0,
            'strategy_success_rates': {},
            'failure_type_counts': {}
        }
        
        logger.info("Recovery engine initialized")
    
    def handle_failure(self, failure_info: FailureInfo) -> RecoveryResult:
        """
        Handle execution failure with appropriate recovery strategy.
        
        Args:
            failure_info: Information about the failure
            
        Returns:
            Recovery result with outcome details
        """
        start_time = time.time()
        
        try:
            logger.info(f"Handling failure: {failure_info.failure_type.value}")
            
            # Analyze failure and select recovery strategies
            strategies = self._select_recovery_strategies(failure_info)
            
            # Attempt recovery with each strategy
            for i, strategy in enumerate(strategies):
                logger.info(f"Attempting recovery strategy {i+1}/{len(strategies)}: {strategy.value}")
                
                recovery_action = self._create_recovery_action(strategy, failure_info)
                
                if recovery_action:
                    result = self._execute_recovery_action(recovery_action, failure_info)
                    
                    if result.success:
                        # Success! Learn and return
                        recovery_time = time.time() - start_time
                        
                        final_result = RecoveryResult(
                            success=True,
                            strategy_used=strategy,
                            recovery_time=recovery_time,
                            actions_executed=1,
                            original_failure=failure_info,
                            recovery_actions_performed=[recovery_action.description],
                            context_after_recovery=self.context_detector.detect_current_context(),
                            reliability_score=self._calculate_reliability_score(strategy, failure_info),
                            robustness_score=self._calculate_robustness_score(result),
                            can_continue_sequence=self._can_continue_after_recovery(result, failure_info)
                        )
                        
                        self._learn_from_success(failure_info.failure_type, strategy)
                        self._update_stats(final_result)
                        
                        return final_result
                
                # Strategy failed, try next one
                logger.warning(f"Recovery strategy {strategy.value} failed")
                self._learn_from_failure(failure_info.failure_type, strategy)
            
            # All strategies failed
            recovery_time = time.time() - start_time
            
            failed_result = RecoveryResult(
                success=False,
                strategy_used=strategies[-1] if strategies else RecoveryStrategy.ABORT_SEQUENCE,
                recovery_time=recovery_time,
                actions_executed=len(strategies),
                original_failure=failure_info,
                recovery_actions_performed=[s.value for s in strategies],
                can_continue_sequence=False,
                error_info=f"All {len(strategies)} recovery strategies failed"
            )
            
            self._update_stats(failed_result)
            return failed_result
            
        except Exception as e:
            logger.error(f"Recovery handling failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.ABORT_SEQUENCE,
                recovery_time=time.time() - start_time,
                actions_executed=0,
                original_failure=failure_info,
                can_continue_sequence=False,
                error_info=f"Recovery error: {e}"
            )
    
    def _select_recovery_strategies(self, failure_info: FailureInfo) -> List[RecoveryStrategy]:
        """Select appropriate recovery strategies for the failure."""
        
        failure_type = failure_info.failure_type
        
        # Get base strategies for this failure type
        base_strategies = self.strategy_map.get(failure_type, [
            RecoveryStrategy.RETRY_WITH_DELAY,
            RecoveryStrategy.SKIP_AND_CONTINUE,
            RecoveryStrategy.ABORT_SEQUENCE
        ])
        
        # Adjust based on learning
        if self.config['learning_enabled']:
            strategies = self._adjust_strategies_by_learning(failure_type, base_strategies)
        else:
            strategies = base_strategies.copy()
        
        # Adjust based on previous failures
        if failure_info.previous_failures > 2:
            # If we've already failed multiple times, be more aggressive
            if RecoveryStrategy.APPLICATION_RESTART not in strategies:
                strategies.insert(0, RecoveryStrategy.APPLICATION_RESTART)
        
        # Limit strategies based on configuration
        if not self.config['aggressive_recovery']:
            # Remove aggressive strategies in conservative mode
            conservative_strategies = [s for s in strategies if s not in [
                RecoveryStrategy.APPLICATION_RESTART,
                RecoveryStrategy.USER_INTERVENTION
            ]]
            if conservative_strategies:
                strategies = conservative_strategies
        
        return strategies[:self.config['max_recovery_attempts']]
    
    def _adjust_strategies_by_learning(self, failure_type: FailureType, 
                                     base_strategies: List[RecoveryStrategy]) -> List[RecoveryStrategy]:
        """Adjust strategies based on learned success/failure rates."""
        
        successful = self.successful_strategies.get(failure_type, [])
        failed = self.failed_strategies.get(failure_type, [])
        
        # Calculate success rates
        strategy_scores = {}
        for strategy in base_strategies:
            success_count = successful.count(strategy)
            failure_count = failed.count(strategy)
            total = success_count + failure_count
            
            if total > 0:
                strategy_scores[strategy] = success_count / total
            else:
                strategy_scores[strategy] = 0.5  # Neutral score
        
        # Sort strategies by success rate
        sorted_strategies = sorted(base_strategies, 
                                 key=lambda s: strategy_scores.get(s, 0.5), 
                                 reverse=True)
        
        return sorted_strategies
    
    def _create_recovery_action(self, strategy: RecoveryStrategy, 
                              failure_info: FailureInfo) -> Optional[RecoveryAction]:
        """Create a recovery action for the given strategy."""
        
        if strategy == RecoveryStrategy.RETRY_IMMEDIATELY:
            return RecoveryAction(
                strategy=strategy,
                description="Retry failed action immediately",
                action=lambda: self._retry_action(failure_info.failed_action),
                timeout=10.0
            )
        
        elif strategy == RecoveryStrategy.RETRY_WITH_DELAY:
            delay = min(2.0 * (failure_info.previous_failures + 1), 10.0)
            return RecoveryAction(
                strategy=strategy,
                description=f"Retry failed action after {delay}s delay",
                action=lambda: self._retry_action_with_delay(failure_info.failed_action, delay),
                timeout=20.0 + delay,
                delay_before=delay
            )
        
        elif strategy == RecoveryStrategy.CONTEXT_RESTORATION:
            return RecoveryAction(
                strategy=strategy,
                description="Restore expected application context",
                action=lambda: self._restore_context(failure_info),
                timeout=self.config['context_restoration_timeout']
            )
        
        elif strategy == RecoveryStrategy.APPLICATION_RESTART:
            return RecoveryAction(
                strategy=strategy,
                description="Restart application and restore state",
                action=lambda: self._restart_application(failure_info),
                timeout=self.config['application_restart_timeout']
            )
        
        elif strategy == RecoveryStrategy.ALTERNATIVE_METHOD:
            return RecoveryAction(
                strategy=strategy,
                description="Try alternative execution method",
                action=lambda: self._try_alternative_method(failure_info),
                timeout=15.0
            )
        
        elif strategy == RecoveryStrategy.SKIP_AND_CONTINUE:
            return RecoveryAction(
                strategy=strategy,
                description="Skip failed action and continue sequence",
                action=lambda: self._skip_action(failure_info),
                timeout=1.0
            )
        
        elif strategy == RecoveryStrategy.USER_INTERVENTION:
            return RecoveryAction(
                strategy=strategy,
                description="Request user intervention",
                action=lambda: self._request_user_intervention(failure_info),
                timeout=self.config['user_intervention_timeout']
            )
        
        else:
            # ABORT_SEQUENCE
            return RecoveryAction(
                strategy=strategy,
                description="Abort automation sequence",
                action=lambda: {'success': False, 'aborted': True},
                timeout=1.0
            )
    
    def _execute_recovery_action(self, action: RecoveryAction, 
                               failure_info: FailureInfo) -> RecoveryResult:
        """Execute a recovery action and return result."""
        
        try:
            # Wait before execution if specified
            if action.delay_before > 0:
                time.sleep(action.delay_before)
            
            start_time = time.time()
            
            # Execute the recovery action
            result = action.action()
            
            execution_time = time.time() - start_time
            
            # Check success
            if isinstance(result, dict):
                success = result.get('success', False)
            else:
                success = bool(result)
            
            # Wait after execution if specified
            if action.delay_after > 0:
                time.sleep(action.delay_after)
            
            return RecoveryResult(
                success=success,
                strategy_used=action.strategy,
                recovery_time=execution_time,
                actions_executed=1,
                original_failure=failure_info,
                recovery_actions_performed=[action.description],
                metadata={'action_result': result}
            )
            
        except Exception as e:
            logger.error(f"Recovery action execution failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=action.strategy,
                recovery_time=time.time() - start_time if 'start_time' in locals() else 0.0,
                actions_executed=1,
                original_failure=failure_info,
                error_info=f"Recovery action error: {e}"
            )
    
    def _retry_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Retry the failed action."""
        # For now, simulate retry
        return {'success': True, 'retried': True}
    
    def _retry_action_with_delay(self, action: Dict[str, Any], delay: float) -> Dict[str, Any]:
        """Retry the failed action after a delay."""
        time.sleep(delay)
        return self._retry_action(action)
    
    def _restore_context(self, failure_info: FailureInfo) -> Dict[str, Any]:
        """Restore the expected application context."""
        
        try:
            # Get current context
            current_context = self.context_detector.detect_current_context()
            
            # Create verification criteria based on failure context
            criteria = VerificationCriteria(
                required_app_name=failure_info.context_at_failure.app_name,
                required_context_type=failure_info.context_at_failure.context_type,
                min_confidence_threshold=0.6
            )
            
            # Check if context already matches
            verification = self.context_verifier.verify_context(criteria)
            
            if verification.status.value in ['verified', 'warning']:
                return {'success': True, 'already_restored': True}
            
            # Try to restore context
            # This would involve focusing the right application, etc.
            # For now, simulate context restoration
            
            # Wait a bit for context to stabilize
            time.sleep(2.0)
            
            # Re-verify
            verification = self.context_verifier.verify_context(criteria)
            
            return {
                'success': verification.status.value in ['verified', 'warning'],
                'verification_status': verification.status.value,
                'confidence': verification.confidence
            }
            
        except Exception as e:
            logger.error(f"Context restoration failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _restart_application(self, failure_info: FailureInfo) -> Dict[str, Any]:
        """Restart the application and restore state."""
        
        try:
            app_name = failure_info.context_at_failure.app_name
            
            # For now, simulate application restart
            logger.info(f"Simulating restart of application: {app_name}")
            
            # This would involve:
            # 1. Closing the application
            # 2. Starting it again  
            # 3. Navigating back to the required state
            
            # Simulate restart time
            time.sleep(5.0)
            
            return {'success': True, 'application_restarted': app_name}
            
        except Exception as e:
            logger.error(f"Application restart failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _try_alternative_method(self, failure_info: FailureInfo) -> Dict[str, Any]:
        """Try alternative method for the failed action."""
        
        action = failure_info.failed_action
        action_type = action.get('type', 'unknown')
        
        # Suggest alternative methods based on action type
        if action_type == 'click':
            # Try keyboard shortcut instead
            if 'text' in action:
                return {'success': True, 'alternative': 'keyboard_shortcut'}
        
        elif action_type == 'type':
            # Try clipboard paste instead
            return {'success': True, 'alternative': 'clipboard_paste'}
        
        # No alternative available
        return {'success': False, 'reason': 'no_alternative_available'}
    
    def _skip_action(self, failure_info: FailureInfo) -> Dict[str, Any]:
        """Skip the failed action and continue."""
        return {'success': True, 'skipped': True}
    
    def _request_user_intervention(self, failure_info: FailureInfo) -> Dict[str, Any]:
        """Request user intervention to resolve the issue."""
        
        # For now, simulate user intervention request
        logger.warning(f"User intervention requested for: {failure_info.error_message}")
        
        # This would involve:
        # 1. Pausing automation
        # 2. Showing user a dialog with the issue
        # 3. Waiting for user to resolve and continue
        
        # Simulate user resolving the issue
        time.sleep(2.0)  # Simulate quick user action
        
        return {'success': True, 'user_intervened': True}
    
    def _calculate_reliability_score(self, strategy: RecoveryStrategy, 
                                   failure_info: FailureInfo) -> float:
        """Calculate reliability score for recovery strategy."""
        
        base_scores = {
            RecoveryStrategy.RETRY_IMMEDIATELY: 0.3,
            RecoveryStrategy.RETRY_WITH_DELAY: 0.6,
            RecoveryStrategy.CONTEXT_RESTORATION: 0.7,
            RecoveryStrategy.APPLICATION_RESTART: 0.8,
            RecoveryStrategy.ALTERNATIVE_METHOD: 0.5,
            RecoveryStrategy.SKIP_AND_CONTINUE: 0.9,  # Always "succeeds"
            RecoveryStrategy.USER_INTERVENTION: 0.9,  # User usually resolves
            RecoveryStrategy.ABORT_SEQUENCE: 0.0
        }
        
        base_score = base_scores.get(strategy, 0.5)
        
        # Adjust based on learning
        if self.config['learning_enabled']:
            failure_type = failure_info.failure_type
            successful = self.successful_strategies.get(failure_type, [])
            failed = self.failed_strategies.get(failure_type, [])
            
            success_count = successful.count(strategy)
            failure_count = failed.count(strategy)
            total = success_count + failure_count
            
            if total >= 3:  # Enough data to learn
                learned_score = success_count / total
                # Weighted average with base score
                base_score = (base_score + learned_score * 2) / 3
        
        return base_score
    
    def _calculate_robustness_score(self, result: RecoveryResult) -> float:
        """Calculate robustness score for recovery result."""
        
        # Base score from strategy
        strategy_robustness = {
            RecoveryStrategy.APPLICATION_RESTART: 0.9,  # Very robust
            RecoveryStrategy.CONTEXT_RESTORATION: 0.7,
            RecoveryStrategy.USER_INTERVENTION: 0.8,
            RecoveryStrategy.RETRY_WITH_DELAY: 0.5,
            RecoveryStrategy.ALTERNATIVE_METHOD: 0.6,
            RecoveryStrategy.SKIP_AND_CONTINUE: 0.3,    # Low robustness
            RecoveryStrategy.RETRY_IMMEDIATELY: 0.2
        }
        
        return strategy_robustness.get(result.strategy_used, 0.5)
    
    def _can_continue_after_recovery(self, result: RecoveryResult, 
                                   failure_info: FailureInfo) -> bool:
        """Determine if sequence can continue after recovery."""
        
        if not result.success:
            return False
        
        # Some strategies always allow continuation
        always_continue = [
            RecoveryStrategy.SKIP_AND_CONTINUE,
            RecoveryStrategy.USER_INTERVENTION
        ]
        
        if result.strategy_used in always_continue:
            return True
        
        # For other strategies, check if context is suitable
        try:
            current_context = self.context_detector.detect_current_context()
            return current_context.confidence >= 0.5
        except:
            return False
    
    def _learn_from_success(self, failure_type: FailureType, strategy: RecoveryStrategy):
        """Learn from successful recovery."""
        if not self.config['learning_enabled']:
            return
        
        if failure_type not in self.successful_strategies:
            self.successful_strategies[failure_type] = []
        
        self.successful_strategies[failure_type].append(strategy)
        
        # Keep only recent successes
        if len(self.successful_strategies[failure_type]) > 50:
            self.successful_strategies[failure_type] = \
                self.successful_strategies[failure_type][-50:]
    
    def _learn_from_failure(self, failure_type: FailureType, strategy: RecoveryStrategy):
        """Learn from failed recovery."""
        if not self.config['learning_enabled']:
            return
        
        if failure_type not in self.failed_strategies:
            self.failed_strategies[failure_type] = []
        
        self.failed_strategies[failure_type].append(strategy)
        
        # Keep only recent failures
        if len(self.failed_strategies[failure_type]) > 25:
            self.failed_strategies[failure_type] = \
                self.failed_strategies[failure_type][-25:]
    
    def _update_stats(self, result: RecoveryResult):
        """Update recovery statistics."""
        self.stats['total_recoveries'] += 1
        
        if result.success:
            self.stats['successful_recoveries'] += 1
        else:
            self.stats['failed_recoveries'] += 1
        
        # Update average recovery time
        count = self.stats['total_recoveries']
        current_avg = self.stats['avg_recovery_time']
        self.stats['avg_recovery_time'] = (current_avg * (count - 1) + result.recovery_time) / count
        
        # Update strategy success rates
        strategy = result.strategy_used.value
        if strategy not in self.stats['strategy_success_rates']:
            self.stats['strategy_success_rates'][strategy] = {'successes': 0, 'total': 0}
        
        self.stats['strategy_success_rates'][strategy]['total'] += 1
        if result.success:
            self.stats['strategy_success_rates'][strategy]['successes'] += 1
        
        # Update failure type counts
        failure_type = result.original_failure.failure_type.value
        if failure_type not in self.stats['failure_type_counts']:
            self.stats['failure_type_counts'][failure_type] = 0
        self.stats['failure_type_counts'][failure_type] += 1
    
    def classify_failure(self, error: Exception, context: ApplicationContext, 
                        action: Dict[str, Any]) -> FailureType:
        """Classify an error into a failure type."""
        
        error_str = str(error).lower()
        
        if 'timeout' in error_str or 'timed out' in error_str:
            return FailureType.TIMEOUT
        elif 'permission' in error_str or 'access denied' in error_str:
            return FailureType.PERMISSION_DENIED
        elif 'network' in error_str or 'connection' in error_str:
            return FailureType.NETWORK_ERROR
        elif 'element not found' in error_str or 'not found' in error_str:
            return FailureType.ELEMENT_NOT_FOUND
        elif 'context' in error_str or 'window' in error_str:
            return FailureType.CONTEXT_MISMATCH
        elif 'coordinate' in error_str or 'invalid position' in error_str:
            return FailureType.COORDINATE_INVALID
        else:
            return FailureType.UNKNOWN_ERROR
    
    def create_failure_info(self, error: Exception, action: Dict[str, Any],
                           context: ApplicationContext, sequence_position: int = 0) -> FailureInfo:
        """Create failure info from an error."""
        
        failure_type = self.classify_failure(error, context, action)
        
        return FailureInfo(
            failure_type=failure_type,
            error_message=str(error),
            failed_action=action,
            context_at_failure=context,
            timestamp=time.time(),
            sequence_position=sequence_position
        )
    
    def get_recovery_history(self, limit: int = 20) -> List[RecoveryResult]:
        """Get recent recovery history."""
        return self.recovery_history[-limit:]
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery performance statistics."""
        stats = self.stats.copy()
        
        if stats['total_recoveries'] > 0:
            stats['success_rate'] = stats['successful_recoveries'] / stats['total_recoveries']
        else:
            stats['success_rate'] = 0.0
        
        # Calculate strategy success rates
        for strategy, data in stats['strategy_success_rates'].items():
            if data['total'] > 0:
                data['success_rate'] = data['successes'] / data['total']
            else:
                data['success_rate'] = 0.0
        
        return stats
    
    def update_config(self, **kwargs):
        """Update recovery engine configuration."""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                logger.info(f"Updated recovery engine config: {key} = {value}")
    
    def cleanup(self):
        """Clean up recovery engine resources."""
        self.recovery_history.clear()
        self.successful_strategies.clear()
        self.failed_strategies.clear()
        logger.info("Recovery engine cleaned up")