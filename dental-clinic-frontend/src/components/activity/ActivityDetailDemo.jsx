/**
 * Activity Detail View Demo Page
 * 
 * This demo page allows us to visually test the ActivityDetailView component
 * and ensure it renders correctly with all its features.
 */

import React, { useState } from 'react';
import ActivityDetailView from './ActivityDetailView';
import { Play, Eye, Settings } from 'lucide-react';

const ActivityDetailDemo = () => {
  const [showDetailView, setShowDetailView] = useState(false);
  const [selectedActivityId, setSelectedActivityId] = useState('demo-activity-1');

  // Mock activities for testing different scenarios
  const mockActivities = [
    {
      id: 'demo-activity-1',
      title: 'Schedule Patient Appointment',
      description: 'Standard appointment scheduling with AI assistance',
      status: 'COMPLETED',
      type: 'USER_REQUEST'
    },
    {
      id: 'demo-activity-2', 
      title: 'Process Insurance Claim',
      description: 'Complex insurance claim processing with multiple steps',
      status: 'IN_PROGRESS',
      type: 'SYSTEM_TASK'
    },
    {
      id: 'demo-activity-3',
      title: 'Patient Data Analysis',
      description: 'Analyzing patient history for treatment recommendations',
      status: 'FAILED',
      type: 'DATA_ANALYSIS'
    }
  ];

  const handleShowDetail = (activityId) => {
    setSelectedActivityId(activityId);
    setShowDetailView(true);
  };

  const handleCloseDetail = () => {
    setShowDetailView(false);
  };

  const handleHumanHandoff = (activity) => {
    console.log('Human handoff requested for activity:', activity);
    alert(`Human handoff requested for: ${activity.title}`);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
            <Eye className="h-8 w-8 mr-3 text-blue-600" />
            Activity Detail View Demo
          </h1>
          <p className="text-gray-600">
            Visual testing environment for the Activity Detail View component. 
            Click on any activity below to see the detailed view in action.
          </p>
        </div>

        {/* Demo Controls */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            Demo Activities
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {mockActivities.map((activity) => (
              <div
                key={activity.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleShowDetail(activity.id)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">{activity.title}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    activity.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                    activity.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {activity.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">{activity.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">{activity.type}</span>
                  <button className="flex items-center space-x-1 text-blue-600 hover:text-blue-700 text-sm">
                    <Play className="h-3 w-3" />
                    <span>View Details</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Component Features Being Tested</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Visual Elements</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Modal overlay and layout</li>
                <li>• Timeline step selection</li>
                <li>• Status badges and icons</li>
                <li>• Performance metrics display</li>
                <li>• Responsive design</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Interactive Features</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• AI explanation toggle</li>
                <li>• Step-by-step navigation</li>
                <li>• Human handoff button</li>
                <li>• Export functionality</li>
                <li>• Close/cancel actions</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-medium text-blue-900 mb-2">Testing Instructions</h3>
          <ol className="text-sm text-blue-800 space-y-1">
            <li>1. Click on any activity card above to open the detail view</li>
            <li>2. Test timeline navigation by clicking different steps</li>
            <li>3. Toggle the AI explanation to see detailed reasoning</li>
            <li>4. Check performance metrics and visual layout</li>
            <li>5. Test human handoff functionality (for in-progress activities)</li>
            <li>6. Verify responsive behavior by resizing the window</li>
          </ol>
        </div>
      </div>

      {/* Activity Detail View Modal */}
      {showDetailView && (
        <ActivityDetailView
          activityId={selectedActivityId}
          onClose={handleCloseDetail}
          onHumanHandoff={handleHumanHandoff}
        />
      )}
    </div>
  );
};

export default ActivityDetailDemo;
