import { useState } from 'react';
import { useCopilotAction } from "@copilotkit/react-core";
import { MessageSquare, Loader2, CheckCircle, XCircle } from 'lucide-react';

/**
 * AgentAction - Embedded agent action button in widgets
 * 
 * This component allows users to trigger agent actions directly from any widget.
 * The agent (Alex, Marcus, or Sophia) will execute the action and report back.
 * 
 * @param {string} agentName - Which agent to use (alex, marcus, sophia)
 * @param {string} action - What action to perform
 * @param {object} context - Context data for the action (patient, appointment, etc.)
 * @param {string} label - Button label
 * @param {string} variant - Button style (primary, secondary, ghost)
 */
export function AgentAction({ 
  agentName, 
  action, 
  context, 
  label, 
  variant = 'secondary',
  icon: Icon = MessageSquare,
  onSuccess,
  onError
}) {
  const [status, setStatus] = useState('idle'); // idle, loading, success, error
  const [result, setResult] = useState(null);

  // Register the action with CopilotKit
  useCopilotAction({
    name: `${agentName}_${action}`,
    description: `Ask ${agentName} to ${action}`,
    parameters: [
      {
        name: "context",
        type: "object",
        description: "Context data for the action",
      },
    ],
    handler: async ({ context: actionContext }) => {
      setStatus('loading');
      try {
        // Call backend API to execute agent action
        const response = await fetch('/api/v1/agent/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agent: agentName,
            action,
            context: actionContext || context,
          }),
        });

        if (!response.ok) throw new Error('Action failed');

        const data = await response.json();
        setResult(data);
        setStatus('success');
        onSuccess?.(data);

        // Auto-reset after 3 seconds
        setTimeout(() => setStatus('idle'), 3000);
      } catch (error) {
        console.error('Agent action failed:', error);
        setStatus('error');
        onError?.(error);
        setTimeout(() => setStatus('idle'), 3000);
      }
    },
  });

  const handleClick = async () => {
    setStatus('loading');
    try {
      const response = await fetch('/api/v1/agent/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent: agentName,
          action,
          context,
        }),
      });

      if (!response.ok) throw new Error('Action failed');

      const data = await response.json();
      setResult(data);
      setStatus('success');
      onSuccess?.(data);

      setTimeout(() => setStatus('idle'), 3000);
    } catch (error) {
      console.error('Agent action failed:', error);
      setStatus('error');
      onError?.(error);
      setTimeout(() => setStatus('idle'), 3000);
    }
  };

  const buttonStyles = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-100 hover:bg-gray-200 text-gray-700',
    ghost: 'hover:bg-gray-100 text-gray-600',
  };

  return (
    <div className="relative inline-block">
      <button
        onClick={handleClick}
        disabled={status === 'loading'}
        className={`
          inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium
          transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
          ${buttonStyles[variant]}
        `}
      >
        {status === 'loading' && <Loader2 className="w-4 h-4 animate-spin" />}
        {status === 'success' && <CheckCircle className="w-4 h-4 text-green-600" />}
        {status === 'error' && <XCircle className="w-4 h-4 text-red-600" />}
        {status === 'idle' && <Icon className="w-4 h-4" />}
        
        <span>
          {status === 'loading' && 'Processing...'}
          {status === 'success' && 'Done!'}
          {status === 'error' && 'Failed'}
          {status === 'idle' && label}
        </span>
      </button>

      {/* Result tooltip */}
      {result && status === 'success' && (
        <div className="absolute top-full left-0 mt-2 p-2 bg-white border border-gray-200 rounded-lg shadow-lg text-xs z-10 min-w-[200px]">
          <p className="text-gray-600">{result.message || 'Action completed successfully'}</p>
        </div>
      )}
    </div>
  );
}

/**
 * AgentChatButton - Opens a chat modal with specific agent
 */
export function AgentChatButton({ agentName, context, label = "Chat" }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white transition-colors"
      >
        <MessageSquare className="w-4 h-4" />
        <span>{label}</span>
      </button>

      {isOpen && (
        <AgentChatModal
          agentName={agentName}
          context={context}
          onClose={() => setIsOpen(false)}
        />
      )}
    </>
  );
}

/**
 * AgentChatModal - Modal for chatting with a specific agent
 */
function AgentChatModal({ agentName, context, onClose }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl h-[600px] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div>
            <h3 className="font-semibold text-lg">Chat with {agentName}</h3>
            <p className="text-sm text-gray-500">
              {agentName === 'Alex' && 'Patient-facing agent'}
              {agentName === 'Marcus' && 'Financial analyst'}
              {agentName === 'Sophia' && 'Operations manager'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <XCircle className="w-5 h-5" />
          </button>
        </div>

        {/* Chat area - will be integrated with assistant-ui */}
        <div className="flex-1 p-4 overflow-y-auto">
          <p className="text-gray-500 text-center mt-8">
            Chat interface will be integrated here with assistant-ui
          </p>
        </div>

        {/* Input area */}
        <div className="p-4 border-t">
          <input
            type="text"
            placeholder={`Ask ${agentName} anything...`}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
    </div>
  );
}
