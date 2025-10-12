/**
 * Frontend Role-Based Access Control (RBAC) Utilities
 * 
 * Provides widget-level and feature-level permissions based on user role.
 * 
 * Role Hierarchy:
 * - super_admin (4) - Full system access
 * - org_admin (3) - Organization admin access
 * - org_staff (2) - Staff member access
 * - org_viewer (1) - Patient/viewer access
 */

// Role constants
export const ROLES = {
  SUPER_ADMIN: 'super_admin',
  ORG_ADMIN: 'org_admin',
  ORG_STAFF: 'org_staff',
  ORG_VIEWER: 'org_viewer',
};

// Role hierarchy (higher number = more permissions)
const ROLE_HIERARCHY = {
  [ROLES.SUPER_ADMIN]: 4,
  [ROLES.ORG_ADMIN]: 3,
  [ROLES.ORG_STAFF]: 2,
  [ROLES.ORG_VIEWER]: 1,
};

// Widget permissions configuration
export const WIDGET_PERMISSIONS = {
  // Dashboard Widgets
  'todays-patients': {
    view: [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
    interact: [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  },
  'decision-queue': {
    view: [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
    interact: [ROLES.ORG_ADMIN], // Only admins can approve/reject
  },
  'fine-tuning': {
    view: [ROLES.ORG_ADMIN],
    interact: [ROLES.ORG_ADMIN],
  },
  'revenue': {
    view: [ROLES.ORG_ADMIN],
    interact: [ROLES.ORG_ADMIN],
  },
  'agent-activity': {
    view: [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
    interact: [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  },
  'transparency-panel': {
    view: [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
    interact: [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  },
  'ai-chat': {
    view: [ROLES.ORG_ADMIN, ROLES.ORG_STAFF, ROLES.ORG_VIEWER],
    interact: [ROLES.ORG_ADMIN, ROLES.ORG_STAFF, ROLES.ORG_VIEWER],
  },
  
  // Patient Portal Widgets
  'patient-dashboard': {
    view: [ROLES.ORG_VIEWER],
    interact: [ROLES.ORG_VIEWER],
  },
  'patient-appointments': {
    view: [ROLES.ORG_VIEWER],
    interact: [ROLES.ORG_VIEWER],
  },
  'patient-medical-records': {
    view: [ROLES.ORG_VIEWER],
    interact: [ROLES.ORG_VIEWER],
  },
  'patient-billing': {
    view: [ROLES.ORG_VIEWER],
    interact: [ROLES.ORG_VIEWER],
  },
  
  // Management Features
  'patients-management': {
    view: [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
    interact: [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  },
  'appointments-management': {
    view: [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
    interact: [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  },
  'analytics': {
    view: [ROLES.ORG_ADMIN],
    interact: [ROLES.ORG_ADMIN],
  },
  'settings': {
    view: [ROLES.ORG_ADMIN],
    interact: [ROLES.ORG_ADMIN],
  },
};

// Feature permissions configuration
export const FEATURE_PERMISSIONS = {
  // AI Features
  'approve-suggestions': [ROLES.ORG_ADMIN],
  'reject-suggestions': [ROLES.ORG_ADMIN],
  'provide-feedback': [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  'fine-tune-models': [ROLES.ORG_ADMIN],
  'view-agent-reasoning': [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  
  // Patient Management
  'create-patient': [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  'edit-patient': [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  'delete-patient': [ROLES.ORG_ADMIN],
  'view-patient-list': [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  
  // Appointments
  'create-appointment': [ROLES.ORG_ADMIN, ROLES.ORG_STAFF, ROLES.ORG_VIEWER],
  'edit-appointment': [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  'cancel-appointment': [ROLES.ORG_ADMIN, ROLES.ORG_STAFF, ROLES.ORG_VIEWER],
  
  // Financial
  'view-revenue': [ROLES.ORG_ADMIN],
  'view-billing': [ROLES.ORG_ADMIN, ROLES.ORG_STAFF, ROLES.ORG_VIEWER],
  'process-payment': [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  
  // Medical Records
  'view-medical-records': [ROLES.ORG_ADMIN, ROLES.ORG_STAFF, ROLES.ORG_VIEWER],
  'edit-medical-records': [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  'upload-xray': [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  'sarah-analysis': [ROLES.ORG_ADMIN, ROLES.ORG_STAFF],
  
  // System
  'view-analytics': [ROLES.ORG_ADMIN],
  'manage-settings': [ROLES.ORG_ADMIN],
  'manage-users': [ROLES.ORG_ADMIN],
};

/**
 * Check if user role has permission for required role
 * Uses role hierarchy - higher roles have all permissions of lower roles
 */
export function hasRolePermission(userRole, requiredRole) {
  // Check if both roles are valid
  if (!userRole || !requiredRole) return false;
  if (!(userRole in ROLE_HIERARCHY) || !(requiredRole in ROLE_HIERARCHY)) return false;
  
  const userLevel = ROLE_HIERARCHY[userRole];
  const requiredLevel = ROLE_HIERARCHY[requiredRole];
  return userLevel >= requiredLevel;
}

/**
 * Check if user can view a widget
 */
export function canViewWidget(userRole, widgetId) {
  const permissions = WIDGET_PERMISSIONS[widgetId];
  if (!permissions) return false;
  
  return permissions.view.some(role => hasRolePermission(userRole, role));
}

/**
 * Check if user can interact with a widget
 */
export function canInteractWithWidget(userRole, widgetId) {
  const permissions = WIDGET_PERMISSIONS[widgetId];
  if (!permissions) return false;
  
  return permissions.interact.some(role => hasRolePermission(userRole, role));
}

/**
 * Check if user has a specific feature permission
 */
export function hasFeaturePermission(userRole, featureId) {
  const allowedRoles = FEATURE_PERMISSIONS[featureId];
  if (!allowedRoles) return false;
  
  return allowedRoles.some(role => hasRolePermission(userRole, role));
}

/**
 * Get user role from localStorage or context
 */
export function getUserRole() {
  // Try to get from localStorage (mock auth)
  const mockUser = localStorage.getItem('mockUser');
  if (mockUser) {
    try {
      const user = JSON.parse(mockUser);
      return user.role;
    } catch (e) {
      console.error('Error parsing mockUser:', e);
    }
  }
  
  // Default to viewer if not found
  return ROLES.ORG_VIEWER;
}

/**
 * Get user info from localStorage or context
 */
export function getUserInfo() {
  const mockUser = localStorage.getItem('mockUser');
  if (mockUser) {
    try {
      return JSON.parse(mockUser);
    } catch (e) {
      console.error('Error parsing mockUser:', e);
    }
  }
  
  return {
    email: 'guest@dentaflow.ai',
    role: ROLES.ORG_VIEWER,
    name: 'Guest User',
  };
}

/**
 * Check if user is admin (org_admin or super_admin)
 */
export function isAdmin(userRole) {
  return userRole === ROLES.ORG_ADMIN || userRole === ROLES.SUPER_ADMIN;
}

/**
 * Check if user is staff (org_staff or higher)
 */
export function isStaff(userRole) {
  return hasRolePermission(userRole, ROLES.ORG_STAFF);
}

/**
 * Check if user is patient (org_viewer)
 */
export function isPatient(userRole) {
  return userRole === ROLES.ORG_VIEWER;
}

/**
 * Get visible widgets for user role
 */
export function getVisibleWidgets(userRole) {
  return Object.keys(WIDGET_PERMISSIONS).filter(widgetId =>
    canViewWidget(userRole, widgetId)
  );
}

/**
 * Get interactive widgets for user role
 */
export function getInteractiveWidgets(userRole) {
  return Object.keys(WIDGET_PERMISSIONS).filter(widgetId =>
    canInteractWithWidget(userRole, widgetId)
  );
}

/**
 * Get available features for user role
 */
export function getAvailableFeatures(userRole) {
  return Object.keys(FEATURE_PERMISSIONS).filter(featureId =>
    hasFeaturePermission(userRole, featureId)
  );
}

/**
 * Format role name for display
 */
export function formatRoleName(role) {
  const roleNames = {
    [ROLES.SUPER_ADMIN]: 'Super Admin',
    [ROLES.ORG_ADMIN]: 'Organization Admin',
    [ROLES.ORG_STAFF]: 'Staff Member',
    [ROLES.ORG_VIEWER]: 'Patient',
  };
  
  return roleNames[role] || role;
}

/**
 * Get role badge color
 */
export function getRoleBadgeColor(role) {
  const colors = {
    [ROLES.SUPER_ADMIN]: 'bg-red-500',
    [ROLES.ORG_ADMIN]: 'bg-blue-500',
    [ROLES.ORG_STAFF]: 'bg-green-500',
    [ROLES.ORG_VIEWER]: 'bg-gray-500',
  };
  
  return colors[role] || 'bg-gray-500';
}

