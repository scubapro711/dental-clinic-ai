import React, { useState } from 'react';
import AgentPageLayout from '@/components/agents/AgentPageLayout';
import AgentStatsGrid from '@/components/agents/AgentStatsGrid';
import AgentToolsList from '@/components/agents/AgentToolsList';
import AgentChat from '@/components/agents/AgentChat';
import AgentApprovals from '@/components/agents/AgentApprovals';
import AgentDataViz from '@/components/agents/AgentDataViz';

/**
 * SophiaPage Component
 * 
 * Detail page for Sophia - Scheduling Optimizer
 * Handles appointment optimization, schedule management, and resource allocation.
 */
const SophiaPage = () => {
  const agent = {
    id: 'sophia',
    name: 'Sophia',
    role: 'Scheduling Optimizer',
    color: '#f97316', // Orange
    description: 'Optimizes scheduling, manages appointments, and maximizes clinic efficiency'
  };

  const [selectedTool, setSelectedTool] = useState(null);

  const handleToolClick = (tool) => {
    setSelectedTool(tool);
    console.log('Tool clicked:', tool);
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
          {agent.name} is your AI-powered Scheduling Optimizer, specializing in appointment 
          management and resource allocation. {agent.name} analyzes scheduling patterns, 
          identifies conflicts, optimizes appointment slots, and maximizes clinic utilization. 
          With intelligent algorithms and real-time schedule monitoring, {agent.name} ensures 
          efficient use of clinic resources, minimizes gaps, and maintains optimal patient flow 
          throughout the day.
        </p>
        
        <div className="mt-4 pt-4 border-t">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Key Responsibilities:</h4>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600">
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Schedule optimization
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Conflict detection and resolution
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Utilization rate monitoring
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Cancellation tracking
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Resource allocation
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Efficiency analytics
            </li>
          </ul>
        </div>
      </div>
    </AgentPageLayout>
  );
};

export default SophiaPage;
