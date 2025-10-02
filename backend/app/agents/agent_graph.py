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
from app.agents.emma import EmmaAgent
from app.agents.lisa import LisaAgent
from app.agents.robert import RobertAgent
from app.agents.jessica import JessicaAgent
from app.memory.causal_memory import causal_memory


class AgentGraph:
    """LangGraph-based agent orchestration."""
    
    def __init__(self):
        """Initialize agent graph with all 4 agents."""
        self.emma = EmmaAgent()
        self.lisa = LisaAgent()
        self.robert = RobertAgent()
        self.jessica = JessicaAgent()
        
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
        workflow.add_node("emma", self._emma_node)
        workflow.add_node("lisa", self._lisa_node)
        workflow.add_node("robert", self._robert_node)
        workflow.add_node("jessica", self._jessica_node)
        
        # Set entry point
        workflow.set_entry_point("emma")
        
        # Add conditional edges from Emma
        workflow.add_conditional_edges(
            "emma",
            self._route_from_emma,
            {
                "lisa": "lisa",
                "robert": "robert",
                "jessica": "jessica",
                "end": END,
            }
        )
        
        # All other agents go to END
        workflow.add_edge("lisa", END)
        workflow.add_edge("robert", END)
        workflow.add_edge("jessica", END)
        
        # Compile graph
        return workflow.compile()
    
    def _emma_node(self, state: AgentState) -> AgentState:
        """
        Emma (Coordinator) node.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state
        """
        return self.emma.process(state)
    
    def _lisa_node(self, state: AgentState) -> AgentState:
        """
        Lisa (Medical) node.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state
        """
        return self.lisa.process(state)
    
    def _robert_node(self, state: AgentState) -> AgentState:
        """
        Robert (Billing) node.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state
        """
        return self.robert.process(state)
    
    def _jessica_node(self, state: AgentState) -> AgentState:
        """
        Jessica (Scheduling) node.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state
        """
        return self.jessica.process(state)
    
    def _route_from_emma(
        self, state: AgentState
    ) -> Literal["lisa", "robert", "jessica", "end"]:
        """
        Route from Emma to appropriate agent or end.
        
        Args:
            state: Current agent state
            
        Returns:
            Next node name
        """
        next_agent = state.get("next_agent")
        
        if next_agent == "lisa":
            return "lisa"
        elif next_agent == "robert":
            return "robert"
        elif next_agent == "jessica":
            return "jessica"
        else:
            # Emma handles it herself
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
        # 🧠 STEP 1: Retrieve similar past interactions from causal memory
        similar_interactions = causal_memory.get_similar_interactions(
            user_message=message,
            limit=3
        )
        
        # Build context from similar interactions
        context_from_memory = ""
        if similar_interactions:
            context_from_memory = "\n\n📚 Similar past interactions:\n"
            for idx, interaction in enumerate(similar_interactions, 1):
                context_from_memory += f"\n{idx}. User: {interaction['user_message']}\n"
                context_from_memory += f"   Agent ({interaction['agent_name']}): {interaction['agent_response']}\n"
                context_from_memory += f"   Outcome: {interaction['outcome']} (Similarity: {interaction['similarity']:.2f})\n"
        
        # Build initial state
        messages = message_history or []
        
        # Add context from causal memory to the message
        enriched_message = message
        if context_from_memory:
            enriched_message = f"{message}\n\n{context_from_memory}"
        
        messages.append(HumanMessage(content=enriched_message))
        
        initial_state: AgentState = {
            "messages": messages,
            "current_agent": "emma",
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
        agent_response = last_message.content
        current_agent = final_state.get("current_agent", "dana")
        
        # 🧠 STEP 2: Store interaction in causal memory
        outcome = "success"
        if final_state.get("requires_human", False):
            outcome = "escalated"
        elif final_state.get("errors"):
            outcome = "failure"
        
        try:
            # Build metadata without None values (Neo4j doesn't support them)
            metadata = {
                "user_id": user_id,
            }
            if final_state.get("intent"):
                metadata["intent"] = final_state.get("intent")
            if final_state.get("next_agent"):
                metadata["next_agent"] = final_state.get("next_agent")
            
            causal_memory.store_interaction(
                user_message=message,
                agent_response=agent_response,
                agent_name=current_agent,
                conversation_id=conversation_id,
                organization_id=organization_id,
                outcome=outcome,
                metadata=metadata
            )
        except Exception as e:
            # Don't fail the request if causal memory fails
            print(f"⚠️ Failed to store interaction in causal memory: {e}")
        
        return {
            "response": agent_response,
            "agent": current_agent,
            "next_agent": final_state.get("next_agent"),
            "requires_human": final_state.get("requires_human", False),
            "state": final_state,
            "similar_interactions": len(similar_interactions) if similar_interactions else 0,
        }
