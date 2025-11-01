import React, { useState, useRef } from 'react';
import Draggable from 'react-draggable';
import InteractiveDemoChat from './InteractiveDemoChat';
import './DemoChatButton.css';

const DemoChatButton = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const nodeRef = useRef(null);  // React 18 compatibility

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  const handleStop = (e, data) => {
    // Save position to localStorage when drag stops
    const position = { x: data.x, y: data.y };
    localStorage.setItem('chatButtonPosition', JSON.stringify(position));
  };

  // Load saved position or use default
  const getSavedPosition = () => {
    const saved = localStorage.getItem('chatButtonPosition');
    if (saved) {
      return JSON.parse(saved);
    }
    // Default: bottom-right corner with safe margins
    // Position is relative to top-left (0,0), not using window size
    return { 
      x: 20,  // 20px from left (will appear on left side)
      y: 20   // 20px from top
    };
  };

  return (
    <>
      {!isChatOpen && (
        <Draggable
          nodeRef={nodeRef}
          defaultPosition={getSavedPosition()}
          onStop={handleStop}
        >
          <div
            ref={nodeRef}
            className="demo-chat-fab-wrapper"
            style={{
              position: 'fixed',
              cursor: 'grab',
              zIndex: 999,
            }}
          >
            <button
              className="demo-chat-fab"
              onClick={toggleChat}
              aria-label="Try Interactive Demo (Draggable)"
            >
              <div className="demo-chat-fab-content">
                <span className="demo-chat-fab-icon">💬</span>
                <span className="demo-chat-fab-text">Try Demo</span>
              </div>
              <div className="demo-chat-fab-pulse"></div>
            </button>
          </div>
        </Draggable>
      )}

      {isChatOpen && <InteractiveDemoChat onClose={toggleChat} />}
    </>
  );
};

export default DemoChatButton;

