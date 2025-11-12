import React, { useState } from 'react';
import AgentPageLayout from '@/components/agents/AgentPageLayout';
import AgentStatsGrid from '@/components/agents/AgentStatsGrid';
import AgentToolsList from '@/components/agents/AgentToolsList';
import AgentChat from '@/components/agents/AgentChat';
import AgentApprovals from '@/components/agents/AgentApprovals';
import AgentDataViz from '@/components/agents/AgentDataViz';

/**
 * HarperPage Component
 * 
 * Detail page for Harper - Compliance Monitor
 * Handles HIPAA compliance, security monitoring, and regulatory adherence.
 */
const HarperPage = () => {
  const agent = {
    id: 'harper',
    name: 'Harper',
    role: 'Compliance Monitor',
    color: '#8b5cf6', // Purple
    description: 'Ensures HIPAA compliance, security monitoring, and regulatory adherence'
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
          {agent.name} is your AI-powered Compliance Monitor, specializing in HIPAA compliance, 
          security monitoring, and regulatory adherence. {agent.name} continuously monitors 
          system access, tracks compliance metrics, identifies potential violations, and ensures 
          all clinic operations meet healthcare regulatory standards. With proactive alerting 
          and comprehensive audit trails, {agent.name} protects patient privacy and maintains 
          the highest standards of data security.
        </p>
        
        <div className="mt-4 pt-4 border-t">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Key Responsibilities:</h4>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600">
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              HIPAA compliance monitoring
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Security alert management
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Access log auditing
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Violation detection
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Data retention compliance
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: agent.color }}></div>
              Regulatory reporting
            </li>
          </ul>
        </div>
      </div>
    </AgentPageLayout>
  );
};

export default HarperPage;
