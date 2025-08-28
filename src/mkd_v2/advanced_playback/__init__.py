"""
MKD Advanced Playback Module

Provides intelligent playback features for context-aware automation:
- Context verification and validation
- Adaptive execution with smart adjustments  
- Error recovery and failure handling
- Performance optimization for reliable playback
"""

from .context_verifier import ContextVerifier, VerificationResult
from .adaptive_executor import AdaptiveExecutor, AdaptationResult
from .recovery_engine import RecoveryEngine, RecoveryStrategy, RecoveryResult
from .performance_optimizer import PerformanceOptimizer, OptimizationLevel, OptimizationResult
from .advanced_playback_engine import AdvancedPlaybackEngine, PlaybackMode, PlaybackConfig, PlaybackResult

__all__ = [
    'ContextVerifier',
    'VerificationResult', 
    'AdaptiveExecutor',
    'AdaptationResult',
    'RecoveryEngine',
    'RecoveryStrategy',
    'RecoveryResult',
    'PerformanceOptimizer',
    'OptimizationLevel',
    'OptimizationResult',
    'AdvancedPlaybackEngine',
    'PlaybackMode',
    'PlaybackConfig',
    'PlaybackResult'
]