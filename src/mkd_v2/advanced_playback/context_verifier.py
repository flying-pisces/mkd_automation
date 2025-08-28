#!/usr/bin/env python3
"""
Context Verification System

Pre-execution environment validation to ensure playback reliability.
Verifies application context, UI state, and execution conditions.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ..intelligence.context_detector import ContextDetector, ApplicationContext, ContextType, UIState
from ..platform.base import PlatformInterface


logger = logging.getLogger(__name__)


class VerificationLevel(Enum):
    """Context verification strictness levels."""
    MINIMAL = "minimal"      # Basic app matching
    STANDARD = "standard"    # App + UI state matching
    STRICT = "strict"        # Exact context matching
    ADAPTIVE = "adaptive"    # Smart context similarity


class VerificationStatus(Enum):
    """Verification result statuses."""
    VERIFIED = "verified"
    WARNING = "warning"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class VerificationCriteria:
    """Criteria for context verification."""
    required_app_name: Optional[str] = None
    required_context_type: Optional[ContextType] = None
    required_ui_state: Optional[UIState] = None
    
    # Window requirements
    min_window_width: int = 0
    min_window_height: int = 0
    required_window_visible: bool = True
    
    # Context stability
    min_stability_duration: float = 1.0  # seconds
    min_confidence_threshold: float = 0.6
    
    # Advanced criteria
    forbidden_ui_states: Set[UIState] = field(default_factory=set)
    required_elements: List[str] = field(default_factory=list)
    execution_timeout: float = 30.0
    
    # Flexibility settings
    allow_context_type_similarity: bool = True
    allow_app_name_fuzzy_match: bool = True
    similarity_threshold: float = 0.7


@dataclass
class VerificationResult:
    """Result of context verification."""
    status: VerificationStatus
    confidence: float
    current_context: ApplicationContext
    verification_time: float
    
    # Detailed results
    app_match: bool = False
    context_type_match: bool = False
    ui_state_match: bool = False
    window_size_ok: bool = True
    stability_ok: bool = True
    
    # Issues and recommendations
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Adaptation suggestions
    suggested_adaptations: List[Dict[str, Any]] = field(default_factory=list)
    recovery_suggestions: List[str] = field(default_factory=list)
    
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextVerifier:
    """
    Intelligent context verification system.
    
    Validates execution environment before playback to ensure reliability.
    """
    
    def __init__(self, context_detector: ContextDetector):
        self.context_detector = context_detector
        
        # Verification history
        self.verification_history: List[VerificationResult] = []
        self.app_compatibility_cache: Dict[str, Dict[str, float]] = {}
        
        # Performance tracking
        self.stats = {
            'total_verifications': 0,
            'successful_verifications': 0,
            'failed_verifications': 0,
            'warnings_issued': 0,
            'avg_verification_time': 0.0
        }
        
        logger.info("Context verifier initialized")
    
    def verify_context(self, criteria: VerificationCriteria, 
                      level: VerificationLevel = VerificationLevel.STANDARD) -> VerificationResult:
        """
        Verify current context against criteria.
        
        Args:
            criteria: Verification criteria to check against
            level: Verification strictness level
            
        Returns:
            Verification result with detailed status
        """
        start_time = time.time()
        
        try:
            # Get current context
            current_context = self.context_detector.detect_current_context()
            
            # Initialize result
            result = VerificationResult(
                status=VerificationStatus.UNKNOWN,
                confidence=0.0,
                current_context=current_context,
                verification_time=0.0
            )
            
            # Perform verification based on level
            if level == VerificationLevel.MINIMAL:
                result = self._verify_minimal(current_context, criteria, result)
            elif level == VerificationLevel.STANDARD:
                result = self._verify_standard(current_context, criteria, result)
            elif level == VerificationLevel.STRICT:
                result = self._verify_strict(current_context, criteria, result)
            elif level == VerificationLevel.ADAPTIVE:
                result = self._verify_adaptive(current_context, criteria, result)
            
            # Calculate overall confidence and status
            result.confidence = self._calculate_verification_confidence(result)
            result.status = self._determine_verification_status(result)
            result.verification_time = time.time() - start_time
            
            # Generate recommendations
            self._generate_recommendations(result, criteria)
            
            # Update statistics
            self._update_stats(result)
            
            # Store in history
            self.verification_history.append(result)
            if len(self.verification_history) > 100:
                self.verification_history = self.verification_history[-100:]
            
            logger.info(f"Context verification: {result.status.value} (confidence: {result.confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Context verification failed: {e}")
            return VerificationResult(
                status=VerificationStatus.FAILED,
                confidence=0.0,
                current_context=self.context_detector._create_unknown_context(),
                verification_time=time.time() - start_time,
                issues=[f"Verification error: {e}"]
            )
    
    def _verify_minimal(self, context: ApplicationContext, criteria: VerificationCriteria, 
                       result: VerificationResult) -> VerificationResult:
        """Perform minimal verification (basic app matching)."""
        
        # Check application name
        if criteria.required_app_name:
            if criteria.allow_app_name_fuzzy_match:
                result.app_match = self._fuzzy_match_app(context.app_name, criteria.required_app_name)
            else:
                result.app_match = context.app_name.lower() == criteria.required_app_name.lower()
            
            if not result.app_match:
                result.issues.append(f"Application mismatch: expected '{criteria.required_app_name}', got '{context.app_name}'")
        else:
            result.app_match = True
        
        # Basic window visibility
        if criteria.required_window_visible and not context.metadata.get('is_active', True):
            result.issues.append("Required window is not visible/active")
            result.window_size_ok = False
        
        return result
    
    def _verify_standard(self, context: ApplicationContext, criteria: VerificationCriteria,
                        result: VerificationResult) -> VerificationResult:
        """Perform standard verification (app + UI state)."""
        
        # First do minimal verification
        result = self._verify_minimal(context, criteria, result)
        
        # Check context type
        if criteria.required_context_type:
            if criteria.allow_context_type_similarity:
                result.context_type_match = self._context_types_compatible(
                    context.context_type, criteria.required_context_type
                )
            else:
                result.context_type_match = context.context_type == criteria.required_context_type
            
            if not result.context_type_match:
                result.issues.append(f"Context type mismatch: expected {criteria.required_context_type.value}, got {context.context_type.value}")
        else:
            result.context_type_match = True
        
        # Check UI state
        if criteria.required_ui_state:
            result.ui_state_match = context.ui_state == criteria.required_ui_state
            if not result.ui_state_match:
                result.warnings.append(f"UI state mismatch: expected {criteria.required_ui_state.value}, got {context.ui_state.value}")
        else:
            result.ui_state_match = True
        
        # Check forbidden UI states
        if context.ui_state in criteria.forbidden_ui_states:
            result.issues.append(f"Current UI state '{context.ui_state.value}' is forbidden for execution")
        
        # Check window size requirements
        bounds = context.window_bounds
        if (bounds.get('width', 0) < criteria.min_window_width or 
            bounds.get('height', 0) < criteria.min_window_height):
            result.window_size_ok = False
            result.warnings.append(f"Window too small: {bounds.get('width', 0)}x{bounds.get('height', 0)}")
        
        return result
    
    def _verify_strict(self, context: ApplicationContext, criteria: VerificationCriteria,
                      result: VerificationResult) -> VerificationResult:
        """Perform strict verification (exact matching)."""
        
        # Do standard verification first
        result = self._verify_standard(context, criteria, result)
        
        # Strict confidence requirement
        if context.confidence < criteria.min_confidence_threshold:
            result.issues.append(f"Context confidence too low: {context.confidence:.2f} < {criteria.min_confidence_threshold:.2f}")
        
        # Check context stability
        if not self.context_detector.is_context_stable(criteria.min_stability_duration):
            result.stability_ok = False
            result.issues.append(f"Context not stable for required duration: {criteria.min_stability_duration}s")
        
        # Exact UI state requirement in strict mode
        if criteria.required_ui_state and context.ui_state != criteria.required_ui_state:
            result.ui_state_match = False
            # Convert warning to issue in strict mode
            result.issues.append(f"Strict UI state mismatch: expected {criteria.required_ui_state.value}, got {context.ui_state.value}")
            if "UI state mismatch" in str(result.warnings):
                result.warnings = [w for w in result.warnings if "UI state mismatch" not in w]
        
        return result
    
    def _verify_adaptive(self, context: ApplicationContext, criteria: VerificationCriteria,
                        result: VerificationResult) -> VerificationResult:
        """Perform adaptive verification (smart similarity)."""
        
        # Start with standard verification
        result = self._verify_standard(context, criteria, result)
        
        # Use compatibility cache for adaptive decisions
        if criteria.required_app_name:
            compatibility = self._get_app_compatibility(context.app_name, criteria.required_app_name)
            if compatibility >= criteria.similarity_threshold:
                result.app_match = True
                if compatibility < 1.0:
                    result.warnings.append(f"Using compatible app: {compatibility:.1%} similarity")
        
        # Adaptive context type matching
        if criteria.required_context_type:
            type_similarity = self._calculate_context_type_similarity(
                context.context_type, criteria.required_context_type
            )
            if type_similarity >= criteria.similarity_threshold:
                result.context_type_match = True
                result.suggested_adaptations.append({
                    'type': 'context_type_adaptation',
                    'similarity': type_similarity,
                    'original': criteria.required_context_type.value,
                    'current': context.context_type.value
                })
        
        # Smart UI state adaptation
        if criteria.required_ui_state and not result.ui_state_match:
            if self._ui_states_compatible(context.ui_state, criteria.required_ui_state):
                result.ui_state_match = True
                result.suggested_adaptations.append({
                    'type': 'ui_state_adaptation',
                    'original': criteria.required_ui_state.value,
                    'current': context.ui_state.value,
                    'reason': 'Compatible UI states'
                })
        
        return result
    
    def _fuzzy_match_app(self, current_app: str, required_app: str) -> bool:
        """Perform fuzzy application name matching."""
        current_lower = current_app.lower()
        required_lower = required_app.lower()
        
        # Exact match
        if current_lower == required_lower:
            return True
        
        # Substring match
        if required_lower in current_lower or current_lower in required_lower:
            return True
        
        # Common app name variations
        variations = {
            'chrome': ['google chrome', 'chromium'],
            'firefox': ['mozilla firefox'],
            'vscode': ['visual studio code', 'code'],
            'terminal': ['terminal', 'iterm', 'cmd', 'powershell']
        }
        
        for canonical, variants in variations.items():
            if (canonical in required_lower or required_lower in variants) and \
               (canonical in current_lower or any(v in current_lower for v in variants)):
                return True
        
        return False
    
    def _context_types_compatible(self, current: ContextType, required: ContextType) -> bool:
        """Check if context types are compatible."""
        if current == required:
            return True
        
        # Define compatible context types
        compatible_groups = [
            {ContextType.WEB_BROWSER},
            {ContextType.DEVELOPMENT_IDE, ContextType.TEXT_EDITOR},
            {ContextType.TERMINAL},
            {ContextType.FILE_MANAGER},
            {ContextType.COMMUNICATION}
        ]
        
        for group in compatible_groups:
            if current in group and required in group:
                return True
        
        return False
    
    def _ui_states_compatible(self, current: UIState, required: UIState) -> bool:
        """Check if UI states are compatible for execution."""
        if current == required:
            return True
        
        # Define compatible UI states
        compatible_pairs = [
            (UIState.IDLE, UIState.FORM_INPUT),  # Can start input from idle
            (UIState.FORM_INPUT, UIState.IDLE),  # Can be idle while in form
        ]
        
        return (current, required) in compatible_pairs or (required, current) in compatible_pairs
    
    def _get_app_compatibility(self, current_app: str, required_app: str) -> float:
        """Get cached compatibility score between apps."""
        cache_key = f"{current_app.lower()}:{required_app.lower()}"
        
        if cache_key not in self.app_compatibility_cache:
            # Calculate compatibility and cache it
            similarity = self._calculate_app_similarity(current_app, required_app)
            self.app_compatibility_cache[cache_key] = {'similarity': similarity, 'last_used': time.time()}
        
        return self.app_compatibility_cache[cache_key]['similarity']
    
    def _calculate_app_similarity(self, app1: str, app2: str) -> float:
        """Calculate similarity between application names."""
        if app1.lower() == app2.lower():
            return 1.0
        
        # Simple Jaccard similarity on words
        words1 = set(app1.lower().split())
        words2 = set(app2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_context_type_similarity(self, type1: ContextType, type2: ContextType) -> float:
        """Calculate similarity between context types."""
        if type1 == type2:
            return 1.0
        
        # Define similarity scores
        similarity_matrix = {
            (ContextType.DEVELOPMENT_IDE, ContextType.TEXT_EDITOR): 0.8,
            (ContextType.TEXT_EDITOR, ContextType.DEVELOPMENT_IDE): 0.8,
            (ContextType.WEB_BROWSER, ContextType.UNKNOWN): 0.3,  # Unknown could be browser
            (ContextType.UNKNOWN, ContextType.WEB_BROWSER): 0.3,
        }
        
        return similarity_matrix.get((type1, type2), 0.0)
    
    def _calculate_verification_confidence(self, result: VerificationResult) -> float:
        """Calculate overall verification confidence."""
        confidence = 0.0
        total_weight = 0.0
        
        # Weight different verification aspects
        weights = {
            'app_match': 0.4,
            'context_type_match': 0.25,
            'ui_state_match': 0.15,
            'window_size_ok': 0.1,
            'stability_ok': 0.1
        }
        
        for aspect, weight in weights.items():
            if getattr(result, aspect):
                confidence += weight
            total_weight += weight
        
        # Normalize
        confidence = confidence / total_weight if total_weight > 0 else 0.0
        
        # Penalize for issues
        issue_penalty = min(0.2 * len(result.issues), 0.8)
        warning_penalty = min(0.05 * len(result.warnings), 0.2)
        
        confidence = max(0.0, confidence - issue_penalty - warning_penalty)
        
        # Boost for context confidence
        context_boost = result.current_context.confidence * 0.1
        confidence = min(1.0, confidence + context_boost)
        
        return confidence
    
    def _determine_verification_status(self, result: VerificationResult) -> VerificationStatus:
        """Determine overall verification status."""
        
        # Failed if critical issues
        if result.issues:
            critical_issues = [
                'Application mismatch',
                'Context type mismatch', 
                'forbidden for execution',
                'Verification error'
            ]
            
            if any(any(critical in issue for critical in critical_issues) for issue in result.issues):
                return VerificationStatus.FAILED
        
        # Warning if non-critical issues or warnings
        if result.issues or result.warnings:
            return VerificationStatus.WARNING
        
        # Verified if high confidence
        if result.confidence >= 0.8:
            return VerificationStatus.VERIFIED
        
        # Warning for medium confidence
        if result.confidence >= 0.5:
            return VerificationStatus.WARNING
        
        # Failed for low confidence
        return VerificationStatus.FAILED
    
    def _generate_recommendations(self, result: VerificationResult, criteria: VerificationCriteria):
        """Generate recommendations based on verification results."""
        
        # App mismatch recommendations
        if not result.app_match and criteria.required_app_name:
            result.recommendations.append(f"Switch to application: {criteria.required_app_name}")
            result.recovery_suggestions.append("focus_required_application")
        
        # Context type mismatch
        if not result.context_type_match and criteria.required_context_type:
            result.recommendations.append(f"Use {criteria.required_context_type.value} type application")
        
        # UI state issues
        if not result.ui_state_match and criteria.required_ui_state:
            result.recommendations.append(f"Wait for {criteria.required_ui_state.value} UI state")
            result.recovery_suggestions.append("wait_for_ui_state")
        
        # Window size issues
        if not result.window_size_ok:
            result.recommendations.append("Resize window to meet minimum requirements")
            result.recovery_suggestions.append("resize_window")
        
        # Stability issues
        if not result.stability_ok:
            result.recommendations.append("Wait for context to stabilize")
            result.recovery_suggestions.append("wait_for_stability")
    
    def _update_stats(self, result: VerificationResult):
        """Update verification statistics."""
        self.stats['total_verifications'] += 1
        
        if result.status == VerificationStatus.VERIFIED:
            self.stats['successful_verifications'] += 1
        elif result.status == VerificationStatus.FAILED:
            self.stats['failed_verifications'] += 1
        
        if result.warnings:
            self.stats['warnings_issued'] += 1
        
        # Update average verification time
        count = self.stats['total_verifications']
        current_avg = self.stats['avg_verification_time']
        self.stats['avg_verification_time'] = (current_avg * (count - 1) + result.verification_time) / count
    
    def verify_execution_ready(self, criteria: VerificationCriteria) -> bool:
        """Simple boolean check if context is ready for execution."""
        result = self.verify_context(criteria, VerificationLevel.STANDARD)
        return result.status in [VerificationStatus.VERIFIED, VerificationStatus.WARNING]
    
    def get_verification_history(self, limit: int = 10) -> List[VerificationResult]:
        """Get recent verification history."""
        return self.verification_history[-limit:]
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """Get verification performance statistics."""
        stats = self.stats.copy()
        if stats['total_verifications'] > 0:
            stats['success_rate'] = stats['successful_verifications'] / stats['total_verifications']
            stats['warning_rate'] = stats['warnings_issued'] / stats['total_verifications']
        else:
            stats['success_rate'] = 0.0
            stats['warning_rate'] = 0.0
        
        return stats
    
    def cleanup(self):
        """Clean up verifier resources."""
        self.verification_history.clear()
        self.app_compatibility_cache.clear()
        logger.info("Context verifier cleaned up")