import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import { Menu, X } from 'lucide-react';

export default function ClinicLayout() {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [user] = useState(() => {
    const stored = localStorage.getItem('user_profile');
    return stored ? JSON.parse(stored) : null;
  });
  const mobileMenuRef = useRef(null);
  const menuButtonRef = useRef(null);

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
    { to: '/clinic/communications', label: 'Communications', icon: '📱' },
    { to: '/clinic/appointments', label: 'Appointments', icon: '📅' },
    { to: '/clinic/compliance', label: 'Compliance', icon: '🛡️' },
    { to: '/clinic/agents', label: 'AI Agents', icon: '🤖' },
    { to: '/clinic/analytics', label: 'Analytics', icon: '📊' },
    { to: '/clinic/settings', label: 'Settings', icon: '⚙️' },
  ];

  // Focus trap for mobile menu
  useEffect(() => {
    if (mobileMenuOpen && mobileMenuRef.current) {
      const menuElement = mobileMenuRef.current;
      const focusableElements = menuElement.querySelectorAll(
        'a[href], button:not([disabled])'
      );
      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      const handleTabKey = (e) => {
        if (e.key === 'Tab') {
          if (e.shiftKey && document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          } else if (!e.shiftKey && document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      };

      menuElement.addEventListener('keydown', handleTabKey);
      firstElement?.focus();

      return () => {
        menuElement.removeEventListener('keydown', handleTabKey);
      };
    }
  }, [mobileMenuOpen]);

  // Escape key to close mobile menu
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && mobileMenuOpen) {
        setMobileMenuOpen(false);
        // Restore focus to menu button
        menuButtonRef.current?.focus();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [mobileMenuOpen]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col" lang="en">
      {/* Skip Navigation */}
      <a href="#main-content" className="skip-navigation">
        Skip to main content
      </a>
      
      {/* Clinic Header */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-800 shadow-lg" role="banner">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/clinic/dashboard" className="flex items-center space-x-2">
                <span className="text-2xl" aria-hidden="true">🦷</span>
                <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-2">
                  <span className="text-lg sm:text-xl font-bold text-white">DentaFlow</span>
                  <span className="text-xs sm:text-sm text-white">Mission Control</span>
                </div>
              </Link>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-6" aria-label="Main navigation">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  <span aria-hidden="true">{link.icon}</span> {link.label}
                </Link>
              ))}
            </nav>

            {/* Desktop User Menu */}
            <div className="hidden md:flex items-center space-x-4">
              {user && (
                <div className="text-sm text-white">
                  <span className="font-medium">{user.full_name || user.email}</span>
                  <span className="text-blue-100 ml-2">({user.role})</span>
                </div>
              )}
              <Link
                to="/clinic/security"
                className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                aria-label="Security settings"
              >
                🔒 Security
              </Link>
              <button
                onClick={handleLogout}
                className="text-white hover:text-red-300 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                aria-label="Logout from clinic portal"
              >
                Logout
              </button>
            </div>

            {/* Mobile Menu Button */}
            <button
              ref={menuButtonRef}
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-md text-white hover:bg-blue-700 transition-colors"
              aria-label="Toggle navigation menu"
              aria-expanded={mobileMenuOpen}
              aria-controls="mobile-menu"
            >
              {mobileMenuOpen ? (
                <X className="w-6 h-6" aria-hidden="true" />
              ) : (
                <Menu className="w-6 h-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {mobileMenuOpen && (
          <div 
            ref={mobileMenuRef}
            id="mobile-menu" 
            className="md:hidden border-t border-blue-700 bg-blue-700"
          >
            <nav className="px-4 py-4 space-y-2" aria-label="Mobile navigation">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-white hover:bg-blue-600 px-3 py-2 rounded-md text-base font-medium transition-colors"
                >
                  <span aria-hidden="true">{link.icon}</span> {link.label}
                </Link>
              ))}
              <div className="border-t border-blue-600 pt-2 mt-2">
                {user && (
                  <div className="px-3 py-2 text-sm text-white">
                    <span className="font-medium">{user.full_name || user.email}</span>
                    <span className="text-blue-100 ml-2">({user.role})</span>
                  </div>
                )}
                <Link
                  to="/clinic/security"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-white hover:bg-blue-600 px-3 py-2 rounded-md text-base font-medium transition-colors"
                >
                  🔒 Security
                </Link>
                <button
                  onClick={() => {
                    handleLogout();
                    setMobileMenuOpen(false);
                  }}
                  className="block w-full text-left text-red-300 hover:bg-blue-600 px-3 py-2 rounded-md text-base font-medium transition-colors"
                  aria-label="Logout from clinic portal"
                >
                  Logout
                </button>
              </div>
            </nav>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main id="main-content" className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8" role="main">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto" role="contentinfo">
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

