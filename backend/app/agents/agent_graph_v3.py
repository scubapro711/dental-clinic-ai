"""
Agent Graph V3 - Multi-Agent System with Supervisor

Supervisor architecture with specialized agents:
- Supervisor: Routes requests to specialized agents
- Alex: Patient-facing interactions
- CFO: Financial analysis and insights
- Admin: Operations and scheduling management

Key Features:
- Tool-calling LLM for routing
- Forward messages (no paraphrasing!)
- Clean context for sub-agents
- Intelligent delegation
"""

import logging
import json
from typing import Dict, Any, List, Literal
from langgraph.graph import StateGraph, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI

from app.agents.graph_state import AgentState
from app.agents.alex import AlexAgent
from app.agents.cfo import CFOAgent
from app.agents.practice_admin import PracticeAdminAgent
from app.agents.cfo import CFOAgent
from app.agents.practice_admin import PracticeAdminAgent
from langgraph.checkpoint.memory import MemorySaver


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


class AgentGraphV3:
    """
    Multi-Agent LangGraph with Supervisor architecture.
    
    Architecture:
    - Supervisor node (routes to agents)
    - Alex node (patient interactions)
    - CFO node (financial analysis) - Coming soon
    - Admin node (operations management) - Coming soon
    
    The supervisor uses tool-calling to delegate to specialized agents,
    and forwards their responses directly without paraphrasing.
    """
    
    def __init__(self, memory=None):
        """
        Initialize agent graph with supervisor and agents.
        
        Args:
            memory: Optional memory checkpointer (for testing). Defaults to MemorySaver.
        """
        # Initialize agents
        self.alex = AlexAgent()
        self.cfo = CFOAgent()
        # self.admin = PracticeAdminAgent()  # Coming soon
        
        # Initialize supervisor LLM
        self.supervisor_llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.1,  # Low temperature for consistent routing
        )
        
        # LangGraph Memory (replaces Neo4j!)
        self.memory = memory if memory is not None else MemorySaver()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build LangGraph workflow with supervisor + agents.
        
        Returns:
            Compiled StateGraph
        """
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("alex", self._alex_node)
        workflow.add_node("cfo", self._cfo_node)
        # workflow.add_node("admin", self._admin_node)  # Coming soon
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Supervisor routes to agents or END
        workflow.add_conditional_edges(
            "supervisor",
            self._route_supervisor,
            {
                "alex": "alex",
                "cfo": "cfo",
                # "admin": "admin",  # Coming soon
                "end": END,
            }
        )
        
        # Agents return to supervisor for potential follow-up
        workflow.add_edge("alex", "supervisor")
        workflow.add_edge("cfo", "supervisor")
        # workflow.add_edge("admin", "supervisor")  # Coming soon
        
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
        if state.get("current_agent") in ["alex", "cfo", "admin"]:
            # Agent just responded, check if we need to call another agent
            # or if we're done
            
            # For now, we're done after one agent response
            # TODO: Add logic for multi-agent queries
            state["next_agent"] = "end"
            state["current_agent"] = "supervisor"
            return state
        
        # Supervisor prompt
        supervisor_prompt = f"""You are the Supervisor Agent for a dental clinic AI system.

Your role:
- Analyze the doctor's or patient's request
- Delegate to specialized agents
- NEVER paraphrase agent responses - forward them directly!

Available agents:
1. **Alex** - Patient interactions, appointments, medical triage
   - Use for: appointment scheduling, patient questions, medical concerns
   
2. **Marcus** (CFO) - Financial analysis, revenue, payments
   - Use for: revenue analysis, payment status, profitability insights, financial trends
   
3. **Sophia** (Admin) - Scheduling, conflicts, operations
   - Use for: scheduling conflicts, staff management, operational efficiency, appointment optimization

Current request: "{last_message.content}"

