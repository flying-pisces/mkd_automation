"""
Advanced Playback Engine

Integrates all advanced playback components into a unified system:
- Context verification before execution
- Adaptive execution with intelligent adjustments
- Comprehensive error recovery
- Performance optimization throughout
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import time
import logging

from .context_verifier import ContextVerifier, VerificationLevel, VerificationCriteria, VerificationResult
from .adaptive_executor import AdaptiveExecutor, AdaptationStrategy, AdaptationResult
from .recovery_engine import RecoveryEngine, RecoveryStrategy, FailureInfo, RecoveryResult
from .performance_optimizer import PerformanceOptimizer, OptimizationLevel, OptimizationResult

logger = logging.getLogger(__name__)


class PlaybackMode(Enum):
    """Advanced playback execution modes"""
    STANDARD = "standard"           # Normal execution with basic optimization
    SAFE = "safe"                  # Conservative with extensive verification
    FAST = "fast"                  # Aggressive optimization for speed
    ADAPTIVE = "adaptive"          # Dynamic adjustment based on conditions
    RECOVERY = "recovery"          # Focus on error recovery and reliability


@dataclass 
class PlaybackConfig:
    """Configuration for advanced playback execution"""
    mode: PlaybackMode = PlaybackMode.ADAPTIVE
    verification_level: VerificationLevel = VerificationLevel.STANDARD
    adaptation_strategy: AdaptationStrategy = AdaptationStrategy.BALANCED
    optimization_level: OptimizationLevel = OptimizationLevel.BALANCED
    recovery_enabled: bool = True
    max_retry_attempts: int = 3
    timeout_per_action: float = 30.0
    failure_threshold: float = 0.1  # 10% failure rate threshold
    performance_monitoring: bool = True


@dataclass
class PlaybackResult:
    """Result of advanced playback execution"""
    success: bool
    total_actions: int
    successful_actions: int
    failed_actions: int
    execution_time: float
    verification_results: List[VerificationResult]
    adaptation_results: List[AdaptationResult] 
    recovery_results: List[RecoveryResult]
    optimization_result: Optional[OptimizationResult]
    performance_metrics: Dict[str, Any]
    recommendations: List[str]
    errors: List[str] = field(default_factory=list)


class AdvancedPlaybackEngine:
    """Unified advanced playback engine with all intelligent features"""
    
    def __init__(self, config: PlaybackConfig = None):
        self.config = config or PlaybackConfig()
        
        # Initialize component systems
        self.context_verifier = ContextVerifier()
        self.adaptive_executor = AdaptiveExecutor()
        self.recovery_engine = RecoveryEngine()
        self.performance_optimizer = PerformanceOptimizer(self.config.optimization_level)
        
        # Execution state
        self.current_execution = None
        self.execution_history = []
        self.failure_count = 0
        self.adaptive_adjustments = 0
        
        # Callbacks for external integration
        self.pre_execution_callback: Optional[Callable] = None
        self.post_execution_callback: Optional[Callable] = None
        self.failure_callback: Optional[Callable] = None
    
    def execute_playbook(self, actions: List[Dict[str, Any]], 
                        context: Dict[str, Any] = None) -> PlaybackResult:
        """Execute a playbook with full advanced features"""
        start_time = time.time()
        context = context or {}
        
        logger.info(f"Starting advanced playbook execution: {len(actions)} actions in {self.config.mode.value} mode")
        
        # Initialize result tracking
        result = PlaybackResult(
            success=False,
            total_actions=len(actions),
            successful_actions=0,
            failed_actions=0,
            execution_time=0,
            verification_results=[],
            adaptation_results=[],
            recovery_results=[],
            optimization_result=None,
            performance_metrics={},
            recommendations=[]
        )
        
        try:
            # Pre-execution callback
            if self.pre_execution_callback:
                self.pre_execution_callback(actions, context)
            
            # Phase 1: Context Verification
            verification_success = self._verify_execution_context(actions, context, result)
            if not verification_success and self.config.mode == PlaybackMode.SAFE:
                result.errors.append("Context verification failed in SAFE mode")
                return result
            
            # Phase 2: Performance Optimization
            if self.config.performance_monitoring:
                optimization_result = self.performance_optimizer.optimize_execution(actions, self.config.optimization_level)
                result.optimization_result = optimization_result
                if optimization_result.success:
                    actions = self._apply_optimization_suggestions(actions, optimization_result)
            
            # Phase 3: Adaptive Execution
            execution_success = self._execute_with_adaptation(actions, context, result)
            
            # Phase 4: Results Analysis
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            result.success = (result.failed_actions / max(result.total_actions, 1)) <= self.config.failure_threshold
            
            # Generate recommendations
            result.recommendations = self._generate_execution_recommendations(result)
            
            # Performance metrics
            if self.config.performance_monitoring:
                result.performance_metrics = self.performance_optimizer.get_performance_report()
            
            # Post-execution callback
            if self.post_execution_callback:
                self.post_execution_callback(result)
            
            logger.info(f"Playbook execution completed: {result.successful_actions}/{result.total_actions} successful in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Playbook execution failed: {e}")
            result.errors.append(f"Execution error: {str(e)}")
            if self.failure_callback:
                self.failure_callback(e, result)
        
        # Store in history
        self.execution_history.append(result)
        if len(self.execution_history) > 100:  # Keep last 100 executions
            self.execution_history.pop(0)
        
        return result
    
    def _verify_execution_context(self, actions: List[Dict[str, Any]], 
                                 context: Dict[str, Any], 
                                 result: PlaybackResult) -> bool:
        """Verify context before execution"""
        logger.debug("Verifying execution context")
        
        # Create verification criteria from actions and context
        criteria = VerificationCriteria(
            required_applications=list(set(action.get('application', '') for action in actions if action.get('application'))),
            required_windows=list(set(action.get('window_title', '') for action in actions if action.get('window_title'))),
            screen_resolution=context.get('screen_resolution'),
            required_elements=[],  # Could be populated from action targets
            custom_checks=[]
        )
        
        verification_result = self.context_verifier.verify_context(criteria, self.config.verification_level)
        result.verification_results.append(verification_result)
        
        if not verification_result.is_valid:
            logger.warning(f"Context verification failed: {verification_result.issues}")
            
            # In adaptive mode, try to fix issues
            if self.config.mode == PlaybackMode.ADAPTIVE:
                self._attempt_context_fixes(verification_result)
                # Re-verify after fixes
                verification_result = self.context_verifier.verify_context(criteria, self.config.verification_level)
                result.verification_results.append(verification_result)
        
        return verification_result.is_valid
    
    def _attempt_context_fixes(self, verification_result: VerificationResult) -> None:
        """Attempt to fix context verification issues"""
        for issue in verification_result.issues:
            logger.info(f"Attempting to fix context issue: {issue}")
            
            if "application not found" in issue.lower():
                # Could try to launch application
                pass
            elif "window not found" in issue.lower():
                # Could try to focus or restore window
                pass
            elif "screen resolution" in issue.lower():
                # Could adjust scaling or positioning
                pass
    
    def _execute_with_adaptation(self, actions: List[Dict[str, Any]], 
                                context: Dict[str, Any], 
                                result: PlaybackResult) -> bool:
        """Execute actions with adaptive capabilities"""
        logger.debug(f"Executing {len(actions)} actions with adaptation")
        
        for i, action in enumerate(actions):
            logger.debug(f"Executing action {i+1}/{len(actions)}: {action.get('type', 'unknown')}")
            
            try:
                # Execute with adaptive engine
                adaptation_result = self.adaptive_executor.execute_with_adaptation(
                    action, 
                    self.config.adaptation_strategy,
                    max_attempts=self.config.max_retry_attempts
                )
                
                result.adaptation_results.append(adaptation_result)
                
                if adaptation_result.success:
                    result.successful_actions += 1
                    if adaptation_result.adaptations_made > 0:
                        self.adaptive_adjustments += 1
                        logger.info(f"Action adapted successfully with {adaptation_result.adaptations_made} adjustments")
                else:
                    result.failed_actions += 1
                    self.failure_count += 1
                    
                    # Attempt recovery if enabled
                    if self.config.recovery_enabled:
                        recovery_success = self._attempt_recovery(action, adaptation_result, result)
                        if recovery_success:
                            result.successful_actions += 1
                            result.failed_actions -= 1
                
            except Exception as e:
                logger.error(f"Action execution failed: {e}")
                result.failed_actions += 1
                result.errors.append(f"Action {i+1} failed: {str(e)}")
                
                # Attempt recovery for exceptions
                if self.config.recovery_enabled:
                    failure_info = FailureInfo(
                        action=action,
                        error_type="execution_exception",
                        error_message=str(e),
                        context=context,
                        attempt_count=1,
                        timestamp=time.time()
                    )
                    recovery_success = self._attempt_recovery_from_failure(failure_info, result)
                    if recovery_success:
                        result.successful_actions += 1
                        result.failed_actions -= 1
            
            # Check if we should abort execution
            if self._should_abort_execution(result):
                logger.warning("Aborting execution due to high failure rate")
                break
        
        return result.failed_actions == 0
    
    def _attempt_recovery(self, action: Dict[str, Any], 
                         adaptation_result: AdaptationResult,
                         result: PlaybackResult) -> bool:
        """Attempt recovery from failed action"""
        failure_info = FailureInfo(
            action=action,
            error_type="adaptation_failure", 
            error_message=adaptation_result.error_message or "Adaptation failed",
            context={},
            attempt_count=adaptation_result.attempts_made,
            timestamp=time.time()
        )
        
        return self._attempt_recovery_from_failure(failure_info, result)
    
    def _attempt_recovery_from_failure(self, failure_info: FailureInfo, 
                                     result: PlaybackResult) -> bool:
        """Attempt recovery from failure"""
        logger.info(f"Attempting recovery for failed action: {failure_info.error_type}")
        
        recovery_result = self.recovery_engine.handle_failure(failure_info)
        result.recovery_results.append(recovery_result)
        
        if recovery_result.success:
            logger.info(f"Recovery successful using strategy: {recovery_result.strategy_used.value}")
            return True
        else:
            logger.warning(f"Recovery failed: {recovery_result.error_message}")
            return False
    
    def _should_abort_execution(self, result: PlaybackResult) -> bool:
        """Check if execution should be aborted due to failure rate"""
        if result.total_actions == 0:
            return False
        
        current_failure_rate = result.failed_actions / result.total_actions
        return current_failure_rate > self.config.failure_threshold
    
    def _apply_optimization_suggestions(self, actions: List[Dict[str, Any]], 
                                      optimization_result: OptimizationResult) -> List[Dict[str, Any]]:
        """Apply optimization suggestions to action sequence"""
        if not optimization_result.success:
            return actions
        
        # Apply optimizations based on recommendations
        optimized_actions = actions.copy()
        
        for recommendation in optimization_result.recommendations:
            if "batch" in recommendation.lower():
                # Group similar actions for batch processing
                optimized_actions = self._group_actions_for_batching(optimized_actions)
            elif "reorder" in recommendation.lower():
                # Reorder actions for efficiency
                optimized_actions = self._reorder_actions_for_efficiency(optimized_actions)
        
        return optimized_actions
    
    def _group_actions_for_batching(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group similar actions for batch processing"""
        # Simple grouping - could be more sophisticated
        return actions  # Placeholder implementation
    
    def _reorder_actions_for_efficiency(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Reorder actions for better execution efficiency"""
        # Simple reordering - prioritize focus changes, then interactions
        focus_actions = [a for a in actions if a.get('type') in ['focus', 'click']]
        other_actions = [a for a in actions if a.get('type') not in ['focus', 'click']]
        return focus_actions + other_actions
    
    def _generate_execution_recommendations(self, result: PlaybackResult) -> List[str]:
        """Generate recommendations based on execution results"""
        recommendations = []
        
        failure_rate = result.failed_actions / max(result.total_actions, 1)
        
        if failure_rate > 0.2:  # >20% failure rate
            recommendations.append("Consider switching to SAFE mode for better reliability")
            recommendations.append("Review action sequences for accuracy")
        
        if self.adaptive_adjustments > result.total_actions * 0.5:  # >50% actions required adaptation
            recommendations.append("UI may have changed significantly - consider re-recording")
        
        if result.execution_time > result.total_actions * 2:  # >2s per action average
            recommendations.append("Consider FAST mode or performance optimization")
        
        # Add optimization recommendations
        if result.optimization_result and result.optimization_result.recommendations:
            recommendations.extend(result.optimization_result.recommendations)
        
        return recommendations
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get comprehensive execution statistics"""
        if not self.execution_history:
            return {"status": "No execution history available"}
        
        recent_executions = self.execution_history[-10:]  # Last 10 executions
        
        return {
            "total_executions": len(self.execution_history),
            "average_success_rate": sum(e.successful_actions / max(e.total_actions, 1) for e in recent_executions) / len(recent_executions),
            "average_execution_time": sum(e.execution_time for e in recent_executions) / len(recent_executions),
            "total_adaptations": sum(len(e.adaptation_results) for e in recent_executions),
            "total_recoveries": sum(len(e.recovery_results) for e in recent_executions),
            "current_config": {
                "mode": self.config.mode.value,
                "verification_level": self.config.verification_level.value,
                "adaptation_strategy": self.config.adaptation_strategy.value,
                "optimization_level": self.config.optimization_level.value,
            },
            "performance_metrics": self.performance_optimizer.get_performance_report() if self.config.performance_monitoring else {}
        }
    
    def update_config(self, new_config: PlaybackConfig) -> None:
        """Update playback configuration"""
        logger.info(f"Updating playback config: {new_config.mode.value} mode")
        self.config = new_config
        
        # Update component configurations
        if hasattr(self.performance_optimizer, 'optimization_level'):
            self.performance_optimizer.optimization_level = new_config.optimization_level
    
    def set_callbacks(self, pre_execution: Callable = None, 
                     post_execution: Callable = None,
                     failure: Callable = None) -> None:
        """Set callback functions for execution events"""
        self.pre_execution_callback = pre_execution
        self.post_execution_callback = post_execution  
        self.failure_callback = failure