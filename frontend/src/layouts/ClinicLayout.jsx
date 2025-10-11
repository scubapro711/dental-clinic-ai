import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { Menu, X } from 'lucide-react';

export default function ClinicLayout() {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [user] = useState(() => {
    const stored = localStorage.getItem('user_profile');
    return stored ? JSON.parse(stored) : null;
  });

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_profile');
    localStorage.removeItem('token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('mockUser');
    navigate('/login');
  };

  const navLinks = [
    { to: '/clinic/dashboard', label: 'Dashboard', icon: '🎯' },
    { to: '/clinic/patients', label: 'Patients', icon: '👥' },
    { to: '/clinic/appointments', label: 'Appointments', icon: '📅' },
    { to: '/clinic/agents', label: 'AI Agents', icon: '🤖' },
    { to: '/clinic/analytics', label: 'Analytics', icon: '📊' },
    { to: '/clinic/settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Clinic Header */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/clinic/dashboard" className="flex items-center space-x-2">
                <span className="text-2xl">🦷</span>
                <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-2">
                  <span className="text-lg sm:text-xl font-bold text-white">DentaFlow</span>
                  <span className="text-xs sm:text-sm text-blue-200">Mission Control</span>
                </div>
              </Link>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-6">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  {link.icon} {link.label}
                </Link>
              ))}
            </nav>

            {/* Desktop User Menu */}
            <div className="hidden md:flex items-center space-x-4">
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

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-md text-white hover:bg-blue-700 transition-colors"
            >
              {mobileMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-blue-700 bg-blue-700">
            <nav className="px-4 py-4 space-y-2">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-white hover:bg-blue-600 px-3 py-2 rounded-md text-base font-medium transition-colors"
                >
                  {link.icon} {link.label}
                </Link>
              ))}
              <div className="border-t border-blue-600 pt-2 mt-2">
                {user && (
                  <div className="px-3 py-2 text-sm text-white">
                    <span className="font-medium">{user.full_name || user.email}</span>
                    <span className="text-blue-200 ml-2">({user.role})</span>
                  </div>
                )}
                <button
                  onClick={() => {
                    handleLogout();
                    setMobileMenuOpen(false);
                  }}
                  className="block w-full text-left text-red-300 hover:bg-blue-600 px-3 py-2 rounded-md text-base font-medium transition-colors"
                >
                  Logout
                </button>
              </div>
            </nav>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-center text-xs sm:text-sm text-gray-500 space-y-2 sm:space-y-0">
            <p>© 2025 DentaFlow Mission Control. AI-Powered Dental Management.</p>
            <p>Version 20.5.0</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

