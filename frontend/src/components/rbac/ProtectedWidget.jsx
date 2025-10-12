import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Lock, ShieldAlert } from 'lucide-react';
import { canViewWidget, canInteractWithWidget, getUserRole, formatRoleName, hasFeaturePermission } from '@/utils/rbac';

/**
 * ProtectedWidget - Wrapper component for widget-level RBAC
 * 
 * Usage:
 *   <ProtectedWidget widgetId="decision-queue" requireInteract={false}>
 *     <DecisionQueueWidget />
 *   </ProtectedWidget>
 * 
 * Props:
 * - widgetId: Unique identifier for the widget (must match WIDGET_PERMISSIONS)
 * - requireInteract: If true, requires interact permission; if false, only view permission
 * - children: The widget component to render if user has permission
 * - fallback: Custom fallback component to show when user lacks permission
 * - showFallback: If true, shows a permission denied message; if false, renders nothing
 */
export default function ProtectedWidget({
  widgetId,
  requireInteract = false,
  children,
  fallback = null,
  showFallback = true,
}) {
  const userRole = getUserRole();
  
  // Check permissions
  const canView = canViewWidget(userRole, widgetId);
  const canInteract = canInteractWithWidget(userRole, widgetId);
  
  // Determine if user has required permission
  const hasPermission = requireInteract ? canInteract : canView;
  
  // If user has permission, render children
  if (hasPermission) {
    return <>{children}</>;
  }
  
  // If custom fallback provided, use it
  if (fallback) {
    return fallback;
  }
  
  // If showFallback is false, render nothing
  if (!showFallback) {
    return null;
  }
  
  // Default fallback: permission denied message
  return (
    <Card className="border-2 border-dashed border-gray-300">
      <CardContent className="p-6">
        <div className="text-center text-sm text-gray-500">
          <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-3">
            <Lock className="w-6 h-6 text-gray-400" />
          </div>
          <p className="font-semibold text-gray-700 mb-1">Access Restricted</p>
          <p className="text-xs">
            This widget requires {requireInteract ? 'interaction' : 'view'} permissions.
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Your role: {formatRoleName(userRole)}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * ProtectedFeature - Component for feature-level RBAC
 * 
 * Usage:
 *   <ProtectedFeature featureId="approve-suggestions">
 *     <Button>Approve</Button>
 *   </ProtectedFeature>
 */
export function ProtectedFeature({
  featureId,
  children,
  fallback = null,
  showFallback = false,
  disableInstead = false,
}) {
  const userRole = getUserRole();
  
  const hasPermission = hasFeaturePermission(userRole, featureId);
  
  // If user has permission, render children
  if (hasPermission) {
    return <>{children}</>;
  }
  
  // If disableInstead is true, render children but disabled
  if (disableInstead && React.isValidElement(children)) {
    return React.cloneElement(children, { disabled: true });
  }
  
  // If custom fallback provided, use it
  if (fallback) {
    return fallback;
  }
  
  // If showFallback is false, render nothing
  if (!showFallback) {
    return null;
  }
  
  // Default fallback: permission denied message
  return (
    <div className="text-xs text-gray-500 flex items-center gap-1">
      <ShieldAlert className="w-3 h-3" />
      <span>Permission required</span>
    </div>
  );
}

/**
 * useWidgetPermissions - Hook for widget permissions
 * 
 * Usage:
 *   const { canView, canInteract } = useWidgetPermissions('decision-queue');
 */
export function useWidgetPermissions(widgetId) {
  const userRole = getUserRole();
  
  return {
    canView: canViewWidget(userRole, widgetId),
    canInteract: canInteractWithWidget(userRole, widgetId),
    userRole,
  };
}

/**
 * useFeaturePermission - Hook for feature permissions
 * 
 * Usage:
 *   const { hasPermission } = useFeaturePermission('approve-suggestions');
 */
export function useFeaturePermission(featureId) {
  const userRole = getUserRole();
  
  return {
    hasPermission: hasFeaturePermission(userRole, featureId),
    userRole,
  };
}

