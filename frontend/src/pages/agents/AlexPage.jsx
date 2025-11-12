import React, { useState } from 'react';
import AgentPageLayout from '@/components/agents/AgentPageLayout';
import AgentStatsGrid from '@/components/agents/AgentStatsGrid';
import AgentToolsList from '@/components/agents/AgentToolsList';
import AgentChat from '@/components/agents/AgentChat';
import AgentApprovals from '@/components/agents/AgentApprovals';
import AgentDataViz from '@/components/agents/AgentDataViz';

/**
 * AlexPage Component
 * 
 * Detail page for Alex - Front Desk Coordinator
 * Handles patient coordination, appointments, and front desk operations.
 */
const AlexPage = () => {
  const agent = {
    id: 'alex',
    name: 'Alex',
    role: 'Front Desk Coordinator',
    color: '#3b82f6', // Blue
    description: 'Manages patient appointments, check-ins, and front desk operations'
  };

  const [selectedTool, setSelectedTool] = useState(null);

  const handleToolClick = (tool) => {
    setSelectedTool(tool);
    console.log('Tool clicked:', tool);
    // In production, this would trigger the tool execution
  };

  return (
    <AgentPageLayout agent={agent}>
      {/* Stats Grid */}
      <AgentStatsGrid agentId={agent.id} agentColor={agent.color} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Left Column - Tools & Data Viz */}
        <div className="lg:col-span-1 space-y-6">
          <AgentToolsList
            agentId={agent.id}
            agentColor={agent.color}
            onToolClick={handleToolClick}
          />
          <AgentDataViz agentId={agent.id} agentColor={agent.color} />
        </div>

        {/* Right Column - Chat & Approvals */}
        <div className="lg:col-span-2 space-y-6">
          <AgentChat
            agentId={agent.id}
            agentName={agent.name}
            agentColor={agent.color}
          />
          <AgentApprovals agentId={agent.id} agentColor={agent.color} />
        </div>
      </div>

      {/* Agent Description Card */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-3">About {agent.name}</h3>
        <p className="text-gray-600 leading-relaxed">
          {agent.name} is your AI-powered Front Desk Coordinator, specializing in patient 
          coordination and appointment management. {agent.name} handles check-ins, schedules 
          appointments, manages patient records, and ensures smooth front desk operations. 
          With access to real-time patient data and scheduling tools, {agent.name} can 
          quickly respond to patient inquiries, coordinate with other agents, and maintain 
          an organized front desk workflow.
        </p>
        
        <div className="mt-4 pt-4 border-t">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Key Responsibilities:</h4>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600">
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Patient check-in and registration
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Appointment scheduling and management
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Patient record retrieval
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Front desk coordination
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Patient communication
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Daily schedule management
            </li>
          </ul>
        </div>
      </div>
    </AgentPageLayout>
  );
};

export default AlexPage;