Which agent should handle this request? Respond with ONLY the agent name: alex, cfo, or admin.
If the request is complete or unclear, respond with: end
"""
        
        # Call supervisor LLM
        response = self.supervisor_llm.invoke([
            SystemMessage(content=supervisor_prompt)
        ])
        
        # Parse routing decision
        routing_decision = response.content.strip().lower()
        
        # Validate routing decision
        valid_agents = ["alex", "cfo", "admin", "end"]
        if routing_decision not in valid_agents:
            logger.warning(f"Invalid routing decision: {routing_decision}, defaulting to alex")
            routing_decision = "alex"
        
        # For now, only Alex and CFO are available
        if routing_decision == "admin":
            logger.info("Admin agent not yet implemented, routing to Alex")
            routing_decision = "alex"
        
        logger.info(f"Supervisor routing to: {routing_decision}")
        
        # Update state
        state["next_agent"] = routing_decision
        state["current_agent"] = "supervisor"
        
        return state
    
    def _route_supervisor(self, state: AgentState) -> Literal["alex", "cfo", "admin", "end"]:
        """
        Route based on supervisor's decision.
        
        Args:
            state: Current agent state
            
        Returns:
            Next node to visit
        """
        next_agent = state.get("next_agent", "end")
        
        if next_agent in ["alex", "cfo", "admin"]:
            return next_agent
        
        return "end"
    
    def _alex_node(self, state: AgentState) -> AgentState:
        """
        Alex (Patient Agent) node.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Alex's response
        """
        logger.info("Alex processing request...")
        
        # Clean context (remove routing logic)
        clean_messages = remove_handoff_messages(state["messages"])
        clean_state = {**state, "messages": clean_messages}
        
        # Process with Alex
        result_state = self.alex.process(clean_state)
        
        # Forward Alex's response (no paraphrasing!)
        result_state["current_agent"] = "alex"
        
        # Store agent response for potential multi-agent queries
        if "agent_responses" not in result_state:
            result_state["agent_responses"] = {}
        result_state["agent_responses"]["alex"] = result_state["messages"][-1].content
        
        logger.info("Alex completed processing")
        
        return result_state
    
    def _cfo_node(self, state: AgentState) -> AgentState:
        """
        CFO (Financial Agent) node.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with CFO's response
        """
        logger.info("CFO processing request...")
        
        # Clean context (remove routing logic)
        clean_messages = remove_handoff_messages(state["messages"])
        clean_state = {**state, "messages": clean_messages}
        
        # Process with CFO
        result_state = self.cfo.process(clean_state)
        
        # Forward CFO's response (no paraphrasing!)
        result_state["current_agent"] = "cfo"
        
        # Store agent response for potential multi-agent queries
        if "agent_responses" not in result_state:
            result_state["agent_responses"] = {}
        result_state["agent_responses"]["cfo"] = result_state["messages"][-1].content
        
        logger.info("CFO completed processing")
        
        return result_state
    
    def _cfo_node(self, state: AgentState) -> AgentState:
        """
        CFO (Financial Agent) node.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with CFO's response
        """
        logger.info("CFO processing request...")
        
        # Clean context (remove routing logic)
        clean_messages = remove_handoff_messages(state["messages"])
        clean_state = {**state, "messages": clean_messages}
        
        # Process with CFO
        result_state = self.cfo.process(clean_state)
        
        # Forward CFO's response (no paraphrasing!)
        result_state["current_agent"] = "cfo"
        
        # Store agent response for potential multi-agent queries
        if "agent_responses" not in result_state:
            result_state["agent_responses"] = {}
        result_state["agent_responses"]["cfo"] = result_state["messages"][-1].content
        
        logger.info("CFO completed processing")
        
        return result_state
    
    # Future nodes (coming soon):
    
    # def _cfo_node(self, state: AgentState) -> AgentState:
    #     """CFO (Financial Agent) node."""
    #     logger.info("CFO processing request...")
    #     clean_messages = remove_handoff_messages(state["messages"])
    #     clean_state = {**state, "messages": clean_messages}
    #     result_state = self.cfo.process(clean_state)
    #     result_state["current_agent"] = "cfo"
    #     if "agent_responses" not in result_state:
    #         result_state["agent_responses"] = {}
    #     result_state["agent_responses"]["cfo"] = result_state["messages"][-1].content
    #     return result_state
    
    # def _admin_node(self, state: AgentState) -> AgentState:
    #     """Admin (Operations Agent) node."""
    #     logger.info("Admin processing request...")
    #     clean_messages = remove_handoff_messages(state["messages"])
    #     clean_state = {**state, "messages": clean_messages}
    #     result_state = self.admin.process(clean_state)
    #     result_state["current_agent"] = "admin"
    #     if "agent_responses" not in result_state:
    #         result_state["agent_responses"] = {}
    #     result_state["agent_responses"]["admin"] = result_state["messages"][-1].content
    #     return result_state
    
    async def process_message(
        self,
        user_id: str,
        organization_id: str,
        conversation_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """
        Process a user message through the multi-agent graph.
        
        Args:
            user_id: User ID
            organization_id: Organization ID
            conversation_id: Conversation ID
            message: User message
            
        Returns:
            Response dictionary with agent and response
        """
        logger.info(f"Processing message for user {user_id} in conversation {conversation_id}")
        
        # Memory is now handled automatically by LangGraph checkpointer!
        # No need to manually retrieve - the graph state persists across invocations
        
        # Use the message as-is
        enriched_message = message
        
        # Optional: Add context note (for now, just use message)
        if False:  # Disabled - memory handled by checkpointer
            context_from_memory = "\n\n[Context from past interactions]:\n"
            for interaction in similar_interactions:
                context_from_memory += f"- {interaction['user_message']} → {interaction['agent_response'][:100]}...\n"
            enriched_message = f"{message}\n\n{context_from_memory}"
        
        messages = [HumanMessage(content=enriched_message)]
        
        initial_state: AgentState = {
            "messages": messages,
            "current_agent": "supervisor",
            "user_id": user_id,
            "organization_id": organization_id,
            "conversation_id": conversation_id,
            "patient_id": None,
            "appointment_id": None,
            "invoice_id": None,
            "intent": None,
            "next_agent": None,
            "tool_results": {},
            "agent_responses": {},
            "errors": [],
            "rate_limit_counters": {},
            "requires_human": False,
            "escalation_level": None,
        }
        
        # Run graph with conversation thread
        final_state = await self.graph.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": conversation_id}}
        )
        
        # Extract response (forwarded from agent, not paraphrased!)
        last_message = final_state["messages"][-1]
        response_text = last_message.content
        
        # Get which agent responded (from agent_responses, not current_agent)
        # current_agent might be "supervisor" after routing back
        agent_responses = final_state.get("agent_responses", {})
        if agent_responses:
            # Get the last agent that responded
            responding_agent = list(agent_responses.keys())[-1]
        else:
            responding_agent = "alex"  # fallback
        
        # Get escalation level from state
        escalation_level = final_state.get("escalation_level")
        
        # Clean up escalation tags from response if present
        for tag in ["[ESCALATE: EMERGENCY]", "[ESCALATE: DOCTOR_REQUIRED]", "[ESCALATE: ROUTINE]"]:
            response_text = response_text.replace(tag, "").strip()
        
        # Determine intent from message content
        intent = self._classify_intent(message)
        
        # Determine outcome
        outcome = "success"
        if final_state.get("requires_human"):
            outcome = "escalated"
        elif final_state.get("errors"):
            outcome = "failure"
        
        # Store interaction in causal memory
        metadata = {
            "agent": responding_agent,
            "intent": intent,
            "escalation_level": escalation_level,
            "requires_human": final_state.get("requires_human", False),
            "supervisor_routed": True,
        }
        
        # Memory automatically stored by LangGraph checkpointer!
        # No manual storage needed - state persists via thread_id
        # No manual storage needed - state persists via thread_id
        
        logger.info(f"Response generated by {responding_agent} for user {user_id}")
        
        return {
            "agent": responding_agent,
            "response": response_text,
            "requires_human": final_state.get("requires_human", False),
            "escalation_level": escalation_level,
            "intent": intent,
            "outcome": outcome,
            "agent_responses": final_state.get("agent_responses", {}),
        }
    
    def _classify_intent(self, message: str) -> str:
        """
        Classify user intent from message.
        
        Args:
            message: User message
            
        Returns:
            Intent classification
        """
        message_lower = message.lower()
        
        # Financial intents
        if any(word in message_lower for word in ["revenue", "payment", "invoice", "bill", "cost", "price", "profit", "חשבונית", "תשלום"]):
            return "financial_inquiry"
        
        # Operations intents
        if any(word in message_lower for word in ["conflict", "schedule", "staff", "efficiency", "optimize", "קונפליקט", "לוח זמנים"]):
            return "operations_inquiry"
        
        # Medical intents
        if any(word in message_lower for word in ["pain", "hurt", "ache", "swelling", "bleeding", "כאב"]):
            return "medical_question"
        
        # Appointment intents
        if any(word in message_lower for word in ["appointment", "book", "available", "תור"]):
            return "appointment_scheduling"
        
        return "general_inquiry"


# Create singleton instance
agent_graph_v3 = AgentGraphV3()
