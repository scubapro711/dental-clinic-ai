/**
 * CopilotKit Test Page
 * 
 * This page demonstrates the CopilotKit integration with our LangGraph agent system.
 * It provides a simple chat interface to test agent interactions.
 */

import React from 'react';
import { CopilotPopup } from '@copilotkit/react-ui';
import { useCopilotChat, useCopilotAction } from '@copilotkit/react-core';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import '@copilotkit/react-ui/styles.css';

export function CopilotTestPage() {
  const { messages, sendMessage, isLoading } = useCopilotChat();
  const [testMessage, setTestMessage] = React.useState('');

  // Define actions that the agent can perform
  useCopilotAction({
    name: 'get_appointments',
    description: 'Get appointments for a specific date',
    parameters: [
      {
        name: 'date',
        type: 'string',
        description: 'Date in YYYY-MM-DD format',
        required: true,
      },
    ],
    handler: async ({ date }) => {
      console.log('Getting appointments for:', date);
      return {
        success: true,
        message: `Fetching appointments for ${date}`,
      };
    },
  });

  const handleSendTest = () => {
    if (testMessage.trim()) {
      sendMessage(testMessage);
      setTestMessage('');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-gray-900">
            🤖 CopilotKit Integration Test
          </h1>
          <p className="text-lg text-gray-600">
            Testing LangGraph agent system with CopilotKit
          </p>
        </div>

        {/* Status Card */}
        <Card className="p-6 bg-white shadow-lg">
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-gray-800">
              Connection Status
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="font-medium text-green-700">Backend Connected</span>
                </div>
                <p className="text-sm text-green-600 mt-1">
                  {import.meta.env.VITE_API_URL || 'http://localhost:8000'}
                </p>
              </div>
              
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="font-medium text-blue-700">Agent: dental_assistant</span>
                </div>
                <p className="text-sm text-blue-600 mt-1">
                  Supervisor + 3 agents
                </p>
              </div>
              
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                  <span className="font-medium text-purple-700">
                    {isLoading ? 'Processing...' : 'Ready'}
                  </span>
                </div>
                <p className="text-sm text-purple-600 mt-1">
                  {messages.length} messages
                </p>
              </div>
            </div>
          </div>
        </Card>

        {/* Test Controls */}
        <Card className="p-6 bg-white shadow-lg">
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-gray-800">
              Quick Test Messages
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Button
                onClick={() => sendMessage('What are the total appointments for today?')}
                variant="outline"
                className="justify-start text-left h-auto py-3"
              >
                <div>
                  <div className="font-medium">📅 Appointments Query</div>
                  <div className="text-sm text-gray-500">Test Alex agent</div>
                </div>
              </Button>
              
              <Button
                onClick={() => sendMessage('Show me today\'s revenue summary')}
                variant="outline"
                className="justify-start text-left h-auto py-3"
              >
                <div>
                  <div className="font-medium">💰 Revenue Query</div>
                  <div className="text-sm text-gray-500">Test CFO agent</div>
                </div>
              </Button>
              
              <Button
                onClick={() => sendMessage('Are there any scheduling conflicts?')}
                variant="outline"
                className="justify-start text-left h-auto py-3"
              >
                <div>
                  <div className="font-medium">⚠️ Conflicts Query</div>
                  <div className="text-sm text-gray-500">Test Admin agent</div>
                </div>
              </Button>
              
              <Button
                onClick={() => sendMessage('I have a toothache, what should I do?')}
                variant="outline"
                className="justify-start text-left h-auto py-3"
              >
                <div>
                  <div className="font-medium">🦷 Medical Query</div>
                  <div className="text-sm text-gray-500">Test triage logic</div>
                </div>
              </Button>
            </div>
          </div>
        </Card>

        {/* Custom Message Input */}
        <Card className="p-6 bg-white shadow-lg">
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-gray-800">
              Custom Message
            </h2>
            <div className="flex space-x-2">
              <input
                type="text"
                value={testMessage}
                onChange={(e) => setTestMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendTest()}
                placeholder="Type your message here..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <Button
                onClick={handleSendTest}
                disabled={!testMessage.trim() || isLoading}
              >
                Send
              </Button>
            </div>
          </div>
        </Card>

        {/* Message History */}
        {messages.length > 0 && (
          <Card className="p-6 bg-white shadow-lg">
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold text-gray-800">
                Message History
              </h2>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-blue-50 border border-blue-200'
                        : 'bg-gray-50 border border-gray-200'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0">
                        {msg.role === 'user' ? '👤' : '🤖'}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-sm text-gray-500 mb-1">
                          {msg.role === 'user' ? 'You' : 'Agent'}
                        </div>
                        <div className="text-gray-800">{msg.content}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        )}

        {/* Instructions */}
        <Card className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200">
          <div className="space-y-3">
            <h3 className="text-xl font-semibold text-gray-800">
              💡 How to Use
            </h3>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start space-x-2">
                <span className="text-blue-500 font-bold">1.</span>
                <span>Click any quick test button to send a pre-defined message</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-blue-500 font-bold">2.</span>
                <span>Or type your own message in the custom input field</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-blue-500 font-bold">3.</span>
                <span>The supervisor will route your message to the appropriate agent</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-blue-500 font-bold">4.</span>
                <span>Watch the message history to see agent responses</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-blue-500 font-bold">5.</span>
                <span>Click the floating chat icon (bottom right) for the CopilotKit popup interface</span>
              </li>
            </ul>
          </div>
        </Card>
      </div>

      {/* CopilotKit Popup - Floating chat interface */}
      <CopilotPopup
        labels={{
          title: "DentalAI Assistant",
          initial: "Hi! I'm your DentalAI assistant. How can I help you today?",
        }}
      />
    </div>
  );
}

export default CopilotTestPage;
