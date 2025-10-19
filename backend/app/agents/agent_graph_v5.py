"""
Agent Graph V5 - Multi-Agent System with 5 Agents (Including Harper)

Supervisor architecture with specialized agents:
- Supervisor: Routes requests to specialized agents
- Alex: Patient-facing interactions (Reception & Patient Relations)
- שרה (Sarah): Clinical operations and patient care
- Marcus (CFO): Financial analysis and insights
- Sophia (Admin): Operations and scheduling management
- Harper: HIPAA Compliance Specialist (NEW!)

Key Features:
- Tool-calling LLM for routing
- Forward messages (no paraphrasing!)
- Clean context for sub-agents
- Intelligent delegation
- Full clinical capabilities via שרה
- Comprehensive HIPAA compliance via Harper

Harper Integration:
- RAG-powered HIPAA knowledge base
- 10 specialized compliance tools
- Role-based access (clinic_admin and super_admin only)
- Proactive compliance monitoring

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
from app.agents.harper_hipaa import harper_node
from app.core.memory import get_memory_saver


logger = logging.getLogger(__name__)


def _limit_conversation_history(messages: List[BaseMessage], max_messages: int = 15) -> List[BaseMessage]:
    """
    Limit conversation history to prevent token overflow.
    
    This is CRITICAL to prevent 429 errors from OpenAI!
    Keep only the last N messages to stay under token limits.
    
    Args:
        messages: List of messages
        max_messages: Maximum number of messages to keep (default: 15)
        
    Returns:
        Limited list of messages
    """
    if len(messages) <= max_messages:
        return messages
    
    # Keep system messages if they exist
    system_messages = [m for m in messages if isinstance(m, SystemMessage)]
    other_messages = [m for m in messages if not isinstance(m, SystemMessage)]
    
    # Keep only last N messages
    limited_messages = other_messages[-max_messages:]
    
    logger.info(f"Limited conversation history from {len(messages)} to {len(system_messages) + len(limited_messages)} messages")
    
    return system_messages + limited_messages


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


class AgentGraphV5:
    """
    Multi-Agent LangGraph with Supervisor architecture - 5 Agents (Including Harper).
    
    Architecture:
    - Supervisor node (routes to agents)
    - Alex node (patient interactions & reception)
    - שרה node (clinical operations)
    - Marcus node (CFO - financial analysis)
    - Sophia node (Admin - operations management)
    - Harper node (HIPAA compliance specialist) - NEW!
    
    The supervisor uses tool-calling to delegate to specialized agents,
    and forwards their responses directly without paraphrasing.
    """
    
    def __init__(self, memory=None, demo_mode: bool = False):
        """
        Initialize agent graph with supervisor and 5 agents.
        
        Args:
            memory: Optional memory checkpointer (for testing). Defaults to PostgresSaver.
            demo_mode: If True, agents operate in Interactive Demo mode
        """
        self.demo_mode = demo_mode
        
        # Initialize agents with demo_mode
        self.alex = AlexAgent(demo_mode=demo_mode)
        self.sarah = sarah_agent  # Clinical assistant (no demo mode yet)
        self.marcus = CFOAgent()  # CFO (no demo mode yet)
        self.sophia = PracticeAdminAgent()  # Admin (no demo mode yet)
        # Harper is initialized in harper_hipaa.py as singleton
        
        logger.info(f"Agent graph V5 initialized in {'DEMO' if demo_mode else 'PRODUCTION'} mode with Harper")
        
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
        Build LangGraph workflow with supervisor + 5 agents.
        
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
        workflow.add_node("harper", self._harper_node)  # NEW!
        
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
                "harper": "harper",  # NEW!
                "end": END,
            }
        )
        
        # Agents return to supervisor for potential follow-up
        workflow.add_edge("alex", "supervisor")
        workflow.add_edge("sarah", "supervisor")
        workflow.add_edge("marcus", "supervisor")
        workflow.add_edge("sophia", "supervisor")
        workflow.add_edge("harper", "supervisor")  # NEW!
        
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
        if state.get("current_agent") in ["alex", "sarah", "marcus", "sophia", "harper"]:
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

5. **Harper** - HIPAA Compliance Specialist (NEW!)
   - Use for: HIPAA compliance questions, PHI handling, breach notifications, BAAs, security assessments, patient rights, risk analysis, compliance reports
   - ONLY available to clinic_admin and super_admin roles
   - Keywords: HIPAA, compliance, privacy, security, breach, PHI, BAA, audit, risk

IMPORTANT ROUTING RULES:
- HIPAA/compliance questions → Harper (admin only)
- Medical/clinical questions → שרה
- Appointments/reception → Alex
- Money/finance → Marcus
- Operations/efficiency → Sophia

Current request: "{last_message.content}"

Which agent should handle this request? Respond with ONLY the agent name: alex, sarah, marcus, sophia, or harper.
If the request is complete or unclear, respond with: end
"""
        
        # Call supervisor LLM
        response = self.supervisor_llm.invoke([
            SystemMessage(content=supervisor_prompt)
        ])
        
        # Parse routing decision
        routing_decision = response.content.strip().lower()
        
        # Validate routing decision
        valid_agents = ["alex", "sarah", "marcus", "sophia", "harper", "end"]
        if routing_decision not in valid_agents:
            logger.warning(f"Invalid routing decision: {routing_decision}, defaulting to alex")
            routing_decision = "alex"
        
        # RBAC Check: Verify user has permission to access this agent
        from app.agents.rbac import can_access_agent, get_permission_denied_message
        
        user_role = state.get("user_role", "patient")  # Default to most restrictive
        
        if routing_decision in ["alex", "sarah", "marcus", "sophia", "harper"]:
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
    
    def _route_supervisor(self, state: AgentState) -> Literal["alex", "sarah", "marcus", "sophia", "harper", "end"]:
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
        
        # Limit conversation history to prevent token overflow
        limited_messages = _limit_conversation_history(state["messages"], max_messages=15)
        
        # Clean messages for Alex (remove supervisor routing)
        clean_messages = remove_handoff_messages(limited_messages)
        
        # Prepare state for Alex
        alex_state = {
            "messages": clean_messages,
            "organization_id": state.get("organization_id"),
            "user_role": state.get("user_role", "patient"),
        }
        
        # Call Alex
        result = self.alex.process(alex_state)
        
        # Update main state with Alex's response
        state["messages"] = result["messages"]
        state["current_agent"] = "alex"
        
        # Preserve suggested_actions from Alex
        if "suggested_actions" in result:
            state["suggested_actions"] = result["suggested_actions"]
        
        return state
    
    def _sarah_node(self, state: AgentState) -> AgentState:
        """
        שרה (Sarah) node - Clinical operations.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Sarah's response
        """
        logger.info("שרה handling request...")
        
        # Limit conversation history
        limited_messages = _limit_conversation_history(state["messages"], max_messages=15)
        
        # Clean messages
        clean_messages = remove_handoff_messages(limited_messages)
        
        # Prepare state for Sarah
        sarah_state = {
            "messages": clean_messages,
            "organization_id": state.get("organization_id"),
            "user_role": state.get("user_role", "patient"),
        }
        
        # Call Sarah
        result = self.sarah(sarah_state)
        
        # Update main state
        state["messages"] = result["messages"]
        state["current_agent"] = "sarah"
        
        if "suggested_actions" in result:
            state["suggested_actions"] = result["suggested_actions"]
        
        return state
    
    def _marcus_node(self, state: AgentState) -> AgentState:
        """
        Marcus node - CFO financial analysis.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Marcus's response
        """
        logger.info("Marcus handling request...")
        
        # Limit conversation history
        limited_messages = _limit_conversation_history(state["messages"], max_messages=15)
        
        # Clean messages
        clean_messages = remove_handoff_messages(limited_messages)
        
        # Prepare state for Marcus
        marcus_state = {
            "messages": clean_messages,
            "organization_id": state.get("organization_id"),
            "user_role": state.get("user_role", "patient"),
        }
        
        # Call Marcus
        result = self.marcus.process(marcus_state)
        
        # Update main state
        state["messages"] = result["messages"]
        state["current_agent"] = "marcus"
        
        if "suggested_actions" in result:
            state["suggested_actions"] = result["suggested_actions"]
        
        return state
    
    def _sophia_node(self, state: AgentState) -> AgentState:
        """
        Sophia node - Practice admin operations.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Sophia's response
        """
        logger.info("Sophia handling request...")
        
        # Limit conversation history
        limited_messages = _limit_conversation_history(state["messages"], max_messages=15)
        
        # Clean messages
        clean_messages = remove_handoff_messages(limited_messages)
        
        # Prepare state for Sophia
        sophia_state = {
            "messages": clean_messages,
            "organization_id": state.get("organization_id"),
            "user_role": state.get("user_role", "patient"),
        }
        
        # Call Sophia
        result = self.sophia.process(sophia_state)
        
        # Update main state
        state["messages"] = result["messages"]
        state["current_agent"] = "sophia"
        
        if "suggested_actions" in result:
            state["suggested_actions"] = result["suggested_actions"]
        
        return state
    
    def _harper_node(self, state: AgentState) -> AgentState:
        """
        Harper node - HIPAA Compliance Specialist.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Harper's response
        """
        logger.info("Harper handling request...")
        
        # Limit conversation history
        limited_messages = _limit_conversation_history(state["messages"], max_messages=15)
        
        # Clean messages
        clean_messages = remove_handoff_messages(limited_messages)
        
        # Prepare state for Harper
        harper_state = {
            "messages": clean_messages,
            "organization_id": state.get("organization_id"),
            "user_role": state.get("user_role", "patient"),
        }
        
        # Call Harper
        result = harper_node(harper_state)
        
        # Update main state
        state["messages"] = result["messages"]
        state["current_agent"] = "harper"
        
        if "suggested_actions" in result:
            state["suggested_actions"] = result["suggested_actions"]
        
        return state
    
    def invoke(self, state: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Invoke the agent graph.
        
        Args:
            state: Initial state
            config: Configuration (including thread_id for memory)
            
        Returns:
            Final state after processing
        """
        return self.graph.invoke(state, config=config)
    
    def stream(self, state: Dict[str, Any], config: Dict[str, Any] = None):
        """
        Stream the agent graph execution.
        
        Args:
            state: Initial state
            config: Configuration (including thread_id for memory)
            
        Yields:
            State updates as they occur
        """
        return self.graph.stream(state, config=config)


# Create default instance
agent_graph_v5 = AgentGraphV5()

