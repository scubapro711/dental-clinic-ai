"""
LangGraph Agent Graph

This module implements the agent graph architecture as per User Story 2.1.

Architecture:
    User Input
        ↓
    Dana (Coordinator)
        ↓
    ┌───────┬───────┬───────┐
    │       │       │       │
  Michal  Yosef  Sarah  Dana
(Medical)(Billing)(Schedule)(General)
    │       │       │       │
    └───────┴───────┴───────┘
            ↓
        Response
"""

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.graph_state import AgentState
from app.agents.dana import DanaAgent
from app.agents.michal import MichalAgent
from app.agents.yosef import YosefAgent
from app.agents.sarah import SarahAgent


class AgentGraph:
    """LangGraph-based agent orchestration."""
    
    def __init__(self):
        """Initialize agent graph with all 4 agents."""
        self.dana = DanaAgent()
        self.michal = MichalAgent()
        self.yosef = YosefAgent()
        self.sarah = SarahAgent()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the agent graph.
        
        Returns:
            Compiled StateGraph
        """
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("dana", self._dana_node)
        workflow.add_node("michal", self._michal_node)
        workflow.add_node("yosef", self._yosef_node)
        workflow.add_node("sarah", self._sarah_node)
        
        # Set entry point
        workflow.set_entry_point("dana")
        
        # Add conditional edges from Dana
        workflow.add_conditional_edges(
            "dana",
            self._route_from_dana,
            {
                "michal": "michal",
                "yosef": "yosef",
                "sarah": "sarah",
                "end": END,
            }
        )
        
        # All other agents go to END
        workflow.add_edge("michal", END)
        workflow.add_edge("yosef", END)
        workflow.add_edge("sarah", END)
        
        # Compile graph
        return workflow.compile()
    
    def _dana_node(self, state: AgentState) -> AgentState:
        """
        Dana (Coordinator) node.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state
        """
        return self.dana.process(state)
    
    def _michal_node(self, state: AgentState) -> AgentState:
        """
        Michal (Medical) node.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state
        """
        return self.michal.process(state)
    
    def _yosef_node(self, state: AgentState) -> AgentState:
        """
        Yosef (Billing) node.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state
        """
        return self.yosef.process(state)
    
    def _sarah_node(self, state: AgentState) -> AgentState:
        """
        Sarah (Scheduling) node.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state
        """
        return self.sarah.process(state)
    
    def _route_from_dana(
        self, state: AgentState
    ) -> Literal["michal", "yosef", "sarah", "end"]:
        """
        Route from Dana to appropriate agent or end.
        
        Args:
            state: Current agent state
            
        Returns:
            Next node name
        """
        next_agent = state.get("next_agent")
        
        if next_agent == "michal":
            return "michal"
        elif next_agent == "yosef":
            return "yosef"
        elif next_agent == "sarah":
            return "sarah"
        else:
            # Dana handles it herself
            return "end"
    
    async def process_message(
        self,
        user_id: str,
        organization_id: str,
        conversation_id: str,
        message: str,
        message_history: list = None,
    ) -> Dict[str, Any]:
        """
        Process user message through the agent graph.
        
        Args:
            user_id: User ID
            organization_id: Organization ID
            conversation_id: Conversation ID
            message: User message
            message_history: Previous messages (optional)
            
        Returns:
            Response dict with agent reply
        """
        # Build initial state
        messages = message_history or []
        messages.append(HumanMessage(content=message))
        
        initial_state: AgentState = {
            "messages": messages,
            "current_agent": "dana",
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
        }
        
        # Run graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Extract response
        last_message = final_state["messages"][-1]
        
        return {
            "response": last_message.content,
            "agent": final_state.get("current_agent", "dana"),
            "next_agent": final_state.get("next_agent"),
            "requires_human": final_state.get("requires_human", False),
            "state": final_state,
        }
