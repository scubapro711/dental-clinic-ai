import { Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

export default function RoleBasedRedirect() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const userProfile = localStorage.getItem('user_profile');

    if (!token || !userProfile) {
      setLoading(false);
      return;
    }

    try {
      const parsed = JSON.parse(userProfile);
      setUser(parsed);
    } catch (error) {
      console.error('Failed to parse user profile:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Role-based redirect
  const role = user.role?.toLowerCase();

  if (role === 'super_admin') {
    return <Navigate to="/admin/dashboard" replace />;
  }

  if (role === 'org_admin' || role === 'org_staff') {
    return <Navigate to="/clinic/dashboard" replace />;
  }

  if (role === 'patient' || role === 'org_viewer') {
    return <Navigate to="/patient/dashboard" replace />;
  }

  // Default fallback
  return <Navigate to="/login" replace />;
}

