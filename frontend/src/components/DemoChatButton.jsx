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
      try {
        const pos = JSON.parse(saved);
        // Validate position is on screen
        if (pos.x >= 0 && pos.x <= window.innerWidth - 200 &&
            pos.y >= 0 && pos.y <= window.innerHeight - 100) {
          return pos;
        }
      } catch (e) {
        // Invalid saved position, use default
      }
    }
    // Default: bottom-right corner with safe margins
    return { 
      x: window.innerWidth - 180,
      y: window.innerHeight - 100
    };
  };

  return (
    <>
      {!isChatOpen && (
        <Draggable
          nodeRef={nodeRef}
          defaultPosition={getSavedPosition()}
          positionOffset={{x: 0, y: 0}}
          onStop={handleStop}
        >
          <div
            ref={nodeRef}
            className="demo-chat-fab-wrapper"
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              cursor: 'grab',
              zIndex: 999,
            }}
          >
            <button
              className="demo-chat-fab"
              onClick={toggleChat}
              aria-label="Chat with AI Assistant (Draggable)"
            >
              <div className="demo-chat-fab-content">
                <span className="demo-chat-fab-icon">💬</span>
                <span className="demo-chat-fab-text">AI Chat</span>
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

