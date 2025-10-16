import { useState, useEffect } from 'react';
import { X, Cookie } from 'lucide-react';

/**
 * Cookie Consent Banner Component
 * 
 * GDPR-compliant cookie consent banner with:
 * - Accept/Reject options
 * - Link to Cookie Policy
 * - LocalStorage persistence
 * - Slide-in animation
 */
export default function CookieConsent() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Check if user has already made a choice
    const cookieConsent = localStorage.getItem('cookieConsent');
    if (!cookieConsent) {
      // Show banner after 1 second delay
      setTimeout(() => setIsVisible(true), 1000);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('cookieConsent', 'accepted');
    setIsVisible(false);
    // Initialize analytics here
    console.log('Cookies accepted - Initialize analytics');
  };

  const handleReject = () => {
    localStorage.setItem('cookieConsent', 'rejected');
    setIsVisible(false);
    console.log('Cookies rejected - No analytics');
  };

  if (!isVisible) return null;

  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-50 p-4 bg-white border-t-2 border-gray-200 shadow-2xl animate-slide-up"
      dir="rtl"
    >
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          {/* Icon and Message */}
          <div className="flex items-start gap-3 flex-1">
            <Cookie className="h-6 w-6 text-blue-600 flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-bold text-gray-900 mb-1">
                אנחנו משתמשים בעוגיות 🍪
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                אנחנו משתמשים בעוגיות כדי לשפר את חוויית השימוש שלך, לנתח תנועה באתר, ולספק תוכן מותאם אישית. 
                על ידי לחיצה על "אני מסכים", אתה מאשר את השימוש שלנו בעוגיות.{' '}
                <a
                  href="/legal/cookies"
                  className="text-blue-600 hover:text-blue-700 underline font-medium"
                >
                  קרא עוד במדיניות העוגיות
                </a>
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <button
              onClick={handleReject}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
            >
              דחה
            </button>
            <button
              onClick={handleAccept}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors shadow-md"
            >
              אני מסכים
            </button>
          </div>
        </div>
      </div>

      {/* Close Button */}
      <button
        onClick={handleReject}
        className="absolute top-2 left-2 p-1 text-gray-400 hover:text-gray-600 transition-colors"
        aria-label="Close"
      >
        <X className="h-5 w-5" />
      </button>

      <style jsx>{`
        @keyframes slide-up {
          from {
            transform: translateY(100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
        .animate-slide-up {
          animation: slide-up 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}

