"""
Feature Flags Management

Centralized feature flag management for gradual rollout and A/B testing.

Usage:
    from app.core.feature_flags import feature_flags
    
    if feature_flags.is_enabled('proactive_suggestions'):
        # Show proactive suggestions
        pass
"""

from typing import Dict, Optional
from enum import Enum
from app.core.config import settings


class FeatureFlag(str, Enum):
    """Available feature flags."""
    
    # Core features
    PROACTIVE_SUGGESTIONS = "proactive_suggestions"
    WHATSAPP = "whatsapp"
    ANALYTICS = "analytics"
    
    # Advanced features
    MFA = "mfa"
    FINE_TUNING = "fine_tuning"
    EXECUTIVE_AGENTS = "executive_agents"
    SELF_HEALING = "self_healing"
    
    # Experimental features
    VOICE_CALLS = "voice_calls"
    VIDEO_CONSULTATIONS = "video_consultations"
    AI_DIAGNOSIS = "ai_diagnosis"


class FeatureFlags:
    """Feature flags manager."""
    
    def __init__(self):
        """Initialize feature flags from settings."""
        self._flags: Dict[str, bool] = {
            # From settings
            FeatureFlag.PROACTIVE_SUGGESTIONS: settings.FEATURE_PROACTIVE_SUGGESTIONS,
            FeatureFlag.WHATSAPP: settings.FEATURE_WHATSAPP,
            FeatureFlag.ANALYTICS: settings.FEATURE_ANALYTICS,
            FeatureFlag.MFA: settings.FEATURE_MFA,
            FeatureFlag.FINE_TUNING: settings.FEATURE_FINE_TUNING,
            FeatureFlag.EXECUTIVE_AGENTS: settings.FEATURE_EXECUTIVE_AGENTS,
            FeatureFlag.SELF_HEALING: settings.FEATURE_SELF_HEALING,
            
            # Experimental (disabled by default)
            FeatureFlag.VOICE_CALLS: False,
            FeatureFlag.VIDEO_CONSULTATIONS: False,
            FeatureFlag.AI_DIAGNOSIS: False,
        }
    
    def is_enabled(self, flag: str) -> bool:
        """
        Check if a feature flag is enabled.
        
        Args:
            flag: Feature flag name
            
        Returns:
            True if enabled, False otherwise
        """
        return self._flags.get(flag, False)
    
    def enable(self, flag: str) -> None:
        """
        Enable a feature flag.
        
        Args:
            flag: Feature flag name
        """
        self._flags[flag] = True
    
    def disable(self, flag: str) -> None:
        """
        Disable a feature flag.
        
        Args:
            flag: Feature flag name
        """
        self._flags[flag] = False
    
    def get_all(self) -> Dict[str, bool]:
        """
        Get all feature flags.
        
        Returns:
            Dictionary of all feature flags
        """
        return self._flags.copy()
    
    def is_enabled_for_organization(self, flag: str, organization_id: str) -> bool:
        """
        Check if a feature flag is enabled for a specific organization.
        
        This allows for gradual rollout or A/B testing per organization.
        
        Args:
            flag: Feature flag name
            organization_id: Organization ID
            
        Returns:
            True if enabled for this organization, False otherwise
        """
        # TODO: Implement per-organization feature flags
        # Could use database table or Redis
        return self.is_enabled(flag)
    
    def is_enabled_for_user(self, flag: str, user_id: str) -> bool:
        """
        Check if a feature flag is enabled for a specific user.
        
        This allows for gradual rollout or A/B testing per user.
        
        Args:
            flag: Feature flag name
            user_id: User ID
            
        Returns:
            True if enabled for this user, False otherwise
        """
        # TODO: Implement per-user feature flags
        # Could use database table or Redis
        return self.is_enabled(flag)


# Singleton instance
feature_flags = FeatureFlags()


# Decorator for feature-flagged endpoints
def require_feature(flag: str):
    """
    Decorator to require a feature flag for an endpoint.
    
    Usage:
        @router.get("/proactive-suggestions")
        @require_feature(FeatureFlag.PROACTIVE_SUGGESTIONS)
        async def get_suggestions():
            pass
    """
    def decorator(func):
        from functools import wraps
        from fastapi import HTTPException
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not feature_flags.is_enabled(flag):
                raise HTTPException(
                    status_code=403,
                    detail=f"Feature '{flag}' is not enabled"
                )
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
