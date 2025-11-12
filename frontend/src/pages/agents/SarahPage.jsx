import React, { useState } from 'react';
import AgentPageLayout from '@/components/agents/AgentPageLayout';
import AgentStatsGrid from '@/components/agents/AgentStatsGrid';
import AgentToolsList from '@/components/agents/AgentToolsList';
import AgentChat from '@/components/agents/AgentChat';
import AgentApprovals from '@/components/agents/AgentApprovals';
import AgentDataViz from '@/components/agents/AgentDataViz';

/**
 * SarahPage Component
 * 
 * Detail page for Sarah - Clinical Assistant
 * Handles treatment planning, clinical documentation, and patient care coordination.
 */
const SarahPage = () => {
  const agent = {
    id: 'sarah',
    name: 'Sarah',
    role: 'Clinical Assistant',
    color: '#ec4899', // Pink
    description: 'Manages treatment planning, clinical notes, and patient care coordination'
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
          {agent.name} is your AI-powered Clinical Assistant, specializing in treatment 
          planning and clinical documentation. {agent.name} assists with patient treatment 
          histories, clinical notes, procedure tracking, and care coordination. With deep 
          integration into clinical workflows and access to comprehensive treatment data, 
          {agent.name} ensures accurate documentation and supports clinical decision-making 
          for optimal patient care.
        </p>
        
        <div className="mt-4 pt-4 border-t">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Key Responsibilities:</h4>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600">
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Treatment planning and documentation
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Clinical notes management
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Patient treatment history tracking
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Procedure coordination
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Clinical data analysis
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Care quality monitoring
            </li>
          </ul>
        </div>
      </div>
    </AgentPageLayout>
  );
};

export default SarahPage;
