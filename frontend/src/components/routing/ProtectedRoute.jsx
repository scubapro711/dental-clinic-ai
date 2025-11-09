import { Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

/**
 * ProtectedRoute Component
 * 
 * Protects routes based on authentication and user roles.
 * Redirects unauthorized users to appropriate pages.
 */
export function ProtectedRoute({ children, allowedRoles, redirectTo = '/login' }) {
  const { user, isAuthenticated, isLoading } = useAuth();
  
  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }
  
  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to={redirectTo} replace state={{ from: window.location.pathname }} />;
  }
  
  // Check if user has required role
  if (allowedRoles && allowedRoles.length > 0) {
    if (!allowedRoles.includes(user?.role)) {
      // Redirect to appropriate portal based on user's actual role
      const defaultPortal = getDefaultPortalForRole(user?.role);
      return <Navigate to={defaultPortal} replace />;
    }
  }
  
  // User is authenticated and has correct role
  return <>{children}</>;
}

/**
 * Get default portal path based on user role
 */
function getDefaultPortalForRole(role) {
  switch (role) {
    case 'super_admin':
      return '/admin/dashboard';
    case 'org_admin':
    case 'org_staff':
      return '/clinic/dashboard';
    case 'patient':
      return '/patient/dashboard';
    case 'org_viewer':
      return '/patient/dashboard'; // Legacy role, same as patient
    default:
      return '/login';
  }
}

/**
 * RoleBasedRedirect Component
 * 
 * Redirects authenticated users to their appropriate portal
 */
export function RoleBasedRedirect() {
  const { user, isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  const defaultPortal = getDefaultPortalForRole(user?.role);
  return <Navigate to={defaultPortal} replace />;
}

