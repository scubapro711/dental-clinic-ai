"""
Harper - HIPAA Compliance Agent

Harper is DentaFlow's specialized HIPAA compliance agent that provides:
- Real-time HIPAA compliance guidance
- RAG-powered knowledge base search
- Compliance assessments and audits
- Breach notification support
- Risk analysis and remediation recommendations

Harper serves both Clinic Admins and Super Admins with role-based access control.

Key Features:
- 10 specialized HIPAA compliance tools
- RAG integration with Pinecone vector database
- Proactive monitoring and alerts
- Comprehensive compliance reporting
- Real-time regulatory updates

Model: gpt-4.1-mini (optimized for compliance accuracy)
"""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.agents.graph_state import AgentState
from app.tools.hipaa_tools import (
    search_hipaa_knowledge,
    check_phi_compliance,
    validate_baa,
    assess_security_controls,
    generate_breach_report,
    audit_access_logs,
    check_patient_rights,
    evaluate_risk,
    generate_compliance_report,
    recommend_remediation
)

logger = logging.getLogger(__name__)


class HarperAgent:
    """
    Harper - HIPAA Compliance Agent
    
    Provides comprehensive HIPAA compliance support for dental clinics.
    Uses RAG (Retrieval-Augmented Generation) with Pinecone vector database
    and 10 specialized compliance tools.
    """
    
    def __init__(self, demo_mode: bool = False):
        """
        Initialize Harper agent.
        
        Args:
            demo_mode: If True, agent operates in Interactive Demo mode
        """
        self.demo_mode = demo_mode
        self.name = "Harper"
        self.role = "HIPAA Compliance Specialist"
        
        # Initialize LLM with gpt-4.1-mini
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            temperature=0.2,  # Low temperature for compliance accuracy
        )
        
        # Bind tools to LLM
        self.tools = [
            search_hipaa_knowledge,
            check_phi_compliance,
            validate_baa,
            assess_security_controls,
            generate_breach_report,
            audit_access_logs,
            check_patient_rights,
            evaluate_risk,
            generate_compliance_report,
            recommend_remediation
        ]
        
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # System prompt
        self.system_prompt = self._build_system_prompt()
        
        logger.info(f"Harper agent initialized in {'DEMO' if demo_mode else 'PRODUCTION'} mode")
    
    def _build_system_prompt(self) -> str:
        """Build Harper's system prompt."""
        return """You are Harper, the HIPAA Compliance Specialist for DentaFlow.

**Your Role:**
You are a highly knowledgeable HIPAA compliance expert who helps dental clinics maintain compliance with HIPAA regulations. You provide accurate, actionable guidance based on official HIPAA regulations, industry best practices, and dental-specific compliance requirements.

**Your Expertise:**
- HIPAA Privacy Rule (45 CFR Part 160 and Part 164, Subparts A and E)
- HIPAA Security Rule (45 CFR Part 164, Subparts A and C)
- HIPAA Breach Notification Rule (45 CFR Part 164, Subpart D)
- HIPAA Enforcement Rule (45 CFR Part 160, Subparts C, D, and E)
- Business Associate Agreements (BAAs)
- Patient Rights (Access, Amendment, Accounting, Restrictions)
- Risk Analysis and Management
- Dental-specific compliance considerations

**Your Tools:**
You have access to 10 specialized compliance tools:

1. **search_hipaa_knowledge** - Search the comprehensive HIPAA knowledge base
   - Use this FIRST for any compliance question
   - Provides authoritative answers from regulations, policies, FAQs, and best practices

2. **check_phi_compliance** - Validate PHI handling compliance
   - Assess encryption, access controls, storage security
   - Returns compliance score and specific findings

3. **validate_baa** - Validate Business Associate Agreements
   - Check BAA status, dates, and required provisions
   - Identify BAAs that need renewal

4. **assess_security_controls** - Assess security safeguards
   - Evaluate technical, administrative, and physical controls
   - Perform gap analysis against HIPAA requirements

5. **generate_breach_report** - Generate breach notification reports
   - Calculate notification timelines and requirements
   - Identify HHS and media notification obligations

6. **audit_access_logs** - Audit PHI access logs
   - Identify suspicious activity and unauthorized access
   - Ensure compliance with audit requirements

7. **check_patient_rights** - Check patient rights compliance
   - Validate handling of access, amendment, and accounting requests
   - Calculate response deadlines

8. **evaluate_risk** - Perform HIPAA risk assessments
   - Assess risks to ePHI confidentiality, integrity, and availability
   - Provide mitigation recommendations

9. **generate_compliance_report** - Generate comprehensive compliance reports
   - Create quarterly, annual, or audit reports
   - Include metrics, findings, and recommendations

10. **recommend_remediation** - Provide remediation recommendations
    - Generate specific action plans for compliance findings
    - Include timelines and resource requirements

**How to Use Tools:**
1. **ALWAYS search the knowledge base first** for compliance questions
2. Use specific tools for assessments, validations, and reports
3. Combine multiple tools when needed for comprehensive analysis
4. Cite specific HIPAA regulations in your responses

**Your Communication Style:**
- **Professional and authoritative** - You're a compliance expert
- **Clear and actionable** - Provide specific steps, not vague advice
- **Cite regulations** - Reference specific HIPAA rules (e.g., "§ 164.312(a)(2)(iv)")
- **Risk-aware** - Clearly communicate severity and urgency
- **Supportive** - Help clinics achieve compliance, don't just point out problems

**Important Guidelines:**
1. **Accuracy is critical** - HIPAA violations can result in significant penalties
2. **Search knowledge base first** - Don't rely solely on training data
3. **Be specific** - Provide exact regulation references and actionable steps
4. **Consider dental context** - Tailor advice to dental practice operations
5. **Escalate when needed** - Recommend legal counsel for complex situations

**Response Format:**
When answering compliance questions:
1. **Search knowledge base** using search_hipaa_knowledge
2. **Provide clear answer** based on search results
3. **Cite specific regulations** (e.g., "HIPAA Privacy Rule § 164.524")
4. **Give actionable steps** - What should they do?
5. **Assess risk/urgency** - Is this critical, high, medium, or low priority?

**Example Response Structure:**
```
Based on HIPAA regulations:

[Clear answer to the question]

**Regulation Reference:** [Specific HIPAA rule citation]

**Required Actions:**
1. [Specific action step]
2. [Specific action step]
3. [Specific action step]

**Timeline:** [When this needs to be completed]
**Risk Level:** [Critical/High/Medium/Low]

[Additional context or recommendations]
```

**Current Date:** {current_date}

Remember: You're here to help dental clinics maintain HIPAA compliance and protect patient privacy. Be thorough, accurate, and supportive!
"""
    
    def process(self, state: AgentState) -> AgentState:
        """
        Process a request for Harper.
        
        This is the main entry point called by the agent graph.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Harper's response
        """
        try:
            logger.info("Harper processing request...")
            
            # Get user role for RBAC
            user_role = state.get("user_role", "patient")
            
            # Check if user has permission to access Harper
            # Harper is only available to clinic_admin and super_admin
            if user_role not in ["clinic_admin", "super_admin"]:
                logger.warning(f"User with role '{user_role}' attempted to access Harper - DENIED")
                
                denial_message = """I'm Harper, the HIPAA Compliance Specialist. I'm only available to Clinic Administrators and Super Administrators.

If you have questions about HIPAA compliance, please contact your clinic administrator."""
                
                state["messages"].append(AIMessage(content=denial_message))
                state["current_agent"] = "harper"
                return state
            
            # Get messages
            messages = state.get("messages", [])
            if not messages:
                logger.error("No messages in state")
                return state
            
            # Build prompt with system message
            system_message = SystemMessage(
                content=self.system_prompt.format(
                    current_date=datetime.now().strftime("%Y-%m-%d")
                )
            )
            
            # Prepare messages for LLM
            llm_messages = [system_message] + messages
            
            # Invoke LLM with tools
            response = self.llm_with_tools.invoke(llm_messages)
            
            # Check if LLM wants to use tools
            if response.tool_calls:
                logger.info(f"Harper calling {len(response.tool_calls)} tool(s)")
                
                # Execute tool calls
                tool_results = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    
                    logger.info(f"Executing tool: {tool_name}")
                    
                    # Find and execute the tool
                    tool_func = next((t for t in self.tools if t.name == tool_name), None)
                    if tool_func:
                        try:
                            result = tool_func.invoke(tool_args)
                            tool_results.append({
                                "tool": tool_name,
                                "result": result
                            })
                        except Exception as e:
                            logger.error(f"Error executing tool {tool_name}: {e}")
                            tool_results.append({
                                "tool": tool_name,
                                "error": str(e)
                            })
                    else:
                        logger.error(f"Tool not found: {tool_name}")
                
                # Generate final response with tool results
                tool_results_text = "\n\n".join([
                    f"**Tool: {tr['tool']}**\n```json\n{tr.get('result', tr.get('error'))}\n```"
                    for tr in tool_results
                ])
                
                final_prompt = f"""Based on the tool results below, provide a comprehensive answer to the user's question.

Tool Results:
{tool_results_text}

Provide a clear, professional response that:
1. Answers the user's question directly
2. Cites specific HIPAA regulations
3. Provides actionable steps
4. Indicates risk level and timeline if applicable

Remember to be professional, accurate, and supportive."""
                
                final_response = self.llm.invoke(
                    llm_messages + [
                        AIMessage(content=tool_results_text),
                        HumanMessage(content=final_prompt)
                    ]
                )
                
                response_content = final_response.content
            else:
                # No tool calls, use direct response
                response_content = response.content
            
            # Add Harper's response to messages
            state["messages"].append(AIMessage(content=response_content))
            state["current_agent"] = "harper"
            
            # Add suggested actions for compliance tasks
            state["suggested_actions"] = self._generate_suggested_actions(response_content, user_role)
            
            logger.info("Harper response generated successfully")
            
            return state
            
        except Exception as e:
            logger.error(f"Error in Harper agent: {e}", exc_info=True)
            
            error_message = f"""I apologize, but I encountered an error while processing your request: {str(e)}

Please try again or contact support if the issue persists."""
            
            state["messages"].append(AIMessage(content=error_message))
            state["current_agent"] = "harper"
            
            return state
    
    def _generate_suggested_actions(self, response_content: str, user_role: str) -> List[Dict[str, Any]]:
        """
        Generate suggested actions based on response content.
        
        Args:
            response_content: Harper's response
            user_role: User's role
            
        Returns:
            List of suggested actions
        """
        suggested_actions = []
        
        # Common compliance actions
        if "breach" in response_content.lower():
            suggested_actions.append({
                "label": "Generate Breach Report",
                "action": "generate_breach_report",
                "icon": "alert-triangle"
            })
        
        if "baa" in response_content.lower() or "business associate" in response_content.lower():
            suggested_actions.append({
                "label": "Review BAAs",
                "action": "review_baas",
                "icon": "file-text"
            })
        
        if "risk" in response_content.lower() or "assessment" in response_content.lower():
            suggested_actions.append({
                "label": "Perform Risk Assessment",
                "action": "risk_assessment",
                "icon": "shield"
            })
        
        if "audit" in response_content.lower():
            suggested_actions.append({
                "label": "Audit Access Logs",
                "action": "audit_logs",
                "icon": "search"
            })
        
        # Always offer to search knowledge base
        suggested_actions.append({
            "label": "Search HIPAA Knowledge Base",
            "action": "search_knowledge",
            "icon": "book-open"
        })
        
        # Super admin only: Generate compliance report
        if user_role == "super_admin":
            suggested_actions.append({
                "label": "Generate Compliance Report",
                "action": "generate_report",
                "icon": "file-chart"
            })
        
        return suggested_actions[:4]  # Limit to 4 actions


# Create singleton instance
harper_agent = HarperAgent()


def harper_node(state: AgentState) -> AgentState:
    """
    Harper node for LangGraph integration.
    
    This function is called by the agent graph when routing to Harper.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with Harper's response
    """
    return harper_agent.process(state)

