/**
 * Feature Flags Configuration
 * 
 * Centralized feature flag management for gradual rollout and A/B testing.
 * 
 * Best Practices:
 * - Use environment variables for production control
 * - Default to false for new features
 * - Document each flag with purpose and rollout plan
 * - Remove flags after full rollout (technical debt)
 */

interface FeatureFlags {
  // Dashboard Customization (Phase 1: Collapse/Expand)
  ENABLE_DASHBOARD_CUSTOMIZATION: boolean
  
  // Future features (Phase 2+)
  ENABLE_DASHBOARD_DRAG_DROP: boolean
  ENABLE_DASHBOARD_TEMPLATES: boolean
  ENABLE_WIDGET_RESIZE: boolean
}

/**
 * Get feature flag value from environment or default
 */
function getFeatureFlag(key: string, defaultValue: boolean): boolean {
  // Check environment variable first (for production control)
  const envValue = import.meta.env[`VITE_${key}`]
  
  if (envValue !== undefined) {
    return envValue === 'true' || envValue === '1'
  }
  
  // Fall back to default
  return defaultValue
}

/**
 * Feature Flags
 * 
 * To enable in production, set environment variable:
 * VITE_ENABLE_DASHBOARD_CUSTOMIZATION=true
 */
export const features: FeatureFlags = {
  // Phase 1: Collapse/Expand (MVP)
  // Rollout: Week 1 (Internal) → Week 2 (5 clinics) → Week 3-5 (Gradual 25%→50%→100%)
  ENABLE_DASHBOARD_CUSTOMIZATION: getFeatureFlag(
    'ENABLE_DASHBOARD_CUSTOMIZATION',
    true // Default: enabled in dev
  ),
  
  // Phase 2: Drag & Drop (Future)
  ENABLE_DASHBOARD_DRAG_DROP: getFeatureFlag(
    'ENABLE_DASHBOARD_DRAG_DROP',
    false
  ),
  
  // Phase 3: Templates (Future)
  ENABLE_DASHBOARD_TEMPLATES: getFeatureFlag(
    'ENABLE_DASHBOARD_TEMPLATES',
    false
  ),
  
  // Phase 3: Widget Resize (Future)
  ENABLE_WIDGET_RESIZE: getFeatureFlag(
    'ENABLE_WIDGET_RESIZE',
    false
  )
}

/**
 * Check if a feature is enabled
 */
export function isFeatureEnabled(feature: keyof FeatureFlags): boolean {
  return features[feature]
}

/**
 * Get all enabled features (for debugging)
 */
export function getEnabledFeatures(): string[] {
  return Object.entries(features)
    .filter(([_, enabled]) => enabled)
    .map(([feature]) => feature)
}
