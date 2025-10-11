import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import { Menu, X } from 'lucide-react';

export default function PatientLayout() {
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
    { to: '/patient/dashboard', label: 'Dashboard' },
    { to: '/patient/appointments', label: 'Appointments' },
    { to: '/patient/medical-records', label: 'Medical Records' },
    { to: '/patient/billing', label: 'Billing' },
    { to: '/patient/profile', label: 'Profile' },
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
      
      {/* Patient Header */}
      <header className="bg-white shadow-sm border-b border-gray-200" role="banner">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/patient/dashboard" className="flex items-center space-x-2">
                <span className="text-2xl">🦷</span>
                <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-2">
                  <span className="text-lg sm:text-xl font-bold text-blue-600">DentaFlow</span>
                  <span className="text-xs sm:text-sm text-gray-500">Patient Portal</span>
                </div>
              </Link>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-8" aria-label="Main navigation">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  {link.label}
                </Link>
              ))}
            </nav>

            {/* Desktop User Menu */}
            <div className="hidden md:flex items-center space-x-4">
              {user && (
                <div className="text-sm text-gray-700">
                  <span className="font-medium">{user.full_name || user.email}</span>
                </div>
              )}
              <button
                onClick={handleLogout}
                className="text-gray-700 hover:text-red-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Logout
              </button>
            </div>

            {/* Mobile Menu Button */}
            <button
              ref={menuButtonRef}
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-md text-gray-700 hover:bg-gray-100 transition-colors"
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
            className="md:hidden border-t border-gray-200 bg-white"
          >
            <nav className="px-4 py-4 space-y-2" aria-label="Mobile navigation">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className="block text-gray-700 hover:text-blue-600 hover:bg-blue-50 px-3 py-2 rounded-md text-base font-medium transition-colors"
                >
                  {link.label}
                </Link>
              ))}
              <div className="border-t border-gray-200 pt-2 mt-2">
                {user && (
                  <div className="px-3 py-2 text-sm text-gray-700">
                    <span className="font-medium">{user.full_name || user.email}</span>
                  </div>
                )}
                <button
                  onClick={() => {
                    handleLogout();
                    setMobileMenuOpen(false);
                  }}
                  className="block w-full text-left text-red-600 hover:bg-red-50 px-3 py-2 rounded-md text-base font-medium transition-colors"
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
          <p className="text-center text-xs sm:text-sm text-gray-500">
            © 2025 DentaFlow Patient Portal. Your dental health, simplified.
          </p>
        </div>
      </footer>
    </div>
  );
}

