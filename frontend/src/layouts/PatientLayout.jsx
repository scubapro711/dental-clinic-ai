import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';

export default function PatientLayout() {
  const navigate = useNavigate();
  const [user] = useState(() => {
    const stored = localStorage.getItem('user_profile');
    return stored ? JSON.parse(stored) : null;
  });

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_profile');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Patient Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/patient/dashboard" className="flex items-center space-x-2">
                <span className="text-2xl">🦷</span>
                <span className="text-xl font-bold text-blue-600">DentaFlow</span>
                <span className="text-sm text-gray-500">Patient Portal</span>
              </Link>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex space-x-8">
              <Link
                to="/patient/dashboard"
                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                Dashboard
              </Link>
              <Link
                to="/patient/appointments"
                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                Appointments
              </Link>
              <Link
                to="/patient/medical-records"
                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                Medical Records
              </Link>
              <Link
                to="/patient/billing"
                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                Billing
              </Link>
              <Link
                to="/patient/profile"
                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                Profile
              </Link>
            </nav>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              {user && (
                <div className="text-sm text-gray-700">
                  <span className="font-medium">{user.full_name || user.email}</span>
                </div>
              )}
              <button
                onClick={handleLogout}
                className="text-gray-700 hover:text-red-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            © 2025 DentaFlow Patient Portal. Your dental health, simplified.
          </p>
        </div>
      </footer>
    </div>
  );
}

