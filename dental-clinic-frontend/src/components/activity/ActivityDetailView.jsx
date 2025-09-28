/**
 * Component 2.3: Activity Detail View
 * 
 * This component provides a comprehensive, detailed view of individual agent activities.
 * It includes explainability features, performance metrics, decision reasoning,
 * and human handoff capabilities - core elements of the Agentic UX vision.
 * 
 * Features:
 * - Detailed activity information with timeline
 * - Decision explanation and reasoning (Explainability)
 * - Performance metrics and confidence scores
 * - Human handoff trigger capability
 * - Interactive timeline with step-by-step breakdown
 * - Modern, professional UI with smooth animations
 */

import React, { useState, useEffect } from 'react';
import { 
  Clock, User, Activity, Brain, TrendingUp, AlertTriangle, 
  CheckCircle, XCircle, Play, Pause, RotateCcw, ExternalLink,
  MessageSquare, Settings, Zap, Target, BarChart3
} from 'lucide-react';

const ActivityDetailView = ({ 
  activityId, 
  onClose, 
  onHumanHandoff,
  websocketUrl = 'ws://localhost:8001/ws' 
}) => {
  // --- State Management ---
  const [activity, setActivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedStep, setSelectedStep] = useState(0);
  const [showExplanation, setShowExplanation] = useState(false);
  const [handoffRequested, setHandoffRequested] = useState(false);

  // --- Mock Data (In real implementation, this would come from API/WebSocket) ---
  useEffect(() => {
    // Simulate loading activity details
    const mockActivity = {
      id: activityId || 'activity-123',
      agentId: 'dental_agent',
      type: 'USER_REQUEST',
      title: 'Schedule Patient Appointment',
      description: 'Processing appointment request for John Doe on March 15th',
      timestamp: new Date(),
      status: 'COMPLETED',
      confidence: 0.92,
      duration: 2.3, // seconds
      steps: [
        {
          id: 1,
          title: 'Request received',
          description: 'Initial request received from user',
          timestamp: new Date(Date.now() - 2300),
          status: 'COMPLETED',
          confidence: 0.95,
          reasoning: 'User provided clear date preference and patient information',
          metrics: { processingTime: 0.3, dataPoints: 5 }
        },
        {
          id: 2,
          title: 'Analyzing request',
          description: 'Analyzing user request for appointment scheduling',
          timestamp: new Date(Date.now() - 2000),
          status: 'COMPLETED',
          confidence: 0.98,
          reasoning: 'Found 3 available slots matching user preferences',
          metrics: { processingTime: 0.8, dataPoints: 12 }
        },
        {
          id: 3,
          title: 'Checking availability',
          description: 'Checking available time slots for March 15th',
          timestamp: new Date(Date.now() - 1500),
          status: 'COMPLETED',
          confidence: 0.87,
          reasoning: 'Minor conflict detected with lunch break, adjusted timing',
          metrics: { processingTime: 1.2, dataPoints: 8 }
        },
        {
          id: 4,
          title: 'Booking confirmed',
          description: 'Appointment booking has been confirmed',
          timestamp: new Date(Date.now() - 500),
          status: 'COMPLETED',
          confidence: 0.92,
          reasoning: 'Successfully booked appointment with confirmation',
          metrics: { processingTime: 0.5, dataPoints: 3 }
        }
      ],
      explanation: {
        decision: 'Why this action was taken',
        reasoning: 'This time slot provides optimal patient experience while maintaining clinic efficiency',
        factors: [
          'Patient availability preference',
          'Doctor schedule optimization',
          'Clinic resource allocation',
          'Historical appointment success rate'
        ],
        confidence_breakdown: {
          'Data Quality': 0.95,
          'Pattern Recognition': 0.91,
          'Context Understanding': 0.89,
          'Decision Logic': 0.93
        }
      },
      metrics: {
        response_time: 2.3,
        accuracy_score: 0.92,
        user_satisfaction: 0.89,
        efficiency_rating: 0.94
      }
    };

    // Set activity data immediately
    setActivity(mockActivity);
    setLoading(false);
  }, [activityId]);

  // --- Helper Functions ---
  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'COMPLETED': return 'text-green-600 bg-green-100';
      case 'IN_PROGRESS': return 'text-blue-600 bg-blue-100';
      case 'FAILED': return 'text-red-600 bg-red-100';
      case 'PENDING': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'COMPLETED': return <CheckCircle className="h-4 w-4" />;
      case 'IN_PROGRESS': return <Play className="h-4 w-4" />;
      case 'FAILED': return <XCircle className="h-4 w-4" />;
      case 'PENDING': return <Pause className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const handleHumanHandoff = () => {
    setHandoffRequested(true);
    if (onHumanHandoff) {
      onHumanHandoff(activity);
    }
  };

  // --- Loading State ---
  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto" role="status" aria-label="Loading"></div>
          <p className="text-center mt-4 text-gray-600">Loading activity details...</p>
        </div>
      </div>
    );
  }

  // --- Error State ---
  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <XCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-center mb-2">Error Loading Activity</h3>
          <p className="text-center text-gray-600 mb-4">{error}</p>
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  // --- Main Render ---
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" role="dialog" aria-modal="true" aria-labelledby="activity-detail-title">
      <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Activity className="h-8 w-8" />
              <div>
                <h2 id="activity-detail-title" className="text-2xl font-bold">{activity.title}</h2>
                <p className="text-blue-100">{activity.description}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${getStatusColor(activity.status)}`}>
                {getStatusIcon(activity.status)}
                <span className="font-medium">{activity.status}</span>
              </div>
              <button
                onClick={onClose}
                className="text-white hover:text-gray-300 transition-colors"
                aria-label="Close"
                type="button"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>
          </div>
        </div>

        <div className="flex h-[calc(90vh-120px)]">
          {/* Left Panel - Timeline */}
          <div className="w-1/3 border-r border-gray-200 p-6 overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Clock className="h-5 w-5 mr-2" />
              Activity Timeline
            </h3>
            
            <div className="space-y-4">
              {activity.steps.map((step, index) => (
                <div
                  key={step.id}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedStep === index 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedStep(index)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(step.status)}
                      <span className="font-medium">{step.title}</span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {formatTime(step.timestamp)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{step.description}</p>
                  <div className="flex items-center justify-between">
                    <span className={`text-sm font-medium ${getConfidenceColor(step.confidence)}`}>
                      {(step.confidence * 100).toFixed(1)}% confidence
                    </span>
                    <span className="text-xs text-gray-500">
                      {step.metrics.processingTime}s
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Panel - Details */}
          <div className="flex-1 p-6 overflow-y-auto">
            <div className="space-y-6">
              {/* Step Details */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <Target className="h-5 w-5 mr-2" />
                  {activity.steps[selectedStep].title}
                </h3>
                
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium mb-2">Processing Details</h4>
                    <p className="text-gray-600 mb-4">{activity.steps[selectedStep].description}</p>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Processing Time:</span>
                        <span className="font-medium">{activity.steps[selectedStep].metrics.processingTime}s</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Data Points:</span>
                        <span className="font-medium">{activity.steps[selectedStep].metrics.dataPoints}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Confidence:</span>
                        <span className={`font-medium ${getConfidenceColor(activity.steps[selectedStep].confidence)}`}>
                          {(activity.steps[selectedStep].confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium mb-2">Decision Reasoning</h4>
                    <div className="bg-white rounded-lg p-4 border border-gray-200">
                      <p className="text-gray-700">{activity.steps[selectedStep].reasoning}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* AI Explanation */}
              <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold flex items-center">
                    <Brain className="h-5 w-5 mr-2" />
                    AI Decision Explanation
                  </h3>
                  <button
                    onClick={() => setShowExplanation(!showExplanation)}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    {showExplanation ? 'Hide' : 'Show'} Details
                  </button>
                </div>
                
                <div className="bg-white rounded-lg p-4 mb-4">
                  <h4 className="font-medium mb-2">Final Decision</h4>
                  <p className="text-gray-700">{activity.explanation.decision}</p>
                </div>
                
                {showExplanation && (
                  <div className="space-y-4 animate-fade-in">
                    <div className="bg-white rounded-lg p-4">
                      <h4 className="font-medium mb-2">Reasoning</h4>
                      <p className="text-gray-700">{activity.explanation.reasoning}</p>
                    </div>
                    
                    <div className="bg-white rounded-lg p-4">
                      <h4 className="font-medium mb-3">Decision Factors</h4>
                      <div className="grid grid-cols-2 gap-2">
                        {activity.explanation.factors.map((factor, index) => (
                          <div key={index} className="flex items-center space-x-2">
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            <span className="text-sm">{factor}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div className="bg-white rounded-lg p-4">
                      <h4 className="font-medium mb-3">Confidence Breakdown</h4>
                      <div className="space-y-2">
                        {Object.entries(activity.explanation.confidence_breakdown).map(([key, value]) => (
                          <div key={key} className="flex items-center justify-between">
                            <span className="text-sm">{key}:</span>
                            <div className="flex items-center space-x-2">
                              <div className="w-24 bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-blue-600 h-2 rounded-full" 
                                  style={{ width: `${value * 100}%` }}
                                ></div>
                              </div>
                              <span className="text-sm font-medium">{(value * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Performance Metrics */}
              <div className="bg-green-50 rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2" />
                  Performance Metrics
                </h3>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white rounded-lg p-4 text-center">
                    <Zap className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900">{activity.metrics.response_time}s</div>
                    <div className="text-sm text-gray-600">Response Time</div>
                  </div>
                  
                  <div className="bg-white rounded-lg p-4 text-center">
                    <Target className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900">{(activity.metrics.accuracy_score * 100).toFixed(1)}%</div>
                    <div className="text-sm text-gray-600">Accuracy</div>
                  </div>
                  
                  <div className="bg-white rounded-lg p-4 text-center">
                    <User className="h-8 w-8 text-green-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900">{(activity.metrics.user_satisfaction * 100).toFixed(1)}%</div>
                    <div className="text-sm text-gray-600">User Satisfaction</div>
                  </div>
                  
                  <div className="bg-white rounded-lg p-4 text-center">
                    <TrendingUp className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900">{(activity.metrics.efficiency_rating * 100).toFixed(1)}%</div>
                    <div className="text-sm text-gray-600">Efficiency</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="border-t border-gray-200 p-6 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Activity ID: {activity.id}
              </span>
              <span className="text-sm text-gray-600">
                Agent: {activity.agentId}
              </span>
              <span className="text-sm text-gray-600">
                Duration: {activity.duration}s
              </span>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => window.open(`/activity/${activity.id}/export`, '_blank')}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2"
              >
                <ExternalLink className="h-4 w-4" />
                <span>Export Details</span>
              </button>
              
              {!handoffRequested && (activity.status === 'IN_PROGRESS' || activity.status === 'ACTIVE') && (
                <button
                  onClick={handleHumanHandoff}
                  className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center space-x-2"
                >
                  <AlertTriangle className="h-4 w-4" />
                  <span>Request Human Handoff</span>
                </button>
              )}
              
              {handoffRequested && (
                <div className="px-4 py-2 bg-yellow-100 text-yellow-800 rounded-lg flex items-center space-x-2">
                  <MessageSquare className="h-4 w-4" />
                  <span>Human handoff requested</span>
                </div>
              )}
              
              <button
                onClick={onClose}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActivityDetailView;
