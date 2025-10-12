"""
Agent Graph V4 - Multi-Agent System with 4 Agents

Supervisor architecture with specialized agents:
- Supervisor: Routes requests to specialized agents
- Alex: Patient-facing interactions (Reception & Patient Relations)
- שרה (Sarah): Clinical operations and patient care
- Marcus (CFO): Financial analysis and insights
- Sophia (Admin): Operations and scheduling management

Key Features:
- Tool-calling LLM for routing
- Forward messages (no paraphrasing!)
- Clean context for sub-agents
- Intelligent delegation
- Full clinical capabilities via שרה

Reference: AGENT_ARCHITECTURE_ANALYSIS.md, MASTER_PLAN_FINAL_V2.md
"""

import logging
import json
import os
from typing import Dict, Any, List, Literal
from langgraph.graph import StateGraph, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI

from app.agents.graph_state import AgentState
from app.agents.alex_v2 import AlexAgent
from app.agents.sarah_clinical import sarah_agent
from app.agents.cfo import CFOAgent
from app.agents.practice_admin import PracticeAdminAgent
from app.core.memory import get_memory_saver


logger = logging.getLogger(__name__)


def remove_handoff_messages(messages: List[BaseMessage]) -> List[BaseMessage]:
    """
    Remove supervisor's routing logic from sub-agent context.
    
    This is CRITICAL for performance (50% improvement!).
    Sub-agents should only see user messages and relevant agent responses,
    not the supervisor's internal routing decisions.
    
    Args:
        messages: List of messages
        
    Returns:
        Cleaned list of messages
    """
    clean_messages = []
    
    routing_keywords = [
        "delegating to",
        "transferring to",
        "routing to",
        "calling",
        "forwarding to",
        "i will delegate",
        "i will transfer",
        "i will route",
        "let me call",
        "let me forward",
    ]
    
    for msg in messages:
        content = msg.content.lower() if hasattr(msg, 'content') else str(msg).lower()
        
        # Skip routing messages
        if any(keyword in content for keyword in routing_keywords):
            continue
        
        # Keep user and agent messages
        clean_messages.append(msg)
    
    return clean_messages


class AgentGraphV4:
    """
    Multi-Agent LangGraph with Supervisor architecture - 4 Agents.
    
    Architecture:
    - Supervisor node (routes to agents)
    - Alex node (patient interactions & reception)
    - שרה node (clinical operations)
    - Marcus node (CFO - financial analysis)
    - Sophia node (Admin - operations management)
    
    The supervisor uses tool-calling to delegate to specialized agents,
    and forwards their responses directly without paraphrasing.
    """
    
    def __init__(self, memory=None):
        """
        Initialize agent graph with supervisor and 4 agents.
        
        Args:
            memory: Optional memory checkpointer (for testing). Defaults to PostgresSaver.
        """
        # Initialize agents
        self.alex = AlexAgent()
        self.sarah = sarah_agent  # Clinical assistant
        self.marcus = CFOAgent()
        self.sophia = PracticeAdminAgent()
        
        # Initialize supervisor LLM
        self.supervisor_llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            temperature=0.1,  # Low temperature for consistent routing
        )
        
        # LangGraph Memory with PostgreSQL (Best Practice!)
        # Uses same DB as application for parity and persistence
        self.memory = memory if memory is not None else get_memory_saver()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build LangGraph workflow with supervisor + 4 agents.
        
        Returns:
            Compiled StateGraph
        """
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("alex", self._alex_node)
        workflow.add_node("sarah", self._sarah_node)
        workflow.add_node("marcus", self._marcus_node)
        workflow.add_node("sophia", self._sophia_node)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Supervisor routes to agents or END
        workflow.add_conditional_edges(
            "supervisor",
            self._route_supervisor,
            {
                "alex": "alex",
                "sarah": "sarah",
                "marcus": "marcus",
                "sophia": "sophia",
                "end": END,
            }
        )
        
        # Agents return to supervisor for potential follow-up
        workflow.add_edge("alex", "supervisor")
        workflow.add_edge("sarah", "supervisor")
        workflow.add_edge("marcus", "supervisor")
        workflow.add_edge("sophia", "supervisor")
        
        # Compile graph with memory checkpointer
        return workflow.compile(checkpointer=self.memory)
    
    def _supervisor_node(self, state: AgentState) -> AgentState:
        """
        Supervisor node - decides which agent to call.
        
        The supervisor analyzes the user's request and delegates to the
        appropriate specialized agent. It uses LLM tool-calling for routing.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with routing decision
        """
        logger.info("Supervisor analyzing request...")
        
        # Get the last message
        last_message = state["messages"][-1]
        
        # Check if we just got a response from an agent
        if state.get("current_agent") in ["alex", "sarah", "marcus", "sophia"]:
            # Agent just responded, check if we need to call another agent
            # or if we're done
            
            # For now, we're done after one agent response
            # TODO: Add logic for multi-agent queries
            state["next_agent"] = "end"
            state["current_agent"] = "supervisor"
            
            # IMPORTANT: Preserve suggested_actions from the agent
            # Don't overwrite them - they were set by the agent that just ran
            # The suggested_actions are already in state, just keep them
            
            return state
        
        # Supervisor prompt
        supervisor_prompt = f"""You are the Supervisor Agent for a dental clinic AI system.

