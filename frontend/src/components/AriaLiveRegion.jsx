import React from 'react';

/**
 * ARIA Live Region Component
 * 
 * Announces dynamic content changes to screen readers
 * 
 * Props:
 * - message: string - The message to announce
 * - politeness: 'polite' | 'assertive' - How urgently to announce
 * - clearDelay: number - Milliseconds before clearing message (default: 3000)
 */
export default function AriaLiveRegion({ 
  message, 
  politeness = 'polite',
  clearDelay = 3000 
}) {
  const [currentMessage, setCurrentMessage] = React.useState('');

  React.useEffect(() => {
    if (message) {
      setCurrentMessage(message);
      
      if (clearDelay > 0) {
        const timer = setTimeout(() => {
          setCurrentMessage('');
        }, clearDelay);
        
        return () => clearTimeout(timer);
      }
    }
  }, [message, clearDelay]);

  return (
    <div
      role="status"
      aria-live={politeness}
      aria-atomic="true"
      className="sr-only"
    >
      {currentMessage}
    </div>
  );
}

/**
 * Hook for managing ARIA live announcements
 */
export function useAriaLive() {
  const [message, setMessage] = React.useState('');
  const [politeness, setPoliteness] = React.useState('polite');

  const announce = React.useCallback((text, urgent = false) => {
    setMessage(text);
    setPoliteness(urgent ? 'assertive' : 'polite');
  }, []);

  const announcePolite = React.useCallback((text) => {
    announce(text, false);
  }, [announce]);

  const announceAssertive = React.useCallback((text) => {
    announce(text, true);
  }, [announce]);

  return {
    message,
    politeness,
    announce,
    announcePolite,
    announceAssertive
  };
}
