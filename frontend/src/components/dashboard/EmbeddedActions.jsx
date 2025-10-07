import React, { useState } from 'react';
import { Button } from '../ui/Button';
import { 
  MessageCircle, 
  Calendar, 
  DollarSign, 
  Phone,
  Mail,
  CheckCircle,
  Loader2,
  Sparkles
} from 'lucide-react';
import { cn } from '../../lib/utils';

/**
 * EmbeddedActions - Action buttons that trigger agent workflows
 * 
 * This implements the "Embedded" agentic UX pattern where AI actions
 * are seamlessly integrated into the workflow without separate agent interfaces.
 */

export const PatientActions = ({ patient, onAction }) => {
  const [loading, setLoading] = useState({});

  const handleAction = async (actionType, actionData) => {
    setLoading(prev => ({ ...prev, [actionType]: true }));
    
    try {
      await onAction(actionType, {
        patient,
        ...actionData,
      });
    } finally {
      setLoading(prev => ({ ...prev, [actionType]: false }));
    }
  };

  return (
    <div className="flex flex-wrap gap-2">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleAction('call', { agent: 'Alex' })}
        disabled={loading.call}
        className="text-purple-600 hover:bg-purple-50"
      >
        {loading.call ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Phone className="w-4 h-4" />
        )}
        Ask Alex to Call
      </Button>

      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleAction('schedule', { agent: 'Alex' })}
        disabled={loading.schedule}
        className="text-blue-600 hover:bg-blue-50"
      >
        {loading.schedule ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Calendar className="w-4 h-4" />
        )}
        Schedule Follow-up
      </Button>

      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleAction('payment_reminder', { agent: 'Marcus' })}
        disabled={loading.payment_reminder}
        className="text-pink-600 hover:bg-pink-50"
      >
        {loading.payment_reminder ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <DollarSign className="w-4 h-4" />
        )}
        Payment Reminder
      </Button>
    </div>
  );
};

export const AppointmentActions = ({ appointment, onAction }) => {
  const [loading, setLoading] = useState({});

  const handleAction = async (actionType, actionData) => {
    setLoading(prev => ({ ...prev, [actionType]: true }));
    
    try {
      await onAction(actionType, {
        appointment,
        ...actionData,
      });
    } finally {
      setLoading(prev => ({ ...prev, [actionType]: false }));
    }
  };

  return (
    <div className="flex flex-wrap gap-2">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleAction('confirm', { agent: 'Alex' })}
        disabled={loading.confirm}
        className="text-green-600 hover:bg-green-50"
      >
        {loading.confirm ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <CheckCircle className="w-4 h-4" />
        )}
        Auto-Confirm
      </Button>

      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleAction('reminder', { agent: 'Alex' })}
        disabled={loading.reminder}
        className="text-blue-600 hover:bg-blue-50"
      >
        {loading.reminder ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Mail className="w-4 h-4" />
        )}
        Send Reminder
      </Button>

      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleAction('reschedule', { agent: 'Sophia' })}
        disabled={loading.reschedule}
        className="text-cyan-600 hover:bg-cyan-50"
      >
        {loading.reschedule ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Calendar className="w-4 h-4" />
        )}
        Optimize Schedule
      </Button>
    </div>
  );
};

export const FinancialActions = ({ data, onAction }) => {
  const [loading, setLoading] = useState({});

  const handleAction = async (actionType, actionData) => {
    setLoading(prev => ({ ...prev, [actionType]: true }));
    
    try {
      await onAction(actionType, {
        data,
        ...actionData,
      });
    } finally {
      setLoading(prev => ({ ...prev, [actionType]: false }));
    }
  };

  return (
    <div className="flex flex-wrap gap-2">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleAction('analyze', { agent: 'Marcus' })}
        disabled={loading.analyze}
        className="text-pink-600 hover:bg-pink-50"
      >
        {loading.analyze ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Sparkles className="w-4 h-4" />
        )}
        Ask Marcus to Analyze
      </Button>

      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleAction('collect', { agent: 'Marcus' })}
        disabled={loading.collect}
        className="text-green-600 hover:bg-green-50"
      >
        {loading.collect ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <DollarSign className="w-4 h-4" />
        )}
        Auto-Collect Payments
      </Button>
    </div>
  );
};

/**
 * ActionToast - Shows feedback when agent actions are triggered
 */
export const ActionToast = ({ action, agent, onClose }) => {
  return (
    <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 max-w-sm animate-slide-up z-50">
      <div className="flex items-start gap-3">
        <div className={cn(
          'w-10 h-10 rounded-full flex items-center justify-center',
          agent === 'Alex' && 'bg-purple-100 text-purple-600',
          agent === 'Marcus' && 'bg-pink-100 text-pink-600',
          agent === 'Sophia' && 'bg-cyan-100 text-cyan-600'
        )}>
          <Sparkles className="w-5 h-5" />
        </div>
        
        <div className="flex-1">
          <p className="font-semibold text-gray-900">
            {agent} is working on it
          </p>
          <p className="text-sm text-gray-600 mt-1">
            {action.message}
          </p>
          {action.estimatedTime && (
            <p className="text-xs text-gray-500 mt-1">
              Est. time: {action.estimatedTime}
            </p>
          )}
        </div>
        
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600"
        >
          ×
        </button>
      </div>
    </div>
  );
};

export default {
  PatientActions,
  AppointmentActions,
  FinancialActions,
  ActionToast,
};
