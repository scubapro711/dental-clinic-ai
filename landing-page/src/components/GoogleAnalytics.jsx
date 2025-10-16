import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * Google Analytics Component
 * 
 * Tracks page views and events
 * Replace GA_MEASUREMENT_ID with your actual Google Analytics ID
 */
export default function GoogleAnalytics() {
  const location = useLocation();
  const GA_MEASUREMENT_ID = process.env.REACT_APP_GA_MEASUREMENT_ID || 'G-XXXXXXXXXX';

  useEffect(() => {
    // Initialize Google Analytics
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('config', GA_MEASUREMENT_ID, {
        page_path: location.pathname + location.search,
      });
    }
  }, [location, GA_MEASUREMENT_ID]);

  return null;
}

/**
 * Track custom events
 * 
 * Usage:
 * trackEvent('button_click', { button_name: 'Start Free Trial' });
 */
export function trackEvent(eventName, eventParams = {}) {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', eventName, eventParams);
  }
}

/**
 * Track conversions
 * 
 * Usage:
 * trackConversion('sign_up', { method: 'email' });
 */
export function trackConversion(conversionName, conversionParams = {}) {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'conversion', {
      send_to: `${process.env.REACT_APP_GA_MEASUREMENT_ID}/${conversionName}`,
      ...conversionParams
    });
  }
}

/**
 * Initialize Google Analytics Script
 * Add this to index.html or App.jsx
 */
export function initGoogleAnalytics(measurementId) {
  if (typeof window === 'undefined') return;

  // Create script tag
  const script1 = document.createElement('script');
  script1.async = true;
  script1.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
  document.head.appendChild(script1);

  // Initialize gtag
  const script2 = document.createElement('script');
  script2.innerHTML = `
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '${measurementId}', {
      'anonymize_ip': true,
      'cookie_flags': 'SameSite=None;Secure'
    });
  `;
  document.head.appendChild(script2);

  // Make gtag available globally
  window.gtag = function() {
    window.dataLayer.push(arguments);
  };
}

