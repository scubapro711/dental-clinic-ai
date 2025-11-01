import React, { useState, useEffect } from 'react';
import Draggable from 'react-draggable';
import InteractiveDemoChat from './InteractiveDemoChat';
import './DemoChatButton.css';

const DemoChatButton = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [position, setPosition] = useState(() => {
    // Load saved position from localStorage
    const saved = localStorage.getItem('chatButtonPosition');
    // Default position: bottom-right corner
    return saved ? JSON.parse(saved) : { 
      x: window.innerWidth - 170, 
      y: window.innerHeight - 90 
    };
  });

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  const handleDrag = (e, data) => {
    const newPosition = { x: data.x, y: data.y };
    setPosition(newPosition);
    // Save position to localStorage
    localStorage.setItem('chatButtonPosition', JSON.stringify(newPosition));
  };

  return (
    <>
      {!isChatOpen && (
        <Draggable
          position={position}
          onDrag={handleDrag}
          onStop={handleDrag}
        >
          <div
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

