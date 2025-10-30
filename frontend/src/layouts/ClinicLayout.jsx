import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Menu, X, LogOut } from 'lucide-react';

export default function ClinicLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
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
    { to: '/clinic/dashboard', label: 'Mission Control', icon: '🎯' },
    { to: '/clinic/dashboard', label: 'Dashboard', icon: '🏠' },
    { to: '/clinic/patients', label: 'Patients', icon: '👥' },
    { to: '/clinic/communications', label: 'Communications', icon: '📱' },
    { to: '/clinic/appointments', label: 'Appointments', icon: '📅' },
    { to: '/clinic/compliance', label: 'Compliance', icon: '🛡️' },
    { to: '/clinic/agents', label: 'AI Agents', icon: '🤖' },
    { to: '/clinic/analytics', label: 'Analytics', icon: '📊' },
    { to: '/clinic/settings', label: 'Settings', icon: '⚙️' },
  ];

  // Close mobile sidebar on route change
  useEffect(() => {
    setMobileSidebarOpen(false);
  }, [location.pathname]);

  // Escape key to close mobile sidebar
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && mobileSidebarOpen) {
        setMobileSidebarOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [mobileSidebarOpen]);

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen bg-gray-50 flex" lang="en" dir="ltr">
      {/* Skip Navigation */}
      <a href="#main-content" className="skip-navigation">
        Skip to main content
      </a>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Header (Mobile Only) */}
        <header className="lg:hidden bg-gradient-to-r from-blue-600 to-blue-800 shadow-lg sticky top-0 z-40" role="banner">
          <div className="px-4 h-16 flex items-center justify-between">
            {/* Logo */}
            <Link to="/clinic/dashboard" className="flex items-center space-x-2">
              <span className="text-2xl" aria-hidden="true">🦷</span>
              <div className="flex flex-col">
                <span className="text-lg font-bold text-white">DentaFlow</span>
                <span className="text-xs text-white opacity-90">Mission Control</span>
              </div>
            </Link>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}
              className="p-2 rounded-md text-white hover:bg-blue-700 transition-colors"
              aria-label="Toggle navigation menu"
              aria-expanded={mobileSidebarOpen}
            >
              {mobileSidebarOpen ? (
                <X className="w-6 h-6" aria-hidden="true" />
              ) : (
                <Menu className="w-6 h-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </header>

        {/* Main Content */}
        <main id="main-content" className="flex-1 lg:pl-64" role="main">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
            <Outlet />
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-auto lg:pl-64" role="contentinfo">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex flex-col sm:flex-row justify-between items-center text-xs sm:text-sm text-gray-500 space-y-2 sm:space-y-0">
              <p>© 2025 DentaFlow Mission Control. AI-Powered Dental Management.</p>
              <p>Version 20.5.0</p>
            </div>
          </div>
        </footer>
      </div>

      {/* Fixed Left Sidebar (Desktop) */}
      <aside 
        className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:left-0 lg:top-0 lg:bottom-0 bg-gradient-to-b from-blue-600 to-blue-800 shadow-2xl"
        role="navigation"
        aria-label="Main navigation"
      >
        {/* Logo */}
        <div className="p-6 border-b border-blue-500">
          <Link to="/clinic/dashboard" className="flex items-center space-x-3">
            <span className="text-3xl" aria-hidden="true">🦷</span>
            <div className="flex flex-col">
              <span className="text-xl font-bold text-white">DentaFlow</span>
              <span className="text-sm text-blue-100">Mission Control</span>
            </div>
          </Link>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 overflow-y-auto py-6 px-4 space-y-2">
          {navLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`
                flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200
                ${isActive(link.to)
                  ? 'bg-white text-blue-700 shadow-lg'
                  : 'text-white hover:bg-blue-700 hover:shadow-md'
                }
              `}
            >
              <span className="text-xl" aria-hidden="true">{link.icon}</span>
              <span>{link.label}</span>
            </Link>
          ))}
        </nav>

        {/* User Section */}
        <div className="border-t border-blue-500 p-4 space-y-3">
          {user && (
            <div className="px-4 py-3 bg-blue-700 rounded-lg">
              <div className="text-sm font-medium text-white">
                {user.full_name || user.email}
              </div>
              <div className="text-xs text-blue-200 mt-1">
                {user.role}
              </div>
            </div>
          )}

          <Link
            to="/clinic/security"
            className="flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium text-white hover:bg-blue-700 transition-colors"
          >
            <span aria-hidden="true">🔒</span>
            <span>Security</span>
          </Link>

          <button
            onClick={handleLogout}
            className="flex items-center space-x-3 w-full px-4 py-3 rounded-lg text-sm font-medium text-red-200 hover:bg-red-600 hover:text-white transition-colors"
            aria-label="Logout from clinic portal"
          >
            <LogOut className="w-5 h-5" aria-hidden="true" />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Mobile Sidebar Overlay */}
      {mobileSidebarOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-50"
          onClick={() => setMobileSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Mobile Sidebar (Slides from Left) */}
      <aside 
        className={`
          lg:hidden fixed top-0 left-0 bottom-0 w-80 max-w-[85vw] bg-gradient-to-b from-blue-600 to-blue-800 shadow-2xl z-50
          transform transition-transform duration-300 ease-in-out
          ${mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
        role="navigation"
        aria-label="Mobile navigation"
      >
        {/* Mobile Sidebar Header */}
        <div className="p-6 border-b border-blue-500 flex items-center justify-between">
          <Link to="/clinic/dashboard" className="flex items-center space-x-3" onClick={() => setMobileSidebarOpen(false)}>
            <span className="text-3xl" aria-hidden="true">🦷</span>
            <div className="flex flex-col">
              <span className="text-xl font-bold text-white">DentaFlow</span>
              <span className="text-sm text-blue-100">Mission Control</span>
            </div>
          </Link>
          <button
            onClick={() => setMobileSidebarOpen(false)}
            className="p-2 rounded-md text-white hover:bg-blue-700 transition-colors"
            aria-label="Close navigation menu"
          >
            <X className="w-6 h-6" aria-hidden="true" />
          </button>
        </div>

        {/* Mobile Navigation Links */}
        <nav className="flex-1 overflow-y-auto py-6 px-4 space-y-2">
          {navLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              onClick={() => setMobileSidebarOpen(false)}
              className={`
                flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200
                ${isActive(link.to)
                  ? 'bg-white text-blue-700 shadow-lg'
                  : 'text-white hover:bg-blue-700 hover:shadow-md'
                }
              `}
            >
              <span className="text-xl" aria-hidden="true">{link.icon}</span>
              <span>{link.label}</span>
            </Link>
          ))}
        </nav>

        {/* Mobile User Section */}
        <div className="border-t border-blue-500 p-4 space-y-3">
          {user && (
            <div className="px-4 py-3 bg-blue-700 rounded-lg">
              <div className="text-sm font-medium text-white">
                {user.full_name || user.email}
              </div>
              <div className="text-xs text-blue-200 mt-1">
                {user.role}
              </div>
            </div>
          )}

          <Link
            to="/clinic/security"
            onClick={() => setMobileSidebarOpen(false)}
            className="flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium text-white hover:bg-blue-700 transition-colors"
          >
            <span aria-hidden="true">🔒</span>
            <span>Security</span>
          </Link>

          <button
            onClick={() => {
              handleLogout();
              setMobileSidebarOpen(false);
            }}
            className="flex items-center space-x-3 w-full px-4 py-3 rounded-lg text-sm font-medium text-red-200 hover:bg-red-600 hover:text-white transition-colors"
            aria-label="Logout from clinic portal"
          >
            <LogOut className="w-5 h-5" aria-hidden="true" />
            <span>Logout</span>
          </button>
        </div>
      </aside>
    </div>
  );
}