Your role:
- Analyze the doctor's or patient's request
- Delegate to specialized agents
- NEVER paraphrase agent responses - forward them directly!

Available agents:

1. **Alex** - Reception & Patient Relations
   - Use for: appointment scheduling, patient questions, basic inquiries, general reception tasks
   
2. **שרה (Sarah)** - Clinical Assistant
   - Use for: dental charts, treatment records, prescriptions, medical history, allergies, treatment plans
   - Clinical operations ONLY - this is the medical expert
   
3. **Marcus** (CFO) - Financial Analysis
   - Use for: revenue analysis, payment status, profitability insights, financial trends, invoicing
   
4. **Sophia** (Admin) - Operations Management
   - Use for: scheduling conflicts, staff management, operational efficiency, appointment optimization

IMPORTANT ROUTING RULES:
- Medical/clinical questions → שרה
- Appointments/reception → Alex
- Money/finance → Marcus
- Operations/efficiency → Sophia

Current request: "{last_message.content}"

Which agent should handle this request? Respond with ONLY the agent name: alex, sarah, marcus, or sophia.
If the request is complete or unclear, respond with: end
"""
        
        # Call supervisor LLM
        response = self.supervisor_llm.invoke([
            SystemMessage(content=supervisor_prompt)
        ])
        
        # Parse routing decision
        routing_decision = response.content.strip().lower()
        
        # Validate routing decision
        valid_agents = ["alex", "sarah", "marcus", "sophia", "end"]
        if routing_decision not in valid_agents:
            logger.warning(f"Invalid routing decision: {routing_decision}, defaulting to alex")
            routing_decision = "alex"
        
        # RBAC Check: Verify user has permission to access this agent
        from app.agents.rbac import can_access_agent, get_permission_denied_message
        
        user_role = state.get("user_role", "patient")  # Default to most restrictive
        
        if routing_decision in ["alex", "sarah", "marcus", "sophia"]:
            if not can_access_agent(user_role, routing_decision):
                logger.warning(
                    f"User with role '{user_role}' attempted to access agent '{routing_decision}' - DENIED"
                )
                
                # Create permission denied message
                denied_message = get_permission_denied_message(user_role, f"access_{routing_decision}")
                
                # Add denial message to conversation
                state["messages"].append(AIMessage(content=denied_message))
                
                # End the conversation
                state["next_agent"] = "end"
                state["current_agent"] = "supervisor"
                
                return state
        
        logger.info(f"Supervisor routing to: {routing_decision}")
        
        # Update state
        state["next_agent"] = routing_decision
        state["current_agent"] = "supervisor"
        
        return state
    
    def _route_supervisor(self, state: AgentState) -> Literal["alex", "sarah", "marcus", "sophia", "end"]:
        """
        Routing function for supervisor conditional edges.
        
        Args:
            state: Current agent state
            
        Returns:
            Next agent to call or "end"
        """
        next_agent = state.get("next_agent", "end")
        logger.info(f"Routing to: {next_agent}")
        return next_agent
    
    def _alex_node(self, state: AgentState) -> AgentState:
        """
        Alex node - Patient interactions and reception.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Alex's response
        """
        logger.info("Alex handling request...")
        
        # Clean messages for Alex (remove supervisor routing)
        clean_messages = remove_handoff_messages(state["messages"])
        
        # Prepare state for Alex
        alex_state = {
            "messages": clean_messages,
            "organization_id": state.get("organization_id"),
            "user_role": state.get("user_role", "patient"),
            "user_id": state.get("user_id", "unknown")
        }
        
        # Call Alex agent
        response_state = self.alex.process(alex_state)
        
        # Extract response from state
        response_message = response_state["messages"][-1]
        
        # Add Alex's response to messages
        state["messages"].append(response_message)
        
        # Update current agent
        state["current_agent"] = "alex"
        
        # Preserve suggested actions if Alex set any
        if "suggested_actions" in response_state:
            state["suggested_actions"] = response_state["suggested_actions"]
        
        return state
    
    def _sarah_node(self, state: AgentState) -> AgentState:
        """
        שרה node - Clinical operations and patient care.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with שרה's response
        """
        logger.info("שרה (Clinical Assistant) handling request...")
        
        # Clean messages for שרה (remove supervisor routing)
        clean_messages = remove_handoff_messages(state["messages"])
        
        # Prepare input for שרה
        input_text = clean_messages[-1].content if clean_messages else ""
        
        # Call שרה agent
        response = self.sarah.invoke({
            "input": input_text,
            "chat_history": clean_messages[:-1] if len(clean_messages) > 1 else []
        })
        
        # Add שרה's response to messages
        state["messages"].append(AIMessage(content=response["output"]))
        
        # Update current agent
        state["current_agent"] = "sarah"
        
        return state
    
    def _marcus_node(self, state: AgentState) -> AgentState:
        """
        Marcus node - Financial analysis and insights.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Marcus's response
        """
        logger.info("Marcus (CFO) handling request...")
        
        # Clean messages for Marcus (remove supervisor routing)
        clean_messages = remove_handoff_messages(state["messages"])
        
        # Prepare state for Marcus
        marcus_state = {
            "messages": clean_messages,
            "organization_id": state.get("organization_id"),
            "user_role": state.get("user_role", "staff"),
            "user_id": state.get("user_id", "unknown")
        }
        
        # Call Marcus agent
        response_state = self.marcus.process(marcus_state)
        
        # Extract response from state
        response_message = response_state["messages"][-1]
        
        # Add Marcus's response to messages
        state["messages"].append(response_message)
        
        # Update current agent
        state["current_agent"] = "marcus"
        
        return state
    
    def _sophia_node(self, state: AgentState) -> AgentState:
        """
        Sophia node - Operations and scheduling management.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Sophia's response
        """
        logger.info("Sophia (Admin) handling request...")
        
        # Clean messages for Sophia (remove supervisor routing)
        clean_messages = remove_handoff_messages(state["messages"])
        
        # Prepare state for Sophia
        sophia_state = {
            "messages": clean_messages,
            "organization_id": state.get("organization_id"),
            "user_role": state.get("user_role", "staff"),
            "user_id": state.get("user_id", "unknown")
        }
        
        # Call Sophia agent
        response_state = self.sophia.process(sophia_state)
        
        # Extract response from state
        response_message = response_state["messages"][-1]
        
        # Add Sophia's response to messages
        state["messages"].append(response_message)
        
        # Update current agent
        state["current_agent"] = "sophia"
        
        return state
    
    def invoke(
        self,
        message: str,
        thread_id: str,
        organization_id: str = None,
        user_role: str = "patient"
    ) -> Dict[str, Any]:
        """
        Invoke the agent graph with a user message.
        
        Args:
            message: User message
            thread_id: Conversation thread ID
            organization_id: Organization ID for multi-tenancy
            user_role: User role for RBAC
            
        Returns:
            Agent response
        """
        # Prepare initial state
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "organization_id": organization_id,
            "user_role": user_role,
            "current_agent": None,
            "next_agent": None,
        }
        
        # Configuration for memory
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        # Invoke graph
        try:
            result = self.graph.invoke(initial_state, config=config)
            
            # Extract final response
            final_message = result["messages"][-1]
            
            return {
                "output": final_message.content,
                "agent": result.get("current_agent"),
                "suggested_actions": result.get("suggested_actions", []),
                "success": True
            }
        except Exception as e:
            logger.error(f"Error in agent graph: {e}", exc_info=True)
            return {
                "output": f"מצטער, נתקלתי בשגיאה: {str(e)}",
                "agent": None,
                "suggested_actions": [],
                "success": False,
                "error": str(e)
            }


# Global instance
agent_graph_v4 = AgentGraphV4()

