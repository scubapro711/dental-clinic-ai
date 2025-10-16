import React, { useState } from 'react';
import InteractiveDemoChat from './InteractiveDemoChat';
import './DemoChatButton.css';

const DemoChatButton = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  return (
    <>
      {!isChatOpen && (
        <button
          className="demo-chat-fab"
          onClick={toggleChat}
          aria-label="Try Interactive Demo"
        >
          <div className="demo-chat-fab-content">
            <span className="demo-chat-fab-icon">💬</span>
            <span className="demo-chat-fab-text">Try Demo</span>
          </div>
          <div className="demo-chat-fab-pulse"></div>
        </button>
      )}

      {isChatOpen && <InteractiveDemoChat onClose={toggleChat} />}
    </>
  );
};

export default DemoChatButton;

