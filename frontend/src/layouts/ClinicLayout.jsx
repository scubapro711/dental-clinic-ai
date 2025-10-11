import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';

export default function ClinicLayout() {
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
      {/* Clinic Header */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/clinic/dashboard" className="flex items-center space-x-2">
                <span className="text-2xl">🦷</span>
                <span className="text-xl font-bold text-white">DentaFlow</span>
                <span className="text-sm text-blue-200">Mission Control</span>
              </Link>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex space-x-6">
              <Link
                to="/clinic/dashboard"
                className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                🎯 Dashboard
              </Link>
              <Link
                to="/clinic/patients"
                className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                👥 Patients
              </Link>
              <Link
                to="/clinic/appointments"
                className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                📅 Appointments
              </Link>
              <Link
                to="/clinic/agents"
                className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                🤖 AI Agents
              </Link>
              <Link
                to="/clinic/analytics"
                className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                📊 Analytics
              </Link>
              <Link
                to="/clinic/settings"
                className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                ⚙️ Settings
              </Link>
            </nav>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              {user && (
                <div className="text-sm text-white">
                  <span className="font-medium">{user.full_name || user.email}</span>
                  <span className="text-blue-200 ml-2">({user.role})</span>
                </div>
              )}
              <button
                onClick={handleLogout}
                className="text-white hover:text-red-300 px-3 py-2 rounded-md text-sm font-medium transition-colors"
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
          <div className="flex justify-between items-center text-sm text-gray-500">
            <p>© 2025 DentaFlow Mission Control. AI-Powered Dental Management.</p>
            <p>Version 20.1.0</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

