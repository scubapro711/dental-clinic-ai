import React, { useState, useEffect } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { 
  Sparkles, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle,
  X,
  ChevronRight,
  Loader2
} from 'lucide-react';
import { cn } from '../../lib/utils';
import API_CONFIG from '@/config/api';

/**
 * ProactiveSuggestionsPanel - AI agents proactively suggest actions
 * 
 * This implements the "Asynchronous" agentic UX pattern where agents
 * work in the background and present actionable insights.
 */

export const ProactiveSuggestionsPanel = () => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dismissedIds, setDismissedIds] = useState(new Set());

  useEffect(() => {
    fetchSuggestions();
    
    // Refresh suggestions every 5 minutes
    const interval = setInterval(fetchSuggestions, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchSuggestions = async () => {
    try {
      const response = await fetch(API_CONFIG.endpoint('suggestions'));
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      }
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      // Use mock data for demo
      setSuggestions(getMockSuggestions());
    } finally {
      setLoading(false);
    }
  };

  const getMockSuggestions = () => [
    {
      id: 'sug-1',
      agent: 'Alex',
      priority: 'high',
      category: 'patient_care',
      title: 'Follow-up Calls Needed',
      description: '3 patients need post-treatment follow-up calls today',
      action: 'Call patients: Sarah Johnson, David Cohen, Rachel Levi',
      impact: 'Improve patient satisfaction and catch complications early',
      estimatedTime: '15 minutes',
      data: {
        patients: ['Sarah Johnson', 'David Cohen', 'Rachel Levi'],
      },
    },
    {
      id: 'sug-2',
      agent: 'Marcus',
      priority: 'high',
      category: 'financial',
      title: 'Uncollected Payments Found',
      description: '$5,240 in outstanding payments over 30 days',
      action: 'Send automated payment reminders to 6 patients',
      impact: 'Recover $5,240 in revenue',
      estimatedTime: '2 minutes (automated)',
      data: {
        amount: 5240,
        patientCount: 6,
      },
    },
    {
      id: 'sug-3',
      agent: 'Sophia',
      priority: 'medium',
      category: 'scheduling',
      title: 'Schedule Optimization Available',
      description: 'Rearrange 4 appointments to reduce gaps',
      action: 'Optimize today\'s schedule to save 2 hours',
      impact: 'Free up 2 hours for emergency appointments or personal time',
      estimatedTime: '30 seconds (automated)',
      data: {
        timeSaved: '2 hours',
        appointmentsAffected: 4,
      },
    },
    {
      id: 'sug-4',
      agent: 'Alex',
      priority: 'medium',
      category: 'patient_care',
      title: 'Appointment Confirmations',
      description: '8 appointments tomorrow need confirmation',
      action: 'Send automated confirmation requests',
      impact: 'Reduce no-shows by 40%',
      estimatedTime: '1 minute (automated)',
      data: {
        appointmentCount: 8,
      },
    },
    {
      id: 'sug-5',
      agent: 'Marcus',
      priority: 'low',
      category: 'insights',
      title: 'Revenue Trend Analysis',
      description: 'Weekly revenue is 12% above target',
      action: 'View detailed financial analysis',
      impact: 'Understand what\'s driving growth',
      estimatedTime: '5 minutes',
      data: {
        trend: '+12%',
      },
    },
  ];

  const handleExecute = async (suggestion) => {
    // TODO: Call backend API to execute suggestion
    console.log('Executing suggestion:', suggestion);
    
    // Simulate execution
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Remove from list
    setDismissedIds(prev => new Set([...prev, suggestion.id]));
  };

  const handleDismiss = (suggestionId) => {
    setDismissedIds(prev => new Set([...prev, suggestionId]));
  };

  const visibleSuggestions = (suggestions || []).filter(s => !dismissedIds.has(s.id));

  const priorityConfig = {
    high: {
      color: 'text-red-600',
      bg: 'bg-red-50',
      border: 'border-red-200',
      badge: 'destructive',
      icon: AlertTriangle,
    },
    medium: {
      color: 'text-orange-600',
      bg: 'bg-orange-50',
      border: 'border-orange-200',
      badge: 'warning',
      icon: TrendingUp,
    },
    low: {
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      badge: 'default',
      icon: Sparkles,
    },
  };

  const agentColor = {
    'Alex': 'text-purple-600',
    'Marcus': 'text-pink-600',
    'Sophia': 'text-cyan-600',
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center">
          <Loader2 className="w-6 h-6 text-gray-400 animate-spin" />
        </div>
      </Card>
    );
  }

  if (visibleSuggestions.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
          <p className="text-gray-600 font-medium">All caught up!</p>
          <p className="text-sm text-gray-500 mt-1">
            Your agents will notify you when they find new opportunities
          </p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900">Smart Suggestions</h3>
        </div>
        <Badge variant="default" size="sm">
          {visibleSuggestions.length} new
        </Badge>
      </div>

      {visibleSuggestions.map((suggestion) => {
        const config = priorityConfig[suggestion.priority];
        const Icon = config.icon;

        return (
          <Card 
            key={suggestion.id}
            className={cn(
              'relative overflow-hidden border-l-4',
              config.border,
              'hover:shadow-md transition-shadow'
            )}
          >
            <button
              onClick={() => handleDismiss(suggestion.id)}
              className="absolute top-2 right-2 p-1 text-gray-400 hover:text-gray-600 rounded"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="flex items-start gap-3">
              <div className={cn(
                'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0',
                config.bg
              )}>
                <Icon className={cn('w-5 h-5', config.color)} />
              </div>

              <div className="flex-1 min-w-0 pr-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className={cn('text-xs font-semibold', agentColor[suggestion.agent])}>
                    {suggestion.agent}
                  </span>
                  <Badge variant={config.badge} size="sm">
                    {suggestion.priority}
                  </Badge>
                </div>

                <h4 className="font-semibold text-gray-900 mb-1">
                  {suggestion.title}
                </h4>

                <p className="text-sm text-gray-600 mb-2">
                  {suggestion.description}
                </p>

                <div className={cn('text-sm p-2 rounded-lg mb-3', config.bg)}>
                  <p className="font-medium text-gray-900">
                    💡 {suggestion.action}
                  </p>
                </div>

                <div className="flex items-center justify-between">
                  <div className="text-xs text-gray-500">
                    <span className="font-medium">Impact:</span> {suggestion.impact}
                  </div>
                  <div className="text-xs text-gray-500">
                    ⏱️ {suggestion.estimatedTime}
                  </div>
                </div>

                <div className="flex gap-2 mt-3">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleExecute(suggestion)}
                    className="flex-1"
                  >
                    Execute
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDismiss(suggestion.id)}
                  >
                    Later
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
};

export default ProactiveSuggestionsPanel;
