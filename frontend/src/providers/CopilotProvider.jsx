import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

/**
 * CopilotProvider - Wraps the app with CopilotKit for LangGraph integration
 * 
 * This provider connects the frontend to our LangGraph multi-agent system:
 * - Supervisor routes requests to Alex, Marcus, or Sophia
 * - Agents can execute tools (Odoo operations)
 * - Real-time streaming of agent responses
 * - Human-in-the-loop approvals for critical actions
 */
export function CopilotProvider({ children }) {
  return (
    <CopilotKit
      runtimeUrl="/api/v1/copilot"
      agent="dental_supervisor"
      // Enable streaming for real-time agent responses
      showDevConsole={import.meta.env.DEV}
    >
      {children}
    </CopilotKit>
  );
}

/**
 * CopilotProviderWithSidebar - Optional sidebar chat interface
 * Use this if you want a persistent chat sidebar
 */
export function CopilotProviderWithSidebar({ children }) {
  return (
    <CopilotKit
      runtimeUrl="/api/v1/copilot"
      agent="dental_supervisor"
      showDevConsole={import.meta.env.DEV}
    >
      <CopilotSidebar
        defaultOpen={false}
        clickOutsideToClose={true}
        labels={{
          title: "Dental AI Assistant",
          initial: "How can I help you manage your clinic today?",
        }}
        instructions="You are an AI assistant helping a dentist manage their clinic. You have access to patient data, appointments, and financial information through Odoo. You can help with scheduling, patient inquiries, financial analysis, and operational optimization."
      >
        {children}
      </CopilotSidebar>
    </CopilotKit>
  );
}
