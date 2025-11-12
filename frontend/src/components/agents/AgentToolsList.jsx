import React from 'react';
import PropTypes from 'prop-types';
import { Wrench, Calendar, Users, DollarSign, FileText, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';

/**
 * AgentToolsList Component
 * 
 * Displays available tools for a specific agent.
 * Groups tools by category for better organization.
 * 
 * @param {Object} props
 * @param {string} props.agentId - Agent ID
 * @param {string} props.agentColor - Agent theme color
 * @param {Function} props.onToolClick - Callback when tool is clicked
 */
const AgentToolsList = ({ agentId, agentColor, onToolClick }) => {
  // Tool definitions for each agent
  const agentTools = {
    alex: {
      title: 'Patient Coordination Tools',
      icon: <Users className="w-5 h-5" />,
      categories: [
        {
          name: 'Appointments',
          tools: [
            { id: 'show_todays_appointments', name: 'Show Today\'s Appointments', description: 'View all appointments scheduled for today' },
            { id: 'count_appointments', name: 'Count Appointments', description: 'Get appointment statistics' },
            { id: 'next_patient', name: 'Next Patient', description: 'Show next scheduled patient' },
            { id: 'schedule_appointment', name: 'Schedule Appointment', description: 'Book a new appointment' },
          ]
        },
        {
          name: 'Patients',
          tools: [
            { id: 'patient_history', name: 'Patient History', description: 'View patient medical history' },
            { id: 'search_patient', name: 'Search Patient', description: 'Find patient records' },
            { id: 'patient_contact', name: 'Patient Contact', description: 'Get patient contact information' },
          ]
        }
      ]
    },
    sarah: {
      title: 'Clinical Tools',
      icon: <FileText className="w-5 h-5" />,
      categories: [
        {
          name: 'Treatments',
          tools: [
            { id: 'treatment_history', name: 'Treatment History', description: 'View patient treatment records' },
            { id: 'root_canal_list', name: 'Root Canal List', description: 'List of root canal procedures' },
            { id: 'common_treatments', name: 'Common Treatments', description: 'Most frequently performed treatments' },
          ]
        },
        {
          name: 'Clinical Notes',
          tools: [
            { id: 'clinical_notes', name: 'Clinical Notes', description: 'Access clinical documentation' },
            { id: 'treatment_counts', name: 'Treatment Counts', description: 'Treatment statistics' },
          ]
        }
      ]
    },
    marcus: {
      title: 'Financial Tools',
      icon: <DollarSign className="w-5 h-5" />,
      categories: [
        {
          name: 'Revenue',
          tools: [
            { id: 'monthly_revenue', name: 'Monthly Revenue', description: 'View current month revenue' },
            { id: 'revenue_trends', name: 'Revenue Trends', description: 'Analyze revenue patterns' },
            { id: 'top_treatments', name: 'Top Treatments by Revenue', description: 'Highest earning treatments' },
          ]
        },
        {
          name: 'Invoices & Payments',
          tools: [
            { id: 'outstanding_invoices', name: 'Outstanding Invoices', description: 'View unpaid invoices' },
            { id: 'payment_success_rate', name: 'Payment Success Rate', description: 'Collection metrics' },
            { id: 'unpaid_patients', name: 'Unpaid Patients', description: 'Patients with outstanding balances' },
            { id: 'average_invoice', name: 'Average Invoice', description: 'Average invoice amount' },
          ]
        }
      ]
    },
    sophia: {
      title: 'Scheduling Tools',
      icon: <Calendar className="w-5 h-5" />,
      categories: [
        {
          name: 'Schedule Management',
          tools: [
            { id: 'weekly_appointments', name: 'Weekly Appointments', description: 'View week schedule' },
            { id: 'scheduling_conflicts', name: 'Scheduling Conflicts', description: 'Identify conflicts' },
            { id: 'utilization_rate', name: 'Utilization Rate', description: 'Schedule efficiency metrics' },
          ]
        },
        {
          name: 'Optimization',
          tools: [
            { id: 'cancelled_appointments', name: 'Cancelled Appointments', description: 'Track cancellations' },
            { id: 'schedule_optimization', name: 'Schedule Optimization', description: 'Optimize appointment slots' },
          ]
        }
      ]
    },
    harper: {
      title: 'Compliance Tools',
      icon: <Shield className="w-5 h-5" />,
      categories: [
        {
          name: 'HIPAA',
          tools: [
            { id: 'hipaa_compliance', name: 'HIPAA Compliance Status', description: 'View compliance metrics' },
            { id: 'security_alerts', name: 'Security Alerts', description: 'Active security notifications' },
            { id: 'access_logs', name: 'Access Logs', description: 'Audit trail' },
          ]
        },
        {
          name: 'Monitoring',
          tools: [
            { id: 'data_retention', name: 'Data Retention', description: 'Data lifecycle management' },
            { id: 'violation_checks', name: 'Violation Checks', description: 'Compliance violations' },
          ]
        }
      ]
    }
  };

  const tools = agentTools[agentId] || { title: 'Tools', icon: <Wrench />, categories: [] };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center gap-3 mb-6">
        <div
          className="p-2 rounded-lg"
          style={{ backgroundColor: `${agentColor}20` }}
        >
          <div style={{ color: agentColor }}>
            {tools.icon}
          </div>
        </div>
        <h2 className="text-xl font-bold text-gray-900">{tools.title}</h2>
      </div>

      <div className="space-y-6">
        {tools.categories.map((category, catIndex) => (
          <div key={catIndex}>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              {category.name}
            </h3>
            <div className="space-y-2">
              {category.tools.map((tool, toolIndex) => (
                <button
                  key={toolIndex}
                  onClick={() => onToolClick && onToolClick(tool)}
                  className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 group-hover:text-gray-700">
                        {tool.name}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {tool.description}
                      </div>
                    </div>
                    <div
                      className="text-xs font-medium px-2 py-1 rounded"
                      style={{
                        backgroundColor: `${agentColor}20`,
                        color: agentColor
                      }}
                    >
                      Run
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

AgentToolsList.propTypes = {
  agentId: PropTypes.string.isRequired,
  agentColor: PropTypes.string.isRequired,
  onToolClick: PropTypes.func,
};

export default AgentToolsList;
