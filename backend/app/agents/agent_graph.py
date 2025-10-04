"""
Agent Graph V2 - Unified Alex Agent

Simplified graph with single Alex agent that synthesizes all expertise.
"""

import logging
import json
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.graph_state import AgentState
from app.agents.alex import AlexAgent
from app.memory.causal_memory import causal_memory


logger = logging.getLogger(__name__)


class AgentGraphV2:
    """Simplified LangGraph with unified Alex agent."""
    
    def __init__(self, memory=None):
        """
        Initialize agent graph with Alex.
        
        Args:
            memory: Optional causal memory instance (for testing)
        """
        self.alex = AlexAgent()
        self.causal_memory = memory if memory is not None else causal_memory
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build LangGraph workflow with single Alex node.
        
        Returns:
            Compiled StateGraph
        """
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add single Alex node
        workflow.add_node("alex", self._alex_node)
        
        # Set entry point
        workflow.set_entry_point("alex")
        
        # Alex always goes to END
        workflow.add_edge("alex", END)
        
        # Compile graph
        return workflow.compile()
    
    def _alex_node(self, state: AgentState) -> AgentState:
        """
        Alex (Unified Agent) node.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state
        """
        return self.alex.process(state)
    
    async def process_message(
        self,
        user_id: str,
        organization_id: str,
        conversation_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """
        Process a user message through the agent graph.
        
        Args:
            user_id: User ID
            organization_id: Organization ID
            conversation_id: Conversation ID
            message: User message
            
        Returns:
            Response dictionary with agent and response
        """
        logger.info(f"Processing message for user {user_id} in conversation {conversation_id}")
        
        # Retrieve similar past interactions from causal memory
        similar_interactions = self.causal_memory.get_similar_interactions(
            user_message=message,
            limit=3
        )
        
        # Enrich message with context from memory
        enriched_message = message
        if similar_interactions:
            context_from_memory = "\n\n[Context from past interactions]:\n"
            for interaction in similar_interactions:
                context_from_memory += f"- {interaction['user_message']} → {interaction['agent_response'][:100]}...\n"
            enriched_message = f"{message}\n\n{context_from_memory}"
        
        messages = [HumanMessage(content=enriched_message)]
        
        initial_state: AgentState = {
            "messages": messages,
            "current_agent": "alex",
            "user_id": user_id,
            "organization_id": organization_id,
            "conversation_id": conversation_id,
            "patient_id": None,
            "appointment_id": None,
            "invoice_id": None,
            "intent": None,
            "next_agent": None,
            "tool_results": {},
            "errors": [],
            "rate_limit_counters": {},
            "requires_human": False,
            "escalation_level": None,
        }
        
        # Run graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Extract response
        last_message = final_state["messages"][-1]
        response_text = last_message.content
        
        # Get escalation level from state (set by Alex agent)
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
            "agent": "alex",
            "intent": intent,
            "escalation_level": escalation_level,
            "requires_human": final_state.get("requires_human", False),
        }
        
        self.causal_memory.store_interaction(
            user_message=message,
            agent_response=response_text,
            agent_name="alex",
            conversation_id=conversation_id,
            organization_id=organization_id,
            outcome=outcome,
            metadata=metadata
        )
        
        logger.info(f"Response generated by Alex for user {user_id}")
        
        return {
            "agent": "alex",
            "response": response_text,
            "requires_human": final_state.get("requires_human", False),
            "escalation_level": escalation_level,
            "intent": intent,
            "outcome": outcome,
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
        
        if any(word in message_lower for word in ["pain", "hurt", "ache", "swelling", "bleeding", "כאב"]):
            return "medical_question"
        elif any(word in message_lower for word in ["invoice", "bill", "payment", "cost", "price", "חשבונית"]):
            return "billing_inquiry"
        elif any(word in message_lower for word in ["appointment", "schedule", "book", "available", "תור"]):
            return "appointment_scheduling"
        else:
            return "general_inquiry"


# Create singleton instance
agent_graph_v2 = AgentGraphV2()
